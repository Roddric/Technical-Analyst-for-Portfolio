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


def test_run_stage1_pools_fdr_across_assets(monkeypatch):
    """Deterministic fixture that DISCRIMINATES pooled BH from per-asset BH.

    Hand-crafted p-values: AAA has nine rows at p=1e-6; BBB has two rows at
    p=0.08 and p=0.9. Pooled BH over all 11 (q=0.10): the 0.08 row is rank
    10 with threshold 10/11*0.10 ~= 0.0909, so it SURVIVES. Per-asset BH on
    BBB alone (n=2): rank-1 threshold is 0.05, so 0.08 FAILS. A per-asset
    regression therefore flips the p=0.08 row and this test catches it."""
    import pandasta_set_search as pss
    fake_universe = {"AAA": {"class": "equity"},
                     "BBB": {"class": "rates", "return_mode": "diff"}}
    monkeypatch.setattr(pss, "UNIVERSE", fake_universe)
    monkeypatch.setattr(pss, "return_mode",
                        lambda t: fake_universe[t].get("return_mode", "log"))
    monkeypatch.setattr(pss, "indicator_series_cache",
                        lambda tkr, cutoff: (synth_ohlcv(n=200), {}))
    fake_p = {"AAA": [1e-6] * 9, "BBB": [0.08, 0.9]}

    def fake_screen(tkr, klass, df, mode, values=None):
        return [{"asset": tkr, "asset_class": klass,
                 "indicator": f"IND-{tkr}-{i}", "slot": "momentum",
                 "horizon": 5, "ic": 0.05, "ic_ir": 0.1, "n_obs": 500,
                 "p_value": p, "note": ""}
                for i, p in enumerate(fake_p[tkr])]

    monkeypatch.setattr(pss, "_screen_one_asset", fake_screen)
    out = pss.run_stage1(cutoff=None)
    assert set(out["asset"]) == {"AAA", "BBB"}
    assert "survives_fdr" in out.columns
    assert out["survives_fdr"].dtype == bool
    # all nine AAA rows (p=1e-6) survive under pooled BH
    assert out.loc[out["asset"] == "AAA", "survives_fdr"].all()
    # the discriminator: p=0.08 survives ONLY under pooled BH (rank-10
    # threshold ~0.0909 pooled vs 0.05 per-asset on BBB's two rows)
    assert bool(out.loc[np.isclose(out["p_value"], 0.08),
                        "survives_fdr"].iloc[0]) is True
    assert bool(out.loc[np.isclose(out["p_value"], 0.9),
                        "survives_fdr"].iloc[0]) is False
    # element-wise agreement with an independent pooled BH recomputation
    pool = out["p_value"].notna().to_numpy()
    expected = np.zeros(len(out), dtype=bool)
    expected[pool] = st.benjamini_hochberg(
        out.loc[out["p_value"].notna(), "p_value"].to_numpy(), pss.FDR_Q)
    assert (out["survives_fdr"].to_numpy() == expected).all()


def test_run_stage1_skips_missing_asset(monkeypatch, capsys):
    import pandasta_set_search as pss
    df_a = synth_ohlcv(n=900, seed=11)
    fake_universe = {"AAA": {"class": "equity"}, "GONE": {"class": "equity"}}
    monkeypatch.setattr(pss, "UNIVERSE", fake_universe)
    monkeypatch.setattr(pss, "return_mode", lambda t: "log")
    def fake_cache(tkr, cutoff):
        if tkr == "GONE":
            raise FileNotFoundError(tkr)
        return df_a, pss._candidate_values(tkr, df_a)
    monkeypatch.setattr(pss, "indicator_series_cache", fake_cache)
    out = pss.run_stage1(cutoff=None)
    assert set(out["asset"]) == {"AAA"}
    assert "SKIP GONE" in capsys.readouterr().out
