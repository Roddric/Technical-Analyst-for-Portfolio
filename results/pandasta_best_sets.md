# pandas_ta best indicator sets (per asset)

> Flat-history selection, defaults-only, FDR q=0.10. OOS = selection on data <= 2023-12-31; FULL = in-sample upper bound (NOT a forecast). ICs are small in absolute terms; composite signals are screened, not regime-conditioned.

## Selection window: 2023-12-31

| asset | class | volume | trend | momentum | volatility | h | comp_IC | comp_IC_IR | redundancy | sign |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|
| BTC-USD | crypto | VU-cmf | TR-aroon | MO-trix | - | 20 | +0.1065 | -0.199 | 0.37 | +1 |
| CHF=X | fx | - | TR-aroon | MO-brar | VO-massi | 20 | +0.0942 | +0.194 | 0.22 | +1 |
| CL=F | energy | - | TR-vhf | - | VO-ACCB_WIDTH | 20 | +0.0799 | +0.098 | 0.05 | +1 |
| DX-Y.NYB | fx | - | TR-dpo | MO-trix | VO-BBP | 20 | +0.0832 | -0.292 | 0.28 | +1 |
| ETH-USD | crypto | VU-nvi | - | MO-slope | - | 20 | +0.0017 | -0.015 | 0.03 | +1 |
| EURUSD=X | fx | - | TR-vortex | MO-stoch | VO-BBP | 20 | +0.0225 | -0.207 | 0.53 | +1 |
| GC=F | metals | VU-nvi | - | MO-crsi | - | 20 | +0.0850 | +0.278 | 0.07 | +1 |
| HYG | credit | VU-adosc | TR-aroon | MO-qqe | VO-ATR_RATIO | 20 | +0.0866 | +0.357 | 0.36 | +1 |
| LQD | credit | VU-pvt | - | MO-bop | - | 20 | +0.0542 | +0.128 | 0.03 | +1 |
| SI=F | metals | VU-ad | - | MO-crsi | VO-DC_WIDTH | 20 | +0.0438 | +0.095 | 0.05 | +1 |
| TLT | rates | VU-adosc | - | MO-crsi | VO-BBP | 20 | +0.0194 | -0.204 | 0.49 | +1 |
| ^FTSE | equity | VU-pvt | TR-dpo | MO-rsi | VO-DC_WIDTH | 20 | +0.1445 | +0.335 | 0.36 | +1 |
| ^GDAXI | equity | - | TR-adx | MO-eri | - | 20 | +0.0668 | +0.137 | 0.04 | +1 |
| ^GSPC | equity | VU-efi | - | MO-stc | VO-BBP | 20 | +0.0484 | +0.144 | 0.41 | +1 |
| ^HSI | equity | VU-nvi | TR-vhf | MO-cmo | VO-BBP | 20 | +0.0256 | -0.167 | 0.14 | +1 |
| ^KS11 | equity | VU-pvi | TR-adx | MO-cfo | VO-ATR_RATIO | 20 | +0.0888 | +0.057 | 0.11 | +1 |
| ^N225 | equity | VU-adosc | TR-chop | MO-tsi | VO-BBP | 20 | +0.0323 | -0.173 | 0.20 | +1 |
| ^NDX | equity | VU-adosc | - | MO-willr | VO-BBP | 20 | +0.0201 | +0.241 | 0.64 | +1 |
| ^STOXX50E | equity | VU-mfi | TR-aroon | MO-cci | VO-ACCB_WIDTH | 20 | +0.0814 | +0.341 | 0.45 | +1 |
| ^TNX | rates | - | TR-dpo | MO-qqe | VO-BBP | 20 | +0.0604 | -0.234 | 0.45 | +1 |

## Selection window: FULL

| asset | class | volume | trend | momentum | volatility | h | comp_IC | comp_IC_IR | redundancy | sign |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|
| BTC-USD | crypto | VU-cmf | TR-aroon | MO-trix | - | 20 | +0.1036 | -0.199 | 0.36 | +1 |
| CHF=X | fx | - | TR-aroon | MO-brar | VO-massi | 20 | +0.0649 | +0.182 | 0.22 | +1 |
| CL=F | energy | - | TR-vhf | MO-slope | VO-ATR_RATIO | 20 | +0.0708 | +0.186 | 0.04 | +1 |
| DX-Y.NYB | fx | - | TR-dpo | MO-trix | VO-BBP | 20 | +0.0828 | -0.288 | 0.28 | +1 |
| ETH-USD | crypto | VU-efi | TR-dpo | MO-ao | - | 20 | +0.1404 | -0.202 | 0.82 | +1 |
| EURUSD=X | fx | - | TR-aroon | MO-pgo | VO-BBP | 20 | +0.0183 | -0.220 | 0.56 | +1 |
| GC=F | metals | - | - | MO-slope | - | 20 | +0.0204 | +0.249 | nan | +1 |
| HYG | credit | VU-pvt | TR-aroon | MO-tsi | VO-ATR_RATIO | 20 | +0.1050 | +0.420 | 0.46 | +1 |
| LQD | credit | VU-pvt | - | MO-bop | - | 20 | +0.0717 | +0.311 | 0.04 | +1 |
| SI=F | metals | VU-nvi | - | MO-slope | VO-ATR_RATIO | 20 | +0.0339 | +0.173 | 0.04 | +1 |
| TLT | rates | VU-pvt | TR-vhf | MO-eri | VO-BBP | 20 | +0.0517 | +0.293 | 0.18 | +1 |
| ^FTSE | equity | VU-pvt | TR-dpo | MO-rsi | VO-DC_WIDTH | 20 | +0.1468 | +0.338 | 0.34 | +1 |
| ^GDAXI | equity | VU-pvo | TR-adx | MO-eri | VO-DC_WIDTH | 20 | +0.0916 | +0.103 | 0.14 | +1 |
| ^GSPC | equity | VU-efi | TR-vortex | MO-stc | VO-BBP | 20 | +0.0447 | +0.165 | 0.47 | +1 |
| ^HSI | equity | VU-nvi | TR-vhf | MO-pgo | VO-BBP | 20 | +0.0220 | -0.145 | 0.16 | +1 |
| ^KS11 | equity | VU-pvi | TR-adx | MO-er | VO-ATR_RATIO | 20 | +0.1030 | +0.043 | 0.08 | +1 |
| ^N225 | equity | VU-adosc | TR-chop | MO-trix | - | 20 | +0.0393 | -0.066 | 0.08 | +1 |
| ^NDX | equity | VU-efi | - | MO-pgo | VO-BBP | 20 | +0.0138 | +0.260 | 0.79 | +1 |
| ^STOXX50E | equity | VU-pvt | TR-aroon | MO-tsi | VO-BBP | 20 | +0.1030 | +0.358 | 0.30 | +1 |
| ^TNX | rates | - | TR-dpo | MO-kst | VO-BBP | 20 | +0.0542 | -0.237 | 0.43 | +1 |
