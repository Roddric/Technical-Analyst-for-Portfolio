# Indicator Library — slot-based technical indicator roster (DRAFT for review)

**Status:** reconstructed draft (the authoritative `indicator_library.md` was not
present in the workspace). Review the rosters and the `shock_behavior` /
`known_failure` priors below, then approve before the grouped backtest runs.

## Architecture
The pipeline fills **four category slots** — Trend, Momentum, Volatility, Volume —
with **exactly one indicator each**. Indicators therefore compete *within* their
slot, never across slots. IDs are prefixed by slot:

| prefix | slot |
|---|---|
| `TR-` | Trend |
| `MO-` | Momentum |
| `VO-` | Volatility |
| `VL-` | Volume |

## Priors carried per indicator
- **shock_behavior** — the library's hand-designed expectation of how the
  indicator behaves in a volatility shock:
  - `MAINTAIN`  — expected to stay informative through the shock.
  - `SUPPRESS`  — expected to lose signal (saturates / lags / whipsaws) in shock.
  - `SUBSTITUTE`— second-string; expected to be swapped in when the primary fails.
- **known_failure** — the documented failure mode.

The grouped backtest reports, per empirical slot winner, whether the flat-history
result **AGREES** or **DISAGREES** with these priors. Disagreement is not "wrong";
for a `SUPPRESS`-tagged indicator that still tops its slot on flat history it is a
flag for possible **regime-masking** — to be resolved by the regime-conditioned run.

## Multi-output / transform handling (documented per indicator)
- `level` — test the named `tested_column` directly.
- `ratio_close` — test `tested_column / close` (scale-free, e.g. ATR).
- `coldiff:A,B` — test `df[A] - df[B]` (e.g. Vortex VTXP − VTXM).
- `width:L,M,U` — test `(df[U] - df[L]) / df[M]` (channel width, e.g. KC/Donchian).
- `slope:N` — test `series.diff(N)` for cumulative lines (OBV, A/D, PVT) — never
  the raw cumulative level.
- `disc_threshold:col,lo,hi` — discrete: +1 if `col<lo`, −1 if `col>hi`, else 0.
- `disc_cross:A,B` — discrete: +1 if `df[A]>df[B]`, else −1.
- `disc_ema_cross:f,s` — discrete: +1 if `EMA(close,f)>EMA(close,s)`, else −1.
- `disc_psar` — discrete: +1 while PSAR long-stop active, −1 while short-stop active.
- `disc_supertrend:col` — discrete: the Supertrend direction column (+1 / −1).

Multi-output picks: **KDJ → J line**, **MACD → histogram (continuous) & line-vs-signal
(discrete)**, **Fisher → FISHERT**, **BBANDS → %B and bandwidth**, **Stoch → %K
(continuous) & %K-vs-%D (discrete)**.

---

## TREND (`TR-`)

| id | type | library_call | tested | transform | shock | known_failure |
|---|---|---|---|---|---|---|
| TR-ADX-14 | continuous | ta.adx(high, low, close, length=14) | ADX_14 | level | MAINTAIN | reads trend *strength* not direction; whipsaws when ADX low |
| TR-AROONOSC-14 | continuous | ta.aroon(high, low, length=14) | AROONOSC_14 | level | SUBSTITUTE | lags at sharp turns; noisy in chop |
| TR-VORTEX-14 | continuous | ta.vortex(high, low, close, length=14) | VTXP−VTXM | coldiff:VTXP_14,VTXM_14 | SUBSTITUTE | frequent false flips near equilibrium |
| TR-TRIX-15 | continuous | ta.trix(close, length=15) | TRIX_15_9 | level | SUPPRESS | triple-smoothed → severe lag in fast reversals |
| TR-QSTICK-10 | continuous | ta.qstick(open, close, length=10) | QS_10 | level | SUBSTITUTE | body-only; ignores wicks / gaps |
| TR-MACDH-12-26-9 | continuous | ta.macd(close, fast=12, slow=26, signal=9) | MACDh_12_26_9 | level | SUPPRESS | MA-lag driven; late in shocks |
| TR-PSAR-CROSS | discrete | ta.psar(high, low, close) | PSAR | disc_psar | SUBSTITUTE | shredded in sideways ranges |
| TR-SUPERT-10-3 | discrete | ta.supertrend(high, low, close, length=10, multiplier=3.0) | SUPERTd_10_3.0 | disc_supertrend:SUPERTd_10_3.0 | MAINTAIN | ATR-based stop lags in gap shocks |
| TR-EMACROSS-50-200 | discrete | (EMA50 vs EMA200) | close | disc_ema_cross:50,200 | SUPPRESS | classic golden/death lag; very slow |
| TR-MACD-CROSS-12-26-9 | discrete | ta.macd(close, fast=12, slow=26, signal=9) | MACD/MACDs | disc_cross:MACD_12_26_9,MACDs_12_26_9 | SUPPRESS | lagging cross; whipsaw in chop |

## MOMENTUM (`MO-`)

| id | type | library_call | tested | transform | shock | known_failure |
|---|---|---|---|---|---|---|
| MO-RSI-14 | continuous | ta.rsi(close, length=14) | RSI_14 | level | SUPPRESS | pins overbought/oversold in strong trends |
| MO-STOCH-14 | continuous | ta.stoch(high, low, close, k=14, d=3) | STOCHk_14_3_3 | level | SUPPRESS | saturates at 0/100 in trends |
| MO-KDJ-9 | continuous | ta.kdj(high, low, close, length=9) | J_9_3 | level | SUBSTITUTE | J overshoots; very noisy |
| MO-ROC-10 | continuous | ta.roc(close, length=10) | ROC_10 | level | MAINTAIN | scale drifts across decades (rank-IC mitigates) |
| MO-MOM-10 | continuous | ta.mom(close, length=10) | MOM_10 | level | MAINTAIN | absolute units; regime-scale sensitive |
| MO-CMO-14 | continuous | ta.cmo(close, length=14) | CMO_14 | level | SUPPRESS | monotone-related to RSI; saturates |
| MO-WILLR-14 | continuous | ta.willr(high, low, close, length=14) | WILLR_14 | level | SUPPRESS | bounded; saturates in trends |
| MO-FISHER-9 | continuous | ta.fisher(high, low, length=9) | FISHERT_9_1 | level | SUBSTITUTE | extreme spikes at range edges |
| MO-TSI-13-25 | continuous | ta.tsi(close) | TSI_13_25_13 | level | SUPPRESS | double-smoothed → laggy |
| MO-UO-7-14-28 | continuous | ta.uo(high, low, close) | UO_7_14_28 | level | MAINTAIN | multi-timeframe blend blurs fast turns |
| MO-AO-5-34 | continuous | ta.ao(high, low) | AO_5_34 | level | SUBSTITUTE | midpoint-based; ignores close |
| MO-CCI-20 | continuous | ta.cci(high, low, close, length=20) | CCI_20_0.015 | level | SUBSTITUTE | unbounded spikes; noisy |
| MO-RSI-THRESH-14 | discrete | ta.rsi(close, length=14) | RSI_14 | disc_threshold:RSI_14,30,70 | SUPPRESS | thresholds rarely hit in low-vol drift |
| MO-STOCH-CROSS-14 | discrete | ta.stoch(high, low, close, k=14, d=3) | STOCHk/STOCHd | disc_cross:STOCHk_14_3_3,STOCHd_14_3_3 | SUPPRESS | frequent whipsaw crosses |

## VOLATILITY (`VO-`)

| id | type | library_call | tested | transform | shock | known_failure |
|---|---|---|---|---|---|---|
| VO-NATR-14 | continuous | ta.natr(high, low, close, length=14) | NATR_14 | level | MAINTAIN | pure magnitude; no direction |
| VO-ATRRATIO-14 | continuous | ta.atr(high, low, close, length=14) | ATRr_14 | ratio_close | MAINTAIN | magnitude only; monotone to NATR |
| VO-BBP-20-2 | continuous | ta.bbands(close, length=20, std=2) | BBP_20_2.0 | level | SUBSTITUTE | %B is position not width; mean-reversion flavored |
| VO-BBB-20-2 | continuous | ta.bbands(close, length=20, std=2) | BBB_20_2.0 | level | MAINTAIN | bandwidth lags realized vol |
| VO-KCW-20 | continuous | ta.kc(high, low, close, length=20) | KC width | width:KCLe_20_2,KCBe_20_2,KCUe_20_2 | MAINTAIN | EMA-centered; laggy width |
| VO-DCW-20 | continuous | ta.donchian(high, low) | Donchian width | width:DCL_20_20,DCM_20_20,DCU_20_20 | MAINTAIN | driven by extremes; sticky after spikes |
| VO-RVI-14 | continuous | ta.rvi(close, high, low, length=14) | RVI_14 | level | SUBSTITUTE | conflates vol with direction |
| VO-UI-14 | continuous | ta.ui(close, length=14) | UI_14 | level | MAINTAIN | drawdown-based; one-sided (downside only) |

## VOLUME (`VL-`)  — N/A for FX (no real volume)

| id | type | library_call | tested | transform | shock | known_failure |
|---|---|---|---|---|---|---|
| VL-OBV-SLOPE-5 | continuous | ta.obv(close, volume) | OBV | slope:5 | MAINTAIN | cumulative; slope needed; step artifacts |
| VL-AD-SLOPE-5 | continuous | ta.ad(high, low, close, volume) | AD | slope:5 | MAINTAIN | mis-weights gaps (no gap term) |
| VL-ADOSC-3-10 | continuous | ta.adosc(high, low, close, volume, fast=3, slow=10) | ADOSC_3_10 | level | MAINTAIN | sensitive to volume spikes |
| VL-MFI-14 | continuous | ta.mfi(high, low, close, volume, length=14) | MFI_14 | level | SUBSTITUTE | bounded; saturates like RSI |
| VL-CMF-20 | continuous | ta.cmf(high, low, close, volume, length=20) | CMF_20 | level | SUBSTITUTE | intrabar-location bias; no gap term |
| VL-EOM-14 | continuous | ta.eom(high, low, close, volume, length=14) | EOM_14_100000000 | level | SUBSTITUTE | unstable when range→0 |
| VL-PVT-SLOPE-5 | continuous | ta.pvt(close, volume) | PVT | slope:5 | MAINTAIN | cumulative; slope needed |

---

## Machine-readable roster (parser consumes this block)

```json
[
{"id":"TR-ADX-14","category":"Trend","indicator_type":"continuous","library_call":"ta.adx(high, low, close, length=14)","output_type":"dataframe","tested_column":"ADX_14","transform":"level","data_inputs":["high","low","close"],"params":{"length":14},"min_bars":40,"shock_behavior":"MAINTAIN","known_failure":"reads trend strength not direction; whipsaws when ADX low"},
{"id":"TR-AROONOSC-14","category":"Trend","indicator_type":"continuous","library_call":"ta.aroon(high, low, length=14)","output_type":"dataframe","tested_column":"AROONOSC_14","transform":"level","data_inputs":["high","low"],"params":{"length":14},"min_bars":30,"shock_behavior":"SUBSTITUTE","known_failure":"lags at sharp turns; noisy in chop"},
{"id":"TR-VORTEX-14","category":"Trend","indicator_type":"continuous","library_call":"ta.vortex(high, low, close, length=14)","output_type":"dataframe","tested_column":"VTXP_14","transform":"coldiff:VTXP_14,VTXM_14","data_inputs":["high","low","close"],"params":{"length":14},"min_bars":30,"shock_behavior":"SUBSTITUTE","known_failure":"frequent false flips near equilibrium"},
{"id":"TR-TRIX-15","category":"Trend","indicator_type":"continuous","library_call":"ta.trix(close, length=15)","output_type":"dataframe","tested_column":"TRIX_15_9","transform":"level","data_inputs":["close"],"params":{"length":15},"min_bars":60,"shock_behavior":"SUPPRESS","known_failure":"triple-smoothed severe lag in fast reversals"},
{"id":"TR-QSTICK-10","category":"Trend","indicator_type":"continuous","library_call":"ta.qstick(open, close, length=10)","output_type":"series","tested_column":"QS_10","transform":"level","data_inputs":["open","close"],"params":{"length":10},"min_bars":20,"shock_behavior":"SUBSTITUTE","known_failure":"body-only; ignores wicks and gaps"},
{"id":"TR-MACDH-12-26-9","category":"Trend","indicator_type":"continuous","library_call":"ta.macd(close, fast=12, slow=26, signal=9)","output_type":"dataframe","tested_column":"MACDh_12_26_9","transform":"level","data_inputs":["close"],"params":{"fast":12,"slow":26,"signal":9},"min_bars":45,"shock_behavior":"SUPPRESS","known_failure":"MA-lag driven; late in shocks"},
{"id":"TR-PSAR-CROSS","category":"Trend","indicator_type":"discrete","library_call":"ta.psar(high, low, close)","output_type":"dataframe","tested_column":"PSARl_0.02_0.2","transform":"disc_psar","data_inputs":["high","low","close"],"params":{"af0":0.02,"af":0.02,"max_af":0.2},"min_bars":10,"shock_behavior":"SUBSTITUTE","known_failure":"shredded in sideways ranges"},
{"id":"TR-SUPERT-10-3","category":"Trend","indicator_type":"discrete","library_call":"ta.supertrend(high, low, close, length=10, multiplier=3.0)","output_type":"dataframe","tested_column":"SUPERTd_10_3.0","transform":"disc_supertrend:SUPERTd_10_3.0","data_inputs":["high","low","close"],"params":{"length":10,"multiplier":3.0},"min_bars":20,"shock_behavior":"MAINTAIN","known_failure":"ATR-based stop lags in gap shocks"},
{"id":"TR-EMACROSS-50-200","category":"Trend","indicator_type":"discrete","library_call":null,"output_type":"derived","tested_column":"close","transform":"disc_ema_cross:50,200","data_inputs":["close"],"params":{"fast":50,"slow":200},"min_bars":200,"shock_behavior":"SUPPRESS","known_failure":"classic golden/death lag; very slow"},
{"id":"TR-MACD-CROSS-12-26-9","category":"Trend","indicator_type":"discrete","library_call":"ta.macd(close, fast=12, slow=26, signal=9)","output_type":"dataframe","tested_column":"MACD_12_26_9","transform":"disc_cross:MACD_12_26_9,MACDs_12_26_9","data_inputs":["close"],"params":{"fast":12,"slow":26,"signal":9},"min_bars":45,"shock_behavior":"SUPPRESS","known_failure":"lagging cross; whipsaw in chop"},

{"id":"MO-RSI-14","category":"Momentum","indicator_type":"continuous","library_call":"ta.rsi(close, length=14)","output_type":"series","tested_column":"RSI_14","transform":"level","data_inputs":["close"],"params":{"length":14},"min_bars":20,"shock_behavior":"SUPPRESS","known_failure":"pins overbought/oversold in strong trends"},
{"id":"MO-STOCH-14","category":"Momentum","indicator_type":"continuous","library_call":"ta.stoch(high, low, close, k=14, d=3)","output_type":"dataframe","tested_column":"STOCHk_14_3_3","transform":"level","data_inputs":["high","low","close"],"params":{"k":14,"d":3},"min_bars":25,"shock_behavior":"SUPPRESS","known_failure":"saturates at 0/100 in trends"},
{"id":"MO-KDJ-9","category":"Momentum","indicator_type":"continuous","library_call":"ta.kdj(high, low, close, length=9)","output_type":"dataframe","tested_column":"J_9_3","transform":"level","data_inputs":["high","low","close"],"params":{"length":9},"min_bars":20,"shock_behavior":"SUBSTITUTE","known_failure":"J overshoots; very noisy"},
{"id":"MO-ROC-10","category":"Momentum","indicator_type":"continuous","library_call":"ta.roc(close, length=10)","output_type":"series","tested_column":"ROC_10","transform":"level","data_inputs":["close"],"params":{"length":10},"min_bars":12,"shock_behavior":"MAINTAIN","known_failure":"scale drifts across decades (rank-IC mitigates)"},
{"id":"MO-MOM-10","category":"Momentum","indicator_type":"continuous","library_call":"ta.mom(close, length=10)","output_type":"series","tested_column":"MOM_10","transform":"level","data_inputs":["close"],"params":{"length":10},"min_bars":12,"shock_behavior":"MAINTAIN","known_failure":"absolute units; regime-scale sensitive"},
{"id":"MO-CMO-14","category":"Momentum","indicator_type":"continuous","library_call":"ta.cmo(close, length=14)","output_type":"series","tested_column":"CMO_14","transform":"level","data_inputs":["close"],"params":{"length":14},"min_bars":20,"shock_behavior":"SUPPRESS","known_failure":"monotone-related to RSI; saturates"},
{"id":"MO-WILLR-14","category":"Momentum","indicator_type":"continuous","library_call":"ta.willr(high, low, close, length=14)","output_type":"series","tested_column":"WILLR_14","transform":"level","data_inputs":["high","low","close"],"params":{"length":14},"min_bars":20,"shock_behavior":"SUPPRESS","known_failure":"bounded; saturates in trends"},
{"id":"MO-FISHER-9","category":"Momentum","indicator_type":"continuous","library_call":"ta.fisher(high, low, length=9)","output_type":"dataframe","tested_column":"FISHERT_9_1","transform":"level","data_inputs":["high","low"],"params":{"length":9},"min_bars":20,"shock_behavior":"SUBSTITUTE","known_failure":"extreme spikes at range edges"},
{"id":"MO-TSI-13-25","category":"Momentum","indicator_type":"continuous","library_call":"ta.tsi(close)","output_type":"dataframe","tested_column":"TSI_13_25_13","transform":"level","data_inputs":["close"],"params":{"fast":13,"slow":25,"signal":13},"min_bars":50,"shock_behavior":"SUPPRESS","known_failure":"double-smoothed laggy"},
{"id":"MO-UO-7-14-28","category":"Momentum","indicator_type":"continuous","library_call":"ta.uo(high, low, close)","output_type":"series","tested_column":"UO_7_14_28","transform":"level","data_inputs":["high","low","close"],"params":{"fast":7,"medium":14,"slow":28},"min_bars":35,"shock_behavior":"MAINTAIN","known_failure":"multi-timeframe blend blurs fast turns"},
{"id":"MO-AO-5-34","category":"Momentum","indicator_type":"continuous","library_call":"ta.ao(high, low)","output_type":"series","tested_column":"AO_5_34","transform":"level","data_inputs":["high","low"],"params":{"fast":5,"slow":34},"min_bars":40,"shock_behavior":"SUBSTITUTE","known_failure":"midpoint-based; ignores close"},
{"id":"MO-CCI-20","category":"Momentum","indicator_type":"continuous","library_call":"ta.cci(high, low, close, length=20)","output_type":"series","tested_column":"CCI_20_0.015","transform":"level","data_inputs":["high","low","close"],"params":{"length":20},"min_bars":25,"shock_behavior":"SUBSTITUTE","known_failure":"unbounded spikes; noisy"},
{"id":"MO-RSI-THRESH-14","category":"Momentum","indicator_type":"discrete","library_call":"ta.rsi(close, length=14)","output_type":"series","tested_column":"RSI_14","transform":"disc_threshold:RSI_14,30,70","data_inputs":["close"],"params":{"length":14,"lo":30,"hi":70},"min_bars":20,"shock_behavior":"SUPPRESS","known_failure":"thresholds rarely hit in low-vol drift"},
{"id":"MO-STOCH-CROSS-14","category":"Momentum","indicator_type":"discrete","library_call":"ta.stoch(high, low, close, k=14, d=3)","output_type":"dataframe","tested_column":"STOCHk_14_3_3","transform":"disc_cross:STOCHk_14_3_3,STOCHd_14_3_3","data_inputs":["high","low","close"],"params":{"k":14,"d":3},"min_bars":25,"shock_behavior":"SUPPRESS","known_failure":"frequent whipsaw crosses"},

{"id":"VO-NATR-14","category":"Volatility","indicator_type":"continuous","library_call":"ta.natr(high, low, close, length=14)","output_type":"series","tested_column":"NATR_14","transform":"level","data_inputs":["high","low","close"],"params":{"length":14},"min_bars":20,"shock_behavior":"MAINTAIN","known_failure":"pure magnitude; no direction"},
{"id":"VO-ATRRATIO-14","category":"Volatility","indicator_type":"continuous","library_call":"ta.atr(high, low, close, length=14)","output_type":"series","tested_column":"ATRr_14","transform":"ratio_close","data_inputs":["high","low","close"],"params":{"length":14},"min_bars":20,"shock_behavior":"MAINTAIN","known_failure":"magnitude only; monotone to NATR"},
{"id":"VO-BBP-20-2","category":"Volatility","indicator_type":"continuous","library_call":"ta.bbands(close, length=20, std=2)","output_type":"dataframe","tested_column":"BBP_20_2.0","transform":"level","data_inputs":["close"],"params":{"length":20,"std":2},"min_bars":25,"shock_behavior":"SUBSTITUTE","known_failure":"%B is position not width; mean-reversion flavored"},
{"id":"VO-BBB-20-2","category":"Volatility","indicator_type":"continuous","library_call":"ta.bbands(close, length=20, std=2)","output_type":"dataframe","tested_column":"BBB_20_2.0","transform":"level","data_inputs":["close"],"params":{"length":20,"std":2},"min_bars":25,"shock_behavior":"MAINTAIN","known_failure":"bandwidth lags realized vol"},
{"id":"VO-KCW-20","category":"Volatility","indicator_type":"continuous","library_call":"ta.kc(high, low, close, length=20)","output_type":"dataframe","tested_column":"KCBe_20_2","transform":"width:KCLe_20_2,KCBe_20_2,KCUe_20_2","data_inputs":["high","low","close"],"params":{"length":20},"min_bars":25,"shock_behavior":"MAINTAIN","known_failure":"EMA-centered; laggy width"},
{"id":"VO-DCW-20","category":"Volatility","indicator_type":"continuous","library_call":"ta.donchian(high, low)","output_type":"dataframe","tested_column":"DCM_20_20","transform":"width:DCL_20_20,DCM_20_20,DCU_20_20","data_inputs":["high","low"],"params":{"lower_length":20,"upper_length":20},"min_bars":25,"shock_behavior":"MAINTAIN","known_failure":"driven by extremes; sticky after spikes"},
{"id":"VO-RVI-14","category":"Volatility","indicator_type":"continuous","library_call":"ta.rvi(close, high, low, length=14)","output_type":"series","tested_column":"RVI_14","transform":"level","data_inputs":["close","high","low"],"params":{"length":14},"min_bars":25,"shock_behavior":"SUBSTITUTE","known_failure":"conflates vol with direction"},
{"id":"VO-UI-14","category":"Volatility","indicator_type":"continuous","library_call":"ta.ui(close, length=14)","output_type":"series","tested_column":"UI_14","transform":"level","data_inputs":["close"],"params":{"length":14},"min_bars":20,"shock_behavior":"MAINTAIN","known_failure":"drawdown-based; one-sided (downside only)"},

{"id":"VL-OBV-SLOPE-5","category":"Volume","indicator_type":"continuous","library_call":"ta.obv(close, volume)","output_type":"series","tested_column":"OBV","transform":"slope:5","data_inputs":["close","volume"],"params":{"slope":5},"min_bars":10,"shock_behavior":"MAINTAIN","known_failure":"cumulative; slope needed; step artifacts"},
{"id":"VL-AD-SLOPE-5","category":"Volume","indicator_type":"continuous","library_call":"ta.ad(high, low, close, volume)","output_type":"series","tested_column":"AD","transform":"slope:5","data_inputs":["high","low","close","volume"],"params":{"slope":5},"min_bars":10,"shock_behavior":"MAINTAIN","known_failure":"mis-weights gaps (no gap term)"},
{"id":"VL-ADOSC-3-10","category":"Volume","indicator_type":"continuous","library_call":"ta.adosc(high, low, close, volume, fast=3, slow=10)","output_type":"series","tested_column":"ADOSC_3_10","transform":"level","data_inputs":["high","low","close","volume"],"params":{"fast":3,"slow":10},"min_bars":15,"shock_behavior":"MAINTAIN","known_failure":"sensitive to volume spikes"},
{"id":"VL-MFI-14","category":"Volume","indicator_type":"continuous","library_call":"ta.mfi(high, low, close, volume, length=14)","output_type":"series","tested_column":"MFI_14","transform":"level","data_inputs":["high","low","close","volume"],"params":{"length":14},"min_bars":20,"shock_behavior":"SUBSTITUTE","known_failure":"bounded; saturates like RSI"},
{"id":"VL-CMF-20","category":"Volume","indicator_type":"continuous","library_call":"ta.cmf(high, low, close, volume, length=20)","output_type":"series","tested_column":"CMF_20","transform":"level","data_inputs":["high","low","close","volume"],"params":{"length":20},"min_bars":25,"shock_behavior":"SUBSTITUTE","known_failure":"intrabar-location bias; no gap term"},
{"id":"VL-EOM-14","category":"Volume","indicator_type":"continuous","library_call":"ta.eom(high, low, close, volume, length=14)","output_type":"series","tested_column":"EOM_14_100000000","transform":"level","data_inputs":["high","low","close","volume"],"params":{"length":14},"min_bars":20,"shock_behavior":"SUBSTITUTE","known_failure":"unstable when range approaches zero"},
{"id":"VL-PVT-SLOPE-5","category":"Volume","indicator_type":"continuous","library_call":"ta.pvt(close, volume)","output_type":"series","tested_column":"PVT","transform":"slope:5","data_inputs":["close","volume"],"params":{"slope":5},"min_bars":10,"shock_behavior":"MAINTAIN","known_failure":"cumulative; slope needed"}
]
```
