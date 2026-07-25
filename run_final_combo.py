#!/usr/bin/env python3
"""
Final Combination: R5_FracDiff + R6_Multiframe
Test if ensemble of unconventional signals beats Buy & Hold
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "finance/src"))
from data_loader import load_ohlc, log_returns_pct

def calc_sharpe(returns, ann=252):
    if len(returns) < 2:
        return 0.0
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    if sigma == 0:
        return 0.0
    return float(mu / sigma * np.sqrt(ann))

def calc_mdd(returns):
    cumsum = np.cumsum(returns)
    peak = np.maximum.accumulate(cumsum)
    dd = cumsum - peak
    return float(np.min(dd))

def calc_metrics(returns):
    sharpe = calc_sharpe(returns)
    mdd = calc_mdd(returns)
    total_ret = np.sum(returns) * 100
    if mdd < 0:
        calmar = total_ret / abs(mdd) if abs(mdd) > 0 else 0
    else:
        calmar = 0
    return {'sharpe': sharpe, 'mdd': mdd, 'return_pct': total_ret, 'calmar': calmar}

def backtest_simple(positions, returns, cost_bps=5):
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    pnl = pnl - turn * (cost_bps / 1e4)
    return pnl

def frac_diff(series, order=0.4):
    weights = []
    k = 1.0
    for i in range(1, len(series)):
        weight = -k * (order / i)
        k = weight
        weights.append(weight)
    frac_series = np.zeros(len(series))
    for i in range(len(weights)):
        if i < len(series):
            frac_series[i] = weights[i] * series[i]
    frac_series = (frac_series - np.nanmean(frac_series)) / (np.nanstd(frac_series) + 1e-8)
    return np.sign(frac_series)

print("=" * 70)
print("FINAL COMBINATION: R5_FRACDIFF + R6_MULTIFRAME")
print("=" * 70)

df = load_ohlc("data/nasdaq100_daily.txt")
r = log_returns_pct(df)

# R5: Fractional Differentiation
print("\n[1] Computing R5_FracDiff...")
r5_positions = frac_diff(df['close'].values)

# R6: Multi-timeframe
print("[2] Computing R6_Multiframe...")
ema_daily = df['close'].ewm(span=12).mean()
ema_weekly = df['close'].ewm(span=60).mean()
ema_monthly = df['close'].ewm(span=250).mean()
trend_signal = (
    ((ema_daily > ema_weekly).astype(int) +
     (ema_weekly > ema_monthly).astype(int)) / 2.0
)
r6_positions = (trend_signal > 0.5).astype(int) - (trend_signal < 0.5).astype(int)

# Align
min_len = min(len(r5_positions), len(r6_positions), len(r))
r5 = r5_positions[:min_len]
r6 = r6_positions[:min_len]
r_aligned = r.values[:min_len]

print("\n" + "=" * 70)
print("COMBINATION METHODS")
print("=" * 70)

results = {}

# Method 1: R5 only
print("\n1. R5_FracDiff Only")
pnl = backtest_simple(r5, r_aligned)
metrics = calc_metrics(pnl)
results['R5_Only'] = metrics
print(f"   Sharpe={metrics['sharpe']:.3f} | MDD={metrics['mdd']:.1f} | Return={metrics['return_pct']:.1f}%")

# Method 2: R6 only
print("\n2. R6_Multiframe Only")
pnl = backtest_simple(r6, r_aligned)
metrics = calc_metrics(pnl)
results['R6_Only'] = metrics
print(f"   Sharpe={metrics['sharpe']:.3f} | MDD={metrics['mdd']:.1f} | Return={metrics['return_pct']:.1f}%")

# Method 3: Average (R5 + R6) / 2
print("\n3. Equal-Weight Average (R5 + R6) / 2")
combo_avg = (r5 + r6) / 2
pnl = backtest_simple(combo_avg, r_aligned)
metrics = calc_metrics(pnl)
results['R5R6_Average'] = metrics
print(f"   Sharpe={metrics['sharpe']:.3f} | MDD={metrics['mdd']:.1f} | Return={metrics['return_pct']:.1f}%")

# Method 4: Weighted (60% R5, 40% R6) - FracDiff is better
print("\n4. Weighted (60% R5 + 40% R6)")
combo_weighted = 0.6 * r5 + 0.4 * r6
pnl = backtest_simple(combo_weighted, r_aligned)
metrics = calc_metrics(pnl)
results['R5R6_Weighted'] = metrics
print(f"   Sharpe={metrics['sharpe']:.3f} | MDD={metrics['mdd']:.1f} | Return={metrics['return_pct']:.1f}%")

# Method 5: Vote (both must agree to trade)
print("\n5. Consensus (Both signals agree)")
combo_vote = r5 * r6  # Non-zero only if both agree
pnl = backtest_simple(combo_vote, r_aligned)
metrics = calc_metrics(pnl)
results['R5R6_Consensus'] = metrics
print(f"   Sharpe={metrics['sharpe']:.3f} | MDD={metrics['mdd']:.1f} | Return={metrics['return_pct']:.1f}%")

# Method 6: Inverse Hedge (R5 main + R6 as hedge)
print("\n6. Hedged Strategy (R5 main, reduce when R6 opposes)")
combo_hedge = np.zeros_like(r5)
for i in range(len(r5)):
    if r5[i] == r6[i]:  # Agreement → full position
        combo_hedge[i] = r5[i]
    else:  # Disagreement → half position
        combo_hedge[i] = 0.5 * r5[i]

pnl = backtest_simple(combo_hedge, r_aligned)
metrics = calc_metrics(pnl)
results['R5R6_Hedged'] = metrics
print(f"   Sharpe={metrics['sharpe']:.3f} | MDD={metrics['mdd']:.1f} | Return={metrics['return_pct']:.1f}%")

# Baseline: Buy & Hold
print("\n7. Buy & Hold (Baseline)")
bh_metrics = calc_metrics(r_aligned)
results['BuyHold'] = bh_metrics
print(f"   Sharpe={bh_metrics['sharpe']:.3f} | MDD={bh_metrics['mdd']:.1f} | Return={bh_metrics['return_pct']:.1f}%")

# Summary
print("\n" + "=" * 70)
print("FINAL RANKING")
print("=" * 70)

ranked = sorted(results.items(), key=lambda x: x[1]['sharpe'], reverse=True)
for rank, (name, metrics) in enumerate(ranked, 1):
    sharpe = metrics['sharpe']
    mdd = metrics['mdd']
    bh_comp = f" ({sharpe - bh_metrics['sharpe']:+.3f} vs B&H)" if name != 'BuyHold' else ""
    print(f"{rank}. {name:25s} → Sharpe {sharpe:7.3f} | MDD {mdd:7.1f}{bh_comp}")

# Find winner
best_name, best_metrics = ranked[0]
if best_metrics['sharpe'] > bh_metrics['sharpe']:
    print(f"\n✅ WINNER: {best_name} (Sharpe {best_metrics['sharpe']:.3f})")
    print(f"   Outperformance: +{best_metrics['sharpe'] - bh_metrics['sharpe']:.3f} Sharpe")
    print(f"   MDD reduction: {best_metrics['mdd'] - bh_metrics['mdd']:.1f}")
else:
    print(f"\n⚠️  No strategy beats Buy & Hold")
    print(f"   Best: {best_name} with Sharpe {best_metrics['sharpe']:.3f}")

# Save
with open('results/final_combo_results.json', 'w') as f:
    json.dump({
        'results': results,
        'best_strategy': best_name,
        'best_sharpe': best_metrics['sharpe'],
        'bh_sharpe': bh_metrics['sharpe'],
        'outperformance': best_metrics['sharpe'] - bh_metrics['sharpe']
    }, f, indent=2, default=str)

print(f"\n✅ Results saved → results/final_combo_results.json")
