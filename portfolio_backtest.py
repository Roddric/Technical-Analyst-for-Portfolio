"""
portfolio_backtest.py
=====================
Long-only, monthly-rebalanced, turnover-smoothed portfolio built from the
per-asset composite technical signals selected by pandasta_set_search.

Ranking -> weights (first trading day each month, decision on prior day data):
  hold top N=8 by composite signal; negative-signal names sit in cash at 0%;
  weight ∝ (1/vol_63d) * tilt, tilt = 1 + 0.5 * scaled_rank in [0.5, 1.5];
  each rebalance moves only halfway (smooth=0.5) from current to target
  weights, and a holding may be liquidated fully only when its own signal is
  non-positive (exit_only_negative); 5 bps per side.

Variants: OOS (sets chosen on data <= 2023-12-31) vs FULL (in-sample upper
bound), reported side by side. Benchmark: equal-weight buy & hold.

Run:  python portfolio_backtest.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from pandasta_data import TRADABLE, load_asset, master_calendar
from pandasta_set_search import composite_signal, indicator_series_cache

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

TOP_N = 8
VOL_WINDOW = 63
COST_PER_SIDE = 0.0005
BACKTEST_START = "2024-01-01"
ANN = 252
DUST = 0.005          # post-smoothing weights below this are cut to zero


# ---------------------------------------------------------------- weights ----
def rank_tilt(n_held: int) -> np.ndarray:
    """Tilt for rank positions 0 (best) .. n-1 (worst): 1 + 0.5*scaled,
    scaled linearly from +1 (best) to -1 (worst). n=1 -> tilt 1."""
    if n_held == 1:
        return np.array([1.0])
    scaled = np.linspace(1.0, -1.0, n_held)
    return 1.0 + 0.5 * scaled


def target_weights(signals: pd.Series, vols: pd.Series, top_n: int = TOP_N) -> pd.Series:
    """Long-only weights over `signals.index`; top_n held by signal, then
    cash rule: only positive-signal members of that top-n are actually
    invested (weights sum to n_positive / min(top_n, n_valid) <= 1); the
    rest sits in cash (implicit — not part of the returned Series, whose
    sum is the invested/risky fraction)."""
    s = signals.dropna()
    if s.empty:
        raise ValueError("target_weights: no assets with valid signals")
    n_valid = len(s)
    n_held = min(top_n, n_valid)
    held = s.sort_values(ascending=False).index[:n_held]
    positive = [a for a in held if s[a] > 0]
    if not positive:
        return pd.Series(0.0, index=signals.index)
    v = vols.reindex(positive).astype("float64")
    v = v.where(v > 1e-8)                 # zero/NaN vol -> fallback below
    inv = 1.0 / v
    inv = inv.fillna(inv.mean() if np.isfinite(inv.mean()) else 1.0)
    tilt = pd.Series(rank_tilt(len(held)), index=held).reindex(positive)
    raw = inv * tilt
    w_pos = raw / raw.sum()
    invested_fraction = len(positive) / n_held
    w_pos = w_pos * invested_fraction
    return w_pos.reindex(signals.index).fillna(0.0)


# --------------------------------------------------------------- backtest ----
def run_backtest(daily_rets: pd.DataFrame, signals: pd.DataFrame,
                 start: str = BACKTEST_START,
                 cost_per_side: float = COST_PER_SIDE,
                 rebal_months: int = 1,
                 smooth: float = 1.0,
                 exit_only_negative: bool = False) -> dict:
    """Daily accounting with weight drift; rebalance on the first trading day
    of every `rebal_months`-th calendar month (1 = monthly, 3 = quarterly on
    Jan/Apr/Jul/Oct) using data through the PRIOR day; costs on turnover.

    `smooth` is the partial-adjustment speed: at each rebalance the book moves
    only `smooth` of the way from its current (drifted) weights toward the
    target, so entries/exits fade in and out instead of snapping (1.0 = jump
    fully to target, the classic behavior). The very first allocation from an
    empty book always goes fully to target. Blended weights under DUST are cut
    to zero (freed weight sits in cash) so exiting tails don't linger forever.

    `exit_only_negative`: a held asset may be sold all the way to zero ONLY
    when its composite signal is non-positive. A positive-signal holding that
    merely fell out of the top-N is trimmed toward zero but floored at DUST —
    it keeps a token position until its signal actually turns negative (or it
    re-enters the top-N). If floors push the gross above 1, weights are
    renormalized to stay fully-funded long-only."""
    cal = daily_rets.index
    vols = daily_rets.rolling(VOL_WINDOW).std() * np.sqrt(ANN)
    live = cal[cal >= pd.Timestamp(start)]
    months = pd.Series(live.month, index=live)
    is_first = months.ne(months.shift(1).fillna(-1))
    on_cycle = ((months - 1) % rebal_months) == 0
    rebal_days = set(live[(is_first & on_cycle).values])

    w = pd.Series(0.0, index=daily_rets.columns)
    daily_out, weights_rows, turnover_rows, cash_rows = [], [], [], []
    for d in live:
        if d in rebal_days:
            prior = cal[cal < d]
            if len(prior):
                p = prior[-1]
                tgt = target_weights(signals.loc[p], vols.loc[p])
                if smooth < 1.0 and w.abs().sum() > 0:   # partial adjustment
                    tgt = w + smooth * (tgt - w)
                    if exit_only_negative:
                        pos_held = (signals.loc[p].reindex(tgt.index) > 0) \
                            & (w > 0) & (tgt < DUST)
                        tgt[pos_held] = DUST             # no full exit while positive
                    tgt[tgt < DUST] = 0.0
                    if tgt.sum() > 1.0:                  # floors can overshoot
                        tgt = tgt / tgt.sum()
                dw = (tgt - w).abs().sum()
                cost = cost_per_side * dw
                w = tgt
                weights_rows.append(pd.Series(w, name=d))
                turnover_rows.append(pd.Series({"turnover": dw / 2.0}, name=d))
                cash_rows.append(pd.Series({"cash": 1.0 - float(w.sum())}, name=d))
            else:
                cost = 0.0
        else:
            cost = 0.0
        r = daily_rets.loc[d].fillna(0.0)
        rp_pre_cost = float((w * r).sum())
        rp = rp_pre_cost - cost
        daily_out.append(rp)
        # cash-aware drift: sleeve value w_i(1+r_i), portfolio grows by
        # (1+rp_pre_cost); new risky weights are the sleeve values rescaled
        # by the portfolio growth factor, so cash's share is the implicit
        # remainder (1 - new_w.sum()) rather than being renormalized away.
        denom = 1.0 + rp_pre_cost
        if denom > 0:
            w = w * (1.0 + r) / denom
        # else: pathological (portfolio value <= 0) — keep w unchanged
    daily = pd.Series(daily_out, index=live, name="daily_return")
    equity = (1.0 + daily).cumprod()
    return {"daily": daily, "equity": equity,
            "weights": pd.DataFrame(weights_rows),
            "turnover": pd.concat(turnover_rows, axis=1).T["turnover"]
            if turnover_rows else pd.Series(dtype=float),
            "cash": pd.concat(cash_rows, axis=1).T["cash"]
            if cash_rows else pd.Series(dtype=float)}


# ---------------------------------------------------------------- metrics ----
def _max_dd(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((equity / peak - 1.0).min())


def metrics_table(daily: pd.Series, equity: pd.Series) -> pd.DataFrame:
    rows = {}
    for label, sl in [("2024", "2024"), ("2025", "2025"), ("2026", "2026")]:
        try:
            d = daily.loc[sl]
        except KeyError:
            continue
        if d.empty:
            continue
        e = (1 + d).cumprod()
        rows[label] = {
            "return": float(e.iloc[-1] - 1.0),
            "ann_vol": float(d.std() * np.sqrt(ANN)),
            "sharpe": float((d.mean() * ANN) / (d.std() * np.sqrt(ANN)))
            if d.std() > 0 else np.nan,
            "max_dd": _max_dd(e),
        }
    d = daily
    rows["FULL"] = {
        "return": float(equity.iloc[-1] - 1.0),
        "ann_vol": float(d.std() * np.sqrt(ANN)),
        "sharpe": float((d.mean() * ANN) / (d.std() * np.sqrt(ANN)))
        if d.std() > 0 else np.nan,
        "max_dd": _max_dd(equity),
    }
    return pd.DataFrame(rows).T


# ------------------------------------------------------------------- main ----
def build_signals(cutoff_label: str) -> pd.DataFrame:
    """Composite signal per tradable asset from the winning sets CSV, on the
    master calendar (crypto ffilled). Assets with no winner are omitted
    (disclosed by caller)."""
    best = pd.read_csv(os.path.join(RESULTS, "pandasta_best_sets.csv"))
    winners = best[(best["is_winner"]) & (best["cutoff"] == cutoff_label)]
    cal = master_calendar()
    sig = {}
    for _, r in winners.iterrows():
        tkr = r["asset"]
        if tkr not in TRADABLE:
            continue
        # recompute members on FULL history (selection already frozen)
        _df, values = indicator_series_cache(tkr, None)
        names = [r[c] for c in ("volume_ind", "trend_ind", "momentum_ind",
                                "volatility_ind")
                 if isinstance(r[c], str) and r[c]]
        stage1 = pd.read_csv(os.path.join(RESULTS, "pandasta_stage1_ic.csv"))
        s1 = stage1[(stage1["asset"] == tkr) & (stage1["cutoff"] == cutoff_label)]
        from pandasta_set_search import _stage1_sign
        members, signs = [], []
        for n in names:
            if n not in values:
                continue
            members.append(values[n][1])
            signs.append(_stage1_sign(s1, n))
        if not members:
            continue
        comp = composite_signal(members, signs) * r["traded_sign"]
        sig[tkr] = comp.reindex(cal).ffill(limit=5)
    return pd.DataFrame(sig, index=cal)


def load_tradable_returns() -> pd.DataFrame:
    cal = master_calendar()
    rets = {}
    for tkr in TRADABLE:
        df = load_asset(tkr)
        if df is None:
            continue
        close = df["close"].reindex(cal.union(df.index)).ffill().reindex(cal)
        rets[tkr] = close.pct_change()
    return pd.DataFrame(rets, index=cal)


def equal_weight_buyhold(daily_rets: pd.DataFrame,
                         start: str = BACKTEST_START) -> tuple[pd.Series, pd.Series]:
    """Equal-weight, fully-invested buy&hold benchmark from `start`: seed equal
    weights over the assets that ever have a return in-window, then let them
    drift with daily returns (no rebalancing). Returns (daily, equity)."""
    live = daily_rets.index[daily_rets.index >= pd.Timestamp(start)]
    valid_cols = [c for c in daily_rets.columns
                  if daily_rets[c].loc[live].notna().any()]
    w = pd.Series(1.0 / len(valid_cols), index=valid_cols)
    out = []
    for d in live:
        r = daily_rets.loc[d, valid_cols].fillna(0.0)
        out.append(float((w * r).sum()))
        g = w * (1 + r)
        w = g / g.sum()
    daily = pd.Series(out, index=live)
    return daily, (1 + daily).cumprod()


# ---------------------------------------------------- walk-forward (v2 · F1) ---
# Annual re-selection cutoffs (expanding window). The set chosen at each cutoff
# governs the following year's monthly rebalances; see governing_cutoff.
WF_CUTOFFS = ["2023-12-31", "2024-12-31", "2025-12-31"]

# A month-end rebalance DECISION is made on the prior trading day (often the
# last trading day of the previous month, e.g. 2023-12-29 for the Jan-2024
# rebalance) and feeds a rebalance a few days later. So a decision may legally
# use a set whose cutoff is slightly AFTER the decision date but still strictly
# before the rebalance it feeds (2023-12-31 cutoff -> Jan-2024 rebalance). This
# short lead maps a decision date to the rebalance it feeds so the year-end set
# governs the next year's rebalances (including the trailing December decision).
SELECTION_LEAD = pd.Timedelta(days=7)


def governing_cutoff(date, cutoffs=WF_CUTOFFS, lead: pd.Timedelta = SELECTION_LEAD):
    """The selection cutoff whose indicator set governs a rebalance decision
    made on `date`: the latest cutoff strictly before the rebalance that
    decision feeds (approximated as `date + lead`). Returns None if no set is
    selectable yet. Guarantees a set is never applied to a rebalance that
    occurs on or before its own data cutoff (no look-ahead)."""
    horizon = pd.Timestamp(date) + lead
    prior = [c for c in sorted(cutoffs) if pd.Timestamp(c) < horizon]
    return prior[-1] if prior else None


def build_walkforward_signals(cutoffs: list[str] = WF_CUTOFFS) -> pd.DataFrame:
    """Time-varying composite signals: each date's row is drawn from the set
    selected at the cutoff that governs it (governing_cutoff). Reuses
    build_signals per cutoff and splices by date. Because 2024 rebalances are
    all governed by the 2023-12-31 epoch, the 2024 slice is bit-identical to the
    frozen OOS signal — the continuity guarantee the harness is checked against.
    Assets absent from a given epoch's winners are NaN for that epoch's dates."""
    cutoffs = sorted(cutoffs)
    frames = {c: build_signals(c) for c in cutoffs}
    cal = frames[cutoffs[0]].index
    cols = sorted(set().union(*(f.columns for f in frames.values())))
    gov = np.array([governing_cutoff(d, cutoffs) for d in cal], dtype=object)
    out = pd.DataFrame(np.nan, index=cal, columns=cols)
    for c in cutoffs:
        mask = gov == c
        if mask.any():
            out.loc[mask, :] = frames[c].reindex(columns=cols).to_numpy()[mask]
    return out


def _monthly_holdings_lines(tag: str, weights: pd.DataFrame,
                            cash: pd.Series, freq_word: str = "Monthly") -> list[str]:
    """MD lines for the per-rebalance holdings table: one row per rebalance
    date, held assets sorted by weight desc, plus 'CASH x%' when the cash
    share exceeds 0.5%."""
    lines = [f"### {freq_word} holdings — {tag}", "",
             "| date | holdings |", "|---|---|"]
    for d in weights.index:
        row = weights.loc[d]
        held = row[row > 1e-6].sort_values(ascending=False)
        parts = [f"{t} {v * 100:.1f}%" for t, v in held.items()]
        c = float(cash.loc[d]) if d in cash.index else 0.0
        if c > 0.005:
            parts.append(f"CASH {c * 100:.1f}%")
        lines.append(f"| {d.date()} | {', '.join(parts)} |")
    lines.append("")
    return lines


def main(rebal_months: int = 1, smooth: float = 0.5,
         exit_only_negative: bool = True) -> None:
    """Defaults ARE the strategy: monthly, half-way smoothing, signal-gated
    exits. Non-default parameter combinations write suffixed files so the
    canonical results are never silently overwritten."""
    os.makedirs(RESULTS, exist_ok=True)
    freq_word = {1: "Monthly", 3: "Quarterly"}.get(rebal_months,
                                                   f"Every-{rebal_months}-month")
    suffix = ("" if rebal_months == 1 else f"_{rebal_months}m") + \
             ("_nosmooth" if smooth >= 1.0 else
              "" if round(smooth * 100) == 50 else f"_s{round(smooth * 100)}") + \
             ("" if exit_only_negative else "_anyexit")
    smooth_txt = ("" if smooth >= 1.0 else
                  f" Turnover-smoothed: each rebalance moves only "
                  f"{smooth:.0%} of the way from current to target weights "
                  f"(entries/exits fade over several rebalances; blended "
                  f"weights < {DUST:.1%} cut to cash).")
    if exit_only_negative:
        smooth_txt += (" Exit rule: a holding is sold fully to zero ONLY when "
                       "its composite signal is non-positive; positive-signal "
                       f"holdings that fall out of the top {TOP_N} are trimmed "
                       f"but floored at {DUST:.1%}.")
    rets = load_tradable_returns()
    lines = ["# Portfolio backtest 2024-2026 — pandas_ta composite sets", "",
             "> Long-only, top-8 by signal, signal-tilted inverse-vol weights; "
             "assets with a non-positive composite signal among the top 8 are "
             "replaced by cash at 0% (freed weight sits in cash, not "
             f"reinvested elsewhere). {freq_word} rebalance, 5 bps/side, rf=0."
             f"{smooth_txt} "
             "2026 is partial (YTD). Index/FX assets traded as proxies. "
             "FULL variant is IN-SAMPLE (upper bound), OOS variant selected "
             "sets on data <= 2023-12-31.",
             ""]
    curves = {}
    for label in ["2023-12-31", "FULL"]:
        tag = "OOS" if label != "FULL" else "IS"
        sig = build_signals(label)
        if sig.shape[1] == 0:
            print(f"!! {tag}: no winning sets found for cutoff {label} — variant SKIPPED")
            lines += [f"## {tag} (selection window: {label})", "",
                      "**SKIPPED — no winning sets in results/pandasta_best_sets.csv "
                      "for this cutoff.** Re-run pandasta_set_search.py first.", ""]
            continue
        missing = sorted(set(TRADABLE) - set(sig.columns))
        res = run_backtest(rets[sig.columns], sig, rebal_months=rebal_months,
                           smooth=smooth, exit_only_negative=exit_only_negative)
        m = metrics_table(res["daily"], res["equity"])
        ann_to = res["turnover"].groupby(res["turnover"].index.year).sum()
        curves[tag] = res["equity"]
        lines += [f"## {tag} (selection window: {label})", "",
                  f"Assets with signals: {len(sig.columns)}/{len(TRADABLE)}"
                  + (f" (no FDR-surviving set: {', '.join(missing)})" if missing else ""),
                  "", m.round(4).to_markdown(), "",
                  "Annual turnover (sum of rebalance one-way): "
                  + ", ".join(f"{y}: {v:.2f}x" for y, v in ann_to.items()), ""]
        res["weights"].to_csv(os.path.join(RESULTS, f"portfolio_weights_{tag}{suffix}.csv"))
        lines += _monthly_holdings_lines(tag, res["weights"], res["cash"], freq_word)
        print(f"\n=== {tag} ===\n{m.round(4)}")
    # benchmark: equal-weight buy & hold from backtest start
    bh, bh_eq = equal_weight_buyhold(rets)
    mb = metrics_table(bh, bh_eq)
    curves["EW_BH"] = bh_eq
    lines += ["## Benchmark: equal-weight buy & hold", "",
              mb.round(4).to_markdown(), ""]
    print(f"\n=== EW buy&hold ===\n{mb.round(4)}")
    pd.DataFrame(curves).to_csv(
        os.path.join(RESULTS, f"portfolio_equity_curves{suffix}.csv"))
    report = f"portfolio_backtest_2024_2026{suffix}.md"
    with open(os.path.join(RESULTS, report), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nreport: results/{report}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebal-months", type=int, default=1,
                    help="rebalance cadence in months (default 1 = monthly)")
    ap.add_argument("--smooth", type=float, default=0.5,
                    help="partial-adjustment speed per rebalance in (0, 1]; "
                         "default 0.5 moves halfway to target each month "
                         "(1.0 = classic hard rebalance)")
    ap.add_argument("--exit-only-negative", default=True,
                    action=argparse.BooleanOptionalAction,
                    help="full exits to zero only for non-positive signals "
                         "(default on); positive-signal holdings outside the "
                         "top-N keep a DUST-floor position")
    args = ap.parse_args()
    main(args.rebal_months, args.smooth, args.exit_only_negative)
