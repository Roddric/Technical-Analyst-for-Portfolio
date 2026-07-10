# Research log — what worked, what didn't, and why

**Version:** v1.1 · **Last updated:** 2026-07-09

This file is the honest record of the v2 research programme built on top of the v1 strategy.
One idea was adopted (**F1**). Five were built, tested, and **rejected** (F2, F2b, F4, F2b+F4,
F3). The rejected code is not in this repo — the *reasons* are, because they are the more
valuable output.

> **A correction, and why it matters.** Releases before v1.1 published F1 at
> **+63.3% / Sharpe 1.91 / −10.6%** and a frozen OOS of **+58.5% / 1.72 / −11.6%**. Those
> figures are **not reproducible from this repository's own contents.** Running
> `walkforward.py` at the very commit that shipped them — its own code, its own
> `price_cache/`, its own selection CSVs — produces **+67.7% / 1.9603 / −10.0%**. The reports
> were generated from an intermediate working state and never regenerated before commit.
>
> It was *not* a data change: the price cache has been byte-identical since the baseline
> commit, and the in-sample and buy & hold rows reproduce to the last digit. Nor was it a code
> or selection change: the 14 winning sets, every `traded_sign`, and all 3,848 stage-1 IC rows
> at the `2023-12-31` cutoff are bit-identical, and `build_signals` is unchanged. Only the
> two variants that flow from that cutoff moved, and they moved together — while the
> continuity invariant (walk-forward 2024 = frozen-OOS 2024, bit-identical) still holds.
>
> The figures throughout this document are the **reproducible** ones. All five rejected
> experiments were compared against an F1 **recomputed in the same run** (Sharpe 1.9603), so
> the correction leaves every verdict untouched.

---

## Adopted: F1 — walk-forward re-selection

### What it is

The v1 strategy picks each asset's indicator set **once**, on a single frozen cutoff (all data
≤ 2023-12-31), then backtests 2024–2026 on those frozen choices. The obvious worry: those picks
might be an artifact of one arbitrary train/test boundary.

F1 (`walkforward.py`) instead **re-runs the entire two-stage selection at annual expanding-window
cutoffs** (2023-12-31 → 2024-12-31 → 2025-12-31). Each freshly re-selected set governs the
*following* year's monthly rebalances, and every rebalance date is spliced to the set that was
actually current at that moment — so there is no look-ahead.

### The measured result

| Variant | Full return | Ann. vol | Sharpe | Max DD |
|---|---:|---:|---:|---:|
| **Walk-forward (annual re-selection)** | **+67.7%** | 10.9% | **1.96** | −10.0% |
| Frozen OOS (single cutoff) | +62.5% | 11.4% | 1.77 | −10.9% |
| In-sample (upper bound, not a forecast) | +86.8% | 11.7% | 2.21 | −10.3% |
| Equal-weight buy & hold | +77.8% | 17.9% | 1.39 | −17.9% |

### Why it gives better results

Three distinct reasons, and it is worth separating them:

1. **It removes a lucky-cutoff artifact — and the edge survives.** This is the *primary* value.
   Re-selection is a harder test than a frozen cutoff, and the strategy passed it. Beating the
   frozen baseline on return, Sharpe **and** drawdown simultaneously is evidence the edge is
   real rather than an accident of where the train/test line was drawn.

2. **It adapts to drift in indicator efficacy.** Which indicator predicts an asset is not
   stable across years. Re-selecting annually lets each asset track its own drift instead of
   being locked to a 2023 answer for three years. The set-stability diagnostic shows this is
   moderate, not chaotic (`^N225`/`^TWII` unchanged in all four slots; the trend slot is
   `dpo`-dominant; `VWO` churns most at ~2.5 of 4 slots per step) — i.e. it is tracking drift,
   not fitting noise.

3. **It measurably reduces overfitting.** The in-sample minus out-of-sample gap narrows from
   **24.2pp** (frozen) to **19.1pp** (walk-forward). That gap *is* the cost of selection
   overfitting; shrinking it means less of the reported performance is illusory.

A continuity check confirms the plumbing: walk-forward 2024 is **bit-identical** to frozen-OOS
2024, because every 2024 rebalance is governed by the 2023-12-31 epoch. If the date-splicing
were wrong, that identity would break.

### Why the strategy beats buy & hold on Sharpe but not on return

The edge is **risk-adjusted, not raw**. The book averages only ~73% invested: names with a
non-positive composite signal sit in **cash at 0%**. In a strong bull market that cash drag
guarantees it trails buy & hold on total return (+67.7% vs +77.8%) — while delivering a far
better Sharpe (1.96 vs 1.39) and **little more than half the drawdown** (−10.0% vs −17.9%).
Three mechanics produce that: the cash gate, inverse-volatility weighting, and the pair of
stabilizers (turnover smoothing at λ=0.5, plus signal-gated exits).

### The honest limit

Only **3 annual epochs** (2026 is partial). This is a directional robustness floor, not a
statistically rich validation.

---

## Rejected: five attempts to beat F1

Every experiment was judged on the same F1 walk-forward harness, with a pre-registered adoption
bar: **beat F1's Sharpe without worsening max drawdown by more than 2pp.** None cleared it.

The attempts split across two orthogonal axes:

- **Cross-sectional** — *which* names to hold, and *how much* of each: F2, F2b, F4, F2b+F4.
- **Timing / exposure** — *when* to be invested vs in cash: F3.

| # | Idea | Its Sharpe | Max DD | Why it failed |
|---|---|---|---|---|
| F2 | Pooled ridge → raw 20d return, **replaces** the composite | **1.67** | −17.1% | Target drift switched off the cash gate |
| F2b | Ridge → cross-sectional z-score, used as tilt **order** | **1.88** | −10.0% | No cross-sectional edge (coefs ≈ 0) |
| F4 | Weight ∝ (1/vol) × min(composite, 3) — cardinal conviction | **1.83** | −9.3% | Signal *magnitude* is a noisy conviction proxy |
| F2b+F4 | Weight ∝ (1/vol) × exp(model prediction) | **1.91** | −11.2% | Inherits F2b's zero-signal model |
| F3 | Meta-labeling → confidence modulates **exposure** | **1.9599** | −10.0% | No timing edge either (coefs ≈ 0) |

### F2 — pooled ridge, raw-return target *(the instructive failure)*

Pooled features across all 14 assets (per-slot z-scores, volatility, asset-class, interactions)
into a ridge regression predicting each asset's **raw 20-day forward return**, with purged and
embargoed cross-validation. The prediction *fully replaced* the composite: its **sign** decided
cash, its **value** decided ranking.

**Why it failed — a target-design error, not a modelling one.** Raw forward returns have
**positive drift** (markets rise). So nearly every prediction came out positive, the sign-based
cash gate **never fired**, and the book sat at **~100% invested vs F1's ~74%**. The strategy
silently collapsed into buy & hold: more raw return (+93%) but **worse Sharpe (1.67, against
an F1 of ~1.9) and a drawdown of −17.1% vs F1's ~−10%**.

Two lessons, both load-bearing for everything after:

- **A drift-dominated target destroys a defensive mechanism** without ever throwing an error.
- Cross-validation had already told us the truth and we could have listened sooner: the ridge
  penalty pegged at the **grid maximum** with coefficients ≈ 0.001. The pooled features carried
  no cross-sectional edge over a simple equal-weight composite.

### F2b — rank-only learned tilt

A careful fix for F2's exact defect. Two independent changes: (1) the target became a
**cross-sectionally de-meaned z-score** (relative performance within each date), so market drift
is removed *by construction*; and (2) the model was demoted to **tilt-only** — the composite kept
the entire cash/hold gate, and the model could only **re-order which held name got which weight**.
Gross exposure and drawdown were pinned to F1 by construction.

**Why it failed.** Even with drift removed and exposure pinned: **Sharpe 1.88 vs a same-run F1 of
1.96**, drawdown identical at −10.0%, cash discipline matched (avg invested 75.65% vs 75.72% —
confirming the tilt-only wiring held, so the negative result is real and not leaked exposure).
The ridge penalty *again* pegged at the grid maximum with coefficients ≈ 0.

**The lesson is deeper than F2's:** it was never the target that was broken. **These pooled
features simply do not rank names any better than an equal-weight composite already does.**

### F4 — uncapped, conviction-weighted portfolio *(no ML)*

A deliberately non-ML change to portfolio *construction*. Two moves: **uncap membership** (hold
every positive-signal name, not an arbitrary top-8), and weight each holding by **conviction** —
`(1/vol_63d) × min(signal, 3)` — instead of the ordinal rank tilt. The gross denominator was left
unchanged, so total invested (and therefore drawdown) stayed **pinned to F1 by construction**,
isolating exactly one question: *does sizing by conviction beat sizing evenly?*

**Why it failed.** **Sharpe 1.83 vs 1.96** — worse, though with a *shallower* drawdown (−9.3% vs
−10.0%). Conviction weighting did what it promised: it concentrated the top holding to **29.3%
vs F1's 19.3%**. Concentrating in the highest-magnitude names simply didn't pay, because the
composite's *magnitude* is too noisy a measure of conviction (composite ICs are only 0.02–0.13).
F1's even-handed rank tilt turns out to be near-optimal.

Two robustness checks, both confirming:
- **Removing the cap changed nothing** — bit-identical results, because the +3 cap **never binds**:
  the strongest held-side signal at any of the 31 rebalance dates is only **2.49**.
- Uncapping membership barely moved breadth (11.35 vs 11.45 avg names held), because the
  signal-gated exit mechanic already carries ~11 fading names.

### F2b + F4 — learned conviction

The fusion: F4's structure (uncapped, exposure pinned) but with the conviction weight driven by
**F2b's learned model prediction** rather than the composite magnitude —
`weight ∝ (1/vol) × exp(model_prediction)`. In effect, asking the model not to *rank* names
(F2b) but to *size* them (F4).

**Why it failed.** **Sharpe 1.91 vs a same-run F1 of 1.96**, with a *worse* −11.2% drawdown. The diagnostic is
decisive: the model's predictions on held names have **mean 0.03, standard deviation 0.04** — the
same ≈ zero-coefficient problem. `exp()` of near-zero values is ≈ 1 for every name, so the
"conviction" weighting **collapses back to near-uniform**, landing just short of F1. Stacking two
mechanisms that failed for the *same root cause* cannot manufacture an edge that isn't there.

### F3 — meta-labeling + confidence-based exposure sizing

The last untried axis: **timing**, not cross-section. F1's composite stayed the *primary* model
(which names, and the cash gate). Two small L2-regularized logistic **meta-models** predicted
whether acting on it currently pays off; their confidence modulated **exposure only** — a
portfolio model scaled gross, a per-name model trimmed a holding toward **cash** (never
redistributed to peers, which would smuggle the dead cross-sectional axis back in).

**The critical design decision.** Exposure was keyed to `(p − p_base)` — the model's *deviation
from its own causally-estimated training base rate* — **not** to the raw probability `p`. This
matters enormously: the label ("being invested beat cash") is true **68–71%** of the time. Had
exposure keyed off raw `p`, a skill-less model would have predicted ~0.70 everywhere, pinned the
book near fully-invested, and **reproduced F2's blow-up exactly**. Keying off the deviation means
a model with no edge emits multipliers of *exactly 1.0*, so **F3 degrades precisely to F1** rather
than to buy & hold.

**Why it failed.** All four ablations land on top of F1:

| Ablation | Return | Sharpe | Max DD | Avg invested |
|---|---:|---:|---:|---:|
| F1 walk-forward | +67.70% | **1.9603** | −10.01% | 75.72% |
| + portfolio timing only | +67.61% | 1.9593 | −9.99% | 75.67% |
| + per-name only | +67.70% | 1.9609 | −10.00% | 75.69% |
| **F3 (+both)** | +67.63% | 1.9599 | −9.98% | 75.65% |

The diagnostics prove the models learned nothing rather than leaving it to inference:

- Logistic penalty **pegged at the grid maximum (1000.0) for both models at all three cutoffs**.
- Largest fitted coefficient: **0.0031** (portfolio `vol`), **−0.0080** (per-name `ic_name`).
- Exposure multipliers **never left neutral**: portfolio ∈ [0.9966, 1.0023], per-name ∈
  [0.9935, 1.0100] — against clip bounds of [0.6, 1.4] and [0.5, 1.5]. The models were *allowed*
  to move exposure ±40%; they moved it ±0.3%.
- `n_train` = **95** monthly observations at the first cutoff. Sample size is the binding
  constraint, not model capacity.

Crucially, the multiplier spread is tiny but **nonzero**. A wiring bug (all-NaN pivot, a
never-matching date key, dead features) would produce multipliers of *exactly* 1.0 with **zero**
spread. The hook demonstrably moves the book — it just moves it negligibly. **The negative result
is genuine, not a plumbing failure.**

---

## The conclusion

Five schemes. Two orthogonal axes. **Every one measured coefficients at ≈ 0.**

On this data — **14 assets, ~3 out-of-sample years, ~95 monthly training observations, composite
ICs of 0.02–0.13** — there is **no exploitable signal beyond what the equal-weight composite
already extracts**, on either axis. The binding constraint is *sample size and overfitting*, not
model capacity. That was the stated hypothesis at the outset; it has now been tested five ways
and held every time.

**F1 is not a disappointing result. It is the frontier of what these features support.** It beats
the frozen-cutoff baseline on return, Sharpe *and* drawdown; it beats equal-weight buy & hold on
Sharpe (1.96 vs 1.39) with roughly half the drawdown; and five serious, independently-designed
attempts to improve on it all failed.

**If more return is wanted, it will not come from a cleverer model layer on these features.** It
has to come from changing the **inputs** — a larger universe, longer history, or genuinely
different signals — so that a model has something to find.

---

## Transferable engineering lessons

Worth keeping regardless of this particular strategy:

1. **Make a skill-less model structurally unable to do harm.** F2 blew up because exposure keyed
   off a drift-dominated raw prediction. F3 keyed off deviation from a causal base rate, so a
   no-edge model degraded *exactly* to the baseline. Design the layer so that "the model learned
   nothing" collapses to your baseline, not to a different and worse strategy.

2. **Pin exposure; change only composition.** When testing a cross-sectional idea (F2b, F4), hold
   gross exposure fixed by construction. It isolates the question being asked and bounds the
   drawdown risk of being wrong.

3. **Pre-register the verdict.** F3 declared "judge on `+both`" *before* the run. The ablations
   are diagnostics that tell you *which* component is empty — not a menu to pick the flattering
   number from afterwards.

4. **A negative result must be proven, not inferred.** "No effect" and "broken wiring" look
   identical in a results table. Check that your coefficients and multipliers are *live* (small
   but nonzero spread) before believing a null.

5. **Watch the regularization path.** In F2, F2b and F3, the penalty pegging at the grid maximum
   with near-zero coefficients was the model *telling us there was no signal* — several
   experiments before the backtest confirmed it.
