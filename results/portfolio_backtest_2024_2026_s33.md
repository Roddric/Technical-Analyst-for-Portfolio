# Portfolio backtest 2024-2026 — pandas_ta composite sets

> Long-only, top-8 by signal, signal-tilted inverse-vol weights; assets with a non-positive composite signal among the top 8 are replaced by cash at 0% (freed weight sits in cash, not reinvested elsewhere). Monthly rebalance, 5 bps/side, rf=0. Turnover-smoothed: each rebalance moves only 33% of the way from current to target weights (entries/exits fade over several rebalances; blended weights < 0.5% cut to cash). 2026 is partial (YTD). Index/FX assets traded as proxies. FULL variant is IN-SAMPLE (upper bound), OOS variant selected sets on data <= 2023-12-31.

## OOS (selection window: 2023-12-31)

Assets with signals: 14/14

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.0732 |    0.0716 |   1.0227 |  -0.0619 |
| 2025 |   0.2998 |    0.1105 |   2.4479 |  -0.1146 |
| 2026 |   0.1571 |    0.156  |   1.9796 |  -0.064  |
| FULL |   0.6142 |    0.1085 |   1.8323 |  -0.1146 |

Annual turnover (sum of rebalance one-way): 2024: 1.70x, 2025: 1.64x, 2026: 0.98x

### Monthly holdings — OOS

| date | holdings |
|---|---|
| 2024-01-02 | ^TWII 19.2%, ^KS11 14.9%, SI=F 9.5%, CL=F 6.4%, CASH 50.0% |
| 2024-02-01 | ^TWII 12.9%, ^KS11 11.9%, CL=F 6.2%, ^NDX 6.2%, SI=F 6.1%, ^GSPC 5.9%, ASHR 4.5%, ^N225 4.4%, CASH 42.0% |
| 2024-03-01 | ^TWII 16.3%, ^KS11 12.3%, ^N225 9.0%, ASHR 6.6%, ^NDX 4.2%, CL=F 4.1%, ^GSPC 4.0%, SI=F 3.9%, ETH-USD 2.1%, BTC-USD 2.0%, CASH 35.5% |
| 2024-04-01 | ^KS11 13.8%, ^TWII 11.2%, ^N225 10.3%, ^NDX 8.9%, ASHR 8.2%, CL=F 2.8%, SI=F 2.8%, ^GSPC 2.7%, BTC-USD 2.4%, ETH-USD 1.4%, CASH 35.5% |
| 2024-05-01 | ^KS11 11.9%, ^NDX 9.7%, ^GSPC 8.0%, ^TWII 7.7%, ^N225 6.6%, ASHR 5.7%, VEA 5.6%, SI=F 4.2%, CL=F 1.9%, BTC-USD 1.4%, ETH-USD 0.8%, CASH 36.5% |
| 2024-06-03 | ASHR 10.7%, ^KS11 7.6%, ^NDX 6.8%, VWO 6.7%, SI=F 6.0%, ^GSPC 5.4%, ^TWII 5.2%, GC=F 4.5%, ^N225 4.3%, CL=F 3.9%, VEA 3.8%, ETH-USD 2.0%, BTC-USD 1.0%, CASH 32.1% |
| 2024-07-01 | ASHR 11.4%, ^NDX 8.5%, ^GSPC 8.5%, ^TWII 7.2%, ^KS11 5.3%, VWO 4.5%, SI=F 3.8%, GC=F 3.0%, ^N225 3.0%, CL=F 2.7%, VEA 2.5%, ETH-USD 1.2%, BTC-USD 0.6%, CASH 37.9% |
| 2024-08-01 | ^NDX 10.5%, ^KS11 8.2%, ASHR 7.7%, ^GSPC 5.7%, CL=F 4.8%, ^TWII 4.6%, VWO 3.0%, SI=F 2.5%, GC=F 2.1%, ^N225 1.9%, VEA 1.7%, ETH-USD 0.8%, CASH 46.5% |
| 2024-09-03 | ^KS11 9.3%, VWO 7.5%, ^NDX 7.1%, CL=F 5.9%, GC=F 5.7%, ASHR 5.1%, ^GSPC 3.9%, ^TWII 3.1%, SI=F 1.7%, ^N225 1.3%, VEA 1.2%, CASH 48.2% |
| 2024-10-01 | VWO 10.7%, ^KS11 10.1%, CL=F 7.7%, VEA 5.9%, ^NDX 4.8%, ASHR 4.1%, GC=F 3.9%, ^GSPC 2.6%, BTC-USD 2.1%, ^TWII 2.0%, SI=F 1.2%, ^N225 0.8%, CASH 44.1% |
| 2024-11-01 | VWO 10.1%, VEA 10.0%, ^GSPC 8.7%, ^NDX 8.7%, ^FTSE 7.7%, CL=F 7.0%, ^KS11 6.6%, ASHR 3.5%, GC=F 2.7%, SI=F 2.0%, BTC-USD 1.5%, ^TWII 1.4%, ^N225 0.6%, CASH 29.5% |
| 2024-12-02 | VEA 14.5%, CL=F 8.3%, VWO 6.5%, ^GSPC 6.1%, ^NDX 6.0%, ^FTSE 5.2%, SI=F 5.0%, BTC-USD 4.5%, ^KS11 4.2%, ASHR 2.3%, ETH-USD 2.3%, GC=F 1.8%, ^TWII 0.9%, CASH 32.4% |
| 2025-01-02 | VEA 17.6%, ^FTSE 10.6%, ^GSPC 9.7%, ^NDX 8.8%, CL=F 7.2%, SI=F 6.5%, VWO 4.4%, BTC-USD 2.9%, ^KS11 2.8%, ASHR 2.5%, ^N225 2.0%, ETH-USD 1.4%, GC=F 1.2%, ^TWII 0.6%, CASH 21.8% |
| 2025-02-03 | VEA 18.5%, ^GSPC 11.6%, ^FTSE 7.3%, CL=F 7.1%, VWO 6.6%, ^NDX 5.8%, SI=F 4.7%, ASHR 4.5%, BTC-USD 2.1%, ^KS11 1.9%, ^N225 1.3%, ETH-USD 0.9%, GC=F 0.8%, CASH 27.0% |
| 2025-03-03 | VEA 12.7%, VWO 11.1%, ^GSPC 10.6%, ^NDX 9.8%, ASHR 7.3%, CL=F 7.1%, SI=F 6.2%, GC=F 5.5%, ^FTSE 5.0%, ^N225 3.9%, ^KS11 1.3%, BTC-USD 1.1%, CASH 18.6% |
| 2025-04-01 | VEA 15.7%, VWO 11.6%, ^FTSE 10.7%, ^NDX 10.1%, ^GSPC 9.9%, ASHR 9.2%, CL=F 4.8%, SI=F 4.5%, GC=F 4.0%, ^KS11 3.3%, ^N225 2.5%, BTC-USD 0.7%, ETH-USD 0.5%, CASH 12.4% |
| 2025-05-01 | ^FTSE 15.3%, VEA 15.0%, CL=F 8.5%, SI=F 8.4%, VWO 7.7%, ^NDX 6.9%, ^GSPC 6.6%, ASHR 6.0%, ^KS11 5.0%, ^TWII 3.3%, GC=F 2.8%, BTC-USD 2.3%, ETH-USD 2.2%, ^N225 1.7%, CASH 8.3% |
| 2025-06-02 | CL=F 10.2%, ^FTSE 10.0%, VEA 10.0%, ASHR 9.7%, GC=F 8.9%, VWO 8.8%, ^KS11 6.7%, ^TWII 5.6%, SI=F 5.4%, ^NDX 4.8%, ^GSPC 4.4%, ETH-USD 3.3%, BTC-USD 1.6%, ^N225 1.1%, CASH 9.4% |
| 2025-07-01 | ^KS11 11.5%, ^FTSE 10.8%, CL=F 10.2%, GC=F 10.0%, VEA 6.6%, ASHR 6.5%, ^TWII 6.3%, VWO 6.0%, ^N225 4.6%, SI=F 3.8%, ^NDX 3.2%, ^GSPC 3.0%, ETH-USD 2.1%, BTC-USD 1.1%, CASH 14.4% |
| 2025-08-01 | GC=F 11.8%, ASHR 10.7%, ^KS11 10.3%, ^N225 8.3%, VEA 8.2%, ^TWII 7.8%, ^FTSE 7.2%, ^NDX 7.0%, CL=F 7.0%, VWO 3.9%, ETH-USD 3.4%, SI=F 2.5%, ^GSPC 2.0%, BTC-USD 0.8%, CASH 9.2% |
| 2025-09-02 | ^N225 10.6%, ^NDX 10.3%, GC=F 8.1%, ASHR 7.8%, ^KS11 6.5%, CL=F 5.9%, VEA 5.5%, ^TWII 5.2%, ^FTSE 4.7%, ETH-USD 2.6%, VWO 2.6%, SI=F 1.7%, ^GSPC 1.3%, CASH 27.3% |
| 2025-10-01 | ^N225 12.6%, ^KS11 9.0%, ^NDX 7.0%, CL=F 6.2%, GC=F 5.7%, ASHR 5.2%, VEA 3.6%, ^TWII 3.6%, ^FTSE 3.1%, VWO 1.8%, ETH-USD 1.6%, SI=F 1.3%, ^GSPC 0.9%, CASH 38.4% |
| 2025-11-03 | ^KS11 14.1%, ^N225 13.7%, GC=F 8.7%, ASHR 7.9%, ^TWII 6.4%, CL=F 5.9%, ^NDX 4.7%, SI=F 3.0%, VEA 2.4%, ^FTSE 2.0%, VWO 1.1%, ETH-USD 0.9%, ^GSPC 0.6%, CASH 28.6% |
| 2025-12-01 | ^N225 13.1%, ^KS11 9.1%, CL=F 7.9%, GC=F 6.2%, ASHR 5.3%, ^TWII 4.2%, ^NDX 3.1%, SI=F 2.4%, VEA 1.6%, ^FTSE 1.4%, VWO 0.8%, ETH-USD 0.5%, CASH 44.6% |
| 2026-01-02 | ^N225 11.6%, ASHR 9.3%, ^NDX 8.4%, GC=F 8.3%, ^TWII 7.5%, ^KS11 6.4%, CL=F 5.1%, SI=F 3.0%, VEA 1.1%, ^FTSE 0.9%, CASH 38.4% |
| 2026-02-02 | ASHR 12.2%, ^NDX 11.0%, ^KS11 9.5%, ^N225 7.8%, GC=F 7.6%, VWO 5.8%, ^TWII 5.2%, CL=F 3.7%, SI=F 3.2%, VEA 0.7%, ^FTSE 0.6%, CASH 32.7% |
| 2026-03-02 | ^KS11 11.7%, ^TWII 10.8%, ^N225 10.4%, VWO 8.2%, ASHR 7.9%, ^NDX 6.8%, ^GSPC 6.3%, GC=F 5.4%, SI=F 3.3%, CL=F 2.4%, ETH-USD 1.0%, CASH 25.8% |
| 2026-04-01 | ^NDX 14.0%, ^FTSE 8.6%, VWO 8.2%, ^TWII 6.9%, GC=F 6.8%, ^KS11 6.7%, ^N225 6.4%, ASHR 5.4%, VEA 5.2%, ^GSPC 4.3%, CL=F 3.7%, ETH-USD 2.8%, SI=F 2.7%, CASH 18.4% |
| 2026-05-01 | VWO 12.0%, ^FTSE 10.3%, ^NDX 9.8%, ^TWII 9.3%, ^KS11 9.0%, GC=F 8.9%, ^N225 7.6%, ETH-USD 4.9%, ASHR 3.6%, VEA 3.4%, BTC-USD 3.0%, ^GSPC 2.9%, CL=F 2.4%, SI=F 1.6%, CASH 11.2% |
| 2026-06-01 | GC=F 13.1%, ^TWII 12.2%, ^KS11 10.5%, ^N225 9.3%, VWO 7.7%, ^NDX 6.9%, ^FTSE 6.5%, ETH-USD 5.1%, SI=F 3.8%, ASHR 2.3%, VEA 2.3%, ^GSPC 1.9%, BTC-USD 1.8%, CL=F 1.2%, CASH 15.4% |
| 2026-07-01 | GC=F 12.8%, ^N225 10.0%, VWO 9.7%, ^TWII 8.7%, ^KS11 7.2%, ^NDX 4.7%, ^FTSE 4.5%, ETH-USD 2.7%, SI=F 2.1%, ASHR 1.6%, VEA 1.6%, ^GSPC 1.3%, BTC-USD 1.0%, CL=F 0.7%, CASH 31.4% |

## IS (selection window: FULL)

Assets with signals: 14/14

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.1741 |    0.0979 |   1.689  |  -0.0777 |
| 2025 |   0.3501 |    0.1088 |   2.8359 |  -0.1048 |
| 2026 |   0.1921 |    0.1601 |   2.3111 |  -0.0684 |
| FULL |   0.8896 |    0.1168 |   2.2529 |  -0.1048 |

Annual turnover (sum of rebalance one-way): 2024: 1.99x, 2025: 1.63x, 2026: 0.93x

### Monthly holdings — IS

| date | holdings |
|---|---|
| 2024-01-02 | ^TWII 33.1%, GC=F 16.2%, ^KS11 14.8%, CL=F 8.8%, BTC-USD 5.6%, SI=F 5.5%, ETH-USD 3.6%, CASH 12.5% |
| 2024-02-01 | ^TWII 22.1%, ^KS11 13.9%, GC=F 10.8%, CL=F 8.3%, ^NDX 6.7%, ASHR 4.4%, BTC-USD 3.8%, ^N225 3.7%, VWO 3.6%, SI=F 3.6%, ETH-USD 2.4%, CASH 16.7% |
| 2024-03-01 | ^TWII 24.7%, ^KS11 14.4%, GC=F 10.1%, ^N225 8.7%, CL=F 7.1%, ASHR 6.1%, BTC-USD 5.1%, ^NDX 4.4%, ETH-USD 4.4%, VWO 2.4%, SI=F 2.2%, CASH 10.5% |
| 2024-04-01 | ^TWII 23.4%, ^N225 9.5%, ^KS11 9.5%, ^NDX 7.8%, GC=F 6.9%, BTC-USD 4.8%, CL=F 4.8%, ASHR 3.9%, ETH-USD 3.0%, VWO 1.5%, SI=F 1.5%, CASH 23.3% |
| 2024-05-01 | ^TWII 18.6%, GC=F 10.9%, ^NDX 10.2%, ^KS11 8.3%, ASHR 6.6%, ^N225 6.2%, SI=F 5.1%, ^GSPC 5.0%, VEA 4.6%, CL=F 3.2%, BTC-USD 2.8%, ETH-USD 1.7%, VWO 1.0%, CASH 15.8% |
| 2024-06-03 | GC=F 13.4%, ^TWII 12.5%, ASHR 11.0%, ^NDX 10.2%, SI=F 7.5%, VWO 6.8%, ^GSPC 6.8%, ^KS11 5.2%, CL=F 4.9%, ^N225 4.0%, VEA 3.1%, ETH-USD 2.5%, BTC-USD 2.0%, CASH 10.2% |
| 2024-07-01 | ^TWII 14.3%, GC=F 13.6%, ^NDX 7.1%, SI=F 7.1%, ASHR 7.0%, ^GSPC 4.6%, VWO 4.6%, ^KS11 3.6%, CL=F 3.4%, ^N225 2.7%, VEA 2.0%, ETH-USD 1.5%, BTC-USD 1.2%, CASH 27.5% |
| 2024-08-01 | ^GSPC 10.5%, ^NDX 9.7%, GC=F 9.4%, ^TWII 9.2%, VWO 7.4%, SI=F 6.2%, VEA 5.1%, CL=F 5.0%, ASHR 4.7%, ^KS11 2.4%, ^N225 1.8%, ETH-USD 0.9%, BTC-USD 0.8%, CASH 26.7% |
| 2024-09-03 | GC=F 12.8%, VWO 9.7%, ^TWII 9.3%, SI=F 7.4%, CL=F 7.4%, ^GSPC 7.2%, ^NDX 6.5%, ^KS11 4.8%, VEA 3.5%, ASHR 3.1%, ^N225 1.2%, BTC-USD 0.5%, CASH 26.6% |
| 2024-10-01 | GC=F 15.2%, CL=F 9.7%, SI=F 9.1%, ^KS11 8.4%, VWO 6.8%, ^TWII 6.0%, ^GSPC 4.8%, ^NDX 4.4%, BTC-USD 3.0%, ASHR 2.4%, VEA 2.3%, ETH-USD 1.4%, ^N225 0.7%, CASH 25.7% |
| 2024-11-01 | GC=F 10.4%, SI=F 9.7%, CL=F 9.1%, ^NDX 9.0%, VWO 8.5%, VEA 7.6%, ^GSPC 6.8%, ^FTSE 6.3%, ^KS11 5.5%, ^TWII 4.1%, ASHR 2.4%, BTC-USD 2.2%, ETH-USD 0.9%, ^N225 0.5%, CASH 16.9% |
| 2024-12-02 | GC=F 13.4%, SI=F 9.9%, CL=F 9.8%, VWO 9.5%, VEA 9.4%, ^KS11 8.6%, ^NDX 6.3%, BTC-USD 4.9%, ^GSPC 4.8%, ^FTSE 4.3%, ETH-USD 3.4%, ^TWII 2.6%, ASHR 1.5%, CASH 11.5% |
| 2025-01-02 | VEA 13.8%, GC=F 12.3%, ^NDX 10.4%, SI=F 9.5%, ^KS11 9.3%, ^FTSE 8.0%, CL=F 7.0%, VWO 6.4%, ^GSPC 5.9%, BTC-USD 3.2%, ASHR 2.5%, ETH-USD 2.1%, ^TWII 1.8%, CASH 7.8% |
| 2025-02-03 | GC=F 13.7%, SI=F 9.6%, VEA 9.2%, VWO 9.2%, ^NDX 6.8%, ^KS11 6.3%, ^FTSE 5.5%, ASHR 4.9%, CL=F 4.5%, ^GSPC 3.9%, BTC-USD 2.2%, ETH-USD 1.4%, ^TWII 1.2%, CASH 21.6% |
| 2025-03-03 | GC=F 17.0%, VWO 10.4%, ^NDX 9.7%, SI=F 9.7%, ^GSPC 8.6%, VEA 6.3%, ^KS11 6.3%, ASHR 6.2%, CL=F 4.9%, ^FTSE 3.7%, BTC-USD 1.2%, ^TWII 0.8%, ETH-USD 0.6%, CASH 14.6% |
| 2025-04-01 | GC=F 12.4%, VWO 12.0%, VEA 10.4%, ^NDX 10.2%, ^FTSE 9.6%, ^GSPC 7.9%, ^KS11 7.5%, SI=F 7.0%, ASHR 6.8%, CL=F 3.3%, ^N225 1.8%, BTC-USD 0.8%, CASH 10.4% |
| 2025-05-01 | GC=F 14.6%, ^FTSE 14.3%, ^KS11 9.6%, SI=F 8.7%, VWO 8.0%, ASHR 7.4%, VEA 7.2%, CL=F 6.9%, ^NDX 6.9%, ^GSPC 5.2%, BTC-USD 1.8%, ETH-USD 1.2%, ^N225 1.2%, CASH 6.9% |
| 2025-06-02 | GC=F 16.6%, ASHR 10.7%, ^KS11 9.9%, ^FTSE 9.5%, CL=F 9.3%, SI=F 9.2%, ^GSPC 6.5%, VWO 5.3%, VEA 4.9%, ^NDX 4.8%, ETH-USD 2.6%, BTC-USD 1.3%, ^N225 0.8%, CASH 8.6% |
| 2025-07-01 | GC=F 15.5%, ^KS11 12.0%, ^FTSE 10.7%, CL=F 8.6%, ASHR 7.2%, SI=F 6.4%, ^N225 4.8%, ^GSPC 4.4%, VWO 3.6%, ^NDX 3.3%, VEA 3.2%, ETH-USD 1.6%, BTC-USD 0.8%, CASH 18.0% |
| 2025-08-01 | GC=F 15.7%, ASHR 11.5%, ^N225 8.8%, ^KS11 8.2%, ^FTSE 7.2%, SI=F 6.7%, CL=F 5.9%, ^NDX 5.7%, VEA 5.3%, ^TWII 4.4%, ETH-USD 3.1%, ^GSPC 2.9%, VWO 2.3%, BTC-USD 0.6%, CASH 11.6% |
| 2025-09-02 | ^NDX 11.8%, ^N225 11.0%, GC=F 10.6%, ASHR 8.3%, ^TWII 7.1%, CL=F 5.9%, ^KS11 5.2%, SI=F 4.7%, ^FTSE 4.7%, VEA 3.6%, ETH-USD 3.2%, ^GSPC 1.9%, VWO 1.6%, CASH 20.3% |
| 2025-10-01 | ^N225 11.6%, ^TWII 9.4%, ^NDX 8.0%, GC=F 7.5%, ^GSPC 7.0%, CL=F 5.9%, ASHR 5.5%, ^KS11 3.5%, SI=F 3.5%, ^FTSE 3.0%, VEA 2.3%, ETH-USD 2.0%, VWO 1.1%, CASH 29.7% |
| 2025-11-03 | ^TWII 12.8%, ^N225 11.6%, GC=F 9.0%, ASHR 8.8%, ^KS11 6.8%, ^NDX 5.3%, SI=F 4.6%, ^GSPC 4.6%, CL=F 3.7%, ^FTSE 2.0%, VEA 1.5%, ETH-USD 1.2%, VWO 0.7%, CASH 27.3% |
| 2025-12-01 | ^TWII 13.7%, ^N225 9.7%, GC=F 9.0%, ^GSPC 8.8%, VWO 6.2%, ASHR 5.8%, CL=F 5.7%, ^KS11 4.4%, SI=F 3.6%, ^NDX 3.5%, ^FTSE 1.3%, VEA 1.0%, ETH-USD 0.6%, CASH 26.6% |
| 2026-01-02 | ^TWII 16.7%, GC=F 9.8%, ASHR 9.0%, ^N225 8.7%, ^NDX 8.2%, CL=F 6.4%, ^GSPC 5.7%, SI=F 5.0%, VWO 4.1%, ^KS11 3.1%, ^FTSE 0.9%, VEA 0.7%, CASH 21.9% |
| 2026-02-02 | ^TWII 15.0%, ASHR 14.3%, ^NDX 10.6%, GC=F 9.8%, VWO 7.1%, ^N225 5.8%, ^KS11 5.4%, SI=F 4.8%, CL=F 4.6%, ^GSPC 3.7%, ^FTSE 0.6%, CASH 18.4% |
| 2026-03-02 | ^TWII 16.8%, ASHR 16.2%, ^NDX 9.5%, GC=F 9.0%, ^N225 8.4%, ^GSPC 8.3%, VWO 7.4%, ^KS11 6.0%, SI=F 3.6%, CL=F 3.0%, CASH 12.0% |
| 2026-04-01 | ^NDX 13.7%, ^GSPC 13.1%, ASHR 11.0%, ^TWII 10.7%, VWO 9.6%, GC=F 8.6%, ^FTSE 5.8%, ^N225 5.2%, ^KS11 4.3%, VEA 3.5%, CL=F 3.2%, SI=F 2.1%, ETH-USD 0.7%, CASH 8.5% |
| 2026-05-01 | ^TWII 13.4%, GC=F 9.7%, ^NDX 9.6%, ^FTSE 8.9%, ^GSPC 8.8%, VEA 7.6%, ASHR 7.2%, ^N225 6.8%, VWO 6.3%, BTC-USD 3.5%, ^KS11 3.4%, ETH-USD 2.3%, CL=F 2.0%, SI=F 1.2%, CASH 9.3% |
| 2026-06-01 | ^TWII 15.6%, GC=F 12.1%, ^FTSE 10.5%, ^GSPC 10.1%, ^N225 9.3%, VWO 8.3%, ^NDX 6.7%, VEA 5.0%, ASHR 4.7%, SI=F 2.9%, ^KS11 2.8%, CL=F 2.6%, BTC-USD 2.2%, ETH-USD 1.3%, CASH 5.9% |
| 2026-07-01 | ^TWII 16.6%, GC=F 13.5%, VWO 11.9%, ^N225 10.4%, ^FTSE 7.2%, ^GSPC 6.8%, ^NDX 4.6%, SI=F 3.6%, VEA 3.4%, ASHR 3.2%, CL=F 2.7%, ^KS11 1.9%, BTC-USD 1.2%, ETH-USD 0.7%, CASH 12.4% |

## Benchmark: equal-weight buy & hold

|      |   return |   ann_vol |   sharpe |   max_dd |
|:-----|---------:|----------:|---------:|---------:|
| 2024 |   0.2381 |    0.1557 |   1.4502 |  -0.1271 |
| 2025 |   0.2888 |    0.1622 |   1.6585 |  -0.1742 |
| 2026 |   0.1142 |    0.2433 |   1.026  |  -0.1257 |
| FULL |   0.7779 |    0.1785 |   1.3879 |  -0.1785 |
