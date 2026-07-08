import numpy as np
import pandas as pd
import pytest

import portfolio_backtest as pb
from portfolio_backtest import build_walkforward_signals, governing_cutoff

CUTOFFS = ["2023-12-31", "2024-12-31", "2025-12-31"]


def test_governing_cutoff_yearly_assignment():
    # a decision anywhere in calendar 2024 must be governed by the 2023-12-31
    # set (2024's own year-end set is not selectable until end of 2024).
    assert governing_cutoff("2024-01-31", CUTOFFS) == "2023-12-31"
    assert governing_cutoff("2024-06-28", CUTOFFS) == "2023-12-31"
    assert governing_cutoff("2024-11-29", CUTOFFS) == "2023-12-31"
    # 2025 -> 2024-12-31 set; 2026 -> 2025-12-31 set
    assert governing_cutoff("2025-07-31", CUTOFFS) == "2024-12-31"
    assert governing_cutoff("2026-02-27", CUTOFFS) == "2025-12-31"


def test_governing_cutoff_year_end_boundary():
    # the trailing December decision that feeds January inherits that year-end
    # set even though the decision date is a couple of days BEFORE the cutoff.
    assert governing_cutoff("2023-12-29", CUTOFFS) == "2023-12-31"
    assert governing_cutoff("2024-12-31", CUTOFFS) == "2024-12-31"
    # nothing selectable before the first cutoff
    assert governing_cutoff("2023-06-30", CUTOFFS) is None


def test_no_lookahead_never_uses_a_future_set():
    # every date is governed by a cutoff strictly before the rebalance it feeds
    # (date + lead), so a set is never applied on/before its own data cutoff.
    for d in pd.bdate_range("2024-01-01", "2026-06-30", freq="B"):
        c = governing_cutoff(d, CUTOFFS)
        if c is not None:
            assert pd.Timestamp(c) < d + pb.SELECTION_LEAD


def test_walkforward_splice_uses_governing_epoch(monkeypatch):
    """build_walkforward_signals must draw each date's row from the governing
    epoch's frame and no other. Monkeypatch build_signals to a sentinel frame
    per cutoff (all values = the cutoff's year) so the source epoch is provable
    from the value itself — then assert the value at every date equals the year
    of governing_cutoff(date) (the exact splice property)."""
    cal = pd.bdate_range("2023-06-01", "2026-06-30")

    def fake_build_signals(cutoff):
        year = float(pd.Timestamp(cutoff).year)
        return pd.DataFrame({"X": year, "Y": year}, index=cal)

    monkeypatch.setattr(pb, "build_signals", fake_build_signals)
    wf = build_walkforward_signals(CUTOFFS)

    expected = pd.Series(
        [float(pd.Timestamp(governing_cutoff(d, CUTOFFS)).year)
         if governing_cutoff(d, CUTOFFS) else np.nan for d in cal],
        index=cal, name="X")
    pd.testing.assert_series_equal(wf["X"], expected, check_names=False)
    # a future epoch is never spliced into an earlier date
    assert np.nanmax(wf["X"].to_numpy()) <= 2025.0


def test_walkforward_continuity_at_2024_decision_days(monkeypatch):
    """Backtest-level continuity guarantee: every rebalance DECISION that feeds a
    2024 monthly rebalance (the last trading day of Dec-2023 .. Nov-2024) is
    governed by the frozen 2023-12-31 epoch, and its spliced signal equals the
    frozen 2023-12-31 frame there — so the walk-forward 2024 backtest slice
    reproduces the current frozen OOS 2024 exactly. (Non-decision tail days of
    Dec-2024 legitimately belong to the 2024-12-31 epoch, since they feed the
    Jan-2025 rebalance.)"""
    cal = pd.bdate_range("2023-06-01", "2026-06-30")
    rng = np.random.default_rng(0)
    frozen = {c: pd.DataFrame(rng.normal(0, 1, (len(cal), 2)),
                              index=cal, columns=["X", "Y"]) for c in CUTOFFS}
    monkeypatch.setattr(pb, "build_signals", lambda c: frozen[c])
    wf = build_walkforward_signals(CUTOFFS)

    # last business day of each month feeding a 2024 rebalance: Dec-2023..Nov-2024
    decision_days = (pd.date_range("2023-12-01", "2024-11-30", freq="BME")
                     .intersection(cal))
    assert len(decision_days) == 12
    for d in decision_days:
        assert governing_cutoff(d, CUTOFFS) == "2023-12-31"
    pd.testing.assert_frame_equal(wf.loc[decision_days],
                                  frozen["2023-12-31"].loc[decision_days])
