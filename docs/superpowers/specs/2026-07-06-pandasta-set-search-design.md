# pandas_ta Optimal Indicator-Set Search + Long-Only Portfolio Backtest — Design

Date: 2026-07-06
Status: approved pending user review
Location of implementation: `Work/ta-flat-backtest/` (parent project), reusing its audited engine.

## Goal

1. Find, per individual asset, the optimal **set** of technical indicators — one each from
   the pandas_ta **volume**, **trend**, **momentum**, **volatility** categories.
2. Turn each asset's winning set into a daily **composite technical signal**.
3. Run a **long-only, 100%-invested** portfolio strategy (clear asset rankings → allocation
   weights, monthly rebalance) and backtest calendar years **2024, 2025, 2026-YTD**,
   reporting annual return, Sharpe, volatility, max drawdown, and turnover.

## Universe

- The 18 assets already in `price_cache/` (equity indices, ^TNX, TLT, HYG, LQD, FX pairs,
  DX-Y, GC=F, SI=F, CL=F), classes as defined by `ASSETS` in `grouped_ic_backtest.py`.
- **New: crypto class — `BTC-USD`, `ETH-USD`**, downloaded via yfinance into `price_cache/`
  using the existing cache format. If the sandbox has no network, the user primes the cache
  with a single provided command.
- Calendar: everything aligned to the equity trading calendar (crypto weekend moves fold
  into the next trading day's bar).
- **Tradable set for the portfolio excludes ^TNX** (yield level, not investable; TLT carries
  duration). FX pairs and DX-Y remain as futures/forward proxies — disclosed in the report.
- Forward-return mode: `log` for prices, `diff` for ^TNX (existing `stats.forward_returns`).

## Stage 1 — per-slot screen (per asset)

- Candidates: every indicator in pandas_ta's own category map for `volume`, `trend`,
  `momentum`, `volatility` — **default parameters only** (~110 candidates).
- Multi-column outputs contribute their primary line (explicit per-indicator column map).
- Exclusions / forced-causal fixes:
  - `dpo` → `centered=False` (pandas_ta default is centered = lookahead).
  - Ichimoku forward-displaced spans excluded.
  - Raw price-level outputs (MA-type levels) excluded — same rule as `indicators.py`.
  - Any candidate failing `stats.assert_no_lookahead` or erroring is logged and skipped.
  - Outputs >50% NaN after warmup dropped.
- Volume handling: zero/missing-volume bars masked; assets with no usable volume
  (FX pairs, DX-Y, ^TNX) skip the volume slot and are flagged (3-slot sets downstream).
- Scoring: identical to the prior TA-Lib run via `stats.py` — Spearman IC vs forward
  returns at h = 1, 5, 10, 20 with Newey-West HAC p-values, rolling IC → IC_IR,
  Benjamini-Hochberg FDR. Output schema matches `results/flat_ic_results.csv`.

## Stage 2 — joint set search (per asset)

- Per asset and horizon: FDR survivors per slot, capped at **top 5 per slot by |IC_IR|**
  (≤ 5⁴ = 625 combos).
- For each combo: sign-align each member by its stage-1 IC sign; z-score causally
  (rolling 252d, min 126); equal-weight average → **composite signal**; score the
  composite with the same IC / HAC / IC_IR machinery.
- Rank sets by |composite IC_IR|; report mean pairwise rank-correlation between members
  as the redundancy diagnostic.
- **Strategy set selection**: the set the strategy actually uses per asset is the one with
  the best |composite IC_IR| at **h = 20** (closest horizon to the monthly holding period).
  The traded signal is the composite × sign(its h=20 IC in the selection window), so a
  reliably inverse composite is used contrarian rather than discarded.
- **Two selection windows** (run both, reported side by side):
  - **OOS**: selection sees data ≤ 2023-12-31 only; sets frozen; strategy trades
    2024–2026 fully out-of-sample.
  - **IS**: selection sees full history including 2024–2026 (in-sample upper bound).
  - The IS−OOS performance gap is reported as the overfitting measure.

## Signals → strategy → backtest

- **Per-asset composite signal**: the asset's own winning set (from the relevant selection
  window), stage-2 construction, computed daily.
- **Ranking & weights** (first trading day of each month):
  1. Rank all tradable assets by composite signal.
  2. Hold the **top 8**.
  3. Weights: inverse 63-day volatility base × signal-strength tilt, normalized to sum
     to 1. Tilt is rank-based (robust to signal-magnitude noise): scale the top-8's
     cross-sectional signal ranks to [−1, +1], tilt = 1 + 0.5 × scaled rank → [0.5, 1.5].
     Same guardrail principle as `allocation_engine.py`: a weak/noisy signal can shade
     weights but never override the inverse-vol risk balance.
  4. Always 100% invested, long-only, no shorts, no leverage.
- **Costs**: 5 bps per side applied to turnover at each rebalance; turnover reported.
- **Metrics**: per calendar year 2024, 2025, 2026-YTD and full period — annual return,
  annualized vol, Sharpe (rf = 0, disclosed), max drawdown, turnover.
- **Benchmark**: equal-weight buy-and-hold of the same tradable universe.

## Components

| File (in `ta-flat-backtest/`) | Purpose |
|---|---|
| `pandasta_set_search.py` | Stage 1 + Stage 2; imports `stats.py`, `price_cache.py`, `ASSETS`; CLI flag for selection cutoff |
| `portfolio_backtest.py` | Signals from frozen sets, ranking, weights, monthly backtest, metrics, report |
| `results/pandasta_stage1_ic.csv` | Stage-1 IC table (schema = `flat_ic_results.csv`) |
| `results/pandasta_best_sets.csv` / `.md` | Winning sets per asset, both selection windows |
| `results/portfolio_backtest_2024_2026.md` | Headline report (both variants, benchmark, disclosures) |
| `results/portfolio_equity_curves.csv`, `results/portfolio_weights.csv` | Daily equity curves; weights at each rebalance |

Environment note: module must `import importlib.metadata` before `import pandas_ta`
(Python 3.14 + pandas_ta 0.4.24 quirk, verified in this venv).

## Error handling

- Indicator call failures: caught, logged with indicator name, skipped — never fatal.
- Insufficient history for a (asset, combo): dropped with a logged reason.
- Missing crypto cache + no network: abort with instructions to prime the cache.
- Lookahead: `assert_no_lookahead` on every forward-return series; causal z-scores only.

## Validation / testing

- Smoke run: ^GSPC only, end-to-end, before the full 20-asset run.
- Sanity checks in the report: weights sum to 1 and are ≥ 0 at every rebalance; equity
  curve has no NaN; per-year bars match the metrics table.
- Spot-check one winning indicator's IC by direct recomputation outside the pipeline.

## Honesty constraints (carried into every report)

- Flat-history selection, not regime-conditioned; monthly-rebalance simulation, not live
  trading. IS variant is an upper bound, not a forecast. |IC| values are small; the tilt
  cap exists so weak signals cannot dominate risk balance. Index/FX assets are traded as
  proxies. rf = 0 in Sharpe. 2026 is a partial year (data through ~2026-07).
