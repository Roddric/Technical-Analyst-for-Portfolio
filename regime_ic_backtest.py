"""
regime_ic_backtest.py
=====================
Regime-conditioned, within-slot IC / expectancy backtest. Regime axis ONLY.

The ONE change from grouped_ic_backtest.py: every IC is computed WITHIN a regime
cell. For each asset and each regime with >= MIN_CELL_N observations, indicators are
ranked within their category slot using only that regime's rows. Tests the thesis
that indicator utility CONCENTRATES in specific regimes and averages out on flat
history.

NON-CONTIGUITY GUARD (the single highest-risk bug in this run):
  A regime cell is a set of NON-CONTIGUOUS date segments (regimes recur). We compute
  every indicator and every forward return on the FULL CONTINUOUS price history first,
  and only THEN mask to the cell's dates. We NEVER slice the price series to cell dates
  and recompute an indicator on the stitched result -- that would fabricate fake
  bar-to-bar transitions at segment boundaries and corrupt the indicator. See the
  masking step in process_asset (marked GUARD).

Sector axis: NOT USED (indices are not sector-assignable). Regime labels come from
regime_labels.csv (phase1_segment driven by real FRED/ALFRED macro).

FDR scope: Benjamini-Hochberg is applied WITHIN each (asset, regime) family -- i.e.
across all continuous indicator x horizon tests competing in that cell -- NOT globally.
Rationale: the question is "which indicator wins THIS slot in THIS regime", so the
comparison family is the cell.

Run:  python regime_ic_backtest.py
Outputs under ./results/:
  regime_ic_results.csv
  regime_winners.md
  regime_vs_flat_comparison.md   (+ hypothesis checks appended)
"""

from __future__ import annotations

import os
import traceback

import numpy as np
import pandas as pd

import data_loader
import price_cache               # on-disk cache in front of yfinance (rate-limit safe)
import stats as st
import grouped_ic_backtest as g   # reuse validated library-parsing + indicator eval

# ==========================================================================
# CONFIG
# ==========================================================================
HORIZONS    = [1, 5, 10, 20]
ROLL_WINDOW = 63
FDR_Q       = 0.10
MIN_CELL_N  = 60      # min obs in a (regime) cell to rank at all
LOW_CONF_N  = 100     # cells below this: winners are HYPOTHESES, not edges
MIN_STATE_N = 30

START   = g.START if hasattr(g, "START") else "1990-01-01"
ASSETS  = g.ASSETS
SLOTS   = g.SLOTS
DEFERRED = g.DEFERRED

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")
REGIME_CSV = os.path.join(HERE, "regime_labels.csv")
FLAT_CSV = os.path.join(RESULTS_DIR, "grouped_ic_results.csv")
# ==========================================================================


def load_regime_labels() -> pd.Series:
    df = pd.read_csv(REGIME_CSV, index_col=0, parse_dates=True)
    return df["regime_code"]


def _row(asset, aclass, regime, cell_n, slot, iid, itype, h, ic_or_spread, ic_ir,
         p, fdr, low_conf, note):
    return {"asset": asset, "asset_class": aclass, "regime": regime, "cell_n": cell_n,
            "slot": slot, "indicator_id": iid, "indicator_type": itype, "horizon": h,
            "ic_or_spread": ic_or_spread, "ic_ir": ic_ir, "p_value": p,
            "survives_fdr": fdr, "low_confidence": bool(low_conf), "note": note}


def process_asset(tkr, meta, df, has_volume, roster, regime_s) -> list[dict]:
    cols = {c: df[c] for c in ("open", "high", "low", "close", "volume")}
    close = df["close"].to_numpy("float64")
    mode = g._return_mode(meta)
    aclass = meta["class"]

    # forward returns on FULL CONTINUOUS history (masked later, never stitched)
    fwd = {}
    for hh in HORIZONS:
        f = st.forward_returns(close, hh, mode=mode)
        st.assert_no_lookahead(f, hh)
        fwd[hh] = f

    # tested series on FULL CONTINUOUS history, once per indicator; plus rolling IC
    tested = {}   # iid -> (series_full, kind, slot, roll_by_h)
    for entry in roster:
        iid = entry["id"]
        needs = set(entry.get("data_inputs", []))
        if ("volume" in needs) and not has_volume:
            tested[iid] = (None, None, entry["category"], None, "input unavailable: no volume")
            continue
        try:
            series, kind = g.build_tested_series(entry, cols)
            roll_by_h = {}
            if kind == "continuous":
                for hh in HORIZONS:
                    roll_by_h[hh] = st.rolling_spearman(series, fwd[hh], ROLL_WINDOW)
            tested[iid] = (series, kind, entry["category"], roll_by_h, "")
        except Exception as exc:
            tested[iid] = (None, None, entry["category"], None, f"indicator error: {exc!r}")

    # align regime labels to this asset's dates
    regime_aligned = regime_s.reindex(df.index)

    rows = []
    regimes_here = regime_aligned.dropna().unique()
    for rc in sorted(regimes_here):
        # GUARD: build a boolean MASK over full-history positions for this regime.
        # We mask precomputed full-history arrays -- we do NOT slice prices and
        # recompute indicators on the stitched subset.
        cell_mask = (regime_aligned == rc).to_numpy()
        cell_n = int(cell_mask.sum())
        if cell_n < MIN_CELL_N:
            continue
        low_conf = cell_n < LOW_CONF_N

        for entry in roster:
            iid = entry["id"]
            series, kind, slot, roll_by_h, err = tested[iid]
            if series is None:
                for hh in HORIZONS:
                    rows.append(_row(tkr, aclass, rc, cell_n, slot, iid,
                                     entry["indicator_type"], hh, np.nan, np.nan,
                                     np.nan, None, low_conf, err))
                continue

            for hh in HORIZONS:
                y = fwd[hh]
                if kind == "continuous":
                    xm = series[cell_mask]
                    ym = y[cell_mask]
                    ic, tstat, pval, nobs = st.spearman_ic_hac(xm, ym, lag=hh)
                    rollm = roll_by_h[hh][cell_mask]
                    ic_ir = st.ic_ir_hac(rollm, lag=hh)
                    note = "fwd=yield change" if mode == "diff" else ""
                    if nobs == 0:
                        note = ("degenerate: all-NaN in cell | " + note).rstrip(" |")
                    rows.append(_row(tkr, aclass, rc, cell_n, slot, iid, "continuous",
                                     hh, ic, ic_ir, pval, None, low_conf, note))
                else:
                    statem = series[cell_mask]
                    ym = y[cell_mask]
                    r = st.discrete_expectancy(statem, ym, MIN_STATE_N)
                    note = (f"bull:n={r['bull']['n']},mean={g._f(r['bull']['mean'])} | "
                            f"bear:n={r['bear']['n']},mean={g._f(r['bear']['mean'])}")
                    if not r["trusted"]:
                        note = "UNTRUSTED(state n<MIN_STATE_N) | " + note
                    rows.append(_row(tkr, aclass, rc, cell_n, slot, iid, "discrete",
                                     hh, r["spread"], np.nan, np.nan, None, low_conf, note))
    return rows


def apply_fdr_per_cell(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int, int]:
    """Benjamini-Hochberg WITHIN each (asset, regime) family (across all continuous
    indicator x horizon tests competing in that cell)."""
    df = df.copy()
    is_cont = df["indicator_type"] == "continuous"
    df.loc[is_cont & df["p_value"].isna(), "survives_fdr"] = False
    n_tests = raw_sig = n_surv = 0
    for (asset, regime), grp in df[is_cont & df["p_value"].notna()].groupby(["asset", "regime"]):
        idx = grp.index
        surv = st.benjamini_hochberg(grp["p_value"].to_numpy(), FDR_Q)
        df.loc[idx, "survives_fdr"] = surv
        n_tests += len(idx)
        raw_sig += int((grp["p_value"] < 0.05).sum())
        n_surv += int(surv.sum())
    return df, n_tests, raw_sig, n_surv


# --------------------------------------------------------------------------- #
# outputs
# --------------------------------------------------------------------------- #
def _regime_label_map(regime_full: pd.DataFrame) -> dict:
    return (regime_full.drop_duplicates("regime_code")
            .set_index("regime_code")["regime_label"].to_dict())


def write_regime_winners(df, roster, labelmap):
    prior = {e["id"]: e for e in roster}
    path = os.path.join(RESULTS_DIR, "regime_winners.md")
    L = []; A = L.append
    A("# Regime Winners — within-slot IC per (asset, regime) cell")
    A("")
    A("> **Regime-conditioned, FLAT-history within each regime.** A slot winner is the "
      "best FDR-surviving indicator in that category *inside that regime*. Cells with "
      f"n<{MIN_CELL_N} are skipped (CELL TOO THIN). Cells with n<{LOW_CONF_N} are "
      "labelled low-confidence: a winner there is a **HYPOTHESIS, not a validated "
      "edge**. FDR is applied within each (asset, regime) family. Sector axis not used.")
    A("")
    for asset in sorted(df.asset.unique()):
        sub = df[df.asset == asset]
        aclass = sub.asset_class.iloc[0]
        A(f"## {asset} ({aclass})")
        for rc in sorted(sub.regime.unique()):
            cell = sub[sub.regime == rc]
            cell_n = int(cell.cell_n.iloc[0])
            lbl = labelmap.get(rc, "")
            tag = "  _(low-confidence, HYPOTHESIS)_" if cell_n < LOW_CONF_N else ""
            A(f"\n### {rc} {lbl} — n={cell_n}{tag}")
            for slot in SLOTS:
                slot_rows = cell[cell.slot == slot]
                cont = slot_rows[(slot_rows.indicator_type == "continuous") &
                                 (slot_rows.ic_or_spread.notna())].copy()
                if slot == "Volume" and cont.empty:
                    A(f"- **{slot}**: n/a (no volume)")
                    continue
                surv = cont[cont.survives_fdr == True].copy()
                if len(surv):
                    surv["absic"] = surv.ic_or_spread.abs()
                    w = surv.sort_values("absic", ascending=False).iloc[0]
                    sb = prior.get(w.indicator_id, {}).get("shock_behavior", "?")
                    A(f"- **{slot}** winner: `{w.indicator_id}` h={int(w.horizon)} "
                      f"IC={w.ic_or_spread:+.4f} IC_IR={w.ic_ir:+.3f} "
                      f"p={w.p_value:.1e} (prior {sb})")
                else:
                    A(f"- **{slot}**: NO WINNER (nothing survives FDR)")
        A("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"[write] {path}")


def write_comparison(df, roster, labelmap, fdr_stats):
    n_tests, raw_sig, n_surv = fdr_stats
    prior = {e["id"]: e for e in roster}
    path = os.path.join(RESULTS_DIR, "regime_vs_flat_comparison.md")
    L = []; A = L.append

    # flat IC lookup from the grouped run: (asset, indicator_id, horizon) -> ic
    flat = pd.read_csv(FLAT_CSV)
    flat_c = flat[flat.indicator_type == "continuous"]
    flat_ic = {(r.asset, r.indicator_id, int(r.horizon)): r.ic_or_spread
               for r in flat_c.itertuples()}

    A("# Regime vs Flat — did regime-conditioning revive dead indicators?")
    A("")
    A("> **THE KEY DELIVERABLE.** For each regime-conditioned FDR-surviving slot "
      "winner, we compare its regime IC to its flat-history IC (grouped run). "
      "**Thesis-confirming** = dead flat (|IC|<0.03) but strong in a regime "
      "(|IC|>0.10). Regime IC on a thin cell is a HYPOTHESIS, not an edge.")
    A("")
    A(f"- Continuous cell tests (valid p): **{n_tests}** | raw p<0.05: **{raw_sig}** "
      f"| survive FDR (within-cell) @ {FDR_Q}: **{n_surv}**")
    A("")

    # gather all FDR-surviving continuous winners per (asset, regime, slot)
    cont = df[(df.indicator_type == "continuous") & (df.survives_fdr == True) &
              (df.ic_or_spread.notna())].copy()
    cont["absic"] = cont.ic_or_spread.abs()
    cont["eff_n"] = cont.cell_n / cont.horizon        # independent forward windows

    # ---- ARTIFACT AUDIT (read this BEFORE the winners tables) ----
    A("## ⚠ ARTIFACT AUDIT — read this first")
    A("")
    A("Within-cell IC magnitude is **inflated by overlapping forward returns in small, "
      "non-contiguous regime cells**. At horizon h an n-row cell holds only ~n/h "
      "*independent* forward windows, so |IC| grows mechanically as h rises / cells "
      "shrink. The evidence, over FDR survivors:")
    A("")
    A("| horizon | survivors | median \\|IC\\| | median independent windows (n/h) |")
    A("|---:|---:|---:|---:|")
    for h in HORIZONS:
        s = cont[cont.horizon == h]
        if len(s):
            A(f"| {h} | {len(s)} | {s.absic.median():.3f} | {(s.eff_n).median():.0f} |")
    corr = cont["absic"].corr(1.0 / np.sqrt(cont["eff_n"].clip(lower=1)))
    A("")
    A(f"- Correlation of survivor \\|IC\\| with 1/sqrt(independent windows): "
      f"**{corr:.2f}** — strong; the big ICs live where the effective sample is tiny.")
    A("- **Consequence:** the raw h=10/h=20 'revivals' below are largely overlap/"
      "small-sample noise, NOT evidence indicators concentrate in regimes. The tables "
      "flag `eff_n` (=n/h) and mark rows with <30 independent windows **ARTIFACT-SUSPECT**.")
    A("- A second tell: in the thinnest cells (e.g. ^KS11 RC-04, n~64) *nearly every* "
      "indicator co-fires at once — that is the *cell/period* being idiosyncratic, not "
      "each indicator carrying signal. Co-firing counts are shown per flagged cell.")
    A("")

    # co-firing: how many indicators survive with |IC|>0.30 in each (asset,regime)
    cofire = (cont[cont.absic > 0.30].groupby(["asset", "regime"]).size()
              .rename("cofire_ct").reset_index())
    cofire_map = {(r.asset, r.regime): int(r.cofire_ct) for r in cofire.itertuples()}

    def _flag(effn, asset, rc):
        if effn < 30:
            cf = cofire_map.get((asset, rc), 0)
            return f"ARTIFACT-SUSPECT (eff_n={effn:.0f}" + (f", {cf} co-fire)" if cf >= 5 else ")")
        if effn < 60:
            return f"weak (eff_n={effn:.0f})"
        return f"adequately-sampled (eff_n={effn:.0f})"

    revived, strong = [], []
    for (asset, rc, slot), grp in cont.groupby(["asset", "regime", "slot"]):
        w = grp.sort_values("absic", ascending=False).iloc[0]
        h = int(w.horizon)
        fic = flat_ic.get((asset, w.indicator_id, h), np.nan)
        rec = {"asset": asset, "regime": rc, "slot": slot,
               "indicator_id": w.indicator_id, "horizon": h, "cell_n": int(w.cell_n),
               "eff_n": float(w.eff_n), "regime_ic": w.ic_or_spread, "flat_ic": fic}
        if abs(w.ic_or_spread) > 0.10:
            strong.append(rec)
            if np.isfinite(fic) and abs(fic) < 0.03:
                revived.append(rec)

    # split thesis-confirming by whether they survive the artifact filter
    clean_rev = [r for r in revived if r["eff_n"] >= 60]
    A("## Thesis-confirming candidates: DEAD flat (|IC|<0.03) -> |IC|>0.10 in regime")
    A(f"_Raw count: {len(revived)}. After requiring >=60 independent windows "
      f"(eff_n>=60): {len(clean_rev)}. The rest are artifact-suspect (above)._")
    A("")
    A("### Adequately-sampled (eff_n >= 60) — the only ones worth a second look")
    if not clean_rev:
        A("_NONE. Every flat-dead -> regime-strong case fails the effective-sample "
          "filter. On this evidence the thesis is **not confirmed**: regime-conditioning "
          "did not revive any broadly-dead indicator once overlap/small-sample inflation "
          "is controlled._")
    else:
        A("")
        A("| asset | regime | slot | indicator | h | flat IC | regime IC | cell_n | eff_n | verdict |")
        A("|---|---|---|---|---:|---:|---:|---:|---:|---|")
        for r in sorted(clean_rev, key=lambda z: -abs(z["regime_ic"])):
            A(f"| {r['asset']} | {r['regime']} | {r['slot']} | {r['indicator_id']} | "
              f"{r['horizon']} | {r['flat_ic']:+.4f} | {r['regime_ic']:+.4f} | "
              f"{r['cell_n']} | {r['eff_n']:.0f} | {_flag(r['eff_n'], r['asset'], r['regime'])} |")
    A("")
    A("### Artifact-suspect (eff_n < 60) — shown for completeness, do NOT trust")
    susp = [r for r in revived if r["eff_n"] < 60]
    A(f"_{len(susp)} cases; top 15 by |IC|. Small-sample/overlap inflated._")
    A("")
    A("| asset | regime | slot | indicator | h | flat IC | regime IC | eff_n | flag |")
    A("|---|---|---|---|---:|---:|---:|---:|---|")
    for r in sorted(susp, key=lambda z: -abs(z["regime_ic"]))[:15]:
        A(f"| {r['asset']} | {r['regime']} | {r['slot']} | {r['indicator_id']} | "
          f"{r['horizon']} | {r['flat_ic']:+.4f} | {r['regime_ic']:+.4f} | "
          f"{r['eff_n']:.0f} | {_flag(r['eff_n'], r['asset'], r['regime'])} |")
    A("")

    A("## Strongest adequately-sampled regime winners (eff_n>=60, |IC|>0.10)")
    strong_clean = [r for r in strong if r["eff_n"] >= 60]
    if not strong_clean:
        A("_None._")
    else:
        A("")
        A("| asset | regime | slot | indicator | h | flat IC | regime IC | cell_n | eff_n |")
        A("|---|---|---|---|---:|---:|---:|---:|---:|")
        for r in sorted(strong_clean, key=lambda z: -abs(z["regime_ic"]))[:25]:
            fic = f"{r['flat_ic']:+.4f}" if np.isfinite(r['flat_ic']) else "n/a"
            A(f"| {r['asset']} | {r['regime']} | {r['slot']} | {r['indicator_id']} | "
              f"{r['horizon']} | {fic} | {r['regime_ic']:+.4f} | {r['cell_n']} | {r['eff_n']:.0f} |")
    A("")

    # ---------------- hypothesis checks ----------------
    _hypothesis_checks(A, df, labelmap)

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"[write] {path}")


CALM_TREND = ["RC-01", "RC-02", "RC-03", "RC-10", "RC-12"]
SHOCK_RC = ["RC-06", "RC-08", "RC-15", "RC-16", "RC-17"]


# Hypothesis checks use only h in {1,5} (low forward-return overlap) and SIGNED-mean
# IC across cells, so they are robust to the small-sample |IC| inflation that
# contaminates raw h=10/20 magnitudes (see ARTIFACT AUDIT).
LOWOVERLAP_H = [1, 5]


def _mean_ic_over(df, indicator_id, regimes, aclass=None, slot=None):
    m = (df.indicator_type == "continuous") & (df.indicator_id == indicator_id) & \
        (df.regime.isin(regimes)) & (df.ic_or_spread.notna()) & \
        (df.horizon.isin(LOWOVERLAP_H))
    if aclass:
        m &= (df.asset_class == aclass)
    if slot:
        m &= (df.slot == slot)
    sub = df[m]
    if len(sub) == 0:
        return np.nan, 0
    return float(sub.ic_or_spread.mean()), len(sub)


def _hypothesis_checks(A, df, labelmap):
    A("## Targeted hypothesis checks (from the flat run)")
    A("")
    A("_Computed on low-overlap horizons h in {1,5} and SIGNED-mean IC across cells, "
      "so noise averages out and the h=10/20 overlap inflation (ARTIFACT AUDIT) does "
      "not drive the verdicts._")
    A("")

    # 1. MO-TSI-13-25 concentrates in calm/trending vs shock (equities)
    calm_ic, nc = _mean_ic_over(df, "MO-TSI-13-25", CALM_TREND, aclass="equity")
    shock_ic, ns = _mean_ic_over(df, "MO-TSI-13-25", SHOCK_RC, aclass="equity")
    A("### 1. MO-TSI-13-25 (equity momentum): calm/trending vs shock")
    A(f"- mean cell IC in calm/trending {CALM_TREND}: "
      f"**{calm_ic:+.4f}** (n={nc} cells)" if nc else "- calm/trending: no cells")
    A(f"- mean cell IC in shock {SHOCK_RC}: "
      f"**{shock_ic:+.4f}** (n={ns} cells)" if ns else "- shock: no cells (shock regimes too thin)")
    if nc and ns:
        verdict = ("regime-masking CONFIRMED (concentrates calm, weak/opposite in shock)"
                   if abs(calm_ic) > abs(shock_ic) * 1.5 else
                   "NOT clearly regime-masked (similar across regimes)")
        A(f"- **Verdict:** {verdict}. SUPPRESS prior "
          f"{'is too blunt' if 'CONFIRMED' in verdict else 'stands; drop TSI as a lead'}.")
    else:
        A("- **Verdict:** INCONCLUSIVE — shock regimes too thin in this universe to "
          "test concentration cleanly (see regime distribution).")
    A("")

    # 2. TR-VORTEX-14 — concentrate anywhere or uniformly weak?
    A("### 2. TR-VORTEX-14 (trend, SUBSTITUTE): concentrated or uniformly-weak-least-bad?")
    vsub = df[(df.indicator_id == "TR-VORTEX-14") & (df.indicator_type == "continuous") &
              (df.ic_or_spread.notna()) & (df.horizon.isin(LOWOVERLAP_H))]
    if len(vsub):
        by_regime = vsub.groupby("regime").ic_or_spread.agg(["mean", "count"])
        by_regime = by_regime.reindex(by_regime["mean"].abs().sort_values(ascending=False).index)
        A("- mean cell IC by regime (top 6 by |mean|):")
        for rc, r in by_regime.head(6).iterrows():
            A(f"  - {rc} {labelmap.get(rc,'')}: {r['mean']:+.4f} (n={int(r['count'])})")
        spread = by_regime["mean"].abs().max() - by_regime["mean"].abs().min()
        A(f"- range of |mean IC| across regimes: {spread:.4f}. "
          f"**Verdict:** {'CONCENTRATES in specific regimes' if spread > 0.06 else 'uniformly weak — least-bad, not concentrated'}.")
    else:
        A("- no data.")
    A("")

    # 3. Volatility MAINTAIN winners across regimes vs shock
    A("### 3. Volatility MAINTAIN winners (VO-UI-14, VO-ATRRATIO-14): stable or shock-spike?")
    for iid in ["VO-UI-14", "VO-ATRRATIO-14"]:
        vsub = df[(df.indicator_id == iid) & (df.indicator_type == "continuous") &
                  (df.ic_or_spread.notna()) & (df.horizon.isin(LOWOVERLAP_H))]
        if not len(vsub):
            A(f"- {iid}: no data"); continue
        allm = float(vsub.ic_or_spread.abs().mean())
        shock_m, ns = _mean_ic_over(df, iid, SHOCK_RC)
        calm_m, nc = _mean_ic_over(df, iid, CALM_TREND)
        A(f"- {iid}: mean |IC| all regimes={allm:.4f} | calm mean IC={calm_m:+.4f} (n={nc}) | "
          f"shock mean IC={shock_m:+.4f} (n={ns})")
    A("- **Verdict:** if |IC| is broadly similar across regimes -> confirms "
      "always-measurable MAINTAIN prior; a strong shock-only spike would instead "
      "indicate shock-specific behaviour (shock cells here are thin — read cautiously).")
    A("")
    A("## Caveats")
    A("- **Regime is US-macro/market defined** (Axis1 uses the broad equity index). For "
      "US equity assets the regime shares information with the asset's own trend — not "
      "lookahead (all axes causal/point-in-time), but shared conditioning. Cross-asset "
      "(gold, FX, rates) regimes are exogenous.")
    A("- **Shock regimes (RC-06/08/15/16) are thin or absent** in 1990-2026 developed "
      "markets under a VIX-Z>3 definition; shock-conditioned claims are weak here.")
    A("- **HY OAS only 2023+** (ICE licensing); pre-2023 shock detection is VIX-driven.")
    A("- **Vintage Axis3** is faithful from ~1992 (ALFRED archive start); 1990-91 macro "
      "is approximate. **ISM PMI unavailable** on FRED — Axis3 leans on GDP+CPI.")
    A("- Still FLAT within each regime: not walk-forward, not out-of-sample validated.")


def lookahead_guard(roster) -> None:
    """Truncated-series recompute assertion (as in the TSI spot-check): an
    indicator value at t must be identical whether computed on the full history
    or on close[:t+1] only. Runs on ^GSPC for two indicators x three sample t's."""
    print("Lookahead guard (truncated-series recompute) ...")
    spy = price_cache.load("^GSPC")
    spy = spy[spy.index >= pd.Timestamp(START)]
    check_ids = ["MO-RSI-14", "VO-NATR-14"]
    ok = True
    for iid in check_ids:
        entry = [e for e in roster if e["id"] == iid][0]
        full_cols = {c: spy[c] for c in ("open", "high", "low", "close", "volume")}
        full_series, _ = g.build_tested_series(entry, full_cols)
        for t in (2000, 4000, 6000):
            if t >= len(spy):
                continue
            trunc = spy.iloc[: t + 1]
            tcols = {c: trunc[c] for c in ("open", "high", "low", "close", "volume")}
            ts, _ = g.build_tested_series(entry, tcols)
            a, b = full_series[t], ts[-1]
            match = (np.isnan(a) and np.isnan(b)) or (np.isfinite(a) and abs(a - b) < 1e-8)
            ok = ok and match
            print(f"  {iid} t={t}: full={a:.6f} trunc={b:.6f} match={match}")
    print(f"  -> lookahead guard: {'PASS' if ok else 'FAIL'}")
    if not ok:
        raise AssertionError("lookahead guard failed: indicator depends on future bars")


def main() -> int:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    roster, skipped = g.parse_library(g.LIBRARY_MD)
    print(f"Library: {len(roster)} indicators, {len(skipped)} skipped.")
    lookahead_guard(roster)

    regime_full = pd.read_csv(REGIME_CSV, index_col=0, parse_dates=True)
    regime_s = regime_full["regime_code"]
    labelmap = _regime_label_map(regime_full.reset_index())
    print(f"Regime labels: {len(regime_s)} days, {regime_s.nunique()} regimes.")

    all_rows = []
    for tkr, meta in ASSETS.items():
        try:
            df = price_cache.load(tkr)
        except Exception as exc:
            print(f"  fetch fail {tkr}: {exc!r}"); continue
        if df is None:
            print(f"  fetch fail {tkr}"); continue
        df = df[df.index >= pd.Timestamp(START)]
        if len(df) == 0:
            print(f"  no data after START {tkr}"); continue
        has_vol = g._has_volume(df)
        try:
            rows = process_asset(tkr, meta, df, has_vol, roster, regime_s)
            all_rows.extend(rows)
            ncells = len({(r["regime"]) for r in rows})
            print(f"  processed {tkr}: {len(rows)} rows across {ncells} regime cells")
        except Exception:
            print(f"  ERROR {tkr}:"); traceback.print_exc()

    if not all_rows:
        print("No results."); return 1

    df = pd.DataFrame(all_rows)
    df, n_tests, raw_sig, n_surv = apply_fdr_per_cell(df)
    df = df.sort_values(["asset_class", "asset", "regime", "slot", "indicator_id",
                         "horizon"]).reset_index(drop=True)

    csv_path = os.path.join(RESULTS_DIR, "regime_ic_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"[write] {csv_path} ({len(df)} rows)")

    write_regime_winners(df, roster, labelmap)
    write_comparison(df, roster, labelmap, (n_tests, raw_sig, n_surv))

    print(f"\nDONE. within-cell continuous tests={n_tests} raw p<0.05={raw_sig} "
          f"survive FDR={n_surv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
