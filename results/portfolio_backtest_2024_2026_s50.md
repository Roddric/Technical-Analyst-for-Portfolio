# Portfolio backtest 2024-2026 — pandas_ta composite sets

> Long-only, top-8 by signal, signal-tilted inverse-vol weights; assets with a non-positive composite signal among the top 8 are replaced by cash at 0% (freed weight sits in cash, not reinvested elsewhere). Monthly rebalance, 5 bps/side, rf=0. Turnover-smoothed: each rebalance moves only 50% of the way from current to target weights (entries/exits fade over several rebalances; blended weights < 0.5% cut to cash). 2026 is partial (YTD). Index/FX assets traded as proxies. FULL variant is IN-SAMPLE (upper bound), OOS variant selected sets on data <= 2023-12-31.

## OOS (selection window: 2023-12-31)

Assets with signals: 14/14

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.0693 |    0.0719 |   0.9678 |  -0.0552 |
| 2025 |   0.3171 |    0.1148 |   2.4768 |  -0.1162 |
| 2026 |   0.1251 |    0.1608 |   1.5709 |  -0.0751 |
| FULL |   0.5845 |    0.1116 |   1.7168 |  -0.1162 |

Annual turnover (sum of rebalance one-way): 2024: 2.43x, 2025: 2.43x, 2026: 1.48x

### Monthly holdings — OOS

| date | holdings |
|---|---|
| 2024-01-02 | ^TWII 19.2%, ^KS11 14.9%, SI=F 9.5%, CL=F 6.4%, CASH 50.0% |
| 2024-02-01 | ^KS11 10.7%, ^TWII 9.7%, ^NDX 9.2%, ^GSPC 8.8%, ASHR 6.7%, ^N225 6.6%, CL=F 5.8%, SI=F 4.6%, CASH 37.7% |
| 2024-03-01 | ^TWII 16.1%, ^N225 12.3%, ^KS11 11.7%, ASHR 8.8%, ^NDX 4.7%, ^GSPC 4.5%, ETH-USD 3.1%, BTC-USD 3.0%, CL=F 2.9%, SI=F 2.2%, CASH 30.7% |
| 2024-04-01 | ^KS11 14.1%, ^N225 12.6%, ^NDX 11.5%, ASHR 10.2%, ^TWII 8.3%, BTC-USD 3.1%, ^GSPC 2.2%, ETH-USD 1.6%, CL=F 1.5%, SI=F 1.2%, CASH 33.7% |
| 2024-05-01 | ^NDX 11.6%, ^KS11 11.3%, ^GSPC 10.4%, VEA 8.3%, ^N225 6.1%, ASHR 5.3%, ^TWII 4.3%, SI=F 3.9%, BTC-USD 1.3%, CL=F 0.8%, ETH-USD 0.7%, CASH 35.9% |
| 2024-06-03 | ASHR 13.0%, VWO 10.0%, GC=F 6.7%, SI=F 6.4%, ^NDX 6.0%, ^KS11 5.4%, ^GSPC 5.3%, CL=F 4.5%, VEA 4.3%, ^N225 3.0%, ETH-USD 2.4%, ^TWII 2.2%, BTC-USD 0.7%, CASH 30.0% |
| 2024-07-01 | ASHR 13.2%, ^GSPC 9.9%, ^NDX 8.9%, ^TWII 6.4%, VWO 5.1%, GC=F 3.3%, SI=F 3.1%, ^KS11 2.8%, CL=F 2.4%, VEA 2.1%, ^N225 1.5%, ETH-USD 1.1%, CASH 40.3% |
| 2024-08-01 | ^NDX 11.6%, ^KS11 8.4%, ASHR 6.7%, CL=F 5.6%, ^GSPC 5.0%, ^TWII 3.1%, VWO 2.6%, GC=F 1.7%, SI=F 1.5%, VEA 1.1%, ^N225 0.8%, ETH-USD 0.5%, CASH 51.4% |
| 2024-09-03 | ^KS11 10.1%, VWO 9.5%, GC=F 7.3%, CL=F 7.0%, ^NDX 5.9%, ASHR 3.3%, ^GSPC 2.6%, ^TWII 1.5%, SI=F 0.8%, VEA 0.6%, CASH 51.4% |
| 2024-10-01 | VWO 13.2%, ^KS11 11.1%, CL=F 9.3%, VEA 8.0%, GC=F 3.8%, BTC-USD 3.1%, ^NDX 3.0%, ASHR 2.0%, ^GSPC 1.3%, ^TWII 0.8%, CASH 44.5% |
| 2024-11-01 | VEA 13.2%, ^FTSE 11.5%, VWO 11.1%, ^GSPC 11.0%, ^NDX 9.8%, CL=F 7.4%, ^KS11 5.5%, ASHR 2.3%, GC=F 2.0%, BTC-USD 1.7%, SI=F 1.7%, CASH 22.7% |
| 2024-12-02 | VEA 18.4%, CL=F 9.2%, SI=F 6.5%, BTC-USD 5.8%, ^FTSE 5.8%, ^GSPC 5.8%, VWO 5.4%, ^NDX 5.1%, ETH-USD 3.4%, ^KS11 2.6%, ASHR 1.2%, GC=F 0.9%, CASH 30.0% |
| 2025-01-02 | VEA 21.2%, ^FTSE 13.6%, ^GSPC 11.4%, ^NDX 9.6%, SI=F 8.1%, CL=F 6.9%, ^N225 3.0%, BTC-USD 2.8%, VWO 2.7%, ASHR 2.1%, ETH-USD 1.6%, ^KS11 1.3%, CASH 15.7% |
| 2025-02-03 | VEA 20.6%, ^GSPC 13.4%, CL=F 7.0%, ^FTSE 7.0%, VWO 6.9%, ASHR 5.3%, ^NDX 4.8%, SI=F 4.3%, BTC-USD 1.5%, ^N225 1.5%, ETH-USD 0.8%, ^KS11 0.7%, CASH 26.3% |
| 2025-03-03 | VWO 13.5%, ^NDX 11.3%, ^GSPC 11.0%, VEA 10.6%, ASHR 9.1%, GC=F 7.4%, CL=F 7.1%, SI=F 6.8%, ^N225 5.3%, ^FTSE 3.6%, BTC-USD 0.6%, CASH 13.8% |
| 2025-04-01 | VEA 16.1%, VWO 12.9%, ^FTSE 12.9%, ^NDX 11.3%, ASHR 11.0%, ^GSPC 10.0%, GC=F 4.1%, ^KS11 3.7%, SI=F 3.7%, CL=F 3.6%, ^N225 2.6%, ETH-USD 0.8%, CASH 7.2% |
| 2025-05-01 | ^FTSE 18.7%, VEA 14.5%, CL=F 10.3%, SI=F 10.0%, VWO 6.5%, ^KS11 6.0%, ^NDX 5.8%, ASHR 5.4%, ^GSPC 5.0%, ^TWII 4.9%, ETH-USD 3.2%, BTC-USD 2.7%, GC=F 2.2%, ^N225 1.3%, CASH 3.6% |
| 2025-06-02 | CL=F 11.9%, GC=F 11.7%, ASHR 11.3%, ^FTSE 9.2%, VWO 8.7%, ^KS11 8.0%, ^TWII 7.6%, VEA 7.2%, SI=F 4.8%, ETH-USD 4.1%, ^NDX 3.0%, ^GSPC 2.5%, BTC-USD 1.4%, ^N225 0.6%, CASH 8.0% |
| 2025-07-01 | ^KS11 14.3%, GC=F 12.1%, ^FTSE 11.0%, CL=F 10.9%, ^TWII 7.7%, ^N225 6.1%, ASHR 5.7%, VWO 4.4%, VEA 3.6%, SI=F 2.5%, ETH-USD 1.9%, ^NDX 1.5%, ^GSPC 1.3%, BTC-USD 0.7%, CASH 16.3% |
| 2025-08-01 | GC=F 13.9%, ASHR 12.4%, ^N225 11.0%, ^KS11 11.0%, ^TWII 9.2%, ^NDX 8.0%, VEA 7.7%, CL=F 5.6%, ^FTSE 5.5%, ETH-USD 3.6%, VWO 2.1%, SI=F 1.2%, ^GSPC 0.6%, CASH 8.2% |
| 2025-09-02 | ^N225 13.0%, ^NDX 12.5%, GC=F 7.1%, ASHR 6.7%, ^KS11 5.2%, CL=F 5.1%, ^TWII 4.6%, VEA 3.9%, ^FTSE 2.7%, ETH-USD 2.0%, VWO 1.1%, SI=F 0.7%, CASH 35.5% |
| 2025-10-01 | ^N225 14.8%, ^KS11 9.5%, ^NDX 6.4%, CL=F 6.2%, GC=F 3.8%, ASHR 3.4%, ^TWII 2.4%, VEA 1.9%, ^FTSE 1.3%, ETH-USD 0.9%, VWO 0.5%, CASH 48.8% |
| 2025-11-03 | ^KS11 16.2%, ^N225 14.7%, GC=F 9.2%, ASHR 8.6%, ^TWII 7.1%, CL=F 5.9%, SI=F 3.2%, ^NDX 3.2%, VEA 0.9%, ^FTSE 0.7%, CASH 30.2% |
| 2025-12-01 | ^N225 13.5%, CL=F 9.0%, ^KS11 7.8%, GC=F 4.9%, ASHR 4.3%, ^TWII 3.5%, SI=F 1.9%, ^NDX 1.6%, CASH 53.5% |
| 2026-01-02 | ^N225 11.2%, ASHR 10.8%, ^NDX 10.4%, GC=F 8.8%, ^TWII 8.7%, CL=F 4.4%, ^KS11 4.1%, SI=F 2.7%, CASH 38.9% |
| 2026-02-02 | ASHR 14.6%, ^NDX 13.4%, ^KS11 9.2%, VWO 8.7%, GC=F 7.4%, ^N225 5.7%, ^TWII 4.6%, SI=F 3.1%, CL=F 2.4%, CASH 31.1% |
| 2026-03-02 | ^TWII 13.1%, ^KS11 12.0%, VWO 10.9%, ^N225 10.3%, ^GSPC 9.5%, ASHR 7.1%, ^NDX 6.3%, GC=F 3.9%, SI=F 3.1%, ETH-USD 1.6%, CL=F 1.2%, CASH 21.1% |
| 2026-04-01 | ^NDX 17.2%, ^FTSE 12.9%, VWO 9.7%, VEA 7.8%, GC=F 6.9%, ^TWII 6.3%, ^KS11 5.2%, ^GSPC 4.8%, ^N225 4.8%, ETH-USD 3.8%, ASHR 3.7%, CL=F 2.7%, SI=F 2.6%, CASH 11.4% |
| 2026-05-01 | VWO 14.5%, ^FTSE 13.4%, GC=F 10.4%, ^TWII 9.8%, ^NDX 9.1%, ^KS11 8.6%, ^N225 7.2%, ETH-USD 6.6%, BTC-USD 4.5%, VEA 3.9%, ^GSPC 2.4%, ASHR 1.8%, CL=F 1.3%, SI=F 1.2%, CASH 5.2% |
| 2026-06-01 | GC=F 16.1%, ^TWII 13.5%, ^KS11 10.0%, ^N225 9.7%, VWO 7.0%, ^FTSE 6.4%, ETH-USD 6.2%, ^NDX 4.8%, SI=F 4.7%, BTC-USD 2.1%, VEA 1.9%, ^GSPC 1.2%, ASHR 0.9%, CL=F 0.5%, CASH 15.0% |
| 2026-07-01 | GC=F 14.7%, VWO 10.3%, ^N225 10.2%, ^TWII 7.2%, ^KS11 5.2%, ^FTSE 3.4%, ETH-USD 2.5%, ^NDX 2.5%, SI=F 1.9%, VEA 1.0%, BTC-USD 0.9%, ^GSPC 0.6%, CASH 39.7% |

## IS (selection window: FULL)

Assets with signals: 14/14

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.1678 |    0.0962 |   1.6607 |  -0.0675 |
| 2025 |   0.3628 |    0.1101 |   2.8908 |  -0.1029 |
| 2026 |   0.1735 |    0.161  |   2.1019 |  -0.0773 |
| FULL |   0.8677 |    0.1169 |   2.2103 |  -0.1029 |

Annual turnover (sum of rebalance one-way): 2024: 2.79x, 2025: 2.44x, 2026: 1.37x

### Monthly holdings — IS

| date | holdings |
|---|---|
| 2024-01-02 | ^TWII 33.1%, GC=F 16.2%, ^KS11 14.8%, CL=F 8.8%, BTC-USD 5.6%, SI=F 5.5%, ETH-USD 3.6%, CASH 12.5% |
| 2024-02-01 | ^TWII 16.6%, ^KS11 13.9%, ^NDX 10.1%, GC=F 8.1%, CL=F 7.7%, ASHR 6.6%, ^N225 5.5%, VWO 5.5%, BTC-USD 2.9%, SI=F 2.7%, ETH-USD 1.8%, CASH 18.8% |
| 2024-03-01 | ^TWII 23.2%, ^KS11 14.7%, ^N225 12.2%, GC=F 8.8%, ASHR 8.0%, CL=F 6.4%, ^NDX 5.0%, ETH-USD 4.5%, BTC-USD 4.4%, VWO 2.7%, SI=F 1.2%, CASH 8.9% |
| 2024-04-01 | ^TWII 22.0%, ^N225 11.7%, ^NDX 9.8%, ^KS11 7.3%, GC=F 4.5%, BTC-USD 4.1%, ASHR 3.8%, CL=F 3.2%, ETH-USD 2.3%, VWO 1.3%, SI=F 0.6%, CASH 29.2% |
| 2024-05-01 | ^TWII 15.1%, ^NDX 12.6%, GC=F 11.5%, ASHR 7.9%, ^GSPC 7.5%, VEA 7.0%, ^KS11 6.6%, SI=F 6.4%, ^N225 5.7%, BTC-USD 1.8%, CL=F 1.6%, ETH-USD 1.0%, VWO 0.7%, CASH 14.8% |
| 2024-06-03 | GC=F 15.0%, ASHR 13.9%, ^NDX 11.2%, VWO 9.5%, SI=F 9.1%, ^GSPC 8.9%, ^TWII 7.6%, CL=F 5.1%, VEA 3.5%, ^KS11 3.1%, ^N225 2.8%, ETH-USD 2.3%, BTC-USD 1.0%, CASH 7.2% |
| 2024-07-01 | GC=F 14.6%, ^TWII 12.1%, SI=F 7.8%, ASHR 6.6%, ^NDX 5.9%, VWO 4.8%, ^GSPC 4.5%, CL=F 2.7%, VEA 1.7%, ^KS11 1.6%, ^N225 1.4%, ETH-USD 1.0%, CASH 35.2% |
| 2024-08-01 | ^GSPC 13.4%, ^NDX 10.5%, VWO 9.0%, GC=F 7.6%, VEA 6.5%, SI=F 6.2%, ^TWII 5.8%, CL=F 5.5%, ASHR 3.4%, ^KS11 0.8%, ^N225 0.7%, CASH 30.6% |
| 2024-09-03 | GC=F 13.4%, VWO 11.5%, CL=F 9.0%, SI=F 8.0%, ^TWII 7.6%, ^GSPC 6.8%, ^KS11 5.3%, ^NDX 5.3%, VEA 3.3%, ASHR 1.6%, CASH 28.1% |
| 2024-10-01 | GC=F 16.5%, CL=F 12.0%, ^KS11 10.6%, SI=F 10.0%, VWO 6.1%, BTC-USD 4.0%, ^TWII 3.7%, ^GSPC 3.4%, ^NDX 2.6%, ETH-USD 2.2%, VEA 1.6%, ASHR 1.0%, CASH 26.2% |
| 2024-11-01 | ^NDX 10.6%, SI=F 10.3%, VEA 10.0%, CL=F 9.9%, ^FTSE 9.5%, VWO 9.1%, GC=F 8.4%, ^GSPC 7.2%, ^KS11 5.2%, BTC-USD 2.2%, ^TWII 1.9%, ASHR 1.7%, ETH-USD 1.0%, CASH 13.0% |
| 2024-12-02 | GC=F 14.2%, VEA 11.5%, SI=F 10.6%, CL=F 10.6%, VWO 10.5%, ^KS11 10.1%, BTC-USD 5.8%, ^NDX 5.5%, ^FTSE 4.8%, ETH-USD 4.5%, ^GSPC 3.8%, ^TWII 0.9%, ASHR 0.8%, CASH 6.4% |
| 2025-01-02 | VEA 17.1%, GC=F 12.1%, ^NDX 12.0%, ^KS11 10.5%, ^FTSE 10.2%, SI=F 9.8%, ^GSPC 6.1%, CL=F 5.7%, VWO 5.3%, BTC-USD 2.8%, ASHR 2.6%, ETH-USD 2.1%, CASH 3.7% |
| 2025-02-03 | GC=F 14.2%, VWO 10.2%, SI=F 9.5%, VEA 8.5%, ASHR 6.3%, ^NDX 5.9%, ^KS11 5.3%, ^FTSE 5.2%, ^GSPC 3.0%, CL=F 2.7%, BTC-USD 1.5%, ETH-USD 1.0%, CASH 26.8% |
| 2025-03-03 | GC=F 18.8%, VWO 11.4%, ^NDX 10.8%, ^GSPC 10.4%, SI=F 9.8%, ASHR 7.4%, ^KS11 5.7%, VEA 4.4%, CL=F 4.3%, ^FTSE 2.6%, BTC-USD 0.6%, CASH 13.8% |
| 2025-04-01 | VWO 13.3%, ^FTSE 12.0%, VEA 11.6%, ^NDX 11.4%, GC=F 10.2%, ^GSPC 8.7%, ^KS11 7.9%, ASHR 7.7%, SI=F 5.3%, ^N225 2.6%, CL=F 2.1%, CASH 7.1% |
| 2025-05-01 | ^FTSE 18.0%, GC=F 14.3%, ^KS11 10.7%, SI=F 9.0%, CL=F 8.6%, ASHR 8.2%, VWO 6.6%, VEA 6.0%, ^NDX 5.8%, ^GSPC 4.3%, ETH-USD 1.8%, BTC-USD 1.8%, ^N225 1.3%, CASH 3.5% |
| 2025-06-02 | GC=F 17.7%, ASHR 12.9%, CL=F 11.3%, ^KS11 10.5%, SI=F 9.6%, ^FTSE 8.9%, ^GSPC 6.7%, ETH-USD 3.5%, VWO 3.3%, VEA 3.0%, ^NDX 3.0%, BTC-USD 1.0%, ^N225 0.7%, CASH 7.9% |
| 2025-07-01 | GC=F 15.9%, ^KS11 13.0%, ^FTSE 11.2%, CL=F 9.1%, ^N225 6.7%, ASHR 6.4%, SI=F 5.0%, ^GSPC 3.3%, VWO 1.7%, ETH-USD 1.7%, ^NDX 1.5%, VEA 1.5%, CASH 23.0% |
| 2025-08-01 | GC=F 16.2%, ASHR 13.4%, ^N225 11.7%, ^KS11 6.6%, ^TWII 6.6%, SI=F 6.2%, ^NDX 6.1%, ^FTSE 5.7%, VEA 5.6%, CL=F 4.7%, ETH-USD 3.5%, ^GSPC 1.7%, VWO 0.8%, CASH 11.2% |
| 2025-09-02 | ^NDX 15.1%, ^N225 13.6%, ^TWII 9.6%, GC=F 8.2%, ASHR 7.2%, CL=F 5.7%, ETH-USD 3.3%, SI=F 3.3%, ^KS11 3.1%, VEA 2.8%, ^FTSE 2.7%, ^GSPC 0.8%, CASH 24.5% |
| 2025-10-01 | ^N225 13.2%, ^TWII 11.7%, ^GSPC 9.0%, ^NDX 7.7%, CL=F 6.0%, GC=F 4.4%, ASHR 3.6%, SI=F 1.8%, ^KS11 1.6%, ETH-USD 1.5%, VEA 1.4%, ^FTSE 1.3%, CASH 36.8% |
| 2025-11-03 | ^TWII 15.6%, ^N225 11.8%, ASHR 9.7%, GC=F 8.2%, ^KS11 7.1%, ^GSPC 4.4%, SI=F 4.4%, ^NDX 3.8%, CL=F 2.8%, VEA 0.7%, ETH-USD 0.7%, ^FTSE 0.7%, CASH 30.1% |
| 2025-12-01 | ^TWII 15.6%, ^GSPC 10.8%, ^N225 9.0%, VWO 8.6%, GC=F 8.2%, CL=F 6.4%, ASHR 4.8%, ^KS11 3.4%, SI=F 2.6%, ^NDX 1.9%, CASH 28.6% |
| 2026-01-02 | ^TWII 19.0%, ASHR 10.0%, ^NDX 9.8%, GC=F 9.8%, ^N225 8.0%, CL=F 7.2%, ^GSPC 5.3%, SI=F 4.7%, VWO 4.3%, ^KS11 1.8%, CASH 20.3% |
| 2026-02-02 | ASHR 17.6%, ^TWII 15.1%, ^NDX 12.7%, GC=F 9.7%, VWO 8.7%, ^KS11 5.6%, SI=F 4.4%, ^N225 4.0%, CL=F 3.8%, ^GSPC 2.5%, CASH 15.8% |
| 2026-03-02 | ASHR 19.0%, ^TWII 17.3%, ^NDX 10.4%, ^GSPC 10.2%, ^N225 8.7%, VWO 8.4%, GC=F 8.3%, ^KS11 6.0%, SI=F 2.5%, CL=F 1.9%, CASH 7.5% |
| 2026-04-01 | ^GSPC 16.5%, ^NDX 16.2%, VWO 11.2%, ASHR 9.8%, ^FTSE 8.7%, GC=F 8.4%, ^TWII 8.3%, VEA 5.2%, ^N225 4.1%, ^KS11 3.9%, CL=F 1.5%, ETH-USD 1.1%, SI=F 1.1%, CASH 4.0% |
| 2026-05-01 | ^TWII 12.8%, ^FTSE 12.0%, VEA 10.5%, GC=F 10.5%, ^NDX 8.5%, ^GSPC 8.3%, ^N225 6.9%, VWO 5.5%, BTC-USD 5.3%, ASHR 4.8%, ETH-USD 3.3%, ^KS11 2.3%, CL=F 0.7%, CASH 8.6% |
| 2026-06-01 | ^TWII 15.9%, GC=F 13.9%, ^FTSE 13.0%, ^GSPC 10.6%, ^N225 10.4%, VWO 9.0%, VEA 5.3%, ^NDX 4.5%, SI=F 3.2%, CL=F 2.6%, BTC-USD 2.4%, ASHR 2.3%, ETH-USD 1.4%, ^KS11 1.4%, CASH 4.1% |
| 2026-07-01 | ^TWII 16.8%, GC=F 15.6%, VWO 14.0%, ^N225 11.1%, ^FTSE 6.7%, ^GSPC 5.4%, SI=F 4.3%, CL=F 3.0%, VEA 2.7%, ^NDX 2.3%, ASHR 1.2%, BTC-USD 1.0%, ^KS11 0.7%, ETH-USD 0.6%, CASH 14.6% |

## Benchmark: equal-weight buy & hold

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.2381 |    0.1557 |   1.4502 |  -0.1271 |
| 2025 |   0.2888 |    0.1622 |   1.6585 |  -0.1742 |
| 2026 |   0.1142 |    0.2433 |   1.026  |  -0.1257 |
| FULL |   0.7779 |    0.1785 |   1.3879 |  -0.1785 |
