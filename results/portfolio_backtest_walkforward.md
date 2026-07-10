# Walk-forward re-selection backtest (v2 · F1)

> **Honest re-selected baseline.** Indicator sets are re-chosen at each cutoff on an EXPANDING window (2023-12-31, 2024-12-31, 2025-12-31); the set picked at each cutoff governs the following period's monthly rebalances. Same strategy as the canonical backtest (long-only, top-8 by signal, inverse-vol x rank tilt, smooth=0.5, signal-gated exits, 5 bps/side, rf=0). Assets with signals: 14/14.

> **Caveat — read first.** Only 3 epochs (2026 partial). This is a directional proof-of-method and robustness check, NOT a statistically rich validation: too few out-of-sample re-selections to size confidence intervals. Treat the walk-forward numbers as a sanity floor on the frozen-cutoff result, not a precise forecast.

## Full-period metrics — walk-forward vs frozen OOS vs IS vs benchmark

|                |   return |   ann_vol |   sharpe |   max_dd |
|:---------------|---------:|----------:|---------:|---------:|
| Walk-forward   |   0.677  |    0.1093 |   1.9603 |  -0.1001 |
| Frozen OOS     |   0.6253 |    0.1142 |   1.7702 |  -0.1094 |
| In-sample (IS) |   0.8677 |    0.1169 |   2.2103 |  -0.1029 |
| EW buy&hold    |   0.7779 |    0.1785 |   1.3879 |  -0.1785 |

## Walk-forward, year by year

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.0852 |    0.0796 |   1.0673 |  -0.062  |
| 2025 |   0.3452 |    0.1062 |   2.8697 |  -0.1001 |
| 2026 |   0.1487 |    0.1571 |   1.873  |  -0.0727 |
| FULL |   0.677  |    0.1093 |   1.9603 |  -0.1001 |

## Overfitting gap (the robustness headline)

- Frozen IS - OOS gap: **+24.2 pp** (the single-cutoff overfit cost quoted in SUMMARY.md).
- IS - **walk-forward** gap: **+19.1 pp**.
- If the walk-forward gap is materially narrower than the frozen gap, re-selection recovered part of the overfit; if the walk-forward FULL return collapses toward zero, the edge was largely the lucky cutoff.

## Set stability across cutoffs

Slots (of 4) whose chosen indicator changed between consecutive cutoffs. High churn ⇒ the IC screen is re-picking on noise.

| asset   | changes_between_cutoffs   |   avg_slots_changed |
|:--------|:--------------------------|--------------------:|
| VWO     | [3, 2]                    |                 2.5 |
| BTC-USD | [1, 2]                    |                 1.5 |
| ^KS11   | [2, 1]                    |                 1.5 |
| ^GSPC   | [0, 2]                    |                 1   |
| SI=F    | [1, 1]                    |                 1   |
| ASHR    | [2, 0]                    |                 1   |
| ^NDX    | [1, 1]                    |                 1   |
| VEA     | [1, 1]                    |                 1   |
| CL=F    | [1, 0]                    |                 0.5 |
| ETH-USD | [0, 1]                    |                 0.5 |
| GC=F    | [1, 0]                    |                 0.5 |
| ^FTSE   | [1, 0]                    |                 0.5 |
| ^N225   | [0, 0]                    |                 0   |
| ^TWII   | [0, 0]                    |                 0   |

## Selected set per epoch

### cutoff 2023-12-31

| asset | volume | trend | momentum | volatility |
|---|---|---|---|---|
| ASHR | VU-adosc | TR-dpo | MO-slope | VO-BBP |
| BTC-USD | VU-mfi | TR-adx | MO-kst | VO-rvi |
| CL=F | VU-pvt | TR-dpo | MO-tsi | VO-ATR_RATIO |
| ETH-USD | VU-nvi | TR-dpo | MO-tsi | VO-rvi |
| GC=F | VU-ad | TR-dpo | MO-crsi | VO-rvi |
| SI=F | VU-ad | TR-dpo | MO-crsi | VO-DC_WIDTH |
| VEA | VU-pvt | TR-aroon | MO-crsi | VO-ATR_RATIO |
| VWO | VU-efi | TR-dpo | MO-uo | VO-natr |
| ^FTSE | VU-pvt | TR-dpo | MO-eri | VO-DC_WIDTH |
| ^GSPC | VU-efi | TR-dpo | MO-slope | VO-BBP |
| ^KS11 | VU-pvi | TR-adx | MO-cfo | VO-DC_WIDTH |
| ^N225 | VU-adosc | TR-chop | MO-trix | VO-ui |
| ^NDX | VU-adosc | TR-dpo | MO-uo | VO-BBP |
| ^TWII | VU-pvt | TR-dpo | MO-eri | VO-BBP |

### cutoff 2024-12-31

| asset | volume | trend | momentum | volatility |
|---|---|---|---|---|
| ASHR | VU-pvi | TR-dpo | MO-crsi | VO-BBP |
| BTC-USD | VU-mfi | TR-vortex | MO-kst | VO-rvi |
| CL=F | VU-pvt | TR-vhf | MO-tsi | VO-ATR_RATIO |
| ETH-USD | VU-nvi | TR-dpo | MO-tsi | VO-rvi |
| GC=F | VU-pvt | TR-dpo | MO-crsi | VO-rvi |
| SI=F | VU-ad | TR-dpo | MO-crsi | VO-rvi |
| VEA | VU-pvt | TR-aroon | MO-slope | VO-ATR_RATIO |
| VWO | VU-obv | TR-dpo | MO-crsi | VO-BBP |
| ^FTSE | VU-pvt | TR-dpo | MO-rsi | VO-DC_WIDTH |
| ^GSPC | VU-efi | TR-dpo | MO-slope | VO-BBP |
| ^KS11 | VU-pvt | TR-adx | MO-cfo | VO-ATR_RATIO |
| ^N225 | VU-adosc | TR-chop | MO-trix | VO-ui |
| ^NDX | VU-adosc | TR-dpo | MO-slope | VO-BBP |
| ^TWII | VU-pvt | TR-dpo | MO-eri | VO-BBP |

### cutoff 2025-12-31

| asset | volume | trend | momentum | volatility |
|---|---|---|---|---|
| ASHR | VU-pvi | TR-dpo | MO-crsi | VO-BBP |
| BTC-USD | VU-cmf | TR-aroon | MO-kst | VO-rvi |
| CL=F | VU-pvt | TR-vhf | MO-tsi | VO-ATR_RATIO |
| ETH-USD | VU-wb_tsv | TR-dpo | MO-tsi | VO-rvi |
| GC=F | VU-pvt | TR-dpo | MO-crsi | VO-rvi |
| SI=F | VU-ad | TR-dpo | MO-crsi | VO-ATR_RATIO |
| VEA | VU-pvt | TR-aroon | MO-rsi | VO-ATR_RATIO |
| VWO | VU-efi | TR-dpo | MO-crsi | VO-ATR_RATIO |
| ^FTSE | VU-pvt | TR-dpo | MO-rsi | VO-DC_WIDTH |
| ^GSPC | VU-efi | TR-vortex | MO-stc | VO-BBP |
| ^KS11 | VU-pvt | TR-adx | MO-tsi | VO-ATR_RATIO |
| ^N225 | VU-adosc | TR-chop | MO-trix | VO-ui |
| ^NDX | VU-adosc | TR-dpo | MO-stochf | VO-BBP |
| ^TWII | VU-pvt | TR-dpo | MO-eri | VO-BBP |
