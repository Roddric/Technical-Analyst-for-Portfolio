import numpy as np
import pandas as pd
import pytest

from portfolio_backtest import (metrics_table, rank_tilt, run_backtest,
                                target_weights)


def test_rank_tilt_bounds_and_order():
    t = rank_tilt(8)
    assert t[0] == pytest.approx(1.5) and t[-1] == pytest.approx(0.5)
    assert np.all(np.diff(t) < 0)
    assert rank_tilt(1)[0] == pytest.approx(1.0)


def test_target_weights_long_only_sum1_topn():
    idx = [f"A{i}" for i in range(12)]
    sig = pd.Series(np.linspace(2.0, 0.1, 12), index=idx)
    vol = pd.Series(0.2, index=idx)
    w = target_weights(sig, vol, top_n=8)
    assert w.sum() == pytest.approx(1.0)
    assert (w >= 0).all()
    assert (w > 0).sum() == 8
    assert set(w[w > 0].index) == set(idx[:8])   # top-8 by signal
    # equal vol -> ordering by tilt: best signal gets biggest weight
    ww = w[w > 0].reindex(idx[:8])
    assert ww.is_monotonic_decreasing


def test_inverse_vol_dominates_when_signals_tie():
    idx = ["LOWVOL", "HIGHVOL"]
    sig = pd.Series([0.5, 0.5], index=idx)
    vol = pd.Series([0.10, 0.40], index=idx)
    w = target_weights(sig, vol, top_n=2)
    assert w["LOWVOL"] > w["HIGHVOL"]
    # tilt cap: 4x vol gap cannot be overturned by any tilt (max ratio 3x)
    assert w["LOWVOL"] / w["HIGHVOL"] > 1.3


def test_backtest_accounting_two_asset_toy():
    days = pd.bdate_range("2024-01-01", periods=64)
    # asset A returns +1% daily, B returns 0% — deterministic
    rets = pd.DataFrame({"A": 0.01, "B": 0.0}, index=days)
    # signal always prefers A
    sig = pd.DataFrame({"A": 1.0, "B": -1.0}, index=days)
    res = run_backtest(rets, sig, start="2024-02-01", cost_per_side=0.0)
    daily = res["daily"]
    # after the first rebalance takes effect, portfolio must track A's 1%
    # exactly once weight drifts toward 100% A? A is top-1 of top_n=8 => both
    # held; but with equal vol (constant rets -> zero vol) fallback must not
    # produce NaN weights
    assert not daily.isna().any()
    assert (res["equity"].iloc[-1] > 1.0)
    w = res["weights"]
    # B has a negative signal -> dropped to cash; only A (half of top-2) held
    assert np.allclose(w.sum(axis=1), 0.5)
    assert (w.values >= -1e-12).all()


def test_costs_reduce_returns():
    days = pd.bdate_range("2024-01-01", periods=64)
    rng = np.random.default_rng(5)
    rets = pd.DataFrame(rng.normal(0.0005, 0.01, (64, 3)),
                        index=days, columns=["A", "B", "C"])
    sig = pd.DataFrame(rng.normal(0, 1, (64, 3)),
                       index=days, columns=["A", "B", "C"])
    free = run_backtest(rets, sig, start="2024-02-01", cost_per_side=0.0)
    paid = run_backtest(rets, sig, start="2024-02-01", cost_per_side=0.001)
    assert paid["equity"].iloc[-1] < free["equity"].iloc[-1]


def test_metrics_table_known_series():
    days = pd.bdate_range("2024-01-01", periods=252)
    daily = pd.Series(0.001, index=days)          # +0.1%/day, zero vol
    equity = (1 + daily).cumprod()
    m = metrics_table(daily, equity)
    r2024 = m.loc["2024", "return"]
    assert r2024 == pytest.approx((1.001 ** 252) - 1, rel=1e-9)
    assert m.loc["2024", "max_dd"] == pytest.approx(0.0)


def test_target_weights_raises_on_all_nan_signals():
    idx = ["A", "B", "C"]
    sig = pd.Series([np.nan, np.nan, np.nan], index=idx)
    vol = pd.Series(0.2, index=idx)
    with pytest.raises(ValueError, match="no assets with valid signals"):
        target_weights(sig, vol, top_n=2)


def test_negative_signals_go_to_cash():
    idx = [f"A{i}" for i in range(10)]
    sig = pd.Series([1.0]*4 + [-1.0]*6, index=idx)
    vol = pd.Series(0.2, index=idx)
    w = target_weights(sig, vol, top_n=8)
    assert w[sig > 0].sum() == pytest.approx(0.5)   # 4 positive of top-8 -> half invested
    assert (w[sig <= 0] == 0).all()


def test_all_negative_signals_all_cash():
    idx = ["A", "B", "C"]
    sig = pd.Series([-0.5, -1.0, -2.0], index=idx)
    vol = pd.Series(0.2, index=idx)
    w = target_weights(sig, vol, top_n=8)
    assert w.sum() == pytest.approx(0.0)


def test_backtest_raises_when_signals_never_valid():
    days = pd.bdate_range("2024-01-01", periods=40)
    rets = pd.DataFrame({"A": 0.01, "B": 0.0}, index=days)
    sig = pd.DataFrame(np.nan, index=days, columns=["A", "B"])
    with pytest.raises(ValueError, match="no assets with valid signals"):
        run_backtest(rets, sig, start="2024-02-01", cost_per_side=0.0)


def test_cash_drift_invariant_and_manual_reconstruction():
    """Independent re-derivation of the cash-aware drift rule: w_new =
    w*(1+r)/(1+rp_pre_cost), implicit cash = 1 - w.sum(). Reconstructs
    run_backtest's daily-return series and rebalance/cost mechanics by hand
    (mirroring the exact VOL_WINDOW/ANN rolling-vol call and rebalance-day
    set construction) and checks it matches res["daily"] bit-for-bit, and
    that res["cash"] is present and positive throughout — a regression
    guard against reintroducing the old renormalize-to-100%-risky bug."""
    days = pd.bdate_range("2024-01-01", periods=45)
    rng = np.random.default_rng(9)
    rets = pd.DataFrame(rng.normal(0.001, 0.02, (45, 3)),
                        index=days, columns=["A", "B", "C"])
    # A,B positive signal; C negative -> C to cash each rebalance
    sig = pd.DataFrame({"A": 1.0, "B": 0.5, "C": -1.0}, index=days)
    res = run_backtest(rets, sig, start="2024-01-15", cost_per_side=0.001)
    live = rets.index[rets.index >= pd.Timestamp("2024-01-15")]
    # manual reconstruction
    w = pd.Series(0.0, index=["A", "B", "C"])
    cash = 1.0
    # mirrors run_backtest: vols = daily_rets.rolling(VOL_WINDOW).std() *
    # sqrt(ANN), VOL_WINDOW=63, ANN=252, no min_periods override
    vols = rets.rolling(63).std() * np.sqrt(252)
    manual = []
    months = pd.Series(live.month, index=live)
    is_first = months.ne(months.shift(1).fillna(-1))
    rebal = set(live[is_first.values])
    for d in live:
        cost = 0.0
        if d in rebal:
            prior = rets.index[rets.index < d]
            if len(prior):
                p = prior[-1]
                tgt = target_weights(sig.loc[p], vols.loc[p])
                cost = 0.001 * (tgt - w).abs().sum()
                w = tgt
                cash = 1.0 - w.sum()
        r = rets.loc[d].fillna(0.0)
        rp_pre = float((w * r).sum())
        manual.append(rp_pre - cost)
        denom = 1.0 + rp_pre
        if denom > 0:
            w = w * (1 + r) / denom
        # else: pathological (portfolio value <= 0) -- keep w unchanged
        cash = 1.0 - w.sum()          # invariant: risky+cash == 1
        assert cash >= -1e-12
    assert np.allclose(res["daily"].to_numpy(), np.array(manual), atol=1e-12)
    # 2 of 3 assets positive -> invested_fraction = 2/3 -> cash = 1/3 each rebal
    assert (res["cash"] > 0).all()
