"""
main.py
=======
Flat (non-regime-conditioned) first-pass IC / expectancy KILL-SCREEN across
liquid global assets and a curated TA-Lib indicator set.

WHAT THIS IS:  a cheap filter to eliminate obviously-useless indicator/asset
pairings before any regime-conditioned testing.
WHAT THIS IS NOT:  validation. Surviving this screen means "not obviously
useless", never "good" or "validated for trading". See NOTES in the summary.

Run:  python main.py
Outputs:
  ./results/flat_ic_results.csv
  ./results/summary_by_assetclass.md
"""

from __future__ import annotations

import os
import sys
import traceback

import numpy as np
import pandas as pd

import data_loader
import indicators as ind
import stats as st


# ==========================================================================
# CONFIG BLOCK  (edit freely; no logic below depends on hard-coded values)
# ==========================================================================
HORIZONS       = [1, 5, 10, 20]      # forward-return horizons in trading days
ROLL_WINDOW    = 63                   # rolling-IC window for IC_IR
FDR_Q          = 0.10                 # Benjamini-Hochberg false discovery rate
MIN_ROWS       = 500                  # below this, asset flagged low-confidence
MIN_PATTERN_N  = 30                   # discrete state needs >= this many obs

# Assets. return_mode: "log" (price) or "diff" (level/yield). Default "log".
ASSETS = {
    # Equities
    "^GSPC":     {"name": "S&P 500",       "class": "equity"},
    "^NDX":      {"name": "Nasdaq 100",     "class": "equity"},
    "^STOXX50E": {"name": "Euro Stoxx 50",  "class": "equity"},
    "^FTSE":     {"name": "FTSE 100",       "class": "equity"},
    "^GDAXI":    {"name": "DAX",            "class": "equity"},
    "^N225":     {"name": "Nikkei 225",     "class": "equity"},
    "^KS11":     {"name": "KOSPI",          "class": "equity"},
    "^HSI":      {"name": "Hang Seng",      "class": "equity"},
    # Rates / credit
    "^TNX":      {"name": "US 10Y yield",   "class": "rates",
                  "return_mode": "diff",
                  "note": "YIELD-based series; fwd 'returns' = fwd change in yield"},
    "TLT":       {"name": "US 20Y+ UST",    "class": "rates",
                  "note": "price proxy; cross-check vs ^TNX"},
    "LQD":       {"name": "IG corporate",   "class": "credit"},
    "HYG":       {"name": "HY corporate",   "class": "credit"},
    # Metals
    "GC=F":      {"name": "Gold",           "class": "metals"},
    "SI=F":      {"name": "Silver",         "class": "metals"},
    # Energy
    "CL=F":      {"name": "WTI crude",      "class": "energy",
                  "note": "continuous front-month stitch (roll artifacts possible)"},
    # FX
    "DX-Y.NYB":  {"name": "USD index",      "class": "fx"},
    "EURUSD=X":  {"name": "EUR/USD",        "class": "fx"},
    "CHF=X":     {"name": "USD/CHF",        "class": "fx"},
}

# Indicator route overrides (per-asset). Reserved hook: e.g. force-skip a volume
# indicator on a specific ticker. Empty by default; the engine already auto-skips
# volume indicators on volume-less series.
INDICATOR_OVERRIDES: dict[str, dict] = {}

# Assets deliberately NOT fetched this run (unreliable yfinance coverage).
DEFERRED = {
    "STAR 50":     "deferred pending data API",
    "CSI 300 native": "deferred pending data API",
    "HSI Tech":    "deferred pending data API",
}

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
# ==========================================================================


def _return_mode(meta: dict) -> str:
    return meta.get("return_mode", "log")


def _has_volume(df: pd.DataFrame) -> bool:
    """True if the series carries real volume (not a zero/NaN placeholder)."""
    v = df["volume"].to_numpy()
    return np.isfinite(v).any() and np.nansum(v) > 0


def preflight(loaded: dict) -> None:
    """Print resolved ticker, date range, row count, flags before the full run."""
    print("\n" + "=" * 78)
    print("PRE-FLIGHT COVERAGE TABLE")
    print("=" * 78)
    hdr = f"{'ticker':<11}{'name':<16}{'class':<8}{'start':<12}{'end':<12}{'rows':>7}  flags"
    print(hdr)
    print("-" * 78)
    for tkr, meta in ASSETS.items():
        info = loaded.get(tkr)
        if info is None or info["df"] is None:
            print(f"{tkr:<11}{meta['name'][:15]:<16}{meta['class']:<8}"
                  f"{'-':<12}{'-':<12}{0:>7}  FETCH FAILED / SKIPPED")
            continue
        d = data_loader.describe(info["df"])
        flags = []
        if d["rows"] < MIN_ROWS:
            flags.append("LOW_CONFIDENCE")
        if _return_mode(meta) == "diff":
            flags.append("YIELD/diff-returns")
        if not info["has_volume"]:
            flags.append("no-volume")
        print(f"{tkr:<11}{meta['name'][:15]:<16}{meta['class']:<8}"
              f"{str(d['start']):<12}{str(d['end']):<12}{d['rows']:>7}  "
              f"{', '.join(flags)}")
    print("-" * 78)
    if DEFERRED:
        print("DEFERRED (not fetched this run):")
        for name, why in DEFERRED.items():
            print(f"    {name:<18} -> {why}")
    print("=" * 78 + "\n")


def process_asset(tkr: str, meta: dict, df: pd.DataFrame, has_volume: bool) -> list[dict]:
    """Compute all continuous + discrete rows for one asset. Returns row dicts."""
    o = df["open"].to_numpy("float64")
    h = df["high"].to_numpy("float64")
    l = df["low"].to_numpy("float64")
    c = df["close"].to_numpy("float64")
    v = df["volume"].to_numpy("float64")

    mode = _return_mode(meta)
    n_rows = len(df)
    low_conf = n_rows < MIN_ROWS
    asset_class = meta["class"]
    overrides = INDICATOR_OVERRIDES.get(tkr, {})

    # Precompute forward returns per horizon (+ lookahead guard).
    fwd = {}
    for hh in HORIZONS:
        f = st.forward_returns(c, hh, mode=mode)
        st.assert_no_lookahead(f, hh)
        fwd[hh] = f

    rows: list[dict] = []

    # ---- CONTINUOUS -> Spearman IC ----
    for iname, (fn, uses_vol) in ind.CONTINUOUS.items():
        if overrides.get(iname) == "skip":
            continue
        vol_note = ""
        if uses_vol and not has_volume:
            # Compute anyway would be degenerate; skip with an explicit note row.
            for hh in HORIZONS:
                rows.append(_row(tkr, asset_class, iname, "continuous", hh,
                                 np.nan, np.nan, 0, np.nan, False, low_conf,
                                 "skipped: volume indicator on volume-less series"))
            continue
        try:
            x = np.asarray(fn(o, h, l, c, v), dtype="float64")
        except Exception as exc:
            for hh in HORIZONS:
                rows.append(_row(tkr, asset_class, iname, "continuous", hh,
                                 np.nan, np.nan, 0, np.nan, False, low_conf,
                                 f"indicator error: {exc!r}"))
            continue

        for hh in HORIZONS:
            y = fwd[hh]
            ic, tstat, pval, nobs = st.spearman_ic_hac(x, y, lag=hh)
            roll = st.rolling_spearman(x, y, ROLL_WINDOW)
            ic_ir = st.ic_ir_hac(roll, lag=hh)
            note = vol_note
            if mode == "diff":
                note = (note + "; " if note else "") + "fwd = yield change"
            rows.append(_row(tkr, asset_class, iname, "continuous", hh,
                             ic, ic_ir, nobs, pval, None, low_conf, note))

    # ---- DISCRETE -> expectancy per state ----
    for iname, (fn, type_label, bull_lbl, bear_lbl) in ind.DISCRETE.items():
        if overrides.get(iname) == "skip":
            continue
        try:
            state = np.asarray(fn(o, h, l, c, v), dtype="float64")
        except Exception as exc:
            for hh in HORIZONS:
                rows.append(_row(tkr, asset_class, iname, type_label, hh,
                                 np.nan, np.nan, 0, np.nan, None, low_conf,
                                 f"indicator error: {exc!r}"))
            continue

        for hh in HORIZONS:
            y = fwd[hh]
            r = st.discrete_expectancy(state, y, MIN_PATTERN_N)
            note = (
                f"{bull_lbl}: n={r['bull']['n']} mean={_f(r['bull']['mean'])} "
                f"hit={_f(r['bull']['hit'])} | "
                f"{bear_lbl}: n={r['bear']['n']} mean={_f(r['bear']['mean'])} "
                f"hit={_f(r['bear']['hit'])}"
            )
            if not r["trusted"]:
                note = "UNTRUSTED (state n<MIN_PATTERN_N) | " + note
            if mode == "diff":
                note = note + " | fwd = yield change"
            rows.append(_row(tkr, asset_class, iname, type_label, hh,
                             r["spread"], np.nan, r["n_min"], np.nan,
                             None, low_conf, note))
    return rows


def _f(x) -> str:
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.5f}"


def _row(asset, asset_class, indicator, itype, horizon, ic_or_spread, ic_ir,
         n_obs, p_value, survives_fdr, low_conf, note) -> dict:
    return {
        "asset": asset,
        "asset_class": asset_class,
        "indicator": indicator,
        "indicator_type": itype,
        "horizon": horizon,
        "ic_or_spread": ic_or_spread,
        "ic_ir": ic_ir,
        "n_obs": n_obs,
        "p_value": p_value,
        "survives_fdr": survives_fdr,
        "low_confidence": bool(low_conf),
        "note": note,
    }


def apply_fdr(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int, int]:
    """BH-FDR across ALL continuous tests with a finite p-value."""
    is_cont = df["indicator_type"] == "continuous"
    has_p = df["p_value"].notna()
    pool = is_cont & has_p
    n_tests = int(pool.sum())
    raw_sig = int((df.loc[pool, "p_value"] < 0.05).sum())

    survive = st.benjamini_hochberg(df.loc[pool, "p_value"].to_numpy(), FDR_Q)
    df.loc[pool, "survives_fdr"] = survive
    # discrete + skipped continuous rows: not part of FDR pool -> leave as NA
    df.loc[is_cont & ~has_p, "survives_fdr"] = False
    n_survive = int(survive.sum())
    return df, n_tests, raw_sig, n_survive


def write_summary(df: pd.DataFrame, loaded: dict, fdr_stats: tuple,
                  failed: list[str]) -> None:
    n_tests, raw_sig, n_survive = fdr_stats
    path = os.path.join(RESULTS_DIR, "summary_by_assetclass.md")
    lines: list[str] = []
    A = lines.append

    A("# Flat IC / Expectancy Kill-Screen — Summary by Asset Class")
    A("")
    A("> **FLAT, non-regime-conditioned first-pass filter.** Surviving here means "
      "*not obviously useless* — it does **not** mean validated, tradable, or good. "
      "This screen can only remove the broadly useless; it cannot promote anything.")
    A("")
    A(f"- Continuous IC tests with a valid p-value: **{n_tests}**")
    A(f"- Look significant raw (p < 0.05): **{raw_sig}**")
    A(f"- Survive Benjamini-Hochberg FDR at q={FDR_Q}: **{n_survive}**")
    if n_tests:
        A(f"- Raw-vs-FDR gives a sense of the noise floor: {raw_sig} raw "
          f"vs {n_survive} after multiple-comparison control.")
    A("")

    cont = df[df["indicator_type"] == "continuous"].copy()
    disc = df[df["indicator_type"].str.startswith("discrete")].copy()

    for aclass in sorted(df["asset_class"].unique()):
        A(f"## {aclass}")
        # headline: exclude low-confidence assets from rankings
        cc = cont[(cont["asset_class"] == aclass) &
                  (~cont["low_confidence"]) &
                  (cont["survives_fdr"] == True) &
                  (cont["ic_ir"].notna())].copy()
        A("")
        A("### Top surviving CONTINUOUS indicators (by |IC_IR|, FDR-survivors only)")
        if len(cc) == 0:
            A("_None survived FDR in this class (from full-confidence assets)._")
        else:
            cc["abs_ir"] = cc["ic_ir"].abs()
            cc = cc.sort_values("abs_ir", ascending=False).head(12)
            A("")
            A("| asset | indicator | h | IC | IC_IR | p | n |")
            A("|---|---|---:|---:|---:|---:|---:|")
            for _, r in cc.iterrows():
                A(f"| {r['asset']} | {r['indicator']} | {r['horizon']} | "
                  f"{r['ic_or_spread']:.4f} | {r['ic_ir']:.3f} | "
                  f"{r['p_value']:.2e} | {int(r['n_obs'])} |")
        A("")
        # discrete: separate list, by |spread|, trusted states only
        dd = disc[(disc["asset_class"] == aclass) &
                  (~disc["low_confidence"]) &
                  (~disc["note"].str.startswith("UNTRUSTED")) &
                  (disc["ic_or_spread"].notna())].copy()
        A("### Top DISCRETE signals (by |expectancy spread|, trusted states only)")
        A("_Spread = forward-return expectancy of bullish state minus bearish "
          "state. This is an expectancy in return units, NOT a correlation._")
        if len(dd) == 0:
            A("_No trusted discrete signals in this class._")
        else:
            dd["abs_sp"] = dd["ic_or_spread"].abs()
            dd = dd.sort_values("abs_sp", ascending=False).head(8)
            A("")
            A("| asset | signal | h | spread | n(min state) |")
            A("|---|---|---:|---:|---:|")
            for _, r in dd.iterrows():
                A(f"| {r['asset']} | {r['indicator']} | {r['horizon']} | "
                  f"{r['ic_or_spread']:+.5f} | {int(r['n_obs'])} |")
        A("")

    # ---------------- NOTES ----------------
    A("## NOTES (read before trusting anything above)")
    A("")
    A("**This is a FLAT, non-regime-conditioned screen.** An indicator that only "
      "works in one regime (e.g. only in high-volatility or only in trending "
      "markets) can average out to near-zero IC over full history and be wrongly "
      "killed here. This screen removes the *broadly* useless; it cannot promote "
      "anything to 'good'. **Regime-conditioned testing is the required next step.**")
    A("")

    # low-confidence assets
    lowc = sorted({r["asset"] for _, r in df[df["low_confidence"]].iterrows()})
    if lowc:
        A(f"- **Low-confidence assets (rows < {MIN_ROWS}, excluded from headline "
          f"rankings):** {', '.join(lowc)}")
    # failed
    if failed:
        A(f"- **Fetch failed / skipped (never crashed the run):** {', '.join(failed)}")
    # deferred
    if DEFERRED:
        A(f"- **Deferred China assets (not fetched, intentional gap):** "
          f"{', '.join(DEFERRED.keys())} — {list(DEFERRED.values())[0]}.")
    # yield
    A("- **^TNX / rates:** ^TNX is a **yield** series; its indicators are computed "
      "on the yield level and its 'forward returns' are forward **changes in "
      "yield**, not price returns. Do not read ^TNX rows on the same scale as "
      "equity/price rows. TLT is a price proxy for long UST and should move "
      "inversely to ^TNX — use it as a cross-check.")
    # CL=F
    A("- **CL=F (WTI crude):** a continuous front-month stitch; roll gaps can "
      "inject artifacts into short-horizon returns. Treat CL=F short-horizon "
      "results with extra caution.")
    # volume-less
    volless = sorted({tkr for tkr, info in loaded.items()
                      if info and info.get("df") is not None and not info["has_volume"]})
    if volless:
        A(f"- **Volume-less series** (volume indicators OBV/AD/ADOSC/MFI skipped): "
          f"{', '.join(volless)}.")

    # broadly-useless indicators (survive FDR almost nowhere)
    surv_by_ind = (cont[cont["survives_fdr"] == True]
                   .groupby("indicator").size())
    all_inds = list(ind.CONTINUOUS.keys())
    useless = sorted([i for i in all_inds if surv_by_ind.get(i, 0) == 0])
    if useless:
        A(f"- **Continuous indicators surviving FDR on NOTHING across all assets/"
          f"horizons (broadly useless in this flat screen):** {', '.join(useless)}.")
    thin = sorted([i for i in all_inds if 0 < surv_by_ind.get(i, 0) <= 2])
    if thin:
        A(f"- **Survive FDR on almost nothing (<=2 cells):** {', '.join(thin)}.")

    # excluded indicators (auditable)
    A("")
    A("### Excluded indicator groups (kept auditable, not tested)")
    for what, why in ind.EXCLUDED.items():
        A(f"- **{what}** — {why}")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"[write] {path}")


def main() -> int:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Flat IC kill-screen — fetching data (yfinance, max daily history)...")

    loaded: dict[str, dict] = {}
    failed: list[str] = []
    for tkr, meta in ASSETS.items():
        print(f"  fetching {tkr} ({meta['name']}) ...")
        try:
            df = data_loader.load_ohlcv(tkr)
        except Exception as exc:
            print(f"    unexpected error {tkr}: {exc!r}")
            df = None
        if df is None:
            failed.append(tkr)
            loaded[tkr] = {"df": None, "has_volume": False}
        else:
            loaded[tkr] = {"df": df, "has_volume": _has_volume(df)}

    preflight(loaded)

    all_rows: list[dict] = []
    for tkr, meta in ASSETS.items():
        info = loaded.get(tkr)
        if info is None or info["df"] is None:
            continue
        try:
            rows = process_asset(tkr, meta, info["df"], info["has_volume"])
            all_rows.extend(rows)
            print(f"  processed {tkr}: {len(rows)} rows")
        except Exception:
            print(f"  ERROR processing {tkr} — skipped:")
            traceback.print_exc()
            continue

    if not all_rows:
        print("No results produced. Aborting.")
        return 1

    df = pd.DataFrame(all_rows)
    df, n_tests, raw_sig, n_survive = apply_fdr(df)

    # stable ordering
    df = df.sort_values(["asset_class", "asset", "indicator_type",
                         "indicator", "horizon"]).reset_index(drop=True)

    csv_path = os.path.join(RESULTS_DIR, "flat_ic_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"[write] {csv_path}  ({len(df)} rows)")

    write_summary(df, loaded, (n_tests, raw_sig, n_survive), failed)

    print("\nDONE.")
    print(f"  continuous tests (valid p): {n_tests} | raw p<0.05: {raw_sig} | "
          f"survive FDR@{FDR_Q}: {n_survive}")
    print(f"  assets processed: {sum(1 for i in loaded.values() if i['df'] is not None)}"
          f" / {len(ASSETS)} | failed: {len(failed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
