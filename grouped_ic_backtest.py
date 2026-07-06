"""
grouped_ic_backtest.py
======================
Grouped (per-slot) FLAT IC / expectancy backtest using LIBRARY-NATIVE indicators
from pandas-ta-classic, sourced from indicator_library.md.

KEY DIFFERENCE from the previous flat run (main.py):
  Indicators are ranked WITHIN their category slot (Trend / Momentum / Volatility
  / Volume), never cross-category. The pipeline fills each of the four slots with
  exactly one indicator, so the only meaningful question is "which indicator wins
  THIS slot for THIS asset", answered with four within-slot leaderboards per asset.

Still FLAT / non-regime-conditioned. "Best-in-slot on full history" != validated,
!= regime-aware. Regime-cell conditioning is the NEXT run.

Reuses:
  data_loader.py  (yfinance layer, unchanged)
  stats.py        (Spearman IC + Newey-West HAC + FDR + discrete expectancy)

Run:  python grouped_ic_backtest.py
Outputs under ./results/:
  grouped_ic_results.csv
  best_in_slot.md
  slot_summary_by_assetclass.md
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback

import numpy as np
import pandas as pd

import pandas_ta_classic as ta   # the pipeline library — must match production

import data_loader
import stats as st


# ==========================================================================
# CONFIG BLOCK
# ==========================================================================
HORIZONS     = [1, 5, 10, 20]
ROLL_WINDOW  = 63
FDR_Q        = 0.10
MIN_ROWS     = 500
START        = "1990-01-01"     # cap pre-1990 thin data (applied post-load)
MIN_STATE_N  = 30               # discrete state min count

SLOTS = ["Trend", "Momentum", "Volatility", "Volume"]

ASSETS = {
    "^GSPC":     {"name": "S&P 500",      "class": "equity"},
    "^NDX":      {"name": "Nasdaq 100",    "class": "equity"},
    "^STOXX50E": {"name": "Euro Stoxx 50", "class": "equity"},
    "^FTSE":     {"name": "FTSE 100",      "class": "equity"},
    "^GDAXI":    {"name": "DAX",           "class": "equity"},
    "^N225":     {"name": "Nikkei 225",    "class": "equity"},
    "^KS11":     {"name": "KOSPI",         "class": "equity"},
    "^HSI":      {"name": "Hang Seng",     "class": "equity"},
    "^TNX":      {"name": "US 10Y yield",  "class": "rates",
                 "return_mode": "diff",
                 "note": "yield-based; fwd = change in yield"},
    "TLT":       {"name": "US 20Y+ UST",   "class": "rates"},
    "LQD":       {"name": "IG corporate",  "class": "credit"},
    "HYG":       {"name": "HY corporate",  "class": "credit"},
    "GC=F":      {"name": "Gold",          "class": "metals"},
    "SI=F":      {"name": "Silver",        "class": "metals"},
    "CL=F":      {"name": "WTI crude",     "class": "energy",
                 "note": "continuous front-month stitch"},
    "DX-Y.NYB":  {"name": "USD index",     "class": "fx"},
    "EURUSD=X":  {"name": "EUR/USD",       "class": "fx"},
    "CHF=X":     {"name": "USD/CHF",       "class": "fx"},
}

DEFERRED = {
    "STAR 50": "deferred pending data API",
    "CSI 300 native": "deferred pending data API",
    "HSI Tech": "deferred pending data API",
}

HERE = os.path.dirname(os.path.abspath(__file__))
LIBRARY_MD  = os.path.join(HERE, "indicator_library.md")
RESULTS_DIR = os.path.join(HERE, "results")
# ==========================================================================


# --------------------------------------------------------------------------- #
# 1. Parse the library
# --------------------------------------------------------------------------- #
_PREFIX_TO_SLOT = {"TR": "Trend", "MO": "Momentum", "VO": "Volatility", "VL": "Volume"}


def parse_library(path: str) -> tuple[list[dict], list[dict]]:
    """
    Read indicator_library.md, extract the machine-readable JSON roster, resolve
    each indicator's category (explicit field, else ID prefix). Returns
    (roster, skipped) where skipped items have an unresolvable category or bad
    schema and are logged, never guessed.
    """
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    m = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
    if not m:
        raise ValueError("no ```json roster block found in indicator_library.md")
    entries = json.loads(m.group(1))

    roster, skipped = [], []
    for e in entries:
        iid = e.get("id", "<no-id>")
        cat = e.get("category")
        if not cat:
            prefix = str(iid).split("-", 1)[0]
            cat = _PREFIX_TO_SLOT.get(prefix)
        if cat not in SLOTS:
            skipped.append({"id": iid, "reason": f"unresolved category ({cat!r})"})
            continue
        if not e.get("transform"):
            skipped.append({"id": iid, "reason": "no transform"})
            continue
        e["category"] = cat
        roster.append(e)
    return roster, skipped


# --------------------------------------------------------------------------- #
# 2. Evaluate an indicator -> a single tested numeric Series (or state Series)
# --------------------------------------------------------------------------- #
def _call_indicator(entry: dict, cols: dict) -> pd.DataFrame | pd.Series | None:
    """Evaluate the library_call string against pandas-ta-classic. `cols` maps
    open/high/low/close/volume to Series. Returns the raw ta output (or None for
    derived indicators that have no direct call, e.g. EMA cross)."""
    call = entry.get("library_call")
    if not call:
        return None
    ns = {"ta": ta, "open": cols["open"], "high": cols["high"],
          "low": cols["low"], "close": cols["close"], "volume": cols["volume"]}
    raw = eval(call, {"__builtins__": {}}, ns)   # controlled: calls authored in library
    # Some pandas-ta-classic functions drop warm-up rows (e.g. stoch), returning a
    # shorter datetime-indexed object. Reindex back onto the price index so every
    # tested series stays length-aligned with the forward returns (dropped rows
    # become explicit NaN warm-up, never filled).
    if isinstance(raw, (pd.Series, pd.DataFrame)):
        raw = raw.reindex(cols["close"].index)
    return raw


def _pick_column(raw, col: str) -> pd.Series:
    if isinstance(raw, pd.Series):
        return raw
    if isinstance(raw, pd.DataFrame):
        if col in raw.columns:
            return raw[col]
        raise KeyError(f"column {col!r} not in {list(raw.columns)}")
    raise TypeError(f"unexpected indicator output type {type(raw)}")


def build_tested_series(entry: dict, cols: dict) -> tuple[np.ndarray, str]:
    """
    Apply the entry's transform to produce the numeric series that gets IC'd (for
    continuous) or the integer state series (for discrete). Returns (array, kind)
    where kind is "continuous" or "discrete".
    """
    tf = entry["transform"]
    close = cols["close"]

    # ---- discrete transforms ----
    if tf.startswith("disc_threshold:"):
        col, lo, hi = tf.split(":", 1)[1].split(",")
        lo, hi = float(lo), float(hi)
        raw = _call_indicator(entry, cols)
        s = _pick_column(raw, col).to_numpy("float64")
        state = np.full(s.shape, np.nan)
        valid = np.isfinite(s)
        state[valid] = 0.0
        state[valid & (s < lo)] = 1.0
        state[valid & (s > hi)] = -1.0
        return state, "discrete"

    if tf.startswith("disc_cross:"):
        a, b = tf.split(":", 1)[1].split(",")
        raw = _call_indicator(entry, cols)
        sa = raw[a].to_numpy("float64"); sb = raw[b].to_numpy("float64")
        state = np.full(sa.shape, np.nan)
        valid = np.isfinite(sa) & np.isfinite(sb)
        state[valid & (sa > sb)] = 1.0
        state[valid & (sa <= sb)] = -1.0
        return state, "discrete"

    if tf.startswith("disc_ema_cross:"):
        f, s = tf.split(":", 1)[1].split(",")
        fast = ta.ema(close, length=int(f)).to_numpy("float64")
        slow = ta.ema(close, length=int(s)).to_numpy("float64")
        state = np.full(fast.shape, np.nan)
        valid = np.isfinite(fast) & np.isfinite(slow)
        state[valid & (fast > slow)] = 1.0
        state[valid & (fast <= slow)] = -1.0
        return state, "discrete"

    if tf == "disc_psar":
        raw = _call_indicator(entry, cols)
        # PSARl_* is populated (non-NaN) while in a long stop, PSARs_* while short
        long_col = [c for c in raw.columns if c.startswith("PSARl")][0]
        short_col = [c for c in raw.columns if c.startswith("PSARs")][0]
        lng = raw[long_col].to_numpy("float64")
        srt = raw[short_col].to_numpy("float64")
        state = np.full(lng.shape, np.nan)
        state[np.isfinite(lng)] = 1.0
        state[np.isfinite(srt)] = -1.0
        return state, "discrete"

    if tf.startswith("disc_supertrend:"):
        col = tf.split(":", 1)[1]
        raw = _call_indicator(entry, cols)
        d = raw[col].to_numpy("float64")   # already +1 / -1
        state = np.where(np.isfinite(d), np.sign(d), np.nan)
        return state, "discrete"

    # ---- continuous transforms ----
    raw = _call_indicator(entry, cols)
    if tf == "level":
        s = _pick_column(raw, entry["tested_column"]).to_numpy("float64")
    elif tf == "ratio_close":
        s = _pick_column(raw, entry["tested_column"]).to_numpy("float64")
        with np.errstate(divide="ignore", invalid="ignore"):
            s = s / close.to_numpy("float64")
    elif tf.startswith("coldiff:"):
        a, b = tf.split(":", 1)[1].split(",")
        s = (raw[a] - raw[b]).to_numpy("float64")
    elif tf.startswith("width:"):
        lo, mid, up = tf.split(":", 1)[1].split(",")
        with np.errstate(divide="ignore", invalid="ignore"):
            s = ((raw[up] - raw[lo]) / raw[mid]).to_numpy("float64")
    elif tf.startswith("slope:"):
        n = int(tf.split(":", 1)[1])
        s = _pick_column(raw, entry["tested_column"]).diff(n).to_numpy("float64")
    else:
        raise ValueError(f"unknown transform {tf!r}")
    return s, "continuous"


# --------------------------------------------------------------------------- #
# 3. Per-asset processing
# --------------------------------------------------------------------------- #
def _return_mode(meta): return meta.get("return_mode", "log")


def _has_volume(df: pd.DataFrame) -> bool:
    v = df["volume"].to_numpy()
    return np.isfinite(v).any() and np.nansum(v) > 0


def process_asset(tkr, meta, df, has_volume, roster) -> list[dict]:
    cols = {c: df[c] for c in ("open", "high", "low", "close", "volume")}
    c = df["close"].to_numpy("float64")
    mode = _return_mode(meta)
    low_conf = len(df) < MIN_ROWS
    aclass = meta["class"]

    fwd = {}
    for hh in HORIZONS:
        f = st.forward_returns(c, hh, mode=mode)
        st.assert_no_lookahead(f, hh)
        fwd[hh] = f

    rows = []
    for entry in roster:
        iid = entry["id"]
        slot = entry["category"]
        needs = set(entry.get("data_inputs", []))
        # skip volume-slot / volume-input indicators on volumeless series
        if ("volume" in needs) and not has_volume:
            for hh in HORIZONS:
                rows.append(_row(tkr, aclass, slot, iid, entry["indicator_type"],
                                 hh, np.nan, np.nan, 0, np.nan, None, low_conf,
                                 "input unavailable: no volume for this series"))
            continue
        try:
            series, kind = build_tested_series(entry, cols)
        except Exception as exc:
            for hh in HORIZONS:
                rows.append(_row(tkr, aclass, slot, iid, entry["indicator_type"],
                                 hh, np.nan, np.nan, 0, np.nan, None, low_conf,
                                 f"indicator error: {exc!r}"))
            continue

        for hh in HORIZONS:
            y = fwd[hh]
            if kind == "continuous":
                ic, tstat, pval, nobs = st.spearman_ic_hac(series, y, lag=hh)
                roll = st.rolling_spearman(series, y, ROLL_WINDOW)
                ic_ir = st.ic_ir_hac(roll, lag=hh)
                note = "fwd = yield change" if mode == "diff" else ""
                if nobs == 0:
                    note = ("degenerate: indicator all-NaN on this series "
                            "(e.g. near-zero volume) | " + note).rstrip(" |")
                rows.append(_row(tkr, aclass, slot, iid, "continuous", hh,
                                 ic, ic_ir, nobs, pval, None, low_conf, note))
            else:  # discrete
                r = st.discrete_expectancy(series, y, MIN_STATE_N)
                note = (f"bull:n={r['bull']['n']},mean={_f(r['bull']['mean'])},"
                        f"hit={_f(r['bull']['hit'])} | "
                        f"bear:n={r['bear']['n']},mean={_f(r['bear']['mean'])},"
                        f"hit={_f(r['bear']['hit'])}")
                if not r["trusted"]:
                    note = "UNTRUSTED(state n<MIN_STATE_N) | " + note
                if mode == "diff":
                    note += " | fwd = yield change"
                rows.append(_row(tkr, aclass, slot, iid, "discrete", hh,
                                 r["spread"], np.nan, r["n_min"], np.nan,
                                 None, low_conf, note))
    return rows


def _f(x):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.5f}"


def _row(asset, aclass, slot, iid, itype, h, ic_or_spread, ic_ir, n_obs, p, fdr,
         low_conf, note):
    return {"asset": asset, "asset_class": aclass, "slot": slot,
            "indicator_id": iid, "indicator_type": itype, "horizon": h,
            "ic_or_spread": ic_or_spread, "ic_ir": ic_ir, "n_obs": n_obs,
            "p_value": p, "survives_fdr": fdr, "low_confidence": bool(low_conf),
            "note": note}


# --------------------------------------------------------------------------- #
# 4. FDR across ALL continuous tests
# --------------------------------------------------------------------------- #
def apply_fdr(df: pd.DataFrame):
    is_cont = df["indicator_type"] == "continuous"
    has_p = df["p_value"].notna()
    pool = is_cont & has_p
    n_tests = int(pool.sum())
    raw_sig = int((df.loc[pool, "p_value"] < 0.05).sum())
    survive = st.benjamini_hochberg(df.loc[pool, "p_value"].to_numpy(), FDR_Q)
    df.loc[pool, "survives_fdr"] = survive
    df.loc[is_cont & ~has_p, "survives_fdr"] = False
    return df, n_tests, raw_sig, int(survive.sum())


# --------------------------------------------------------------------------- #
# 5. Pre-flight
# --------------------------------------------------------------------------- #
def preflight_roster(roster, skipped):
    print("\n" + "=" * 78)
    print("PRE-FLIGHT: RESOLVED INDICATOR ROSTER (by slot)")
    print("=" * 78)
    for slot in SLOTS:
        items = [e for e in roster if e["category"] == slot]
        print(f"\n{slot}  ({len(items)} indicators)")
        print("-" * 78)
        for e in items:
            call = e["library_call"] or f"(derived: {e['transform']})"
            print(f"  {e['id']:<22} {e['indicator_type']:<11} "
                  f"{e['shock_behavior']:<11} {call}")
    if skipped:
        print("\nSKIPPED (category/schema unresolved, logged not guessed):")
        for s in skipped:
            print(f"  {s['id']:<22} {s['reason']}")
    print("=" * 78)


def preflight_coverage(loaded):
    print("\n" + "=" * 78)
    print(f"PRE-FLIGHT: ASSET COVERAGE (START={START}, MIN_ROWS={MIN_ROWS})")
    print("=" * 78)
    print(f"{'ticker':<11}{'name':<15}{'class':<8}{'start':<12}{'end':<12}{'rows':>7}  flags")
    print("-" * 78)
    for tkr, meta in ASSETS.items():
        info = loaded.get(tkr)
        if not info or info["df"] is None:
            print(f"{tkr:<11}{meta['name'][:14]:<15}{meta['class']:<8}"
                  f"{'-':<12}{'-':<12}{0:>7}  FETCH FAILED")
            continue
        d = data_loader.describe(info["df"])
        flags = []
        if d["rows"] < MIN_ROWS: flags.append("LOW_CONFIDENCE")
        if _return_mode(meta) == "diff": flags.append("yield/diff")
        if not info["has_volume"]: flags.append("no-volume(VL slot N/A)")
        print(f"{tkr:<11}{meta['name'][:14]:<15}{meta['class']:<8}"
              f"{str(d['start']):<12}{str(d['end']):<12}{d['rows']:>7}  {', '.join(flags)}")
    print("-" * 78)
    print("DEFERRED (not fetched):", ", ".join(DEFERRED.keys()))
    print("=" * 78)


# --------------------------------------------------------------------------- #
# 6. Outputs
# --------------------------------------------------------------------------- #
def _prior_check(shock_behavior: str, is_winner: bool) -> str:
    """Compare an empirical slot winner to the library's shock prior."""
    sb = shock_behavior
    if sb == "MAINTAIN":
        return (f"library prior MAINTAIN -> AGREES: expected to hold signal and it "
                f"leads the slot on flat history")
    if sb == "SUPPRESS":
        return (f"library prior SUPPRESS -> DISAGREES: expected to lose signal yet it "
                f"tops the slot on flat history; possible regime-masking, flag for "
                f"regime run")
    if sb == "SUBSTITUTE":
        return (f"library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged "
                f"primary yet wins flat; revisit slot priority under regimes")
    return f"library prior {sb}"


def write_best_in_slot(df, roster, loaded):
    prior = {e["id"]: e for e in roster}
    path = os.path.join(RESULTS_DIR, "best_in_slot.md")
    L = []; A = L.append
    A("# Best-in-Slot — flat full-history IC (per asset, four slots)")
    A("")
    A("> **FLAT / non-regime-conditioned.** A 'slot winner' is the best "
      "FDR-surviving indicator in that category on full history. This is "
      "**best-in-slot on flat history only** — NOT regime-validated, NOT a "
      "confirmed production choice. Regime-cell conditioning is the next run.")
    A("")
    for tkr, meta in ASSETS.items():
        info = loaded.get(tkr)
        if not info or info["df"] is None:
            continue
        sub = df[df.asset == tkr]
        A(f"## {tkr} — {meta['name']} ({meta['class']})")
        if info["df"] is not None and len(info["df"]) < MIN_ROWS:
            A(f"_low confidence: {len(info['df'])} rows < MIN_ROWS={MIN_ROWS}_")
        for slot in SLOTS:
            A(f"\n### {slot} slot")
            slot_rows = sub[sub.slot == slot]
            cont = slot_rows[(slot_rows.indicator_type == "continuous") &
                             (slot_rows.ic_ir.notna())].copy()
            disc = slot_rows[(slot_rows.indicator_type == "discrete") &
                             (slot_rows.ic_or_spread.notna()) &
                             (~slot_rows.note.astype(str).str.startswith("UNTRUSTED"))].copy()

            # volume slot N/A on volumeless assets
            if slot == "Volume" and not info["has_volume"]:
                A("_Volume slot N/A — no real volume for this series._")
                continue

            # leaderboard (continuous by |IC_IR|)
            if len(cont):
                cont["absir"] = cont.ic_ir.abs()
                best = cont.sort_values("absir", ascending=False).head(6)
                A("")
                A("| indicator | h | IC | IC_IR | p | survives_fdr | n |")
                A("|---|---:|---:|---:|---:|:--:|---:|")
                for _, r in best.iterrows():
                    A(f"| {r.indicator_id} | {int(r.horizon)} | {r.ic_or_spread:.4f} | "
                      f"{r.ic_ir:.3f} | {r.p_value:.2e} | "
                      f"{'yes' if r.survives_fdr==True else 'no'} | {int(r.n_obs)} |")
            if len(disc):
                disc["absp"] = disc.ic_or_spread.abs()
                bestd = disc.sort_values("absp", ascending=False).head(4)
                A("")
                A("| discrete signal | h | expectancy spread | n(min state) |")
                A("|---|---:|---:|---:|")
                for _, r in bestd.iterrows():
                    A(f"| {r.indicator_id} | {int(r.horizon)} | "
                      f"{r.ic_or_spread:+.5f} | {int(r.n_obs)} |")

            # provisional winner = best FDR-surviving continuous in slot
            surv = cont[cont.survives_fdr == True]
            if len(surv):
                w = surv.sort_values("absir", ascending=False).iloc[0]
                p = prior.get(w.indicator_id, {})
                chk = _prior_check(p.get("shock_behavior", "?"), True)
                A("")
                A(f"**Slot winner: {w.indicator_id}** (h={int(w.horizon)}, "
                  f"IC={w.ic_or_spread:.4f}, IC_IR={w.ic_ir:.3f}). {chk}.")
            else:
                A("")
                A("**NO SLOT WINNER — nothing in this category survives FDR.**")
        A("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"[write] {path}")


def write_slot_summary(df, roster, fdr_stats):
    n_tests, raw_sig, n_survive = fdr_stats
    prior = {e["id"]: e for e in roster}
    path = os.path.join(RESULTS_DIR, "slot_summary_by_assetclass.md")
    L = []; A = L.append
    A("# Slot Summary by Asset Class — who wins each slot, across assets")
    A("")
    A("> **FLAT / non-regime-conditioned.** 'Wins most often' = most FDR-surviving "
      "best-in-slot finishes across the assets in that class, on full history. This "
      "is the closest thing to actionable, but it is still not regime-validated.")
    A("")
    A(f"- Continuous IC tests with valid p-value: **{n_tests}**  |  raw p<0.05: "
      f"**{raw_sig}**  |  survive FDR@{FDR_Q}: **{n_survive}**")
    A("")

    # compute, per (asset, slot), the winning continuous FDR-survivor
    cont = df[(df.indicator_type == "continuous") & (df.ic_ir.notna())].copy()
    cont["absir"] = cont.ic_ir.abs()
    winners = []  # (asset_class, slot, indicator_id)
    for (asset, slot), g in cont.groupby(["asset", "slot"]):
        surv = g[g.survives_fdr == True]
        if len(surv):
            w = surv.sort_values("absir", ascending=False).iloc[0]
            winners.append((g.asset_class.iloc[0], slot, w.indicator_id))
    wdf = pd.DataFrame(winners, columns=["asset_class", "slot", "indicator_id"])

    for aclass in sorted(df.asset_class.unique()):
        A(f"## {aclass}")
        for slot in SLOTS:
            sub = wdf[(wdf.asset_class == aclass) & (wdf.slot == slot)]
            A(f"\n### {slot} slot")
            if len(sub) == 0:
                A("_No FDR-surviving winner in this slot for any asset in this class._")
                continue
            counts = sub.indicator_id.value_counts()
            A("")
            A("| indicator | winning assets | shock prior | prior check |")
            A("|---|---:|:--:|---|")
            for iid, cnt in counts.items():
                sb = prior.get(iid, {}).get("shock_behavior", "?")
                verdict = ("AGREES" if sb == "MAINTAIN"
                           else "DISAGREES(regime-mask?)" if sb == "SUPPRESS"
                           else "PARTIAL" if sb == "SUBSTITUTE" else "?")
                A(f"| {iid} | {cnt} | {sb} | {verdict} |")
        A("")

    A("## NOTES")
    A("- **FLAT screen caveat:** an indicator strong only in one regime can show "
      "near-zero flat IC and be wrongly demoted here. This screen finds best-in-slot "
      "on full history; it cannot promote anything to regime-validated.")
    A("- **Prior check semantics:** MAINTAIN winner = library prior AGREES; SUPPRESS "
      "winner = DISAGREES, flag as possible regime-masking for the regime run; "
      "SUBSTITUTE winner = PARTIAL (a second-string indicator leading flat).")
    A("- **^TNX** is yield-based (forward change in yield), not price returns.")
    A("- **CL=F** is a continuous front-month stitch; roll artifacts possible.")
    A(f"- **Deferred (not fetched):** {', '.join(DEFERRED.keys())}.")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"[write] {path}")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def load_all():
    loaded = {}
    failed = []
    for tkr, meta in ASSETS.items():
        print(f"  fetching {tkr} ({meta['name']}) ...")
        try:
            df = data_loader.load_ohlcv(tkr)
        except Exception as exc:
            print(f"    error {tkr}: {exc!r}")
            df = None
        if df is not None:
            df = df[df.index >= pd.Timestamp(START)]      # apply START cap
            if len(df) == 0:
                df = None
        if df is None:
            failed.append(tkr)
            loaded[tkr] = {"df": None, "has_volume": False}
        else:
            loaded[tkr] = {"df": df, "has_volume": _has_volume(df)}
    return loaded, failed


def main(preflight_only: bool = False) -> int:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    roster, skipped = parse_library(LIBRARY_MD)
    print(f"Parsed library: {len(roster)} indicators resolved, {len(skipped)} skipped.")
    preflight_roster(roster, skipped)

    print("\nFetching data (yfinance, max history capped at START) ...")
    loaded, failed = load_all()
    preflight_coverage(loaded)

    if preflight_only:
        print("\n[preflight-only] stopping before full IC computation.")
        return 0

    all_rows = []
    for tkr, meta in ASSETS.items():
        info = loaded.get(tkr)
        if not info or info["df"] is None:
            continue
        try:
            rows = process_asset(tkr, meta, info["df"], info["has_volume"], roster)
            all_rows.extend(rows)
            print(f"  processed {tkr}: {len(rows)} rows")
        except Exception:
            print(f"  ERROR processing {tkr}:")
            traceback.print_exc()

    if not all_rows:
        print("No results. Abort.")
        return 1

    df = pd.DataFrame(all_rows)
    df, n_tests, raw_sig, n_survive = apply_fdr(df)
    df = df.sort_values(["asset_class", "asset", "slot", "indicator_id", "horizon"]
                        ).reset_index(drop=True)

    csv_path = os.path.join(RESULTS_DIR, "grouped_ic_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"[write] {csv_path} ({len(df)} rows)")

    write_best_in_slot(df, roster, loaded)
    write_slot_summary(df, roster, (n_tests, raw_sig, n_survive))

    print(f"\nDONE. continuous tests={n_tests} raw p<0.05={raw_sig} "
          f"survive FDR@{FDR_Q}={n_survive}")
    print(f"assets processed={sum(1 for i in loaded.values() if i['df'] is not None)}"
          f"/{len(ASSETS)} failed={len(failed)}")
    return 0


if __name__ == "__main__":
    pf = "--preflight" in sys.argv
    sys.exit(main(preflight_only=pf))
