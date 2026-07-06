"""
Phase 1 — Regime Segmentation Engine
=====================================
Segments historical OHLCV + macro data into (regime_code, sector) labeled cells.
Uses vintage-point-in-time data only — no revised GDP/CPI figures.

Each output row carries:
  date, ticker, regime_code, sector, fast_confidence, slow_confidence,
  overall_confidence, shock_flag, transition_flag, vol_mode

Pipeline position: feeds Phase 2 (IC computation).
Dependencies: numpy, pandas, scipy only — no external TA libraries.

Notes
-----
- All Slow Layer data must be tagged vintage (first-print only).
- VIX Z-score uses 126-day rolling window. Cold-start (<63 days) falls back
  to percentile rank and sets vol_mode='bootstrap'.
- Shock detection uses RELATIVE thresholds (Z-score), not absolute VIX levels.
- Steepener type is computed in Fast Layer on 40-session rolling window.
- Execution floor: overall_confidence < 60 → Cash/Neutral (flagged, not dropped).
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SECTORS = ["XLK", "XLE", "XLF", "XLV", "XLY", "XLP", "XLI", "XLB", "XLRE", "XLU", "XLC"]

REGIME_CODES = [
    "RC-01", "RC-02", "RC-03", "RC-04", "RC-05", "RC-06",
    "RC-07", "RC-08", "RC-09", "RC-10", "RC-11", "RC-12",
    "RC-13", "RC-14", "RC-15", "RC-16", "RC-17", "RC-18",
    "RC-19", "RC-20",
]

# Minimum observations per regime × sector cell for IC to be meaningful
MIN_CELL_OBS = 30

# Confidence thresholds
EXECUTION_FLOOR = 60        # overall_confidence below this → Cash/Neutral
TRANSITION_THRESHOLD = 70   # fast_confidence below this → REGIME TRANSITION flag
SHOCK_ACTIVE_Z = 3.0        # VIX Z-score above this → Shock Active
SHOCK_WATCH_Z = 2.0         # VIX Z-score above this → Shock Watch
VIX_COLDSTART_DAYS = 63     # minimum days before Z-score is valid

# ---------------------------------------------------------------------------
# Data loaders — yfinance (OHLCV, VIX) + FRED (rates, HY OAS) + ALFRED (vintage)
# ---------------------------------------------------------------------------
# These are the ONLY sanctioned data entry points for live/backtest runs.
#
# Vintage mandate enforcement: load_alfred_first_prints() uses the FRED API
# output_type=4 parameter, which returns ONLY initial-release observations,
# each stamped with its realtime_start (the release date). The observation is
# indexed by RELEASE DATE, not reference period, because the Slow Layer keys
# on "what was knowable on this trading day". This is the vintage mandate in
# code — do not substitute load_fred_series() (revised data) for Slow Layer
# inputs. load_fred_series is for Fast Layer series only (DGS2/DGS10/HY OAS),
# which are never revised in a way that matters here.

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def load_yf_ohlcv(tickers, start, end=None, auto_adjust=True):
    """
    Download daily OHLCV via yfinance for one or more tickers.

    Returns dict {ticker: DataFrame[open, high, low, close, volume]} with a
    DatetimeIndex normalized to date (no tz). ^VIX is a valid ticker here.

    auto_adjust=True gives split/dividend-adjusted prices — correct for
    return computation and sector correlation. Set False only if you need
    raw close for corporate-action work.
    """
    import yfinance as yf
    data = yf.download(tickers=list(tickers) if not isinstance(tickers, str) else tickers,
                       start=start, end=end, auto_adjust=auto_adjust,
                       progress=False, group_by="ticker", threads=True)
    out = {}
    single = isinstance(tickers, str) or len(tickers) == 1
    tick_list = [tickers] if isinstance(tickers, str) else list(tickers)
    for t in tick_list:
        df = data if single and not isinstance(data.columns, pd.MultiIndex) else data[t]
        df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
        df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
        out[t] = df.dropna(how="all")
    return out


def load_fred_series(series_id, api_key, start="1990-01-01"):
    """
    Load a CURRENT (revised) FRED series as a daily-indexed float Series.
    Use for Fast Layer inputs only: DGS2, DGS10, BAMLH0A0HYM2, VIXCLS.
    NEVER use for Slow Layer macro — that must go through
    load_alfred_first_prints() to respect the vintage mandate.
    """
    import requests
    params = {"series_id": series_id, "api_key": api_key,
              "file_type": "json", "observation_start": start}
    r = requests.get(FRED_BASE, params=params, timeout=30)
    r.raise_for_status()
    obs = r.json()["observations"]
    s = pd.Series(
        {pd.Timestamp(o["date"]): float(o["value"]) if o["value"] != "." else np.nan
         for o in obs}, name=series_id).sort_index()
    return s.dropna()


def load_alfred_first_prints(series_id, api_key, start="1990-01-01"):
    """
    Load FIRST-PRINT (initial release) observations for a macro series via
    the FRED/ALFRED API with output_type=4.

    output_type=4 returns exactly one row per reference period: the value as
    it was FIRST published, together with realtime_start = the publication
    date. That is the vintage mandate: the 2008 Q3 GDP advance print of
    -0.3%, not the revised -3.7%.

    Returns DataFrame indexed by RELEASE DATE (realtime_start) with columns:
        value        — the first-print value
        ref_period   — the reference period the print describes
        vintage_flag — always True (contract marker for the Slow Layer)

    The Slow Layer forward-fills from release dates, so indexing on
    realtime_start is what makes staleness computation correct.
    """
    import requests
    params = {"series_id": series_id, "api_key": api_key,
              "file_type": "json", "observation_start": start,
              "realtime_start": "1776-07-04", "realtime_end": "9999-12-31",
              "output_type": 4}
    r = requests.get(FRED_BASE, params=params, timeout=30)
    r.raise_for_status()
    obs = r.json()["observations"]
    rows = []
    for o in obs:
        if o["value"] == ".":
            continue
        rows.append({
            "release_date": pd.Timestamp(o["realtime_start"]),
            "ref_period":   pd.Timestamp(o["date"]),
            "value":        float(o["value"]),
        })
    df = pd.DataFrame(rows).set_index("release_date").sort_index()
    df["vintage_flag"] = True
    return df


def build_macro_vintage_frame(api_key, start="1994-01-01"):
    """
    Assemble the Slow Layer macro input frame from ALFRED first prints.

    Series and transformations:
        GDPC1    → GDP QoQ % annualized computed ACROSS first prints:
                   each quarter's advance level vs the PRIOR quarter's
                   first-print level. Not identical to BEA's official advance
                   QoQ (which compares against the revised prior quarter),
                   but it is the only construction that uses zero future
                   information. Documented deviation.
        CPIAUCSL → CPI YoY % across first prints (this month's first print
                   vs the first print of the same month last year).
        UNRATE   → level, first print.
        NAPM     → ISM Manufacturing PMI (if unavailable on ALFRED, caller
                   must supply ISM data from another vintage-safe source;
                   this function then leaves the column NaN and the Slow
                   Layer degrades gracefully with reduced slow_confidence).

    Returns DataFrame indexed by release date with columns:
        gdp_qoq, cpi_yoy, unemployment, ism_mfg, ism_svcs (NaN if missing)
    """
    frames = {}

    gdp = load_alfred_first_prints("GDPC1", api_key, start)
    gdp = gdp.sort_values("ref_period")
    gdp["gdp_qoq"] = (gdp["value"] / gdp["value"].shift(1)) ** 4 * 100 - 100
    frames["gdp_qoq"] = gdp.set_index(gdp.index)["gdp_qoq"]

    cpi = load_alfred_first_prints("CPIAUCSL", api_key, start)
    cpi = cpi.sort_values("ref_period")
    cpi["cpi_yoy"] = cpi["value"].pct_change(12) * 100
    frames["cpi_yoy"] = cpi.set_index(cpi.index)["cpi_yoy"]

    unrate = load_alfred_first_prints("UNRATE", api_key, start)
    frames["unemployment"] = unrate["value"]

    for col, sid in [("ism_mfg", "NAPM"), ("ism_svcs", "NMFCI")]:
        try:
            ism = load_alfred_first_prints(sid, api_key, start)
            frames[col] = ism["value"]
        except Exception:
            frames[col] = pd.Series(dtype=float)   # graceful degradation

    macro = pd.DataFrame(frames).sort_index()
    macro["vintage_flag"] = True
    return macro


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FastLayerResult:
    """Output of the Fast Layer — Axes 1, 2, 4 + steepener type."""
    axis1_trend: str            # "Bull" | "Bear" | "Sideways"
    axis2_vol: str              # "High" | "Low"
    axis4_shock: str            # "Active" | "Watch" | "None"
    steepener_type: str         # "BearSteepener" | "BullSteepener" | "BearFlattener" | "BullFlattener" | "Flat"
    fast_confidence: float      # 0–100
    vol_mode: str               # "normal" | "bootstrap"
    vix_zscore: float
    vix_velocity: float         # % change over 5 sessions
    hy_spread_zscore: float


@dataclass
class SlowLayerResult:
    """Output of the Slow Layer — Axis 3 only, vintage data."""
    axis3_cycle: str            # "Expansion" | "Reflation" | "Stagflation" | "Recession"
    slow_confidence: float      # 0–100
    last_updated: Optional[pd.Timestamp]
    data_vintage: bool          # True = point-in-time data confirmed
    ism_split_flag: bool        # Manufacturing vs Services PMI divergence
    steepener_contradiction: bool  # steepener type contradicts other A3 signals
    staleness_days: int


@dataclass
class RegimeResult:
    """Final output of the Priority Arbiter for one date."""
    date: pd.Timestamp
    regime_code: str
    regime_label: str
    overall_confidence: float
    fast_confidence: float
    slow_confidence: float
    shock_flag: bool            # True = Shock Active
    shock_watch_flag: bool      # True = Shock Watch (not full shock)
    transition_flag: bool       # True = regime boundary, blend weights
    vol_mode: str
    floor_triggered: bool       # True = overall_confidence < 60
    floor_reason: str           # e.g. "TRANSITION_HAIRCUT"
    axis1: str
    axis2: str
    axis3: str
    axis4: str
    steepener_type: str
    vix_zscore: float


# ---------------------------------------------------------------------------
# Fast Layer — Axis 1: Trend Direction
# ---------------------------------------------------------------------------

def compute_axis1_trend(spy_close: pd.Series,
                        spy_high: pd.Series,
                        spy_low: pd.Series) -> pd.DataFrame:
    """
    Classify trend direction from SPY price data.

    Returns DataFrame with columns:
        axis1, sma_200, sma_50, adx, rolling_3m_return, fast_trend_conf
    """
    results = pd.DataFrame(index=spy_close.index)

    # Simple moving averages
    results["sma_50"]  = spy_close.rolling(50, min_periods=40).mean()
    results["sma_200"] = spy_close.rolling(200, min_periods=160).mean()

    # Rolling 3-month (63 session) return
    results["rolling_3m_return"] = spy_close.pct_change(63) * 100

    # ADX (Wilder's method, 14-period)
    adx_df = _wilder_adx(spy_high, spy_low, spy_close, period=14)
    results["adx"]  = adx_df["adx"]
    results["di_pos"] = adx_df["di_pos"]
    results["di_neg"] = adx_df["di_neg"]

    # Vectorized Axis 1 classification per ARCHITECTURE_V4 Step 2A:
    #   Bull:     SPY above 200D MA, ADX > 25 with +DI leading, 3M return > +8%
    #   Bear:     SPY below 200D MA, ADX > 25 with -DI leading, 3M return < -8%
    #   Sideways: SPY within ±3% of 200D MA AND ADX < 20 (explicit override)
    # NOTE: the MA signal is PRICE vs 200D MA (spec), not the 50/200 golden
    # cross — the cross is a slower, different signal and was a spec deviation.
    has_200 = results["sma_200"].notna()
    has_adx = results["adx"].notna()
    valid   = has_200 & has_adx

    price_vs_200 = spy_close / results["sma_200"] - 1.0   # signed % distance
    above_200    = price_vs_200 > 0
    ret_3m       = results["rolling_3m_return"]
    adx_val      = results["adx"]
    di_bull      = results["di_pos"] > results["di_neg"]

    # Explicit Sideways condition from spec: within ±3% of 200D MA AND ADX < 20
    sideways_explicit = valid & (price_vs_200.abs() < 0.03) & (adx_val < 20)

    # Build bull/bear signal counts vectorized
    bull_from_ma  = (valid & above_200).astype(int)
    bear_from_ma  = (valid & ~above_200).astype(int)

    ret_valid   = ret_3m.notna()
    bull_from_r = (ret_valid & (ret_3m > 8)).astype(int)
    bear_from_r = (ret_valid & (ret_3m < -8)).astype(int)

    adx_strong  = has_adx & (adx_val > 25)
    bull_from_d = (adx_strong & di_bull).astype(int)
    bear_from_d = (adx_strong & ~di_bull).astype(int)

    bull_total  = bull_from_ma + bull_from_r + bull_from_d
    bear_total  = bear_from_ma + bear_from_r + bear_from_d
    signal_sum  = bull_total + bear_total

    safe_sum    = signal_sum.replace(0, np.nan)  # avoid div-by-zero for confidence
    bull_conf   = (50 + (bull_total / safe_sum) * 50).clip(upper=95)
    bear_conf   = (50 + (bear_total / safe_sum) * 50).clip(upper=95)

    axis1_conditions = [
        ~valid,                                   # insufficient data
        sideways_explicit,                        # spec: ±3% of 200MA + ADX<20
        (signal_sum == 0),                        # no directional signals
        bull_total > bear_total,                  # bull wins
        bear_total > bull_total,                  # bear wins
    ]
    axis1_choices = ["Sideways", "Sideways", "Sideways", "Bull", "Bear"]
    results["axis1"] = np.select(axis1_conditions, axis1_choices, default="Sideways")

    # Sideways-explicit gets elevated confidence (strong agreement of conditions)
    conf_conditions = [
        ~valid,
        sideways_explicit,
        (signal_sum == 0),
        bull_total > bear_total,
        bear_total > bull_total,
    ]
    conf_choices = [50.0, 70.0, 50.0, bull_conf, bear_conf]
    results["fast_trend_conf"] = np.select(
        conf_conditions, conf_choices, default=50.0
    ).astype(float)

    return results


def _wilder_adx(high: pd.Series, low: pd.Series,
                close: pd.Series, period: int = 14) -> pd.DataFrame:
    """Wilder's ADX, +DI, -DI. Preserves the original Series index."""
    # Save index before converting to numpy
    idx    = high.index
    h_vals = high.values
    l_vals = low.values
    c_vals = close.values
    n      = len(c_vals)

    tr  = np.zeros(n)
    pdm = np.zeros(n)
    ndm = np.zeros(n)

    for i in range(1, n):
        tr[i]  = max(h_vals[i] - l_vals[i],
                     abs(h_vals[i] - c_vals[i-1]),
                     abs(l_vals[i] - c_vals[i-1]))
        up   = h_vals[i] - h_vals[i-1]
        down = l_vals[i-1] - l_vals[i]
        pdm[i] = up   if (up > down and up > 0) else 0.0
        ndm[i] = down if (down > up and down > 0) else 0.0

    def wilder_smooth(arr, p):
        s = np.full(len(arr), np.nan)
        if len(arr) > p:
            s[p] = arr[1:p+1].sum()
            for i in range(p+1, len(arr)):
                s[i] = s[i-1] - (s[i-1] / p) + arr[i]
        return s

    atr_s = wilder_smooth(tr,  period)
    pdm_s = wilder_smooth(pdm, period)
    ndm_s = wilder_smooth(ndm, period)

    with np.errstate(divide="ignore", invalid="ignore"):
        pdi = np.where(atr_s > 0, 100.0 * pdm_s / atr_s, 0.0)
        ndi = np.where(atr_s > 0, 100.0 * ndm_s / atr_s, 0.0)
        dx  = np.where((pdi + ndi) > 0,
                       100.0 * np.abs(pdi - ndi) / (pdi + ndi), 0.0)

    # ADX init uses AVERAGE of first period DX values (not sum like TR/DM)
    def adx_smooth(arr, p):
        s = np.full(len(arr), np.nan)
        if len(arr) > p:
            s[p] = np.nanmean(arr[1:p+1])   # Wilder spec: simple average for first ADX
            for i in range(p+1, len(arr)):
                s[i] = s[i-1] - (s[i-1] / p) + arr[i]
        return s

    adx = adx_smooth(dx, period)

    # Use original index so it aligns with the calling DataFrame
    return pd.DataFrame({"adx": adx, "di_pos": pdi, "di_neg": ndi}, index=idx)


# ---------------------------------------------------------------------------
# Fast Layer — Axis 2: Volatility Level (relative, Z-score based)
# ---------------------------------------------------------------------------

def compute_axis2_vol(vix: pd.Series,
                      spy_close: pd.Series = None) -> pd.DataFrame:
    """
    Classify volatility level per ARCHITECTURE_V4 Step 2A (dual condition):
      High Vol: VIX Z-score (126D) > +1.0 AND realized 20D SPY vol > 20% ann.
      Low Vol:  VIX Z-score (126D) < -0.5 AND realized 20D SPY vol < 14% ann.
    Cold-start fallback: percentile rank if < 63 days of VIX history.

    The realized-vol AND-condition prevents implied-vol-only misclassification:
    VIX can spike on option demand while actual price movement stays calm
    (and vice versa post-event when VIX stays bid but realized vol collapses).

    If spy_close is None (legacy call), realized vol conditions are skipped
    and a `realized_vol_available=False` column records the degradation.

    Returns DataFrame with: axis2, vix_zscore, vix_pct_rank, vol_mode,
                            vol_conf, realized_vol_ann, realized_vol_available
    """
    results = pd.DataFrame(index=vix.index)
    window  = 126  # ~6 months

    rolling_mean = vix.rolling(window, min_periods=VIX_COLDSTART_DAYS).mean()
    rolling_std  = vix.rolling(window, min_periods=VIX_COLDSTART_DAYS).std()

    # Z-score where we have enough history
    with np.errstate(divide="ignore", invalid="ignore"):
        zscore = (vix - rolling_mean) / rolling_std

    # Percentile rank fallback where Z-score not yet available
    pct_rank = vix.expanding(min_periods=5).rank(pct=True)

    results["vix_zscore"] = zscore
    results["vix_pct_rank"] = pct_rank

    # Realized 20D annualized vol on SPY (spec condition)
    if spy_close is not None:
        log_ret = np.log(spy_close / spy_close.shift(1))
        realized = log_ret.rolling(20, min_periods=15).std() * np.sqrt(252) * 100
        realized = realized.reindex(vix.index)
        results["realized_vol_ann"] = realized
        results["realized_vol_available"] = realized.notna()
    else:
        results["realized_vol_ann"] = np.nan
        results["realized_vol_available"] = False

    zscore_col  = results["vix_zscore"]
    pct_col     = results["vix_pct_rank"]
    has_z       = zscore_col.notna()
    rv          = results["realized_vol_ann"]
    has_rv      = results["realized_vol_available"]

    # Dual conditions per spec; degrade to Z-only when realized vol unavailable
    high_cond = has_z & (zscore_col > 1.0)  & (~has_rv | (rv > 20.0))
    low_cond  = has_z & (zscore_col < -0.5) & (~has_rv | (rv < 14.0))

    # --- Axis 2 label (vectorized via np.select) ---
    vol_conditions = [
        high_cond,
        low_cond,
        ~has_z & (pct_col >= 0.70),
        ~has_z & (pct_col <= 0.35),
    ]
    vol_choices = ["High", "Low", "High", "Low"]
    results["axis2"]    = np.select(vol_conditions, vol_choices, default="Mid")

    # --- Vol mode (vectorized) ---
    results["vol_mode"] = np.where(has_z, "normal", "bootstrap")

    # --- Vol confidence (vectorized) ---
    # Normal-mode confidence: distance from thresholds scales up to 95
    conf_high = (50 + (zscore_col - 1.0)  * 25).clip(upper=95)
    conf_low  = (50 + (-zscore_col - 0.5) * 30).clip(upper=90)
    conf_mid  = pd.Series(55.0, index=results.index)
    # Bootstrap-mode confidence
    conf_boot = (50 + (pct_col - 0.50).abs() * 80).clip(upper=85).fillna(50)

    results["vol_conf"] = np.where(
        ~has_z, conf_boot,
        np.where(zscore_col > 1.0, conf_high,
        np.where(zscore_col < -0.5, conf_low, conf_mid))
    )

    return results


# ---------------------------------------------------------------------------
# Fast Layer — Axis 4: Macro Shock Detection (relative thresholds)
# ---------------------------------------------------------------------------

def compute_axis4_shock(vix: pd.Series,
                        hy_spread: pd.Series,
                        spy_close: pd.Series) -> pd.DataFrame:
    """
    Detect macro shock using relative VIX Z-score + credit spread velocity.
    No fixed VIX thresholds — all relative to rolling baselines.

    Returns DataFrame with: axis4, shock_flag, shock_watch_flag,
                            vix_zscore, vix_velocity, hy_zscore
    """
    results = pd.DataFrame(index=vix.index)
    window  = 126

    # VIX Z-score (same as Axis 2)
    vix_mean = vix.rolling(window, min_periods=VIX_COLDSTART_DAYS).mean()
    vix_std  = vix.rolling(window, min_periods=VIX_COLDSTART_DAYS).std()
    with np.errstate(divide="ignore", invalid="ignore"):
        vix_z = (vix - vix_mean) / vix_std

    # VIX velocity: % change over 5 sessions
    vix_velocity = vix.pct_change(5) * 100

    # HY spread Z-score
    if hy_spread is not None and not hy_spread.isna().all():
        hy_mean = hy_spread.rolling(window, min_periods=30).mean()
        hy_std  = hy_spread.rolling(window, min_periods=30).std()
        with np.errstate(divide="ignore", invalid="ignore"):
            hy_z = (hy_spread - hy_mean) / hy_std
    else:
        hy_z = pd.Series(0.0, index=vix.index)

    results["vix_zscore"]    = vix_z
    results["vix_velocity"]  = vix_velocity
    results["hy_spread_zscore"] = hy_z

    # SPY cross-asset correlation (simple 20D rolling correlation with GLD proxy)
    # In production: compute rolling corr(SPY, TLT, GLD) — here use vol proxy
    spy_vol_20d = spy_close.pct_change().rolling(20).std() * np.sqrt(252) * 100
    results["spy_vol_20d"] = spy_vol_20d

    def classify_shock(row):
        z   = row["vix_zscore"]
        vel = row["vix_velocity"]
        hy  = row["hy_spread_zscore"]

        if pd.isna(z):
            return "None", False, False

        # Shock Active: VIX Z > +3.0 AND (velocity > 40% OR HY spread spike)
        if z > SHOCK_ACTIVE_Z and (vel > 40 or hy > 1.5):
            return "Active", True, False

        # Shock Watch: VIX Z between 2.0 and 3.0
        if z > SHOCK_WATCH_Z:
            return "Watch", False, True

        return "None", False, False

    classified = results.apply(classify_shock, axis=1, result_type="expand")
    results["axis4"]          = classified[0]
    results["shock_flag"]     = classified[1]
    results["shock_watch_flag"] = classified[2]

    return results


# ---------------------------------------------------------------------------
# Fast Layer — Yield Curve Steepener Type
# ---------------------------------------------------------------------------

def compute_steepener_type(dgs2: pd.Series, dgs10: pd.Series,
                            window: int = 40) -> pd.Series:
    """
    Classify yield curve steepener type on 40-session rolling window.
    Used as a Fast Layer tiebreaker for Axis 3 classification.

    Macro convention: compute the spread first (10Y − 2Y), then difference it
    over the window. This avoids floating-point drift that occurs when
    differencing the two yields independently and then subtracting.

    Returns Series with: BearSteepener | BullSteepener |
                         BearFlattener | BullFlattener | Flat
    """
    # Standard macro convention: spread first, then diff
    spread        = dgs10 - dgs2               # raw 10Y-2Y spread (inspectable)
    spread_change = spread.diff(window)        # change in spread over window
    d2y           = dgs2.diff(window)          # change in 2Y yield
    d10y          = dgs10.diff(window)         # change in 10Y yield

    def classify(idx):
        sc  = spread_change.iloc[idx]
        d2  = d2y.iloc[idx]
        d10 = d10y.iloc[idx]

        if pd.isna(sc) or pd.isna(d2) or pd.isna(d10):
            return "Flat"

        threshold = 0.05  # bp threshold for meaningful change

        if abs(sc) < threshold:
            return "Flat"
        if sc > 0 and d10 > threshold:
            return "BearSteepener"   # long rates rising → growth/reflation
        if sc > 0 and d2 < -threshold:
            return "BullSteepener"   # short rates falling → rate cuts expected
        if sc < 0 and d2 > threshold:
            return "BearFlattener"   # short rates rising → Fed hiking
        if sc < 0 and d10 < -threshold:
            return "BullFlattener"   # long rates falling → flight to safety
        return "Flat"

    return pd.Series(
        [classify(i) for i in range(len(spread_change))],
        index=dgs2.index
    )


# ---------------------------------------------------------------------------
# Slow Layer — Axis 3: Economic Cycle (vintage data only)
# ---------------------------------------------------------------------------

def compute_axis3_cycle(macro_df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify economic cycle from vintage macro data.

    Parameters
    ----------
    macro_df : pd.DataFrame
        Indexed by date (release date of each print), columns:
          gdp_qoq      : GDP quarter-on-quarter % (advance print only)
          cpi_yoy      : CPI year-on-year % (first release only)
          unemployment : unemployment rate (first print)
          ism_mfg      : ISM Manufacturing PMI (first release)
          ism_svcs     : ISM Services PMI (first release)
          yield_10y    : 10Y Treasury yield
          yield_2y     : 2Y Treasury yield
          fed_stance   : "Neutral" | "Hiking" | "HikingAggressive" | "Cutting"
          vintage_flag : must be True (enforced below)

    Returns
    -------
    DataFrame with: axis3, slow_confidence, ism_split_flag,
                    steepener_contradiction_flag, staleness_days
    """
    # Enforce vintage flag — this is the look-ahead bias guard
    if "vintage_flag" in macro_df.columns:
        if not macro_df["vintage_flag"].all():
            raise ValueError(
                "Slow Layer received non-vintage data. "
                "All macro inputs must use first-print releases only. "
                "Use ALFRED API with vintage_dates parameter for backtesting."
            )

    # Forward-fill macro data between releases using the actual trading calendar.
    # DO NOT use pd.date_range(..., freq="B") — that generates Mon-Fri business
    # days which ignores market holidays (July 4th, Thanksgiving, etc.), causing
    # row misalignments when this joins with spy_ohlcv. Instead, reindex is called
    # later in segment_history against spy_ohlcv.index directly.
    # Here we fill on the raw macro index so staleness calculations are correct.
    macro_filled = macro_df.ffill()

    results = pd.DataFrame(index=macro_filled.index)

    def score_axis3(row):
        scores = {"Expansion": 0, "Reflation": 0, "Stagflation": 0, "Recession": 0}
        confidence_factors = []

        gdp    = row.get("gdp_qoq", np.nan)
        cpi    = row.get("cpi_yoy", np.nan)
        unemp  = row.get("unemployment", np.nan)
        ism_m  = row.get("ism_mfg", np.nan)
        ism_s  = row.get("ism_svcs", np.nan)
        stance = row.get("fed_stance", "")

        # GDP signal (weight 2 — most authoritative)
        if not pd.isna(gdp):
            if gdp > 2.0:
                scores["Expansion"] += 2
            elif gdp > 0 and gdp <= 2.5:
                scores["Reflation"] += 1; scores["Expansion"] += 1
            elif gdp < 0:
                scores["Recession"] += 2
            else:
                scores["Stagflation"] += 1; scores["Reflation"] += 1
            confidence_factors.append(1.0)

        # CPI signal (weight 2)
        if not pd.isna(cpi):
            if 2.0 <= cpi <= 3.5:
                scores["Expansion"] += 2
            elif 3.5 < cpi <= 6.0:
                scores["Reflation"] += 2
            elif cpi > 6.0:
                scores["Stagflation"] += 2
            else:
                scores["Recession"] += 1; scores["Expansion"] += 1
            confidence_factors.append(1.0)

        # ISM Manufacturing (weight 1)
        if not pd.isna(ism_m):
            if ism_m > 55:
                scores["Expansion"] += 1
            elif 50 <= ism_m <= 55:
                scores["Reflation"] += 1
            elif 45 <= ism_m < 50:
                scores["Stagflation"] += 1
            else:
                scores["Recession"] += 1
            confidence_factors.append(0.8)

        # ISM Services (weight 1)
        if not pd.isna(ism_s):
            if ism_s > 55:
                scores["Expansion"] += 1
            elif 50 <= ism_s <= 55:
                scores["Reflation"] += 1
            elif 45 <= ism_s < 50:
                scores["Stagflation"] += 1
            else:
                scores["Recession"] += 1
            confidence_factors.append(0.8)

        # Fed stance confirmation (weight 0.5)
        if stance:
            stance_map = {
                "Neutral":           {"Expansion": 0.5},
                "Hiking":            {"Reflation": 0.5},
                "HikingAggressive":  {"Stagflation": 0.5},
                "Cutting":           {"Recession": 0.5},
            }
            for key, boosts in stance_map.items():
                if stance == key:
                    for cycle, val in boosts.items():
                        scores[cycle] += val

        # Determine winner
        total = sum(scores.values())
        if total == 0:
            return "Expansion", 50.0, False, False

        winner    = max(scores, key=scores.get)
        runner_up = sorted(scores, key=scores.get, reverse=True)[1]

        max_score    = scores[winner]
        runner_score = scores[runner_up]

        # Confidence: how dominant is the winner?
        dominance = (max_score - runner_score) / total
        conf      = min(50 + dominance * 100, 95)

        # ISM split flag: mfg and svcs point to different cycles
        ism_split = False
        if not pd.isna(ism_m) and not pd.isna(ism_s):
            mfg_exp  = ism_m > 50
            svcs_exp = ism_s > 50
            ism_split = (mfg_exp != svcs_exp)
            if ism_split:
                conf -= 10

        return winner, conf, ism_split, False

    classified = results.reindex(macro_filled.index).copy()
    scored = pd.DataFrame(
        [score_axis3(row) for _, row in macro_filled.iterrows()],
        index=macro_filled.index,
        columns=["axis3", "slow_confidence", "ism_split_flag", "steepener_contradiction_flag"]
    )

    results = scored.copy()
    results["last_updated"] = macro_df.index[-1] if len(macro_df) > 0 else None

    # Staleness: days since last macro release
    last_release = macro_df.index
    def get_staleness(date):
        prior = last_release[last_release <= date]
        if len(prior) == 0:
            return 999
        return (date - prior[-1]).days

    results["staleness_days"] = [get_staleness(d) for d in macro_filled.index]

    # Staleness penalty: > 45 days → slow_confidence -= 20
    stale_mask = results["staleness_days"] > 45
    results.loc[stale_mask, "slow_confidence"] -= 20
    results["slow_confidence"] = results["slow_confidence"].clip(0, 100)

    return results


# ---------------------------------------------------------------------------
# Priority Arbiter — combine Fast + Slow, apply 7 rules
# ---------------------------------------------------------------------------

REGIME_MAP = {
    # (axis1_trend, axis2_vol, axis3_cycle, axis4_shock)
    ("Bull",     "Low",  "Expansion",  "None"):   ("RC-01", "Goldilocks Bull"),
    ("Bull",     "High", "Expansion",  "None"):   ("RC-02", "Choppy Bull"),
    ("Bull",     "Low",  "Reflation",  "None"):   ("RC-03", "Reflation Melt-Up"),
    ("Bull",     "High", "Reflation",  "None"):   ("RC-04", "Inflationary Bull"),
    ("Bear",     "High", "Recession",  "None"):   ("RC-05", "Classic Bear"),
    ("Bear",     "High", "Recession",  "Active"): ("RC-06", "Crisis Bear"),
    ("Bear",     "High", "Stagflation","None"):   ("RC-07", "Stagflation Bear"),
    ("Bear",     "High", "Stagflation","Active"): ("RC-08", "Supply Shock Bear"),
    ("Bear",     "High", "Reflation",  "Active"): ("RC-09", "Post-Shock Reflation Bear"),
    ("Sideways", "Low",  "Expansion",  "None"):   ("RC-10", "Quiet Consolidation"),
    ("Sideways", "High", "Expansion",  "None"):   ("RC-11", "Volatile Chop"),
    ("Sideways", "Low",  "Reflation",  "None"):   ("RC-12", "Slow Reflation Drift"),
    ("Sideways", "High", "Stagflation","None"):   ("RC-13", "Stagflation Chop"),
    ("Sideways", "High", "Recession",  "None"):   ("RC-14", "Bear Market Base"),
    ("Bull",     "High", "Expansion",  "Active"): ("RC-15", "Bull Market Shock"),
    ("Sideways", "High", "Expansion",  "Active"): ("RC-16", "Shock in Chop"),
    ("Bear",     "High", "Expansion",  "Active"): ("RC-17", "Sudden Bear Entry"),
    ("Bull",     "Low",  "Recession",  "None"):   ("RC-18", "Early Recovery Bull"),
    ("Bull",     "High", "Recession",  "Active"): ("RC-19", "Shock Recovery"),
    ("Sideways", "Low",  "Recession",  "None"):   ("RC-20", "Slow Recovery Base"),
}

# Nearest neighbor fallback for unmapped combos
def _nearest_regime(a1, a2, a3, a4):
    """
    Find the closest mapped regime by relaxing axes in priority order.

    Relaxation order:
      1. Shock (most common unmapped scenario — Watch/Mid not in map)
      2. Vol   (Mid vol not in map)
      3. Trend (least likely to relax, but handles edge cases)
      4. Macro cycle (relax to Expansion before final fallback — prevents
         a valid (Bull, Low, Stagflation, None) environment from hard-defaulting
         to RC-10 without attempting any cycle alternatives)
    """
    # Try relaxing shock first (most common unmapped scenario)
    for shock_alt in ["None", "Active", "Watch"]:
        key = (a1, a2, a3, shock_alt)
        if key in REGIME_MAP:
            return REGIME_MAP[key], "SHOCK_RELAXED"
    # Try relaxing vol
    for vol_alt in ["High", "Low", "Mid"]:
        key = (a1, vol_alt, a3, a4)
        if key in REGIME_MAP:
            return REGIME_MAP[key], "VOL_RELAXED"
    # Try relaxing trend
    for trend_alt in ["Bull", "Bear", "Sideways"]:
        key = (trend_alt, a2, a3, a4)
        if key in REGIME_MAP:
            return REGIME_MAP[key], "TREND_RELAXED"
    # Try relaxing Axis 3 (macro cycle) before giving up
    for cycle_alt in ["Expansion", "Recession", "Reflation", "Stagflation"]:
        if cycle_alt == a3:
            continue  # already tried
        key = (a1, a2, cycle_alt, a4)
        if key in REGIME_MAP:
            return REGIME_MAP[key], "CYCLE_RELAXED"
    # Final fallback
    return ("RC-10", "Quiet Consolidation"), "FALLBACK"


def priority_arbiter(date: pd.Timestamp,
                     fast: FastLayerResult,
                     slow: SlowLayerResult) -> RegimeResult:
    """
    Apply Priority Arbiter rules 1–7 to produce the active regime.

    Rules (in strict order):
      1. Shock Override — suppress A3 if shock active
      2. Fast owns A1, A2, A4
      3. Slow owns A3 (unless Rule 1)
      4. Staleness penalty
      5. Transition detection → blend flag + haircut
      6. Steepener contradiction → slow_confidence −10
      7. Execution floor — overall_confidence < 60 → Cash/Neutral
    """
    axis1  = fast.axis1_trend
    axis2  = fast.axis2_vol
    axis4  = fast.axis4_shock
    fc     = fast.fast_confidence

    axis3  = slow.axis3_cycle
    sc     = slow.slow_confidence

    shock_flag      = fast.axis4_shock == "Active"
    shock_watch_flag = fast.axis4_shock == "Watch"

    floor_reason   = ""
    transition_flag = False

    # Rule 1 — Shock Override
    if shock_flag:
        # Suppress Axis 3 — map to shock regime ignoring cycle
        axis3 = "SUPPRESSED"

    # Rule 3 — Steepener contradiction adjusts slow_confidence
    if slow.steepener_contradiction:
        sc = max(sc - 10, 0)
        floor_reason += "STEEPENER_CONTRADICTION;"

    # Rule 4 — Staleness penalty already applied in slow layer
    if slow.staleness_days > 45 and sc < 50:
        floor_reason += "STALE_SLOW_DATA;"

    # Find regime from map
    if shock_flag:
        # Shock override: use shock axis4 for mapping
        lookup_key = (axis1, "High", axis3 if axis3 != "SUPPRESSED" else "Expansion", "Active")
    else:
        lookup_key = (axis1, axis2, axis3, axis4)

    if lookup_key in REGIME_MAP:
        regime_code, regime_label = REGIME_MAP[lookup_key]
        mapping_conf = 90.0
    else:
        (regime_code, regime_label), reason = _nearest_regime(
            axis1, axis2, axis3 if axis3 != "SUPPRESSED" else "Expansion", axis4
        )
        mapping_conf = 65.0
        floor_reason += f"NEAREST_NEIGHBOR_{reason};"

    # Rule 5 — Transition detection
    conf_gap = abs(fc - sc)
    if fc < TRANSITION_THRESHOLD or conf_gap > 30:
        transition_flag = True
        haircut = 15.0
        if floor_reason:
            floor_reason += "TRANSITION_HAIRCUT;"
        else:
            floor_reason = "TRANSITION_HAIRCUT;"
    else:
        haircut = 0.0

    # Combine fast + slow confidence (weighted average)
    if shock_flag:
        # Shock: fast layer dominates
        combined = fc * 0.85 + mapping_conf * 0.15
    else:
        combined = (fc * 0.5 + sc * 0.3 + mapping_conf * 0.2)

    overall_confidence = max(combined - haircut, 0)

    # Rule 6 — Shock Watch Zone
    if shock_watch_flag and not shock_flag:
        floor_reason += "SHOCK_WATCH_ZONE;"

    # Layer divergence (spec floor reason): layers strongly disagree
    if conf_gap > 40:
        floor_reason += "LAYER_DIVERGENCE;"

    # Vol bootstrap mode (spec floor reason): Z-score cold-start degrades
    # the reliability of A2/A4 classification
    if getattr(fast, "vol_mode", "normal") == "bootstrap":
        floor_reason += "VOL_BOOTSTRAP_MODE;"

    # Rule 7 — Execution floor
    floor_triggered = overall_confidence < EXECUTION_FLOOR
    if floor_triggered and not floor_reason:
        floor_reason = "LOW_CONFIDENCE"

    # Spec: when multiple floor reasons fire simultaneously, report COMBINED
    # (individual reasons retained after the prefix for debuggability)
    if floor_reason.count(";") > 1:
        floor_reason = "COMBINED;" + floor_reason

    return RegimeResult(
        date=date,
        regime_code=regime_code,
        regime_label=regime_label,
        overall_confidence=round(overall_confidence, 2),
        fast_confidence=round(fc, 2),
        slow_confidence=round(sc, 2),
        shock_flag=shock_flag,
        shock_watch_flag=shock_watch_flag,
        transition_flag=transition_flag,
        vol_mode=fast.vol_mode,
        floor_triggered=floor_triggered,
        floor_reason=floor_reason.strip(";"),
        axis1=axis1,
        axis2=axis2,
        axis3=axis3,
        axis4=axis4,
        steepener_type=fast.steepener_type,
        vix_zscore=round(fast.vix_zscore, 3),
    )


# ---------------------------------------------------------------------------
# Dynamic Sector Assignment (Pearson correlation only — no beta in scoring)
# ---------------------------------------------------------------------------

def assign_sector(ticker_returns: pd.Series,
                  sector_returns: pd.DataFrame,
                  window: int = 60) -> pd.DataFrame:
    """
    Assign ticker to sector using rolling 60-day Pearson correlation.
    Beta is computed as diagnostic only — NOT used in scoring.

    Parameters
    ----------
    ticker_returns  : daily log-returns for the ticker
    sector_returns  : DataFrame with OHLCV-derived log-returns, one column per sector ETF
    window          : rolling window (default 60 sessions)

    Returns
    -------
    DataFrame with: assigned_sector, top_correlation, assignment_confidence,
                    second_sector, second_confidence, beta_diagnostic,
                    sector_ambiguous, sector_unclassifiable
    """
    results = []

    for date in ticker_returns.index:
        # Get trailing window
        end_idx   = ticker_returns.index.get_loc(date)
        start_idx = max(0, end_idx - window + 1)
        actual_window = end_idx - start_idx + 1

        t_ret = ticker_returns.iloc[start_idx:end_idx + 1].dropna()

        if actual_window < 30 or len(t_ret) < 20:
            results.append({
                "date": date, "assigned_sector": None,
                "top_correlation": np.nan, "assignment_confidence": 0.0,
                "second_sector": None, "second_confidence": 0.0,
                "beta_diagnostic": np.nan, "sector_ambiguous": False,
                "sector_unclassifiable": True, "short_history": True,
            })
            continue

        corr_scores   = {}
        beta_diags    = {}
        short_history = actual_window < window

        for sector in sector_returns.columns:
            s_ret = sector_returns[sector].iloc[start_idx:end_idx + 1]
            common = t_ret.index.intersection(s_ret.dropna().index)
            if len(common) < 20:
                continue

            t_vals = t_ret.loc[common].values
            s_vals = s_ret.loc[common].values

            # Guard against zero-variance inputs (halted ticker, illiquid ETF,
            # or perfectly flat price series). scipy.stats.pearsonr raises
            # ConstantInputWarning and returns NaN for these — skip the pair.
            if np.std(t_vals) == 0 or np.std(s_vals) == 0:
                continue

            # Pearson correlation — the ONLY scoring metric
            corr_val, _ = stats.pearsonr(t_vals, s_vals)
            corr_scores[sector] = corr_val

            # Beta — diagnostic only (NOT used in assignment decision)
            cov_val  = np.cov(t_vals, s_vals)[0, 1]
            var_val  = np.var(s_vals, ddof=1)
            beta_diags[sector] = cov_val / var_val if var_val > 0 else np.nan

        if not corr_scores:
            results.append({
                "date": date, "assigned_sector": None,
                "top_correlation": np.nan, "assignment_confidence": 0.0,
                "second_sector": None, "second_confidence": 0.0,
                "beta_diagnostic": np.nan, "sector_ambiguous": False,
                "sector_unclassifiable": True, "short_history": short_history,
            })
            continue

        # Suppress negative correlations (not a valid sector match)
        positive_corr = {s: max(v, 0) for s, v in corr_scores.items()}
        total_positive = sum(positive_corr.values())

        if total_positive == 0:
            results.append({
                "date": date, "assigned_sector": None,
                "top_correlation": np.nan, "assignment_confidence": 0.0,
                "second_sector": None, "second_confidence": 0.0,
                "beta_diagnostic": np.nan, "sector_ambiguous": False,
                "sector_unclassifiable": True, "short_history": short_history,
            })
            continue

        # Sort by raw correlation (including negative)
        sorted_sectors = sorted(corr_scores.items(),
                                key=lambda x: x[1], reverse=True)
        top_sector, top_corr_val = sorted_sectors[0]
        sec_sector = sorted_sectors[1][0] if len(sorted_sectors) > 1 else None
        sec_corr_val = sorted_sectors[1][1] if sec_sector else 0.0

        # Confidence = gap ratio dampened by absolute correlation strength.
        # Raw gap ratio (top - sec) / top is hyper-sensitive to noise when
        # top_corr_val is near zero (e.g. top=0.02, sec=0.01 → gap ratio=0.50,
        # but a 0.02 Pearson is statistical noise). The dampener min(top/0.30, 1.0)
        # scales confidence toward zero when the absolute correlation is weak,
        # regardless of how large the gap looks in relative terms.
        if top_corr_val <= 0:
            assign_conf = 0.0
        elif sec_corr_val < 0:
            # No positive competitor — use absolute strength, dampened
            assign_conf = min(top_corr_val, 1.0) * min(top_corr_val / 0.30, 1.0)
        else:
            raw_gap_ratio = (top_corr_val - sec_corr_val) / top_corr_val
            dampener      = min(top_corr_val / 0.30, 1.0)  # ramps to 1.0 at corr≥0.30
            assign_conf   = raw_gap_ratio * dampener

        # Normalize to 0-1 range for interpretability
        # gap_ratio ~0.10 = slight edge; ~0.25 = clear winner; ~0.50 = dominant
        sec_conf = (sec_corr_val / top_corr_val) if top_corr_val > 0 else 0.0

        # Short history penalty (spec: -0.15 on the share-of-mass scale where
        # AMBIGUOUS threshold = 0.35, i.e. 43% of threshold. On the gap-ratio
        # scale used here, AMBIGUOUS = 0.10, so the proportional equivalent is
        # 0.43 x 0.10 ~= 0.05). SHORT_HISTORY flag is carried in output.
        if short_history:
            assign_conf = max(assign_conf - 0.05, 0)

        # Thresholds calibrated to gap_ratio scale
        ambiguous        = assign_conf < 0.10   # very close second sector
        unclassifiable   = (assign_conf < 0.02  # essentially tied
                            or top_corr_val <= 0)  # no positive correlation

        results.append({
            "date": date,
            "assigned_sector": top_sector,
            "top_correlation": round(corr_scores[top_sector], 4),
            "assignment_confidence": round(assign_conf, 4),
            "second_sector": sec_sector,
            "second_confidence": round(sec_conf, 4),
            "beta_diagnostic": round(beta_diags.get(top_sector, np.nan), 4),
            "sector_ambiguous": ambiguous,
            "sector_unclassifiable": unclassifiable,
            "short_history": short_history,
        })

    return pd.DataFrame(results).set_index("date")


# ---------------------------------------------------------------------------
# Full Segmentation Pipeline — main entry point
# ---------------------------------------------------------------------------

def segment_history(spy_ohlcv: pd.DataFrame,
                    vix: pd.Series,
                    hy_spread: pd.Series,
                    dgs2: pd.Series,
                    dgs10: pd.Series,
                    macro_vintage: pd.DataFrame,
                    ticker_returns: pd.Series,
                    sector_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full Phase 1 segmentation for one ticker.

    Returns a DataFrame with one row per trading day containing:
        date, regime_code, regime_label, assigned_sector,
        overall_confidence, fast_confidence, slow_confidence,
        shock_flag, shock_watch_flag, transition_flag, floor_triggered,
        floor_reason, axis1, axis2, axis3, axis4, steepener_type,
        vix_zscore, assignment_confidence, beta_diagnostic,
        sector_ambiguous, sector_unclassifiable, vol_mode

    Each row is a (date, regime, sector) cell observation.
    """
    print("  Phase 1: Computing Fast Layer axes...")
    trend_df     = compute_axis1_trend(spy_ohlcv["close"],
                                       spy_ohlcv["high"],
                                       spy_ohlcv["low"])
    vol_df       = compute_axis2_vol(vix, spy_close=spy_ohlcv["close"])
    shock_df     = compute_axis4_shock(vix, hy_spread, spy_ohlcv["close"])
    steepener_s  = compute_steepener_type(dgs2, dgs10, window=40)
    # Raw spread (10Y-2Y) exposed for deep-inversion flag in slow layer lookup
    raw_spread_s = dgs10 - dgs2

    print("  Phase 1: Computing Slow Layer (Axis 3)...")
    slow_df_raw  = compute_axis3_cycle(macro_vintage)
    # Align slow layer to the actual trading calendar (not freq="B" business days).
    # This eliminates NaN misalignments on market holidays that freq="B" misses.
    slow_df      = slow_df_raw.reindex(spy_ohlcv.index, method="ffill")

    print("  Phase 1: Running Priority Arbiter...")
    regime_records = []

    for date in spy_ohlcv.index:
        # Build FastLayerResult
        t_row = trend_df.loc[date] if date in trend_df.index else None
        v_row = vol_df.loc[date]   if date in vol_df.index   else None
        s_row = shock_df.loc[date] if date in shock_df.index else None

        if t_row is None or v_row is None or s_row is None:
            continue

        fast = FastLayerResult(
            axis1_trend  = t_row["axis1"]    if not pd.isna(t_row.get("axis1",   np.nan)) else "Sideways",
            axis2_vol    = v_row["axis2"]    if not pd.isna(v_row.get("axis2",   np.nan)) else "Mid",
            axis4_shock  = s_row["axis4"]    if not pd.isna(s_row.get("axis4",   np.nan)) else "None",
            steepener_type = steepener_s.loc[date] if date in steepener_s.index else "Flat",
            fast_confidence = float(t_row.get("fast_trend_conf", 50)),
            vol_mode     = v_row.get("vol_mode", "normal"),
            vix_zscore   = float(v_row.get("vix_zscore", 0)),
            vix_velocity = float(s_row.get("vix_velocity", 0)),
            hy_spread_zscore = float(s_row.get("hy_spread_zscore", 0)),
        )

        # Inject raw spread into slow_df row so the contradiction check can
        # detect deep inversions regardless of 40-day velocity
        raw_spread_val = float(raw_spread_s.loc[date]) if date in raw_spread_s.index else np.nan

        # Build SlowLayerResult — slow_df is pre-aligned to spy_ohlcv.index
        if date in slow_df.index and not slow_df.loc[date].isna().all():
            slow_row = slow_df.loc[date]
        else:
            slow_row = None

        if slow_row is None:
            slow = SlowLayerResult(
                axis3_cycle="Expansion", slow_confidence=50.0,
                last_updated=None, data_vintage=True, ism_split_flag=False,
                steepener_contradiction=False, staleness_days=999,
            )
        else:
            # Check steepener contradiction
            steepener = fast.steepener_type
            cycle     = slow_row["axis3"]
            st_contradiction = (
                (steepener == "BullSteepener" and cycle in ["Expansion", "Reflation"]) or
                (steepener == "BearSteepener" and cycle in ["Recession"])
            )

            # Deep inversion flag: a heavily inverted curve (10Y-2Y < -0.50%)
            # is a structural contraction warning regardless of 40-day velocity.
            # A "Flat" steepener can mask a deeply inverted curve, so we pass
            # the raw spread level through and flag it directly.
            raw_spread = raw_spread_val
            if not pd.isna(raw_spread) and raw_spread < -0.50:
                st_contradiction = True   # deep inversion overrides any steepener label

            slow = SlowLayerResult(
                axis3_cycle=slow_row["axis3"],
                slow_confidence=float(slow_row["slow_confidence"]),
                last_updated=date,
                data_vintage=True,
                ism_split_flag=bool(slow_row.get("ism_split_flag", False)),
                steepener_contradiction=st_contradiction,
                staleness_days=int(slow_row.get("staleness_days", 0)),
            )

        result = priority_arbiter(date, fast, slow)
        regime_records.append(vars(result))

    regime_df = pd.DataFrame(regime_records).set_index("date")

    print("  Phase 1: Computing Dynamic Sector Assignment...")
    # Sector returns start 1 day after prices — align forward-fill
    sector_df = assign_sector(ticker_returns, sector_returns, window=60)
    sector_df = sector_df.reindex(regime_df.index, method="ffill")

    # Merge regime + sector
    combined = regime_df.join(sector_df, how="left")

    print(f"  Phase 1: Complete. {len(combined)} observations segmented.")
    return combined


# ---------------------------------------------------------------------------
# Cell statistics — count observations per (regime, sector) cell
# ---------------------------------------------------------------------------

def compute_cell_stats(segmented_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each (regime_code, assigned_sector) pair, count observations
    and flag LOW_SAMPLE cells (< MIN_CELL_OBS observations).

    Used by Phase 2 to decide whether to use empirical IC or Bayesian prior.
    """
    # Exclude floor-triggered and unclassifiable rows
    valid = segmented_df[
        ~segmented_df["floor_triggered"].astype(bool) &
        ~segmented_df["sector_unclassifiable"].fillna(False).astype(bool)
    ]

    cell_stats = (
        valid.groupby(["regime_code", "assigned_sector"])
        .agg(
            obs_count=("regime_code", "count"),
            avg_confidence=("overall_confidence", "mean"),
            shock_pct=("shock_flag", "mean"),
            transition_pct=("transition_flag", "mean"),
        )
        .reset_index()
    )

    cell_stats["low_sample"] = cell_stats["obs_count"] < MIN_CELL_OBS
    cell_stats["set_id"] = (
        "SET-" + cell_stats["regime_code"] + "-" + cell_stats["assigned_sector"]
    )

    return cell_stats.sort_values("obs_count", ascending=False)


# ---------------------------------------------------------------------------
# Quick validation on synthetic data
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Phase 1 — Segmentation Engine: Validation on synthetic data")
    print("=" * 60)

    np.random.seed(42)
    n = 500
    dates = pd.bdate_range("2022-01-01", periods=n)

    # Synthetic SPY OHLCV
    spy_close = pd.Series(
        400 * np.exp(np.cumsum(np.random.normal(0.0003, 0.012, n))),
        index=dates
    )
    spy_high  = spy_close * (1 + np.abs(np.random.normal(0, 0.005, n)))
    spy_low   = spy_close * (1 - np.abs(np.random.normal(0, 0.005, n)))
    spy_ohlcv = pd.DataFrame({
        "open": spy_close.shift(1).fillna(spy_close.iloc[0]),
        "high": spy_high, "low": spy_low, "close": spy_close
    })

    # Synthetic VIX (baseline ~18, occasional spikes)
    vix_base = 18 + np.random.normal(0, 3, n)
    vix_base[200:220] = 38   # shock period
    vix = pd.Series(np.abs(vix_base), index=dates)

    # Synthetic HY spread
    hy_spread = pd.Series(
        400 + np.cumsum(np.random.normal(0, 5, n)), index=dates
    )

    # Synthetic yield curve
    dgs2  = pd.Series(3.0 + np.random.normal(0, 0.1, n), index=dates)
    dgs10 = pd.Series(4.0 + np.random.normal(0, 0.15, n), index=dates)

    # Synthetic macro vintage data (quarterly GDP, monthly CPI)
    macro_dates = pd.bdate_range("2022-01-01", periods=n, freq="QS")[:8]
    macro_vintage = pd.DataFrame({
        "gdp_qoq":     [2.1, 1.8, -0.5, -0.8, 0.5, 1.2, 2.0, 2.5],
        "cpi_yoy":     [3.2, 4.1, 5.8, 7.1, 6.5, 4.2, 3.1, 2.8],
        "unemployment":[4.0, 4.1, 4.3, 4.6, 4.8, 4.5, 4.2, 4.0],
        "ism_mfg":     [56, 53, 48, 44, 46, 50, 54, 57],
        "ism_svcs":    [57, 55, 52, 49, 51, 53, 56, 58],
        "fed_stance":  ["Neutral","Hiking","Hiking","HikingAggressive",
                        "HikingAggressive","Cutting","Cutting","Neutral"],
        "vintage_flag":[True]*8,
    }, index=macro_dates)

    # Synthetic ticker + sector returns
    ticker_ret = spy_close.pct_change().apply(np.log1p).dropna()
    sector_ret_dict = {}
    for s in SECTORS:
        noise = np.random.normal(0, 0.003, len(ticker_ret))
        sector_ret_dict[s] = (ticker_ret.values + noise)
    sector_returns = pd.DataFrame(sector_ret_dict, index=ticker_ret.index)
    # Make XLK most correlated
    sector_returns["XLK"] = ticker_ret.values + np.random.normal(0, 0.001, len(ticker_ret))

    # Run segmentation
    result = segment_history(
        spy_ohlcv=spy_ohlcv,
        vix=vix,
        hy_spread=hy_spread,
        dgs2=dgs2,
        dgs10=dgs10,
        macro_vintage=macro_vintage,
        ticker_returns=ticker_ret,
        sector_returns=sector_returns,
    )

    print("\nSegmentation output (first 5 rows):")
    print(result[["regime_code", "regime_label", "assigned_sector",
                   "overall_confidence", "shock_flag", "transition_flag",
                   "axis1", "axis2", "axis3", "vol_mode"]].head())

    print("\nRegime distribution:")
    print(result["regime_code"].value_counts().head(10))

    print("\nShock period check (rows 200-220):")
    shock_period = result.iloc[200:220][["regime_code", "shock_flag", "axis4", "vix_zscore"]]
    print(shock_period)

    cell_stats = compute_cell_stats(result)
    print("\nTop cells by observation count:")
    print(cell_stats[["regime_code", "assigned_sector",
                       "obs_count", "low_sample"]].head(10))

    low = cell_stats[cell_stats["low_sample"]]
    print(f"\nLOW_SAMPLE cells: {len(low)} (will use Bayesian prior in Phase 2)")
    print("Phase 1 validation complete.")
