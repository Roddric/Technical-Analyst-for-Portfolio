# pandas_ta best indicator sets (per asset)

> Flat-history selection, defaults-only, FDR q=0.10. OOS = selection on data <= 2023-12-31; FULL = in-sample upper bound (NOT a forecast). ICs are small in absolute terms; composite signals are screened, not regime-conditioned.

## Selection window: 2023-12-31

| asset | class | volume | trend | momentum | volatility | h | comp_IC | comp_IC_IR | redundancy | sign | fallback |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| ASHR | equity | VU-adosc | TR-dpo | MO-slope | VO-BBP | 20 | +0.0678 | +0.119 | 0.34 | +1 | trend |
| BTC-USD | crypto | VU-mfi | TR-adx | MO-kst | VO-rvi | 20 | +0.0992 | -0.140 | 0.34 | +1 | volatility |
| CL=F | energy | VU-pvt | TR-dpo | MO-tsi | VO-ATR_RATIO | 20 | +0.0582 | +0.231 | 0.49 | +1 | volume,trend,momentum,volatility |
| ETH-USD | crypto | VU-nvi | TR-dpo | MO-tsi | VO-rvi | 20 | +0.0616 | -0.195 | 0.32 | +1 | trend,momentum,volatility |
| GC=F | metals | VU-ad | TR-dpo | MO-crsi | VO-rvi | 20 | +0.0704 | +0.214 | 0.24 | +1 | trend,volatility |
| SI=F | metals | VU-ad | TR-dpo | MO-crsi | VO-DC_WIDTH | 20 | +0.0592 | +0.214 | 0.09 | +1 | trend |
| VEA | equity | VU-pvt | TR-aroon | MO-crsi | VO-ATR_RATIO | 20 | +0.0395 | +0.403 | 0.23 | +1 | volume |
| VWO | equity | VU-efi | TR-dpo | MO-uo | VO-natr | 20 | +0.0594 | +0.247 | 0.51 | +1 | trend |
| ^FTSE | equity | VU-pvt | TR-dpo | MO-eri | VO-DC_WIDTH | 20 | +0.1268 | +0.336 | 0.32 | +1 | - |
| ^GSPC | equity | VU-efi | TR-dpo | MO-slope | VO-BBP | 20 | +0.0318 | +0.230 | 0.54 | +1 | trend |
| ^KS11 | equity | VU-pvi | TR-adx | MO-cfo | VO-DC_WIDTH | 20 | +0.0991 | +0.023 | 0.14 | +1 | - |
| ^N225 | equity | VU-adosc | TR-chop | MO-trix | VO-ui | 20 | +0.0210 | -0.138 | 0.15 | +1 | volatility |
| ^NDX | equity | VU-adosc | TR-dpo | MO-uo | VO-BBP | 20 | +0.0161 | +0.257 | 0.62 | +1 | trend |
| ^TWII | equity | VU-pvt | TR-dpo | MO-eri | VO-BBP | 20 | +0.0168 | -0.195 | 0.45 | +1 | volume,trend |

## Selection window: FULL

| asset | class | volume | trend | momentum | volatility | h | comp_IC | comp_IC_IR | redundancy | sign | fallback |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| ASHR | equity | VU-pvi | TR-dpo | MO-crsi | VO-BBP | 20 | +0.0421 | +0.070 | 0.49 | +1 | trend |
| BTC-USD | crypto | VU-cmf | TR-aroon | MO-trix | VO-rvi | 20 | +0.0990 | -0.204 | 0.37 | +1 | volatility |
| CL=F | energy | VU-pvt | TR-vhf | MO-tsi | VO-ACCB_WIDTH | 20 | +0.0438 | +0.241 | 0.19 | +1 | volume,momentum |
| ETH-USD | crypto | VU-efi | TR-dpo | MO-tsi | VO-rvi | 20 | +0.1043 | -0.224 | 0.65 | +1 | trend,momentum,volatility |
| GC=F | metals | VU-pvt | TR-dpo | MO-crsi | VO-rvi | 20 | +0.0716 | +0.210 | 0.25 | +1 | volume,trend,volatility |
| SI=F | metals | VU-nvi | TR-dpo | MO-slope | VO-ATR_RATIO | 20 | +0.0409 | +0.244 | 0.11 | +1 | trend |
| VEA | equity | VU-pvt | TR-aroon | MO-willr | VO-ATR_RATIO | 20 | +0.0626 | +0.373 | 0.35 | +1 | - |
| VWO | equity | VU-efi | TR-dpo | MO-uo | VO-ATR_RATIO | 20 | +0.0495 | +0.325 | 0.51 | +1 | trend |
| ^FTSE | equity | VU-pvt | TR-dpo | MO-rsi | VO-DC_WIDTH | 20 | +0.1468 | +0.338 | 0.34 | +1 | - |
| ^GSPC | equity | VU-efi | TR-vortex | MO-stc | VO-BBP | 20 | +0.0447 | +0.165 | 0.47 | +1 | - |
| ^KS11 | equity | VU-pvt | TR-adx | MO-er | VO-ATR_RATIO | 20 | +0.0440 | +0.113 | 0.13 | +1 | volume |
| ^N225 | equity | VU-adosc | TR-chop | MO-trix | VO-ui | 20 | +0.0223 | -0.136 | 0.16 | +1 | volatility |
| ^NDX | equity | VU-adosc | TR-dpo | MO-stochf | VO-BBP | 20 | +0.0150 | +0.270 | 0.62 | +1 | trend |
| ^TWII | equity | VU-pvt | TR-dpo | MO-slope | VO-BBP | 20 | +0.0441 | -0.317 | 0.34 | +1 | volume,trend |
