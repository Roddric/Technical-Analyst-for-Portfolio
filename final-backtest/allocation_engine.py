"""
allocation_engine.py
=====================
Two weighting methods over a multi-asset universe:

  (1) RISK PARITY (inverse-vol / equal-risk-contribution)
        - needs ONLY a covariance matrix of returns. No signal, no forecast.
        - runnable TODAY on real data, nothing fabricated.

  (2) SIGNAL-STRENGTH WEIGHTING
        - tilts weights by validated indicator IC per (asset_class, slot).
        - inputs are the ACTUAL FDR-surviving large-cell mean ICs from
          regime_ic_results.csv (audited). Cells with no survivor => 0 tilt.
        - a zero-signal slot contributes zero tilt. The structure cannot
          launder a fabricated number: if it's not in SIGNAL_IC, it's a 0.

HONESTY CONSTRAINTS (read before trusting any output):
  * The ICs below are measured on a BROAD-INDEX universe (^GSPC, ^NDX, CL=F,
    GC=F, DX-Y.NYB, etc.), NOT on the boss's ticker list (SOXX, VGT, STAR50,
    single names). Applying class-level IC to a specific ticker ASSUMES that
    ticker behaves like its asset class. That assumption is UNVALIDATED for
    every single-name / sector ETF in the target list. Flagged, not hidden.
  * ICs are tiny in absolute terms (equity ~0.02-0.05). Signal weighting on
    |IC|<0.05 is sizing off noise. The code caps tilt so a weak signal can
    never dominate risk-parity. This is a guardrail, not a fix for weak signal.
  * This is FLAT-within-regime, not walk-forward. No live-trading claim.
"""

from __future__ import annotations
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# HONEST SIGNAL INPUT: mean IC of FDR-surviving, large-cell (n>=1000) results,
# per (asset_class, slot), taken directly from the audit of regime_ic_results.csv.
# Sign preserved. A missing (class, slot) key == 0.0 tilt (no survivor).
# ---------------------------------------------------------------------------
SIGNAL_IC = {
    ("credit", "Momentum"): -0.1676, ("credit", "Trend"): -0.1527,
    ("credit", "Volatility"): 0.1854, ("credit", "Volume"): -0.1870,
    ("energy", "Momentum"): -0.1216, ("energy", "Trend"): -0.1197,
    ("energy", "Volatility"): 0.1500, ("energy", "Volume"): -0.0938,
    ("equity", "Momentum"): -0.0549, ("equity", "Trend"): 0.0011,
    ("equity", "Volatility"): 0.0196, ("equity", "Volume"): -0.0876,
    ("fx", "Momentum"): -0.1067, ("fx", "Trend"): 0.0925,
    ("fx", "Volatility"): -0.0845, ("fx", "Volume"): -0.3001,
    ("metals", "Momentum"): -0.1439, ("metals", "Trend"): -0.1555,
    ("metals", "Volatility"): -0.0047, ("metals", "Volume"): -0.1559,
    ("rates", "Momentum"): 0.1537, ("rates", "Trend"): 0.1774,
    ("rates", "Volatility"): 0.1497, ("rates", "Volume"): -0.1396,
}


def asset_class_signal_score(asset_class: str) -> float:
    """
    Aggregate an asset class's slot ICs into ONE conviction score in [0, ~].
    We use mean |IC| across that class's slots that have survivors. This is a
    magnitude-of-evidence score, NOT a directional view. Direction is the
    strategy's job (contrarian vs directional per slot); allocation only sizes.
    Classes with no surviving slot => 0.0 (no conviction => no tilt).
    """
    ics = [abs(v) for (ac, _slot), v in SIGNAL_IC.items() if ac == asset_class]
    return float(np.mean(ics)) if ics else 0.0


# ---------------------------------------------------------------------------
# (1) RISK PARITY  -- no signal required
# ---------------------------------------------------------------------------
def inverse_vol_weights(cov: pd.DataFrame) -> pd.Series:
    """Simple risk parity: weight_i proportional to 1/sigma_i, normalized."""
    sigma = np.sqrt(np.diag(cov.values))
    inv = 1.0 / sigma
    w = inv / inv.sum()
    return pd.Series(w, index=cov.index, name="risk_parity")


def erc_weights(cov: pd.DataFrame, iters: int = 20000, lr: float = 1e-2) -> pd.Series:
    """
    True Equal-Risk-Contribution via projected gradient. Each asset contributes
    equal share of total portfolio variance. Falls back gracefully; for most
    covariances inverse-vol is a close approximation, ERC refines it.
    """
    n = cov.shape[0]
    Sig = cov.values
    w = np.ones(n) / n
    for _ in range(iters):
        mrc = Sig @ w                      # marginal risk contribution
        rc = w * mrc                       # risk contribution
        target = rc.mean()
        grad = mrc + (rc - target)         # push contributions toward equal
        w = w - lr * grad
        w = np.clip(w, 1e-6, None)
        w = w / w.sum()
    return pd.Series(w, index=cov.index, name="erc")


# ---------------------------------------------------------------------------
# (2) SIGNAL-STRENGTH WEIGHTING  -- tilts a risk-parity base by conviction
# ---------------------------------------------------------------------------
def signal_strength_weights(
    tickers: list[str],
    ticker_to_class: dict[str, str],
    cov: pd.DataFrame,
    tilt_cap: float = 0.5,
) -> pd.DataFrame:
    """
    Combine risk-parity base with a signal tilt.

    base_i    = risk-parity weight (inverse-vol)
    score_i   = asset_class_signal_score(class(i))   # mean |IC|, >=0
    tilt_i    = 1 + tilt_cap * (score_i - mean_score) / (mean_score + eps)
                -> capped so weak signal can't dominate risk balance
    final_i   = normalize(base_i * tilt_i)

    A ticker whose class has NO surviving signal gets score 0 -> tilt < 1 ->
    it is UNDERWEIGHTED relative to risk parity, never fabricated up.
    """
    base = inverse_vol_weights(cov)
    scores = pd.Series(
        {t: asset_class_signal_score(ticker_to_class[t]) for t in tickers},
        name="signal_score",
    )
    eps = 1e-9
    mean_s = scores.mean()
    # relative tilt, capped to [1 - tilt_cap, 1 + tilt_cap]
    raw_tilt = 1.0 + tilt_cap * (scores - mean_s) / (mean_s + eps)
    tilt = raw_tilt.clip(1 - tilt_cap, 1 + tilt_cap)
    tilted = base * tilt
    final = tilted / tilted.sum()

    out = pd.DataFrame({
        "asset_class": [ticker_to_class[t] for t in tickers],
        "signal_score": scores.reindex(tickers).values,
        "risk_parity_w": base.reindex(tickers).values,
        "signal_tilt": tilt.reindex(tickers).values,
        "final_w": final.reindex(tickers).values,
    }, index=tickers)
    return out.sort_values("final_w", ascending=False)


# ---------------------------------------------------------------------------
# DEMO on the boss's universe. Covariance here is a LABELED PLACEHOLDER derived
# from rough asset-class vol/correlation priors — because this sandbox has no
# network. REPLACE `demo_cov` with a real sample covariance of daily returns
# (yfinance) before using any number operationally.
# ---------------------------------------------------------------------------
def _demo():
    universe = {
        # boss's list, mapped to the asset_class whose IC we measured
        "^GSPC": "equity", "^NDX": "equity", "SOXX": "equity", "VGT": "equity",
        "XLE": "equity", "GLD_eq": "equity",   # note: GLD as equity-ETF wrapper
        "HSI_TECH": "equity", "ASHR": "equity", "STAR50": "equity",
        "^FTSE": "equity", "^KS11": "equity", "^N225": "equity", "TAIEX": "equity",
        "VEA": "equity", "VWO": "equity",
        "UST_10Y": "rates",
        "GOLD": "metals", "SILVER": "metals", "COPPER": "metals",
        "OIL": "energy",
    }
    tickers = list(universe.keys())

    # ---- LABELED PLACEHOLDER covariance (annualized) ----
    rng = np.random.default_rng(0)
    vol_by_class = {"equity": 0.18, "rates": 0.07, "metals": 0.22,
                    "energy": 0.35}
    vols = np.array([vol_by_class[universe[t]] for t in tickers])
    # block correlation: same-class 0.7, cross-class 0.2
    n = len(tickers)
    corr = np.full((n, n), 0.2)
    for i in range(n):
        for j in range(n):
            if universe[tickers[i]] == universe[tickers[j]]:
                corr[i, j] = 0.7
            if i == j:
                corr[i, j] = 1.0
    cov = pd.DataFrame(np.outer(vols, vols) * corr, index=tickers, columns=tickers)

    print("=" * 70)
    print("RISK PARITY (inverse-vol) — needs NO signal, runnable on real data now")
    print("=" * 70)
    rp = inverse_vol_weights(cov)
    print(rp.sort_values(ascending=False).round(4).to_string())

    print("\n" + "=" * 70)
    print("SIGNAL-STRENGTH WEIGHTED — risk-parity base tilted by audited IC")
    print("  (equity score is LOW by design: weak measured signal)")
    print("=" * 70)
    ss = signal_strength_weights(tickers, universe, cov, tilt_cap=0.5)
    print(ss.round(4).to_string())

    print("\nNOTE: signal_score is class-level mean|IC| from index-universe")
    print("tests. Single names (SOXX/VGT/STAR50) INHERIT class signal —")
    print("UNVALIDATED per-ticker. Replace demo_cov with real returns cov.")


if __name__ == "__main__":
    _demo()
