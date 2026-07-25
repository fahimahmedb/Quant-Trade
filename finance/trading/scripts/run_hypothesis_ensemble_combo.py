#!/usr/bin/env python3
"""
Ensemble Combination: Use top 3 hypotheses + vote/stack for final signal
This tests if combination > individual (synergy effect)
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_loader import load_ohlc, log_returns_pct
from prediction import backtest, trading_metrics, dsr

def run_ensemble_combo(predictions_h1, predictions_h2, predictions_h3, data_path, output_path):
    """
    Combine 3 hypothesis predictions via:
    1. Simple average vote
    2. Logistic regression meta-model (if available)
    """
    print("[ENSEMBLE] Combining top 3 hypotheses...")

    df_raw = load_ohlc(data_path)
    r = log_returns_pct(df_raw)

    # Align prediction lengths
    min_len = min(len(predictions_h1), len(predictions_h2), len(predictions_h3), len(r))
    h1 = np.array(predictions_h1[:min_len])
    h2 = np.array(predictions_h2[:min_len])
    h3 = np.array(predictions_h3[:min_len])
    r_fwd = r.values[:min_len]

    # Method 1: Simple average
    ensemble_avg = (h1 + h2 + h3) / 3.0
    positions_avg = ensemble_avg >= 0.5

    bt_avg = backtest(positions_avg, r_fwd, cost_bps=5, delay=1)
    tm_avg = trading_metrics(bt_avg, r_fwd)

    # Method 2: Weighted average (by DSR or Sharpe)
    # Placeholder weights (should come from hypothesis results)
    weights = np.array([0.4, 0.35, 0.25])
    ensemble_weighted = h1 * weights[0] + h2 * weights[1] + h3 * weights[2]
    positions_weighted = ensemble_weighted >= 0.5

    bt_weighted = backtest(positions_weighted, r_fwd, cost_bps=5, delay=1)
    tm_weighted = trading_metrics(bt_weighted, r_fwd)

    dsr_avg = dsr(tm_avg['Sharpe'], 3, len(r_fwd))
    dsr_weighted = dsr(tm_weighted['Sharpe'], 3, len(r_fwd))

    results = {
        'ensemble_type': 'Top 3 Combination',
        'method_simple_average': {
            'Sharpe_OOS': float(tm_avg['Sharpe']),
            'Calmar': float(tm_avg['Calmar']),
            'MDD': float(tm_avg['MDD']),
            'Return': float(tm_avg['Return']),
            'DSR': float(dsr_avg)
        },
        'method_weighted_average': {
            'Sharpe_OOS': float(tm_weighted['Sharpe']),
            'Calmar': float(tm_weighted['Calmar']),
            'MDD': float(tm_weighted['MDD']),
            'Return': float(tm_weighted['Return']),
            'DSR': float(dsr_weighted)
        },
        'best_method': 'weighted_average' if tm_weighted['Sharpe'] > tm_avg['Sharpe'] else 'simple_average',
        'best_sharpe': float(max(tm_avg['Sharpe'], tm_weighted['Sharpe']))
    }

    print(f"[ENSEMBLE] Avg Sharpe={tm_avg['Sharpe']:.3f}, Weighted Sharpe={tm_weighted['Sharpe']:.3f}")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[ENSEMBLE] Done → {output_path}")

    return results

if __name__ == '__main__':
    # This is called from the main orchestrator after top 3 are done
    print("[ENSEMBLE] This script is called by the orchestrator post-processing phase")
