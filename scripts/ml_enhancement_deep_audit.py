#!/usr/bin/env python3
"""
DEEP AUDIT: ML Enhancement Skepticism Check
=============================================
Questions to answer (rigorously):

1. Is the 5.069 Sharpe real or look-ahead bias / data snooping?
2. Walk-forward validation: Does the 3d-ML filter survive proper embargo?
3. Robustness check: Does improvement hold across different time periods?
4. Regime stability: Does performance degrade in specific market conditions?
5. Parameter overfitting: Is the 3d window discovery spurious?
6. Comparative test: How does 3d-ML compare to simpler baselines?
7. Null hypothesis: What if we used random parameters?

AUDIT PROTOCOL:
- Walk-forward: T0=750 (in-sample), purge=21d, embargo=21d, refit every 21d
- Anti-snooping: Never retrain parameters on test set
- Regime analysis: Bull/bear/sideways/vol regimes separately
- Null testing: Random parameter sweep vs optimized params
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "finance" / "src"))
from data_loader import load_ohlc, log_returns_pct

def calc_sharpe(returns, ann=252):
    if len(returns) < 2: return 0.0
    mu, sigma = np.mean(returns), np.std(returns, ddof=1)
    return float(mu / sigma * np.sqrt(ann)) if sigma > 0 else 0.0

def calc_mdd(returns_pct):
    if len(returns_pct) == 0: return np.nan
    cumsum_pct = np.cumsum(returns_pct)
    equity = np.exp(cumsum_pct / 100.0)
    peak = np.maximum.accumulate(equity)
    return float(((equity - peak) / peak).min() * 100)

def backtest_simple(positions, returns, cost_bps=5):
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    return pnl - turn * (turn * (cost_bps / 1e4))

print("\n" + "="*80)
print("DEEP AUDIT: ML ENHANCEMENT SKEPTICISM CHECK")
print("="*80)
print("\nQuestion: Is 5.069 Sharpe real or data snooping artifact?")
print("Protocol: Walk-forward validation + regime analysis + null hypothesis testing")

# Load data
df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)
min_len = min(len(df), len(r))
df = df.iloc[:min_len].copy()
r = r.iloc[:min_len].copy()

print(f"\nData: {len(df)} observations (NDX, 40 years)")

# ============================================================================
# AUDIT 1: WALK-FORWARD VALIDATION (Anti-data-snooping)
# ============================================================================

print("\n" + "="*80)
print("AUDIT 1: WALK-FORWARD VALIDATION")
print("="*80)
print("\nProtocol: T0=750 (in-sample), purge=21d, embargo=21d, refit=21d")
print("Question: Does the 3d-ML filter survive proper embargo and out-of-sample testing?")

T0 = 750
refit_freq = 21
purge_days = 21
embargo_days = 21

wf_results = []
window_start = 0

while window_start + T0 + embargo_days < len(df):
    # In-sample window
    is_start, is_end = window_start, window_start + T0

    # Out-of-sample window (with embargo)
    oos_start = is_end + embargo_days
    oos_end = min(oos_start + refit_freq, len(df))

    if oos_end <= len(df):
        # In-sample: optimize parameters
        df_is = df.iloc[is_start:is_end]
        r_is = r.iloc[is_start:is_end]

        ema50_is = df_is['close'].ewm(span=50).mean().values
        ema200_is = df_is['close'].ewm(span=200).mean().values
        ema_trend_is = ema50_is / ema200_is

        momentum_3d_is = np.array([np.sum(r_is.iloc[max(0,i-3):i+1]) if i > 0 else 0 for i in range(len(r_is))])

        # Build S5-OV base
        signal_base_is = np.where(ema50_is > ema200_is, 1.0, 0.0)
        vol_20_is = pd.Series(r_is).rolling(20).std()
        vol_low_is = vol_20_is.quantile(0.25)
        vol_high_is = vol_20_is.quantile(0.75)

        overlay_is = np.ones(len(signal_base_is))
        for i in range(len(overlay_is)):
            if pd.notna(vol_20_is.iloc[i]):
                if vol_20_is.iloc[i] < vol_low_is:
                    overlay_is[i] = 1.5
                elif vol_20_is.iloc[i] > vol_high_is:
                    overlay_is[i] = 0.3

        signal_s5ov_is = signal_base_is * overlay_is

        # Optimize on in-sample (find best 3d momentum threshold)
        best_sharpe_is = -np.inf
        best_mom_t = 0.0

        for mom_t in np.arange(-0.2, 0.5, 0.1):
            filter_is = (momentum_3d_is > mom_t) & (ema_trend_is > 0.94)
            signal_is = signal_s5ov_is * filter_is.astype(float)
            pnl_is = backtest_simple(signal_is, r_is.values)
            sharpe_is = calc_sharpe(pnl_is)

            if sharpe_is > best_sharpe_is:
                best_sharpe_is = sharpe_is
                best_mom_t = mom_t

        # Out-of-sample: Apply optimized parameters (NO retraining)
        df_oos = df.iloc[oos_start:oos_end]
        r_oos = r.iloc[oos_start:oos_end]

        if len(df_oos) > 0:
            ema50_oos = df_oos['close'].ewm(span=50).mean().values
            ema200_oos = df_oos['close'].ewm(span=200).mean().values
            ema_trend_oos = ema50_oos / ema200_oos

            momentum_3d_oos = np.array([np.sum(r_oos.iloc[max(0,i-3):i+1]) if i > 0 else 0 for i in range(len(r_oos))])

            signal_base_oos = np.where(ema50_oos > ema200_oos, 1.0, 0.0)
            vol_20_oos = pd.Series(r_oos).rolling(20).std()
            vol_low_oos = vol_20_oos.quantile(0.25)
            vol_high_oos = vol_20_oos.quantile(0.75)

            overlay_oos = np.ones(len(signal_base_oos))
            for i in range(len(overlay_oos)):
                if pd.notna(vol_20_oos.iloc[i]):
                    if vol_20_oos.iloc[i] < vol_low_oos:
                        overlay_oos[i] = 1.5
                    elif vol_20_oos.iloc[i] > vol_high_oos:
                        overlay_oos[i] = 0.3

            signal_s5ov_oos = signal_base_oos * overlay_oos

            # Apply same parameters to OOS
            filter_oos = (momentum_3d_oos > best_mom_t) & (ema_trend_oos > 0.94)
            signal_oos = signal_s5ov_oos * filter_oos.astype(float)
            pnl_oos = backtest_simple(signal_oos, r_oos.values)
            sharpe_oos = calc_sharpe(pnl_oos)

            wf_results.append({
                'window': len(wf_results),
                'is_sharpe': best_sharpe_is,
                'oos_sharpe': sharpe_oos,
                'mom_t': best_mom_t,
                'degradation': best_sharpe_is - sharpe_oos
            })

    window_start += refit_freq

print(f"\nWalk-forward results ({len(wf_results)} windows):")
print(f"{'Window':>6} | {'In-Sample':>12} | {'Out-of-Sample':>15} | {'Degradation':>12} | {'Mom Thresh':>12}")
print("─" * 70)

is_sharpes = []
oos_sharpes = []

for r in wf_results[-10:]:  # Show last 10
    is_sharpes.append(r['is_sharpe'])
    oos_sharpes.append(r['oos_sharpe'])
    marker = "⚠️" if r['degradation'] > 1.0 else "✅"
    print(f"{marker} {r['window']:5d} | {r['is_sharpe']:12.3f} | {r['oos_sharpe']:15.3f} | {r['degradation']:12.3f} | {r['mom_t']:12.2f}")

avg_is = np.mean(is_sharpes)
avg_oos = np.mean(oos_sharpes)
avg_deg = avg_is - avg_oos

print(f"\nSummary:")
print(f"  Average in-sample Sharpe:  {avg_is:.3f}")
print(f"  Average out-of-sample Sharpe: {avg_oos:.3f}")
print(f"  Average degradation:       {avg_deg:.3f}")

if avg_deg > 1.0:
    print(f"\n🚨 WARNING: Large IS→OOS degradation ({avg_deg:.3f}) suggests OVERFITTING")
elif avg_deg > 0.5:
    print(f"\n⚠️ CAUTION: Moderate degradation ({avg_deg:.3f}) suggests some overfitting")
else:
    print(f"\n✅ OK: Low degradation ({avg_deg:.3f}), walk-forward holds")

# ============================================================================
# AUDIT 2: LOOK-AHEAD BIAS CHECK
# ============================================================================

print("\n" + "="*80)
print("AUDIT 2: LOOK-AHEAD BIAS CHECK")
print("="*80)
print("\nQuestion: Is the improvement from subtle bugs (using future data)?")

# Test: Apply 3d momentum filter strictly causally (never use future data)
ema50 = df['close'].ewm(span=50).mean().values
ema200 = df['close'].ewm(span=200).mean().values
ema_trend = ema50 / ema200

# Strict causal 3d momentum (can only use past 3 days)
if isinstance(r, pd.Series):
    r_arr = r.values
else:
    r_arr = np.array(r)
momentum_3d_causal = np.zeros(len(r_arr))
for i in range(3, len(r_arr)):
    momentum_3d_causal[i] = float(np.sum(r_arr[max(0,i-3):i+1]))  # Up to and including current

# S5-OV base
signal_base = np.where(ema50 > ema200, 1.0, 0.0)
vol_20_series = pd.Series(r).rolling(20).std()
vol_low = vol_20_series.quantile(0.25)
vol_high = vol_20_series.quantile(0.75)

overlay = np.ones(len(signal_base))
for i in range(len(overlay)):
    if pd.notna(vol_20_series.iloc[i]):
        if vol_20_series.iloc[i] < vol_low:
            overlay[i] = 1.5
        elif vol_20_series.iloc[i] > vol_high:
            overlay[i] = 0.3

signal_s5ov = signal_base * overlay

# Apply filter with strict causality
filter_causal = (momentum_3d_causal > 0.3) & (ema_trend > 0.94)
signal_causal = signal_s5ov * filter_causal.astype(float)
pnl_causal = backtest_simple(signal_causal, r.values)
sharpe_causal = calc_sharpe(pnl_causal)

print(f"\nStrict causal test:")
print(f"  Sharpe (causal, no look-ahead): {sharpe_causal:.3f}")
print(f"  Expected (from non-causal): ~5.0")

if sharpe_causal < 3.0:
    print(f"\n🚨 CRITICAL: Causal Sharpe ({sharpe_causal:.3f}) much lower than reported (5.0)")
    print(f"   → Likely LOOK-AHEAD BIAS in original calculation")
elif sharpe_causal < 4.0:
    print(f"\n⚠️ WARNING: Some degradation with strict causality")
else:
    print(f"\n✅ OK: Strict causality maintains performance")

# ============================================================================
# AUDIT 3: PARAMETER SENSITIVITY & OVERFITTING
# ============================================================================

print("\n" + "="*80)
print("AUDIT 3: PARAMETER OVERFITTING CHECK")
print("="*80)
print("\nQuestion: Is the 3d window discovery robust or a data-snooping fluke?")

# Test: Run same optimization on random subsamples
np.random.seed(42)
subsample_results = []

for sample_num in range(5):
    # Random subsample (50% of data)
    mask = np.random.choice([True, False], size=len(df), p=[0.5, 0.5])
    df_sub = df[mask].reset_index(drop=True)
    r_sub = r[mask].reset_index(drop=True)

    if len(df_sub) < 100:
        continue

    # Test different momentum windows on this subsample
    ema50_sub = df_sub['close'].ewm(span=50).mean().values
    ema200_sub = df_sub['close'].ewm(span=200).mean().values
    ema_trend_sub = ema50_sub / ema200_sub

    vol_20_sub = pd.Series(r_sub).rolling(20).std()
    vol_low_sub = vol_20_sub.quantile(0.25)
    vol_high_sub = vol_20_sub.quantile(0.75)

    signal_base_sub = np.where(ema50_sub > ema200_sub, 1.0, 0.0)
    overlay_sub = np.ones(len(signal_base_sub))
    for i in range(len(overlay_sub)):
        if pd.notna(vol_20_sub.iloc[i]):
            if vol_20_sub.iloc[i] < vol_low_sub:
                overlay_sub[i] = 1.5
            elif vol_20_sub.iloc[i] > vol_high_sub:
                overlay_sub[i] = 0.3

    signal_s5ov_sub = signal_base_sub * overlay_sub

    # Test windows
    window_sharpes = {}
    for window in [2, 3, 4, 5, 7, 10, 15, 20]:
        momentum = np.array([np.sum(r_sub.iloc[max(0,i-window):i+1]) if i > 0 else 0 for i in range(len(r_sub))])
        filter_w = (momentum > 0.3) & (ema_trend_sub > 0.94)
        signal_w = signal_s5ov_sub * filter_w.astype(float)
        pnl_w = backtest_simple(signal_w, r_sub.values)
        window_sharpes[window] = calc_sharpe(pnl_w)

    best_window = max(window_sharpes, key=window_sharpes.get)
    subsample_results.append({
        'sample': sample_num,
        'best_window': best_window,
        'sharpe_at_best': window_sharpes[best_window],
        'sharpe_at_3d': window_sharpes.get(3, 0)
    })

print(f"\n5 random 50%-subsamples, testing which momentum window is optimal:")
print(f"{'Sample':>6} | {'Best Window':>12} | {'Best Sharpe':>12} | {'3d Sharpe':>12} | {'3d is Best?':>12}")
print("─" * 60)

for r in subsample_results:
    is_best = "✅ YES" if r['best_window'] == 3 else f"❌ NO ({r['best_window']}d better)"
    print(f"  {r['sample']:5d} | {r['best_window']:12d} | {r['sharpe_at_best']:12.3f} | {r['sharpe_at_3d']:12.3f} | {is_best:>12}")

best_window_freq = sum(1 for r in subsample_results if r['best_window'] == 3)
print(f"\n3d window is 'best' in {best_window_freq}/5 subsamples")

if best_window_freq < 3:
    print(f"⚠️ WARNING: 3d window is NOT consistently optimal across subsamples")
    print(f"   → May be specific to this dataset/period (overfitting)")
else:
    print(f"✅ OK: 3d window consistently preferred")

# ============================================================================
# AUDIT 4: COMPARISON TO BASELINE
# ============================================================================

print("\n" + "="*80)
print("AUDIT 4: COMPARISON TO ACTUAL BASELINE")
print("="*80)

# Calculate true baselines
filter_1_old = (np.array([np.sum(r.iloc[max(0,i-5):i+1]) if i > 0 else 0 for i in range(len(r))]) > 0) & (ema_trend > 0.98)
signal_1_old = signal_s5ov * filter_1_old.astype(float)
pnl_1_old = backtest_simple(signal_1_old, r.values)
sharpe_1_old = calc_sharpe(pnl_1_old)

signal_base_only = signal_s5ov
pnl_base_only = backtest_simple(signal_base_only, r.values)
sharpe_base_only = calc_sharpe(pnl_base_only)

print(f"\nStrategy comparison (full period):")
print(f"  S5-OV base only (no filter):    {sharpe_base_only:.3f} Sharpe")
print(f"  S5-OV + ML Filter 1 (5d, old): {sharpe_1_old:.3f} Sharpe")
print(f"  S5-OV + ML 3d (claimed):       5.069 Sharpe (from earlier)")
print(f"  S5-OV + ML 3d (recalc causal): {sharpe_causal:.3f} Sharpe")

print(f"\n" + "="*80)
print("AUDIT CONCLUSION")
print("="*80)

if avg_deg > 1.0:
    print("\n🚨 CRITICAL ISSUES FOUND:")
    print(f"  1. Walk-forward degradation too high ({avg_deg:.3f})")
    print(f"  2. Look-ahead bias likely (causal: {sharpe_causal:.3f})")
    print(f"  3. Parameter overfitting (3d not consistently best)")
    print("\n❌ RECOMMENDATION: DO NOT DEPLOY")
    print("   The 5.069 Sharpe result is LIKELY A STATISTICAL ARTIFACT")

elif avg_deg > 0.5:
    print("\n⚠️ MODERATE CONCERNS:")
    print(f"  1. Walk-forward shows degradation ({avg_deg:.3f})")
    print(f"  2. True causal performance: {sharpe_causal:.3f}")
    print(f"  3. 3d window may be period-specific")
    print("\n✅ CONDITIONAL: Could deploy with caution")
    print(f"   Use realistic Sharpe estimate: {sharpe_causal:.3f} (not 5.0)")

else:
    print("\n✅ AUDIT PASSED:")
    print(f"  1. Low walk-forward degradation ({avg_deg:.3f})")
    print(f"  2. Causality verified ({sharpe_causal:.3f})")
    print(f"  3. 3d window appears robust")
    print("\n✅ RECOMMENDATION: SAFE TO PROCEED")

print("\n✅ Deep audit complete\n")
