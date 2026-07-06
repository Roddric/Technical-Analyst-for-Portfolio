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
