"""
ta_advisor.py
=============
Single agent-facing entry point for the TA indicator-set pipeline.

Give THIS file's invocation to an AI agent (OpenClaw tool/command). It answers,
for a given as-of date:
  1. per-asset technical analysis (composite signal from that asset's frozen
     optimal indicator set, member-by-member contributions),
  2. which assets to HOLD and why (rank, sign, cash rule),
  3. target portfolio weightings including the cash position.

It lives in final-backtest/ and bootstraps the canonical pipeline modules from
the parent ta-flat-backtest folder (stats.py, pandasta_*, portfolio_backtest,
price_cache/, results/pandasta_best_sets.csv). It performs NO re-selection:
sets stay frozen exactly as backtested. Runnable from any working directory.

Usage:
    python ta_advisor.py                     # latest cached data, OOS sets
    python ta_advisor.py --date 2026-06-30   # as-of a past date
    python ta_advisor.py --window FULL       # in-sample sets (upper bound)
    python ta_advisor.py --json out.json     # machine-readable output
    python ta_advisor.py --refresh           # update price cache first (Yahoo)

Honesty notes baked into the output: fallback slots (no FDR survivor) are
flagged per asset; the composite ICs are small; this is the same signal logic
that produced the 2024-2026 OOS backtest (+58.5%, Sharpe 1.72) — see
results/SUMMARY.md before trusting any recommendation.

The weights reported here are the TARGET weights. The backtested strategy
applies partial adjustment: each monthly rebalance trades only halfway from
the current book toward these targets (lambda = 0.5), and a holding is sold
fully to zero only when its own composite signal is non-positive.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Bootstrap: the canonical pipeline lives in the parent (ta-flat-backtest).
# Inserting the parent at position 0 makes those modules win over any stale
# copies sitting next to this file, regardless of the agent's working dir.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from pandasta_data import TRADABLE, UNIVERSE, load_asset, master_calendar
from pandasta_set_search import (STRATEGY_H, _stage1_sign, causal_zscore,
                                 indicator_series_cache)
from portfolio_backtest import (RESULTS, TOP_N, VOL_WINDOW, build_signals,
                                load_tradable_returns, target_weights)

STALE_DAYS = 7


def _member_detail(tkr: str, names: list[str], s1_asset: pd.DataFrame,
                   asof: pd.Timestamp) -> list[dict]:
    """Latest sign-aligned z-score per set member for one asset."""
    _df, values = indicator_series_cache(tkr, None)
    out = []
    for n in names:
        if n not in values:
            out.append({"indicator": n, "note": "not computable on current data"})
            continue
        sign = _stage1_sign(s1_asset, n)
        z = causal_zscore(values[n][1]) * sign
        z_asof = z.loc[:asof].dropna()
        out.append({
            "indicator": n,
            "slot": values[n][0],
            "aligned_z": round(float(z_asof.iloc[-1]), 3) if len(z_asof) else None,
            "sign": int(sign),
        })
    return out


def refresh_cache(tickers) -> None:
    """Update price_cache CSVs via Ticker.history (yf.download is unreliable
    in this environment — see memory/env notes)."""
    import os
    import re
    import time

    import yfinance as yf

    import price_cache as pc
    for tkr in tickers:
        try:
            h = yf.Ticker(tkr).history(period="max", auto_adjust=True)
            if h is None or len(h) == 0:
                print(f"  refresh {tkr}: EMPTY — kept existing cache", file=sys.stderr)
                continue
            df = h.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
            df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
            df.index.name = "Date"
            safe = re.sub(r"[^A-Za-z0-9]+", "_", tkr)
            df.dropna(how="all").sort_index().to_csv(
                os.path.join(pc.CACHE_DIR, f"{safe}.csv"))
            print(f"  refresh {tkr}: {len(df)} rows through {df.index.max().date()}",
                  file=sys.stderr)
        except Exception as e:  # noqa: BLE001 — a failed refresh keeps old cache
            print(f"  refresh {tkr} FAILED ({type(e).__name__}) — kept cache",
                  file=sys.stderr)
        time.sleep(2)


def advise(window: str = "2023-12-31", date: str | None = None) -> dict:
    best = pd.read_csv(f"{RESULTS}/pandasta_best_sets.csv")
    stage1 = pd.read_csv(f"{RESULTS}/pandasta_stage1_ic.csv")
    winners = best[(best["is_winner"]) & (best["cutoff"] == window)]

    sig = build_signals(window)
    rets = load_tradable_returns()
    vols = rets.rolling(VOL_WINDOW).std() * np.sqrt(252)

    cal = master_calendar()
    asof = cal[cal <= pd.Timestamp(date)][-1] if date else sig.dropna(how="all").index[-1]
    last_data = rets.dropna(how="all").index[-1]
    stale = (pd.Timestamp.now().normalize() - last_data).days > STALE_DAYS

    sig_row = sig.loc[asof]
    vol_row = vols.loc[asof]
    weights = target_weights(sig_row, vol_row)
    ranks = sig_row.rank(ascending=False)

    assets = []
    for tkr in sorted(sig.columns, key=lambda t: -sig_row.get(t, -np.inf)):
        w = winners[winners["asset"] == tkr]
        if w.empty:
            continue
        w = w.iloc[0]
        names = [w[c] for c in ("volume_ind", "trend_ind", "momentum_ind",
                                "volatility_ind") if isinstance(w[c], str) and w[c]]
        s1 = stage1[(stage1["asset"] == tkr) & (stage1["cutoff"] == window)]
        s = float(sig_row[tkr]) if pd.notna(sig_row[tkr]) else None
        rk = int(ranks[tkr]) if pd.notna(ranks.get(tkr, np.nan)) else None
        held = bool(weights[tkr] > 0)
        if s is None:
            why = "no signal (insufficient data as of this date)"
        elif rk is not None and rk > TOP_N:
            why = f"rank {rk} of {len(sig.columns)} — outside the top {TOP_N}"
        elif s <= 0:
            why = (f"rank {rk} but composite signal is non-positive ({s:+.2f}) "
                   f"— cash rule replaces it with cash")
        else:
            why = (f"rank {rk} of {len(sig.columns)} with positive composite "
                   f"signal ({s:+.2f}) — held")
        fb = w.get("fdr_fallback_slots", "")
        assets.append({
            "asset": tkr,
            "name": UNIVERSE[tkr]["name"],
            "class": UNIVERSE[tkr]["class"],
            "composite_signal": None if s is None else round(s, 3),
            "rank": rk,
            "held": held,
            "weight": round(float(weights[tkr]), 4),
            "why": why,
            "set": names,
            "fdr_fallback_slots": fb if isinstance(fb, str) else "",
            "selection_comp_ic_h20": round(float(w["comp_ic"]), 4),
            "members": _member_detail(tkr, names, s1, asof),
            "vol_63d_ann": round(float(vol_row[tkr]), 4) if pd.notna(vol_row[tkr]) else None,
        })

    return {
        "as_of": str(asof.date()),
        "last_data_date": str(last_data.date()),
        "data_stale_warning": stale,
        "selection_window": window,
        "strategy": (f"long-only; top {TOP_N} by composite signal; only "
                     "positive-signal assets held; inverse-vol x rank-tilt "
                     "weights; remainder in cash at 0%. Weights below are "
                     "TARGETS: trade halfway toward them (lambda=0.5) and "
                     "sell a holding to zero only if its signal is "
                     "non-positive"),
        "cash_weight": round(float(1 - weights.sum()), 4),
        "holdings": {a["asset"]: a["weight"] for a in assets if a["held"]},
        "assets": assets,
        "disclosures": [
            f"Sets frozen on the {window} selection window; no re-selection.",
            "Composite ICs are small (0.02-0.13); this sized 1.72 OOS Sharpe "
            "2024-2026 but trailed equal-weight buy&hold on raw return.",
            "fdr_fallback_slots lists slots whose indicator did NOT survive "
            "the false-discovery gate (weaker evidence).",
            "Not investment advice; simulation logic, index proxies, rf=0.",
        ],
    }


def _print_human(r: dict) -> None:
    print(f"TA ADVISOR — as of {r['as_of']} (data through {r['last_data_date']}"
          f"{', STALE — consider --refresh' if r['data_stale_warning'] else ''})")
    print(f"Selection window: {r['selection_window']} | {r['strategy']}\n")
    print(f"{'asset':<9} {'class':<11} {'signal':>7} {'rank':>4} "
          f"{'weight':>7}  decision")
    for a in r["assets"]:
        sig = "  n/a" if a["composite_signal"] is None else f"{a['composite_signal']:+.2f}"
        print(f"{a['asset']:<9} {a['class']:<11} {sig:>7} "
              f"{a['rank'] if a['rank'] else '-':>4} {a['weight']*100:>6.1f}%  "
              f"{'HOLD' if a['held'] else 'skip'} — {a['why']}")
    print(f"{'CASH':<9} {'':<11} {'':>7} {'':>4} {r['cash_weight']*100:>6.1f}%")
    print("\nPer-asset detail (set members, sign-aligned z as of date):")
    for a in r["assets"]:
        fb = f" | fallback: {a['fdr_fallback_slots']}" if a["fdr_fallback_slots"] else ""
        print(f"  {a['asset']} ({a['name']}) comp_ic(sel)={a['selection_comp_ic_h20']:+.3f}{fb}")
        for m in a["members"]:
            if "note" in m:
                print(f"      {m['indicator']}: {m['note']}")
            else:
                print(f"      {m['slot']:<10} {m['indicator']:<14} z={m['aligned_z']:+.2f}"
                      if m["aligned_z"] is not None else
                      f"      {m['slot']:<10} {m['indicator']:<14} z=n/a")
    print("\nDisclosures:")
    for d in r["disclosures"]:
        print(f"  - {d}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument("--window", choices=["OOS", "FULL"], default="OOS",
                    help="OOS = sets frozen on <=2023 data (default); FULL = in-sample")
    ap.add_argument("--date", default=None, help="as-of date YYYY-MM-DD (default: latest)")
    ap.add_argument("--json", default=None, help="also write JSON to this path")
    ap.add_argument("--refresh", action="store_true", help="update price cache first")
    args = ap.parse_args()
    if args.refresh:
        refresh_cache(TRADABLE)
    window = "2023-12-31" if args.window == "OOS" else "FULL"
    r = advise(window, args.date)
    _print_human(r)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=1)
        print(f"\nJSON written to {args.json}")


if __name__ == "__main__":
    main()
