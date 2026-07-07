# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`final-backtest/` holds the agent-facing entry point for the technical-indicator-set pipeline that lives in the **parent directory** (`ta-flat-backtest/`). The pipeline itself — indicator registry, universe/data layer, two-stage set search, portfolio backtest, audited statistics — is documented in the parent `README.md`; read that first.

- **`ta_advisor.py`** — single CLI for automation/AI agents. For a given as-of date it reports each asset's composite technical signal (member-by-member, sign-aligned z-scores), which assets to hold and why (rank, sign, cash rule), and target portfolio weights including the cash position. It bootstraps the canonical modules from the parent via `sys.path.insert(0, parent)`, performs **no re-selection** (indicator sets stay frozen exactly as backtested from `results/pandasta_best_sets.csv`), and is runnable from any working directory.

```bash
python ta_advisor.py                     # latest cached data, OOS sets
python ta_advisor.py --date 2026-06-30   # as-of a past date
python ta_advisor.py --window FULL       # in-sample sets (upper bound)
python ta_advisor.py --json out.json     # machine-readable output
python ta_advisor.py --refresh           # update price cache first (Yahoo)
```

## Rules that matter here

- **Do not duplicate parent modules into this directory.** The advisor deliberately imports the parent's canonical `pandasta_*` / `portfolio_backtest` / `price_cache`; stale copies next to this file are shadowed by the bootstrap and only cause drift confusion.
- The advisor's output includes honesty disclosures (frozen selection window, small ICs, FDR-fallback slots, OOS vs in-sample framing). Preserve them when extending the output — never let a weaker-evidence signal print without its flag.
- Prefer `yf.Ticker(t).history(period="max")` over `yf.download()` for cache refreshes — the latter intermittently fails in this environment where the former succeeds.
- Tests for the whole pipeline live in the parent's `tests/` (run `pytest tests -q` from the parent); there are no tests specific to this directory, so verify advisor changes by reproducing a known backtest rebalance (e.g. `--date 2026-06-30` must match the July 2026 row of `results/portfolio_backtest_2024_2026.md`).
