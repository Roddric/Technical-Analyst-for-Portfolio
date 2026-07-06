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
