# ta-flat-backtest

Quant-research codebase that finds an **optimal set of technical indicators per asset**
(one each from the volume / trend / momentum / volatility families in `pandas_ta`),
turns each asset's set into a composite signal, and backtests a long-only,
cash-optional portfolio over 2024–2026 on 14 assets (global equity indices, metals,
energy, crypto).

**Headline result (out-of-sample: indicator sets frozen on data ≤ 2023-12-31):**

| Variant | Full-period return | Ann. vol | Sharpe (rf=0) | Max DD | Turnover |
|---|---:|---:|---:|---:|---:|
| Monthly, smoothed (λ=0.5) + signal-gated exits | **+58.5%** | 11.2% | **1.72** | −11.6% | ~1.5–2.4×/yr |
| Monthly, hard rebalance | +53.5% | 12.3% | 1.46 | −11.2% | ~3–5×/yr |
| Quarterly rebalance | +49.5% | 11.0% | 1.53 | −13.9% | ~1.6–1.9×/yr |
| Equal-weight buy & hold (benchmark) | +77.8% | 17.9% | 1.39 | −17.9% | — |

The strategy's edge is **risk-adjusted**, not raw return: it beats buy & hold on Sharpe
and drawdown while averaging only ~72% invested. Full results, per-asset indicator
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
   rank tilt, 5 bps/side costs. Optional: `--smooth` partial adjustment (weights move
   only a fraction toward target, so exits fade instead of snapping to zero),
   `--exit-only-negative` (full liquidation only when the asset's own signal is
   non-positive), `--rebal-months 3` (quarterly).

**Look-ahead discipline:** OOS sets are selected on ≤2023 data only; all indicator
transforms are truncation-invariance tested; `dpo` is forced non-centered; the FDR
test suite includes mutation checks.

## Quickstart

Developed on Python 3.14 / pandas 3.x (3.12+ should work).

```bash
pip install -r requirements.txt
pytest tests -q                              # 36 tests

python pandasta_set_search.py                # rebuild indicator-set selection
python portfolio_backtest.py                 # monthly backtest (OOS + IS + benchmark)
python portfolio_backtest.py --smooth 0.5 --exit-only-negative
python portfolio_backtest.py --rebal-months 3
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
| `portfolio_backtest.py` | Portfolio construction + backtest engine (smoothing, exit gate, cadence) |
| `final-backtest/ta_advisor.py` | Single agent-facing CLI: analyze assets, list holds, output weights |
| `stats.py` | Audited IC / HAC / FDR statistics used by everything above |
| `price_cache/`, `price_cache.py` | Cached daily OHLCV CSVs (Yahoo Finance, through 2026-07) |
| `results/` | All outputs — start with `results/SUMMARY.md` |
| `tests/` | Pytest suite: causality, FDR pooling, cash accounting, smoothing math |
| `docs/superpowers/` | Design spec and implementation plan |
| `data_loader.py`, `macro_loader.py`, `indicators.py`, `main.py`, `grouped_ic_backtest.py`, `regime_*`, `walkforward_backtest.py`, `spot_check_tsi.py`, `final-backtest/phase1_segment.py`, `final-backtest/allocation_engine.py` | Earlier research tracks (grouped IC study, regime segmentation engine); independent of the main pipeline |

## Data notes

- Price data ships in `price_cache/` (daily OHLCV pulled from Yahoo Finance) so all
  results reproduce offline. Yahoo data is for personal/research use — check their
  terms before redistributing.
- The legacy macro modules (`macro_loader.py`, regime engine) need a free FRED API
  key in `fred_key.txt` (git-ignored — never commit it). The main pipeline does not.
- CSI 300 is proxied by the ASHR ETF; index legs (^GSPC etc.) are non-tradable
  proxies — live implementation needs futures/ETFs with their own costs.

## Caveats — read before trusting any number

Composite ICs are small (0.02–0.13). Selection uses a single frozen cutoff, not
walk-forward re-selection; the IS variant is an in-sample upper bound (IS−OOS gap
≈ 24pp is the measured overfitting cost). Smoothing λ and rebalance cadence were
compared, not selected out-of-sample. 2026 is a partial year. Sharpe uses rf=0.

**This is research code. Nothing here is investment advice.**
