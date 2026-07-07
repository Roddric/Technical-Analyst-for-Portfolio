# Technical Indicator-Set Portfolio — Results Summary

**Project:** per-asset optimal pandas_ta indicator sets → composite signals → long-only monthly portfolio with turnover smoothing and signal-gated exits.
**Data:** daily OHLCV through 2026-07-01/06 (Yahoo). **Backtest:** 2024-01 → 2026-07 (2026 is a partial year).
**Selection discipline:** OOS sets frozen on data ≤ 2023-12-31; the IS (full-history) variant is an in-sample upper bound, not a forecast.

## Universe (14 assets)

Equities: S&P 500 (^GSPC), Nasdaq 100 (^NDX), FTSE 100 (^FTSE), KOSPI (^KS11), Nikkei 225 (^N225), TAIEX (^TWII), CSI 300 via ASHR ETF, VEA (developed ex-US), VWO (emerging).
Metals: Gold (GC=F), Silver (SI=F). Energy: WTI crude (CL=F). Crypto: BTC-USD, ETH-USD.
ASHR proxies CSI 300 because Yahoo's native index history starts 2021-03 — too short for selection.

## Optimal indicator set per asset (OOS, all four slots filled)

| Asset | Volume | Trend | Momentum | Volatility | comp IC (h=20) | FDR fallback slots |
|---|---|---|---|---|---:|---|
| ^GSPC | efi | dpo | slope | bbands %B | +0.032 | trend |
| ^NDX | adosc | dpo | uo | bbands %B | +0.016 | trend |
| ^FTSE | pvt | dpo | eri | donchian width | +0.127 | — |
| ^KS11 | pvi | adx | cfo | donchian width | +0.099 | — |
| ^N225 | adosc | chop | trix | ui | +0.021 | volatility |
| ^TWII | pvt | dpo | eri | bbands %B | +0.017 | volume, trend |
| ASHR | adosc | dpo | slope | bbands %B | +0.068 | trend |
| VEA | pvt | aroon | crsi | atr ratio | +0.040 | volume |
| VWO | efi | dpo | uo | natr | +0.059 | trend |
| GC=F | ad | dpo | crsi | rvi | +0.070 | trend, volatility |
| SI=F | ad | dpo | crsi | donchian width | +0.059 | trend |
| CL=F | pvt | dpo | tsi | atr ratio | +0.058 | **all four** |
| BTC-USD | mfi | adx | kst | rvi | +0.099 | volatility |
| ETH-USD | nvi | dpo | tsi | rvi | +0.062 | trend, momentum, volatility |

A **fallback** slot had no indicator surviving the Benjamini-Hochberg false-discovery gate (q=0.10); the best-|IC_IR| candidate fills it as requested, but it is statistically weaker evidence. CL=F and ETH-USD sets are entirely fallback — treat their signals with extra skepticism.

Methodology: Spearman IC vs forward returns (h = 1/5/10/20) with Newey-West HAC p-values; composite = equal-weight average of sign-aligned, causally z-scored (252d/126) members; winner by |composite IC_IR| at h=20; traded sign = sign of composite IC at h=20 in the selection window.

## Strategy

At each month's first trading day (deciding on the prior day's data):

1. Rank all 14 assets by composite signal; take the top 8; **only positive-signal members are investable — the rest of the book sits in cash at 0%**; weight holdings by inverse 63-day volatility × rank tilt (1±0.5).
2. **Turnover smoothing:** the book moves only **halfway** (λ = 0.5) from its current drifted weights toward that target, so entries and exits fade over several months instead of snapping 15% → 0 → 15%. The largest single-rebalance weight change is 13pp (vs 28pp unsmoothed); turnover is ~1.5–2.4×/yr.
3. **Signal-gated exits:** a holding may be sold fully to zero **only when its own composite signal is non-positive**. A positive-signal holding that merely falls out of the top 8 is trimmed but floored at 0.5% until its signal actually flips.
4. Costs: 5 bps per side on turnover; long-only, no leverage; rf = 0.

## Backtest results

**OOS (the honest number):**

| Year | Return | Ann. vol | Sharpe (rf=0) | Max DD | Avg invested |
|---|---:|---:|---:|---:|---:|
| 2024 | +6.9% | 7.2% | 0.97 | −5.5% | 62% |
| 2025 | +31.7% | 11.5% | 2.48 | −11.6% | 78% |
| 2026 YTD | +12.5% | 16.1% | 1.57 | −7.5% | 77% |
| **Full** | **+58.5%** | **11.2%** | **1.72** | **−11.6%** | 71% |

**IS upper bound:** +86.8% full-period, Sharpe 2.21, maxDD −10.3%. **Equal-weight buy & hold benchmark:** +77.8%, vol 17.9%, Sharpe 1.39, maxDD −17.9%.

## Interpretation

- **The strategy's edge is risk-adjusted, not raw return**: it beats the benchmark on Sharpe (1.72 vs 1.39) and drawdown (−11.6% vs −17.9%) but trails on total return, because it averaged only ~71% invested in a strong bull period.
- **2024 lagged** (+6.9% vs +23.8%) from a double miss: 62% average investment (cash drag) *and* an invested sleeve tilted to Asia/commodities while US mega-caps led.
- **2025 is the signal working**: 78% invested, beating the benchmark outright (+31.7% vs +28.9%).
- **2026 YTD beats the benchmark** (+12.5% vs +11.4%) with a shallower drawdown — fading exits kept more of the rebound around the March and June sell-offs.
- **IS−OOS gap ≈ 28pp** over the full period: the measured cost of selection overfitting. Expect live results closer to OOS than IS.

## Caveats (read before acting on any number)

Flat-history selection, not regime-conditioned; single frozen cutoff, not walk-forward re-selection. Composite ICs are small (0.02–0.13). Fallback slots bypass the FDR gate. The smoothing speed (λ = 0.5) was not selected out-of-sample. Index legs (^GSPC etc.) are proxies — live implementation needs futures/ETFs with their own costs. rf=0 in Sharpe. 2026 is half a year. Yahoo data quality applies throughout.

## Where everything lives

| Artifact | Path |
|---|---|
| Per-asset winning sets (both windows) | `results/pandasta_best_sets.md` / `.csv` |
| Stage-1 IC table (every indicator × asset × horizon) | `results/pandasta_stage1_ic.csv` |
| Backtest report + monthly holdings | `results/portfolio_backtest_2024_2026.md` |
| Equity curves / per-rebalance weights | `results/portfolio_equity_curves.csv`, `portfolio_weights_OOS.csv`, `portfolio_weights_IS.csv` |
| Interactive charts (IS vs OOS equity, composition, weight heatmap) | https://claude.ai/code/artifact/c0a925a7-b5c0-48d0-ad75-bb8269fc01f5 |
| Agent entry point (signals, holds, weights) | `final-backtest/ta_advisor.py` |
| Spec / plan | `docs/superpowers/specs/`, `docs/superpowers/plans/` |
