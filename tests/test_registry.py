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


def test_accessor_hijack_recovery():
    """compute_candidate must produce identical values even if
    pandas_ta_classic re-registered the 'ta' accessor after import."""
    df = synth_ohlcv()
    cands = {c.name: c for c in build_candidates()}
    cand = cands["MO-stc"]
    baseline = compute_candidate(df, cand)

    import pandas_ta_classic  # noqa: F401 -- hijacks the accessor on import
    import warnings as _w
    with _w.catch_warnings():
        _w.simplefilter("ignore", UserWarning)
        pd.api.extensions.register_dataframe_accessor("ta")(
            pandas_ta_classic.core.AnalysisIndicators)

    hijacked = compute_candidate(df, cand)
    pd.testing.assert_series_equal(baseline, hijacked)
