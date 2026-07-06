"""
data_loader.py
==============
Isolated data-fetching layer. The ONLY module that knows the source is yfinance.

Public API:
    load_ohlcv(ticker, ...) -> pd.DataFrame | None

Returns a normalized OHLCV DataFrame:
    - index : pandas DatetimeIndex (sorted, unique, tz-naive)
    - columns: open, high, low, close, volume  (all float64)
    - or None if the fetch ultimately failed (caller should skip + log)

Downstream code must NOT import yfinance or reference any yfinance concept.
If the source ever changes, only this file changes.
"""
from __future__ import annotations

import time
import warnings

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except Exception as exc:  # pragma: no cover - hard dependency
    raise ImportError(
        "yfinance is required for data_loader. Install with `pip install yfinance`."
    ) from exc


_REQUIRED = ["open", "high", "low", "close", "volume"]


def _normalize(raw: pd.DataFrame, ticker: str) -> pd.DataFrame | None:
    """Coerce a raw yfinance frame into the normalized OHLCV contract."""
    if raw is None or len(raw) == 0:
        return None

    df = raw.copy()

    # yfinance may return a MultiIndex on columns (field, ticker) even for a
    # single symbol. Collapse to the field level.
    if isinstance(df.columns, pd.MultiIndex):
        # Prefer the level that contains the OHLC field names.
        lvl0 = set(str(c).lower() for c in df.columns.get_level_values(0))
        if {"open", "high", "low", "close"} & lvl0:
            df.columns = df.columns.get_level_values(0)
        else:
            df.columns = df.columns.get_level_values(-1)

    # Case-insensitive column mapping.
    colmap = {}
    for c in df.columns:
        lc = str(c).strip().lower()
        if lc in ("open", "high", "low", "close", "volume"):
            colmap[c] = lc
        elif lc == "adj close":
            colmap[c] = "adj_close"
    df = df.rename(columns=colmap)

    missing = [c for c in ("open", "high", "low", "close") if c not in df.columns]
    if missing:
        return None

    if "volume" not in df.columns:
        # Some series (FX, yields) legitimately have no volume.
        df["volume"] = 0.0

    df = df[[c for c in _REQUIRED if c in df.columns]].copy()

    # Types + index hygiene.
    df.index = pd.to_datetime(df.index)
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_localize(None)
    df = df[~df.index.duplicated(keep="last")].sort_index()

    for c in _REQUIRED:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")

    # Drop rows with no usable price. Do NOT fill — missing stays missing.
    df = df.dropna(subset=["open", "high", "low", "close"])

    # Guard against non-positive prices that would break log-returns / TA-Lib.
    price_cols = ["open", "high", "low", "close"]
    bad = (df[price_cols] <= 0).any(axis=1)
    if bad.any():
        df = df[~bad]

    if len(df) == 0:
        return None
    return df


def load_ohlcv(
    ticker: str,
    period: str = "max",
    interval: str = "1d",
    retries: int = 3,
    backoff: float = 2.0,
) -> pd.DataFrame | None:
    """
    Fetch max available daily history for `ticker` and return normalized OHLCV.

    Retries with exponential backoff on empty/error responses. Returns None
    (never raises) so a single bad ticker cannot crash a batch run.
    """
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                raw = yf.download(
                    ticker,
                    period=period,
                    interval=interval,
                    auto_adjust=True,   # split/div-adjusted close for clean TA
                    actions=False,
                    progress=False,
                    threads=False,
                )
            norm = _normalize(raw, ticker)
            if norm is not None and len(norm) > 0:
                return norm
            last_err = "empty frame"
        except Exception as exc:  # network / rate-limit / parse
            last_err = repr(exc)

        if attempt < retries:
            time.sleep(backoff * attempt)

    print(f"    [data_loader] FAILED {ticker} after {retries} tries: {last_err}")
    return None


def describe(df: pd.DataFrame | None) -> dict:
    """Small coverage summary used by the pre-flight table."""
    if df is None or len(df) == 0:
        return {"rows": 0, "start": None, "end": None}
    return {
        "rows": int(len(df)),
        "start": df.index[0].date().isoformat(),
        "end": df.index[-1].date().isoformat(),
    }
