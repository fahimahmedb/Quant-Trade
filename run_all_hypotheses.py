#!/usr/bin/env python3
"""
Master Orchestrator: Launch all 6 hypothesis tests in parallel
Then consolidate results + ensemble voting
"""
import subprocess
import json
import numpy as np
import pandas as pd
from pathlib import Path
import time

SCRIPTS = [
    "finance/trading/scripts/run_hypothesis_1_technical_ensemble.py",
    "finance/trading/scripts/run_hypothesis_2_regime_mean_reversion.py",
    "finance/trading/scripts/run_hypothesis_3_deep_learning_attention.py",
    "finance/trading/scripts/run_hypothesis_4_gradient_boosting_ensemble.py",
    "finance/trading/scripts/run_hypothesis_5_sentiment_multimodal.py",
    "finance/trading/scripts/run_hypothesis_6_reinforcement_learning.py",
]

OUTPUT_FILES = [
    "results/hypothesis_1.json",
    "results/hypothesis_2.json",
    "results/hypothesis_3.json",
    "results/hypothesis_4.json",
    "results/hypothesis_5.json",
    "results/hypothesis_6.json",
]

DATA_PATH = "data/nasdaq100_daily.txt"

def launch_all_hypotheses():
    """Launch all 6 scripts in background"""
    print("🚀 LAUNCHING ALL HYPOTHESES IN PARALLEL")
    print("=" * 60)

    processes = []
    for i, script in enumerate(SCRIPTS):
        print(f"[{i+1}] Launching {script.split('_')[-1].split('.')[0]}...")
        proc = subprocess.Popen(
            ["python3", script, DATA_PATH, OUTPUT_FILES[i]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append((i+1, proc, OUTPUT_FILES[i]))

    return processes

def wait_and_consolidate(processes, timeout=3600):
    """Wait for all processes + consolidate results"""
    print("\n⏳ WAITING FOR COMPLETION...")
    print("=" * 60)

    results = {}
    completed = []
    start_time = time.time()

    while len(completed) < len(processes):
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(f"❌ TIMEOUT ({timeout}s) reached!")
            for h, proc, _ in processes:
                if proc.poll() is None:
                    proc.terminate()
            break

        for h, proc, output_file in processes:
            if h not in completed:
                if proc.poll() is not None:  # Process finished
                    completed.append(h)
                    stdout, stderr = proc.communicate()

                    # Try to read result
                    if Path(output_file).exists():
                        try:
                            with open(output_file, 'r') as f:
                                result = json.load(f)
                                results[h] = result
                                print(f"✅ Hypothesis {h}: {result.get('hypothesis', 'Unknown')}")
                                print(f"   Sharpe: {result.get('Sharpe_OOS', 'N/A'):.3f}")
                        except Exception as e:
                            print(f"⚠️  Hypothesis {h}: Failed to read results ({e})")
                    else:
                        print(f"⚠️  Hypothesis {h}: No output file")

        time.sleep(5)

    return results

def ensemble_vote(results):
    """Combine best hypotheses via ensemble voting"""
    print("\n📊 ENSEMBLE VOTING & COMBINATION")
    print("=" * 60)

    # Rank by Sharpe
    ranked = sorted(results.items(), key=lambda x: x[1].get('Sharpe_OOS', -999), reverse=True)

    print("\nRanking by Sharpe (OOS):")
    for rank, (h, res) in enumerate(ranked, 1):
        sharpe = res.get('Sharpe_OOS', -999)
        dsr = res.get('DSR', -999)
        print(f"{rank}. H{h}: {res.get('hypothesis', '?')[:40]:40s} | Sharpe={sharpe:7.3f} | DSR={dsr:7.3f}")

    # Top 2-3 to combine
    top_n = min(3, len(ranked))
    top_hypotheses = [h for h, _ in ranked[:top_n]]

    print(f"\n🎯 TOP {top_n} TO COMBINE:")
    for i, h in enumerate(top_hypotheses, 1):
        res = results[h]
        print(f"  {i}. H{h}: {res.get('hypothesis', '?')} (Sharpe={res.get('Sharpe_OOS', 0):.3f})")

    summary = {
        'all_results': results,
        'ranking': [{'rank': r, 'hypothesis': h, 'sharpe': results[h].get('Sharpe_OOS', -999)} for r, (h, _) in enumerate(ranked, 1)],
        'top_candidates_for_ensemble': top_hypotheses
    }

    return summary, top_hypotheses

def main():
    print("\n" + "=" * 60)
    print("QUANT-TRADE: MULTI-HYPOTHESIS PARALLEL TESTING")
    print("=" * 60)

    # Launch
    processes = launch_all_hypotheses()

    # Wait & consolidate
    results = wait_and_consolidate(processes)

    # Ensemble voting
    summary, top = ensemble_vote(results)

    # Save summary
    with open('results/hypothesis_ensemble_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n✅ COMPLETE. Summary saved → results/hypothesis_ensemble_summary.json")
    print(f"   Top candidates for combination: H{', H'.join(map(str, top))}")

if __name__ == '__main__':
    main()
