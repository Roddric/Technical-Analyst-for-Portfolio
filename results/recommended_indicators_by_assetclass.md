# Recommended Indicators per Slot, by Asset Class

**What this is:** a single best-pick per category slot (Trend / Momentum / Volatility /
Volume) for each asset class, combining (a) the empirical flat IC screen
(`grouped_ic_results.csv`) and (b) domain intuition where the data is silent or thin.
The goal is to pick the *best available option per slot* even when the edge is weak.

**Honesty header — read once:**
- Empirical ICs here are small (mostly |IC| 0.03–0.06). Surviving the screen means
  *not obviously useless*, not *validated* or *tradeable after costs*.
- The **only strong, robust empirical edge** is **FX short-horizon mean-reversion**
  (|IC| ≈ 0.20–0.27). Everything else is "best-in-a-weak-field."
- **Sign matters.** NEG = contrarian (fade the reading); POS = directional (follow it).
- Rows marked *(intuition)* are domain reasoning, **not** backtested here — used only
  where the flat screen found no FDR survivor (notably Metals/Energy Trend & Momentum).
- Regime-conditioned results were **artifact-dominated** (overlap/small-sample), so
  they are used only as soft hypotheses, never as the basis for a pick.

---

## What each slot is (and why the architecture has four)

The pipeline fills four slots with exactly one indicator each. They answer different,
non-overlapping questions. You do **not** ask "does RSI beat ATR" — they live in
different slots and do different jobs.

### 1. Trend  — *"Which way, and is there a trend at all?"*
Measures **direction and trend strength**. A trend indicator's job is to tell you
whether price is in a persistent directional move (follow it) or ranging (ignore it /
fade it). Trend indicators are **laggy by construction** — they trade timeliness for
robustness. In this study trend signals were the weakest slot on flat history, because
"trend" only pays in specific regimes and averages to ~0 across all history.

### 2. Momentum  — *"How stretched is the current move?"*
Measures the **rate of change / overbought-oversold state**. Bounded oscillators (RSI,
Stoch, UO) are really **mean-reversion** tools at short horizons — a high reading means
"stretched, likely to snap back," not "strong, keep going." Raw momentum (MOM, ROC) is
the opposite: it measures persistence. That is why momentum-slot signs flip between
contrarian (oscillators) and directional (raw momentum) depending on asset and horizon.

### 3. Volatility  — *"How big are the moves right now?"*
Measures **magnitude, not direction**. This is the one slot that "works" almost
everywhere — but only because **volatility is autocorrelated** (vol clusters: calm
follows calm, storms follow storms). It does **not** predict return *direction*. Its
real job is **position sizing, stop placement, and regime gating** — turn other signals
off when vol is extreme, size down when NATR spikes.

### 4. Volume  — *"Is the move backed by participation?"*
Measures **conviction / money flow**. Volume indicators confirm or diverge from price:
price up on rising ADOSC/CMF = real buying; price up on falling volume = suspect.
**Not available for spot FX** (no centralized volume). Weakest and noisiest slot overall;
best used as a *confirmation filter*, not a standalone signal.

---

## Master table — best pick per slot per asset class

Legend: **sign** NEG=contrarian / POS=directional · **h** = horizon (trading days)
where the edge is clearest · *(intuition)* = domain pick, not from the screen.

| Asset class | Trend | Momentum | Volatility | Volume |
|---|---|---|---|---|
| **Equity indices** | VORTEX-14 · NEG · h1 | TSI-13-25 · NEG · h1 | **Ulcer Index-14** · POS · h1 | ADOSC-3-10 · NEG · h1 |
| **FX (majors)** | VORTEX-14 · POS · h1 | **Ultimate Osc 7-14-28** · NEG · h1 ⭐ | RVI-14 · NEG · h1 | — (no volume) |
| **Rates (yields/USTs)** | Aroon Osc-14 · POS · h10 | MOM-10 · NEG · h1 | RVI-14 / ATR-ratio · h1 | ADOSC-3-10 · NEG · h1 |
| **Credit (IG/HY)** | VORTEX-14 · NEG · h20 | TSI-13-25 · NEG · h10 | Ulcer Index-14 · POS · h1 | CMF-20 · NEG · h5 |
| **Metals (gold/silver)** | *ADX-14 gate + EMA50/200 (intuition)* | *ROC-10 / MOM-10 (intuition)* | **ATR-ratio-14** · POS · h1 | CMF-20 · NEG · h1 |
| **Energy (WTI)** | *Donchian-20 breakout (intuition)* | *MOM-10 directional (intuition)* | **ATR-ratio-14** · POS · h10 | *ADOSC (intuition)* |

Discrete cross/threshold signals that survived (best per class, for regime/state gating):

| Asset class | Trend (discrete) | Momentum (discrete) |
|---|---|---|
| Equity | EMA 50/200 cross (golden/death), spread +0.017 @h20 | RSI 30/70 threshold, +0.021 @h20 |
| Rates | Supertrend 10-3, +0.030 @h20 | RSI threshold, **−0.067 @h20** (contrarian) |
| Credit | PSAR cross | RSI threshold, +0.018 @h20 |
| Metals | PSAR cross | RSI threshold, +0.015 @h20 |
| Energy | Supertrend 10-3 | RSI threshold, −0.044 @h20 |
| FX | EMA 50/200 cross | RSI threshold, +0.019 @h20 |

---

## Per-asset-class detail: signals, technical strategies, subjective strategies

For each class: **Empirical read** (what the data says) → **Technical strategy**
(mechanical rules) → **Subjective strategy** (discretionary/domain overlay).

### Equity indices (^GSPC, ^NDX, ^STOXX50E, ^FTSE, ^GDAXI, ^N225, ^KS11, ^HSI)

**Empirical read.** Everything wins at **h=1 and is contrarian** (Vortex, TSI, ADOSC all
NEG) except volatility (Ulcer Index, POS). Translation: at the 1-day horizon, equity
indices **mean-revert** — stretched moves snap back. Volatility is the sturdiest slot
(vol clustering). Magnitudes are small (|IC|~0.03–0.045).

- **Trend — Vortex-14.** Signal: VTXP crosses above VTXM = uptrend, below = downtrend.
  Here it reads *contrarian at h1* (extended trend readings precede a snap-back).
- **Momentum — TSI-13-25.** Double-smoothed momentum; zero-line and signal-line cross.
  Contrarian at h1.
- **Volatility — Ulcer Index-14.** Downside-only volatility (depth × duration of
  drawdown). Rising UI = accumulating stress. POS IC = high stress precedes higher
  short-horizon forward returns (the "buy-the-dip / vol-mean-reversion" effect).
- **Volume — ADOSC-3-10 (Chaikin oscillator).** Volume-momentum; contrarian at h1.

**Technical strategy (mechanical).**
- *Mean-reversion core:* on a 1–5 day horizon, **fade** RSI<30 (long) / RSI>70 (short)
  **only when EMA50>EMA200** (long side) — i.e. buy dips in uptrends, the golden-cross
  regime filter that survived at +0.017 spread.
- *Vol gate:* compute Ulcer Index / NATR percentile. **Size up** mean-reversion entries
  when UI is elevated (dips in stress get bought); **stand down** entirely when NATR is
  in its top 5% (crash risk — reversion breaks).
- *Trend overlay:* use EMA50/200 as the *only* trend gate; don't trade counter-trend
  mean-reversion when the 200-day slope is negative.

**Subjective strategy (discretionary).**
- Equity indices have a **long-side drift** (equity risk premium). Bias mean-reversion
  longs over shorts; treat short signals as "reduce/hedge," not "go net short."
- Short-term reversion **inverts into momentum around macro catalysts** (CPI, FOMC,
  earnings season). Suspend "buy the dip" into a known event; the dip may be information.
- Cross-index divergence is a tell: if ^NDX cracks while ^GSPC holds, trust the weaker
  one (breadth deteriorating). Use ^N225/^HSI overnight as a sentiment read for the US open.

### FX majors (DX-Y.NYB, EURUSD=X, USD/CHF)  ⭐ the one real edge

**Empirical read.** **Ultimate Oscillator is strongly contrarian at h1 (|IC|≈0.22)** —
the standout finding of the whole study, and it *sharpened* inside calm-bull regimes.
FX majors **mean-revert hard at 1–5 days.** Trend (Vortex) is weakly directional; volume
slot is **not applicable** (spot FX has no consolidated volume).

- **Momentum — Ultimate Oscillator 7-14-28.** Multi-timeframe oscillator. UO>70 = fade
  long / short bias; UO<30 = fade short / long bias. This is the pick to actually use.
- **Trend — Vortex-14** (directional, weak) as a *filter* only.
- **Volatility — RVI-14** for sizing.

**Technical strategy (mechanical).**
- *Reversion engine:* short EUR/USD (or long USD) when **UO>70**, cover/flip when UO
  crosses back below 50; symmetric on the downside. Best at h1–h5, then decays.
- *Confirm with RSI band:* require RSI(14)>70 or <30 alongside UO for higher-conviction
  entries (the RSI-threshold discrete also survived, +0.019 spread).
- *Regime sharpener:* the edge is strongest in **calm-bull (RC-01)**; widen bands or
  stand aside when VIX-Z is elevated (shock breaks mean-reversion → momentum).

**Subjective strategy (discretionary).**
- Respect the **carry/policy backdrop**: FX mean-reversion works within a range but
  *fails during trends driven by rate-differential shifts* (e.g. a hiking cycle). Check
  the 2Y yield spread direction before fading a move.
- **DXY as the hub:** trade EUR/USD and USD/CHF as expressions of USD strength; if DXY
  is breaking a multi-month level, drop the contrarian bias and go with the break.
- Time-of-day/liquidity matters (London/NY overlap); reversion signals on thin Asian
  liquidity are less reliable — discount them.

### Rates (^TNX yield, TLT)

**Empirical read.** ^TNX is **yield-based** (signals predict yield *changes*, not price).
Trend (Aroon Osc) is **directional at h10** — rate trends persist over ~2 weeks; short
horizon (MOM, RVI, ADOSC) is contrarian. The RSI-threshold discrete is notably contrarian
(−0.067 @h20).

**Technical strategy.**
- *Trend-follow the medium horizon:* Aroon Oscillator > 0 (and rising) = yields
  trending up → short duration / short TLT; use a 10-day holding horizon.
- *Fade the extreme:* at h1, MOM/RSI extremes in yields mean-revert — fade a 1-day yield
  spike. Supertrend(10,3) flip (+0.030 @h20) as the trend-state gate.

**Subjective strategy.**
- Rates are **policy-driven**: the dominant variable is the Fed path, not the chart.
  Use technicals for *timing within* a macro thesis, never against it.
- Watch the **2s10s curve**: a bull-steepener vs bear-flattener changes which end of the
  curve leads. TLT (long end) and ^TNX (10Y) should move inversely in price terms —
  divergence flags a curve move worth trading on the curve, not outright.

### Credit (LQD, HYG)

**Empirical read.** The **best non-FX magnitudes** (Vortex −0.10 @h20, TSI −0.09 @h10) —
both **contrarian**. Credit spreads are highly autocorrelated and mean-revert; these
ETFs have real volume so CMF (money flow) is meaningful (−0.07 @h5).

**Technical strategy.**
- *Spread reversion:* fade extended moves in HYG at the 1–2 week horizon (Vortex/TSI
  contrarian); confirm with CMF — a price drop on *outflows* (CMF<0) is more likely to
  extend, a drop on *inflows* is a buyable reversion.
- *Vol gate:* Ulcer Index on HYG as a stress meter — rising UI = risk-off; halt reversion
  longs.

**Subjective strategy.**
- Credit is the **canary**: HYG weakness *leading* equities is a genuine risk-off tell —
  trust it over the chart. Treat HYG less as a tradeable and more as a **regime input**
  for the equity book.
- Liquidity in HY dries up in stress; technical signals get unreliable exactly when you
  most want them. Size accordingly.

### Metals (GC=F gold, SI=F silver)

**Empirical read.** **No Trend or Momentum FDR survivor** — the flat screen found no
standalone directional edge (they wash out across regimes). Only Volatility (ATR-ratio,
POS) and Volume (CMF, contrarian) survived. This is the clearest **regime-masking**
candidate: gold's momentum likely lives in risk-off / real-rate regimes and averages to
zero flat.

- Volatility — **ATR-ratio-14** for sizing (works).
- Trend/Momentum — *(intuition)* see below; the screen is silent, not disproving.

**Technical strategy.**
- *Volatility-scaled trend (intuition):* gold **trends** structurally. Use **ADX-14 as a
  gate** (only take trend trades when ADX>25) plus an **EMA50/200** direction filter;
  size inversely to ATR-ratio. This is the classic metals approach even though flat IC
  is ~0 — because the payoff is regime-concentrated.
- *Silver = high-beta gold:* same signals, smaller size, wider stops (ATR-ratio is
  structurally higher).

**Subjective strategy.**
- Gold is a **real-rates and USD** instrument first, a chart second. Falling real yields
  + weak USD = the tailwind regime; that's when to lean into trend signals.
- Treat gold as **portfolio insurance**: its best trends coincide with equity stress, so
  a metals long is partly a hedge — hold through chop you'd cut elsewhere.

### Energy (CL=F WTI)

**Empirical read.** Like metals: **no Trend/Momentum survivor**, only **Volatility
(ATR-ratio, POS, |IC|≈0.08 @h10)** — the strongest volatility read in the study. WTI is a
**continuous front-month stitch** (roll artifacts at short horizons — discount h1).

**Technical strategy.**
- *Breakout trend-follow (intuition):* commodities are the classic CTA/trend market.
  **Donchian-20 channel breakout** entries, ATR-based trailing stop, is the archetypal
  crude system — flat IC is ~0 because trends are regime-bound (supply shocks), but the
  fat-tailed payoff favors trend-following.
- *Vol regime is real:* ATR-ratio elevated → widen stops and cut size; crude vol
  clusters violently.

**Subjective strategy.**
- Crude is driven by **inventories, OPEC, and the futures curve** (backwardation vs
  contango). Backwardation = structural tailwind for longs (positive roll); flip bias
  with the curve, not just the chart.
- Geopolitical spikes are **mean-reverting fear** unless supply is actually removed —
  fade the panic wick, hold the structural break.

---

## How to assemble the four slots into one decision

The slots combine, they don't compete:
1. **Volatility** sets the environment → position size and whether to trade at all
   (stand down at vol extremes).
2. **Trend** sets the *direction filter* → only take signals aligned with it (or only
   fade when ranging).
3. **Momentum** sets the *entry timing* → the oscillator extreme is your trigger.
4. **Volume** is the *confirmation* → veto entries where flow diverges from price.

**Default per-class posture from this study:**
- **FX:** momentum-led **mean-reversion** (UO), vol-gated. *(the real edge)*
- **Equity:** dip-buying **mean-reversion** in up-trends, vol-gated, event-aware.
- **Credit:** spread **mean-reversion** + use as a risk-off regime input.
- **Rates:** medium-horizon **trend-follow** the yield, fade 1-day extremes.
- **Metals/Energy:** **volatility for sizing is the only proven piece**; trend-follow
  is the intuitive best-guess for direction, to be validated by regime-conditioned
  testing on the right (risk-off / supply-shock) cells — not by flat IC.

---

## Caveats (do not skip)
- Empirical picks come from a **flat, full-history, single-indicator Spearman IC screen**.
  Not walk-forward, not cost-adjusted, not out-of-sample.
- *(intuition)* rows and every "Subjective strategy" block are **domain reasoning, not
  results** — they are hypotheses for the regime-conditioned run to test on single stocks
  and the right regime cells.
- Metals/Energy Trend & Momentum picks are explicitly **not supported by the flat data**
  (no FDR survivor) — included because the goal was "best available option," and their
  absence flat is itself the regime-masking signal to chase next.
- Signs (contrarian vs directional) are as important as the indicator name. Re-check them
  per asset before deploying.
