"""
walkforward.py
==============
v2 · F1 — walk-forward re-selection harness.

Re-selects each asset's indicator set at a sequence of annual as-of cutoffs
(expanding window) and backtests the SAME long-only strategy (monthly,
smooth=0.5, signal-gated exits) while switching each asset, at every date, to
the set that was selectable strictly before the rebalance that date's decision
feeds. This produces the honest RE-SELECTED baseline that replaces the single
frozen-cutoff OOS number, alongside two robustness diagnostics:

  * overfit gap  = IS(full) - walk-forward, compared to the frozen IS-OOS gap;
  * set stability = how many of the 4 slots change indicator between cutoffs
    (churn => the IC screen is fitting noise => fragile edge).

Only three epochs (2024 / 2025 / 2026, 2026 partial): this is a directional
proof-of-method robustness check, NOT a statistically rich validation. Read the
caveat block in the emitted report before trusting any number.

Run:
    python walkforward.py             # full 14-asset annual walk-forward
    python walkforward.py --smoke     # ^GSPC only (fast wiring check)
    python walkforward.py --quarterly # quarter-end cutoffs (more epochs, slow)
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from pandasta_data import TRADABLE
from pandasta_set_search import run_walkforward_selection
from portfolio_backtest import (BACKTEST_START, RESULTS, WF_CUTOFFS,
                                build_signals, build_walkforward_signals,
                                equal_weight_buyhold, load_tradable_returns,
                                metrics_table, run_backtest)

SLOT_COLS = ["volume_ind", "trend_ind", "momentum_ind", "volatility_ind"]


def quarterly_cutoffs() -> list[str]:
    """Quarter-end cutoffs spanning the annual schedule (diagnostic cadence)."""
    qs = pd.date_range(WF_CUTOFFS[0], WF_CUTOFFS[-1], freq="QE")
    return [d.strftime("%Y-%m-%d") for d in qs]


def _backtest(sig: pd.DataFrame, rets: pd.DataFrame) -> dict:
    """Canonical strategy params (the ones frozen in the README/SUMMARY)."""
    return run_backtest(rets[sig.columns], sig, smooth=0.5,
                        exit_only_negative=True)


def set_stability(best_winners: pd.DataFrame, cutoffs: list[str]) -> pd.DataFrame:
    """Per asset, the number of the 4 slots whose chosen indicator changed
    between each pair of consecutive cutoffs, plus the average."""
    rows = []
    for tkr, g in best_winners.groupby("asset"):
        g = g.drop_duplicates("cutoff").set_index("cutoff")
        seq = [c for c in cutoffs if c in g.index]
        changed = []
        for a, b in zip(seq, seq[1:]):
            va = g.loc[a, SLOT_COLS].fillna("").to_numpy()
            vb = g.loc[b, SLOT_COLS].fillna("").to_numpy()
            changed.append(int((va != vb).sum()))
        rows.append({"asset": tkr,
                     "changes_between_cutoffs": changed,
                     "avg_slots_changed": (float(np.mean(changed))
                                           if changed else float("nan"))})
    return pd.DataFrame(rows).sort_values("avg_slots_changed",
                                          ascending=False, na_position="last")


def _report(cutoffs: list[str], variants: dict[str, dict],
            bh: tuple[pd.Series, pd.Series], stability: pd.DataFrame,
            best_winners: pd.DataFrame, n_assets: int) -> list[str]:
    wf_full = metrics_table(variants["Walk-forward"]["daily"],
                            variants["Walk-forward"]["equity"]).loc["FULL"]
    is_full = metrics_table(variants["In-sample (IS)"]["daily"],
                            variants["In-sample (IS)"]["equity"]).loc["FULL"]
    oos_full = metrics_table(variants["Frozen OOS"]["daily"],
                             variants["Frozen OOS"]["equity"]).loc["FULL"]
    gap_wf = (is_full["return"] - wf_full["return"]) * 100
    gap_frozen = (is_full["return"] - oos_full["return"]) * 100

    lines = [
        "# Walk-forward re-selection backtest (v2 · F1)", "",
        "> **Honest re-selected baseline.** Indicator sets are re-chosen at each "
        f"cutoff on an EXPANDING window ({', '.join(cutoffs)}); the set picked at "
        "each cutoff governs the following period's monthly rebalances. Same "
        "strategy as the canonical backtest (long-only, top-8 by signal, "
        "inverse-vol x rank tilt, smooth=0.5, signal-gated exits, 5 bps/side, "
        "rf=0). Assets with signals: "
        f"{n_assets}/{len(TRADABLE)}.", "",
        "> **Caveat — read first.** Only "
        f"{len(cutoffs)} epochs (2026 partial). This is a directional "
        "proof-of-method and robustness check, NOT a statistically rich "
        "validation: too few out-of-sample re-selections to size confidence "
        "intervals. Treat the walk-forward numbers as a sanity floor on the "
        "frozen-cutoff result, not a precise forecast.", "",
        "## Full-period metrics — walk-forward vs frozen OOS vs IS vs benchmark",
        "",
    ]
    summary = pd.DataFrame({
        "Walk-forward": wf_full,
        "Frozen OOS": oos_full,
        "In-sample (IS)": is_full,
        "EW buy&hold": metrics_table(bh[0], bh[1]).loc["FULL"],
    }).T[["return", "ann_vol", "sharpe", "max_dd"]]
    lines += [summary.round(4).to_markdown(), "",
              "## Walk-forward, year by year", "",
              metrics_table(variants["Walk-forward"]["daily"],
                            variants["Walk-forward"]["equity"]).round(4).to_markdown(),
              "",
              "## Overfitting gap (the robustness headline)", "",
              f"- Frozen IS - OOS gap: **{gap_frozen:+.1f} pp** "
              "(the single-cutoff overfit cost quoted in SUMMARY.md).",
              f"- IS - **walk-forward** gap: **{gap_wf:+.1f} pp**.",
              "- If the walk-forward gap is materially narrower than the frozen "
              "gap, re-selection recovered part of the overfit; if the "
              "walk-forward FULL return collapses toward zero, the edge was "
              "largely the lucky cutoff.", "",
              "## Set stability across cutoffs", "",
              "Slots (of 4) whose chosen indicator changed between consecutive "
              "cutoffs. High churn ⇒ the IC screen is re-picking on noise.", "",
              stability.to_markdown(index=False), "",
              "## Selected set per epoch", ""]
    for cutoff in cutoffs:
        g = best_winners[best_winners["cutoff"] == cutoff].sort_values("asset")
        if g.empty:
            continue
        lines.append(f"### cutoff {cutoff}")
        lines.append("")
        lines.append("| asset | volume | trend | momentum | volatility |")
        lines.append("|---|---|---|---|---|")
        for _, r in g.iterrows():
            lines.append(f"| {r['asset']} | {r['volume_ind'] or '-'} | "
                         f"{r['trend_ind'] or '-'} | {r['momentum_ind'] or '-'} | "
                         f"{r['volatility_ind'] or '-'} |")
        lines.append("")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description="walk-forward re-selection harness")
    ap.add_argument("--smoke", action="store_true",
                    help="^GSPC only (fast wiring check)")
    ap.add_argument("--quarterly", action="store_true",
                    help="quarter-end cutoffs (more epochs, much slower)")
    args = ap.parse_args()

    cutoffs = quarterly_cutoffs() if args.quarterly else list(WF_CUTOFFS)
    tickers = ["^GSPC"] if args.smoke else None

    run_walkforward_selection(cutoffs, tickers)
    best = pd.read_csv(os.path.join(RESULTS, "pandasta_best_sets.csv"))
    winners = best[best["is_winner"] & best["cutoff"].isin(cutoffs)]

    rets = load_tradable_returns()
    wf_sig = build_walkforward_signals(cutoffs)
    if args.smoke:
        wf_sig = wf_sig[[c for c in wf_sig.columns if c == "^GSPC"]]
    variants = {
        "Walk-forward": _backtest(wf_sig, rets),
        "Frozen OOS": _backtest(build_signals("2023-12-31")[wf_sig.columns], rets),
        "In-sample (IS)": _backtest(build_signals("FULL")[wf_sig.columns], rets),
    }
    bh = equal_weight_buyhold(rets)

    stability = set_stability(winners, cutoffs)
    lines = _report(cutoffs, variants, bh, stability, winners, wf_sig.shape[1])

    curves = pd.DataFrame({
        "walk_forward": variants["Walk-forward"]["equity"],
        "frozen_oos": variants["Frozen OOS"]["equity"],
        "in_sample": variants["In-sample (IS)"]["equity"],
        "ew_buyhold": bh[1],
    })
    suffix = "_quarterly" if args.quarterly else ""
    curves.to_csv(os.path.join(RESULTS,
                               f"portfolio_equity_curves_walkforward{suffix}.csv"))
    report = f"portfolio_backtest_walkforward{suffix}.md"
    with open(os.path.join(RESULTS, report), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    wf_m = metrics_table(variants["Walk-forward"]["daily"],
                         variants["Walk-forward"]["equity"])
    print(f"\n=== walk-forward ===\n{wf_m.round(4)}")
    print(f"\nreport: results/{report}")


if __name__ == "__main__":
    main()
