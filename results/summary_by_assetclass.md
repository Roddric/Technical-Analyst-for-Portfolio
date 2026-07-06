# Flat IC / Expectancy Kill-Screen — Summary by Asset Class

> **FLAT, non-regime-conditioned first-pass filter.** Surviving here means *not obviously useless* — it does **not** mean validated, tradable, or good. This screen can only remove the broadly useless; it cannot promote anything.

- Continuous IC tests with a valid p-value: **1552**
- Look significant raw (p < 0.05): **390**
- Survive Benjamini-Hochberg FDR at q=0.1: **284**
- Raw-vs-FDR gives a sense of the noise floor: 390 raw vs 284 after multiple-comparison control.

## credit

### Top surviving CONTINUOUS indicators (by |IC_IR|, FDR-survivors only)

| asset | indicator | h | IC | IC_IR | p | n |
|---|---|---:|---:|---:|---:|---:|
| HYG | ATR_RATIO_14 | 1 | 0.0519 | 0.808 | 6.06e-04 | 4821 |
| HYG | NATR_14 | 1 | 0.0519 | 0.808 | 6.06e-04 | 4821 |
| LQD | ULTOSC | 1 | -0.0304 | -0.652 | 1.82e-02 | 5989 |
| HYG | NATR_14 | 5 | 0.1044 | 0.450 | 1.53e-04 | 4817 |
| HYG | ATR_RATIO_14 | 5 | 0.1044 | 0.450 | 1.53e-04 | 4817 |
| HYG | ATR_RATIO_14 | 10 | 0.1435 | 0.312 | 1.35e-04 | 4812 |
| HYG | NATR_14 | 10 | 0.1435 | 0.312 | 1.35e-04 | 4812 |
| HYG | ADOSC_3_10 | 5 | -0.0571 | -0.300 | 1.61e-02 | 4822 |
| HYG | AROONOSC_14 | 20 | -0.1084 | -0.277 | 6.75e-03 | 4802 |
| HYG | ULTOSC | 20 | -0.0941 | -0.275 | 1.28e-02 | 4788 |
| HYG | ADOSC_3_10 | 10 | -0.0754 | -0.236 | 1.00e-02 | 4817 |
| HYG | ATR_RATIO_14 | 20 | 0.1875 | 0.215 | 2.62e-04 | 4802 |

### Top DISCRETE signals (by |expectancy spread|, trusted states only)
_Spread = forward-return expectancy of bullish state minus bearish state. This is an expectancy in return units, NOT a correlation._

| asset | signal | h | spread | n(min state) |
|---|---|---:|---:|---:|
| HYG | RSI_14_THRESHOLD | 20 | +0.01806 | 146 |
| HYG | RSI_14_THRESHOLD | 10 | +0.01109 | 146 |
| HYG | RSI_14_THRESHOLD | 5 | +0.00866 | 146 |
| LQD | RSI_14_THRESHOLD | 20 | +0.00430 | 142 |
| HYG | SAR_PRICE_CROSS | 20 | -0.00351 | 1860 |
| LQD | RSI_14_THRESHOLD | 5 | +0.00244 | 142 |
| LQD | MACD_SIGNAL_CROSS | 20 | +0.00221 | 2801 |
| LQD | SAR_PRICE_CROSS | 20 | +0.00211 | 2548 |

## energy

### Top surviving CONTINUOUS indicators (by |IC_IR|, FDR-survivors only)

| asset | indicator | h | IC | IC_IR | p | n |
|---|---|---:|---:|---:|---:|---:|
| CL=F | ATR_RATIO_14 | 10 | 0.0818 | 0.242 | 1.23e-02 | 6464 |
| CL=F | NATR_14 | 10 | 0.0818 | 0.242 | 1.23e-02 | 6464 |
| CL=F | ATR_RATIO_14 | 20 | 0.1108 | 0.182 | 1.41e-02 | 6454 |
| CL=F | NATR_14 | 20 | 0.1108 | 0.182 | 1.41e-02 | 6454 |

### Top DISCRETE signals (by |expectancy spread|, trusted states only)
_Spread = forward-return expectancy of bullish state minus bearish state. This is an expectancy in return units, NOT a correlation._

| asset | signal | h | spread | n(min state) |
|---|---|---:|---:|---:|
| CL=F | RSI_14_THRESHOLD | 20 | -0.04366 | 287 |
| CL=F | RSI_14_THRESHOLD | 10 | -0.01548 | 287 |
| CL=F | MACD_SIGNAL_CROSS | 20 | +0.00730 | 3068 |
| CL=F | SAR_PRICE_CROSS | 20 | +0.00597 | 3035 |
| CL=F | MACD_SIGNAL_CROSS | 5 | -0.00287 | 3083 |
| CL=F | EMA_50_200_CROSS | 20 | -0.00238 | 2614 |
| CL=F | EMA_50_200_CROSS | 10 | -0.00162 | 2614 |
| CL=F | SAR_PRICE_CROSS | 5 | -0.00158 | 3050 |

## equity

### Top surviving CONTINUOUS indicators (by |IC_IR|, FDR-survivors only)

| asset | indicator | h | IC | IC_IR | p | n |
|---|---|---:|---:|---:|---:|---:|
| ^STOXX50E | CMO_14 | 1 | -0.0460 | -1.067 | 1.08e-03 | 4808 |
| ^STOXX50E | RSI_14 | 1 | -0.0460 | -1.067 | 1.08e-03 | 4808 |
| ^FTSE | RSI_14 | 1 | -0.0289 | -0.826 | 3.36e-03 | 10718 |
| ^FTSE | CMO_14 | 1 | -0.0289 | -0.826 | 3.36e-03 | 10718 |
| ^NDX | ADOSC_3_10 | 1 | -0.0333 | -0.696 | 7.20e-04 | 10255 |
| ^STOXX50E | CCI_20 | 1 | -0.0436 | -0.672 | 1.98e-03 | 4803 |
| ^STOXX50E | BBANDS_PCTB_20_2 | 1 | -0.0416 | -0.663 | 3.04e-03 | 4803 |
| ^KS11 | ATR_RATIO_14 | 1 | 0.0453 | 0.657 | 2.85e-04 | 7259 |
| ^KS11 | NATR_14 | 1 | 0.0453 | 0.657 | 2.85e-04 | 7259 |
| ^NDX | STOCH_K_14 | 1 | -0.0234 | -0.654 | 1.72e-02 | 10247 |
| ^NDX | ULTOSC | 1 | -0.0275 | -0.633 | 4.97e-03 | 10236 |
| ^STOXX50E | NATR_14 | 5 | 0.0770 | 0.628 | 4.12e-03 | 4804 |

### Top DISCRETE signals (by |expectancy spread|, trusted states only)
_Spread = forward-return expectancy of bullish state minus bearish state. This is an expectancy in return units, NOT a correlation._

| asset | signal | h | spread | n(min state) |
|---|---|---:|---:|---:|
| ^STOXX50E | RSI_14_THRESHOLD | 20 | +0.02129 | 116 |
| ^KS11 | RSI_14_THRESHOLD | 20 | -0.01938 | 269 |
| ^NDX | RSI_14_THRESHOLD | 10 | +0.01471 | 172 |
| ^NDX | RSI_14_THRESHOLD | 5 | +0.01337 | 172 |
| ^NDX | EMA_50_200_CROSS | 20 | +0.01241 | 1944 |
| ^HSI | RSI_14_THRESHOLD | 20 | +0.00980 | 378 |
| ^KS11 | RSI_14_THRESHOLD | 5 | +0.00876 | 269 |
| ^NDX | RSI_14_THRESHOLD | 1 | +0.00740 | 172 |

## fx

### Top surviving CONTINUOUS indicators (by |IC_IR|, FDR-survivors only)

| asset | indicator | h | IC | IC_IR | p | n |
|---|---|---:|---:|---:|---:|---:|
| EURUSD=X | ULTOSC | 1 | -0.2148 | -1.200 | 1.79e-56 | 5830 |
| EURUSD=X | STOCHF_K_14 | 1 | -0.0936 | -1.199 | 6.50e-14 | 5843 |
| EURUSD=X | WILLR_14 | 1 | -0.0937 | -1.199 | 5.90e-14 | 5845 |
| CHF=X | ULTOSC | 1 | -0.2257 | -1.163 | 1.19e-62 | 5896 |
| CHF=X | WILLR_14 | 1 | -0.0740 | -0.897 | 2.20e-09 | 5911 |
| CHF=X | STOCHF_K_14 | 1 | -0.0745 | -0.897 | 1.80e-09 | 5909 |
| EURUSD=X | STOCH_K_14 | 1 | -0.0442 | -0.888 | 4.54e-04 | 5841 |
| DX-Y.NYB | CMO_14 | 1 | 0.0410 | -0.592 | 1.01e-06 | 14075 |
| DX-Y.NYB | RSI_14 | 1 | 0.0410 | -0.591 | 1.01e-06 | 14075 |
| DX-Y.NYB | PPO_12_26 | 1 | 0.0404 | -0.372 | 6.70e-06 | 14064 |
| DX-Y.NYB | APO_12_26 | 1 | 0.0410 | -0.371 | 5.01e-06 | 14064 |
| DX-Y.NYB | ROC_10 | 1 | 0.0253 | -0.340 | 4.69e-03 | 14079 |

### Top DISCRETE signals (by |expectancy spread|, trusted states only)
_Spread = forward-return expectancy of bullish state minus bearish state. This is an expectancy in return units, NOT a correlation._

| asset | signal | h | spread | n(min state) |
|---|---|---:|---:|---:|
| CHF=X | RSI_14_THRESHOLD | 20 | +0.01852 | 237 |
| CHF=X | RSI_14_THRESHOLD | 10 | +0.01324 | 237 |
| DX-Y.NYB | RSI_14_THRESHOLD | 20 | -0.00979 | 882 |
| DX-Y.NYB | RSI_14_THRESHOLD | 10 | -0.00606 | 882 |
| CHF=X | RSI_14_THRESHOLD | 5 | +0.00483 | 239 |
| DX-Y.NYB | RSI_14_THRESHOLD | 5 | -0.00336 | 885 |
| EURUSD=X | RSI_14_THRESHOLD | 10 | +0.00285 | 232 |
| CHF=X | EMA_50_200_CROSS | 20 | -0.00269 | 2341 |

## metals

### Top surviving CONTINUOUS indicators (by |IC_IR|, FDR-survivors only)

| asset | indicator | h | IC | IC_IR | p | n |
|---|---|---:|---:|---:|---:|---:|
| SI=F | AD | 1 | -0.0385 | -0.683 | 1.43e-03 | 6482 |
| SI=F | AD | 5 | -0.0730 | -0.260 | 1.70e-03 | 6478 |
| SI=F | NATR_14 | 1 | 0.0323 | 0.201 | 7.88e-03 | 6468 |
| SI=F | ATR_RATIO_14 | 1 | 0.0323 | 0.201 | 7.88e-03 | 6468 |
| SI=F | AD | 10 | -0.0970 | -0.169 | 2.33e-03 | 6473 |
| SI=F | AD | 20 | -0.1423 | -0.119 | 1.17e-03 | 6463 |

### Top DISCRETE signals (by |expectancy spread|, trusted states only)
_Spread = forward-return expectancy of bullish state minus bearish state. This is an expectancy in return units, NOT a correlation._

| asset | signal | h | spread | n(min state) |
|---|---|---:|---:|---:|
| GC=F | RSI_14_THRESHOLD | 20 | +0.01534 | 178 |
| SI=F | RSI_14_THRESHOLD | 10 | +0.00997 | 204 |
| GC=F | RSI_14_THRESHOLD | 10 | +0.00991 | 180 |
| SI=F | RSI_14_THRESHOLD | 20 | +0.00965 | 201 |
| GC=F | SAR_PRICE_CROSS | 20 | -0.00571 | 2952 |
| GC=F | EMA_50_200_CROSS | 20 | +0.00559 | 1437 |
| SI=F | EMA_50_200_CROSS | 20 | +0.00555 | 2456 |
| GC=F | RSI_14_THRESHOLD | 5 | +0.00493 | 180 |

## rates

### Top surviving CONTINUOUS indicators (by |IC_IR|, FDR-survivors only)

| asset | indicator | h | IC | IC_IR | p | n |
|---|---|---:|---:|---:|---:|---:|
| TLT | OBV | 1 | -0.0335 | -1.257 | 7.81e-03 | 6017 |
| TLT | ADOSC_3_10 | 1 | -0.0594 | -0.681 | 8.43e-06 | 6008 |
| TLT | MOM_10 | 1 | -0.0329 | -0.648 | 1.35e-02 | 6007 |
| TLT | ROC_10 | 1 | -0.0328 | -0.646 | 1.32e-02 | 6007 |
| TLT | OBV | 5 | -0.0690 | -0.627 | 2.97e-03 | 6013 |
| TLT | ULTOSC | 1 | -0.0379 | -0.624 | 2.55e-03 | 5989 |
| TLT | STOCHF_K_14 | 1 | -0.0328 | -0.594 | 8.36e-03 | 6002 |
| TLT | WILLR_14 | 1 | -0.0328 | -0.594 | 8.42e-03 | 6004 |
| TLT | OBV | 10 | -0.0997 | -0.451 | 1.97e-03 | 6008 |
| ^TNX | PPO_12_26 | 1 | 0.0244 | -0.431 | 4.90e-03 | 16083 |
| ^TNX | APO_12_26 | 1 | 0.0312 | -0.428 | 5.18e-04 | 16083 |
| ^TNX | RSI_14 | 1 | 0.0449 | -0.409 | 2.32e-08 | 16094 |

### Top DISCRETE signals (by |expectancy spread|, trusted states only)
_Spread = forward-return expectancy of bullish state minus bearish state. This is an expectancy in return units, NOT a correlation._

| asset | signal | h | spread | n(min state) |
|---|---|---:|---:|---:|
| ^TNX | RSI_14_THRESHOLD | 20 | -0.07575 | 1073 |
| ^TNX | RSI_14_THRESHOLD | 10 | -0.07051 | 1073 |
| ^TNX | MACD_SIGNAL_CROSS | 20 | +0.04558 | 8027 |
| ^TNX | RSI_14_THRESHOLD | 5 | -0.03613 | 1073 |
| ^TNX | MACD_SIGNAL_CROSS | 10 | +0.02675 | 8029 |
| ^TNX | SAR_PRICE_CROSS | 20 | +0.02599 | 7986 |
| ^TNX | SAR_PRICE_CROSS | 10 | +0.01845 | 7996 |
| ^TNX | EMA_50_200_CROSS | 20 | +0.01845 | 7456 |

## NOTES (read before trusting anything above)

**This is a FLAT, non-regime-conditioned screen.** An indicator that only works in one regime (e.g. only in high-volatility or only in trending markets) can average out to near-zero IC over full history and be wrongly killed here. This screen removes the *broadly* useless; it cannot promote anything to 'good'. **Regime-conditioned testing is the required next step.**

- **Deferred China assets (not fetched, intentional gap):** STAR 50, CSI 300 native, HSI Tech — deferred pending data API.
- **^TNX / rates:** ^TNX is a **yield** series; its indicators are computed on the yield level and its 'forward returns' are forward **changes in yield**, not price returns. Do not read ^TNX rows on the same scale as equity/price rows. TLT is a price proxy for long UST and should move inversely to ^TNX — use it as a cross-check.
- **CL=F (WTI crude):** a continuous front-month stitch; roll gaps can inject artifacts into short-horizon returns. Treat CL=F short-horizon results with extra caution.
- **Volume-less series** (volume indicators OBV/AD/ADOSC/MFI skipped): CHF=X, EURUSD=X.

### Excluded indicator groups (kept auditable, not tested)
- **CDL* candlestick patterns (~60)** — fire too rarely; poor screen; not worth multiple-comparisons cost
- **Raw overlays as standalone values (SMA/EMA/WMA/DEMA/TEMA/TRIMA/KAMA/MAMA/T3/MIDPOINT/MIDPRICE/HT_TRENDLINE)** — never IC a raw MA level; use derived cross (discrete) or price/MA ratio
- **Math Transform / Math Operator / Price Transform groups** — not signals
