# Best-in-Slot — flat full-history IC (per asset, four slots)

> **FLAT / non-regime-conditioned.** A 'slot winner' is the best FDR-surviving indicator in that category on full history. This is **best-in-slot on flat history only** — NOT regime-validated, NOT a confirmed production choice. Regime-cell conditioning is the next run.

## ^GSPC — S&P 500 (equity)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | -0.0102 | -0.921 | 3.62e-01 | no | 9146 |
| TR-VORTEX-14 | 1 | -0.0335 | -0.720 | 1.31e-03 | yes | 9175 |
| TR-QSTICK-10 | 1 | -0.0394 | -0.712 | 2.96e-04 | yes | 9180 |
| TR-MACDH-12-26-9 | 1 | -0.0308 | -0.629 | 4.95e-03 | yes | 9156 |
| TR-AROONOSC-14 | 1 | -0.0277 | -0.567 | 7.69e-03 | yes | 9175 |
| TR-TRIX-15 | 5 | -0.0320 | -0.510 | 1.14e-01 | no | 9142 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-SUPERT-10-3 | 20 | -0.00505 | 3563 |
| TR-EMACROSS-50-200 | 20 | +0.00330 | 1881 |
| TR-SUPERT-10-3 | 10 | -0.00139 | 3570 |
| TR-SUPERT-10-3 | 5 | -0.00131 | 3575 |

**Slot winner: TR-VORTEX-14** (h=1, IC=-0.0335, IC_IR=-0.720). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | -0.0270 | -1.115 | 1.06e-02 | yes | 9152 |
| MO-RSI-14 | 1 | -0.0464 | -1.037 | 7.18e-06 | yes | 9176 |
| MO-AO-5-34 | 1 | -0.0162 | -0.921 | 1.37e-01 | no | 9156 |
| MO-UO-7-14-28 | 1 | -0.0647 | -0.822 | 2.44e-10 | yes | 9162 |
| MO-FISHER-9 | 1 | -0.0460 | -0.800 | 9.12e-06 | yes | 9181 |
| MO-STOCH-14 | 1 | -0.0497 | -0.790 | 1.27e-06 | yes | 9174 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | +0.01979 | 159 |
| MO-RSI-THRESH-14 | 5 | +0.01217 | 159 |
| MO-RSI-THRESH-14 | 10 | +0.00980 | 159 |
| MO-RSI-THRESH-14 | 1 | +0.00565 | 159 |

**Slot winner: MO-TSI-13-25** (h=1, IC=-0.0270, IC_IR=-1.115). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-ATRRATIO-14 | 1 | 0.0240 | 0.927 | 2.35e-02 | no | 9176 |
| VO-UI-14 | 1 | 0.0284 | 0.876 | 7.65e-03 | yes | 9163 |
| VO-NATR-14 | 1 | 0.0270 | 0.819 | 1.08e-02 | yes | 9175 |
| VO-KCW-20 | 1 | 0.0243 | 0.781 | 2.17e-02 | no | 9169 |
| VO-BBP-20-2 | 1 | -0.0461 | -0.773 | 5.99e-06 | yes | 9170 |
| VO-RVI-14 | 1 | -0.0434 | -0.751 | 2.21e-05 | yes | 9163 |

**Slot winner: VO-UI-14** (h=1, IC=0.0284, IC_IR=0.876). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-ADOSC-3-10 | 1 | -0.0460 | -0.910 | 9.06e-06 | yes | 9180 |
| VL-CMF-20 | 1 | -0.0368 | -0.777 | 3.21e-04 | yes | 9170 |
| VL-MFI-14 | 1 | -0.0381 | -0.689 | 2.49e-04 | yes | 9176 |
| VL-EOM-14 | 1 | -0.0239 | -0.671 | 3.22e-02 | no | 9161 |
| VL-AD-SLOPE-5 | 1 | -0.0447 | -0.604 | 1.90e-05 | yes | 9184 |
| VL-PVT-SLOPE-5 | 1 | -0.0407 | -0.600 | 2.05e-04 | yes | 9183 |

**Slot winner: VL-ADOSC-3-10** (h=1, IC=-0.0460, IC_IR=-0.910). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

## ^NDX — Nasdaq 100 (equity)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0129 | -0.868 | 2.56e-01 | no | 9146 |
| TR-VORTEX-14 | 1 | -0.0109 | -0.663 | 3.02e-01 | no | 9175 |
| TR-QSTICK-10 | 1 | -0.0188 | -0.614 | 7.98e-02 | no | 9180 |
| TR-AROONOSC-14 | 1 | -0.0112 | -0.564 | 2.82e-01 | no | 9175 |
| TR-MACDH-12-26-9 | 1 | -0.0201 | -0.560 | 5.70e-02 | no | 9156 |
| TR-TRIX-15 | 5 | 0.0038 | -0.478 | 8.52e-01 | no | 9142 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-EMACROSS-50-200 | 20 | +0.01719 | 1734 |
| TR-EMACROSS-50-200 | 10 | +0.00796 | 1734 |
| TR-EMACROSS-50-200 | 5 | +0.00399 | 1734 |
| TR-MACD-CROSS-12-26-9 | 5 | -0.00263 | 4449 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | -0.0034 | -1.001 | 7.52e-01 | no | 9152 |
| MO-RSI-14 | 1 | -0.0174 | -0.913 | 9.63e-02 | no | 9176 |
| MO-AO-5-34 | 1 | -0.0025 | -0.824 | 8.16e-01 | no | 9156 |
| MO-FISHER-9 | 1 | -0.0223 | -0.710 | 3.19e-02 | no | 9181 |
| MO-STOCH-14 | 1 | -0.0270 | -0.699 | 8.43e-03 | yes | 9174 |
| MO-UO-7-14-28 | 1 | -0.0322 | -0.694 | 1.60e-03 | yes | 9162 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 5 | +0.01582 | 145 |
| MO-RSI-THRESH-14 | 10 | +0.01538 | 145 |
| MO-RSI-THRESH-14 | 1 | +0.01009 | 145 |
| MO-RSI-THRESH-14 | 20 | +0.00673 | 145 |

**Slot winner: MO-STOCH-14** (h=1, IC=-0.0270, IC_IR=-0.699). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-ATRRATIO-14 | 1 | 0.0148 | 0.815 | 1.66e-01 | no | 9176 |
| VO-UI-14 | 1 | 0.0102 | 0.813 | 3.39e-01 | no | 9163 |
| VO-NATR-14 | 1 | 0.0158 | 0.684 | 1.40e-01 | no | 9175 |
| VO-BBP-20-2 | 1 | -0.0173 | -0.625 | 9.47e-02 | no | 9170 |
| VO-RVI-14 | 1 | -0.0114 | -0.622 | 2.68e-01 | no | 9163 |
| VO-KCW-20 | 1 | 0.0146 | 0.620 | 1.71e-01 | no | 9169 |

**Slot winner: VO-BBP-20-2** (h=5, IC=-0.0467, IC_IR=-0.401). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-ADOSC-3-10 | 1 | -0.0358 | -0.747 | 4.68e-04 | yes | 9180 |
| VL-CMF-20 | 1 | -0.0061 | -0.633 | 5.58e-01 | no | 9170 |
| VL-MFI-14 | 1 | -0.0030 | -0.611 | 7.76e-01 | no | 9176 |
| VL-EOM-14 | 1 | -0.0074 | -0.584 | 4.97e-01 | no | 9175 |
| VL-PVT-SLOPE-5 | 1 | -0.0276 | -0.460 | 1.10e-02 | yes | 9183 |
| VL-AD-SLOPE-5 | 1 | -0.0359 | -0.453 | 4.32e-04 | yes | 9184 |

**Slot winner: VL-ADOSC-3-10** (h=1, IC=-0.0358, IC_IR=-0.747). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

## ^STOXX50E — Euro Stoxx 50 (equity)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | -0.0285 | -0.937 | 5.37e-02 | no | 4779 |
| TR-VORTEX-14 | 1 | -0.0383 | -0.705 | 6.43e-03 | yes | 4808 |
| TR-AROONOSC-14 | 1 | -0.0397 | -0.584 | 4.76e-03 | yes | 4808 |
| TR-QSTICK-10 | 1 | -0.0345 | -0.572 | 1.96e-02 | no | 4813 |
| TR-TRIX-15 | 5 | -0.0660 | -0.511 | 1.42e-02 | yes | 4775 |
| TR-MACDH-12-26-9 | 1 | -0.0169 | -0.417 | 2.56e-01 | no | 4789 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-SUPERT-10-3 | 20 | -0.00827 | 2233 |
| TR-PSAR-CROSS | 20 | -0.00573 | 2081 |
| TR-PSAR-CROSS | 10 | -0.00377 | 2081 |
| TR-SUPERT-10-3 | 10 | -0.00308 | 2233 |

**Slot winner: TR-VORTEX-14** (h=1, IC=-0.0383, IC_IR=-0.705). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | -0.0346 | -1.128 | 1.48e-02 | yes | 4785 |
| MO-RSI-14 | 1 | -0.0462 | -1.068 | 1.03e-03 | yes | 4809 |
| MO-AO-5-34 | 1 | -0.0275 | -0.831 | 6.05e-02 | no | 4789 |
| MO-CMO-14 | 1 | -0.0408 | -0.732 | 3.42e-03 | yes | 4808 |
| MO-CCI-20 | 1 | -0.0436 | -0.672 | 1.98e-03 | yes | 4803 |
| MO-FISHER-9 | 1 | -0.0267 | -0.657 | 5.66e-02 | no | 4814 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | +0.02123 | 116 |
| MO-RSI-THRESH-14 | 5 | +0.00380 | 116 |
| MO-RSI-THRESH-14 | 1 | +0.00264 | 116 |
| MO-RSI-THRESH-14 | 10 | +0.00202 | 116 |

**Slot winner: MO-TSI-13-25** (h=1, IC=-0.0346, IC_IR=-1.128). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-ATRRATIO-14 | 1 | 0.0294 | 1.024 | 4.34e-02 | no | 4809 |
| VO-NATR-14 | 1 | 0.0310 | 0.865 | 3.29e-02 | no | 4808 |
| VO-UI-14 | 1 | 0.0375 | 0.850 | 9.33e-03 | yes | 4796 |
| VO-KCW-20 | 1 | 0.0284 | 0.841 | 5.05e-02 | no | 4802 |
| VO-RVI-14 | 1 | -0.0317 | -0.721 | 2.48e-02 | no | 4796 |
| VO-BBP-20-2 | 1 | -0.0416 | -0.663 | 3.04e-03 | yes | 4803 |

**Slot winner: VO-UI-14** (h=1, IC=0.0375, IC_IR=0.850). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-MFI-14 | 1 | -0.0451 | -0.783 | 6.68e-03 | yes | 3236 |
| VL-EOM-14 | 1 | -0.0399 | -0.670 | 2.76e-02 | no | 3052 |
| VL-CMF-20 | 1 | -0.0125 | -0.506 | 4.59e-01 | no | 3236 |
| VL-MFI-14 | 5 | -0.0861 | -0.372 | 4.11e-03 | yes | 3232 |
| VL-EOM-14 | 5 | -0.0660 | -0.369 | 4.26e-02 | no | 3048 |
| VL-CMF-20 | 5 | -0.0588 | -0.324 | 5.26e-02 | no | 3232 |

**Slot winner: VL-MFI-14** (h=1, IC=-0.0451, IC_IR=-0.783). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

## ^FTSE — FTSE 100 (equity)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | -0.0322 | -0.934 | 3.67e-03 | yes | 9173 |
| TR-VORTEX-14 | 1 | -0.0390 | -0.666 | 1.53e-04 | yes | 9202 |
| TR-AROONOSC-14 | 1 | -0.0387 | -0.568 | 1.66e-04 | yes | 9202 |
| TR-QSTICK-10 | 1 | -0.0362 | -0.531 | 9.80e-04 | yes | 9207 |
| TR-TRIX-15 | 5 | -0.0712 | -0.505 | 3.89e-04 | yes | 9169 |
| TR-MACDH-12-26-9 | 1 | -0.0258 | -0.460 | 1.81e-02 | no | 9183 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-SUPERT-10-3 | 20 | -0.00578 | 4092 |
| TR-PSAR-CROSS | 20 | -0.00463 | 4081 |
| TR-MACD-CROSS-12-26-9 | 20 | -0.00328 | 4548 |
| TR-EMACROSS-50-200 | 20 | -0.00305 | 2665 |

**Slot winner: TR-TRIX-15** (h=1, IC=-0.0322, IC_IR=-0.934). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | -0.0392 | -1.119 | 2.13e-04 | yes | 9179 |
| MO-RSI-14 | 1 | -0.0399 | -0.929 | 1.37e-04 | yes | 9203 |
| MO-AO-5-34 | 1 | -0.0424 | -0.915 | 1.03e-04 | yes | 9183 |
| MO-CCI-20 | 1 | -0.0411 | -0.632 | 7.21e-05 | yes | 9197 |
| MO-FISHER-9 | 1 | -0.0382 | -0.632 | 2.01e-04 | yes | 9208 |
| MO-CMO-14 | 1 | -0.0335 | -0.623 | 1.12e-03 | yes | 9202 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | +0.01215 | 219 |
| MO-RSI-THRESH-14 | 10 | +0.00861 | 219 |
| MO-RSI-THRESH-14 | 5 | +0.00822 | 219 |
| MO-RSI-THRESH-14 | 1 | +0.00190 | 219 |

**Slot winner: MO-TSI-13-25** (h=1, IC=-0.0392, IC_IR=-1.119). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-UI-14 | 1 | 0.0443 | 0.893 | 3.43e-05 | yes | 9190 |
| VO-ATRRATIO-14 | 1 | 0.0232 | 0.836 | 3.09e-02 | no | 9203 |
| VO-NATR-14 | 1 | 0.0281 | 0.724 | 9.12e-03 | yes | 9202 |
| VO-KCW-20 | 1 | 0.0246 | 0.691 | 2.21e-02 | no | 9196 |
| VO-BBP-20-2 | 1 | -0.0351 | -0.596 | 6.83e-04 | yes | 9197 |
| VO-RVI-14 | 1 | -0.0374 | -0.593 | 2.95e-04 | yes | 9190 |

**Slot winner: VO-UI-14** (h=1, IC=0.0443, IC_IR=0.893). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-EOM-14 | 1 | -0.0498 | -0.713 | 7.16e-05 | yes | 6915 |
| VL-MFI-14 | 1 | -0.0480 | -0.666 | 4.21e-05 | yes | 6942 |
| VL-CMF-20 | 1 | -0.0408 | -0.589 | 5.15e-04 | yes | 6942 |
| VL-ADOSC-3-10 | 1 | -0.0317 | -0.432 | 2.40e-03 | yes | 9207 |
| VL-EOM-14 | 5 | -0.0948 | -0.393 | 9.71e-06 | yes | 6911 |
| VL-PVT-SLOPE-5 | 1 | -0.0347 | -0.342 | 1.32e-03 | yes | 9210 |

**Slot winner: VL-EOM-14** (h=1, IC=-0.0498, IC_IR=-0.713). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

## ^GDAXI — DAX (equity)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | -0.0034 | -0.885 | 7.65e-01 | no | 9188 |
| TR-VORTEX-14 | 1 | -0.0145 | -0.597 | 1.61e-01 | no | 9217 |
| TR-AROONOSC-14 | 1 | -0.0208 | -0.582 | 4.48e-02 | no | 9217 |
| TR-TRIX-15 | 5 | -0.0170 | -0.488 | 4.06e-01 | no | 9184 |
| TR-MACDH-12-26-9 | 1 | -0.0141 | -0.451 | 1.87e-01 | no | 9198 |
| TR-QSTICK-10 | 1 | -0.0117 | -0.388 | 2.74e-01 | no | 9222 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-PSAR-CROSS | 20 | -0.00356 | 3921 |
| TR-PSAR-CROSS | 10 | -0.00309 | 3926 |
| TR-EMACROSS-50-200 | 20 | +0.00248 | 2586 |
| TR-PSAR-CROSS | 5 | -0.00178 | 3931 |

**Slot winner: TR-ADX-14** (h=20, IC=0.1209, IC_IR=0.026). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | -0.0096 | -1.047 | 3.66e-01 | no | 9194 |
| MO-RSI-14 | 1 | -0.0183 | -0.876 | 8.02e-02 | no | 9218 |
| MO-AO-5-34 | 1 | -0.0122 | -0.875 | 2.60e-01 | no | 9198 |
| MO-FISHER-9 | 1 | -0.0178 | -0.667 | 8.47e-02 | no | 9223 |
| MO-CMO-14 | 1 | -0.0132 | -0.651 | 2.02e-01 | no | 9217 |
| MO-MOM-10 | 1 | -0.0242 | -0.602 | 2.31e-02 | no | 9221 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 10 | -0.00390 | 254 |
| MO-RSI-THRESH-14 | 20 | +0.00285 | 254 |
| MO-STOCH-CROSS-14 | 20 | +0.00120 | 4556 |
| MO-RSI-THRESH-14 | 1 | +0.00069 | 254 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-UI-14 | 1 | 0.0151 | 0.786 | 1.57e-01 | no | 9205 |
| VO-ATRRATIO-14 | 1 | 0.0154 | 0.740 | 1.52e-01 | no | 9218 |
| VO-RVI-14 | 1 | -0.0236 | -0.653 | 2.33e-02 | no | 9205 |
| VO-NATR-14 | 1 | 0.0160 | 0.630 | 1.39e-01 | no | 9217 |
| VO-KCW-20 | 1 | 0.0149 | 0.599 | 1.66e-01 | no | 9211 |
| VO-BBP-20-2 | 1 | -0.0160 | -0.529 | 1.20e-01 | no | 9212 |

**Slot winner: VO-DCW-20** (h=5, IC=0.0544, IC_IR=0.154). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-EOM-14 | 1 | -0.0228 | -0.689 | 6.44e-02 | no | 6637 |
| VL-MFI-14 | 1 | -0.0120 | -0.613 | 3.22e-01 | no | 6768 |
| VL-CMF-20 | 1 | 0.0047 | -0.450 | 6.86e-01 | no | 6768 |
| VL-EOM-14 | 5 | -0.0423 | -0.389 | 4.83e-02 | no | 6633 |
| VL-MFI-14 | 5 | -0.0299 | -0.335 | 1.65e-01 | no | 6764 |
| VL-CMF-20 | 5 | -0.0173 | -0.296 | 4.16e-01 | no | 6764 |

**Slot winner: VL-PVT-SLOPE-5** (h=5, IC=-0.0412, IC_IR=-0.166). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

## ^N225 — Nikkei 225 (equity)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0042 | -0.801 | 7.09e-01 | no | 8911 |
| TR-VORTEX-14 | 1 | -0.0033 | -0.549 | 7.60e-01 | no | 8940 |
| TR-QSTICK-10 | 1 | -0.0124 | -0.457 | 2.55e-01 | no | 8945 |
| TR-TRIX-15 | 5 | -0.0003 | -0.445 | 9.88e-01 | no | 8907 |
| TR-MACDH-12-26-9 | 1 | -0.0113 | -0.436 | 3.00e-01 | no | 8921 |
| TR-AROONOSC-14 | 1 | -0.0009 | -0.428 | 9.30e-01 | no | 8940 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-EMACROSS-50-200 | 20 | +0.00386 | 3902 |
| TR-SUPERT-10-3 | 20 | -0.00283 | 4272 |
| TR-PSAR-CROSS | 20 | -0.00256 | 4091 |
| TR-EMACROSS-50-200 | 10 | +0.00252 | 3902 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0030 | -0.896 | 7.82e-01 | no | 8917 |
| MO-RSI-14 | 1 | -0.0046 | -0.823 | 6.63e-01 | no | 8941 |
| MO-AO-5-34 | 1 | -0.0013 | -0.750 | 9.03e-01 | no | 8921 |
| MO-FISHER-9 | 1 | -0.0142 | -0.625 | 1.78e-01 | no | 8946 |
| MO-STOCH-14 | 1 | -0.0113 | -0.589 | 2.78e-01 | no | 8939 |
| MO-CMO-14 | 1 | -0.0050 | -0.563 | 6.35e-01 | no | 8940 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 10 | -0.00634 | 294 |
| MO-RSI-THRESH-14 | 20 | -0.00400 | 294 |
| MO-RSI-THRESH-14 | 1 | +0.00288 | 294 |
| MO-STOCH-CROSS-14 | 20 | -0.00275 | 4433 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-ATRRATIO-14 | 1 | 0.0102 | 0.656 | 3.37e-01 | no | 8941 |
| VO-UI-14 | 1 | 0.0054 | 0.651 | 6.17e-01 | no | 8928 |
| VO-RVI-14 | 1 | -0.0237 | -0.623 | 2.39e-02 | no | 8928 |
| VO-NATR-14 | 1 | 0.0128 | 0.552 | 2.29e-01 | no | 8940 |
| VO-BBP-20-2 | 1 | -0.0031 | -0.503 | 7.68e-01 | no | 8935 |
| VO-KCW-20 | 1 | 0.0110 | 0.490 | 3.02e-01 | no | 8934 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-MFI-14 | 1 | -0.0193 | -0.600 | 1.36e-01 | no | 5889 |
| VL-EOM-14 | 1 | -0.0140 | -0.548 | 3.00e-01 | no | 5742 |
| VL-CMF-20 | 1 | -0.0229 | -0.422 | 7.86e-02 | no | 5889 |
| VL-EOM-14 | 5 | -0.0106 | -0.317 | 6.48e-01 | no | 5738 |
| VL-MFI-14 | 5 | -0.0242 | -0.300 | 2.96e-01 | no | 5885 |
| VL-ADOSC-3-10 | 1 | -0.0191 | -0.292 | 6.62e-02 | no | 8945 |

**NO SLOT WINNER — nothing in this category survives FDR.**

## ^KS11 — KOSPI (equity)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0291 | -0.773 | 3.06e-02 | no | 7230 |
| TR-VORTEX-14 | 1 | 0.0203 | -0.458 | 9.43e-02 | no | 7259 |
| TR-TRIX-15 | 5 | 0.0307 | -0.445 | 2.03e-01 | no | 7226 |
| TR-QSTICK-10 | 1 | -0.0091 | -0.445 | 4.56e-01 | no | 7264 |
| TR-AROONOSC-14 | 1 | 0.0056 | -0.425 | 6.45e-01 | no | 7259 |
| TR-MACDH-12-26-9 | 1 | -0.0055 | -0.406 | 6.54e-01 | no | 7240 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-EMACROSS-50-200 | 20 | +0.00617 | 2829 |
| TR-MACD-CROSS-12-26-9 | 20 | +0.00447 | 3456 |
| TR-PSAR-CROSS | 20 | +0.00349 | 3199 |
| TR-MACD-CROSS-12-26-9 | 10 | +0.00347 | 3463 |

**Slot winner: TR-VORTEX-14** (h=10, IC=0.0657, IC_IR=-0.198). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0203 | -0.859 | 1.05e-01 | no | 7236 |
| MO-RSI-14 | 1 | 0.0178 | -0.754 | 1.46e-01 | no | 7260 |
| MO-AO-5-34 | 1 | 0.0215 | -0.676 | 8.87e-02 | no | 7240 |
| MO-UO-7-14-28 | 1 | -0.0051 | -0.555 | 6.73e-01 | no | 7246 |
| MO-FISHER-9 | 1 | 0.0066 | -0.539 | 5.86e-01 | no | 7265 |
| MO-MOM-10 | 1 | 0.0018 | -0.524 | 8.87e-01 | no | 7263 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | -0.01906 | 270 |
| MO-RSI-THRESH-14 | 5 | +0.00889 | 270 |
| MO-RSI-THRESH-14 | 10 | -0.00475 | 270 |
| MO-STOCH-CROSS-14 | 10 | -0.00278 | 3615 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-ATRRATIO-14 | 1 | 0.0450 | 0.657 | 3.11e-04 | yes | 7260 |
| VO-UI-14 | 1 | 0.0081 | 0.604 | 5.13e-01 | no | 7247 |
| VO-NATR-14 | 1 | 0.0449 | 0.511 | 3.11e-04 | yes | 7259 |
| VO-RVI-14 | 1 | 0.0145 | -0.505 | 2.20e-01 | no | 7247 |
| VO-KCW-20 | 1 | 0.0450 | 0.487 | 3.02e-04 | yes | 7253 |
| VO-BBP-20-2 | 1 | 0.0195 | -0.441 | 9.84e-02 | no | 7254 |

**Slot winner: VO-ATRRATIO-14** (h=1, IC=0.0450, IC_IR=0.657). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-ADOSC-3-10 | 1 | -0.0175 | -0.615 | 1.40e-01 | no | 7264 |
| VL-EOM-14 | 1 | -0.0010 | -0.510 | 9.40e-01 | no | 7243 |
| VL-AD-SLOPE-5 | 1 | -0.0280 | -0.439 | 1.70e-02 | yes | 7268 |
| VL-CMF-20 | 1 | 0.0065 | -0.438 | 5.92e-01 | no | 7254 |
| VL-PVT-SLOPE-5 | 1 | 0.0037 | -0.410 | 7.67e-01 | no | 7267 |
| VL-MFI-14 | 1 | 0.0235 | -0.402 | 4.99e-02 | no | 7260 |

**Slot winner: VL-AD-SLOPE-5** (h=1, IC=-0.0280, IC_IR=-0.439). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

## ^HSI — Hang Seng (equity)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0157 | -0.847 | 1.72e-01 | no | 8960 |
| TR-TRIX-15 | 5 | 0.0135 | -0.490 | 5.23e-01 | no | 8956 |
| TR-AROONOSC-14 | 1 | -0.0007 | -0.445 | 9.45e-01 | no | 8989 |
| TR-VORTEX-14 | 1 | 0.0186 | -0.409 | 8.15e-02 | no | 8989 |
| TR-TRIX-15 | 10 | 0.0084 | -0.348 | 7.70e-01 | no | 8951 |
| TR-MACDH-12-26-9 | 1 | 0.0038 | -0.309 | 7.29e-01 | no | 8970 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-EMACROSS-50-200 | 20 | +0.00593 | 3118 |
| TR-PSAR-CROSS | 20 | -0.00298 | 4116 |
| TR-EMACROSS-50-200 | 10 | +0.00239 | 3118 |
| TR-MACD-CROSS-12-26-9 | 10 | +0.00199 | 4468 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0158 | -0.861 | 1.53e-01 | no | 8966 |
| MO-AO-5-34 | 1 | 0.0037 | -0.759 | 7.40e-01 | no | 8970 |
| MO-RSI-14 | 1 | 0.0218 | -0.634 | 4.28e-02 | no | 8990 |
| MO-TSI-13-25 | 5 | 0.0131 | -0.518 | 5.15e-01 | no | 8962 |
| MO-FISHER-9 | 1 | 0.0055 | -0.482 | 6.07e-01 | no | 8995 |
| MO-RSI-14 | 5 | 0.0158 | -0.438 | 4.12e-01 | no | 8986 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | +0.00636 | 347 |
| MO-RSI-THRESH-14 | 5 | +0.00132 | 348 |
| MO-STOCH-CROSS-14 | 10 | -0.00110 | 4467 |
| MO-RSI-THRESH-14 | 1 | -0.00103 | 351 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-UI-14 | 1 | -0.0101 | 0.610 | 3.58e-01 | no | 8977 |
| VO-ATRRATIO-14 | 1 | -0.0131 | 0.495 | 2.32e-01 | no | 8990 |
| VO-RVI-14 | 1 | 0.0115 | -0.449 | 2.71e-01 | no | 8977 |
| VO-NATR-14 | 1 | -0.0078 | 0.425 | 4.76e-01 | no | 8989 |
| VO-KCW-20 | 1 | -0.0094 | 0.379 | 3.90e-01 | no | 8983 |
| VO-BBP-20-2 | 1 | 0.0236 | -0.343 | 2.41e-02 | no | 8984 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-EOM-14 | 1 | -0.0057 | -0.590 | 6.67e-01 | no | 6080 |
| VL-MFI-14 | 1 | 0.0068 | -0.477 | 5.93e-01 | no | 6154 |
| VL-CMF-20 | 1 | 0.0099 | -0.392 | 4.41e-01 | no | 6154 |
| VL-EOM-14 | 5 | 0.0057 | -0.298 | 8.05e-01 | no | 6076 |
| VL-ADOSC-3-10 | 1 | 0.0025 | -0.273 | 8.12e-01 | no | 8994 |
| VL-MFI-14 | 5 | -0.0009 | -0.264 | 9.67e-01 | no | 6150 |

**NO SLOT WINNER — nothing in this category survives FDR.**

## ^TNX — US 10Y yield (rates)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0121 | -0.738 | 2.72e-01 | no | 9113 |
| TR-VORTEX-14 | 1 | -0.0010 | -0.499 | 9.27e-01 | no | 9142 |
| TR-MACDH-12-26-9 | 1 | -0.0173 | -0.498 | 1.14e-01 | no | 9123 |
| TR-AROONOSC-14 | 1 | 0.0067 | -0.420 | 5.25e-01 | no | 9142 |
| TR-TRIX-15 | 5 | 0.0282 | -0.394 | 1.52e-01 | no | 9109 |
| TR-QSTICK-10 | 1 | -0.0012 | -0.391 | 9.12e-01 | no | 9147 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-SUPERT-10-3 | 20 | +0.03016 | 4496 |
| TR-SUPERT-10-3 | 10 | +0.01904 | 4496 |
| TR-MACD-CROSS-12-26-9 | 20 | +0.01751 | 4394 |
| TR-MACD-CROSS-12-26-9 | 10 | +0.01409 | 4394 |

**Slot winner: TR-AROONOSC-14** (h=10, IC=0.0609, IC_IR=-0.130). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0114 | -0.878 | 2.96e-01 | no | 9119 |
| MO-RSI-14 | 1 | 0.0036 | -0.803 | 7.38e-01 | no | 9143 |
| MO-AO-5-34 | 1 | 0.0045 | -0.763 | 6.88e-01 | no | 9123 |
| MO-FISHER-9 | 1 | -0.0109 | -0.605 | 2.99e-01 | no | 9148 |
| MO-ROC-10 | 1 | -0.0138 | -0.594 | 1.95e-01 | no | 9146 |
| MO-MOM-10 | 1 | -0.0085 | -0.593 | 4.32e-01 | no | 9146 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | -0.06736 | 393 |
| MO-RSI-THRESH-14 | 10 | -0.05622 | 393 |
| MO-STOCH-CROSS-14 | 5 | -0.01301 | 4377 |
| MO-STOCH-CROSS-14 | 10 | -0.01200 | 4377 |

**Slot winner: MO-CMO-14** (h=10, IC=0.0591, IC_IR=-0.184). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-RVI-14 | 1 | -0.0209 | -0.625 | 4.65e-02 | no | 9130 |
| VO-UI-14 | 1 | 0.0129 | 0.588 | 2.28e-01 | no | 9130 |
| VO-BBP-20-2 | 1 | 0.0009 | -0.555 | 9.32e-01 | no | 9137 |
| VO-ATRRATIO-14 | 1 | 0.0235 | 0.422 | 2.82e-02 | no | 9143 |
| VO-NATR-14 | 1 | 0.0244 | 0.326 | 2.40e-02 | no | 9142 |
| VO-BBP-20-2 | 5 | 0.0082 | -0.299 | 6.47e-01 | no | 9133 |

**Slot winner: VO-ATRRATIO-14** (h=5, IC=0.0601, IC_IR=0.203). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-CMF-20 | 1 | 0.0586 | 1.237 | 4.90e-01 | no | 125 |
| VL-CMF-20 | 20 | -0.1971 | -1.180 | 4.37e-01 | no | 125 |
| VL-CMF-20 | 10 | -0.1110 | -0.622 | 5.96e-01 | no | 125 |
| VL-CMF-20 | 5 | 0.0096 | 0.225 | 9.50e-01 | no | 125 |
| VL-ADOSC-3-10 | 20 | 0.0750 | -0.006 | 5.10e-02 | no | 9128 |
| VL-AD-SLOPE-5 | 20 | -0.0071 | -0.005 | 7.14e-01 | no | 9132 |

**Slot winner: VL-OBV-SLOPE-5** (h=20, IC=0.0293, IC_IR=-0.003). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

## TLT — US 20Y+ UST (rates)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0005 | -0.804 | 9.73e-01 | no | 5974 |
| TR-VORTEX-14 | 1 | -0.0224 | -0.604 | 7.93e-02 | no | 6003 |
| TR-MACDH-12-26-9 | 1 | -0.0304 | -0.502 | 2.27e-02 | no | 5984 |
| TR-QSTICK-10 | 1 | -0.0280 | -0.497 | 3.80e-02 | no | 6008 |
| TR-AROONOSC-14 | 1 | -0.0116 | -0.441 | 3.59e-01 | no | 6003 |
| TR-TRIX-15 | 5 | 0.0073 | -0.420 | 7.71e-01 | no | 5970 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-MACD-CROSS-12-26-9 | 20 | +0.00258 | 2841 |
| TR-PSAR-CROSS | 20 | +0.00130 | 2980 |
| TR-EMACROSS-50-200 | 20 | -0.00104 | 2228 |
| TR-SUPERT-10-3 | 20 | +0.00091 | 2942 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-RSI-14 | 1 | -0.0234 | -0.906 | 6.67e-02 | no | 6004 |
| MO-TSI-13-25 | 1 | -0.0074 | -0.905 | 5.69e-01 | no | 5980 |
| MO-AO-5-34 | 1 | -0.0078 | -0.755 | 5.65e-01 | no | 5984 |
| MO-MOM-10 | 1 | -0.0329 | -0.649 | 1.35e-02 | yes | 6007 |
| MO-ROC-10 | 1 | -0.0328 | -0.647 | 1.32e-02 | yes | 6007 |
| MO-CCI-20 | 1 | -0.0204 | -0.630 | 1.04e-01 | no | 5998 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | -0.00644 | 135 |
| MO-RSI-THRESH-14 | 5 | +0.00316 | 135 |
| MO-RSI-THRESH-14 | 10 | -0.00254 | 135 |
| MO-STOCH-CROSS-14 | 5 | -0.00162 | 2901 |

**Slot winner: MO-MOM-10** (h=1, IC=-0.0329, IC_IR=-0.649). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-RVI-14 | 1 | -0.0445 | -0.729 | 4.41e-04 | yes | 5991 |
| VO-BBP-20-2 | 1 | -0.0241 | -0.661 | 5.48e-02 | no | 5998 |
| VO-UI-14 | 1 | 0.0008 | 0.499 | 9.50e-01 | no | 5991 |
| VO-RVI-14 | 5 | -0.0434 | -0.313 | 4.40e-02 | no | 5987 |
| VO-BBP-20-2 | 5 | -0.0061 | -0.302 | 7.79e-01 | no | 5994 |
| VO-UI-14 | 5 | -0.0156 | 0.252 | 5.21e-01 | no | 5987 |

**Slot winner: VO-RVI-14** (h=1, IC=-0.0445, IC_IR=-0.729). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-ADOSC-3-10 | 1 | -0.0594 | -0.681 | 8.42e-06 | yes | 6008 |
| VL-EOM-14 | 1 | -0.0115 | -0.627 | 3.80e-01 | no | 6003 |
| VL-MFI-14 | 1 | -0.0232 | -0.605 | 6.84e-02 | no | 6004 |
| VL-OBV-SLOPE-5 | 1 | -0.0558 | -0.541 | 3.15e-05 | yes | 6012 |
| VL-CMF-20 | 1 | -0.0222 | -0.536 | 8.19e-02 | no | 5998 |
| VL-AD-SLOPE-5 | 1 | -0.0590 | -0.495 | 8.17e-06 | yes | 6012 |

**Slot winner: VL-ADOSC-3-10** (h=1, IC=-0.0594, IC_IR=-0.681). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

## LQD — IG corporate (credit)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0133 | -0.753 | 3.34e-01 | no | 5974 |
| TR-VORTEX-14 | 1 | -0.0011 | -0.483 | 9.32e-01 | no | 6003 |
| TR-QSTICK-10 | 1 | -0.0211 | -0.465 | 1.20e-01 | no | 6008 |
| TR-MACDH-12-26-9 | 1 | -0.0037 | -0.399 | 7.88e-01 | no | 5984 |
| TR-TRIX-15 | 5 | 0.0309 | -0.392 | 2.35e-01 | no | 5970 |
| TR-AROONOSC-14 | 1 | 0.0048 | -0.382 | 7.06e-01 | no | 6003 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-MACD-CROSS-12-26-9 | 20 | +0.00221 | 2801 |
| TR-PSAR-CROSS | 20 | +0.00206 | 2552 |
| TR-MACD-CROSS-12-26-9 | 10 | +0.00131 | 2802 |
| TR-PSAR-CROSS | 10 | +0.00108 | 2552 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0021 | -0.871 | 8.76e-01 | no | 5980 |
| MO-RSI-14 | 1 | -0.0041 | -0.764 | 7.54e-01 | no | 6004 |
| MO-AO-5-34 | 1 | 0.0013 | -0.707 | 9.23e-01 | no | 5984 |
| MO-UO-7-14-28 | 1 | -0.0305 | -0.652 | 1.82e-02 | no | 5990 |
| MO-CMO-14 | 1 | 0.0017 | -0.506 | 8.98e-01 | no | 6003 |
| MO-WILLR-14 | 1 | -0.0145 | -0.490 | 2.58e-01 | no | 6004 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | +0.00430 | 142 |
| MO-RSI-THRESH-14 | 5 | +0.00244 | 142 |
| MO-RSI-THRESH-14 | 10 | +0.00209 | 142 |
| MO-STOCH-CROSS-14 | 5 | -0.00072 | 2942 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-RVI-14 | 1 | -0.0170 | -0.550 | 1.84e-01 | no | 5991 |
| VO-UI-14 | 1 | 0.0027 | 0.549 | 8.36e-01 | no | 5991 |
| VO-BBP-20-2 | 1 | -0.0078 | -0.477 | 5.47e-01 | no | 5998 |
| VO-UI-14 | 5 | -0.0128 | 0.270 | 6.09e-01 | no | 5987 |
| VO-BBP-20-2 | 5 | 0.0135 | -0.266 | 5.52e-01 | no | 5994 |
| VO-ATRRATIO-14 | 1 | 0.0192 | 0.260 | 1.44e-01 | no | 6004 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-ADOSC-3-10 | 1 | -0.0213 | -0.559 | 1.06e-01 | no | 6008 |
| VL-EOM-14 | 1 | 0.0096 | -0.505 | 4.64e-01 | no | 6003 |
| VL-CMF-20 | 1 | -0.0132 | -0.476 | 3.01e-01 | no | 5998 |
| VL-AD-SLOPE-5 | 1 | -0.0313 | -0.413 | 1.82e-02 | no | 6012 |
| VL-MFI-14 | 1 | 0.0051 | -0.410 | 6.85e-01 | no | 6004 |
| VL-PVT-SLOPE-5 | 1 | -0.0146 | -0.373 | 2.79e-01 | no | 6011 |

**NO SLOT WINNER — nothing in this category survives FDR.**

## HYG — HY corporate (credit)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0060 | -0.938 | 7.18e-01 | no | 4792 |
| TR-VORTEX-14 | 1 | -0.0033 | -0.565 | 8.28e-01 | no | 4821 |
| TR-TRIX-15 | 5 | -0.0105 | -0.536 | 7.27e-01 | no | 4788 |
| TR-TRIX-15 | 10 | -0.0555 | -0.412 | 1.64e-01 | no | 4783 |
| TR-VORTEX-14 | 5 | -0.0415 | -0.403 | 1.06e-01 | no | 4817 |
| TR-AROONOSC-14 | 1 | 0.0007 | -0.385 | 9.60e-01 | no | 4821 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-PSAR-CROSS | 20 | -0.00372 | 1890 |
| TR-SUPERT-10-3 | 20 | -0.00337 | 1620 |
| TR-MACD-CROSS-12-26-9 | 20 | -0.00104 | 2339 |
| TR-MACD-CROSS-12-26-9 | 5 | +0.00101 | 2349 |

**Slot winner: TR-VORTEX-14** (h=20, IC=-0.1027, IC_IR=-0.307). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | -0.0175 | -1.118 | 2.57e-01 | no | 4798 |
| MO-AO-5-34 | 1 | -0.0103 | -0.831 | 5.29e-01 | no | 4802 |
| MO-RSI-14 | 1 | -0.0096 | -0.809 | 5.30e-01 | no | 4822 |
| MO-TSI-13-25 | 5 | -0.0496 | -0.610 | 6.97e-02 | no | 4794 |
| MO-CMO-14 | 1 | -0.0031 | -0.573 | 8.38e-01 | no | 4821 |
| MO-RSI-14 | 5 | -0.0418 | -0.555 | 1.11e-01 | no | 4818 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | +0.01805 | 146 |
| MO-RSI-THRESH-14 | 10 | +0.01108 | 146 |
| MO-RSI-THRESH-14 | 5 | +0.00866 | 146 |
| MO-STOCH-CROSS-14 | 20 | +0.00181 | 2388 |

**Slot winner: MO-TSI-13-25** (h=10, IC=-0.0904, IC_IR=-0.503). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-UI-14 | 1 | 0.0440 | 0.827 | 3.76e-03 | yes | 4809 |
| VO-ATRRATIO-14 | 1 | 0.0519 | 0.807 | 6.04e-04 | yes | 4822 |
| VO-KCW-20 | 1 | 0.0518 | 0.750 | 6.17e-04 | yes | 4815 |
| VO-NATR-14 | 1 | 0.0522 | 0.730 | 5.51e-04 | yes | 4821 |
| VO-ATRRATIO-14 | 5 | 0.1044 | 0.450 | 1.52e-04 | yes | 4818 |
| VO-NATR-14 | 5 | 0.1066 | 0.437 | 9.89e-05 | yes | 4817 |

**Slot winner: VO-UI-14** (h=1, IC=0.0440, IC_IR=0.827). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-CMF-20 | 1 | -0.0282 | -0.577 | 5.72e-02 | no | 4816 |
| VL-ADOSC-3-10 | 1 | -0.0301 | -0.520 | 3.35e-02 | no | 4826 |
| VL-MFI-14 | 1 | -0.0063 | -0.512 | 6.74e-01 | no | 4822 |
| VL-EOM-14 | 1 | 0.0239 | -0.479 | 1.47e-01 | no | 4821 |
| VL-EOM-14 | 5 | -0.0298 | -0.362 | 2.91e-01 | no | 4817 |
| VL-PVT-SLOPE-5 | 1 | -0.0141 | -0.350 | 3.48e-01 | no | 4829 |

**Slot winner: VL-CMF-20** (h=5, IC=-0.0679, IC_IR=-0.312). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

## GC=F — Gold (metals)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0056 | -0.772 | 6.63e-01 | no | 6438 |
| TR-VORTEX-14 | 1 | 0.0006 | -0.493 | 9.62e-01 | no | 6467 |
| TR-TRIX-15 | 5 | -0.0094 | -0.455 | 7.00e-01 | no | 6434 |
| TR-AROONOSC-14 | 1 | -0.0064 | -0.431 | 5.93e-01 | no | 6467 |
| TR-MACDH-12-26-9 | 1 | -0.0060 | -0.406 | 6.34e-01 | no | 6448 |
| TR-QSTICK-10 | 1 | 0.0063 | -0.380 | 6.20e-01 | no | 6472 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-PSAR-CROSS | 20 | -0.00566 | 2953 |
| TR-EMACROSS-50-200 | 20 | +0.00557 | 1437 |
| TR-MACD-CROSS-12-26-9 | 20 | -0.00389 | 3063 |
| TR-PSAR-CROSS | 10 | -0.00295 | 2961 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0044 | -0.889 | 7.17e-01 | no | 6444 |
| MO-RSI-14 | 1 | -0.0080 | -0.830 | 5.11e-01 | no | 6468 |
| MO-AO-5-34 | 1 | 0.0092 | -0.757 | 4.66e-01 | no | 6448 |
| MO-CMO-14 | 1 | -0.0080 | -0.614 | 5.07e-01 | no | 6467 |
| MO-TSI-13-25 | 5 | -0.0137 | -0.512 | 5.59e-01 | no | 6440 |
| MO-MOM-10 | 1 | -0.0073 | -0.493 | 5.67e-01 | no | 6471 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | +0.01534 | 178 |
| MO-RSI-THRESH-14 | 10 | +0.00991 | 180 |
| MO-RSI-THRESH-14 | 5 | +0.00489 | 181 |
| MO-STOCH-CROSS-14 | 10 | +0.00138 | 3199 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-RVI-14 | 1 | -0.0205 | -0.655 | 9.52e-02 | no | 6455 |
| VO-UI-14 | 1 | 0.0047 | 0.518 | 7.10e-01 | no | 6455 |
| VO-BBP-20-2 | 1 | -0.0072 | -0.499 | 5.54e-01 | no | 6462 |
| VO-BBP-20-2 | 5 | -0.0142 | -0.287 | 5.08e-01 | no | 6458 |
| VO-UI-14 | 5 | 0.0169 | 0.268 | 4.79e-01 | no | 6451 |
| VO-BBP-20-2 | 10 | -0.0283 | -0.262 | 2.92e-01 | no | 6453 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-MFI-14 | 1 | -0.0143 | -0.397 | 2.28e-01 | no | 6461 |
| VL-EOM-14 | 1 | 0.0093 | -0.357 | 5.07e-01 | no | 5156 |
| VL-CMF-20 | 1 | 0.0018 | -0.286 | 8.89e-01 | no | 6462 |
| VL-EOM-14 | 5 | 0.0131 | -0.205 | 5.89e-01 | no | 5152 |
| VL-EOM-14 | 10 | -0.0092 | -0.175 | 7.68e-01 | no | 5147 |
| VL-MFI-14 | 5 | -0.0193 | -0.175 | 3.59e-01 | no | 6457 |

**NO SLOT WINNER — nothing in this category survives FDR.**

## SI=F — Silver (metals)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0087 | -0.744 | 4.95e-01 | no | 6440 |
| TR-TRIX-15 | 5 | -0.0133 | -0.459 | 5.85e-01 | no | 6436 |
| TR-VORTEX-14 | 1 | 0.0084 | -0.362 | 4.92e-01 | no | 6469 |
| TR-MACDH-12-26-9 | 1 | -0.0023 | -0.339 | 8.54e-01 | no | 6450 |
| TR-TRIX-15 | 10 | -0.0279 | -0.326 | 4.01e-01 | no | 6431 |
| TR-AROONOSC-14 | 1 | 0.0096 | -0.316 | 4.26e-01 | no | 6469 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-EMACROSS-50-200 | 20 | +0.00549 | 2456 |
| TR-SUPERT-10-3 | 10 | +0.00323 | 3222 |
| TR-PSAR-CROSS | 20 | -0.00296 | 3067 |
| TR-EMACROSS-50-200 | 10 | +0.00260 | 2456 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0079 | -0.865 | 5.12e-01 | no | 6446 |
| MO-RSI-14 | 1 | 0.0017 | -0.805 | 8.92e-01 | no | 6470 |
| MO-AO-5-34 | 1 | 0.0079 | -0.712 | 5.37e-01 | no | 6450 |
| MO-CMO-14 | 1 | 0.0033 | -0.547 | 7.88e-01 | no | 6469 |
| MO-TSI-13-25 | 5 | -0.0177 | -0.522 | 4.49e-01 | no | 6442 |
| MO-UO-7-14-28 | 1 | -0.0067 | -0.478 | 5.77e-01 | no | 6456 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 10 | +0.00997 | 204 |
| MO-RSI-THRESH-14 | 20 | +0.00965 | 201 |
| MO-RSI-THRESH-14 | 5 | +0.00478 | 205 |
| MO-STOCH-CROSS-14 | 5 | +0.00072 | 3219 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-RVI-14 | 1 | -0.0093 | -0.584 | 4.40e-01 | no | 6457 |
| VO-BBP-20-2 | 1 | 0.0000 | -0.472 | 9.97e-01 | no | 6464 |
| VO-UI-14 | 1 | 0.0137 | 0.448 | 2.70e-01 | no | 6457 |
| VO-BBP-20-2 | 5 | -0.0070 | -0.291 | 7.46e-01 | no | 6460 |
| VO-UI-14 | 5 | 0.0382 | 0.263 | 1.14e-01 | no | 6453 |
| VO-BBP-20-2 | 10 | -0.0295 | -0.255 | 2.88e-01 | no | 6455 |

**Slot winner: VO-ATRRATIO-14** (h=1, IC=0.0324, IC_IR=0.201). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-CMF-20 | 1 | -0.0344 | -0.436 | 5.95e-03 | yes | 6456 |
| VL-MFI-14 | 1 | -0.0039 | -0.329 | 7.46e-01 | no | 6444 |
| VL-EOM-14 | 1 | 0.0041 | -0.254 | 8.09e-01 | no | 3684 |
| VL-PVT-SLOPE-5 | 1 | -0.0041 | -0.250 | 7.48e-01 | no | 6477 |
| VL-EOM-14 | 10 | -0.0579 | -0.246 | 1.43e-01 | no | 3684 |
| VL-EOM-14 | 5 | -0.0339 | -0.234 | 2.69e-01 | no | 3684 |

**Slot winner: VL-CMF-20** (h=1, IC=-0.0344, IC_IR=-0.436). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

## CL=F — WTI crude (energy)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0157 | -0.656 | 2.31e-01 | no | 6445 |
| TR-QSTICK-10 | 1 | -0.0074 | -0.560 | 5.57e-01 | no | 6479 |
| TR-VORTEX-14 | 1 | 0.0094 | -0.527 | 4.38e-01 | no | 6474 |
| TR-MACDH-12-26-9 | 1 | -0.0138 | -0.505 | 2.79e-01 | no | 6455 |
| TR-AROONOSC-14 | 1 | 0.0036 | -0.422 | 7.64e-01 | no | 6474 |
| TR-TRIX-15 | 5 | 0.0217 | -0.356 | 3.82e-01 | no | 6441 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-SUPERT-10-3 | 20 | +0.00811 | 3068 |
| TR-MACD-CROSS-12-26-9 | 20 | +0.00734 | 3065 |
| TR-SUPERT-10-3 | 10 | +0.00623 | 3078 |
| TR-PSAR-CROSS | 20 | +0.00607 | 3036 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0077 | -0.868 | 5.39e-01 | no | 6451 |
| MO-RSI-14 | 1 | -0.0005 | -0.868 | 9.67e-01 | no | 6475 |
| MO-AO-5-34 | 1 | 0.0111 | -0.693 | 3.83e-01 | no | 6455 |
| MO-UO-7-14-28 | 1 | -0.0091 | -0.692 | 4.54e-01 | no | 6461 |
| MO-STOCH-14 | 1 | -0.0027 | -0.637 | 8.22e-01 | no | 6473 |
| MO-WILLR-14 | 1 | -0.0107 | -0.633 | 3.73e-01 | no | 6475 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | -0.04366 | 287 |
| MO-RSI-THRESH-14 | 10 | -0.01548 | 287 |
| MO-STOCH-CROSS-14 | 10 | -0.00515 | 3197 |
| MO-STOCH-CROSS-14 | 5 | -0.00199 | 3200 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-ATRRATIO-14 | 1 | 0.0258 | 0.631 | 4.10e-02 | no | 6475 |
| VO-RVI-14 | 1 | -0.0071 | -0.613 | 5.60e-01 | no | 6462 |
| VO-UI-14 | 1 | 0.0039 | 0.596 | 7.59e-01 | no | 6462 |
| VO-BBP-20-2 | 1 | -0.0030 | -0.590 | 8.02e-01 | no | 6469 |
| VO-NATR-14 | 1 | 0.0218 | 0.408 | 8.43e-02 | no | 6474 |
| VO-BBP-20-2 | 5 | 0.0007 | -0.321 | 9.74e-01 | no | 6465 |

**Slot winner: VO-ATRRATIO-14** (h=10, IC=0.0813, IC_IR=0.243). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-ADOSC-3-10 | 1 | -0.0022 | -0.699 | 8.58e-01 | no | 6479 |
| VL-CMF-20 | 1 | 0.0121 | -0.661 | 3.33e-01 | no | 6469 |
| VL-EOM-14 | 1 | 0.0009 | -0.497 | 9.42e-01 | no | 6322 |
| VL-MFI-14 | 1 | 0.0164 | -0.466 | 1.80e-01 | no | 6475 |
| VL-AD-SLOPE-5 | 1 | -0.0072 | -0.460 | 5.59e-01 | no | 6483 |
| VL-PVT-SLOPE-5 | 1 | 0.0031 | -0.424 | 8.06e-01 | no | 6482 |

**NO SLOT WINNER — nothing in this category survives FDR.**

## DX-Y.NYB — USD index (fx)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0311 | -0.719 | 3.80e-03 | yes | 9256 |
| TR-VORTEX-14 | 1 | 0.0137 | -0.489 | 1.84e-01 | no | 9285 |
| TR-QSTICK-10 | 1 | -0.0002 | -0.458 | 9.82e-01 | no | 9290 |
| TR-TRIX-15 | 5 | 0.0475 | -0.430 | 1.73e-02 | no | 9252 |
| TR-MACDH-12-26-9 | 1 | -0.0074 | -0.414 | 4.83e-01 | no | 9266 |
| TR-AROONOSC-14 | 1 | 0.0111 | -0.364 | 2.79e-01 | no | 9285 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-SUPERT-10-3 | 20 | +0.00129 | 4542 |
| TR-MACD-CROSS-12-26-9 | 20 | +0.00124 | 4601 |
| TR-EMACROSS-50-200 | 20 | +0.00103 | 4315 |
| TR-SUPERT-10-3 | 10 | +0.00095 | 4550 |

**Slot winner: TR-TRIX-15** (h=1, IC=0.0311, IC_IR=-0.719). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-TSI-13-25 | 1 | 0.0264 | -0.836 | 1.09e-02 | yes | 9262 |
| MO-RSI-14 | 1 | 0.0104 | -0.829 | 3.13e-01 | no | 9286 |
| MO-AO-5-34 | 1 | 0.0233 | -0.681 | 2.91e-02 | no | 9266 |
| MO-ROC-10 | 1 | -0.0030 | -0.536 | 7.77e-01 | no | 9289 |
| MO-MOM-10 | 1 | -0.0030 | -0.536 | 7.77e-01 | no | 9289 |
| MO-CMO-14 | 1 | 0.0108 | -0.517 | 2.97e-01 | no | 9285 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | -0.00677 | 494 |
| MO-RSI-THRESH-14 | 10 | -0.00273 | 494 |
| MO-RSI-THRESH-14 | 5 | -0.00176 | 498 |
| MO-RSI-THRESH-14 | 1 | -0.00034 | 500 |

**Slot winner: MO-TSI-13-25** (h=1, IC=0.0264, IC_IR=-0.836). library prior SUPPRESS -> DISAGREES: expected to lose signal yet it tops the slot on flat history; possible regime-masking, flag for regime run.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-RVI-14 | 1 | -0.0177 | -0.638 | 8.08e-02 | no | 9273 |
| VO-BBP-20-2 | 1 | 0.0020 | -0.528 | 8.41e-01 | no | 9280 |
| VO-UI-14 | 1 | -0.0153 | 0.506 | 1.39e-01 | no | 9273 |
| VO-RVI-14 | 5 | -0.0062 | -0.296 | 7.29e-01 | no | 9269 |
| VO-UI-14 | 5 | -0.0301 | 0.286 | 1.18e-01 | no | 9269 |
| VO-BBP-20-2 | 5 | 0.0204 | -0.277 | 2.66e-01 | no | 9276 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volume slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VL-PVT-SLOPE-5 | 1 | 0.0147 | 0.011 | 1.93e-01 | no | 9293 |
| VL-AD-SLOPE-5 | 1 | 0.0147 | 0.011 | 1.93e-01 | no | 9294 |
| VL-OBV-SLOPE-5 | 1 | 0.0147 | 0.011 | 1.93e-01 | no | 9294 |
| VL-ADOSC-3-10 | 1 | 0.0056 | 0.008 | 5.77e-01 | no | 9290 |
| VL-ADOSC-3-10 | 20 | 0.0119 | -0.008 | 7.43e-01 | no | 9271 |
| VL-OBV-SLOPE-5 | 20 | -0.0046 | -0.007 | 1.37e-03 | yes | 9275 |

**Slot winner: VL-AD-SLOPE-5** (h=20, IC=-0.0046, IC_IR=-0.007). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

## EURUSD=X — EUR/USD (fx)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0114 | -0.784 | 4.02e-01 | no | 5815 |
| TR-MACDH-12-26-9 | 1 | -0.0254 | -0.523 | 5.98e-02 | no | 5825 |
| TR-TRIX-15 | 5 | 0.0141 | -0.440 | 5.74e-01 | no | 5811 |
| TR-TRIX-15 | 10 | 0.0272 | -0.289 | 4.26e-01 | no | 5806 |
| TR-VORTEX-14 | 5 | 0.0262 | -0.265 | 2.59e-01 | no | 5840 |
| TR-AROONOSC-14 | 5 | 0.0067 | -0.226 | 7.72e-01 | no | 5840 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-PSAR-CROSS | 1 | +0.00069 | 2925 |
| TR-PSAR-CROSS | 5 | +0.00054 | 2921 |
| TR-PSAR-CROSS | 10 | +0.00044 | 2916 |
| TR-EMACROSS-50-200 | 20 | +0.00034 | 2703 |

**Slot winner: TR-VORTEX-14** (h=1, IC=0.0570, IC_IR=-0.005). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-UO-7-14-28 | 1 | -0.2145 | -1.200 | 2.53e-56 | yes | 5831 |
| MO-WILLR-14 | 1 | -0.0937 | -1.199 | 5.90e-14 | yes | 5845 |
| MO-RSI-14 | 1 | -0.0222 | -1.066 | 8.52e-02 | no | 5845 |
| MO-KDJ-9 | 1 | -0.0834 | -1.030 | 1.71e-11 | yes | 5850 |
| MO-TSI-13-25 | 1 | 0.0004 | -0.993 | 9.78e-01 | no | 5821 |
| MO-STOCH-14 | 1 | -0.0440 | -0.888 | 4.80e-04 | yes | 5843 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 10 | +0.00278 | 232 |
| MO-STOCH-CROSS-14 | 10 | -0.00129 | 2888 |
| MO-STOCH-CROSS-14 | 5 | -0.00128 | 2893 |
| MO-STOCH-CROSS-14 | 20 | -0.00113 | 2883 |

**Slot winner: MO-UO-7-14-28** (h=1, IC=-0.2145, IC_IR=-1.200). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-BBP-20-2 | 1 | -0.0274 | -0.711 | 3.28e-02 | no | 5839 |
| VO-RVI-14 | 1 | -0.0310 | -0.629 | 1.57e-02 | yes | 5832 |
| VO-UI-14 | 1 | -0.0009 | 0.495 | 9.44e-01 | no | 5832 |
| VO-BBP-20-2 | 5 | -0.0157 | -0.327 | 4.86e-01 | no | 5835 |
| VO-RVI-14 | 5 | -0.0306 | -0.277 | 1.70e-01 | no | 5828 |
| VO-UI-14 | 5 | 0.0003 | 0.265 | 9.90e-01 | no | 5828 |

**Slot winner: VO-RVI-14** (h=1, IC=-0.0310, IC_IR=-0.629). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Volume slot
_Volume slot N/A — no real volume for this series._

## CHF=X — USD/CHF (fx)

### Trend slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| TR-TRIX-15 | 1 | 0.0008 | -0.724 | 9.55e-01 | no | 5881 |
| TR-TRIX-15 | 5 | -0.0121 | -0.424 | 6.34e-01 | no | 5877 |
| TR-MACDH-12-26-9 | 1 | -0.0030 | -0.383 | 8.20e-01 | no | 5891 |
| TR-TRIX-15 | 10 | -0.0315 | -0.299 | 3.56e-01 | no | 5872 |
| TR-VORTEX-14 | 5 | 0.0164 | -0.247 | 4.90e-01 | no | 5906 |
| TR-ADX-14 | 1 | 0.0138 | 0.239 | 2.78e-01 | no | 5911 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| TR-EMACROSS-50-200 | 20 | -0.00269 | 2341 |
| TR-EMACROSS-50-200 | 10 | -0.00121 | 2341 |
| TR-PSAR-CROSS | 1 | +0.00113 | 2816 |
| TR-PSAR-CROSS | 5 | +0.00104 | 2812 |

**Slot winner: TR-VORTEX-14** (h=1, IC=0.0666, IC_IR=0.122). library prior SUBSTITUTE (second-string) -> PARTIAL: not the tagged primary yet wins flat; revisit slot priority under regimes.

### Momentum slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| MO-UO-7-14-28 | 1 | -0.2259 | -1.163 | 9.31e-63 | yes | 5897 |
| MO-WILLR-14 | 1 | -0.0740 | -0.897 | 2.21e-09 | yes | 5911 |
| MO-TSI-13-25 | 1 | -0.0064 | -0.878 | 6.21e-01 | no | 5887 |
| MO-RSI-14 | 1 | -0.0151 | -0.784 | 2.42e-01 | no | 5911 |
| MO-KDJ-9 | 1 | -0.0654 | -0.722 | 1.36e-07 | yes | 5916 |
| MO-STOCH-14 | 1 | -0.0245 | -0.639 | 5.13e-02 | no | 5909 |

| discrete signal | h | expectancy spread | n(min state) |
|---|---:|---:|---:|
| MO-RSI-THRESH-14 | 20 | +0.01860 | 237 |
| MO-RSI-THRESH-14 | 10 | +0.01326 | 237 |
| MO-RSI-THRESH-14 | 5 | +0.00483 | 239 |
| MO-RSI-THRESH-14 | 1 | +0.00077 | 240 |

**Slot winner: MO-UO-7-14-28** (h=1, IC=-0.2259, IC_IR=-1.163). library prior MAINTAIN -> AGREES: expected to hold signal and it leads the slot on flat history.

### Volatility slot

| indicator | h | IC | IC_IR | p | survives_fdr | n |
|---|---:|---:|---:|---:|:--:|---:|
| VO-UI-14 | 1 | 0.0057 | 0.580 | 6.62e-01 | no | 5898 |
| VO-BBP-20-2 | 1 | -0.0153 | -0.520 | 2.29e-01 | no | 5905 |
| VO-RVI-14 | 1 | -0.0185 | -0.487 | 1.51e-01 | no | 5898 |
| VO-UI-14 | 5 | 0.0170 | 0.328 | 4.91e-01 | no | 5894 |
| VO-ATRRATIO-14 | 1 | 0.0115 | 0.291 | 3.75e-01 | no | 5911 |
| VO-BBP-20-2 | 5 | -0.0120 | -0.285 | 6.01e-01 | no | 5901 |

**NO SLOT WINNER — nothing in this category survives FDR.**

### Volume slot
_Volume slot N/A — no real volume for this series._

