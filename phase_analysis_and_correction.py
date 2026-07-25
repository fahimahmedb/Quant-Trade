#!/usr/bin/env python3
"""
PHASE 1: ANALYSIS & CORRECTION
===============================

Analyze all previous hypothesis results to identify:
  1. What works (and why)
  2. What doesn't work (and why)
  3. Small signals that hint at bigger patterns
  4. Derivative hypotheses to test next

This is the "correction phase" before final audit.
"""

import json
import pandas as pd
from pathlib import Path

print("\n" + "=" * 70)
print("PHASE 1: COMPREHENSIVE ANALYSIS OF ALL HYPOTHESES")
print("=" * 70)

# Load all results
results_dir = Path('results')

datasets = {
    'Classical Signals (H1-H6)': 'hypothesis_summary.json',
    'Unconventional Signals (R1-R10)': 'risky_hypotheses.json',
    'Ensemble Combinations': 'hypothesis_ensemble.json',
    'FracDiff Validation': 'fracdiff_validation.json',
    'Final Combo (Best)': 'final_combo_results.json',
}

all_results = {}

for name, filename in datasets.items():
    filepath = results_dir / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            all_results[name] = json.load(f)
        print(f"\n✓ Loaded: {name}")
    else:
        print(f"\n✗ Not found: {name}")

print("\n" + "=" * 70)
print("SECTION 1: RANKING ALL STRATEGIES")
print("=" * 70)

# Extract Sharpe ratios from all datasets
all_strategies = []

# Classical signals
for k, v in all_results['Classical Signals (H1-H6)'].items():
    if isinstance(v, dict) and 'sharpe' in v:
        all_strategies.append((k, v['sharpe'], 'Classical'))

# Unconventional signals
for k, v in all_results['Unconventional Signals (R1-R10)'].items():
    if isinstance(v, dict) and 'sharpe' in v:
        all_strategies.append((k, v['sharpe'], 'Unconventional'))

# Ensemble methods
ensemble_results = all_results['Ensemble Combinations']
if 'results' in ensemble_results:
    for k, v in ensemble_results['results'].items():
        all_strategies.append((k, v['sharpe'], 'Ensemble'))
else:
    for k, v in ensemble_results.items():
        if isinstance(v, dict) and 'sharpe' in v:
            all_strategies.append((k, v['sharpe'], 'Ensemble'))

# Final combo
final_results = all_results['Final Combo (Best)']
if 'results' in final_results:
    for k, v in final_results['results'].items():
        all_strategies.append((k, v['sharpe'], 'Final'))
else:
    for k, v in final_results.items():
        if isinstance(v, dict) and 'sharpe' in v:
            all_strategies.append((k, v['sharpe'], 'Final'))

# Sort by Sharpe
all_strategies.sort(key=lambda x: x[1], reverse=True)

print("\nRanking (Top 15):")
print(f"{'Rank':<5} {'Strategy':<30} {'Sharpe':>10} {'Type':<15}")
print("-" * 65)

for rank, (strategy, sharpe, type_) in enumerate(all_strategies[:15], 1):
    print(f"{rank:<5} {strategy:<30} {sharpe:>10.3f} {type_:<15}")

print("\n" + "=" * 70)
print("SECTION 2: PERFORMANCE PATTERNS & CLUSTERS")
print("=" * 70)

# Group by type
by_type = {}
for strategy, sharpe, type_ in all_strategies:
    if type_ not in by_type:
        by_type[type_] = []
    by_type[type_].append(sharpe)

print("\nPerformance by Category:")
for type_, sharpes in sorted(by_type.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
    avg = sum(sharpes) / len(sharpes)
    max_s = max(sharpes)
    min_s = min(sharpes)
    print(f"\n{type_}:")
    print(f"  Count: {len(sharpes)}")
    print(f"  Avg Sharpe: {avg:.3f}")
    print(f"  Best: {max_s:.3f}")
    print(f"  Worst: {min_s:.3f}")
    print(f"  Range: {max_s - min_s:.3f}")

print("\n" + "=" * 70)
print("SECTION 3: SMALL SIGNALS & CLUES")
print("=" * 70)

print("\n🔍 Key Observations:")

# 1. What beats BH?
bh_sharpe = 0.529
winners = [(s, sh) for s, sh, _ in all_strategies if sh > bh_sharpe]
print(f"\n1. WINNERS (beat BH sharpe={bh_sharpe:.3f}):")
for strategy, sharpe in winners:
    improvement = (sharpe - bh_sharpe) / bh_sharpe * 100
    print(f"   • {strategy}: {sharpe:.3f} (+{improvement:.1f}%)")

# 2. Biggest losers
losers = [(s, sh) for s, sh, _ in all_strategies if sh < -0.1]
print(f"\n2. BIG LOSERS (Sharpe < -0.1) - Learn what NOT to do:")
for strategy, sharpe in losers:
    print(f"   • {strategy}: {sharpe:.3f} (inverse might work?)")

# 3. Clustering: Classical vs Unconventional
classical_sharpes = [sh for s, sh, t in all_strategies if 'H' in s and 'H7' not in s]
risky_sharpes = [sh for s, sh, t in all_strategies if 'R' in s]

print(f"\n3. PARADIGM COMPARISON:")
print(f"   Classical (H1-H6):")
print(f"     Avg: {sum(classical_sharpes)/len(classical_sharpes):.3f}")
print(f"     All < BH? {all(sh < bh_sharpe for sh in classical_sharpes)}")
print(f"\n   Unconventional (R1-R10):")
print(f"     Avg: {sum(risky_sharpes)/len(risky_sharpes):.3f}")
print(f"     Winners: {sum(1 for sh in risky_sharpes if sh > bh_sharpe)}/10")

# 4. Momentum vs Mean Reversion in classical
momentum_sharpe = all_results['Classical Signals (H1-H6)'].get('H2_Momentum', {}).get('sharpe', 0)
mean_rev_sharpe = all_results['Classical Signals (H1-H6)'].get('H1_MeanReversion', {}).get('sharpe', 0)

print(f"\n4. MOMENTUM vs MEAN REVERSION (Classical):")
print(f"   Momentum (H2): {momentum_sharpe:.3f}")
print(f"   Mean Reversion (H1): {mean_rev_sharpe:.3f}")
print(f"   Winner: {'Momentum' if momentum_sharpe > mean_rev_sharpe else 'Mean Reversion'}")
print(f"   Insight: Both weak, but {('Momentum' if momentum_sharpe > mean_rev_sharpe else 'Mean Reversion').upper()} slightly better")

# 5. FracDiff + Multiframe = best ensemble
print(f"\n5. ENSEMBLE INSIGHTS:")
print(f"   Best: R5R6_Average (Sharpe 0.676)")
print(f"   Components:")
print(f"     - R5_FracDiff: {all_results['Unconventional Signals (R1-R10)'].get('R5_FracDiff', {}).get('sharpe', 0):.3f}")
print(f"     - R6_Multiframe: {all_results['Unconventional Signals (R1-R10)'].get('R6_Multiframe', {}).get('sharpe', 0):.3f}")
print(f"   Insight: Combination of tactical (R5) + strategic (R6) = best of both worlds")

print("\n" + "=" * 70)
print("SECTION 4: DERIVATIVE HYPOTHESES (CORRECTION PHASE)")
print("=" * 70)

print("""
Based on analysis, propose H8-H12 to test in PHASE 2:

H8: FRACTIONAL DIFF TUNING
   What: Test fractional diff with DIFFERENT orders (0.3, 0.5, 0.7)
   Why: Parameter plateau exists 0.2-0.6, but test edges
   Insight: FracDiff is best unconventional signal, maybe deeper tuning helps

H9: MOMENTUM + TREND FILTER
   What: H2_Momentum (0.308) filtered by R6_Multiframe trend
   Why: Momentum weak alone, but trend filter (R6) might improve it
   Insight: Combining weak signal + strong filter could boost
   Expected: Sharpe 0.35-0.40 (better than H2's 0.308)

H10: MEAN REVERSION IN LOW-VOL
   What: H1_MeanReversion (RSI) but ONLY trade in vol tercile 1 (low vol)
   Why: Mean reversion works best in calm markets, not extreme vol
   Insight: Regime-aware trading (done partially in H3, but not well)
   Expected: Sharpe 0.25-0.35 (better than H1's 0.213)

H11: FRACTAL STRUCTURE (Price Action)
   What: Detect 3-bar patterns (HHH, LLL, HL, LH patterns)
   Why: Unconventional but not tested yet. Fractals reveal hidden structure
   Insight: Price patterns that don't require indicators
   Expected: Sharpe 0.40-0.50 (alternative to FracDiff)

H12: VOLATILITY-ADJUSTED FRACTIONAL DIFF
   What: R5_FracDiff but scale exposure by inverse volatility
   Why: FracDiff has high MDD, but vol adjustment (like Phase D) helps
   Insight: Combine best signal (FracDiff) with risk control (vol targeting)
   Expected: Sharpe 0.55+ with MDD reduction to -100

Action Plan:
  1. Code H8-H12 with focus on developing logic (not concise)
  2. Run all 5 in parallel
  3. Compare to existing results
  4. Identify which deserve deeper iteration
  5. Do CORRECTION PHASE (iterate on best performers)
  6. Final AUDIT on all results
""")

print("\n" + "=" * 70)
print("KEY INSIGHTS FOR CORRECTION")
print("=" * 70)

print("""
✓ What Works:
  - Unconventional > Classical (mean unconventional sharpe beats classical)
  - Ensemble > Single signal (R5R6 0.676 >> R5 0.534)
  - Risk control matters (MDD reduction is valuable in production)
  - Parameter stability = real edge (not lucky spike)

✗ What Doesn't:
  - Classical TA (all H1-H6 underperform BH)
  - Too complex (consensus voting worse than average)
  - Vol-based signals alone (R3 vol jump = -0.034)
  - Contrarian inverse (R1 = -0.309, worst)

? Unexplored:
  - LSTM would help (but TF not available, use alternative)
  - Deep indicator combinations (H7 attempted but failed on env)
  - Adaptive parameters (fix at optimal, don't adapt)
  - Cross-asset regime correlation (only NASDAQ tested)

Next move: CODE & TEST H8-H12 with proper development time.
""")

print("\n✅ Analysis complete. Ready for PHASE 2 (Derivative Hypotheses)\n")
