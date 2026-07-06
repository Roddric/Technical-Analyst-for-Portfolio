"""
macro_loader.py
===============
Isolated FRED / ALFRED data layer for the regime engine (phase1_segment.py).
The ONLY module that knows the macro source is FRED. Mirrors data_loader.py's role
for market data: downstream code consumes plain pandas objects and does not care
where they came from.

Provides the six macro inputs phase1_segment.segment_history expects:
    vix           : pd.Series  (daily VIX level)                      <- VIXCLS
    hy_spread     : pd.Series  (daily HY OAS, %)                      <- BAMLH0A0HYM2
    dgs2, dgs10   : pd.Series  (daily 2Y / 10Y Treasury yield, %)     <- DGS2 / DGS10
    macro_vintage : pd.DataFrame indexed by RELEASE date, columns:
                    gdp_qoq, cpi_yoy, unemployment, ism_mfg, ism_svcs,
                    fed_stance, vintage_flag  (first-print / point-in-time)

Vintage discipline (the look-ahead guard):
- Axis3 macro (GDP/CPI/UNRATE) uses ALFRED FIRST-PRINT values indexed by their real
  release date (realtime_start), so nothing is known before it was actually published.
- ALFRED's vintage archive begins 1991-12-04; observation periods before that clamp
  to the earliest archived vintage. So point-in-time Axis3 is faithful from ~1992;
  1990-1991 Axis3 is approximate (flagged by the caller via macro coverage start).
- ISM PMI is not redistributable on FRED (licensing) -> emitted as NaN; Axis3 scoring
  handles missing ISM and leans on GDP+CPI (weight 2 each) + fed_stance.
- HY OAS on FRED only starts 2023-07-03 (ICE licensing); earlier dates are NaN, which
  Axis4 tolerates (shock detection is VIX-Z primary, HY is an OR-gated confirmation).

All raw pulls are cached to ./macro_cache/*.csv so re-runs are fast and offline-safe.
"""

from __future__ import annotations

import os
import time

import numpy as np
import pandas as pd

try:
    from fredapi import Fred
except Exception as exc:  # pragma: no cover
    raise ImportError("fredapi required: pip install fredapi") from exc

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "macro_cache")
KEY_FILE = os.path.join(HERE, "fred_key.txt")

ALFRED_ARCHIVE_START = pd.Timestamp("1991-12-04")   # earliest vintage FRED archives


def _api_key() -> str:
    if os.environ.get("FRED_API_KEY"):
        return os.environ["FRED_API_KEY"].strip()
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE).read().strip()
    raise RuntimeError("No FRED API key: set FRED_API_KEY or create fred_key.txt")


def _fred() -> Fred:
    return Fred(api_key=_api_key())


# --------------------------------------------------------------------------- #
# cached raw pulls
# --------------------------------------------------------------------------- #
def _cache_path(name: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{name}.csv")


def _cached_series(fred, series_id: str, start: str, force: bool = False) -> pd.Series:
    """get_series with on-disk cache and simple retry."""
    path = _cache_path(f"series_{series_id}")
    if os.path.exists(path) and not force:
        s = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
        s.name = series_id
        return s
    last = None
    for attempt in range(3):
        try:
            s = fred.get_series(series_id, observation_start=start)
            s = s.dropna()
            s.name = series_id
            s.to_frame(series_id).to_csv(path)
            return s
        except Exception as exc:
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"FRED get_series({series_id}) failed: {last!r}")


def _cached_all_releases(fred, series_id: str, force: bool = False) -> pd.DataFrame:
    """get_series_all_releases (vintage-aware) with on-disk cache."""
    path = _cache_path(f"allrel_{series_id}")
    if os.path.exists(path) and not force:
        df = pd.read_csv(path, parse_dates=["realtime_start", "date"])
        return df
    last = None
    for attempt in range(3):
        try:
            df = fred.get_series_all_releases(series_id)
            df = df.dropna(subset=["value"])
            df.to_csv(path, index=False)
            return df
        except Exception as exc:
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"FRED get_series_all_releases({series_id}) failed: {last!r}")


# --------------------------------------------------------------------------- #
# first-print (point-in-time) helper
# --------------------------------------------------------------------------- #
def _first_prints(fred, series_id: str, force: bool = False) -> pd.DataFrame:
    """
    Return each observation's FIRST published value with its real release date.
    Columns: period (obs date), release (realtime_start), value.
    The earliest realtime_start per observation period is the first print.
    """
    ar = _cached_all_releases(fred, series_id, force=force)
    ar = ar.sort_values("realtime_start")
    fp = ar.groupby("date", as_index=False).first()
    fp = fp.rename(columns={"date": "period", "realtime_start": "release"})
    fp["period"] = pd.to_datetime(fp["period"])
    fp["release"] = pd.to_datetime(fp["release"])
    fp["value"] = pd.to_numeric(fp["value"], errors="coerce")
    return fp.dropna(subset=["value"]).sort_values("release").reset_index(drop=True)


# --------------------------------------------------------------------------- #
# public: market-ish daily macro series
# --------------------------------------------------------------------------- #
def load_vix(start: str = "1990-01-01", force: bool = False) -> pd.Series:
    return _cached_series(_fred(), "VIXCLS", start, force).astype(float)


def load_hy_spread(start: str = "1990-01-01", force: bool = False) -> pd.Series:
    """HY OAS (%). Only 2023-07+ on FRED (ICE licensing); returned as-is."""
    return _cached_series(_fred(), "BAMLH0A0HYM2", start, force).astype(float)


def load_yields(start: str = "1990-01-01", force: bool = False) -> tuple[pd.Series, pd.Series]:
    f = _fred()
    dgs2 = _cached_series(f, "DGS2", start, force).astype(float)
    dgs10 = _cached_series(f, "DGS10", start, force).astype(float)
    return dgs2, dgs10


# --------------------------------------------------------------------------- #
# public: vintage Axis3 macro table (release-date indexed)
# --------------------------------------------------------------------------- #
def _fed_stance_from_funds(fred, start: str, force: bool) -> pd.DataFrame:
    """Derive a coarse fed_stance from the effective fed funds rate (FEDFUNDS).
    Not revised, so release-timed as observation month + ~1 month."""
    ff = _cached_series(fred, "FEDFUNDS", "1988-01-01", force).astype(float)
    chg3 = ff.diff(3)                       # 3-month change in policy rate
    stance = pd.Series("Neutral", index=ff.index, dtype=object)
    stance[chg3 > 0.75] = "HikingAggressive"
    stance[(chg3 > 0.10) & (chg3 <= 0.75)] = "Hiking"
    stance[chg3 < -0.10] = "Cutting"
    rel = ff.index + pd.DateOffset(days=30)  # published early next month
    out = pd.DataFrame({"release": rel, "fed_stance": stance.values})
    return out


def load_macro_vintage(start: str = "1990-01-01", force: bool = False) -> pd.DataFrame:
    """
    Build the point-in-time macro_vintage table phase1_segment expects, indexed by
    RELEASE date. gdp_qoq / cpi_yoy / unemployment are ALFRED first-prints; ism_* are
    NaN (unavailable on FRED); fed_stance from FEDFUNDS; vintage_flag=True.
    """
    f = _fred()

    def _by_release(fp: pd.DataFrame, col: str) -> pd.DataFrame:
        """One row per release date. When several observation periods share a
        release date (pre-1992 vintages all clamp to the ALFRED archive start),
        keep the LATEST period's value — that is what is 'known' on that date."""
        fp = fp.sort_values("period").drop_duplicates("release", keep="last")
        return fp.set_index("release")[[col]].sort_index()

    # GDP QoQ SAAR %  from first-print REAL GDP levels (GDPC1). The pre-computed
    # %-change series (A191RL1Q225SBEA) is only vintage-archived from 2014, so we
    # derive QoQ annualized from first-print levels, which archive back to ~1991.
    gdp_fp = _first_prints(f, "GDPC1", force).sort_values("period")
    gdp_fp["gdp_qoq"] = (np.power(gdp_fp["value"] / gdp_fp["value"].shift(1), 4) - 1.0) * 100.0
    gdp = _by_release(gdp_fp.dropna(subset=["gdp_qoq"]), "gdp_qoq")

    # CPI YoY from first-print CPI levels (period-aligned pct_change(12))
    cpi_fp = _first_prints(f, "CPIAUCSL", force).sort_values("period")
    cpi_fp["cpi_yoy"] = cpi_fp["value"].pct_change(12) * 100.0
    cpi = _by_release(cpi_fp.dropna(subset=["cpi_yoy"]), "cpi_yoy")

    # Unemployment rate first-print
    un = _first_prints(f, "UNRATE", force).rename(columns={"value": "unemployment"})
    un = _by_release(un, "unemployment")

    # Fed stance (release dates already unique/monthly)
    fed = _fed_stance_from_funds(f, start, force)
    fed = fed.drop_duplicates("release", keep="last").set_index("release")[["fed_stance"]].sort_index()

    # Merge everything onto the union of release dates
    macro = pd.concat([gdp, cpi, un, fed], axis=1, sort=True)

    # ISM not available on FRED (licensing) -> explicit NaN columns
    macro["ism_mfg"] = np.nan
    macro["ism_svcs"] = np.nan
    macro["vintage_flag"] = True

    macro.index = pd.to_datetime(macro.index)
    macro = macro[macro.index >= pd.Timestamp("1988-01-01")]
    # order columns as the engine reads them
    macro = macro[["gdp_qoq", "cpi_yoy", "unemployment", "ism_mfg", "ism_svcs",
                   "fed_stance", "vintage_flag"]]
    return macro


def coverage_report(start: str = "1990-01-01", force: bool = False) -> dict:
    """Fetch everything and summarize coverage (for the pre-flight)."""
    vix = load_vix(start, force)
    hy = load_hy_spread(start, force)
    dgs2, dgs10 = load_yields(start, force)
    macro = load_macro_vintage(start, force)
    def span(s):
        s = s.dropna()
        return (s.index.min(), s.index.max(), len(s))
    return {
        "VIXCLS": span(vix), "HY_OAS": span(hy),
        "DGS2": span(dgs2), "DGS10": span(dgs10),
        "macro_releases": (macro.index.min(), macro.index.max(), len(macro)),
        "gdp_first_release": macro["gdp_qoq"].dropna().index.min(),
        "cpi_first_release": macro["cpi_yoy"].dropna().index.min(),
        "alfred_archive_start": ALFRED_ARCHIVE_START,
    }


if __name__ == "__main__":
    print("macro_loader smoke test — fetching FRED/ALFRED (cached) ...")
    rep = coverage_report()
    for k, v in rep.items():
        print(f"  {k:<22} {v}")
    m = load_macro_vintage()
    print("\nmacro_vintage tail:")
    print(m.tail(6).to_string())
    print("\nfed_stance distribution:")
    print(m["fed_stance"].value_counts(dropna=False).to_string())
