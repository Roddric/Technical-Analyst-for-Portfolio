import numpy as np
import pandas as pd
import pytest

import stats as st
from pandasta_set_search import HORIZONS, FDR_Q, run_stage1, _screen_one_asset
from tests.test_registry import synth_ohlcv


def test_screen_one_asset_schema_and_fdr_columns():
    df = synth_ohlcv(n=900)
    rows = _screen_one_asset("SYN", "equity", df, mode="log")
    out = pd.DataFrame(rows)
    assert set(out.columns) >= {"asset", "asset_class", "indicator", "slot",
                                "horizon", "ic", "ic_ir", "n_obs", "p_value",
                                "note"}
    assert set(out["horizon"]) == set(HORIZONS)
    # every candidate that produced values appears at every horizon
    per_ind = out.groupby("indicator")["horizon"].nunique()
    assert (per_ind == len(HORIZONS)).all()


def test_planted_signal_is_detected():
    """A predictor built from the (future) 5-day return must show huge IC.
    This validates wiring, not causality (construction is deliberately
    lookahead INSIDE THE TEST ONLY)."""
    df = synth_ohlcv(n=900)
    close = df["close"].to_numpy()
    fwd5 = st.forward_returns(close, 5)
    x = fwd5 + np.random.default_rng(0).normal(0, np.nanstd(fwd5) * 0.3,
                                               len(fwd5))
    ic, t, p, n = st.spearman_ic_hac(x, fwd5, lag=5)
    assert ic > 0.8 and p < 1e-10


def test_cutoff_truncates_history():
    df = synth_ohlcv(n=900)  # bdates from 2015-01-02
    rows_full = _screen_one_asset("SYN", "equity", df, mode="log")
    rows_cut = _screen_one_asset("SYN", "equity",
                                 df.loc[:"2016-12-31"], mode="log")
    n_full = max(r["n_obs"] for r in rows_full)
    n_cut = max(r["n_obs"] for r in rows_cut)
    assert n_cut < n_full
