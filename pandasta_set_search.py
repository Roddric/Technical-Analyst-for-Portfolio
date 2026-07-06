"""
pandasta_set_search.py
======================
Stage 1: per-asset, per-slot IC screen of pandas_ta candidates (defaults only).
Stage 2: joint set search — composite of one survivor per slot, scored with
the same HAC machinery. Two selection windows: OOS (<=2023-12-31) and IS
(full history). See docs/superpowers/specs/2026-07-06-pandasta-set-search-design.md.

Run:
    python pandasta_set_search.py             # both cutoffs, all assets
    python pandasta_set_search.py --smoke     # ^GSPC only, OOS cutoff
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd

import stats as st
from pandasta_data import UNIVERSE, load_asset, return_mode, volume_usable
from pandasta_registry import SLOTS, build_candidates, compute_candidate

HORIZONS = [1, 5, 10, 20]
ROLL_WINDOW = 63
FDR_Q = 0.10
MIN_COVERAGE = 0.30     # candidate must be non-NaN on >=30% of post-warmup bars
Z_WINDOW, Z_MIN = 252, 126
TOP_K_PER_SLOT = 5
STRATEGY_H = 20

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

OOS_CUTOFF = "2023-12-31"


def _candidate_values(tkr: str, df: pd.DataFrame) -> dict[str, tuple[str, pd.Series]]:
    """name -> (slot, values) for every computable candidate on this asset."""
    vol_ok, vol_masked = volume_usable(df)
    work = df.copy()
    work["volume"] = vol_masked
    out = {}
    for cand in build_candidates():
        if cand.uses_volume and not vol_ok:
            continue
        try:
            x = compute_candidate(work, cand)
        except Exception as e:  # noqa: BLE001 — any indicator failure is a skip
            print(f"    skip {tkr} {cand.name}: {type(e).__name__}: {e}")
            continue
        tail = x.iloc[Z_MIN:]
        if len(tail) == 0 or tail.notna().mean() < MIN_COVERAGE:
            continue
        out[cand.name] = (cand.slot, x)
    return out


def indicator_series_cache(tkr: str, cutoff: str | None) -> tuple[pd.DataFrame, dict]:
    df = load_asset(tkr)
    if df is None:
        raise FileNotFoundError(f"no cached data for {tkr}")
    if cutoff is not None:
        df = df.loc[:cutoff]
    return df, _candidate_values(tkr, df)


def _screen_one_asset(tkr: str, klass: str, df: pd.DataFrame, mode: str,
                      values: dict | None = None) -> list[dict]:
    close = df["close"].to_numpy(dtype="float64")
    if values is None:
        values = _candidate_values(tkr, df)
    fwd = {}
    for h in HORIZONS:
        y = st.forward_returns(close, h, mode)
        st.assert_no_lookahead(y, h)
        fwd[h] = y
    rows = []
    for name, (slot, xs) in values.items():
        x = xs.to_numpy(dtype="float64")
        for h in HORIZONS:
            y = fwd[h]
            ic, t, p, n = st.spearman_ic_hac(x, y, lag=h)
            roll = st.rolling_spearman(x, y, ROLL_WINDOW)
            ic_ir = st.ic_ir_hac(roll, lag=h)
            rows.append({"asset": tkr, "asset_class": klass, "indicator": name,
                         "slot": slot, "horizon": h, "ic": ic, "ic_ir": ic_ir,
                         "n_obs": n, "p_value": p, "note": ""})
    return rows


def run_stage1(cutoff: str | None, tickers: list[str] | None = None) -> pd.DataFrame:
    tickers = tickers or list(UNIVERSE)
    all_rows = []
    for tkr in tickers:
        meta = UNIVERSE[tkr]
        print(f"  stage1 {tkr} (cutoff={cutoff}) ...")
        try:
            df, values = indicator_series_cache(tkr, cutoff)
        except FileNotFoundError:
            print(f"  SKIP {tkr}: no cached data")
            continue
        all_rows.extend(_screen_one_asset(tkr, meta["class"], df,
                                          return_mode(tkr), values))
    out = pd.DataFrame(all_rows)
    pool = out["p_value"].notna()
    out["survives_fdr"] = False
    out.loc[pool, "survives_fdr"] = st.benjamini_hochberg(
        out.loc[pool, "p_value"].to_numpy(), FDR_Q)
    out["survives_fdr"] = out["survives_fdr"].astype(bool)
    return out


def causal_zscore(x: pd.Series) -> pd.Series:
    mu = x.rolling(Z_WINDOW, min_periods=Z_MIN).mean()
    sd = x.rolling(Z_WINDOW, min_periods=Z_MIN).std()
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (x - mu) / sd
    return z.replace([np.inf, -np.inf], np.nan)


def composite_signal(members: list[pd.Series], signs: list[float]) -> pd.Series:
    zs = [causal_zscore(m) * s for m, s in zip(members, signs)]
    mat = pd.concat(zs, axis=1)
    return mat.mean(axis=1)          # NaN-tolerant mean across available members


def _top_k_per_slot(s1_asset: pd.DataFrame) -> tuple[dict[str, list[str]], set[str]]:
    """slot -> up to TOP_K_PER_SLOT indicator names, plus the set of slots
    that had to fall back to a non-survivor pick.

    Preferred: FDR survivors, ranked by max |ic_ir| across horizons, top
    TOP_K_PER_SLOT. Fallback: if a slot has stage-1 rows but zero survivors,
    take the single best indicator in that slot by max |ic_ir| (ignoring NaN
    ic_ir rows; if all NaN, use max |ic|). A slot with no stage-1 rows at
    all is never fabricated and stays absent."""
    surv = s1_asset[s1_asset["survives_fdr"]]
    picks: dict[str, list[str]] = {}
    fallback_slots: set[str] = set()
    for slot in SLOTS:
        all_sl = s1_asset[s1_asset["slot"] == slot]
        if all_sl.empty:
            continue
        sl = surv[surv["slot"] == slot]
        if not sl.empty:
            ranked = (sl.assign(a=sl["ic_ir"].abs())
                        .groupby("indicator")["a"].max()
                        .sort_values(ascending=False))
            picks[slot] = list(ranked.index[:TOP_K_PER_SLOT])
            continue
        # fallback: no survivors, but stage-1 rows exist for this slot
        ranked_ir = (all_sl.assign(a=all_sl["ic_ir"].abs())
                          .groupby("indicator")["a"].max()
                          .sort_values(ascending=False))
        ranked_ir = ranked_ir[ranked_ir.notna()]
        if not ranked_ir.empty:
            best = ranked_ir.index[0]
        else:
            ranked_ic = (all_sl.assign(a=all_sl["ic"].abs())
                              .groupby("indicator")["a"].max()
                              .sort_values(ascending=False))
            best = ranked_ic.index[0]
        picks[slot] = [best]
        fallback_slots.add(slot)
    return picks, fallback_slots


def _stage1_sign(s1_asset: pd.DataFrame, indicator: str) -> float:
    """Sign of stage-1 IC at h=STRATEGY_H (fallback: horizon with max |ic|)."""
    rows = s1_asset[s1_asset["indicator"] == indicator]
    at_h = rows[rows["horizon"] == STRATEGY_H]
    r = at_h.iloc[0] if len(at_h) else rows.loc[rows["ic"].abs().idxmax()]
    return 1.0 if (r["ic"] >= 0 or np.isnan(r["ic"])) else -1.0


def run_stage2(stage1_df: pd.DataFrame, cutoff: str | None,
               tickers: list[str] | None = None) -> pd.DataFrame:
    tickers = tickers or sorted(stage1_df["asset"].unique())
    rows = []
    for tkr in tickers:
        s1 = stage1_df[stage1_df["asset"] == tkr]
        klass = UNIVERSE.get(tkr, {"class": "synthetic"})["class"]
        picks, fallback_slots = _top_k_per_slot(s1)
        if not picks:
            print(f"  stage2 {tkr}: no FDR survivors in any slot — skipped")
            continue
        try:
            df, values = indicator_series_cache(tkr, cutoff)
        except FileNotFoundError:
            print(f"  SKIP {tkr}: no cached data")
            continue
        close = df["close"].to_numpy(dtype="float64")
        mode = return_mode(tkr) if tkr in UNIVERSE else "log"
        fwd = {h: st.forward_returns(close, h, mode) for h in HORIZONS}
        for h in HORIZONS:
            st.assert_no_lookahead(fwd[h], h)
        slots_used = [s for s in SLOTS if s in picks]
        fallback_str = ",".join(s for s in slots_used if s in fallback_slots)
        print(f"  stage2 {tkr}: slots={slots_used} "
              f"combos={np.prod([len(picks[s]) for s in slots_used])}"
              + (f" fallback={fallback_str}" if fallback_str else ""))
        best_key, best_val = None, -np.inf
        for combo in itertools.product(*(picks[s] for s in slots_used)):
            members = [values[name][1] for name in combo]
            signs = [_stage1_sign(s1, name) for name in combo]
            comp = composite_signal(members, signs).to_numpy(dtype="float64")
            zmat = pd.concat([causal_zscore(m) for m in members], axis=1)
            red = zmat.corr(method="spearman").abs()
            k = len(combo)
            redundancy = (float((red.sum().sum() - k) / (k * (k - 1)))
                          if k > 1 else np.nan)
            by_slot = dict(zip(slots_used, combo))
            for h in HORIZONS:
                ic, t, p, n = st.spearman_ic_hac(comp, fwd[h], lag=h)
                roll = st.rolling_spearman(comp, fwd[h], ROLL_WINDOW)
                ic_ir = st.ic_ir_hac(roll, lag=h)
                rows.append({
                    "asset": tkr, "asset_class": klass,
                    "cutoff": cutoff or "FULL",
                    "volume_ind": by_slot.get("volume", ""),
                    "trend_ind": by_slot.get("trend", ""),
                    "momentum_ind": by_slot.get("momentum", ""),
                    "volatility_ind": by_slot.get("volatility", ""),
                    "n_slots": k, "horizon": h,
                    "comp_ic": ic, "comp_p": p, "comp_ic_ir": ic_ir,
                    "redundancy": redundancy,
                    "traded_sign": 1.0 if (np.isnan(ic) or ic >= 0) else -1.0,
                    "is_winner": False,
                    "fdr_fallback_slots": fallback_str,
                })
                if h == STRATEGY_H and np.isfinite(ic_ir) and abs(ic_ir) > best_val:
                    best_val, best_key = abs(ic_ir), len(rows) - 1
        if best_key is not None:
            rows[best_key]["is_winner"] = True
        else:
            print(f"  stage2 {tkr}: no finite composite IC_IR at h={STRATEGY_H} — no winner emitted")
    return pd.DataFrame(rows)


def _write_best_sets_md(best: pd.DataFrame, path: str) -> None:
    lines = ["# pandas_ta best indicator sets (per asset)", "",
             "> Flat-history selection, defaults-only, FDR q=0.10. "
             "OOS = selection on data <= 2023-12-31; FULL = in-sample upper "
             "bound (NOT a forecast). ICs are small in absolute terms; "
             "composite signals are screened, not regime-conditioned.", ""]
    for cutoff, grp in best.groupby("cutoff"):
        lines.append(f"## Selection window: {cutoff}")
        lines.append("")
        lines.append("| asset | class | volume | trend | momentum | volatility "
                     "| h | comp_IC | comp_IC_IR | redundancy | sign | fallback |")
        lines.append("|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|")
        for _, r in grp[grp["is_winner"]].sort_values("asset").iterrows():
            fallback_col = r.get("fdr_fallback_slots", "") or "-"
            lines.append(
                f"| {r['asset']} | {r['asset_class']} | {r['volume_ind'] or '-'} "
                f"| {r['trend_ind'] or '-'} | {r['momentum_ind'] or '-'} "
                f"| {r['volatility_ind'] or '-'} | {r['horizon']} "
                f"| {r['comp_ic']:+.4f} | {r['comp_ic_ir']:+.3f} "
                f"| {r['redundancy']:.2f} | {r['traded_sign']:+.0f} "
                f"| {fallback_col} |")
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="^GSPC, OOS only")
    args = ap.parse_args()
    os.makedirs(RESULTS, exist_ok=True)
    tickers = ["^GSPC"] if args.smoke else None
    s1_frames, s2_frames = [], []
    for cutoff in ([OOS_CUTOFF] if args.smoke else [OOS_CUTOFF, None]):
        label = cutoff or "FULL"
        print(f"=== stage 1 (cutoff={label}) ===")
        s1 = run_stage1(cutoff, tickers)
        s1["cutoff"] = label
        s1_frames.append(s1)
        print(f"=== stage 2 (cutoff={label}) ===")
        s2_frames.append(run_stage2(s1, cutoff, tickers))
    pd.concat(s1_frames).to_csv(os.path.join(RESULTS, "pandasta_stage1_ic.csv"),
                                index=False)
    best = pd.concat(s2_frames)
    best.to_csv(os.path.join(RESULTS, "pandasta_best_sets.csv"), index=False)
    _write_best_sets_md(best, os.path.join(RESULTS, "pandasta_best_sets.md"))
    n_win = int(best["is_winner"].sum())
    print(f"done: {n_win} winning sets written to results/")


if __name__ == "__main__":
    main()
