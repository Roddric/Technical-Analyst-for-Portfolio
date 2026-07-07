"""
portfolio_backtest.py
=====================
Long-only, 100%-invested, monthly-rebalanced portfolio built from the per-asset
composite technical signals selected by pandasta_set_search.

Ranking -> weights (first trading day each month, decision on prior day data):
  hold top N=8 by composite signal; weight ∝ (1/vol_63d) * tilt,
  tilt = 1 + 0.5 * scaled_rank in [0.5, 1.5]; normalized; 5 bps per side.

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
                 smooth: float = 1.0) -> dict:
    """Daily accounting with weight drift; rebalance on the first trading day
    of every `rebal_months`-th calendar month (1 = monthly, 3 = quarterly on
    Jan/Apr/Jul/Oct) using data through the PRIOR day; costs on turnover.

    `smooth` is the partial-adjustment speed: at each rebalance the book moves
    only `smooth` of the way from its current (drifted) weights toward the
    target, so entries/exits fade in and out instead of snapping (1.0 = jump
    fully to target, the classic behavior). The very first allocation from an
    empty book always goes fully to target. Blended weights under DUST are cut
    to zero (freed weight sits in cash) so exiting tails don't linger forever."""
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
                    tgt[tgt < DUST] = 0.0
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


def main(rebal_months: int = 1, smooth: float = 1.0) -> None:
    os.makedirs(RESULTS, exist_ok=True)
    freq_word = {1: "Monthly", 3: "Quarterly"}.get(rebal_months,
                                                   f"Every-{rebal_months}-month")
    suffix = ("" if rebal_months == 1 else f"_{rebal_months}m") + \
             ("" if smooth >= 1.0 else f"_s{round(smooth * 100)}")
    smooth_txt = ("" if smooth >= 1.0 else
                  f" Turnover-smoothed: each rebalance moves only "
                  f"{smooth:.0%} of the way from current to target weights "
                  f"(entries/exits fade over several rebalances; blended "
                  f"weights < {DUST:.1%} cut to cash).")
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
                           smooth=smooth)
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
    live = rets.index[rets.index >= pd.Timestamp(BACKTEST_START)]
    valid_cols = [c for c in rets.columns
                  if rets[c].loc[live].notna().any()]
    bh_w = pd.Series(1.0 / len(valid_cols), index=valid_cols)
    bh_daily = []
    w = bh_w.copy()
    for d in live:
        r = rets.loc[d, valid_cols].fillna(0.0)
        rp = float((w * r).sum())
        bh_daily.append(rp)
        g = w * (1 + r)
        w = g / g.sum()
    bh = pd.Series(bh_daily, index=live)
    bh_eq = (1 + bh).cumprod()
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
                    help="rebalance cadence in months (1=monthly, 3=quarterly)")
    ap.add_argument("--smooth", type=float, default=1.0,
                    help="partial-adjustment speed per rebalance in (0, 1]; "
                         "e.g. 0.5 moves halfway to target (1.0 = no smoothing)")
    args = ap.parse_args()
    main(args.rebal_months, args.smooth)
