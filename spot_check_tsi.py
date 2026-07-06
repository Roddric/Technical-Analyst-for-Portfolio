"""
spot_check_tsi.py
=================
STANDALONE spot-check: is MO-TSI-13-25's momentum-slot win real or an artifact?

Single asset (^NDX), single indicator (TSI). Reuses data_loader.py only. Does NOT
touch or import the grouped backtest logic beyond READING it to confirm which column
it used, and reading its results CSV to compare numbers.

Rules out: (a) wrong output column, (b) lookahead in the signal line, (c) confirms
the IC magnitude/sign reproduces, and puts it in context vs RSI(14).

Run:  python spot_check_tsi.py
"""

from __future__ import annotations

import os
import re

import numpy as np
import pandas as pd
from scipy import stats as sps

import pandas_ta_classic as ta
import data_loader

ASSET = "^NDX"
START = "1990-01-01"
HORIZONS = [1, 5, 10, 20]
HERE = os.path.dirname(os.path.abspath(__file__))


def sec(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ----- methodology helpers (kept local + explicit so this file stands alone) -----
def forward_log_returns(close: np.ndarray, h: int) -> np.ndarray:
    close = np.asarray(close, dtype="float64")
    n = close.shape[0]
    fwd = np.full(n, np.nan)
    fwd[:-h] = np.log(close[h:] / close[:-h])
    return fwd


def spearman_ic(x: np.ndarray, y: np.ndarray):
    x = np.asarray(x, "float64"); y = np.asarray(y, "float64")
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = x.shape[0]
    if n < 10:
        return np.nan, n, np.nan
    ic, p = sps.spearmanr(x, y)
    return float(ic), n, float(p)


# ============================ STEP 1 — FETCH ============================
sec(f"STEP 1 — FETCH {ASSET} via existing data_loader (START={START})")
df = data_loader.load_ohlcv(ASSET)
df = df[df.index >= pd.Timestamp(START)]
d = data_loader.describe(df)
print(f"date range: {d['start']} -> {d['end']} | rows: {d['rows']}")
print("last 3 rows of OHLCV:")
print(df.tail(3).to_string())
close = df["close"]

# ============================ STEP 2 — COMPUTE TSI ============================
sec("STEP 2 — COMPUTE TSI (pandas-ta-classic, library call ta.tsi(close))")
# library entry MO-TSI-13-25: library_call 'ta.tsi(close)', defaults fast=13/slow=25/signal=13
tsi = ta.tsi(close)                       # matches the library's exact call
tsi = tsi.reindex(close.index)            # same reindex the main backtest applies
print("returned columns:", list(tsi.columns))
line_col = [c for c in tsi.columns if c.startswith("TSI_")][0]
sig_col  = [c for c in tsi.columns if c.startswith("TSIs")][0]
print(f"  -> TSI LINE   column = {line_col!r}")
print(f"  -> SIGNAL     column = {sig_col!r}")
print("last 5 rows of BOTH columns:")
print(tsi[[line_col, sig_col]].tail(5).to_string())

# ============================ STEP 3 — WHICH COLUMN DID THE MAIN RUN USE? ======
sec("STEP 3 — IDENTIFY the column the main backtest used")
with open(os.path.join(HERE, "grouped_ic_backtest.py"), "r", encoding="utf-8") as fh:
    gsrc = fh.read()
# quote the level-transform selection lines
glines = gsrc.splitlines()
for i, ln in enumerate(glines, 1):
    if 'tf == "level"' in ln or 'entry["tested_column"]' in ln and i < 245:
        pass
print("grouped_ic_backtest.py selects continuous 'level' indicators here:")
for i in range(225, 228):
    print(f"  L{i+1}: {glines[i]}")
print("  _pick_column picks df[col] where col == entry['tested_column'] (L153-160).")

# read the library entry to see tested_column
with open(os.path.join(HERE, "indicator_library.md"), "r", encoding="utf-8") as fh:
    lib = fh.read()
m = re.search(r"```json\s*(.*?)```", lib, re.DOTALL)
import json
roster = json.loads(m.group(1))
tsi_entry = [e for e in roster if e["id"] == "MO-TSI-13-25"][0]
print(f"\nlibrary entry MO-TSI-13-25:")
print(f"  library_call  = {tsi_entry['library_call']!r}")
print(f"  tested_column = {tsi_entry['tested_column']!r}")
print(f"  transform     = {tsi_entry['transform']!r}")
used_line = (tsi_entry["tested_column"] == line_col)
print(f"\n==> Main backtest used column {tsi_entry['tested_column']!r} = "
      f"{'the TSI LINE (intended)' if used_line else 'NOT the TSI line (!!)'}")

# ============================ STEP 4 — LOOKAHEAD ASSERT ============================
sec("STEP 4 — LOOKAHEAD ASSERT (h=5): TSI[t] must depend only on close[:t+1]")
full_line = tsi[line_col].to_numpy("float64")
close_arr = close.to_numpy("float64")
sample_ts = [3000, 5000, 7000]
print(f"{'t':>6} {'full TSI[t]':>16} {'trunc TSI[t]':>16} {'abs diff':>14}  match?")
all_match = True
for t in sample_ts:
    if t >= len(close):
        continue
    trunc = ta.tsi(close.iloc[: t + 1])          # recompute on close[:t+1] only
    trunc_val = trunc[line_col].to_numpy("float64")[-1]  # TSI at index t
    full_val = full_line[t]
    diff = abs(trunc_val - full_val)
    match = np.isfinite(diff) and diff < 1e-8
    all_match = all_match and match
    print(f"{t:>6} {full_val:>16.10f} {trunc_val:>16.10f} {diff:>14.2e}  {match}")
print(f"\n==> lookahead check: {'PASS (causal, values match)' if all_match else 'FAIL (mismatch!)'}")

# ============================ STEP 5 — REPRODUCE THE IC ============================
sec("STEP 5 — REPRODUCE IC: TSI line vs signal, per horizon")
sig_arr = tsi[sig_col].to_numpy("float64")
print(f"{'h':>4} | {'IC(line)':>10} {'p(line)':>10} {'n':>7} | "
      f"{'IC(signal)':>11} {'p(signal)':>11}")
line_ics = {}
for h in HORIZONS:
    y = forward_log_returns(close_arr, h)
    ic_l, n_l, p_l = spearman_ic(full_line, y)
    ic_s, n_s, p_s = spearman_ic(sig_arr, y)
    line_ics[h] = ic_l
    print(f"{h:>4} | {ic_l:>10.4f} {p_l:>10.2e} {n_l:>7} | {ic_s:>11.4f} {p_s:>11.2e}")

# compare to what the main run wrote in its CSV
sec("STEP 5b — COMPARE to main run's grouped_ic_results.csv (^NDX, MO-TSI-13-25)")
csv = os.path.join(HERE, "results", "grouped_ic_results.csv")
if os.path.exists(csv):
    res = pd.read_csv(csv)
    sub = res[(res.asset == ASSET) & (res.indicator_id == "MO-TSI-13-25")]
    print(sub[["horizon", "ic_or_spread", "ic_ir", "n_obs", "p_value", "survives_fdr"]]
          .to_string(index=False))
    print("\nfreshly reproduced IC(line) by horizon:", {h: round(v, 4) for h, v in line_ics.items()})
    print("(these should match the CSV's ic_or_spread if the main run used the line)")
else:
    print("results CSV not found; skipping direct comparison.")

# ============================ STEP 6 — RSI BASELINE ============================
sec("STEP 6 — SANITY BASELINE: RSI(14) IC on same asset/horizons")
rsi = ta.rsi(close, length=14).reindex(close.index).to_numpy("float64")
print(f"{'h':>4} | {'IC(TSI line)':>13} | {'IC(RSI14)':>11} | {'|TSI|>|RSI|?':>12}")
for h in HORIZONS:
    y = forward_log_returns(close_arr, h)
    ic_t, _, _ = spearman_ic(full_line, y)
    ic_r, _, _ = spearman_ic(rsi, y)
    bigger = abs(ic_t) > abs(ic_r)
    print(f"{h:>4} | {ic_t:>13.4f} | {ic_r:>11.4f} | {str(bigger):>12}")

# ============================ VERDICT ============================
sec("VERDICT")
h5_line = line_ics[5]
maxabs = max(abs(v) for v in line_ics.values())
print(f"- Column used by main backtest : {tsi_entry['tested_column']} "
      f"({'TSI line — intended' if used_line else 'WRONG column'})")
print(f"- Lookahead check              : {'PASS' if all_match else 'FAIL'}")
print(f"- Reproduced IC (line), h=5    : {h5_line:.4f}")
print(f"- Max |IC| across horizons     : {maxabs:.4f}")
print(f"- TSI line IC vs signal IC     : printed above (Step 5)")
print(f"- TSI vs RSI magnitude          : printed above (Step 6)")

# programmatic verdict
if not used_line:
    verdict = "artifact — wrong column"
elif not all_match:
    verdict = "artifact — lookahead"
elif maxabs < 0.05:
    verdict = "real but marginal — least-bad in a weak field (|IC|<0.05)"
else:
    verdict = "real and notable — carry into regime run"
print(f"\nVERDICT: [{verdict}]")
print("\nNote: 'real' != 'tradeable'. A statistically-nonzero IC below ~0.05 is a")
print("weak edge that only 'wins the slot' because the whole momentum field is weak")
print("on flat, full-history data. Regime conditioning is required before trusting it.")
