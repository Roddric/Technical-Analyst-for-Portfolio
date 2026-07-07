# ta-flat-backtest

Quant-research codebase that finds an **optimal set of technical indicators per asset**
(one each from the volume / trend / momentum / volatility families in `pandas_ta`),
turns each asset's set into a composite signal, and backtests a long-only,
cash-optional portfolio over 2024–2026 on 14 assets (global equity indices, metals,
energy, crypto).

**Headline result (out-of-sample: indicator sets frozen on data ≤ 2023-12-31):**

| | Full-period return | Ann. vol | Sharpe (rf=0) | Max DD | Turnover |
|---|---:|---:|---:|---:|---:|
| Strategy | **+58.5%** | 11.2% | **1.72** | −11.6% | ~1.5–2.4×/yr |
| Equal-weight buy & hold (benchmark) | +77.8% | 17.9% | 1.39 | −17.9% | — |

The strategy's edge is **risk-adjusted**, not raw return: it beats buy & hold on Sharpe
and drawdown while averaging only ~71% invested. Full results, per-asset indicator
sets, and caveats: [`results/SUMMARY.md`](results/SUMMARY.md).

## How it works

1. **Stage 1 — per-slot screen** (`pandasta_set_search.py`): every curated `pandas_ta`
   indicator (defaults only, causality-checked) is scored per asset by Spearman rank IC
   against 1/5/10/20-day forward returns with Newey–West HAC p-values; a pooled
   Benjamini–Hochberg FDR gate (q=0.10) keeps survivors. Slots with no survivor are
   filled by best |IC_IR| and flagged as weaker evidence.
2. **Stage 2 — joint set search**: top-5 per slot are combined; each candidate set's
   members are sign-aligned, causally z-scored (252d window) and equal-weight averaged
   into a composite; the winner per asset maximizes |composite IC_IR| at horizon 20,
   with a redundancy penalty.
3. **Portfolio** (`portfolio_backtest.py`): monthly rebalance deciding on prior-day
   data — rank all assets by composite signal, hold the top 8, park any
   negative-signal name in **cash at 0%**, weight the rest by inverse 63-day vol ×
   rank tilt, 5 bps/side costs. Two stabilizers are built into the strategy:
   **turnover smoothing** (each rebalance moves only halfway from current to target
   weights, so entries/exits fade over months instead of snapping 15% → 0 → 15%)
   and **signal-gated exits** (a holding may be liquidated fully only when its own
   composite signal is non-positive; falling out of the top 8 alone just trims it,
   floored at 0.5%).

**Look-ahead discipline:** OOS sets are selected on ≤2023 data only; all indicator
transforms are truncation-invariance tested; `dpo` is forced non-centered; the FDR
test suite includes mutation checks.

## Quickstart

Developed on Python 3.14 / pandas 3.x (3.12+ should work).

```bash
pip install -r requirements.txt
pytest tests -q                              # 36 tests

python pandasta_set_search.py                # rebuild indicator-set selection
python portfolio_backtest.py                 # backtest (OOS + IS + benchmark)
python final-backtest/ta_advisor.py          # current advice: signals, holds, weights
```

`ta_advisor.py` is the agent/automation entry point: one command prints (or emits
JSON via `--json out.json`) the per-asset composite signals, which assets to hold and
why, and target portfolio weights including cash, using the frozen backtested sets.
`--refresh` pulls latest Yahoo prices into the cache first.

## Repository layout

| Path | What it is |
|---|---|
| `pandasta_registry.py` | Curated `pandas_ta` candidates, exclusions with reasons, causality guards |
| `pandasta_data.py` | 14-asset universe, price loading, master trading calendar |
| `pandasta_set_search.py` | Two-stage indicator-set search (FDR screen → joint composite) |
| `portfolio_backtest.py` | Portfolio construction + backtest engine (smoothing, exit gate) |
| `final-backtest/ta_advisor.py` | Single agent-facing CLI: analyze assets, list holds, output weights |
| `stats.py` | Audited IC / HAC / FDR statistics used by everything above |
| `price_cache/`, `price_cache.py` | Cached daily OHLCV CSVs (Yahoo Finance, through 2026-07) |
| `results/` | All outputs — start with `results/SUMMARY.md` |
| `tests/` | Pytest suite: causality, FDR pooling, cash accounting, smoothing math |
| `docs/superpowers/` | Design spec and implementation plan |

## Data notes

- Price data ships in `price_cache/` (daily OHLCV pulled from Yahoo Finance) so all
  results reproduce offline. Yahoo data is for personal/research use — check their
  terms before redistributing. Refresh via `python final-backtest/ta_advisor.py --refresh`
  or `python price_cache.py`.
- CSI 300 is proxied by the ASHR ETF; index legs (^GSPC etc.) are non-tradable
  proxies — live implementation needs futures/ETFs with their own costs.

## Caveats — read before trusting any number

Composite ICs are small (0.02–0.13). Selection uses a single frozen cutoff, not
walk-forward re-selection; the IS variant is an in-sample upper bound (IS−OOS gap
≈ 28pp is the measured overfitting cost). The smoothing speed (λ=0.5) was not
selected out-of-sample. 2026 is a partial year. Sharpe uses rf=0.

**This is research code. Nothing here is investment advice.**
