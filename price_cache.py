"""
price_cache.py
==============
Thin on-disk cache in front of data_loader.load_ohlcv, to survive yfinance
rate-limiting across repeated backtest runs. Successful fetches are cached to
./price_cache/<ticker>.csv; failed fetches are NOT cached (so a later run retries
only the still-missing tickers). Normalized OHLCV contract is unchanged.
"""

from __future__ import annotations

import os
import re
import time

import pandas as pd

import data_loader

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "price_cache")


def _safe(tkr: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", tkr)


def _path(tkr: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{_safe(tkr)}.csv")


def load(tkr: str) -> pd.DataFrame | None:
    """Return cached normalized OHLCV if present, else fetch + cache."""
    path = _path(tkr)
    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        for c in ("open", "high", "low", "close", "volume"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df
    df = data_loader.load_ohlcv(tkr)
    if df is not None and len(df) > 0:
        df.to_csv(path)
    return df


def prime(tickers, sleep_s: float = 4.0) -> dict:
    """Fetch any not-yet-cached tickers, spacing requests to dodge rate limits.
    Returns {ticker: rows or None}."""
    status = {}
    for tkr in tickers:
        path = _path(tkr)
        if os.path.exists(path):
            df = load(tkr)
            status[tkr] = len(df) if df is not None else None
            print(f"  cached  {tkr:<11} rows={status[tkr]}")
            continue
        df = data_loader.load_ohlcv(tkr)
        if df is not None and len(df) > 0:
            df.to_csv(path)
            status[tkr] = len(df)
            print(f"  fetched {tkr:<11} rows={len(df)}")
        else:
            status[tkr] = None
            print(f"  FAILED  {tkr:<11} (will retry next run)")
        time.sleep(sleep_s)     # be gentle with yfinance
    return status


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    from grouped_ic_backtest import ASSETS
    print("Priming price cache (spaced requests) ...")
    st = prime(list(ASSETS.keys()))
    missing = [t for t, v in st.items() if v is None]
    print(f"\nCached {sum(1 for v in st.values() if v)}/{len(st)}. "
          f"Missing: {missing if missing else 'none'}")
