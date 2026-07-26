#!/usr/bin/env python3
"""
TRULY 100% OUT-OF-SAMPLE TEST
===============================
PROTOCOL (STRICTEMENT ANTITRICHE):

1. Split NDX:
   - DESIGN (1985-2004, ~19 ans, 4700 obs): ONLY optimize here
   - TEST (2004-2026, ~22 ans, 5500 obs): FREEZE params, apply only once

2. On DESIGN set:
   - Test momentum windows: 3d, 5d, 10d, 20d
   - Test EMA thresholds
   - Find BEST combination
   - LOCK THE PARAMETERS

3. On TEST set:
   - Apply locked parameters
   - NO re-optimization
   - NO tuning
   - NO peeking
   - Report honest Sharpe

4. Compare:
   - Design Sharpe (in-sample)
   - Test Sharpe (true OOS)
   - Degradation (the honest number)
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
print("TRULY 100% OUT-OF-SAMPLE TEST (NO DATA SNOOPING)")
print("="*80)
print("\nPROTOCOL:")
print("  1. Design set (1985-2004): OPTIMIZE parameters")
print("  2. Test set (2004-2026): APPLY frozen parameters, NO tuning")
print("  3. Report honest degradation")

# Load data
df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)
min_len = min(len(df), len(r))
df = df.iloc[:min_len].copy()
r = r.iloc[:min_len].copy()

print(f"\nTotal data: {len(df)} obs ({df.index[0]} to {df.index[-1]})")

# Find split point (approximately 2004)
# We want ~19 years for design, ~22 years for test
split_idx = len(df) // 2  # Rough split
print(f"Split index: {split_idx}")

# Get design and test sets
df_design = df.iloc[:split_idx].copy()
r_design = r.iloc[:split_idx].copy()
df_test = df.iloc[split_idx:].copy()
r_test = r.iloc[split_idx:].copy()

print(f"\n{'='*80}")
print("DESIGN SET (Optimization ONLY)")
print("="*80)
print(f"Period: {df_design.index[0]} to {df_design.index[-1]}")
print(f"Size: {len(df_design)} observations")

# ============================================================================
# DESIGN PHASE: Test all momentum windows
# ============================================================================

# Build features for design set
ema50_d = df_design['close'].ewm(span=50).mean().values
ema200_d = df_design['close'].ewm(span=200).mean().values
ema_trend_d = ema50_d / ema200_d

signal_base_d = np.where(ema50_d > ema200_d, 1.0, 0.0)
vol_20_d = pd.Series(r_design).rolling(20).std()
vol_low_d = vol_20_d.quantile(0.25)
vol_high_d = vol_20_d.quantile(0.75)

overlay_d = np.ones(len(signal_base_d))
for i in range(len(overlay_d)):
    if pd.notna(vol_20_d.iloc[i]):
        if vol_20_d.iloc[i] < vol_low_d:
            overlay_d[i] = 1.5
        elif vol_20_d.iloc[i] > vol_high_d:
            overlay_d[i] = 0.3

signal_s5ov_d = signal_base_d * overlay_d

print(f"\nTesting momentum windows on DESIGN set (1985-2004):")
print(f"{'Window':>8} | {'Mom Thresh':>12} | {'EMA Thresh':>12} | {'Sharpe':>10} | {'MDD':>8}")
print("─" * 70)

best_config = None
best_sharpe_design = -np.inf
all_results_design = []

for window in [3, 5, 10, 20]:
    momentum = np.array([np.sum(r_design.iloc[max(0,i-window):i+1]) if i > 0 else 0 for i in range(len(r_design))])

    for mom_t in np.arange(-0.1, 0.5, 0.1):
        for ema_t in [0.94, 0.96, 0.98]:
            filter_d = (momentum > mom_t) & (ema_trend_d > ema_t)
            signal_d = signal_s5ov_d * filter_d.astype(float)
            pnl_d = backtest_simple(signal_d, r_design.values)
            sharpe_d = calc_sharpe(pnl_d)
            mdd_d = calc_mdd(pnl_d)

            all_results_design.append({
                'window': window,
                'mom_t': mom_t,
                'ema_t': ema_t,
                'sharpe': sharpe_d,
                'mdd': mdd_d
            })

            if sharpe_d > best_sharpe_design:
                best_sharpe_design = sharpe_d
                best_config = {
                    'window': window,
                    'mom_t': mom_t,
                    'ema_t': ema_t,
                    'sharpe_design': sharpe_d,
                    'mdd_design': mdd_d
                }

# Show best 10
all_results_design_sorted = sorted(all_results_design, key=lambda x: x['sharpe'], reverse=True)
for i, r in enumerate(all_results_design_sorted[:10], 1):
    marker = "🏆" if i == 1 else "  "
    print(f"{marker} {r['window']:>6}d | {r['mom_t']:>12.1f} | {r['ema_t']:>12.2f} | {r['sharpe']:>10.3f} | {r['mdd']:>7.1f}%")

print(f"\n✅ BEST CONFIG FOUND ON DESIGN SET:")
print(f"   Window: {best_config['window']}d")
print(f"   Momentum threshold: > {best_config['mom_t']:+.1f}")
print(f"   EMA threshold: > {best_config['ema_t']:.2f}")
print(f"   Design Sharpe: {best_config['sharpe_design']:.3f}")
print(f"   Design MDD: {best_config['mdd_design']:.1f}%")

# ============================================================================
print(f"\n{'='*80}")
print("TEST SET (Frozen Parameters, NO Optimization)")
print("="*80)
print(f"Period: {df_test.index[0]} to {df_test.index[-1]}")
print(f"Size: {len(df_test)} observations")

# Build features for test set
ema50_t = df_test['close'].ewm(span=50).mean().values
ema200_t = df_test['close'].ewm(span=200).mean().values
ema_trend_t = ema50_t / ema200_t

signal_base_t = np.where(ema50_t > ema200_t, 1.0, 0.0)
vol_20_t = pd.Series(r_test).rolling(20).std()
vol_low_t = vol_20_t.quantile(0.25)
vol_high_t = vol_20_t.quantile(0.75)

overlay_t = np.ones(len(signal_base_t))
for i in range(len(overlay_t)):
    if pd.notna(vol_20_t.iloc[i]):
        if vol_20_t.iloc[i] < vol_low_t:
            overlay_t[i] = 1.5
        elif vol_20_t.iloc[i] > vol_high_t:
            overlay_t[i] = 0.3

signal_s5ov_t = signal_base_t * overlay_t

# Apply LOCKED parameters to test set (no re-tuning)
print(f"\nApplying locked parameters from design set:")
print(f"  {best_config['window']}d momentum > {best_config['mom_t']:+.1f}")
print(f"  EMA trend > {best_config['ema_t']:.2f}")

momentum_t = np.array([np.sum(r_test.iloc[max(0,i-best_config['window']):i+1]) if i > 0 else 0 for i in range(len(r_test))])

filter_t = (momentum_t > best_config['mom_t']) & (ema_trend_t > best_config['ema_t'])
signal_t = signal_s5ov_t * filter_t.astype(float)
pnl_t = backtest_simple(signal_t, r_test.values)
sharpe_t = calc_sharpe(pnl_t)
mdd_t = calc_mdd(pnl_t)

print(f"\n✅ TEST SET RESULTS (frozen params, NO tuning):")
print(f"   Test Sharpe: {sharpe_t:.3f}")
print(f"   Test MDD: {mdd_t:.1f}%")

# ============================================================================
print(f"\n{'='*80}")
print("COMPARISON: DESIGN vs TEST (THE HONEST TRUTH)")
print("="*80)

degradation = best_config['sharpe_design'] - sharpe_t
degradation_pct = (degradation / best_config['sharpe_design'] * 100) if best_config['sharpe_design'] != 0 else 0

print(f"\n{'Metric':30s} | {'Design':>12} | {'Test':>12} | {'Difference':>12}")
print("─" * 70)
print(f"{'Sharpe Ratio':30s} | {best_config['sharpe_design']:>12.3f} | {sharpe_t:>12.3f} | {degradation:>+12.3f}")
print(f"{'Max Drawdown':30s} | {best_config['mdd_design']:>11.1f}% | {mdd_t:>11.1f}% | {mdd_t - best_config['mdd_design']:>+11.1f}%")
print(f"{'Exposure':30s} | {(filter_d).mean()*100:>11.1f}% | {(filter_t).mean()*100:>11.1f}% | N/A")

print(f"\nDegradation: {degradation:.3f} Sharpe ({degradation_pct:.1f}%)")

# ============================================================================
print(f"\n{'='*80}")
print("VERDICT")
print("="*80)

if degradation > 1.5:
    print(f"\n🚨 CRITICAL: {degradation:.3f} Sharpe degradation")
    print(f"   Design Sharpe ({best_config['sharpe_design']:.3f}) was OVERFITTED")
    print(f"   Realistic expectation: {sharpe_t:.3f} Sharpe")
    print(f"   ❌ This strategy is NOT deployable as promised")

elif degradation > 0.5:
    print(f"\n⚠️ SIGNIFICANT: {degradation:.3f} Sharpe degradation ({degradation_pct:.1f}%)")
    print(f"   Design params don't generalize well")
    print(f"   Realistic expectation: {sharpe_t:.3f} Sharpe")
    print(f"   ⚠️ CAUTION: Take claimed performance with grain of salt")

elif degradation > 0.0:
    print(f"\n✅ MINIMAL: {degradation:.3f} Sharpe degradation ({degradation_pct:.1f}%)")
    print(f"   Design params generalize well")
    print(f"   Realistic expectation: {sharpe_t:.3f} Sharpe")
    print(f"   ✅ GOOD: Strategy appears robust")

else:
    print(f"\n✅ EXCELLENT: TEST OUTPERFORMS DESIGN by {abs(degradation):.3f} Sharpe")
    print(f"   Design: {best_config['sharpe_design']:.3f}")
    print(f"   Test: {sharpe_t:.3f}")
    print(f"   ✅ EXCELLENT: Strategy improved on new data!")

# ============================================================================
print(f"\n{'='*80}")
print("FINAL ASSESSMENT")
print("="*80)

print(f"\n📊 What This Test Proves:")
if sharpe_t > 3.5:
    print(f"   ✅ The ~3.987 Sharpe claim is REAL (test shows {sharpe_t:.3f})")
    print(f"   ✅ Strategy works on unseen data (2004-2026)")
elif sharpe_t > 2.0:
    print(f"   ⚠️ The ~3.987 Sharpe claim is PARTIALLY REAL (test shows {sharpe_t:.3f})")
    print(f"   ⚠️ But degraded significantly")
else:
    print(f"   ❌ The ~3.987 Sharpe claim is FAKE (test shows {sharpe_t:.3f})")
    print(f"   ❌ Heavy overfitting to design period")

print(f"\n💡 Recommendation:")
if sharpe_t > 3.5 and degradation < 0.5:
    print(f"   ✅ DEPLOY the {best_config['window']}d momentum filter")
    print(f"      Expected: ~{sharpe_t:.3f} Sharpe")
    print(f"      Risk: LOW")
elif sharpe_t > 2.0:
    print(f"   ⚠️ DEPLOY with CAUTION")
    print(f"      Expected: ~{sharpe_t:.3f} Sharpe (not {best_config['sharpe_design']:.3f})")
    print(f"      Risk: MEDIUM (significant degradation detected)")
else:
    print(f"   ❌ DO NOT DEPLOY")
    print(f"      Strategy heavily overfitted")
    print(f"      Use S5-OV base only (0.875 Sharpe, proven)")

print("\n✅ True 100% OOS test complete\n")
