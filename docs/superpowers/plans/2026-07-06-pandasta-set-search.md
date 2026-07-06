# pandas_ta Indicator-Set Search + Long-Only Portfolio Backtest — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Per-asset optimal (volume, trend, momentum, volatility) pandas_ta indicator sets via a two-stage IC screen, then a long-only 100%-invested monthly-rebalanced portfolio backtested over 2024–2026 with OOS and IS selection variants side by side.

**Architecture:** Three new modules in `Work/ta-flat-backtest/` reusing the audited `stats.py` engine and `price_cache.py`: a candidate registry (`pandasta_registry.py`), the two-stage screen (`pandasta_set_search.py`), and the portfolio engine (`portfolio_backtest.py`). Tests in `tests/` with pytest.

**Tech Stack:** Python 3.14 venv at `C:\Users\l\quant-workspace\.venv` (already active for `python`), pandas 3.0.3, numpy 2.5.0, scipy 1.18.0, pandas_ta 0.4.24, yfinance 1.5.1, pytest 9.1.1.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-06-pandasta-set-search-design.md`. Working directory for ALL commands: `C:\Users\l\quant-workspace\Work\ta-flat-backtest` (the parent project, a git repo).
- **`import importlib.metadata` MUST precede `import pandas_ta`** (Python 3.14 + pandas_ta 0.4.24 crash otherwise — verified).
- Mirror prior-run conventions exactly: `HORIZONS = [1, 5, 10, 20]`, `ROLL_WINDOW = 63`, `FDR_Q = 0.10`, BH-FDR pooled across ALL continuous tests in the run, output schema of `results/flat_ic_results.csv`.
- Stage-2/composite: causal z-score window 252, min_periods 126; top **5** per slot by max |IC_IR| across horizons; strategy set = best |composite IC_IR| at **h=20**; traded sign = sign(composite IC at h=20 in selection window).
- Portfolio: top **8** assets, tilt = 1 + 0.5 × scaled_rank ∈ [0.5, 1.5] on inverse 63-day-vol base; monthly rebalance (first trading day, decision on prior day's data); 5 bps per side (cost = 0.0005 × Σ|Δw|); always fully invested, long-only; rf = 0; benchmark = equal-weight buy-and-hold.
- Selection windows: OOS cutoff `2023-12-31`, IS cutoff `None` (full history). Backtest window: 2024-01-01 → last available data (~2026-07).
- Universe = `ASSETS` from `grouped_ic_backtest.py` + `BTC-USD`, `ETH-USD` (class `crypto`). Tradable set excludes `^TNX`. `^TNX` uses `return_mode="diff"`. Master calendar = ^GSPC trading days; crypto ffilled onto it.
- Git identity for commits: use `git -c user.name="l" -c user.email="limroddric@gmail.com" commit ...` (repo has no configured identity).
- Every results artifact carries the honesty disclosures from the spec (flat-history, IS = upper bound, proxies, rf=0, partial 2026).

---

### Task 1: Candidate registry with causality guarantee

**Files:**
- Create: `pandasta_registry.py`
- Test: `tests/test_registry.py` (create `tests/` with empty `tests/__init__.py`)

**Interfaces:**
- Produces: `Candidate` dataclass (`name, slot, fn, column, kwargs, uses_volume, derived`), `build_candidates() -> list[Candidate]`, `compute_candidate(df: pd.DataFrame, cand: Candidate) -> pd.Series` (float64, index-aligned to `df`, NaN where undefined), `SLOTS = ("volume", "trend", "momentum", "volatility")`.
- Consumes: nothing project-internal.

The registry enumerates pandas_ta's category map at defaults, with an explicit exclusion table (probed 2026-07-06 in this venv) and an explicit primary-column map for multi-column outputs. Derived band-width candidates and `atr_ratio` mirror `indicators.py`'s normalization rule (never a raw price level).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_registry.py
import numpy as np
import pandas as pd
import pytest

from pandasta_registry import SLOTS, build_candidates, compute_candidate


def synth_ohlcv(n=700, seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-02", periods=n)
    c = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, n))), index=idx)
    h = c * (1 + np.abs(rng.normal(0, 0.004, n)))
    l = c * (1 - np.abs(rng.normal(0, 0.004, n)))
    o = c.shift(1).fillna(c.iloc[0])
    v = pd.Series(rng.integers(100_000, 1_000_000, n).astype("float64"), index=idx)
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": v})


def test_all_slots_populated():
    cands = build_candidates()
    by_slot = {s: [c for c in cands if c.slot == s] for s in SLOTS}
    for s in SLOTS:
        assert len(by_slot[s]) >= 5, f"slot {s} too thin: {len(by_slot[s])}"
    names = [c.name for c in cands]
    assert len(names) == len(set(names)), "duplicate candidate names"


def test_volume_candidates_tagged():
    for c in build_candidates():
        if c.slot == "volume":
            assert c.uses_volume, f"{c.name} in volume slot must be uses_volume"


def test_compute_returns_aligned_float_series():
    df = synth_ohlcv()
    for cand in build_candidates():
        x = compute_candidate(df, cand)
        assert isinstance(x, pd.Series), cand.name
        assert x.index.equals(df.index), cand.name
        assert x.dtype == "float64", cand.name
        # must produce real values on >30% of bars after warm-up
        assert x.iloc[300:].notna().mean() > 0.3, f"{cand.name} mostly NaN"


def test_causality_truncation_invariance():
    """indicator[t] must not change when future bars are removed.
    Catches centered/repainting indicators (dpo centered, zigzag, ...)."""
    df = synth_ohlcv()
    cut = 25
    for cand in build_candidates():
        full = compute_candidate(df, cand).iloc[: len(df) - cut]
        trunc = compute_candidate(df.iloc[: len(df) - cut], cand)
        pd.testing.assert_series_equal(
            full, trunc, check_exact=False, rtol=1e-9, atol=1e-12,
            obj=f"causality violation in {cand.name}",
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_registry.py -x -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'pandasta_registry'`

- [ ] **Step 3: Write the registry**

```python
# pandasta_registry.py
"""
pandasta_registry.py
====================
Curated enumeration of pandas_ta indicators at DEFAULT parameters for the four
slots (volume, trend, momentum, volatility).

Rules (mirrors indicators.py design):
  * No raw price-LEVEL outputs (MA-type lines, band levels, trailing stops).
    Band information enters only as %B or normalized width.
  * Everything must be causal: indicator[t] depends only on bars <= t.
    dpo is forced centered=False (pandas_ta default is centered = lookahead).
    zigzag / ichimoku-style forward or repainting outputs are excluded.
  * Multi-column outputs contribute ONE explicit primary column.
Probed against pandas_ta 0.4.24 on 2026-07-06; qqe and psar return empty at
defaults on daily synthetic data and are excluded.
"""
from __future__ import annotations

import importlib.metadata  # noqa: F401  (must precede pandas_ta on py3.14)
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import pandas_ta as ta  # noqa: F401  (df.ta accessor)

SLOTS = ("volume", "trend", "momentum", "volatility")

# fn -> reason, for the audit trail in reports
EXCLUDED = {
    "qqe": "empty output at defaults (probe 2026-07-06)",
    "psar": "empty output at defaults (probe 2026-07-06)",
    "smc": "multi-structure output, no scalar primary line",
    "exhc": "sparse exhaustion counts, mostly NaN",
    "squeeze_pro": "duplicate of squeeze with binary flags",
    "ht_trendline": "raw price level",
    "decay": "utility transform, not a signal",
    "increasing": "binary utility",
    "decreasing": "binary utility",
    "long_run": "requires external fast/slow inputs",
    "short_run": "requires external fast/slow inputs",
    "tsignals": "requires external trend input",
    "xsignals": "requires external signal input",
    "zigzag": "repaints (non-causal by construction)",
    "amat": "binary state pair",
    "rwi": "paired high/low lines, no scalar primary",
    "alphatrend": "trailing price level",
    "cksp": "stop price levels",
    "atrts": "trailing-stop price level",
    "aberration": "band price levels",
    "accbands": "band price levels (width captured as derived ACCB_WIDTH)",
    "donchian": "band price levels (width captured as derived DC_WIDTH)",
    "kc": "band price levels (width captured as derived KC_WIDTH)",
    "hwc": "channel price levels",
    "chandelier_exit": "stop price levels",
    "atr": "price-scaled; normalized form kept as natr + derived ATR_RATIO",
    "true_range": "price-scaled level",
    "pdist": "price-scaled level",
    "thermo": "price-difference-scaled level",
    "bbands": "band levels; %B kept as primary column candidate",
    "vwap": "anchored intraday concept + price level",
    "vwma": "raw price level",
    "pvol": "price*volume trending level",
    "pvr": "1-4 categorical code",
    "aobv": "bundle incl. binary run flags",
    "kdj": "kept via stoch (K duplicates)",
}

# fn -> primary output column (multi-column outputs only)
PRIMARY_COL = {
    "brar": "AR_26",
    "eri": "BULLP_13",
    "fisher": "FISHERT_9_1",
    "kst": "KST_10_15_20_30_10_10_10_15",
    "macd": "MACDh_12_26_9",
    "ppo": "PPOh_12_26_9",
    "rvgi": "RVGI_14_4",
    "smi": "SMI_5_20_5_1.0",
    "squeeze": "SQZ_20_2.0_20_1.5",
    "stc": "STC_10_12_26_0.5",
    "stoch": "STOCHk_14_3_3",
    "stochf": "STOCHFk_14_3",
    "stochrsi": "STOCHRSIk_14_14_3_3",
    "tmo": "TMO_14_5_3",
    "trix": "TRIX_30_9",
    "tsi": "TSI_13_25_13",
    "adx": "ADX_14",
    "aroon": "AROONOSC_14",
    "vortex": "VTXP_14",
    "kvo": "KVO_34_55_13",
    "pvi": "PVI",
    "pvo": "PVOh_12_26_9",
    "wb_tsv": "TSV_18_10",
    "bbands": "BBP_5_2.0",
}

PER_FN_KWARGS = {
    "dpo": {"centered": False},  # pandas_ta default centered=True is lookahead
}

SLOT_PREFIX = {"momentum": "MO", "trend": "TR", "volatility": "VO", "volume": "VU"}


@dataclass(frozen=True)
class Candidate:
    name: str
    slot: str
    fn: str                 # pandas_ta accessor name, or derived key
    column: str | None      # column when output is a DataFrame
    kwargs: dict = field(default_factory=dict)
    uses_volume: bool = False
    derived: str | None = None  # None | "atr_ratio" | "kc_width" | "dc_width" | "accb_width"


def _derived_candidates() -> list[Candidate]:
    return [
        Candidate("VO-ATR_RATIO", "volatility", "atr_ratio", None, {}, False, "atr_ratio"),
        Candidate("VO-KC_WIDTH", "volatility", "kc_width", None, {}, False, "kc_width"),
        Candidate("VO-DC_WIDTH", "volatility", "dc_width", None, {}, False, "dc_width"),
        Candidate("VO-ACCB_WIDTH", "volatility", "accb_width", None, {}, False, "accb_width"),
        Candidate("VO-BBP", "volatility", "bbands", "BBP_5_2.0", {}, False, None),
    ]


def build_candidates() -> list[Candidate]:
    cats = {s: sorted(ta.Category[s]) for s in SLOTS}
    volume_fns = set(cats["volume"]) | {"mfi"}
    out: list[Candidate] = []
    for slot in SLOTS:
        for fn in cats[slot]:
            if fn in EXCLUDED:
                continue
            if slot == "volatility" and fn == "bbands":
                continue  # added via _derived_candidates as VO-BBP
            name = f"{SLOT_PREFIX[slot]}-{fn}"
            out.append(Candidate(
                name=name, slot=slot, fn=fn,
                column=PRIMARY_COL.get(fn),
                kwargs=PER_FN_KWARGS.get(fn, {}),
                uses_volume=(fn in volume_fns),
            ))
    out.extend(_derived_candidates())
    return out


def _band_width(df: pd.DataFrame, method: str) -> pd.Series:
    if method == "kc_width":
        b = df.ta.kc()
        w = (b["KCUe_20_2"] - b["KCLe_20_2"]) / b["KCBe_20_2"]
    elif method == "dc_width":
        b = df.ta.donchian()
        w = (b["DCU_20_20"] - b["DCL_20_20"]) / b["DCM_20_20"]
    elif method == "accb_width":
        b = df.ta.accbands()
        w = (b["ACCBU_20"] - b["ACCBL_20"]) / b["ACCBM_20"]
    else:
        raise ValueError(method)
    return w


def compute_candidate(df: pd.DataFrame, cand: Candidate) -> pd.Series:
    """Compute one candidate on a normalized OHLCV frame. Returns float64
    Series aligned to df.index (NaN where undefined). Raises on failure —
    caller decides whether to skip."""
    if cand.derived == "atr_ratio":
        atr = df.ta.natr()  # NATR = 100*ATR/close, already normalized
        x = df.ta.atr() / df["close"]
        out = x
    elif cand.derived in ("kc_width", "dc_width", "accb_width"):
        out = _band_width(df, cand.derived)
    else:
        res = getattr(df.ta, cand.fn)(**cand.kwargs)
        if res is None:
            raise ValueError(f"{cand.fn} returned None")
        if isinstance(res, pd.DataFrame):
            if cand.column is None or cand.column not in res.columns:
                raise ValueError(f"{cand.fn}: primary column {cand.column!r} "
                                 f"not in {list(res.columns)}")
            out = res[cand.column]
        else:
            out = res
    out = pd.to_numeric(out, errors="coerce").astype("float64")
    return out.reindex(df.index)
```

- [ ] **Step 4: Run the tests; iterate on the exclusion table**

Run: `python -m pytest tests/test_registry.py -x -q`

Expected: PASS. **If `test_causality_truncation_invariance` or the NaN-coverage test fails for specific indicators, that is the test doing its job**: add the failing `fn` to `EXCLUDED` with reason `"failed causality truncation test"` or `"mostly NaN on daily data"` and re-run until green. Do NOT weaken the test. Also remove the unused `atr` variable in `compute_candidate` if the linter/your eye catches it (it is vestigial — `out = x` is the ratio; delete the `natr` line).

- [ ] **Step 5: Commit**

```bash
git add pandasta_registry.py tests/
git -c user.name="l" -c user.email="limroddric@gmail.com" commit -m "feat: pandas_ta candidate registry with causality-tested defaults"
```

---

### Task 2: Universe + data layer (crypto included)

**Files:**
- Create: `pandasta_data.py`
- Test: `tests/test_data.py`

**Interfaces:**
- Produces: `UNIVERSE: dict` (ASSETS + BTC-USD/ETH-USD, same schema: `{"name", "class", optional "return_mode"}`), `TRADABLE: list[str]` (UNIVERSE minus ^TNX), `load_asset(tkr) -> pd.DataFrame | None` (normalized OHLCV), `volume_usable(df) -> tuple[bool, pd.Series]` (flag + volume with zero-prefix masked to NaN), `master_calendar(start=None) -> pd.DatetimeIndex` (^GSPC trading days), `return_mode(tkr) -> str` ("log" or "diff").
- Consumes: `price_cache.load`, `grouped_ic_backtest.ASSETS`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_data.py
import numpy as np
import pandas as pd

from pandasta_data import (UNIVERSE, TRADABLE, load_asset, master_calendar,
                           return_mode, volume_usable)


def test_universe_has_crypto_and_classes():
    assert UNIVERSE["BTC-USD"]["class"] == "crypto"
    assert UNIVERSE["ETH-USD"]["class"] == "crypto"
    assert len(UNIVERSE) == 20
    assert "^TNX" not in TRADABLE and "BTC-USD" in TRADABLE
    assert len(TRADABLE) == 19


def test_return_modes():
    assert return_mode("^TNX") == "diff"
    assert return_mode("^GSPC") == "log"


def test_volume_usable_masks_zero_prefix():
    idx = pd.bdate_range("2000-01-03", periods=100)
    v = pd.Series([0.0] * 40 + [1e6] * 60, index=idx)
    df = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0,
                       "close": 1.0, "volume": v}, index=idx)
    ok, masked = volume_usable(df)
    assert ok
    assert masked.iloc[:40].isna().all()
    assert (masked.iloc[40:] > 0).all()


def test_volume_unusable_when_all_zero():
    idx = pd.bdate_range("2000-01-03", periods=100)
    df = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0,
                       "close": 1.0, "volume": 0.0}, index=idx)
    ok, _ = volume_usable(df)
    assert not ok


def test_load_and_calendar():
    spx = load_asset("^GSPC")
    assert spx is not None and len(spx) > 9000
    cal = master_calendar("2024-01-01")
    assert cal[0] >= pd.Timestamp("2024-01-01")
    assert cal.is_monotonic_increasing
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_data.py -x -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'pandasta_data'`

- [ ] **Step 3: Implement**

```python
# pandasta_data.py
"""Universe (incl. crypto) and data access for the pandas_ta set search.
Crypto trades 7d/week; portfolio-level alignment to the equity calendar is
done by the consumer (portfolio_backtest) via reindex+ffill of CLOSE, so
weekend crypto moves fold into the next trading day."""
from __future__ import annotations

import pandas as pd

import price_cache
from grouped_ic_backtest import ASSETS

UNIVERSE: dict = {
    **ASSETS,
    "BTC-USD": {"name": "Bitcoin", "class": "crypto"},
    "ETH-USD": {"name": "Ethereum", "class": "crypto"},
}

# ^TNX is a yield level, not investable (TLT carries duration exposure)
TRADABLE = [t for t in UNIVERSE if t != "^TNX"]

MIN_NONZERO_VOL_FRAC = 0.50


def return_mode(tkr: str) -> str:
    return UNIVERSE[tkr].get("return_mode", "log")


def load_asset(tkr: str) -> pd.DataFrame | None:
    df = price_cache.load(tkr)
    if df is None or len(df) == 0:
        return None
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    return df.sort_index()


def volume_usable(df: pd.DataFrame) -> tuple[bool, pd.Series]:
    """(usable_flag, volume with the leading zero/NaN prefix masked to NaN).
    Usable iff, after the first nonzero print, >=50% of bars have volume>0."""
    v = pd.to_numeric(df["volume"], errors="coerce")
    nz = v > 0
    if not nz.any():
        return False, v.where(nz)
    first = nz.idxmax()
    tail = v.loc[first:]
    frac = float((tail > 0).mean())
    masked = v.copy()
    masked.loc[:first] = pd.NA
    masked.loc[first] = v.loc[first]
    masked = masked.where(masked > 0).astype("float64")
    return frac >= MIN_NONZERO_VOL_FRAC, masked


def master_calendar(start: str | None = None) -> pd.DatetimeIndex:
    spx = load_asset("^GSPC")
    idx = spx.index
    if start is not None:
        idx = idx[idx >= pd.Timestamp(start)]
    return idx
```

- [ ] **Step 4: Prime the crypto cache (network verified working 2026-07-06)**

Run: `python -c "import price_cache; print(price_cache.prime(['BTC-USD','ETH-USD']))"`
Expected: `fetched BTC-USD rows=~4310`, `fetched ETH-USD rows=~3300` (or `cached` on re-run). Then `python -m pytest tests/test_data.py -x -q` → PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add pandasta_data.py tests/test_data.py
git -c user.name="l" -c user.email="limroddric@gmail.com" commit -m "feat: universe with crypto class + volume usability masking"
```

---

### Task 3: Stage 1 — per-asset, per-slot IC screen

**Files:**
- Create: `pandasta_set_search.py` (stage 1 half)
- Test: `tests/test_set_search.py`

**Interfaces:**
- Consumes: `build_candidates`, `compute_candidate` (Task 1); `UNIVERSE`, `load_asset`, `volume_usable`, `return_mode` (Task 2); `stats.forward_returns`, `stats.assert_no_lookahead`, `stats.spearman_ic_hac`, `stats.rolling_spearman`, `stats.ic_ir_hac`, `stats.benjamini_hochberg`.
- Produces: `run_stage1(cutoff: str | None, tickers: list[str] | None = None) -> pd.DataFrame` with columns `asset, asset_class, indicator, slot, horizon, ic, ic_ir, n_obs, p_value, survives_fdr, note` — plus module constants `HORIZONS = [1, 5, 10, 20]`, `ROLL_WINDOW = 63`, `FDR_Q = 0.10`. Also `indicator_series_cache(tkr, cutoff) -> dict[str, pd.Series]` used by stage 2 (computed once per asset, keyed by candidate name).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_set_search.py
import numpy as np
import pandas as pd
import pytest

import stats as st
from pandasta_set_search import HORIZONS, FDR_Q, run_stage1, _screen_one_asset
from tests.test_registry import synth_ohlcv


def test_screen_one_asset_schema_and_fdr_columns():
    df = synth_ohlcv(n=900)
    rows = _screen_one_asset("SYN", "equity", df, mode="log")
    out = pd.DataFrame(rows)
    assert set(out.columns) >= {"asset", "asset_class", "indicator", "slot",
                                "horizon", "ic", "ic_ir", "n_obs", "p_value",
                                "note"}
    assert set(out["horizon"]) == set(HORIZONS)
    # every candidate that produced values appears at every horizon
    per_ind = out.groupby("indicator")["horizon"].nunique()
    assert (per_ind == len(HORIZONS)).all()


def test_planted_signal_is_detected():
    """A predictor built from the (future) 5-day return must show huge IC.
    This validates wiring, not causality (construction is deliberately
    lookahead INSIDE THE TEST ONLY)."""
    df = synth_ohlcv(n=900)
    close = df["close"].to_numpy()
    fwd5 = st.forward_returns(close, 5)
    x = fwd5 + np.random.default_rng(0).normal(0, np.nanstd(fwd5) * 0.3,
                                               len(fwd5))
    ic, t, p, n = st.spearman_ic_hac(x, fwd5, lag=5)
    assert ic > 0.8 and p < 1e-10


def test_cutoff_truncates_history():
    df = synth_ohlcv(n=900)  # bdates from 2015-01-02
    rows_full = _screen_one_asset("SYN", "equity", df, mode="log")
    rows_cut = _screen_one_asset("SYN", "equity",
                                 df.loc[:"2016-12-31"], mode="log")
    n_full = max(r["n_obs"] for r in rows_full)
    n_cut = max(r["n_obs"] for r in rows_cut)
    assert n_cut < n_full
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_set_search.py -x -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'pandasta_set_search'`

- [ ] **Step 3: Implement stage 1**

```python
# pandasta_set_search.py
"""
pandasta_set_search.py
======================
Stage 1: per-asset, per-slot IC screen of pandas_ta candidates (defaults only).
Stage 2: joint set search — composite of one survivor per slot, scored with
the same HAC machinery. Two selection windows: OOS (<=2023-12-31) and IS
(full history). See docs/superpowers/specs/2026-07-06-pandasta-set-search-design.md.

Run:
    python pandasta_set_search.py             # both cutoffs, all assets
    python pandasta_set_search.py --smoke     # ^GSPC only, OOS cutoff
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd

import stats as st
from pandasta_data import UNIVERSE, load_asset, return_mode, volume_usable
from pandasta_registry import SLOTS, build_candidates, compute_candidate

HORIZONS = [1, 5, 10, 20]
ROLL_WINDOW = 63
FDR_Q = 0.10
MIN_COVERAGE = 0.30     # candidate must be non-NaN on >=30% of post-warmup bars
Z_WINDOW, Z_MIN = 252, 126
TOP_K_PER_SLOT = 5
STRATEGY_H = 20

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

OOS_CUTOFF = "2023-12-31"


def _candidate_values(tkr: str, df: pd.DataFrame) -> dict[str, tuple[str, pd.Series]]:
    """name -> (slot, values) for every computable candidate on this asset."""
    vol_ok, vol_masked = volume_usable(df)
    work = df.copy()
    work["volume"] = vol_masked
    out = {}
    for cand in build_candidates():
        if cand.uses_volume and not vol_ok:
            continue
        try:
            x = compute_candidate(work, cand)
        except Exception as e:  # noqa: BLE001 — any indicator failure is a skip
            print(f"    skip {tkr} {cand.name}: {type(e).__name__}: {e}")
            continue
        if x.iloc[Z_MIN:].notna().mean() < MIN_COVERAGE:
            continue
        out[cand.name] = (cand.slot, x)
    return out


def indicator_series_cache(tkr: str, cutoff: str | None) -> tuple[pd.DataFrame, dict]:
    df = load_asset(tkr)
    if df is None:
        raise FileNotFoundError(f"no cached data for {tkr}")
    if cutoff is not None:
        df = df.loc[:cutoff]
    return df, _candidate_values(tkr, df)


def _screen_one_asset(tkr: str, klass: str, df: pd.DataFrame, mode: str,
                      values: dict | None = None) -> list[dict]:
    close = df["close"].to_numpy(dtype="float64")
    if values is None:
        values = _candidate_values(tkr, df)
    fwd = {}
    for h in HORIZONS:
        y = st.forward_returns(close, h, mode)
        st.assert_no_lookahead(y, h)
        fwd[h] = y
    rows = []
    for name, (slot, xs) in values.items():
        x = xs.to_numpy(dtype="float64")
        for h in HORIZONS:
            y = fwd[h]
            ic, t, p, n = st.spearman_ic_hac(x, y, lag=h)
            roll = st.rolling_spearman(x, y, ROLL_WINDOW)
            ic_ir = st.ic_ir_hac(roll, lag=h)
            rows.append({"asset": tkr, "asset_class": klass, "indicator": name,
                         "slot": slot, "horizon": h, "ic": ic, "ic_ir": ic_ir,
                         "n_obs": n, "p_value": p, "note": ""})
    return rows


def run_stage1(cutoff: str | None, tickers: list[str] | None = None) -> pd.DataFrame:
    tickers = tickers or list(UNIVERSE)
    all_rows = []
    for tkr in tickers:
        meta = UNIVERSE[tkr]
        print(f"  stage1 {tkr} (cutoff={cutoff}) ...")
        df, values = indicator_series_cache(tkr, cutoff)
        all_rows.extend(_screen_one_asset(tkr, meta["class"], df,
                                          return_mode(tkr), values))
    out = pd.DataFrame(all_rows)
    pool = out["p_value"].notna()
    out["survives_fdr"] = False
    out.loc[pool, "survives_fdr"] = st.benjamini_hochberg(
        out.loc[pool, "p_value"].to_numpy(), FDR_Q)
    return out
```

(The `argparse` main and stage 2 land in Tasks 4–5; keep the imports now — `itertools`, `argparse`, `sys` are used there.)

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_set_search.py tests/test_registry.py -q`
Expected: PASS (all).

- [ ] **Step 5: Smoke-run stage 1 on ^GSPC**

Run: `python -c "from pandasta_set_search import run_stage1, OOS_CUTOFF; df = run_stage1(OOS_CUTOFF, ['^GSPC']); print(len(df), 'rows'); print(df.sort_values('ic_ir', key=abs, ascending=False).head(8)[['indicator','slot','horizon','ic','ic_ir','survives_fdr']])"`
Expected: ~65-75 indicators × 4 horizons ≈ 260–300 rows, |IC| values in the 0.00–0.10 range (tiny is normal/honest), some `survives_fdr=True`.

- [ ] **Step 6: Commit**

```bash
git add pandasta_set_search.py tests/test_set_search.py
git -c user.name="l" -c user.email="limroddric@gmail.com" commit -m "feat: stage-1 per-asset pandas_ta IC screen (HAC + FDR, prior-run conventions)"
```

---

### Task 4: Stage 2 — joint composite set search

**Files:**
- Modify: `pandasta_set_search.py` (append stage-2 functions + CLI main)
- Test: append to `tests/test_set_search.py`

**Interfaces:**
- Produces: `causal_zscore(x: pd.Series) -> pd.Series`; `composite_signal(members: list[pd.Series], signs: list[float]) -> pd.Series`; `run_stage2(stage1_df, cutoff, tickers=None) -> pd.DataFrame` with columns `asset, asset_class, cutoff, volume_ind, trend_ind, momentum_ind, volatility_ind, n_slots, horizon, comp_ic, comp_p, comp_ic_ir, redundancy, traded_sign, is_winner`; CLI writing `results/pandasta_stage1_ic.csv`, `results/pandasta_best_sets.csv`, `results/pandasta_best_sets.md`.
- Consumes: everything from Task 3 (same module).

- [ ] **Step 1: Write the failing tests (append to tests/test_set_search.py)**

```python
from pandasta_set_search import causal_zscore, composite_signal, run_stage2


def test_causal_zscore_is_causal_and_normalized():
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2010-01-04", periods=800)
    x = pd.Series(rng.normal(0, 1, 800), index=idx)
    z = causal_zscore(x)
    assert z.iloc[:125].isna().all()          # min_periods honored
    # causality: truncating the future never changes the past
    z_cut = causal_zscore(x.iloc[:600])
    pd.testing.assert_series_equal(z.iloc[:600], z_cut)
    assert abs(z.iloc[300:].mean()) < 0.5     # roughly centered


def test_composite_sign_alignment():
    idx = pd.bdate_range("2010-01-04", periods=400)
    a = pd.Series(np.linspace(0, 1, 400), index=idx)
    comp_pos = composite_signal([a, a], [1.0, 1.0])
    comp_mix = composite_signal([a, a], [1.0, -1.0])
    # sign-aligned identical members reinforce; opposite signs cancel
    assert comp_pos.iloc[350:].abs().mean() > comp_mix.iloc[350:].abs().mean()


def test_stage2_picks_winner_per_asset():
    df = synth_ohlcv(n=1200)
    s1 = pd.DataFrame(_screen_one_asset("SYN", "equity", df, mode="log"))
    s1["survives_fdr"] = True  # force survivors so the combo loop runs
    import pandasta_set_search as pss
    import pandas as _pd
    # monkeypatch loading so run_stage2 sees the synthetic asset
    pss_load = pss.indicator_series_cache
    try:
        pss.indicator_series_cache = lambda tkr, cutoff: (df, pss._candidate_values("SYN", df))
        best = pss.run_stage2(s1, cutoff=None, tickers=["SYN"])
    finally:
        pss.indicator_series_cache = pss_load
    winners = best[best["is_winner"]]
    assert len(winners) == 1
    w = winners.iloc[0]
    assert w["horizon"] == 20
    assert w["traded_sign"] in (1.0, -1.0)
    assert 0 <= w["redundancy"] <= 1 or np.isnan(w["redundancy"])
```

Note: `run_stage2` must accept `tickers=["SYN"]` with `UNIVERSE.get(tkr, {"class": "synthetic"})` fallback for the class label — implement accordingly.

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_set_search.py -x -q`
Expected: FAIL with `ImportError: cannot import name 'causal_zscore'`

- [ ] **Step 3: Implement stage 2 + CLI (append to pandasta_set_search.py)**

```python
def causal_zscore(x: pd.Series) -> pd.Series:
    mu = x.rolling(Z_WINDOW, min_periods=Z_MIN).mean()
    sd = x.rolling(Z_WINDOW, min_periods=Z_MIN).std()
    with np.errstate(divide="ignore", invalid="ignore"):
        z = (x - mu) / sd
    return z.replace([np.inf, -np.inf], np.nan)


def composite_signal(members: list[pd.Series], signs: list[float]) -> pd.Series:
    zs = [causal_zscore(m) * s for m, s in zip(members, signs)]
    mat = pd.concat(zs, axis=1)
    return mat.mean(axis=1)          # NaN-tolerant mean across available members


def _top_k_per_slot(s1_asset: pd.DataFrame) -> dict[str, list[str]]:
    """slot -> up to TOP_K_PER_SLOT indicator names among FDR survivors,
    ranked by max |ic_ir| across horizons."""
    surv = s1_asset[s1_asset["survives_fdr"]]
    picks: dict[str, list[str]] = {}
    for slot in SLOTS:
        sl = surv[surv["slot"] == slot]
        if sl.empty:
            continue
        ranked = (sl.assign(a=sl["ic_ir"].abs())
                    .groupby("indicator")["a"].max()
                    .sort_values(ascending=False))
        picks[slot] = list(ranked.index[:TOP_K_PER_SLOT])
    return picks


def _stage1_sign(s1_asset: pd.DataFrame, indicator: str) -> float:
    """Sign of stage-1 IC at h=STRATEGY_H (fallback: horizon with max |ic|)."""
    rows = s1_asset[s1_asset["indicator"] == indicator]
    at_h = rows[rows["horizon"] == STRATEGY_H]
    r = at_h.iloc[0] if len(at_h) else rows.loc[rows["ic"].abs().idxmax()]
    return 1.0 if (r["ic"] >= 0 or np.isnan(r["ic"])) else -1.0


def run_stage2(stage1_df: pd.DataFrame, cutoff: str | None,
               tickers: list[str] | None = None) -> pd.DataFrame:
    tickers = tickers or sorted(stage1_df["asset"].unique())
    rows = []
    for tkr in tickers:
        s1 = stage1_df[stage1_df["asset"] == tkr]
        klass = UNIVERSE.get(tkr, {"class": "synthetic"})["class"]
        picks = _top_k_per_slot(s1)
        if not picks:
            print(f"  stage2 {tkr}: no FDR survivors in any slot — skipped")
            continue
        df, values = indicator_series_cache(tkr, cutoff)
        close = df["close"].to_numpy(dtype="float64")
        mode = return_mode(tkr) if tkr in UNIVERSE else "log"
        fwd = {h: st.forward_returns(close, h, mode) for h in HORIZONS}
        slots_used = [s for s in SLOTS if s in picks]
        print(f"  stage2 {tkr}: slots={slots_used} "
              f"combos={np.prod([len(picks[s]) for s in slots_used])}")
        best_key, best_val = None, -np.inf
        for combo in itertools.product(*(picks[s] for s in slots_used)):
            members = [values[name][1] for name in combo]
            signs = [_stage1_sign(s1, name) for name in combo]
            comp = composite_signal(members, signs).to_numpy(dtype="float64")
            zmat = pd.concat([causal_zscore(m) for m in members], axis=1)
            red = zmat.corr(method="spearman").abs()
            k = len(combo)
            redundancy = (float((red.sum().sum() - k) / (k * (k - 1)))
                          if k > 1 else np.nan)
            by_slot = dict(zip(slots_used, combo))
            for h in HORIZONS:
                ic, t, p, n = st.spearman_ic_hac(comp, fwd[h], lag=h)
                roll = st.rolling_spearman(comp, fwd[h], ROLL_WINDOW)
                ic_ir = st.ic_ir_hac(roll, lag=h)
                rows.append({
                    "asset": tkr, "asset_class": klass,
                    "cutoff": cutoff or "FULL",
                    "volume_ind": by_slot.get("volume", ""),
                    "trend_ind": by_slot.get("trend", ""),
                    "momentum_ind": by_slot.get("momentum", ""),
                    "volatility_ind": by_slot.get("volatility", ""),
                    "n_slots": k, "horizon": h,
                    "comp_ic": ic, "comp_p": p, "comp_ic_ir": ic_ir,
                    "redundancy": redundancy,
                    "traded_sign": 1.0 if (np.isnan(ic) or ic >= 0) else -1.0,
                    "is_winner": False,
                })
                if h == STRATEGY_H and np.isfinite(ic_ir) and abs(ic_ir) > best_val:
                    best_val, best_key = abs(ic_ir), len(rows) - 1
        if best_key is not None:
            rows[best_key]["is_winner"] = True
    return pd.DataFrame(rows)


def _write_best_sets_md(best: pd.DataFrame, path: str) -> None:
    lines = ["# pandas_ta best indicator sets (per asset)", "",
             "> Flat-history selection, defaults-only, FDR q=0.10. "
             "OOS = selection on data <= 2023-12-31; FULL = in-sample upper "
             "bound (NOT a forecast). ICs are small in absolute terms; "
             "composite signals are screened, not regime-conditioned.", ""]
    for cutoff, grp in best.groupby("cutoff"):
        lines.append(f"## Selection window: {cutoff}")
        lines.append("")
        lines.append("| asset | class | volume | trend | momentum | volatility "
                     "| h | comp_IC | comp_IC_IR | redundancy | sign |")
        lines.append("|---|---|---|---|---|---|---:|---:|---:|---:|---:|")
        for _, r in grp[grp["is_winner"]].sort_values("asset").iterrows():
            lines.append(
                f"| {r['asset']} | {r['asset_class']} | {r['volume_ind'] or '-'} "
                f"| {r['trend_ind'] or '-'} | {r['momentum_ind'] or '-'} "
                f"| {r['volatility_ind'] or '-'} | {r['horizon']} "
                f"| {r['comp_ic']:+.4f} | {r['comp_ic_ir']:+.3f} "
                f"| {r['redundancy']:.2f} | {r['traded_sign']:+.0f} |")
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="^GSPC, OOS only")
    args = ap.parse_args()
    os.makedirs(RESULTS, exist_ok=True)
    tickers = ["^GSPC"] if args.smoke else None
    s1_frames, s2_frames = [], []
    for cutoff in ([OOS_CUTOFF] if args.smoke else [OOS_CUTOFF, None]):
        label = cutoff or "FULL"
        print(f"=== stage 1 (cutoff={label}) ===")
        s1 = run_stage1(cutoff, tickers)
        s1["cutoff"] = label
        s1_frames.append(s1)
        print(f"=== stage 2 (cutoff={label}) ===")
        s2_frames.append(run_stage2(s1, cutoff, tickers))
    pd.concat(s1_frames).to_csv(os.path.join(RESULTS, "pandasta_stage1_ic.csv"),
                                index=False)
    best = pd.concat(s2_frames)
    best.to_csv(os.path.join(RESULTS, "pandasta_best_sets.csv"), index=False)
    _write_best_sets_md(best, os.path.join(RESULTS, "pandasta_best_sets.md"))
    n_win = int(best["is_winner"].sum())
    print(f"done: {n_win} winning sets written to results/")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/ -q`
Expected: PASS (all tests, all files).

- [ ] **Step 5: Smoke run end-to-end**

Run: `python pandasta_set_search.py --smoke`
Expected: stage-1 rows, stage-2 combo counts printed, `results/pandasta_stage1_ic.csv`, `results/pandasta_best_sets.csv`, `results/pandasta_best_sets.md` exist; ^GSPC has exactly one `is_winner=True` row at `horizon=20`.

- [ ] **Step 6: Commit**

```bash
git add pandasta_set_search.py tests/test_set_search.py
git -c user.name="l" -c user.email="limroddric@gmail.com" commit -m "feat: stage-2 joint composite set search with redundancy diagnostic + CLI"
```

---

### Task 5: Full two-window run + spot-check

**Files:**
- Modify: none (run only)
- Output: `results/pandasta_stage1_ic.csv`, `results/pandasta_best_sets.csv`, `results/pandasta_best_sets.md`

**Interfaces:**
- Consumes: Task 4 CLI.
- Produces: the frozen best-sets artifacts Task 7 reads. Task 6/7 rely on `results/pandasta_best_sets.csv` columns exactly as defined in Task 4.

- [ ] **Step 1: Full run (both cutoffs, all 20 assets)**

Run: `python pandasta_set_search.py` (expect several minutes; ~70 candidates × 20 assets × 4 horizons × 2 windows of full-history rolling ICs)
Expected: completes without traceback; per-asset skip lines are fine (logged reasons). 20 winners per window is the ideal; fewer is acceptable when an asset has no FDR survivor in any slot — those assets are reported and (in Task 7) fall back to exclusion from the tradable ranking with a disclosure.

- [ ] **Step 2: Spot-check one winner outside the pipeline**

Pick the ^GSPC winner's momentum member from `results/pandasta_best_sets.md` (say it is `MO-rsi`). Recompute directly:

```python
# spot check (run as: python - <<'EOF' ... EOF or a scratch file)
import importlib.metadata, numpy as np, pandas as pd, pandas_ta as ta
import stats as st
from pandasta_data import load_asset
df = load_asset("^GSPC").loc[:"2023-12-31"]
x = df.ta.rsi().to_numpy()          # adjust accessor to the actual winner
y = st.forward_returns(df["close"].to_numpy(), 20)
print(st.spearman_ic_hac(x, y, lag=20))
```

Expected: IC matches the corresponding `pandasta_stage1_ic.csv` row for (asset=^GSPC, indicator=MO-rsi, horizon=20, cutoff=2023-12-31) to ~1e-12.

- [ ] **Step 3: Commit results**

```bash
git add results/pandasta_stage1_ic.csv results/pandasta_best_sets.csv results/pandasta_best_sets.md
git -c user.name="l" -c user.email="limroddric@gmail.com" commit -m "results: pandas_ta stage-1 screen + best sets, OOS and FULL windows"
```

---

### Task 6: Portfolio engine — signals → ranks → weights → accounting

**Files:**
- Create: `portfolio_backtest.py`
- Test: `tests/test_portfolio.py`

**Interfaces:**
- Consumes: `results/pandasta_best_sets.csv` (winner rows), `indicator_series_cache` + `composite_signal` + `causal_zscore` from `pandasta_set_search`, `TRADABLE`, `UNIVERSE`, `load_asset`, `master_calendar` from `pandasta_data`.
- Produces:
  - `rank_tilt(n_held: int) -> np.ndarray` — tilt vector for rank positions 0(best)..n-1, `1 + 0.5 * scaled_rank`, scaled_rank ∈ [+1, −1] best→worst; single-asset edge case tilt = 1.
  - `target_weights(signals: pd.Series, vols: pd.Series, top_n=8) -> pd.Series` — long-only, sums to 1.
  - `run_backtest(daily_rets: pd.DataFrame, signals: pd.DataFrame, start="2024-01-01", cost_per_side=0.0005) -> dict` with keys `equity (pd.Series)`, `weights (pd.DataFrame, rebalance rows)`, `turnover (pd.Series)`, `daily (pd.Series)`.
  - `metrics_table(daily: pd.Series, equity: pd.Series) -> pd.DataFrame` — rows 2024, 2025, 2026 (YTD), FULL; columns `return, ann_vol, sharpe, max_dd`.
  - CLI writing `results/portfolio_backtest_2024_2026.md`, `results/portfolio_equity_curves.csv`, `results/portfolio_weights.csv`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_portfolio.py
import numpy as np
import pandas as pd
import pytest

from portfolio_backtest import (metrics_table, rank_tilt, run_backtest,
                                target_weights)


def test_rank_tilt_bounds_and_order():
    t = rank_tilt(8)
    assert t[0] == pytest.approx(1.5) and t[-1] == pytest.approx(0.5)
    assert np.all(np.diff(t) < 0)
    assert rank_tilt(1)[0] == pytest.approx(1.0)


def test_target_weights_long_only_sum1_topn():
    idx = [f"A{i}" for i in range(12)]
    sig = pd.Series(np.linspace(1, -1, 12), index=idx)
    vol = pd.Series(0.2, index=idx)
    w = target_weights(sig, vol, top_n=8)
    assert w.sum() == pytest.approx(1.0)
    assert (w >= 0).all()
    assert (w > 0).sum() == 8
    assert set(w[w > 0].index) == set(idx[:8])   # top-8 by signal
    # equal vol -> ordering by tilt: best signal gets biggest weight
    ww = w[w > 0].reindex(idx[:8])
    assert ww.is_monotonic_decreasing


def test_inverse_vol_dominates_when_signals_tie():
    idx = ["LOWVOL", "HIGHVOL"]
    sig = pd.Series([0.5, 0.5], index=idx)
    vol = pd.Series([0.10, 0.40], index=idx)
    w = target_weights(sig, vol, top_n=2)
    assert w["LOWVOL"] > w["HIGHVOL"]
    # tilt cap: 4x vol gap cannot be overturned by any tilt (max ratio 3x)
    assert w["LOWVOL"] / w["HIGHVOL"] > 1.3


def test_backtest_accounting_two_asset_toy():
    days = pd.bdate_range("2024-01-01", periods=64)
    # asset A returns +1% daily, B returns 0% — deterministic
    rets = pd.DataFrame({"A": 0.01, "B": 0.0}, index=days)
    # signal always prefers A
    sig = pd.DataFrame({"A": 1.0, "B": -1.0}, index=days)
    res = run_backtest(rets, sig, start="2024-02-01", cost_per_side=0.0)
    daily = res["daily"]
    # after the first rebalance takes effect, portfolio must track A's 1%
    # exactly once weight drifts toward 100% A? A is top-1 of top_n=8 => both
    # held; but with equal vol (constant rets -> zero vol) fallback must not
    # produce NaN weights
    assert not daily.isna().any()
    assert (res["equity"].iloc[-1] > 1.0)
    w = res["weights"]
    assert np.allclose(w.sum(axis=1), 1.0)
    assert (w.values >= -1e-12).all()


def test_costs_reduce_returns():
    days = pd.bdate_range("2024-01-01", periods=64)
    rng = np.random.default_rng(5)
    rets = pd.DataFrame(rng.normal(0.0005, 0.01, (64, 3)),
                        index=days, columns=["A", "B", "C"])
    sig = pd.DataFrame(rng.normal(0, 1, (64, 3)),
                       index=days, columns=["A", "B", "C"])
    free = run_backtest(rets, sig, start="2024-02-01", cost_per_side=0.0)
    paid = run_backtest(rets, sig, start="2024-02-01", cost_per_side=0.001)
    assert paid["equity"].iloc[-1] < free["equity"].iloc[-1]


def test_metrics_table_known_series():
    days = pd.bdate_range("2024-01-01", periods=252)
    daily = pd.Series(0.001, index=days)          # +0.1%/day, zero vol
    equity = (1 + daily).cumprod()
    m = metrics_table(daily, equity)
    r2024 = m.loc["2024", "return"]
    assert r2024 == pytest.approx((1.001 ** 252) - 1, rel=1e-9)
    assert m.loc["2024", "max_dd"] == pytest.approx(0.0)
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_portfolio.py -x -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'portfolio_backtest'`

- [ ] **Step 3: Implement**

```python
# portfolio_backtest.py
"""
portfolio_backtest.py
=====================
Long-only, 100%-invested, monthly-rebalanced portfolio built from the per-asset
composite technical signals selected by pandasta_set_search.

Ranking -> weights (first trading day each month, decision on prior day data):
  hold top N=8 by composite signal; weight ∝ (1/vol_63d) * tilt,
  tilt = 1 + 0.5 * scaled_rank in [0.5, 1.5]; normalized; 5 bps per side.

Variants: OOS (sets chosen on data <= 2023-12-31) vs FULL (in-sample upper
bound), reported side by side. Benchmark: equal-weight buy & hold.

Run:  python portfolio_backtest.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from pandasta_data import TRADABLE, UNIVERSE, load_asset, master_calendar
from pandasta_set_search import (HORIZONS, STRATEGY_H, composite_signal,
                                 indicator_series_cache)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

TOP_N = 8
VOL_WINDOW = 63
COST_PER_SIDE = 0.0005
BACKTEST_START = "2024-01-01"
ANN = 252


# ---------------------------------------------------------------- weights ----
def rank_tilt(n_held: int) -> np.ndarray:
    """Tilt for rank positions 0 (best) .. n-1 (worst): 1 + 0.5*scaled,
    scaled linearly from +1 (best) to -1 (worst). n=1 -> tilt 1."""
    if n_held == 1:
        return np.array([1.0])
    scaled = np.linspace(1.0, -1.0, n_held)
    return 1.0 + 0.5 * scaled


def target_weights(signals: pd.Series, vols: pd.Series, top_n: int = TOP_N) -> pd.Series:
    """Long-only weights over `signals.index`; top_n held, rest zero."""
    s = signals.dropna()
    held = s.sort_values(ascending=False).index[:min(top_n, len(s))]
    v = vols.reindex(held).astype("float64")
    v = v.where(v > 1e-8)                 # zero/NaN vol -> fallback below
    inv = 1.0 / v
    inv = inv.fillna(inv.mean() if np.isfinite(inv.mean()) else 1.0)
    tilt = pd.Series(rank_tilt(len(held)), index=held)
    raw = inv * tilt
    w = raw / raw.sum()
    return w.reindex(signals.index).fillna(0.0)


# --------------------------------------------------------------- backtest ----
def run_backtest(daily_rets: pd.DataFrame, signals: pd.DataFrame,
                 start: str = BACKTEST_START,
                 cost_per_side: float = COST_PER_SIDE) -> dict:
    """Daily accounting with weight drift; rebalance on the first trading day
    of each month using data through the PRIOR day; costs on turnover."""
    cal = daily_rets.index
    vols = daily_rets.rolling(VOL_WINDOW).std() * np.sqrt(ANN)
    live = cal[cal >= pd.Timestamp(start)]
    months = pd.Series(live.month, index=live)
    is_first = months.ne(months.shift(1).fillna(-1))
    rebal_days = set(live[is_first.values])

    w = pd.Series(0.0, index=daily_rets.columns)
    daily_out, weights_rows, turnover_rows = [], [], []
    for d in live:
        if d in rebal_days:
            prior = cal[cal < d]
            if len(prior):
                p = prior[-1]
                tgt = target_weights(signals.loc[p], vols.loc[p])
                dw = (tgt - w).abs().sum()
                cost = cost_per_side * dw
                w = tgt
                weights_rows.append(pd.Series(w, name=d))
                turnover_rows.append(pd.Series({"turnover": dw / 2.0}, name=d))
            else:
                cost = 0.0
        else:
            cost = 0.0
        r = daily_rets.loc[d].fillna(0.0)
        rp = float((w * r).sum()) - cost
        daily_out.append(rp)
        growth = w * (1.0 + r)
        tot = growth.sum()
        w = growth / tot if tot > 0 else w
    daily = pd.Series(daily_out, index=live, name="daily_return")
    equity = (1.0 + daily).cumprod()
    return {"daily": daily, "equity": equity,
            "weights": pd.DataFrame(weights_rows),
            "turnover": pd.concat(turnover_rows, axis=1).T["turnover"]
            if turnover_rows else pd.Series(dtype=float)}


# ---------------------------------------------------------------- metrics ----
def _max_dd(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((equity / peak - 1.0).min())


def metrics_table(daily: pd.Series, equity: pd.Series) -> pd.DataFrame:
    rows = {}
    for label, sl in [("2024", "2024"), ("2025", "2025"), ("2026", "2026")]:
        d = daily.loc[sl]
        if d.empty:
            continue
        e = (1 + d).cumprod()
        rows[label] = {
            "return": float(e.iloc[-1] - 1.0),
            "ann_vol": float(d.std() * np.sqrt(ANN)),
            "sharpe": float((d.mean() * ANN) / (d.std() * np.sqrt(ANN)))
            if d.std() > 0 else np.nan,
            "max_dd": _max_dd(e),
        }
    d = daily
    rows["FULL"] = {
        "return": float(equity.iloc[-1] - 1.0),
        "ann_vol": float(d.std() * np.sqrt(ANN)),
        "sharpe": float((d.mean() * ANN) / (d.std() * np.sqrt(ANN)))
        if d.std() > 0 else np.nan,
        "max_dd": _max_dd(equity),
    }
    return pd.DataFrame(rows).T


# ------------------------------------------------------------------- main ----
def build_signals(cutoff_label: str) -> pd.DataFrame:
    """Composite signal per tradable asset from the winning sets CSV, on the
    master calendar (crypto ffilled). Assets with no winner are omitted
    (disclosed by caller)."""
    best = pd.read_csv(os.path.join(RESULTS, "pandasta_best_sets.csv"))
    winners = best[(best["is_winner"]) & (best["cutoff"] == cutoff_label)]
    cutoff = None if cutoff_label == "FULL" else cutoff_label
    cal = master_calendar()
    sig = {}
    for _, r in winners.iterrows():
        tkr = r["asset"]
        if tkr not in TRADABLE:
            continue
        # recompute members on FULL history (selection already frozen)
        df, values = indicator_series_cache(tkr, None)
        names = [r[c] for c in ("volume_ind", "trend_ind", "momentum_ind",
                                "volatility_ind")
                 if isinstance(r[c], str) and r[c]]
        stage1 = pd.read_csv(os.path.join(RESULTS, "pandasta_stage1_ic.csv"))
        s1 = stage1[(stage1["asset"] == tkr) & (stage1["cutoff"] == cutoff_label)]
        from pandasta_set_search import _stage1_sign
        members, signs = [], []
        for n in names:
            if n not in values:
                continue
            members.append(values[n][1])
            signs.append(_stage1_sign(s1, n))
        if not members:
            continue
        comp = composite_signal(members, signs) * r["traded_sign"]
        sig[tkr] = comp.reindex(cal).ffill(limit=5)
    return pd.DataFrame(sig, index=cal)


def load_tradable_returns() -> pd.DataFrame:
    cal = master_calendar()
    rets = {}
    for tkr in TRADABLE:
        df = load_asset(tkr)
        if df is None:
            continue
        close = df["close"].reindex(cal.union(df.index)).ffill().reindex(cal)
        rets[tkr] = close.pct_change()
    return pd.DataFrame(rets, index=cal)


def main() -> None:
    os.makedirs(RESULTS, exist_ok=True)
    rets = load_tradable_returns()
    lines = ["# Portfolio backtest 2024-2026 — pandas_ta composite sets", "",
             "> Long-only, 100% invested, top-8 signal-tilted inverse-vol, "
             "monthly rebalance, 5 bps/side, rf=0. 2026 is partial (YTD). "
             "Index/FX assets traded as proxies. FULL variant is IN-SAMPLE "
             "(upper bound), OOS variant selected sets on data <= 2023-12-31.",
             ""]
    curves = {}
    for label in ["2023-12-31", "FULL"]:
        tag = "OOS" if label != "FULL" else "IS"
        sig = build_signals(label)
        missing = sorted(set(TRADABLE) - set(sig.columns))
        res = run_backtest(rets[sig.columns], sig)
        m = metrics_table(res["daily"], res["equity"])
        ann_to = res["turnover"].groupby(res["turnover"].index.year).sum()
        curves[tag] = res["equity"]
        lines += [f"## {tag} (selection window: {label})", "",
                  f"Assets with signals: {len(sig.columns)}/{len(TRADABLE)}"
                  + (f" (no FDR-surviving set: {', '.join(missing)})" if missing else ""),
                  "", m.round(4).to_markdown(), "",
                  "Annual turnover (sum of rebalance one-way): "
                  + ", ".join(f"{y}: {v:.2f}x" for y, v in ann_to.items()), ""]
        res["weights"].to_csv(os.path.join(RESULTS, f"portfolio_weights_{tag}.csv"))
        print(f"\n=== {tag} ===\n{m.round(4)}")
    # benchmark: equal-weight buy & hold from backtest start
    live = rets.index[rets.index >= pd.Timestamp(BACKTEST_START)]
    valid_cols = [c for c in rets.columns
                  if rets[c].loc[live].notna().any()]
    bh_w = pd.Series(1.0 / len(valid_cols), index=valid_cols)
    bh_daily = []
    w = bh_w.copy()
    for d in live:
        r = rets.loc[d, valid_cols].fillna(0.0)
        rp = float((w * r).sum())
        bh_daily.append(rp)
        g = w * (1 + r)
        w = g / g.sum()
    bh = pd.Series(bh_daily, index=live)
    bh_eq = (1 + bh).cumprod()
    mb = metrics_table(bh, bh_eq)
    curves["EW_BH"] = bh_eq
    lines += ["## Benchmark: equal-weight buy & hold", "",
              mb.round(4).to_markdown(), ""]
    print(f"\n=== EW buy&hold ===\n{mb.round(4)}")
    pd.DataFrame(curves).to_csv(os.path.join(RESULTS, "portfolio_equity_curves.csv"))
    with open(os.path.join(RESULTS, "portfolio_backtest_2024_2026.md"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\nreport: results/portfolio_backtest_2024_2026.md")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_portfolio.py -q` then `python -m pytest tests/ -q`
Expected: PASS. Note for the toy test: with 2 assets and constant returns the 63-day vol is 0 → the `v.where(v > 1e-8)` + mean-fallback path must yield finite weights; if the fallback mean is NaN (all vols zero) it falls back to 1.0 → equal inverse-vol. Verify no NaN leaks.

- [ ] **Step 5: Commit**

```bash
git add portfolio_backtest.py tests/test_portfolio.py
git -c user.name="l" -c user.email="limroddric@gmail.com" commit -m "feat: long-only monthly portfolio engine with rank-tilted inverse-vol weights"
```

---

### Task 7: Full backtest runs, report, headline numbers

**Files:**
- Modify: none (run + verify)
- Output: `results/portfolio_backtest_2024_2026.md`, `results/portfolio_equity_curves.csv`, `results/portfolio_weights_OOS.csv`, `results/portfolio_weights_IS.csv`

**Interfaces:**
- Consumes: Task 5 artifacts + Task 6 CLI.

- [ ] **Step 1: Run the backtest**

Run: `python portfolio_backtest.py`
Expected: OOS table, IS table, EW benchmark table printed; report + curves + weights CSVs written. Sanity gates (all must hold — investigate any failure, do not hand-wave):
- every weights row sums to 1 ± 1e-9, all weights ≥ 0;
- equity curves contain no NaN;
- IS metrics ≥ OOS metrics is *expected but not guaranteed* — either way, report the gap;
- 2026 row covers only through the last cached date (~2026-07).

- [ ] **Step 2: Verify with the superpowers:verification-before-completion skill**

Re-run `python -m pytest tests/ -q` (all green) and re-run `python portfolio_backtest.py` reproducing identical numbers (determinism check — no RNG in the pipeline).

- [ ] **Step 3: Commit results**

```bash
git add results/portfolio_backtest_2024_2026.md results/portfolio_equity_curves.csv results/portfolio_weights_OOS.csv results/portfolio_weights_IS.csv
git -c user.name="l" -c user.email="limroddric@gmail.com" commit -m "results: 2024-2026 long-only backtest, OOS vs IS, with EW benchmark"
```

- [ ] **Step 4: Report to user**

Post in chat: per-asset winning sets table (from `pandasta_best_sets.md`), the OOS vs IS vs benchmark metrics tables (annual return, Sharpe, vol, maxDD per 2024/2025/2026-YTD), annual turnover, and the honest caveats (IS = upper bound; OOS is the number that matters; tiny ICs; proxies; partial 2026).

---

## Self-review (done at plan time)

- **Spec coverage:** universe+crypto (T2), stage 1 conventions (T3), stage 2 composite/redundancy/h=20/sign (T4), OOS+IS windows (T4 CLI, T5), signals→top-8 tilted inverse-vol→monthly→5bps (T6), metrics 2024/25/26+benchmark+turnover (T6/T7), disclosures (T4 MD + T6 report), lookahead guards (T1 truncation test, `assert_no_lookahead` in T3, causal z tested in T4). ^TNX screened but not tradable (T2 TRADABLE). Gap check: spec's "top 3 sets per asset in MD" simplified to winner-only in MD (full ranking lives in `pandasta_best_sets.csv`) — acceptable; CSV carries everything.
- **Placeholder scan:** none found; all steps carry code/commands.
- **Type consistency:** `indicator_series_cache` returns `(df, dict[name -> (slot, Series)])` — used consistently in T3, T4, T6. `run_stage2` winner selection at `STRATEGY_H=20` matches T6 `build_signals` reading `is_winner` rows. `cutoff` label convention: `"2023-12-31"` / `"FULL"` in both CSVs and `build_signals`.
