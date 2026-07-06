# Portfolio backtest 2024-2026 — pandas_ta composite sets

> Long-only, 100% invested, top-8 signal-tilted inverse-vol, monthly rebalance, 5 bps/side, rf=0. 2026 is partial (YTD). Index/FX assets traded as proxies. FULL variant is IN-SAMPLE (upper bound), OOS variant selected sets on data <= 2023-12-31.

## OOS (selection window: 2023-12-31)

Assets with signals: 19/19

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.0787 |    0.0752 |   1.0447 |  -0.0827 |
| 2025 |   0.1343 |    0.0803 |   1.6226 |  -0.0943 |
| 2026 |   0.0161 |    0.0872 |   0.4163 |  -0.0409 |
| FULL |   0.2433 |    0.0796 |   1.1408 |  -0.0943 |

Annual turnover (sum of rebalance one-way): 2024: 6.81x, 2025: 7.84x, 2026: 4.19x

## IS (selection window: FULL)

Assets with signals: 19/19

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.1127 |    0.0938 |   1.1853 |  -0.0955 |
| 2025 |   0.1811 |    0.0884 |   1.9424 |  -0.0847 |
| 2026 |   0.0217 |    0.0849 |   0.5562 |  -0.0329 |
| FULL |   0.3427 |    0.0899 |   1.3653 |  -0.0955 |

Annual turnover (sum of rebalance one-way): 2024: 6.98x, 2025: 7.28x, 2026: 4.73x

## Benchmark: equal-weight buy & hold

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.1749 |    0.1142 |   1.4684 |  -0.0938 |
| 2025 |   0.2075 |    0.1241 |   1.5941 |  -0.1224 |
| 2026 |   0.04   |    0.1934 |   0.5096 |  -0.1123 |
| FULL |   0.4755 |    0.1369 |   1.213  |  -0.1224 |
