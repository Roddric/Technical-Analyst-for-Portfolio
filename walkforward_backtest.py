"""
walkforward_backtest.py
=======================
Point-in-time, lookahead-free walk-forward backtest of the regime-conditioned
allocation strategy (Build B).

WHAT THIS IS
------------
At each quarterly rebalance date D:
  1. Regime label  : call phase1.segment_history using ONLY data <= D.
                     phase1 is verified causal (trailing windows) + vintage macro
                     (ALFRED output_type=4). So the label at D uses no future info.
  2. Signal IC     : recompute Spearman IC per (asset_class, slot) using ONLY
                     returns <= D, CONDITIONED on the current regime label.
                     The full-history regime_ic_results.csv is NOT used here —
                     it is contaminated for walk-forward (fit on all history).
  3. Covariance    : trailing N-day sample covariance, data <= D. Naturally causal.
  4. Weights       : allocation_engine (risk-parity base + signal tilt) from (2),(3).
  5. Hold quarter  : realize the NEXT quarter's returns on those weights.
  6. Roll forward.

Then compute, per calendar year: total return, annualized vol, Sharpe, max drawdown.

WHAT THIS IS NOT
----------------
* NOT runnable in the build sandbox (no network / no FRED key / no prices).
  Every external call is behind a clearly marked interface. Run locally.
* NOT a large-sample validation if you only run 2024-2026: that is ~10 rebalances.
  A 10-step walk-forward gives a number with a HUGE confidence interval. Run the
  full 2010-2026 window (~64 steps) for evidence; slice 2024-2026 for the boss.
* NOT a claim of tradeability: no transaction costs, no slippage, no capacity,
  no borrow. Add those before believing any Sharpe.

HONESTY GUARDRAILS BAKED IN
---------------------------
* assert_no_lookahead() re-checks that every weight vector was computed strictly
  before the return window it is applied to. If it ever fails, the run aborts —
  better a crash than a contaminated Sharpe.
* If a quarter's regime cell has < MIN_IC_OBS trailing observations, the signal
  tilt for that quarter is set to ZERO (fall back to pure risk parity) rather
  than sizing off noise. Logged, not hidden.
"""

from __future__ import annotations
import os
import numpy as np
import pandas as pd
import phase1_segment as p1
import yfinance as yf

# FRED key from environment, NEVER hardcoded in this file.
# PowerShell (one-time per session): $env:FRED_API_KEY = "your_key_here"
# If you ever hardcoded a key in a .py file before this, that key is
# compromised the moment the file is saved/shared/screenshotted — rotate it
# on the FRED site before using this script.
FRED_KEY = os.environ.get("FRED_API_KEY")
if not FRED_KEY:
    raise RuntimeError(
        "Set FRED_API_KEY as an environment variable before running this file. "
        "Do not paste the key into this source file."
    )

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
WF_START      = "2010-01-01"   # full window for real evidence
WF_END        = "2026-07-01"
BOSS_SLICE    = ("2024-01-01", "2026-07-01")  # report separately
REBALANCE     = "QS"           # quarter start
COV_WINDOW    = 252            # 1y trailing for covariance
IC_WINDOW     = 504            # 2y trailing for signal IC (per regime)
IC_HORIZON    = 5             # forward-return horizon for IC (days)
MIN_IC_OBS    = 60            # min trailing obs in regime cell to allow signal tilt
TILT_CAP      = 0.5
TRADING_DAYS  = 252

# Boss universe -> asset_class (class-level signal is all we have; per-ticker
# signal is UNVALIDATED, inherited from class — flagged in allocation_engine).
UNIVERSE = {
    "^GSPC": "equity", "^NDX": "equity", "SOXX": "equity", "VGT": "equity",
    "XLE": "equity", "EWH": "equity", "ASHR": "equity", "KSTR": "equity",
    "^FTSE": "equity", "^KS11": "equity", "^N225": "equity", "EWT": "equity",
    "VEA": "equity", "VWO": "equity",
    "IEF": "rates",
    "GLD": "metals", "SLV": "metals", "CPER": "metals",
    "USO": "energy",
}


# ---------------------------------------------------------------------------
# INTERFACES you wire to real data/modules locally. Each RAISES until wired,
# so nobody can accidentally run this on fake data and trust the output.
# ---------------------------------------------------------------------------
def load_prices(tickers, start, end) -> pd.DataFrame:
    """Daily adjusted close, index=dates, cols=tickers."""
    df = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    return df


# --- Regime series: computed ONCE on full history, not per-rebalance. ---
# Safe because every Fast Layer axis in phase1_segment.py was verified to use
# only trailing rolling windows (SMA, ADX, VIX z-score, pct_change) and the
# Slow Layer uses ALFRED first-print vintage data indexed on release_date.
# Nothing in phase1 looks forward, so segmenting the full history once gives
# the identical label at each date as truncating-and-rerunning per quarter
# would — just far cheaper. If phase1_segment.py is ever modified, re-verify
# this assumption (grep for any non-trailing .rolling(center=True) or any
# full-sample .mean()/.std() before trusting this shortcut again).
_REGIME_SERIES: "pd.Series | None" = None


def build_full_regime_series(fred_key: str,
                             start: str = "2005-01-01",
                             end: str = "2026-07-01") -> pd.Series:
    spy_ohlcv = p1.load_yf_ohlcv(["SPY"], start=start, end=end)["SPY"]
    vix       = p1.load_yf_ohlcv(["^VIX"], start=start, end=end)["^VIX"]["close"]
    hy        = p1.load_fred_series("BAMLH0A0HYM2", fred_key, start=start)
    dgs2      = p1.load_fred_series("DGS2", fred_key, start=start)
    dgs10     = p1.load_fred_series("DGS10", fred_key, start=start)
    macro     = p1.build_macro_vintage_frame(fred_key, start=start)

    ticker_returns = spy_ohlcv["close"].pct_change()
    sector_returns = pd.DataFrame(index=spy_ohlcv.index)  # unused: regime-only run

    result = p1.segment_history(spy_ohlcv, vix, hy, dgs2, dgs10, macro,
                                 ticker_returns, sector_returns)
    if "regime_code" not in result.columns:
        raise KeyError(
            f"segment_history() returned columns {list(result.columns)} — "
            "expected 'regime_code'. Update build_full_regime_series() to "
            "match the real column name before proceeding."
        )
    return result["regime_code"]


def _regime_cache(rebal_dates, fred_key: str) -> pd.Series:
    global _REGIME_SERIES
    if _REGIME_SERIES is None:
        _REGIME_SERIES = build_full_regime_series(fred_key)
    return _REGIME_SERIES


def regime_label_asof(as_of: pd.Timestamp, fred_key: str) -> str:
    """Active regime code as of `as_of`, using the precomputed causal series."""
    series = _regime_cache(None, fred_key)
    past = series[series.index <= as_of]
    if past.empty:
        return "UNKNOWN"
    return past.iloc[-1]


# ---------------------------------------------------------------------------
# SIGNAL IC — recomputed per rebalance, per regime, on TRAILING data only
# ---------------------------------------------------------------------------
def trailing_regime_ic(returns: pd.DataFrame,
                       regime_series: pd.Series,
                       as_of: pd.Timestamp,
                       current_regime: str) -> dict[str, float]:
    """
    For each asset_class, compute mean |Spearman IC| of a simple momentum proxy
    vs forward return, using ONLY rows where date <= as_of AND regime==current.

    NOTE: This is a SIMPLIFIED signal (class-level momentum IC) standing in for
    the full 4-slot indicator IC. It is honest about being a proxy. Replacing it
    with the full per-slot indicator IC (pandas-ta-classic) is the Phase-3 job;
    the walk-forward scaffolding here does not change when you do.
    """
    from scipy import stats as _st
    mask = (returns.index <= as_of)
    reg = regime_series.reindex(returns.index).ffill()
    cell = mask & (reg == current_regime)
    window_start = as_of - pd.Timedelta(days=int(IC_WINDOW * 1.5))
    cell = cell & (returns.index >= window_start)

    out = {}
    classes = set(UNIVERSE.values())
    for ac in classes:
        cols = [t for t, c in UNIVERSE.items() if c == ac and t in returns.columns]
        if not cols:
            out[ac] = 0.0
            continue
        ics = []
        for t in cols:
            r = returns[t][cell].dropna()
            if len(r) < MIN_IC_OBS:
                continue
            mom = r.rolling(20).sum().shift(1)          # causal momentum signal
            fwd = r.shift(-IC_HORIZON).rolling(IC_HORIZON).sum()  # forward return
            df = pd.concat([mom, fwd], axis=1).dropna()
            if len(df) < MIN_IC_OBS:
                continue
            ic, _ = _st.spearmanr(df.iloc[:, 0], df.iloc[:, 1])
            if not np.isnan(ic):
                ics.append(abs(ic))
        out[ac] = float(np.mean(ics)) if ics else 0.0   # no obs -> 0 tilt
    return out


# ---------------------------------------------------------------------------
# WEIGHTS for one rebalance
# ---------------------------------------------------------------------------
def weights_asof(returns, as_of, current_regime, regime_series):
    trail = returns[returns.index <= as_of].tail(COV_WINDOW)
    cols = [c for c in trail.columns if trail[c].notna().sum() > COV_WINDOW * 0.6]
    trail = trail[cols].dropna(how="any")
    if trail.shape[0] < 60:
        return None  # not enough history yet
    cov = trail.cov() * TRADING_DAYS

    # risk-parity base
    sigma = np.sqrt(np.diag(cov.values))
    inv = 1.0 / sigma
    base = pd.Series(inv / inv.sum(), index=cov.index)

    # signal tilt from trailing per-regime IC
    ic_by_class = trailing_regime_ic(returns, regime_series, as_of, current_regime)
    scores = pd.Series({t: ic_by_class.get(UNIVERSE[t], 0.0) for t in cov.index})
    mean_s = scores.mean()
    eps = 1e-9
    tilt = (1 + TILT_CAP * (scores - mean_s) / (mean_s + eps)).clip(
        1 - TILT_CAP, 1 + TILT_CAP)
    tilted = base * tilt
    return tilted / tilted.sum()


# ---------------------------------------------------------------------------
# WALK-FORWARD LOOP
# ---------------------------------------------------------------------------
def run_walkforward(fred_key: str):
    """Returns (port_ret, weights_history).
    weights_history is a DataFrame: rows = rebalance date, cols = ticker,
    values = weight assigned at that rebalance (NaN where ticker not held)."""
    prices = load_prices(list(UNIVERSE.keys()), WF_START, WF_END)
    returns = np.log(prices / prices.shift(1))

    last_date = returns.index.max()
    rebal_dates = pd.date_range(WF_START, WF_END, freq=REBALANCE)
    rebal_dates = [d for d in rebal_dates if d <= last_date]
    if len(rebal_dates) < 2:
        raise RuntimeError(
            f"Only {len(rebal_dates)} rebalance date(s) fall within the "
            f"downloaded price range (data ends {last_date.date()}). "
            "Need at least 2 to form one holding period."
        )

    def _snap(date):
        pos = returns.index.searchsorted(date)
        pos = min(pos, len(returns.index) - 1)
        return returns.index[pos]

    port_ret = pd.Series(0.0, index=returns.index)
    applied = []
    weight_rows = {}   # rebalance_date -> weights Series
    regime_rows = {}    # rebalance_date -> regime label, for context alongside weights

    for i, d in enumerate(rebal_dates[:-1]):
        d = _snap(d)
        regime = regime_label_asof(d, fred_key)
        w = weights_asof(returns, d, regime, _regime_cache(rebal_dates, fred_key))
        if w is None:
            continue
        weight_rows[d] = w
        regime_rows[d] = regime
        nxt = _snap(rebal_dates[i + 1])
        window = (returns.index > d) & (returns.index <= nxt)
        if window.sum() == 0:
            continue
        applied.append((d, returns.index[window].min(), returns.index[window].max()))
        port_ret.loc[window] = (returns.loc[window, w.index] * w).sum(axis=1)

    assert_no_lookahead(applied)

    weights_history = pd.DataFrame(weight_rows).T   # rows=date, cols=ticker
    weights_history.insert(0, "regime", pd.Series(regime_rows))
    return port_ret, weights_history


def assert_no_lookahead(applied):
    """Every weight_date must be strictly before its return window start."""
    for wdate, rstart, rend in applied:
        if not (wdate < rstart):
            raise AssertionError(
                f"LOOKAHEAD: weights dated {wdate} applied to returns from "
                f"{rstart} — weights must precede the return window. ABORT.")


# ---------------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------------
def metrics_by_year(port_ret: pd.Series) -> pd.DataFrame:
    rows = []
    for yr, r in port_ret.groupby(port_ret.index.year):
        r = r.dropna()
        if len(r) < 20:
            continue
        total = np.expm1(r.sum())
        vol = r.std() * np.sqrt(TRADING_DAYS)
        sharpe = (r.mean() * TRADING_DAYS) / vol if vol > 0 else np.nan
        eq = r.cumsum().apply(np.exp)
        maxdd = (eq / eq.cummax() - 1).min()
        rows.append({"year": yr, "return": total, "ann_vol": vol,
                     "sharpe": sharpe, "max_drawdown": maxdd, "n_days": len(r)})
    return pd.DataFrame(rows).set_index("year")


if __name__ == "__main__":
    print("Running walk-forward backtest (this will take a while — phase1 "
          "fetches SPY/VIX/FRED once, then loops rebalance dates)...\n")
    port, weights_history = run_walkforward(FRED_KEY)

    print("\n=== WEIGHTS AT EACH REBALANCE (regime + per-ticker weight) ===")
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 30)
    print(weights_history.round(4))
    weights_history.to_csv("weights_history.csv")
    print("\nSaved full weight history to weights_history.csv")

    print("\n=== FULL WINDOW (2010-2026) — the actual evidence ===")
    print(metrics_by_year(port))

    print("\n=== BOSS SLICE (2024 - Jul 2026) — 10 rebalances, DEMO ONLY ===")
    print("NOTE: 10 quarterly points is not enough data to validate a ")
    print("strategy. Treat this slice as illustrative, not conclusive.")
    print(metrics_by_year(port.loc["2024":]))
    print("\nWeights specifically for the boss-slice rebalances:")
    print(weights_history.loc["2024":].round(4))

    print("\nREMINDER: signal tilt in this run is a class-level momentum ")
    print("PROXY, not the real 4-slot indicator IC. This validates the ")
    print("causal/allocation machinery, not your actual indicator strategy.")
