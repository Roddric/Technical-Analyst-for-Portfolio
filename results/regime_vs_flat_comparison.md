# Regime vs Flat — did regime-conditioning revive dead indicators?

> **THE KEY DELIVERABLE.** For each regime-conditioned FDR-surviving slot winner, we compare its regime IC to its flat-history IC (grouped run). **Thesis-confirming** = dead flat (|IC|<0.03) but strong in a regime (|IC|>0.10). Regime IC on a thin cell is a HYPOTHESIS, not an edge.

- Continuous cell tests (valid p): **33868** | raw p<0.05: **4236** | survive FDR (within-cell) @ 0.1: **2064**

## ⚠ ARTIFACT AUDIT — read this first

Within-cell IC magnitude is **inflated by overlapping forward returns in small, non-contiguous regime cells**. At horizon h an n-row cell holds only ~n/h *independent* forward windows, so |IC| grows mechanically as h rises / cells shrink. The evidence, over FDR survivors:

| horizon | survivors | median \|IC\| | median independent windows (n/h) |
|---:|---:|---:|---:|
| 1 | 282 | 0.106 | 1044 |
| 5 | 399 | 0.283 | 36 |
| 10 | 618 | 0.354 | 14 |
| 20 | 765 | 0.386 | 7 |

- Correlation of survivor \|IC\| with 1/sqrt(independent windows): **0.76** — strong; the big ICs live where the effective sample is tiny.
- **Consequence:** the raw h=10/h=20 'revivals' below are largely overlap/small-sample noise, NOT evidence indicators concentrate in regimes. The tables flag `eff_n` (=n/h) and mark rows with <30 independent windows **ARTIFACT-SUSPECT**.
- A second tell: in the thinnest cells (e.g. ^KS11 RC-04, n~64) *nearly every* indicator co-fires at once — that is the *cell/period* being idiosyncratic, not each indicator carrying signal. Co-firing counts are shown per flagged cell.

## Thesis-confirming candidates: DEAD flat (|IC|<0.03) -> |IC|>0.10 in regime
_Raw count: 162. After requiring >=60 independent windows (eff_n>=60): 13. The rest are artifact-suspect (above)._

### Adequately-sampled (eff_n >= 60) — the only ones worth a second look

| asset | regime | slot | indicator | h | flat IC | regime IC | cell_n | eff_n | verdict |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| ^STOXX50E | RC-05 | Volume | VL-OBV-SLOPE-5 | 1 | -0.0161 | -0.3223 | 115 | 115 | adequately-sampled (eff_n=115) |
| LQD | RC-13 | Volatility | VO-RVI-14 | 1 | -0.0170 | -0.3081 | 83 | 83 | adequately-sampled (eff_n=83) |
| GC=F | RC-14 | Volatility | VO-BBB-20-2 | 1 | +0.0089 | +0.3053 | 140 | 140 | adequately-sampled (eff_n=140) |
| GC=F | RC-11 | Trend | TR-MACDH-12-26-9 | 20 | -0.0294 | -0.2189 | 1307 | 65 | adequately-sampled (eff_n=65) |
| ^NDX | RC-17 | Momentum | MO-RSI-14 | 1 | -0.0174 | -0.2097 | 226 | 226 | adequately-sampled (eff_n=226) |
| HYG | RC-03 | Volatility | VO-BBP-20-2 | 1 | +0.0113 | -0.2058 | 98 | 98 | adequately-sampled (eff_n=98) |
| ^N225 | RC-12 | Volume | VL-MFI-14 | 1 | -0.0193 | -0.1975 | 418 | 418 | adequately-sampled (eff_n=418) |
| CL=F | RC-01 | Momentum | MO-TSI-13-25 | 20 | -0.0037 | -0.1676 | 1895 | 95 | adequately-sampled (eff_n=95) |
| CL=F | RC-01 | Trend | TR-AROONOSC-14 | 20 | +0.0055 | -0.1197 | 1895 | 95 | adequately-sampled (eff_n=95) |
| ^N225 | RC-11 | Trend | TR-MACDH-12-26-9 | 20 | -0.0127 | -0.1181 | 1832 | 92 | adequately-sampled (eff_n=92) |
| ^N225 | RC-11 | Momentum | MO-STOCH-14 | 20 | -0.0181 | -0.1141 | 1832 | 92 | adequately-sampled (eff_n=92) |
| CHF=X | RC-01 | Volatility | VO-RVI-14 | 10 | -0.0286 | -0.1133 | 1763 | 176 | adequately-sampled (eff_n=176) |
| ^N225 | RC-11 | Volatility | VO-NATR-14 | 10 | +0.0224 | +0.1108 | 1832 | 183 | adequately-sampled (eff_n=183) |

### Artifact-suspect (eff_n < 60) — shown for completeness, do NOT trust
_149 cases; top 15 by |IC|. Small-sample/overlap inflated._

| asset | regime | slot | indicator | h | flat IC | regime IC | eff_n | flag |
|---|---|---|---|---:|---:|---:|---:|---|
| TLT | RC-13 | Trend | TR-TRIX-15 | 20 | +0.0066 | -0.6828 | 4 | ARTIFACT-SUSPECT (eff_n=4, 5 co-fire) |
| ^KS11 | RC-13 | Volatility | VO-UI-14 | 20 | +0.0180 | +0.6789 | 4 | ARTIFACT-SUSPECT (eff_n=4, 22 co-fire) |
| ^N225 | RC-07 | Momentum | MO-TSI-13-25 | 20 | +0.0146 | -0.6647 | 7 | ARTIFACT-SUSPECT (eff_n=7, 19 co-fire) |
| ^KS11 | RC-07 | Volatility | VO-UI-14 | 20 | +0.0180 | +0.6363 | 6 | ARTIFACT-SUSPECT (eff_n=6, 25 co-fire) |
| ^N225 | RC-04 | Trend | TR-TRIX-15 | 10 | +0.0038 | +0.6297 | 7 | ARTIFACT-SUSPECT (eff_n=7, 15 co-fire) |
| ^KS11 | RC-09 | Volume | VL-ADOSC-3-10 | 10 | +0.0004 | -0.6251 | 12 | ARTIFACT-SUSPECT (eff_n=12, 44 co-fire) |
| GC=F | RC-09 | Momentum | MO-AO-5-34 | 20 | -0.0071 | -0.6127 | 7 | ARTIFACT-SUSPECT (eff_n=7, 31 co-fire) |
| LQD | RC-20 | Trend | TR-AROONOSC-14 | 20 | +0.0098 | +0.6105 | 5 | ARTIFACT-SUSPECT (eff_n=5, 27 co-fire) |
| LQD | RC-20 | Momentum | MO-AO-5-34 | 20 | +0.0156 | +0.6046 | 5 | ARTIFACT-SUSPECT (eff_n=5, 27 co-fire) |
| DX-Y.NYB | RC-14 | Volatility | VO-DCW-20 | 20 | +0.0039 | +0.6005 | 8 | ARTIFACT-SUSPECT (eff_n=8, 17 co-fire) |
| LQD | RC-13 | Trend | TR-TRIX-15 | 20 | +0.0192 | -0.6001 | 4 | ARTIFACT-SUSPECT (eff_n=4, 8 co-fire) |
| ^NDX | RC-13 | Momentum | MO-AO-5-34 | 20 | -0.0217 | -0.5888 | 6 | ARTIFACT-SUSPECT (eff_n=6) |
| ^NDX | RC-04 | Volume | VL-ADOSC-3-10 | 10 | -0.0273 | +0.5863 | 7 | ARTIFACT-SUSPECT (eff_n=7, 30 co-fire) |
| CL=F | RC-04 | Trend | TR-TRIX-15 | 20 | +0.0101 | -0.5847 | 3 | ARTIFACT-SUSPECT (eff_n=3) |
| ^NDX | RC-04 | Momentum | MO-AO-5-34 | 5 | -0.0111 | +0.5834 | 14 | ARTIFACT-SUSPECT (eff_n=14, 30 co-fire) |

## Strongest adequately-sampled regime winners (eff_n>=60, |IC|>0.10)

| asset | regime | slot | indicator | h | flat IC | regime IC | cell_n | eff_n |
|---|---|---|---|---:|---:|---:|---:|---:|
| ^TNX | RC-01 | Volume | VL-CMF-20 | 20 | -0.1971 | -0.7909 | 2499 | 125 |
| DX-Y.NYB | RC-11 | Volume | VL-CMF-20 | 20 | -0.4107 | -0.7319 | 1938 | 97 |
| ^TNX | RC-02 | Volume | VL-CMF-20 | 10 | -0.1110 | -0.7125 | 1378 | 138 |
| CHF=X | RC-07 | Momentum | MO-UO-7-14-28 | 1 | -0.2259 | -0.5937 | 120 | 120 |
| CHF=X | RC-13 | Momentum | MO-UO-7-14-28 | 1 | -0.2259 | -0.4939 | 83 | 83 |
| CHF=X | RC-17 | Momentum | MO-UO-7-14-28 | 1 | -0.2259 | -0.4854 | 112 | 112 |
| EURUSD=X | RC-07 | Momentum | MO-UO-7-14-28 | 1 | -0.2145 | -0.4555 | 120 | 120 |
| EURUSD=X | RC-13 | Momentum | MO-UO-7-14-28 | 1 | -0.2145 | -0.4070 | 83 | 83 |
| EURUSD=X | RC-14 | Momentum | MO-UO-7-14-28 | 1 | -0.2145 | -0.3283 | 105 | 105 |
| ^STOXX50E | RC-05 | Volume | VL-OBV-SLOPE-5 | 1 | -0.0161 | -0.3223 | 115 | 115 |
| CHF=X | RC-14 | Momentum | MO-UO-7-14-28 | 1 | -0.2259 | -0.3122 | 105 | 105 |
| SI=F | RC-11 | Volume | VL-EOM-14 | 10 | -0.0579 | -0.3100 | 1307 | 131 |
| LQD | RC-13 | Volatility | VO-RVI-14 | 1 | -0.0170 | -0.3081 | 83 | 83 |
| GC=F | RC-14 | Volatility | VO-BBB-20-2 | 1 | +0.0089 | +0.3053 | 140 | 140 |
| HYG | RC-14 | Volatility | VO-NATR-14 | 1 | +0.0522 | +0.2923 | 106 | 106 |
| CHF=X | RC-18 | Momentum | MO-UO-7-14-28 | 1 | -0.2259 | -0.2901 | 176 | 176 |
| ^FTSE | RC-02 | Volume | VL-CMF-20 | 20 | -0.1440 | -0.2737 | 1357 | 68 |
| CHF=X | RC-01 | Momentum | MO-UO-7-14-28 | 1 | -0.2259 | -0.2737 | 1763 | 1763 |
| ^TNX | RC-03 | Volume | VL-CMF-20 | 1 | +0.0586 | +0.2697 | 313 | 313 |
| CL=F | RC-01 | Volatility | VO-ATRRATIO-14 | 20 | +0.1103 | +0.2508 | 1895 | 95 |
| SI=F | RC-11 | Trend | TR-MACDH-12-26-9 | 20 | -0.0329 | -0.2505 | 1307 | 65 |
| HYG | RC-01 | Volatility | VO-ATRRATIO-14 | 20 | +0.1875 | +0.2481 | 1475 | 74 |
| EURUSD=X | RC-01 | Momentum | MO-UO-7-14-28 | 1 | -0.2145 | -0.2473 | 1732 | 1732 |
| EURUSD=X | RC-11 | Momentum | MO-UO-7-14-28 | 1 | -0.2145 | -0.2339 | 1238 | 1238 |
| ^FTSE | RC-11 | Volume | VL-EOM-14 | 20 | -0.1472 | -0.2322 | 1914 | 96 |

## Targeted hypothesis checks (from the flat run)

_Computed on low-overlap horizons h in {1,5} and SIGNED-mean IC across cells, so noise averages out and the h=10/20 overlap inflation (ARTIFACT AUDIT) does not drive the verdicts._

### 1. MO-TSI-13-25 (equity momentum): calm/trending vs shock
- mean cell IC in calm/trending ['RC-01', 'RC-02', 'RC-03', 'RC-10', 'RC-12']: **-0.0068** (n=80 cells)
- mean cell IC in shock ['RC-06', 'RC-08', 'RC-15', 'RC-16', 'RC-17']: **-0.0837** (n=16 cells)
- **Verdict:** NOT clearly regime-masked (similar across regimes). SUPPRESS prior stands; drop TSI as a lead.

### 2. TR-VORTEX-14 (trend, SUBSTITUTE): concentrated or uniformly-weak-least-bad?
- mean cell IC by regime (top 6 by |mean|):
  - RC-09 Post-Shock Reflation Bear: -0.1041 (n=36)
  - RC-17 Sudden Bear Entry: -0.0557 (n=36)
  - RC-03 Reflation Melt-Up: -0.0285 (n=36)
  - RC-13 Stagflation Chop: -0.0280 (n=36)
  - RC-12 Slow Reflation Drift: +0.0276 (n=36)
  - RC-18 Early Recovery Bull: -0.0263 (n=36)
- range of |mean IC| across regimes: 0.1040. **Verdict:** CONCENTRATES in specific regimes.

### 3. Volatility MAINTAIN winners (VO-UI-14, VO-ATRRATIO-14): stable or shock-spike?
- VO-UI-14: mean |IC| all regimes=0.0792 | calm mean IC=+0.0009 (n=180) | shock mean IC=+0.1098 (n=36)
- VO-ATRRATIO-14: mean |IC| all regimes=0.0923 | calm mean IC=+0.0105 (n=180) | shock mean IC=+0.1244 (n=36)
- **Verdict:** if |IC| is broadly similar across regimes -> confirms always-measurable MAINTAIN prior; a strong shock-only spike would instead indicate shock-specific behaviour (shock cells here are thin — read cautiously).

## Caveats
- **Regime is US-macro/market defined** (Axis1 uses the broad equity index). For US equity assets the regime shares information with the asset's own trend — not lookahead (all axes causal/point-in-time), but shared conditioning. Cross-asset (gold, FX, rates) regimes are exogenous.
- **Shock regimes (RC-06/08/15/16) are thin or absent** in 1990-2026 developed markets under a VIX-Z>3 definition; shock-conditioned claims are weak here.
- **HY OAS only 2023+** (ICE licensing); pre-2023 shock detection is VIX-driven.
- **Vintage Axis3** is faithful from ~1992 (ALFRED archive start); 1990-91 macro is approximate. **ISM PMI unavailable** on FRED — Axis3 leans on GDP+CPI.
- Still FLAT within each regime: not walk-forward, not out-of-sample validated.
