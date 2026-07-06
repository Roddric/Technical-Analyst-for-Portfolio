import numpy as np
import pandas as pd
import pytest

import stats as st
from pandasta_set_search import HORIZONS, FDR_Q, run_stage1, _screen_one_asset, _top_k_per_slot
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


def test_top_k_per_slot_fallback_fills_empty_slot():
    """slot 'trend' has stage-1 rows but zero FDR survivors; other slots have
    survivors. _top_k_per_slot must still return a trend pick (fallback:
    best |ic_ir|) and flag it in fallback_slots, while leaving survivor
    slots unflagged."""
    rows = []
    # trend: two candidates, neither survives FDR
    rows.append({"indicator": "trend_weak", "slot": "trend", "ic": 0.01,
                "ic_ir": 0.05, "survives_fdr": False})
    rows.append({"indicator": "trend_best", "slot": "trend", "ic": 0.03,
                "ic_ir": 0.20, "survives_fdr": False})
    # volume, momentum, volatility: each has a clear FDR survivor
    for slot, name in [("volume", "vol_ind"), ("momentum", "mom_ind"),
                       ("volatility", "atr_ind")]:
        rows.append({"indicator": name, "slot": slot, "ic": 0.10,
                    "ic_ir": 0.5, "survives_fdr": True})
        rows.append({"indicator": f"{name}_loser", "slot": slot, "ic": 0.02,
                    "ic_ir": 0.1, "survives_fdr": False})
    s1 = pd.DataFrame(rows)
    picks, fallback_slots = _top_k_per_slot(s1)
    assert fallback_slots == {"trend"}
    assert "trend" in picks
    assert picks["trend"] == ["trend_best"]        # best |ic_ir| among the slot
    for slot in ("volume", "momentum", "volatility"):
        assert slot not in fallback_slots
        assert slot in picks


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


from pandasta_set_search import causal_zscore, composite_signal, run_stage2


def test_causal_zscore_is_causal_and_normalized():
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2010-01-04", periods=800)
    x = pd.Series(rng.normal(0, 1, 800), index=idx)
    z = causal_zscore(x)
    assert z.iloc[:125].isna().all()          # min_periods honored
    # causality: truncating the future never changes the past
    z_cut = causal_zscore(x.iloc[:600])
    pd.testing.assert_series_equal(z.iloc[:600], z_cut)
    assert abs(z.iloc[300:].mean()) < 0.5     # roughly centered


def test_composite_sign_alignment():
    idx = pd.bdate_range("2010-01-04", periods=400)
    a = pd.Series(np.linspace(0, 1, 400), index=idx)
    comp_pos = composite_signal([a, a], [1.0, 1.0])
    comp_mix = composite_signal([a, a], [1.0, -1.0])
    # sign-aligned identical members reinforce; opposite signs cancel
    assert comp_pos.iloc[350:].abs().mean() > comp_mix.iloc[350:].abs().mean()


def test_stage2_picks_winner_per_asset():
    df = synth_ohlcv(n=1200)
    s1 = pd.DataFrame(_screen_one_asset("SYN", "equity", df, mode="log"))
    s1["survives_fdr"] = True  # force survivors so the combo loop runs
    import pandasta_set_search as pss
    import pandas as _pd
    # monkeypatch loading so run_stage2 sees the synthetic asset
    pss_load = pss.indicator_series_cache
    try:
        pss.indicator_series_cache = lambda tkr, cutoff: (df, pss._candidate_values("SYN", df))
        best = pss.run_stage2(s1, cutoff=None, tickers=["SYN"])
    finally:
        pss.indicator_series_cache = pss_load
    winners = best[best["is_winner"]]
    assert len(winners) == 1
    w = winners.iloc[0]
    assert w["horizon"] == 20
    assert w["traded_sign"] in (1.0, -1.0)
    assert 0 <= w["redundancy"] <= 1 or np.isnan(w["redundancy"])


def test_run_stage2_fallback_stamps_fdr_fallback_slots():
    """End-to-end coverage of run_stage2's fallback branch: a slot with
    stage-1 rows but zero FDR survivors must fall back to its best-|ic_ir|
    indicator (per _top_k_per_slot) and the winning row must carry that
    slot's name in fdr_fallback_slots, while a slot that DID have survivors
    must not appear there."""
    df = synth_ohlcv(n=1200)
    s1 = pd.DataFrame(_screen_one_asset("SYN", "equity", df, mode="log"))
    assert (s1["slot"] == "trend").any(), "fixture must include a trend row"
    # force every "trend" row to fail FDR; every other slot's rows survive
    s1["survives_fdr"] = np.where(s1["slot"] == "trend", False, True)
    import pandasta_set_search as pss
    pss_load = pss.indicator_series_cache
    try:
        pss.indicator_series_cache = lambda tkr, cutoff: (df, pss._candidate_values("SYN", df))
        best = pss.run_stage2(s1, cutoff=None, tickers=["SYN"])
    finally:
        pss.indicator_series_cache = pss_load
    winners = best[best["is_winner"]]
    assert len(winners) == 1
    w = winners.iloc[0]
    fallback_slots = set(w["fdr_fallback_slots"].split(",")) if w["fdr_fallback_slots"] else set()
    assert "trend" in fallback_slots
    # a slot that had survivors (e.g. momentum) must not be flagged as fallback
    assert "momentum" not in fallback_slots
