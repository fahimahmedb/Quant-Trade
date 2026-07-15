"""Test LogitL2 signal WITHOUT overlay to isolate whether the problem is the signal itself or the overlay.
Since the overlay showed OOS/IS stuck at 1.12 across all CAP values, we need to test:
1. LogitL2 signal alone (from Étape B): does it have positive OOS Sharpe on NDX?
2. LogitL2 + overlay: does adding overlay degrade it further?
This will definitively show which component is failing.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct
from prediction import (
    build_features, triple_barrier_labels, walk_forward_signals,
    backtest, trading_metrics
)
from overlay import vol_target_exposure, extreme_cut, walk_forward_vol_forecast_multi

# CONFIG (same as run_etape_b.py phase 2 fix)
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 21, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0
SEED = 42

# Load NDX (longer history for robust testing)
DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
df_orig = load_ohlc(str(DATA_PATH))
df = df_orig.set_index("date")
close = df["close"].astype(float)
logp = np.log(close)
r_fwd = logp.shift(-1) - logp  # forward return
r_fwd_val = r_fwd.values
r_pct = log_returns_pct(df_orig).values
r_bt = r_pct / 100.0
dates = df.index
n = len(df)

# Build features and labels (same as Étape B)
X = build_features(df)
y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
y.index = df.index

# Generate LogitL2 signal (pure signal, no overlay)
print("=" * 90)
print("TEST 1: PURE LOGITL2 SIGNAL (NO OVERLAY)")
print("=" * 90)

def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)

pos_signal = walk_forward_signals(X, y, pd.Series(r_fwd_val, index=dates), logistic,
                                  T0, REFIT_EVERY, EMBARGO, standardize=True)

oos = np.arange(T0, n - 1)
pnl_signal_only = backtest(pos_signal, r_fwd_val, COST_BPS)[oos]
metr_signal_only = trading_metrics(pnl_signal_only)

print(f"\nLogitL2 Signal (no overlay):")
print(f"  Sharpe (ann):   {metr_signal_only['sharpe_ann']:+.4f}")
print(f"  Sharpe (daily): {metr_signal_only['sharpe_daily']:+.4f}")
print(f"  MDD:            {metr_signal_only['max_drawdown_pct']:.1f}%")
print(f"  Return (ann):   {metr_signal_only['ann_return_pct']:+.1f}%")
print(f"  Profit factor:  {metr_signal_only['profit_factor']:.2f}")

# Now add the overlay on top of this signal
print("\n" + "=" * 90)
print("TEST 2: LOGITL2 SIGNAL + OVERLAY (vol-targeting + extreme-cut)")
print("=" * 90)

# Vol forecasts
PCTL_GRID = [95]
fc = walk_forward_vol_forecast_multi(r_bt, T0, REFIT_EVERY, PCTL_GRID)
vol_fcst = fc["vol_fcst"]
vol_target = fc["vol_target"]
vol_thresh = fc["vol_thresh"]

# Apply overlay to the signal
CAP = 1.50
EXTREME_CUT_FRAC = 0.0
pctl = 95

expo_vt = vol_target_exposure(vol_fcst, vol_target, CAP)
expo_overlay = extreme_cut(expo_vt, vol_fcst, vol_thresh[pctl], EXTREME_CUT_FRAC)

# Align dimensions (in case of off-by-one due to forward return NaN)
min_len = min(len(pos_signal), len(expo_overlay))
pos_signal_aligned = pos_signal[:min_len]
expo_overlay_aligned = expo_overlay[:min_len]

# Combine: signal * overlay
pos_combined = np.nan_to_num(pos_signal_aligned * expo_overlay_aligned, nan=0.0)

pnl_combined_raw = backtest(pos_combined, r_fwd_val[:min_len], COST_BPS)
# Re-filter to OOS after aligning
oos_aligned = np.arange(T0, min_len - 1)
pnl_combined = pnl_combined_raw[oos_aligned]
metr_combined = trading_metrics(pnl_combined)

print(f"\nLogitL2 Signal + Overlay (cap={CAP}, pctl={pctl}):")
print(f"  Sharpe (ann):   {metr_combined['sharpe_ann']:+.4f}")
print(f"  Sharpe (daily): {metr_combined['sharpe_daily']:+.4f}")
print(f"  MDD:            {metr_combined['max_drawdown_pct']:.1f}%")
print(f"  Return (ann):   {metr_combined['ann_return_pct']:+.1f}%")
print(f"  Profit factor:  {metr_combined['profit_factor']:.2f}")

# Compare
print("\n" + "=" * 90)
print("COMPARISON")
print("=" * 90)
print(f"Effect of overlay on LogitL2:")
print(f"  Sharpe (ann):  {metr_signal_only['sharpe_ann']:+.4f} → {metr_combined['sharpe_ann']:+.4f} "
      f"({metr_combined['sharpe_ann'] - metr_signal_only['sharpe_ann']:+.4f})")
print(f"  Profit factor: {metr_signal_only['profit_factor']:.2f} → {metr_combined['profit_factor']:.2f}")
print(f"  MDD:           {metr_signal_only['max_drawdown_pct']:.1f}% → {metr_combined['max_drawdown_pct']:.1f}%")

if metr_combined['sharpe_ann'] > metr_signal_only['sharpe_ann']:
    print(f"\n✓ Overlay IMPROVES LogitL2 signal (as intended for risk management)")
else:
    print(f"\n✗ Overlay DEGRADES LogitL2 signal (unintended negative interaction)")

# Also compare to Buy & Hold
print("\n" + "=" * 90)
print("TEST 3: BUY & HOLD BASELINE")
print("=" * 90)
pos_bh = np.ones(n)
pnl_bh = backtest(pos_bh, r_fwd_val, COST_BPS)[oos]
metr_bh = trading_metrics(pnl_bh)

print(f"\nBuy & Hold (no signal, no overlay):")
print(f"  Sharpe (ann):   {metr_bh['sharpe_ann']:+.4f}")
print(f"  MDD:            {metr_bh['max_drawdown_pct']:.1f}%")
print(f"  Return (ann):   {metr_bh['ann_return_pct']:+.1f}%")

# Summary verdict
print("\n" + "=" * 90)
print("DIAGNOSTIC VERDICT")
print("=" * 90)

rank = sorted([
    ("Buy & Hold", metr_bh['sharpe_ann']),
    ("LogitL2 only", metr_signal_only['sharpe_ann']),
    ("LogitL2 + Overlay", metr_combined['sharpe_ann']),
], key=lambda x: x[1], reverse=True)

print("Ranking by Sharpe (annual):")
for i, (name, sharpe) in enumerate(rank, 1):
    print(f"  {i}. {name}: {sharpe:+.4f}")

if metr_signal_only['sharpe_ann'] < 0:
    print("\n❌ FINDING: LogitL2 signal has NEGATIVE Sharpe — this explains overfitting.")
    print("   The signal itself is negative-expectancy on NDX OOS.")
    print("   → Recommendation: Accept Buy & Hold as the only viable strategy.")
elif metr_signal_only['sharpe_ann'] > metr_bh['sharpe_ann']:
    print("\n✓ FINDING: LogitL2 signal BEATS Buy & Hold.")
    if metr_combined['sharpe_ann'] > metr_signal_only['sharpe_ann']:
        print("   Overlay improves it further.")
    else:
        print("   But overlay degrades it → investigate overlay component.")
else:
    print("\n⚠️  FINDING: LogitL2 signal underperforms Buy & Hold.")
    print(f"   Signal Sharpe: {metr_signal_only['sharpe_ann']:+.4f}")
    print(f"   BH Sharpe:     {metr_bh['sharpe_ann']:+.4f}")
    print(f"   Gap: {metr_bh['sharpe_ann'] - metr_signal_only['sharpe_ann']:+.4f}")
    if metr_combined['sharpe_ann'] > metr_signal_only['sharpe_ann']:
        print("   Overlay improves signal but still below BH.")
    else:
        print("   Overlay makes it worse.")
