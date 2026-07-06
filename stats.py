"""
stats.py
========
IC / expectancy engine. Pure numpy/scipy; knows nothing about assets or sources.

Provides:
  forward_returns(close, h, mode)        -> aligned forward return/change series
  spearman_ic_hac(x, y, lag)             -> IC, t, p, n  (Newey-West HAC p-value)
  rolling_spearman(x, y, window)         -> per-bar rolling Spearman IC series
  ic_ir_hac(roll_ic, lag)                -> mean / NW-HAC-std  (overlap-aware)
  discrete_expectancy(state, y, min_n)   -> per-state stats + bull/bear spread
  benjamini_hochberg(pvals, q)           -> boolean survive mask

Why HAC everywhere: forward returns at horizon h overlap across h consecutive
bars, so they are strongly autocorrelated. A naive standard error understates
the true error and inflates both t-stats and IC_IR. Newey-West (Bartlett kernel,
lag = h) corrects for this.
"""

from __future__ import annotations

import numpy as np
from scipy import stats as sps


# --------------------------------------------------------------------------- #
# Forward returns
# --------------------------------------------------------------------------- #
def forward_returns(close: np.ndarray, h: int, mode: str = "log") -> np.ndarray:
    """
    fwd[t] aligned to indicator[t]; realized over (t, t+h].

    mode="log":  log(close[t+h] / close[t])          (price series)
    mode="diff": close[t+h] - close[t]               (yield/level series, e.g. ^TNX)

    The last h entries are NaN (no future data). No value at or before t enters
    fwd[t] beyond close[t] itself, and close[t] is known at t -> no lookahead of
    the *return direction* into the predictor.
    """
    close = np.asarray(close, dtype="float64")
    n = close.shape[0]
    fwd = np.full(n, np.nan)
    if h <= 0 or h >= n:
        return fwd
    future = close[h:]
    base = close[:-h]
    if mode == "diff":
        fwd[:-h] = future - base
    else:
        with np.errstate(divide="ignore", invalid="ignore"):
            fwd[:-h] = np.log(future / base)
    return fwd


def assert_no_lookahead(fwd: np.ndarray, h: int) -> None:
    """The forward-return construction must leave exactly the last h bars NaN
    at the tail (they have no future). This is a structural lookahead guard."""
    tail = fwd[-h:]
    assert np.all(np.isnan(tail)), (
        f"lookahead guard: expected last {h} forward returns to be NaN")


# --------------------------------------------------------------------------- #
# Continuous: Spearman IC with Newey-West HAC p-value
# --------------------------------------------------------------------------- #
def _bartlett_lrv(u: np.ndarray, lag: int) -> float:
    """Newey-West long-run variance of the series u (Bartlett kernel)."""
    n = u.shape[0]
    g0 = float(u @ u)
    s = g0
    L = max(int(lag), 0)
    for l in range(1, L + 1):
        if l >= n:
            break
        w = 1.0 - l / (L + 1.0)
        g = float(u[l:] @ u[:-l])
        s += 2.0 * w * g
    return s


def spearman_ic_hac(x: np.ndarray, y: np.ndarray, lag: int):
    """
    Full-history Spearman IC between predictor x and forward return y, with a
    two-sided p-value from a Newey-West HAC t-stat (lag = horizon).

    Implemented as OLS of standardized average-ranks: with both sides ranked and
    standardized, the slope beta == Pearson-of-ranks == Spearman IC, and its HAC
    standard error gives an overlap-robust p-value.

    Returns (ic, t_stat, p_value, n_obs). NaNs are dropped pairwise first.
    """
    x = np.asarray(x, dtype="float64")
    y = np.asarray(y, dtype="float64")
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = x.shape[0]
    if n < 10:
        return (np.nan, np.nan, np.nan, n)

    rx = sps.rankdata(x)           # average ranks (tie-correct)
    ry = sps.rankdata(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    sx = rx.std(ddof=0)
    sy = ry.std(ddof=0)
    if sx == 0 or sy == 0:         # degenerate (constant) predictor
        return (np.nan, np.nan, np.nan, n)
    rx /= sx
    ry /= sy

    beta = float((rx @ ry) / (rx @ rx))     # == Spearman IC
    resid = ry - beta * rx
    u = rx * resid
    xx = float(rx @ rx)
    lrv = _bartlett_lrv(u, lag)
    var_beta = lrv / (xx ** 2)
    if not np.isfinite(var_beta) or var_beta <= 0:
        return (beta, np.nan, np.nan, n)
    se = np.sqrt(var_beta)
    t = beta / se
    p = 2.0 * sps.norm.sf(abs(t))
    return (beta, float(t), float(p), n)


# --------------------------------------------------------------------------- #
# Rolling Spearman IC + overlap-aware IC_IR
# --------------------------------------------------------------------------- #
def rolling_spearman(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
    """
    Vectorized rolling Spearman IC (window bars) with NO per-row python loop.

    Builds sliding windows via stride views, ranks within each window
    (double-argsort = ordinal rank; fast, tie effects negligible for a screen),
    and computes the per-window Pearson correlation of ranks in one vectorized
    pass. Windows containing any NaN are set to NaN.

    Returns an array the same length as x; the first (window-1) entries are NaN.
    """
    x = np.asarray(x, dtype="float64")
    y = np.asarray(y, dtype="float64")
    n = x.shape[0]
    out = np.full(n, np.nan)
    if n < window or window < 5:
        return out

    xw = np.lib.stride_tricks.sliding_window_view(x, window)   # (n-w+1, w)
    yw = np.lib.stride_tricks.sliding_window_view(y, window)

    valid = np.isfinite(xw).all(axis=1) & np.isfinite(yw).all(axis=1)
    if not valid.any():
        return out

    xv = xw[valid]
    yv = yw[valid]
    # ordinal ranks within each row
    rx = np.argsort(np.argsort(xv, axis=1), axis=1).astype("float64")
    ry = np.argsort(np.argsort(yv, axis=1), axis=1).astype("float64")
    rx -= rx.mean(axis=1, keepdims=True)
    ry -= ry.mean(axis=1, keepdims=True)
    num = (rx * ry).sum(axis=1)
    den = np.sqrt((rx * rx).sum(axis=1) * (ry * ry).sum(axis=1))
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = np.where(den > 0, num / den, np.nan)

    filled = np.full(xw.shape[0], np.nan)
    filled[valid] = corr
    out[window - 1:] = filled
    return out


def ic_ir_hac(roll_ic: np.ndarray, lag: int) -> float:
    """
    IC_IR = mean(rolling IC) / (Newey-West HAC std of rolling IC), lag = horizon.

    The rolling ICs overlap heavily (adjacent windows share window-1 bars), so
    their naive std understates dispersion and inflates the IR. We divide by the
    Bartlett long-run standard deviation instead.
    """
    r = np.asarray(roll_ic, dtype="float64")
    r = r[np.isfinite(r)]
    n = r.shape[0]
    if n < 10:
        return np.nan
    mu = r.mean()
    u = r - mu
    lrv = _bartlett_lrv(u, lag) / n        # long-run variance of the series
    if not np.isfinite(lrv) or lrv <= 0:
        return np.nan
    return float(mu / np.sqrt(lrv))


# --------------------------------------------------------------------------- #
# Discrete: per-state expectancy + bull/bear spread
# --------------------------------------------------------------------------- #
def discrete_expectancy(state: np.ndarray, y: np.ndarray, min_n: int) -> dict:
    """
    For a state array coded {+1 bull, -1 bear, 0 neutral, NaN warm-up} and
    forward returns y, compute per-state mean return, hit rate, count, and the
    bull-minus-bear expectancy spread.

    `trusted` is False if either the bull or bear state has fewer than min_n obs.
    """
    state = np.asarray(state, dtype="float64")
    y = np.asarray(y, dtype="float64")
    m = np.isfinite(state) & np.isfinite(y)
    state, y = state[m], y[m]

    def _stats(mask):
        yy = y[mask]
        k = yy.shape[0]
        if k == 0:
            return {"n": 0, "mean": np.nan, "hit": np.nan}
        return {"n": int(k), "mean": float(yy.mean()),
                "hit": float((yy > 0).mean())}

    bull = _stats(state == 1.0)
    bear = _stats(state == -1.0)
    neutral = _stats(state == 0.0)

    if np.isnan(bull["mean"]) or np.isnan(bear["mean"]):
        spread = np.nan
    else:
        spread = bull["mean"] - bear["mean"]

    trusted = (bull["n"] >= min_n) and (bear["n"] >= min_n)
    return {
        "bull": bull, "bear": bear, "neutral": neutral,
        "spread": spread,
        "n_min": int(min(bull["n"], bear["n"])),
        "n_total": int(bull["n"] + bear["n"] + neutral["n"]),
        "trusted": bool(trusted),
    }


# --------------------------------------------------------------------------- #
# Benjamini-Hochberg FDR
# --------------------------------------------------------------------------- #
def benjamini_hochberg(pvals, q: float) -> np.ndarray:
    """
    Benjamini-Hochberg step-up. Returns a boolean mask (True = survives FDR at q)
    aligned to the input order. NaN p-values never survive.
    """
    p = np.asarray(pvals, dtype="float64")
    n = p.shape[0]
    survive = np.zeros(n, dtype=bool)
    finite = np.isfinite(p)
    idx = np.where(finite)[0]
    if idx.size == 0:
        return survive

    pf = p[idx]
    order = np.argsort(pf)
    ps = pf[order]
    m = ps.shape[0]
    ranks = np.arange(1, m + 1)
    thresh = (ranks / m) * q
    below = ps <= thresh
    if below.any():
        kmax = np.max(np.where(below)[0])      # largest rank meeting the line
        keep_sorted = np.zeros(m, dtype=bool)
        keep_sorted[: kmax + 1] = True
        keep = np.zeros(m, dtype=bool)
        keep[order] = keep_sorted
        survive[idx] = keep
    return survive
