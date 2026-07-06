"""
indicators.py
=============
Curated TA-Lib indicator set only. NO full-library enumeration.

Two families:
  CONTINUOUS  -> a real-valued Series per bar, screened via Spearman rank IC.
  DISCRETE    -> a categorical state per bar (bullish / bearish / neutral),
                 screened via forward-return expectancy per state.

Design rules enforced here:
  * Never expose a raw moving-average LEVEL as a continuous signal. MA info only
    enters via a derived cross (discrete) or a price/MA ratio (continuous).
  * All TA-Lib functions are causal: indicator[t] depends only on prices <= t.
  * Warm-up NaNs are left as NaN (dropped later, never filled).

Every indicator function receives arrays (o, h, l, c, v) as float64 numpy arrays
and returns a numpy array aligned to the same index (NaN where undefined).
"""

from __future__ import annotations

import numpy as np
import talib


# --------------------------------------------------------------------------- #
# CONTINUOUS indicators  ->  Spearman IC
# --------------------------------------------------------------------------- #
# Each entry: name -> callable(o,h,l,c,v) -> np.ndarray
# `name` is the label used in output. Volume-based indicators are tagged so the
# engine can flag them on volume-less series (yields / FX).

def _rsi(o, h, l, c, v):        return talib.RSI(c, timeperiod=14)
def _stoch_k(o, h, l, c, v):
    k, d = talib.STOCH(h, l, c, fastk_period=14, slowk_period=3, slowk_matype=0,
                       slowd_period=3, slowd_matype=0)
    return k
def _stochf_k(o, h, l, c, v):
    k, d = talib.STOCHF(h, l, c, fastk_period=14, fastd_period=3, fastd_matype=0)
    return k
def _cci(o, h, l, c, v):        return talib.CCI(h, l, c, timeperiod=20)
def _willr(o, h, l, c, v):      return talib.WILLR(h, l, c, timeperiod=14)
def _mfi(o, h, l, c, v):        return talib.MFI(h, l, c, v, timeperiod=14)
def _cmo(o, h, l, c, v):        return talib.CMO(c, timeperiod=14)
def _roc(o, h, l, c, v):        return talib.ROC(c, timeperiod=10)
def _mom(o, h, l, c, v):        return talib.MOM(c, timeperiod=10)
def _ultosc(o, h, l, c, v):     return talib.ULTOSC(h, l, c, timeperiod1=7,
                                                     timeperiod2=14, timeperiod3=28)
def _aroonosc(o, h, l, c, v):   return talib.AROONOSC(h, l, timeperiod=14)

def _adx(o, h, l, c, v):        return talib.ADX(h, l, c, timeperiod=14)
def _adxr(o, h, l, c, v):       return talib.ADXR(h, l, c, timeperiod=14)
def _dx(o, h, l, c, v):         return talib.DX(h, l, c, timeperiod=14)

def _natr(o, h, l, c, v):       return talib.NATR(h, l, c, timeperiod=14)
def _atr_ratio(o, h, l, c, v):
    atr = talib.ATR(h, l, c, timeperiod=14)
    with np.errstate(divide="ignore", invalid="ignore"):
        return atr / c

def _obv(o, h, l, c, v):        return talib.OBV(c, v)
def _ad(o, h, l, c, v):         return talib.AD(h, l, c, v)
def _adosc(o, h, l, c, v):      return talib.ADOSC(h, l, c, v, fastperiod=3, slowperiod=10)

def _bbands_pctb(o, h, l, c, v):
    up, mid, low = talib.BBANDS(c, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (c - low) / (up - low)
def _apo(o, h, l, c, v):        return talib.APO(c, fastperiod=12, slowperiod=26, matype=0)
def _ppo(o, h, l, c, v):        return talib.PPO(c, fastperiod=12, slowperiod=26, matype=0)


# name -> (callable, uses_volume)
CONTINUOUS = {
    # momentum
    "RSI_14":       (_rsi,       False),
    "STOCH_K_14":   (_stoch_k,   False),
    "STOCHF_K_14":  (_stochf_k,  False),
    "CCI_20":       (_cci,       False),
    "WILLR_14":     (_willr,     False),
    "MFI_14":       (_mfi,       True),
    "CMO_14":       (_cmo,       False),
    "ROC_10":       (_roc,       False),
    "MOM_10":       (_mom,       False),
    "ULTOSC":       (_ultosc,    False),
    "AROONOSC_14":  (_aroonosc,  False),
    # trend strength
    "ADX_14":       (_adx,       False),
    "ADXR_14":      (_adxr,      False),
    "DX_14":        (_dx,        False),
    # volatility (normalized only)
    "NATR_14":      (_natr,      False),
    "ATR_RATIO_14": (_atr_ratio, False),
    # volume
    "OBV":          (_obv,       True),
    "AD":           (_ad,        True),
    "ADOSC_3_10":   (_adosc,     True),
    # derived bounded
    "BBANDS_PCTB_20_2": (_bbands_pctb, False),
    "APO_12_26":    (_apo,       False),
    "PPO_12_26":    (_ppo,       False),
}


# --------------------------------------------------------------------------- #
# DISCRETE signals  ->  forward-return expectancy per state
# --------------------------------------------------------------------------- #
# Each returns an integer-coded state array aligned to the index:
#   +1 = bullish-labelled state, -1 = bearish-labelled state, 0 = neutral/flat,
#   NaN during warm-up.
# The "bullish/bearish" LABEL is just a fixed reference for computing the spread
# (exp[+1] - exp[-1]); the engine reports the spread with its natural sign, so a
# label being "wrong" (contrarian) shows up as a negative spread, not a bug.

def _macd_cross(o, h, l, c, v):
    """MACD line vs signal line. above -> +1 (long), below -> -1 (short)."""
    macd, sig, hist = talib.MACD(c, fastperiod=12, slowperiod=26, signalperiod=9)
    state = np.full(c.shape, np.nan)
    valid = ~np.isnan(macd) & ~np.isnan(sig)
    diff = macd - sig
    state[valid & (diff > 0)] = 1.0
    state[valid & (diff < 0)] = -1.0
    state[valid & (diff == 0)] = 0.0
    return state

def _ema_cross(o, h, l, c, v):
    """EMA(50) vs EMA(200). fast>slow -> +1, else -1."""
    fast = talib.EMA(c, timeperiod=50)
    slow = talib.EMA(c, timeperiod=200)
    state = np.full(c.shape, np.nan)
    valid = ~np.isnan(fast) & ~np.isnan(slow)
    state[valid & (fast > slow)] = 1.0
    state[valid & (fast <= slow)] = -1.0
    return state

def _rsi_threshold(o, h, l, c, v):
    """RSI(14) bands. oversold(<30) -> +1 (bullish label), overbought(>70) -> -1."""
    rsi = talib.RSI(c, timeperiod=14)
    state = np.full(c.shape, np.nan)
    valid = ~np.isnan(rsi)
    state[valid] = 0.0                      # neutral band
    state[valid & (rsi < 30)] = 1.0
    state[valid & (rsi > 70)] = -1.0
    return state

def _sar_cross(o, h, l, c, v):
    """Parabolic SAR. close above SAR -> +1 (uptrend), below -> -1."""
    sar = talib.SAR(h, l, acceleration=0.02, maximum=0.2)
    state = np.full(c.shape, np.nan)
    valid = ~np.isnan(sar)
    state[valid & (c > sar)] = 1.0
    state[valid & (c <= sar)] = -1.0
    return state


# name -> (callable, type_label, bull_label, bear_label)
DISCRETE = {
    "MACD_SIGNAL_CROSS": (_macd_cross,   "discrete_cross",     "macd>signal", "macd<signal"),
    "EMA_50_200_CROSS":  (_ema_cross,    "discrete_cross",     "ema50>ema200", "ema50<=ema200"),
    "RSI_14_THRESHOLD":  (_rsi_threshold, "discrete_threshold", "oversold<30", "overbought>70"),
    "SAR_PRICE_CROSS":   (_sar_cross,    "discrete_cross",     "close>sar",   "close<sar"),
}


# --------------------------------------------------------------------------- #
# Excluded (kept auditable in output notes)
# --------------------------------------------------------------------------- #
EXCLUDED = {
    "CDL* candlestick patterns (~60)":
        "fire too rarely; poor screen; not worth multiple-comparisons cost",
    "Raw overlays as standalone values (SMA/EMA/WMA/DEMA/TEMA/TRIMA/KAMA/MAMA/T3/"
    "MIDPOINT/MIDPRICE/HT_TRENDLINE)":
        "never IC a raw MA level; use derived cross (discrete) or price/MA ratio",
    "Math Transform / Math Operator / Price Transform groups":
        "not signals",
}
