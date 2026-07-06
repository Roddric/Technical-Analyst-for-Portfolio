"""
regime_labels.py
================
Produce a date-indexed REGIME label series by driving phase1_segment.py with real
macro data (FRED/ALFRED via macro_loader.py) and SPY OHLCV (yfinance via data_loader).

REGIME AXIS ONLY — no sector axis.
The architecture's cells are regime x sector, but this universe is indices / asset
classes (^GSPC, GC=F, ...), which are not sector-assignable (an index IS the market).
So we run phase1_segment's regime path (Fast Layer axes 1/2/4 + steepener, Slow Layer
axis 3, Priority Arbiter) and DELIBERATELY DO NOT call assign_sector(). This is logged
in the output. The sector axis remains untested until the regime backtest runs on
single stocks, its real design target.

Output: ./regime_labels.csv  (date -> regime_code + confidence/flags)
"""

from __future__ import annotations

import os
import pandas as pd

import data_loader
import macro_loader
import phase1_segment as p1

HERE = os.path.dirname(os.path.abspath(__file__))
START = "1990-01-01"
SPY_TICKER = "^GSPC"          # market proxy for Axis 1 (the engine calls it "SPY")
OUT_CSV = os.path.join(HERE, "regime_labels.csv")


def _align(series: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    """Reindex a daily macro series onto the trading calendar, forward-filling
    gaps (macro prints persist until the next release)."""
    return series.reindex(index).ffill()


def build_regime_labels(start: str = START, force_macro: bool = False) -> pd.DataFrame:
    # ---- market data (Axis 1 uses the broad index as "SPY") ----
    spy = data_loader.load_ohlcv(SPY_TICKER)
    spy = spy[spy.index >= pd.Timestamp(start)]
    idx = spy.index

    # ---- macro data (FRED / ALFRED) ----
    vix = _align(macro_loader.load_vix(start, force_macro), idx)
    hy = _align(macro_loader.load_hy_spread(start, force_macro), idx)
    dgs2, dgs10 = macro_loader.load_yields(start, force_macro)
    dgs2 = _align(dgs2, idx)
    dgs10 = _align(dgs10, idx)
    macro_vintage = macro_loader.load_macro_vintage(start, force_macro)

    print(f"  SPY({SPY_TICKER}) {idx.min().date()}..{idx.max().date()} n={len(idx)}")
    print(f"  VIX non-nan={int(vix.notna().sum())} | HY non-nan={int(hy.notna().sum())} "
          f"| DGS2 non-nan={int(dgs2.notna().sum())} | DGS10 non-nan={int(dgs10.notna().sum())}")
    print(f"  macro_vintage releases={len(macro_vintage)} "
          f"({macro_vintage.index.min().date()}..{macro_vintage.index.max().date()})")

    # ---- Fast Layer (reuse phase1_segment verbatim) ----
    print("  Fast Layer: Axis1 trend / Axis2 vol / Axis4 shock / steepener ...")
    trend_df = p1.compute_axis1_trend(spy["close"], spy["high"], spy["low"])
    vol_df = p1.compute_axis2_vol(vix)
    shock_df = p1.compute_axis4_shock(vix, hy, spy["close"])
    steepener_s = p1.compute_steepener_type(dgs2, dgs10, window=40)
    raw_spread_s = dgs10 - dgs2

    # ---- Slow Layer (Axis 3), aligned to trading calendar ----
    print("  Slow Layer: Axis3 economic cycle (vintage) ...")
    slow_df_raw = p1.compute_axis3_cycle(macro_vintage)
    slow_df = slow_df_raw.reindex(idx, method="ffill")

    # ---- Priority Arbiter per date (regime-only; NO assign_sector) ----
    print("  Priority Arbiter (regime-only; assign_sector DELIBERATELY SKIPPED) ...")
    records = []
    for date in idx:
        if date not in trend_df.index or date not in vol_df.index or date not in shock_df.index:
            continue
        t_row = trend_df.loc[date]
        v_row = vol_df.loc[date]
        s_row = shock_df.loc[date]

        fast = p1.FastLayerResult(
            axis1_trend=t_row["axis1"] if pd.notna(t_row.get("axis1")) else "Sideways",
            axis2_vol=v_row["axis2"] if pd.notna(v_row.get("axis2")) else "Mid",
            axis4_shock=s_row["axis4"] if pd.notna(s_row.get("axis4")) else "None",
            steepener_type=steepener_s.loc[date] if date in steepener_s.index else "Flat",
            fast_confidence=float(t_row.get("fast_trend_conf", 50)),
            vol_mode=v_row.get("vol_mode", "normal"),
            vix_zscore=float(v_row.get("vix_zscore", 0) or 0),
            vix_velocity=float(s_row.get("vix_velocity", 0) or 0),
            hy_spread_zscore=float(s_row.get("hy_spread_zscore", 0) or 0),
        )

        raw_spread_val = float(raw_spread_s.loc[date]) if date in raw_spread_s.index else float("nan")
        if date in slow_df.index and not slow_df.loc[date].isna().all():
            slow_row = slow_df.loc[date]
            steepener = fast.steepener_type
            cycle = slow_row["axis3"]
            st_contra = (
                (steepener == "BullSteepener" and cycle in ["Expansion", "Reflation"]) or
                (steepener == "BearSteepener" and cycle in ["Recession"])
            )
            if pd.notna(raw_spread_val) and raw_spread_val < -0.50:
                st_contra = True
            slow = p1.SlowLayerResult(
                axis3_cycle=slow_row["axis3"],
                slow_confidence=float(slow_row["slow_confidence"]),
                last_updated=date, data_vintage=True,
                ism_split_flag=bool(slow_row.get("ism_split_flag", False)),
                steepener_contradiction=st_contra,
                staleness_days=int(slow_row.get("staleness_days", 0)),
            )
        else:
            slow = p1.SlowLayerResult(
                axis3_cycle="Expansion", slow_confidence=50.0, last_updated=None,
                data_vintage=True, ism_split_flag=False,
                steepener_contradiction=False, staleness_days=999,
            )

        result = p1.priority_arbiter(date, fast, slow)
        records.append(vars(result))

    regime_df = pd.DataFrame(records).set_index("date").sort_index()
    keep = ["regime_code", "regime_label", "overall_confidence", "fast_confidence",
            "slow_confidence", "shock_flag", "shock_watch_flag", "transition_flag",
            "floor_triggered", "floor_reason", "axis1", "axis2", "axis3", "axis4",
            "steepener_type", "vix_zscore"]
    regime_df = regime_df[keep]
    return regime_df


def main():
    print("Building regime labels (regime axis ONLY; sector axis NOT USED) ...")
    regime_df = build_regime_labels()
    regime_df.to_csv(OUT_CSV)
    print(f"\n[write] {OUT_CSV}  ({len(regime_df)} rows)")

    print("\n=== HEAD ===")
    print(regime_df[["regime_code", "regime_label", "axis1", "axis2", "axis3", "axis4",
                     "overall_confidence"]].head().to_string())
    print("\n=== TAIL ===")
    print(regime_df[["regime_code", "regime_label", "axis1", "axis2", "axis3", "axis4",
                     "overall_confidence"]].tail().to_string())

    print("\n=== REGIME DISTRIBUTION (days per regime) ===")
    vc = regime_df["regime_code"].value_counts()
    labelmap = regime_df.drop_duplicates("regime_code").set_index("regime_code")["regime_label"]
    for rc, n in vc.items():
        thin = "  <-- THIN (<60d)" if n < 60 else ""
        print(f"  {rc}  {labelmap.get(rc,''):<26} {n:>6}{thin}")

    thin = vc[vc < 60]
    print(f"\nRegimes with <60 days (too thin to rank reliably): "
          f"{list(thin.index) if len(thin) else 'none'}")
    print(f"Shock-active days: {int(regime_df['shock_flag'].sum())} | "
          f"floor-triggered days: {int(regime_df['floor_triggered'].sum())} | "
          f"transition days: {int(regime_df['transition_flag'].sum())}")
    print("\nNOTE: assign_sector was DELIBERATELY NOT run — indices are not "
          "sector-assignable. Sector axis remains untested (single-stock target).")


if __name__ == "__main__":
    main()
