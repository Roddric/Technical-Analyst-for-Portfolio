# Technical Indicator-Set Portfolio — Results Summary

**Project:** per-asset optimal pandas_ta indicator sets → composite signals → long-only monthly portfolio.
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

At each month's first trading day (deciding on the prior day's data): rank all 14 by composite signal; take the top 8; **hold only those with a positive signal — the rest of the book sits in cash at 0%**; weight holdings by inverse 63-day volatility × rank tilt (1±0.5); 5 bps per side on turnover; long-only, no leverage.

## Backtest results

**OOS (the honest number):**

| Year | Return | Ann. vol | Sharpe (rf=0) | Max DD | Avg invested |
|---|---:|---:|---:|---:|---:|
| 2024 | +7.6% | 8.1% | 0.95 | −5.2% | 63% |
| 2025 | +34.7% | 12.5% | 2.46 | −11.2% | 75% |
| 2026 YTD | +5.9% | 17.9% | 0.74 | −9.2% | 85% |
| **Full** | **+53.5%** | **12.3%** | **1.46** | **−11.2%** | 72% |

**IS upper bound:** +77.1% full-period, Sharpe 1.87. **Equal-weight buy & hold benchmark:** +77.8%, vol 17.9%, Sharpe 1.39, maxDD −17.9%.

### Turnover-smoothed monthly variant (partial adjustment, λ = 0.5)

Each monthly rebalance moves only halfway from current (drifted) weights to target, so entries/exits fade over several months instead of snapping 15% → 0 → 15%; blended weights < 0.5% are cut to cash. Largest single-rebalance weight change drops from 28pp to 13pp; turnover halves to ~1.5–2.4×/yr.

| Year | Smoothed OOS return | Sharpe | maxDD | Hard-monthly OOS return |
|---|---:|---:|---:|---:|
| 2024 | +6.9% | 0.97 | −5.5% | +7.6% |
| 2025 | +31.7% | 2.48 | −11.6% | +34.7% |
| 2026 YTD | +12.5% | 1.57 | −7.5% | +5.9% |
| **Full** | **+58.5%** | **1.72** | **−11.6%** | +53.5% |

Smoothing improves both return and Sharpe overall — the 2026 whipsaw months are where the hard rebalance bled. Sensitivity: λ = 1/3 gives +61.4% / Sharpe 1.83 at ~1.6×/yr turnover (`results/portfolio_backtest_2024_2026_s33.md`); λ was not selected out-of-sample. Report: `results/portfolio_backtest_2024_2026_s50.md`; charts: https://claude.ai/code/artifact/47767b26-4a6f-43d5-877d-02775577193d

### Signal-gated exits (`--exit-only-negative`, with smoothing)

A holding may be sold fully to zero ONLY when its own composite signal is non-positive; a positive-signal holding that merely falls out of the top 8 is trimmed but floored at 0.5% until its signal flips (gross renormalized if floors overshoot 1). On 2024–2026 history the gate never binds — every full exit the smoothed strategy made was already signal-negative — so OOS/IS results are identical to the λ = 0.5 smoothed run above; the rule is now guaranteed by code rather than by coincidence. Report: `results/portfolio_backtest_2024_2026_s50_xn.md`; charts (equity graph shows IS vs OOS only): https://claude.ai/code/artifact/c0a925a7-b5c0-48d0-ad75-bb8269fc01f5

### Quarterly-rebalance variant (same strategy, rebalance Jan/Apr/Jul/Oct)

| Year | Qtr OOS return | Qtr Sharpe | Qtr maxDD | Monthly OOS return |
|---|---:|---:|---:|---:|
| 2024 | +9.3% | 1.39 | −4.7% | +7.6% |
| 2025 | +26.3% | 2.05 | −13.9% | +34.7% |
| 2026 YTD | +8.3% | 1.12 | −7.8% | +5.9% |
| **Full** | **+49.5%** | **1.53** | **−13.9%** | **+53.5%** |

Quarterly cuts turnover to ~1.6–1.9×/yr (from ~4–5× monthly), lowers vol (11.0% vs 12.3%) and edges out monthly on Sharpe (1.53 vs 1.46), but gives up 4pp of total return and takes a deeper max drawdown — a stale book sits unchanged for three months (the Oct-2025 rebalance went 62.5% cash for a full quarter, forfeiting most of monthly's late-2025 gains). Quarterly IS upper bound: +92.3%, Sharpe 2.25. Report: `results/portfolio_backtest_2024_2026_3m.md`; charts: https://claude.ai/code/artifact/8c31ecb8-bf65-44a1-a3cd-fd113a3dd66f

## Interpretation

- **The strategy's edge is risk-adjusted, not raw return**: it beats the benchmark on Sharpe (1.46 vs 1.39) and drawdown (−11.2% vs −17.9%) but trails on total return, because it averaged only 72% invested in a strong bull period.
- **2024 lagged** (+7.6% vs +23.8%) from a double miss: 63% average investment (cash drag) *and* an invested sleeve tilted to Asia/commodities while US mega-caps led.
- **2025 is the signal working**: 75% invested, sleeve earning +51%, beating the benchmark outright (+34.7% vs +28.9%).
- **2026 YTD** took the March (−8.9%) and June (−4.8%) sell-offs at ~85% invested — the cash cushion arrived after the damage.
- **IS−OOS gap ≈ 24pp** over the full period: the measured cost of selection overfitting. Expect live results closer to OOS than IS.

## Caveats (read before acting on any number)

Flat-history selection, not regime-conditioned; single frozen cutoff, not walk-forward re-selection. Composite ICs are small (0.02–0.13). Fallback slots bypass the FDR gate. Index legs (^GSPC etc.) are proxies — live implementation needs futures/ETFs with their own costs. rf=0 in Sharpe. 2026 is half a year. Yahoo data quality applies throughout.

## Where everything lives

| Artifact | Path |
|---|---|
| Per-asset winning sets (both windows) | `results/pandasta_best_sets.md` / `.csv` |
| Stage-1 IC table (every indicator × asset × horizon) | `results/pandasta_stage1_ic.csv` |
| Backtest report + monthly holdings | `results/portfolio_backtest_2024_2026.md` |
| Equity curves / per-rebalance weights | `results/portfolio_equity_curves.csv`, `portfolio_weights_OOS.csv`, `portfolio_weights_IS.csv` |
| Interactive charts | https://claude.ai/code/artifact/a5737ad2-8022-4071-a7a1-9af52e99b99b |
| Spec / plan | `docs/superpowers/specs/`, `docs/superpowers/plans/` |
