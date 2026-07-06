# Portfolio backtest 2024-2026 — pandas_ta composite sets

> Long-only, top-8 by signal, signal-tilted inverse-vol weights; assets with a non-positive composite signal among the top 8 are replaced by cash at 0% (freed weight sits in cash, not reinvested elsewhere). Monthly rebalance, 5 bps/side, rf=0. 2026 is partial (YTD). Index/FX assets traded as proxies. FULL variant is IN-SAMPLE (upper bound), OOS variant selected sets on data <= 2023-12-31.

## OOS (selection window: 2023-12-31)

Assets with signals: 14/14

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.0764 |    0.0812 |   0.9475 |  -0.0517 |
| 2025 |   0.3466 |    0.1251 |   2.4621 |  -0.112  |
| 2026 |   0.0592 |    0.179  |   0.7423 |  -0.0916 |
| FULL |   0.5354 |    0.1234 |   1.4607 |  -0.112  |

Annual turnover (sum of rebalance one-way): 2024: 4.85x, 2025: 5.12x, 2026: 3.32x

### Monthly holdings — OOS

| date | holdings |
|---|---|
| 2024-01-02 | ^TWII 19.2%, ^KS11 14.9%, SI=F 9.5%, CL=F 6.4%, CASH 50.0% |
| 2024-02-01 | ^NDX 18.5%, ^GSPC 17.7%, ASHR 13.5%, ^N225 13.2%, ^KS11 7.3%, CL=F 4.8%, CASH 25.0% |
| 2024-03-01 | ^TWII 22.3%, ^N225 17.7%, ^KS11 12.3%, ASHR 10.5%, ETH-USD 6.3%, BTC-USD 5.9%, CASH 25.0% |
| 2024-04-01 | ^NDX 18.3%, ^KS11 16.5%, ^N225 13.0%, ASHR 11.8%, BTC-USD 2.9%, CASH 37.5% |
| 2024-05-01 | ^GSPC 18.7%, VEA 16.7%, ^NDX 12.1%, ^KS11 8.4%, SI=F 6.6%, CASH 37.5% |
| 2024-06-03 | ASHR 21.0%, VWO 20.0%, GC=F 13.4%, SI=F 8.5%, CL=F 8.3%, ETH-USD 3.9%, CASH 25.0% |
| 2024-07-01 | ^GSPC 14.4%, ASHR 13.8%, ^NDX 11.4%, ^TWII 10.4%, CASH 50.0% |
| 2024-08-01 | ^NDX 14.5%, ^KS11 13.9%, CL=F 9.0%, CASH 62.5% |
| 2024-09-03 | VWO 16.5%, GC=F 12.8%, ^KS11 12.0%, CL=F 8.7%, CASH 50.0% |
| 2024-10-01 | VWO 16.2%, VEA 15.4%, ^KS11 12.5%, CL=F 12.2%, BTC-USD 6.2%, CASH 37.5% |
| 2024-11-01 | ^FTSE 23.0%, ^GSPC 20.8%, VEA 18.8%, ^NDX 16.6%, VWO 9.3%, CL=F 5.3%, SI=F 3.4%, ASHR 2.8% |
| 2024-12-02 | VEA 23.7%, SI=F 11.4%, CL=F 11.3%, BTC-USD 9.3%, ETH-USD 6.8%, CASH 37.5% |
| 2025-01-02 | VEA 24.4%, ^FTSE 21.4%, ^GSPC 17.2%, ^NDX 14.1%, SI=F 9.9%, ^N225 6.1%, CL=F 3.9%, ASHR 3.0% |
| 2025-02-03 | VEA 19.9%, ^GSPC 15.5%, VWO 11.2%, ASHR 8.6%, CL=F 7.2%, CASH 37.5% |
| 2025-03-03 | VWO 20.0%, ^NDX 18.0%, GC=F 14.7%, ASHR 12.7%, ^N225 9.3%, SI=F 9.3%, ^GSPC 8.6%, CL=F 7.4% |
| 2025-04-01 | ^FTSE 22.4%, VEA 21.6%, ASHR 13.0%, ^NDX 12.2%, VWO 12.1%, ^GSPC 9.7%, ^KS11 7.5%, ETH-USD 1.6% |
| 2025-05-01 | ^FTSE 24.6%, CL=F 17.6%, SI=F 16.5%, VEA 12.2%, ^TWII 9.9%, ^KS11 8.2%, ETH-USD 5.7%, BTC-USD 5.3% |
| 2025-06-02 | GC=F 21.3%, ASHR 17.4%, CL=F 13.7%, VWO 11.1%, ^TWII 10.2%, ^KS11 10.0%, ETH-USD 3.9%, CASH 12.5% |
| 2025-07-01 | ^KS11 20.0%, ^FTSE 13.2%, GC=F 13.0%, ^N225 11.4%, CL=F 9.5%, ^TWII 7.8%, CASH 25.0% |
| 2025-08-01 | ASHR 19.2%, GC=F 16.1%, ^N225 16.0%, ^NDX 14.5%, VEA 11.9%, ^TWII 10.6%, ^KS11 7.3%, ETH-USD 4.3% |
| 2025-09-02 | ^NDX 17.3%, ^N225 15.1%, CL=F 5.1%, CASH 62.5% |
| 2025-10-01 | ^N225 16.3%, ^KS11 13.6%, CL=F 7.6%, CASH 62.5% |
| 2025-11-03 | ^KS11 21.6%, GC=F 14.6%, ASHR 14.0%, ^N225 13.0%, ^TWII 11.8%, SI=F 6.5%, CL=F 6.1%, CASH 12.5% |
| 2025-12-01 | ^N225 12.8%, CL=F 12.2%, CASH 75.0% |
| 2026-01-02 | ^NDX 19.3%, ASHR 17.4%, ^TWII 13.7%, GC=F 12.5%, ^N225 9.0%, SI=F 3.1%, CASH 25.0% |
| 2026-02-02 | ASHR 18.6%, VWO 17.5%, ^NDX 16.7%, ^KS11 13.4%, GC=F 5.6%, SI=F 3.2%, CASH 25.0% |
| 2026-03-02 | ^TWII 21.3%, ^GSPC 18.9%, ^N225 14.7%, ^KS11 13.5%, VWO 13.2%, ETH-USD 3.1%, SI=F 2.7%, CASH 12.5% |
| 2026-04-01 | ^NDX 28.0%, ^FTSE 25.7%, VEA 15.7%, GC=F 10.1%, VWO 8.4%, ETH-USD 5.9%, CL=F 3.6%, SI=F 2.5% |
| 2026-05-01 | VWO 19.4%, ^FTSE 14.8%, GC=F 14.4%, ^TWII 12.6%, ^KS11 11.0%, ETH-USD 9.4%, ^N225 9.3%, BTC-USD 9.1% |
| 2026-06-01 | GC=F 22.6%, ^TWII 16.2%, ^N225 11.6%, ^KS11 9.4%, SI=F 8.3%, ETH-USD 6.8%, CASH 25.0% |
| 2026-07-01 | GC=F 14.5%, VWO 13.3%, ^N225 9.7%, CASH 62.5% |

## IS (selection window: FULL)

Assets with signals: 14/14

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.1596 |    0.107  |   1.4376 |  -0.07   |
| 2025 |   0.3652 |    0.1197 |   2.6838 |  -0.1065 |
| 2026 |   0.1189 |    0.1727 |   1.4093 |  -0.0927 |
| FULL |   0.7714 |    0.1273 |   1.8734 |  -0.1065 |

Annual turnover (sum of rebalance one-way): 2024: 5.86x, 2025: 5.28x, 2026: 2.82x

### Monthly holdings — IS

| date | holdings |
|---|---|
| 2024-01-02 | ^TWII 33.1%, GC=F 16.2%, ^KS11 14.8%, CL=F 8.8%, BTC-USD 5.6%, SI=F 5.5%, ETH-USD 3.6%, CASH 12.5% |
| 2024-02-01 | ^NDX 20.1%, ^KS11 13.8%, ASHR 13.1%, ^N225 11.0%, VWO 10.9%, CL=F 6.1%, CASH 25.0% |
| 2024-03-01 | ^TWII 29.8%, ^N225 18.7%, ^KS11 15.4%, GC=F 9.9%, ASHR 9.3%, ETH-USD 6.6%, CL=F 5.2%, BTC-USD 4.9% |
| 2024-04-01 | ^TWII 20.4%, ^NDX 14.7%, ^N225 11.5%, BTC-USD 3.3%, CASH 50.0% |
| 2024-05-01 | GC=F 18.2%, ^NDX 15.6%, ^GSPC 14.9%, VEA 13.9%, SI=F 12.0%, ASHR 11.9%, ^TWII 7.5%, ^KS11 5.9% |
| 2024-06-03 | ASHR 20.1%, GC=F 18.7%, VWO 18.4%, SI=F 11.1%, ^GSPC 10.2%, ^NDX 9.4%, CL=F 8.8%, ETH-USD 3.3% |
| 2024-07-01 | ^TWII 16.1%, GC=F 14.4%, SI=F 7.0%, CASH 62.5% |
| 2024-08-01 | ^GSPC 22.3%, ^NDX 15.2%, VWO 13.1%, VEA 11.2%, CL=F 8.4%, SI=F 4.8%, CASH 25.0% |
| 2024-09-03 | GC=F 19.1%, VWO 14.1%, CL=F 12.7%, ^KS11 9.8%, SI=F 9.8%, ^TWII 9.5%, CASH 25.0% |
| 2024-10-01 | GC=F 19.0%, ^KS11 16.2%, CL=F 15.9%, SI=F 11.6%, BTC-USD 8.0%, ETH-USD 4.4%, CASH 25.0% |
| 2024-11-01 | ^FTSE 18.9%, ^NDX 18.6%, VEA 18.5%, VWO 12.4%, ^GSPC 11.0%, SI=F 10.3%, CL=F 7.8%, ASHR 2.4% |
| 2024-12-02 | GC=F 20.2%, ^KS11 15.3%, VEA 13.0%, VWO 12.1%, SI=F 11.6%, CL=F 11.5%, BTC-USD 8.6%, ETH-USD 7.6% |
| 2025-01-02 | VEA 23.0%, ^NDX 18.3%, ^FTSE 15.6%, ^KS11 11.0%, GC=F 9.9%, SI=F 9.5%, ^GSPC 8.4%, ASHR 4.4% |
| 2025-02-03 | GC=F 16.1%, VWO 15.2%, ASHR 10.1%, SI=F 8.6%, CASH 50.0% |
| 2025-03-03 | GC=F 23.2%, ^GSPC 17.9%, ^NDX 15.8%, VWO 12.6%, SI=F 10.3%, ASHR 8.4%, ^KS11 6.0%, CL=F 5.9% |
| 2025-04-01 | ^FTSE 21.5%, VEA 18.8%, VWO 15.3%, ^NDX 13.0%, ^KS11 10.4%, ASHR 8.1%, ^GSPC 7.6%, ^N225 5.3% |
| 2025-05-01 | ^FTSE 24.2%, GC=F 17.8%, CL=F 15.4%, ^KS11 13.3%, SI=F 13.0%, ASHR 9.0%, ETH-USD 3.7%, BTC-USD 3.6% |
| 2025-06-02 | GC=F 21.7%, ASHR 17.7%, CL=F 13.9%, SI=F 10.5%, ^KS11 10.2%, ^GSPC 9.0%, ETH-USD 4.6%, CASH 12.5% |
| 2025-07-01 | GC=F 14.8%, ^KS11 14.4%, ^FTSE 13.9%, ^N225 12.6%, CL=F 6.7%, CASH 37.5% |
| 2025-08-01 | ASHR 20.3%, GC=F 17.0%, ^N225 16.9%, ^TWII 13.2%, ^NDX 10.6%, VEA 9.8%, SI=F 7.6%, ETH-USD 4.6% |
| 2025-09-02 | ^NDX 24.3%, ^N225 15.6%, ^TWII 12.6%, CL=F 7.3%, ETH-USD 2.7%, CASH 37.5% |
| 2025-10-01 | ^GSPC 17.2%, ^TWII 13.7%, ^N225 12.6%, CL=F 6.5%, CASH 50.0% |
| 2025-11-03 | ^TWII 18.8%, ASHR 16.0%, ^KS11 12.4%, GC=F 12.1%, ^N225 8.8%, SI=F 6.9%, CASH 25.0% |
| 2025-12-01 | VWO 17.3%, ^GSPC 17.2%, ^TWII 16.0%, CL=F 10.1%, GC=F 7.8%, ^N225 6.7%, CASH 25.0% |
| 2026-01-02 | ^TWII 21.9%, ^NDX 17.8%, ASHR 15.1%, GC=F 11.3%, CL=F 8.2%, ^N225 7.1%, SI=F 6.2%, CASH 12.5% |
| 2026-02-02 | ASHR 25.6%, ^NDX 16.1%, VWO 13.2%, ^TWII 10.3%, GC=F 9.4%, ^KS11 9.0%, SI=F 3.9%, CASH 12.5% |
| 2026-03-02 | ASHR 20.9%, ^TWII 18.9%, ^GSPC 17.9%, ^N225 13.2%, ^NDX 8.9%, VWO 8.2%, GC=F 6.3%, ^KS11 5.7% |
| 2026-04-01 | ^GSPC 22.7%, ^NDX 21.9%, ^FTSE 17.4%, VWO 14.1%, VEA 10.4%, GC=F 8.9%, ^KS11 2.5%, ETH-USD 2.2% |
| 2026-05-01 | ^TWII 16.3%, VEA 16.0%, ^FTSE 15.9%, GC=F 13.5%, BTC-USD 10.6%, ^N225 9.5%, ETH-USD 5.6%, CASH 12.5% |
| 2026-06-01 | GC=F 18.0%, ^TWII 17.6%, ^FTSE 14.5%, ^N225 13.4%, ^GSPC 12.9%, VWO 12.7%, SI=F 6.3%, CL=F 4.6% |
| 2026-07-01 | VWO 18.8%, GC=F 18.6%, ^TWII 16.8%, ^N225 10.9%, SI=F 6.0%, CL=F 3.8%, CASH 25.0% |

## Benchmark: equal-weight buy & hold

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.2381 |    0.1557 |   1.4502 |  -0.1271 |
| 2025 |   0.2888 |    0.1622 |   1.6585 |  -0.1742 |
| 2026 |   0.1142 |    0.2433 |   1.026  |  -0.1257 |
| FULL |   0.7779 |    0.1785 |   1.3879 |  -0.1785 |
