"""Universe (incl. crypto) and data access for the pandas_ta set search.
Crypto trades 7d/week; portfolio-level alignment to the equity calendar is
done by the consumer (portfolio_backtest) via reindex+ffill of CLOSE, so
weekend crypto moves fold into the next trading day."""
from __future__ import annotations

import numpy as np
import pandas as pd

import price_cache
from grouped_ic_backtest import ASSETS

UNIVERSE: dict = {
    **ASSETS,
    "BTC-USD": {"name": "Bitcoin", "class": "crypto"},
    "ETH-USD": {"name": "Ethereum", "class": "crypto"},
}

# ^TNX is a yield level, not investable (TLT carries duration exposure)
TRADABLE = [t for t in UNIVERSE if t != "^TNX"]

MIN_NONZERO_VOL_FRAC = 0.50


def return_mode(tkr: str) -> str:
    return UNIVERSE[tkr].get("return_mode", "log")


def load_asset(tkr: str) -> pd.DataFrame | None:
    df = price_cache.load(tkr)
    if df is None or len(df) == 0:
        return None
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    return df.sort_index()


def volume_usable(df: pd.DataFrame) -> tuple[bool, pd.Series]:
    """(usable_flag, volume with the leading zero/NaN prefix masked to NaN).
    Usable iff, after the first nonzero print, >=50% of bars have volume>0."""
    v = pd.to_numeric(df["volume"], errors="coerce")
    nz = v > 0
    if not nz.any():
        return False, v.where(nz)
    first = nz.idxmax()
    tail = v.loc[first:]
    frac = float((tail > 0).mean())
    masked = v.copy()
    masked.loc[:first] = np.nan
    masked.loc[first] = v.loc[first]
    masked = masked.astype("float64")
    return frac >= MIN_NONZERO_VOL_FRAC, masked


def master_calendar(start: str | None = None) -> pd.DatetimeIndex:
    spx = load_asset("^GSPC")
    idx = spx.index
    if start is not None:
        idx = idx[idx >= pd.Timestamp(start)]
    return idx
