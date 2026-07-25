#!/usr/bin/env python3
"""
PHASE 2: RUN DERIVATIVE HYPOTHESES (H8-H12)
=============================================

Launch all 5 derivative hypotheses in parallel, then analyze results
and prepare for final comprehensive audit.
"""

import subprocess
import json
import time
from pathlib import Path

print("\n" + "=" * 70)
print("PHASE 2: DERIVATIVE HYPOTHESIS TESTING (H8-H12)")
print("=" * 70)

HYPOTHESES = [
    ("H8", "finance/trading/scripts/run_hypothesis_8_fracdiff_tuning.py", "results/hypothesis_8_fracdiff_tuning.json"),
    ("H9", "finance/trading/scripts/run_hypothesis_9_momentum_filter.py", "results/hypothesis_9_momentum_filter.json"),
    ("H10", "finance/trading/scripts/run_hypothesis_10_mean_reversion_lowvol.py", "results/hypothesis_10_mean_reversion_lowvol.json"),
    ("H11", "finance/trading/scripts/run_hypothesis_11_fractal_patterns.py", "results/hypothesis_11_fractal_patterns.json"),
    ("H12", "finance/trading/scripts/run_hypothesis_12_vol_adjusted_fracdiff.py", "results/hypothesis_12_vol_adjusted_fracdiff.json"),
]

print("\n🚀 LAUNCHING ALL 5 HYPOTHESES IN PARALLEL...")
print("-" * 70)

processes = []
data_path = "data/nasdaq100_daily.txt"

for name, script, output in HYPOTHESES:
    print(f"[{name}] Launching {script.split('/')[-1]}...")
    proc = subprocess.Popen(
        ["python3", script, data_path, output],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes.append((name, proc, output))

print("\n⏳ WAITING FOR COMPLETION...")
print("-" * 70)

# Wait for all to complete
start_time = time.time()
timeout = 600  # 10 minutes

results_h8h12 = {}

while len(results_h8h12) < len(processes):
    elapsed = time.time() - start_time
    if elapsed > timeout:
        print(f"\n⚠️  TIMEOUT ({timeout}s) reached!")
        break

    for name, proc, output in processes:
        if name not in results_h8h12:
            if proc.poll() is not None:  # Process finished
                stdout, stderr = proc.communicate()

                # Try to read result
                if Path(output).exists():
                    try:
                        with open(output, 'r') as f:
                            result = json.load(f)
                            results_h8h12[name] = result
                            sharpe = result.get('sharpe') or result.get('best_sharpe') or result.get('vol_adjusted', {}).get('sharpe')
                            print(f"✅ {name}: Complete (Sharpe {sharpe:.3f})")
                    except Exception as e:
                        print(f"⚠️  {name}: Failed to read results ({e})")
                        results_h8h12[name] = {'error': str(e)}
                else:
                    print(f"⚠️  {name}: No output file")
                    results_h8h12[name] = {'error': 'No output file'}

    time.sleep(2)

print("\n" + "=" * 70)
print("PHASE 2 RESULTS: DERIVATIVE HYPOTHESES (H8-H12)")
print("=" * 70)

# Extract and rank
rankings = []

for h_name, result in sorted(results_h8h12.items()):
    if 'error' in result:
        print(f"\n{h_name}: ERROR - {result['error']}")
        continue

    # Extract sharpe (different formats)
    sharpe = None
    if 'sharpe' in result:
        sharpe = result['sharpe']
    elif 'best_sharpe' in result:
        sharpe = result['best_sharpe']
    elif 'vol_adjusted' in result:
        sharpe = result['vol_adjusted'].get('sharpe')

    if sharpe is not None:
        rankings.append((h_name, sharpe))
        mdd = None
        if 'mdd' in result:
            mdd = result['mdd']
        elif 'best_mdd' in result:
            mdd = result['best_mdd']
        elif 'vol_adjusted' in result:
            mdd = result['vol_adjusted'].get('mdd')

        print(f"\n{h_name}: {result.get('hypothesis', 'Unknown')}")
        print(f"  Sharpe: {sharpe:.3f}")
        if mdd:
            print(f"  MDD: {mdd:.1f}")

# Ranking
rankings.sort(key=lambda x: x[1], reverse=True)

print("\n" + "=" * 70)
print("H8-H12 RANKING")
print("=" * 70)

print(f"\n{'Rank':<5} {'Hypothesis':<15} {'Sharpe':>10}")
print("-" * 35)

for rank, (name, sharpe) in enumerate(rankings, 1):
    print(f"{rank:<5} {name:<15} {sharpe:>10.3f}")

# Compare to baselines
print("\n" + "=" * 70)
print("COMPARISON TO PREVIOUS BEST")
print("=" * 70)

baselines = {
    'BH': 0.529,
    'R5_FracDiff': 0.534,
    'R5R6_Average': 0.676,
}

if rankings:
    best_h812 = rankings[0][1]
    print(f"\nBest from H8-H12: {best_h812:.3f}")
    print(f"vs Buy&Hold: {best_h812 - baselines['BH']:+.3f}")
    print(f"vs R5_FracDiff: {best_h812 - baselines['R5_FracDiff']:+.3f}")
    print(f"vs R5R6_Average: {best_h812 - baselines['R5R6_Average']:+.3f}")

    if best_h812 > baselines['R5R6_Average']:
        print("\n🏆 NEW CHAMPION! H8-H12 beats R5R6_Average!")
    elif best_h812 > baselines['R5_FracDiff']:
        print(f"\n✓ H8-H12 improved on single signals")
    else:
        print(f"\n⚠️  H8-H12 couldn't beat existing best")

# Save summary
summary = {
    'phase': '2_derivative_hypotheses',
    'h8h12_results': results_h8h12,
    'ranking': rankings,
    'best': {'hypothesis': rankings[0][0], 'sharpe': rankings[0][1]} if rankings else None,
    'baselines': baselines
}

with open('results/phase2_derivative_summary.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print(f"\n✅ Phase 2 summary saved → results/phase2_derivative_summary.json")
print("\nNext: PHASE 3 - COMPREHENSIVE AUDIT\n")
