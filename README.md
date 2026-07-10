# Technical Analyst for Portfolio Construction — v1.1

Quant-research codebase that finds an **optimal set of technical indicators per asset**
(one each from the volume / trend / momentum / volatility families in `pandas_ta`),
turns each asset's set into a composite signal, and backtests a long-only,
cash-optional portfolio over 2024–2026 on 14 assets (global equity indices, metals,
energy, crypto).

**Headline result (2024–2026):**

| | Full-period return | Ann. vol | Sharpe (rf=0) | Max DD | Turnover |
|---|---:|---:|---:|---:|---:|
| Strategy — frozen OOS (sets ≤ 2023-12-31) | +62.5% | 11.4% | 1.77 | −10.9% | ~1.5–2.4×/yr |
| Strategy — **walk-forward** (annual re-selection) | **+67.7%** | 10.9% | **1.96** | −10.0% | — |
| Equal-weight buy & hold (benchmark) | +77.8% | 17.9% | 1.39 | −17.9% | — |

The strategy's edge is **risk-adjusted**, not raw return: it beats buy & hold on Sharpe
and drawdown while averaging only ~73% invested. Crucially, re-selecting each asset's
indicator set annually on an expanding window (**walk-forward**, `walkforward.py`) does not
degrade the frozen-cutoff result — it *improves* on it (+67.7% / 1.96 Sharpe), and narrows
the in-sample→out-of-sample overfit gap from 24.2pp to 19.1pp. That is evidence the edge is
not merely a lucky single cutoff — though the walk-forward has only 3 annual epochs (2026
partial), so treat it as a directional robustness floor, not a precise forecast. Full
results, per-asset indicator sets, and caveats: [`results/SUMMARY.md`](results/SUMMARY.md).

> **Reproducibility.** Every figure above is regenerated from the committed code and the
> committed `price_cache/` by `python portfolio_backtest.py` and `python walkforward.py`.
> Earlier releases published figures (frozen OOS +58.5% / 1.72, walk-forward +63.3% / 1.91)
> that the repository could **not** reproduce from its own contents — they were generated
> from an intermediate working state and never regenerated. Those numbers are corrected here.
> The strategy, the data and the conclusions are unchanged; only the stale figures moved.

**What's new in v1.1:** the walk-forward harness (**F1**) is the headline strategy, and the
repo now ships a full [**research log**](docs/RESEARCH-LOG.md) documenting *why* it works —
plus five subsequent attempts to beat it (learned cross-sectional signals, conviction
weighting, and meta-labeled exposure sizing) that were all **built, tested, and rejected**.
Their code is not here; their reasons are. See [Research log](#research-log--what-didnt-work).

## How it works

1. **Stage 1 — per-slot screen** (`pandasta_set_search.py`): every curated `pandas_ta`
   indicator (defaults only, causality-checked) is scored per asset by Spearman rank IC
   against 1/5/10/20-day forward returns with Newey–West HAC p-values; a pooled
   Benjamini–Hochberg FDR gate (q=0.10) keeps survivors. Slots with no survivor are
   filled by best |IC_IR| and flagged as weaker evidence.
2. **Stage 2 — joint set search**: top-5 per slot are combined; each candidate set's
   members are sign-aligned, causally z-scored (252d window) and equal-weight averaged
   into a composite; the winner per asset maximizes |composite IC_IR| at horizon 20,
   with a redundancy penalty.
3. **Portfolio** (`portfolio_backtest.py`): monthly rebalance deciding on prior-day
   data — rank all assets by composite signal, hold the top 8, park any
   negative-signal name in **cash at 0%**, weight the rest by inverse 63-day vol ×
   rank tilt, 5 bps/side costs. Two stabilizers are built into the strategy:
   **turnover smoothing** (each rebalance moves only halfway from current to target
   weights, so entries/exits fade over months instead of snapping 15% → 0 → 15%)
   and **signal-gated exits** (a holding may be liquidated fully only when its own
   composite signal is non-positive; falling out of the top 8 alone just trims it,
   floored at 0.5%).

**Look-ahead discipline:** OOS sets are selected on ≤2023 data only; all indicator
transforms are truncation-invariance tested; `dpo` is forced non-centered; the FDR
test suite includes mutation checks.

## Quickstart

Developed on Python 3.14 / pandas 3.x (3.12+ should work).

```bash
pip install -r requirements.txt
pytest tests -q                              # 41 tests

python pandasta_set_search.py                # rebuild indicator-set selection
python portfolio_backtest.py                 # backtest (OOS + IS + benchmark)
python walkforward.py                        # walk-forward re-selection baseline
python final-backtest/ta_advisor.py          # current advice: signals, holds, weights
```

`ta_advisor.py` is the agent/automation entry point: one command prints (or emits
JSON via `--json out.json`) the per-asset composite signals, which assets to hold and
why, and target portfolio weights including cash, using the frozen backtested sets.
`--refresh` pulls latest Yahoo prices into the cache first.

## Repository layout

| Path | What it is |
|---|---|
| `pandasta_registry.py` | Curated `pandas_ta` candidates, exclusions with reasons, causality guards |
| `pandasta_data.py` | 14-asset universe, price loading, master trading calendar |
| `pandasta_set_search.py` | Two-stage indicator-set search (FDR screen → joint composite) |
| `portfolio_backtest.py` | Portfolio construction + backtest engine (smoothing, exit gate) |
| `walkforward.py` | Walk-forward re-selection harness (v2·F1): annual re-selection, honest re-selected baseline + robustness diagnostics |
| `final-backtest/ta_advisor.py` | Single agent-facing CLI: analyze assets, list holds, output weights |
| `stats.py` | Audited IC / HAC / FDR statistics used by everything above |
| `price_cache/`, `price_cache.py` | Cached daily OHLCV CSVs (Yahoo Finance, through 2026-07) |
| `results/` | All outputs — start with `results/SUMMARY.md` |
| `tests/` | Pytest suite: causality, FDR pooling, cash accounting, smoothing math |
| `docs/RESEARCH-LOG.md` | Why F1 works, and why five attempts to beat it failed |
| `docs/superpowers/` | Design spec and implementation plan |

## Data notes

- Price data ships in `price_cache/` (daily OHLCV pulled from Yahoo Finance) so all
  results reproduce offline. Yahoo data is for personal/research use — check their
  terms before redistributing. Refresh via `python final-backtest/ta_advisor.py --refresh`
  or `python price_cache.py`.
- CSI 300 is proxied by the ASHR ETF; index legs (^GSPC etc.) are non-tradable
  proxies — live implementation needs futures/ETFs with their own costs.

## Research log — what didn't work

Beyond F1, **five** further ideas were designed, implemented under TDD, validated on the same
walk-forward harness, and **rejected**. Each had a pre-registered adoption bar: *beat F1's
Sharpe without worsening max drawdown by more than 2pp.* None cleared it. Each was compared
against an F1 **recomputed in the same run** (Sharpe **1.9603**), so every comparison is
apples-to-apples regardless of the stale-figure correction noted above.

| Idea | Axis | Its Sharpe / maxDD | Why it failed |
|---|---|---|---|
| **F2** — pooled ridge → raw 20d return, replaces the composite | cross-sectional | 1.67 / −17.1% | Raw-return **drift** made every prediction positive → the cash gate never fired → ~100% invested (vs F1's ~74%) → became buy & hold |
| **F2b** — ridge → cross-sectional z-score, used as tilt *order* | cross-sectional | 1.88 / −10.0% | Drift fixed, exposure pinned — still no edge. Ridge penalty pegged at grid max, **coefficients ≈ 0** |
| **F4** — weight ∝ (1/vol) × min(composite, 3) | cross-sectional | 1.83 / −9.3% | Concentrated the top holding (29.3% vs 19.3%) but the composite's **magnitude is a noisy conviction proxy**; the even rank tilt is near-optimal |
| **F2b+F4** — weight ∝ (1/vol) × exp(model prediction) | cross-sectional | 1.91 / −11.2% | Model predictions are ≈ 0 (std 0.04), so weighting **collapses to near-uniform**. Stacking two failures doesn't create edge |
| **F3** — meta-labeling → confidence modulates *exposure* | timing / exposure | 1.9599 / −10.0% | No timing edge either. Penalty pegged at grid max; **largest coefficient 0.003**; exposure multipliers never left neutral |

(F2 predates the figure correction and was recorded against the then-published F1 of 1.91; its
margin is wide enough that the correction does not affect its verdict.)

**The conclusion.** Five schemes across two orthogonal axes — *which names to hold* and *when to
be invested* — every one measured coefficients at ≈ 0. On 14 assets, ~3 out-of-sample years and
~95 monthly training observations with composite ICs of 0.02–0.13, **there is no exploitable
signal beyond what the equal-weight composite already extracts.** The binding constraint is
sample size and overfitting, not model capacity. F1 appears to be at the frontier of what these
features support; more return would have to come from better **inputs**, not a cleverer layer.

The full write-up — including why F1 improves on the frozen cutoff, and the transferable
engineering lessons (e.g. *make a skill-less model structurally unable to do harm*) — is in
[**`docs/RESEARCH-LOG.md`**](docs/RESEARCH-LOG.md).

## Caveats — read before trusting any number

Composite ICs are small (0.02–0.13). The canonical backtest freezes sets on a single
cutoff; `walkforward.py` now re-selects annually and confirms the edge holds (see above),
but with only 3 epochs it is a directional check, not a rich validation. The IS variant is
an in-sample upper bound (IS−OOS gap ≈ 24.2pp, IS−walk-forward ≈ 19.1pp are the measured
overfitting costs). The smoothing speed (λ=0.5) was not selected out-of-sample. 2026 is a
partial year. Sharpe uses rf=0.

**This is research code. Nothing here is investment advice.**
