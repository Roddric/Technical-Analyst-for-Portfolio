# v2 · F1 — Walk-Forward Re-Selection Harness (design)

**Date:** 2026-07-07 · **Status:** implemented on branch `v2-f1-walkforward`

## Problem

The headline OOS result (+58.5%, Sharpe 1.72, 2024–2026) is produced by a **single frozen
selection cutoff**: indicator sets are chosen on data ≤ 2023-12-31 and never re-chosen. The
repo already quantifies the risk — an **IS−OOS gap ≈ 28pp** — and both `README.md` and
`results/SUMMARY.md` flag "single frozen cutoff, not walk-forward re-selection" as the top
caveat. Until the edge survives out-of-sample *re-selection*, no higher-capacity model
(cross-sectional combination, meta-labeling, later DL/RL) can be trusted, because each would
be validated against a possibly-lucky cutoff.

F1 builds the walk-forward harness and produces the honest re-selected baseline. It is the
first, deliberately-narrow increment of the v2 research engine; F2 (regularized
cross-sectional signal combination) and F3 (meta-labeling + confidence sizing) build on it
and are out of scope here.

## Approach

Selection is already parameterized by an as-of `cutoff` (`indicator_series_cache(tkr,
cutoff)`, `run_stage1(cutoff)`, `run_stage2(_, cutoff)`), and the output CSVs already carry a
`cutoff` column. Walk-forward is therefore **looping the existing machinery over a schedule
of cutoffs and splicing the resulting sets by date** — not a rewrite.

- **Schedule:** annual, expanding window. Cutoffs `2023-12-31`, `2024-12-31`, `2025-12-31`
  govern trading in 2024, 2025, 2026 respectively. Expanding (not rolling) because history is
  scarce (~10–13y). Cadence is parameterized; a quarterly diagnostic is available.
- **Governing-cutoff rule:** a month-end rebalance *decision* is made on the prior trading
  day (e.g. 2023-12-29 for the Jan-2024 rebalance) and feeds a rebalance a few days later, so
  a decision may legally use a set whose cutoff is slightly *after* the decision date but
  still strictly before the rebalance it feeds. `governing_cutoff(date)` returns the latest
  cutoff strictly before `date + 7d`. This (a) never applies a set to a rebalance on/before
  its own data cutoff — the no-look-ahead invariant — and (b) makes the 2023-12-31 epoch
  govern every 2024 rebalance, so the walk-forward 2024 backtest slice reproduces the frozen
  OOS 2024 (the continuity check).

## Components (extend canonical modules; existing outputs unchanged)

- `pandasta_set_search.run_walkforward_selection(cutoffs, tickers=None, skip_existing=True)`
  — loops `run_stage1`/`run_stage2` over cutoffs, **upserts** rows into
  `pandasta_stage1_ic.csv` / `pandasta_best_sets.csv` by `cutoff` (reusing already-present
  cutoffs so the 2023-12-31 epoch stays bit-identical to the canonical OOS sets; FULL and all
  other cutoffs preserved).
- `portfolio_backtest`:
  - `governing_cutoff(date, cutoffs, lead)` and `WF_CUTOFFS`, `SELECTION_LEAD` constants.
  - `build_walkforward_signals(cutoffs)` — per-cutoff `build_signals` spliced by date.
  - `equal_weight_buyhold(rets, start)` — benchmark extracted from `main` (identical output),
    reused by both `main` and the harness.
- `walkforward.py` (new, thin) — orchestrates selection → WF signals → backtest of the SAME
  strategy (monthly, smooth=0.5, signal-gated exits) → writes
  `results/portfolio_backtest_walkforward.md` and
  `results/portfolio_equity_curves_walkforward.csv`. Report: WF vs frozen-OOS vs IS vs
  benchmark, the IS−WF overfit gap vs the frozen 28pp, and a per-asset set-stability table.

## Honesty constraints

- Only 3 epochs (2026 partial): a directional proof-of-method robustness check, **not** a
  statistically rich validation. The report states this up front.
- No change to the canonical frozen pipeline or its result files; the walk-forward artifacts
  are additive and separately named.

## Verification

1. `python walkforward.py` → `results/portfolio_backtest_walkforward.md` shows WF
   return/vol/Sharpe/maxDD beside OOS, IS, benchmark.
2. Continuity: WF 2024 return ≈ frozen OOS 2024 (+6.9%). Divergence ⇒ stitching bug.
3. Read the headline: how much of Sharpe 1.72 / +58.5% survives re-selection; IS−WF vs 28pp.
4. `pytest tests -q` green, including `tests/test_walkforward.py` (governing-cutoff
   boundaries, no-look-ahead, splice property, 2024 decision-day continuity).

## Roadmap

F2 regularized cross-sectional combination → F3 meta-labeling + confidence sizing → later
DL/RL tiers, each judged only against this F1 walk-forward baseline.
