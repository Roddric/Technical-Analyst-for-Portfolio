# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A small, standalone quant-research codebase (no package manifest, no test suite, no build system) consisting of two independent Python modules:

- **`phase1_segment.py`** — Regime Segmentation Engine ("Phase 1"). Classifies each historical trading day into a `(regime_code, sector)` cell from OHLCV + macro data. Feeds a downstream "Phase 2" (IC computation) that is not part of this repo — `phase1_segment.py` only produces the labeled cells and per-cell observation counts that Phase 2 would consume.
- **`allocation_engine.py`** — portfolio weighting. Takes a covariance matrix (+ optionally the audited ICs baked into `SIGNAL_IC`) and produces risk-parity or signal-tilted weights. Consumes the *output* of the Phase 1/2 pipeline (`regime_ic_results.csv`, audited IC-by-cell), not its live output directly.

There is no dependency between the two files at import time — they are run/read independently.

## Running

No package manager, lockfile, or requirements.txt exists. Dependencies are plain `numpy`, `pandas`, `scipy` for `phase1_segment.py` (plus optional `yfinance`/`requests` only inside the data-loader functions), and `numpy`, `pandas` for `allocation_engine.py`.

```bash
python phase1_segment.py       # runs the synthetic-data validation in __main__
python allocation_engine.py    # runs the demo in _demo() under __main__
```

There are no automated tests. `phase1_segment.py`'s `__main__` block *is* the validation harness: it builds synthetic OHLCV/VIX/macro data and asserts nothing, but prints regime distributions, a shock-period slice, and cell stats for manual inspection — check this output whenever Phase 1 logic changes. Likewise `allocation_engine.py`'s `_demo()` prints risk-parity vs signal-tilted weights over a placeholder covariance for manual inspection.

To exercise a single function interactively, import it directly, e.g.:
```bash
python -c "from phase1_segment import compute_axis1_trend; ..."
```

## Architecture — `phase1_segment.py`

The engine is a **Fast Layer / Slow Layer / Priority Arbiter** design:

- **Fast Layer** (daily, price/vol-driven, no lookahead risk): computes four axes from OHLCV/VIX/credit-spread/yield data.
  - Axis 1 — Trend (`compute_axis1_trend`): Bull/Bear/Sideways from price-vs-200DMA, 3-month return, and Wilder ADX (`_wilder_adx`, hand-rolled — not from a TA library, per the module's "no external TA libraries" constraint).
  - Axis 2 — Volatility (`compute_axis2_vol`): High/Low/Mid from VIX Z-score (126D rolling) with a realized-vol AND-condition; falls back to percentile rank ("bootstrap" `vol_mode`) when there's under `VIX_COLDSTART_DAYS` (63) days of history.
  - Axis 4 — Shock (`compute_axis4_shock`): Active/Watch/None from *relative* VIX Z-score + velocity + HY spread Z-score — deliberately not fixed VIX levels.
  - Steepener type (`compute_steepener_type`): yield-curve regime tiebreaker on a 40-session window; spread is diffed *after* computing 10Y−2Y (not diffed independently then subtracted) to avoid float drift.
- **Slow Layer** (`compute_axis3_cycle`, quarterly/monthly macro cadence): Axis 3 — Economic cycle (Expansion/Reflation/Stagflation/Recession) from vintage-only GDP/CPI/unemployment/ISM/Fed-stance signals, weighted-vote scored. **Hard-enforces a vintage mandate**: raises `ValueError` if `vintage_flag` isn't all `True` — this is the look-ahead-bias guard. Never feed it revised/current-vintage series.
- **Priority Arbiter** (`priority_arbiter`): combines Fast + Slow into one `RegimeResult` via 7 ordered rules (shock override suppresses Axis 3; fast owns axes 1/2/4; slow owns axis 3; staleness penalty; transition detection/haircut; steepener-contradiction penalty; execution floor). Below `EXECUTION_FLOOR` (60) confidence, a day is flagged (not dropped) for Cash/Neutral treatment downstream.
- **`REGIME_MAP`** maps the 4-axis tuple to one of 20 `RC-01`..`RC-20` labeled regimes. Unmapped combinations fall back through `_nearest_regime`, which relaxes axes in a fixed priority order (shock → vol → trend → cycle) before defaulting to `RC-10`.
- **Dynamic Sector Assignment** (`assign_sector`): assigns a ticker to one of `SECTORS` via rolling 60-day Pearson correlation only (beta is computed but is diagnostic-only, never used in the assignment decision, by design).
- **`segment_history`** is the orchestration entry point tying all of the above into one per-day DataFrame; **`compute_cell_stats`** aggregates the result into `(regime_code, assigned_sector)` cells and flags `low_sample` cells (< `MIN_CELL_OBS` = 30 obs) that Phase 2 should treat with a Bayesian prior instead of the empirical IC.

### Data-vintage discipline (critical, easy to violate silently)

`load_fred_series()` (current/revised data) and `load_alfred_first_prints()` (first-print/vintage data, `output_type=4`) are **not interchangeable**. Fast Layer series (DGS2, DGS10, HY OAS) may use either; **Slow Layer macro inputs (GDP, CPI, ISM, etc.) must go through `load_alfred_first_prints`/`build_macro_vintage_frame`** — mixing in revised data reintroduces look-ahead bias that `compute_axis3_cycle`'s vintage-flag check is specifically designed to catch. If you add a new Slow Layer input, wire it through the vintage path and make sure it carries `vintage_flag=True`.

Similarly, Slow Layer data is forward-filled and reindexed against the **actual trading calendar** (`spy_ohlcv.index`), not `pd.date_range(freq="B")` — the latter includes market holidays and causes row misalignment. Preserve this reindex-against-real-calendar pattern in any new alignment code.

## Architecture — `allocation_engine.py`

Two independent weighting schemes over a covariance matrix:

- **Risk parity**: `inverse_vol_weights` (closed-form 1/σ) and `erc_weights` (true equal-risk-contribution via projected gradient descent, `iters`/`lr` tunable). Needs no signal input.
- **Signal-strength weighting** (`signal_strength_weights`): tilts the risk-parity base by a per-asset-class conviction score derived from `SIGNAL_IC`. `SIGNAL_IC` is hardcoded per `(asset_class, slot)` from **audited, FDR-surviving** IC results in `regime_ic_results.csv` (a file outside this repo) — a missing key means "no survivor," which resolves to a `0.0` tilt, not a guess. The tilt is capped (`tilt_cap`, default 0.5) so a weak/noisy signal can never dominate the risk-parity base.

Read the module docstring's "HONESTY CONSTRAINTS" section before trusting any output: the ICs were measured on a broad-index universe, not on single-name/sector tickers, so `asset_class_signal_score` assumes a ticker behaves like its asset class — unvalidated for single names. `_demo()`'s covariance matrix is an explicitly **labeled placeholder** (asset-class vol/correlation priors, not real sample covariance) — replace it with a real covariance from actual returns before using any weight operationally. When extending this file, preserve the same honesty-labeling convention: never let a missing/synthetic input silently masquerade as validated data.
