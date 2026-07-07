# Portfolio backtest 2024-2026 — pandas_ta composite sets

> Long-only, top-8 by signal, signal-tilted inverse-vol weights; assets with a non-positive composite signal among the top 8 are replaced by cash at 0% (freed weight sits in cash, not reinvested elsewhere). Quarterly rebalance, 5 bps/side, rf=0. 2026 is partial (YTD). Index/FX assets traded as proxies. FULL variant is IN-SAMPLE (upper bound), OOS variant selected sets on data <= 2023-12-31.

## OOS (selection window: 2023-12-31)

Assets with signals: 14/14

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.0932 |    0.0658 |   1.3871 |  -0.0473 |
| 2025 |   0.2628 |    0.1184 |   2.0462 |  -0.1389 |
| 2026 |   0.0831 |    0.1548 |   1.1247 |  -0.0782 |
| FULL |   0.4952 |    0.1098 |   1.5298 |  -0.1389 |

Annual turnover (sum of rebalance one-way): 2024: 1.58x, 2025: 1.85x, 2026: 1.57x

### Quarterly holdings — OOS

| date | holdings |
|---|---|
| 2024-01-02 | ^TWII 19.2%, ^KS11 14.9%, SI=F 9.5%, CL=F 6.4%, CASH 50.0% |
| 2024-04-01 | ^NDX 18.3%, ^KS11 16.5%, ^N225 13.0%, ASHR 11.8%, BTC-USD 2.9%, CASH 37.5% |
| 2024-07-01 | ^GSPC 14.4%, ASHR 13.8%, ^NDX 11.4%, ^TWII 10.4%, CASH 50.0% |
| 2024-10-01 | VWO 16.2%, VEA 15.4%, ^KS11 12.5%, CL=F 12.2%, BTC-USD 6.2%, CASH 37.5% |
| 2025-01-02 | VEA 24.4%, ^FTSE 21.4%, ^GSPC 17.2%, ^NDX 14.1%, SI=F 9.9%, ^N225 6.1%, CL=F 3.9%, ASHR 3.0% |
| 2025-04-01 | ^FTSE 22.4%, VEA 21.6%, ASHR 13.0%, ^NDX 12.2%, VWO 12.1%, ^GSPC 9.7%, ^KS11 7.5%, ETH-USD 1.6% |
| 2025-07-01 | ^KS11 20.0%, ^FTSE 13.2%, GC=F 13.0%, ^N225 11.4%, CL=F 9.5%, ^TWII 7.8%, CASH 25.0% |
| 2025-10-01 | ^N225 16.3%, ^KS11 13.6%, CL=F 7.6%, CASH 62.5% |
| 2026-01-02 | ^NDX 19.3%, ASHR 17.4%, ^TWII 13.7%, GC=F 12.5%, ^N225 9.0%, SI=F 3.1%, CASH 25.0% |
| 2026-04-01 | ^NDX 28.0%, ^FTSE 25.7%, VEA 15.7%, GC=F 10.1%, VWO 8.4%, ETH-USD 5.9%, CL=F 3.6%, SI=F 2.5% |
| 2026-07-01 | GC=F 14.5%, VWO 13.3%, ^N225 9.7%, CASH 62.5% |

## IS (selection window: FULL)

Assets with signals: 14/14

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.2348 |    0.0919 |   2.3422 |  -0.0422 |
| 2025 |   0.2662 |    0.1105 |   2.2102 |  -0.1294 |
| 2026 |   0.2301 |    0.1783 |   2.4516 |  -0.0615 |
| FULL |   0.9233 |    0.1206 |   2.2455 |  -0.1294 |

Annual turnover (sum of rebalance one-way): 2024: 1.51x, 2025: 1.77x, 2026: 1.79x

### Quarterly holdings — IS

| date | holdings |
|---|---|
| 2024-01-02 | ^TWII 33.1%, GC=F 16.2%, ^KS11 14.8%, CL=F 8.8%, BTC-USD 5.6%, SI=F 5.5%, ETH-USD 3.6%, CASH 12.5% |
| 2024-04-01 | ^TWII 20.4%, ^NDX 14.7%, ^N225 11.5%, BTC-USD 3.3%, CASH 50.0% |
| 2024-07-01 | ^TWII 16.1%, GC=F 14.4%, SI=F 7.0%, CASH 62.5% |
| 2024-10-01 | GC=F 19.0%, ^KS11 16.2%, CL=F 15.9%, SI=F 11.6%, BTC-USD 8.0%, ETH-USD 4.4%, CASH 25.0% |
| 2025-01-02 | VEA 23.0%, ^NDX 18.3%, ^FTSE 15.6%, ^KS11 11.0%, GC=F 9.9%, SI=F 9.5%, ^GSPC 8.4%, ASHR 4.4% |
| 2025-04-01 | ^FTSE 21.5%, VEA 18.8%, VWO 15.3%, ^NDX 13.0%, ^KS11 10.4%, ASHR 8.1%, ^GSPC 7.6%, ^N225 5.3% |
| 2025-07-01 | GC=F 14.8%, ^KS11 14.4%, ^FTSE 13.9%, ^N225 12.6%, CL=F 6.7%, CASH 37.5% |
| 2025-10-01 | ^GSPC 17.2%, ^TWII 13.7%, ^N225 12.6%, CL=F 6.5%, CASH 50.0% |
| 2026-01-02 | ^TWII 21.9%, ^NDX 17.8%, ASHR 15.1%, GC=F 11.3%, CL=F 8.2%, ^N225 7.1%, SI=F 6.2%, CASH 12.5% |
| 2026-04-01 | ^GSPC 22.7%, ^NDX 21.9%, ^FTSE 17.4%, VWO 14.1%, VEA 10.4%, GC=F 8.9%, ^KS11 2.5%, ETH-USD 2.2% |
| 2026-07-01 | VWO 18.8%, GC=F 18.6%, ^TWII 16.8%, ^N225 10.9%, SI=F 6.0%, CL=F 3.8%, CASH 25.0% |

## Benchmark: equal-weight buy & hold

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.2381 |    0.1557 |   1.4502 |  -0.1271 |
| 2025 |   0.2888 |    0.1622 |   1.6585 |  -0.1742 |
| 2026 |   0.1142 |    0.2433 |   1.026  |  -0.1257 |
| FULL |   0.7779 |    0.1785 |   1.3879 |  -0.1785 |
