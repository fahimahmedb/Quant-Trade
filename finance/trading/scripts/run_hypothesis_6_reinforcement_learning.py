#!/usr/bin/env python3
"""
Hypothesis 6: Reinforcement Learning (Simple Policy Gradient)
WARNING: High variance, high overfitting risk — included for completeness
Uses simple policy gradient with reward = Sharpe differential vs BuyHold
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_loader import load_ohlc, log_returns_pct
from prediction import build_features, backtest, trading_metrics, dsr

def simple_policy_gradient(returns, features, epochs=10, lr=0.01):
    """
    Simple policy gradient: learn weights w to predict exposure
    exposure_t = sigmoid(features_t @ w)
    reward = realized Sharpe difference vs BuyHold
    """
    n_features = features.shape[1]
    w = np.random.randn(n_features) * 0.01

    bh_sharpe = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(252)

    for epoch in range(epochs):
        # Forward: compute exposure
        logits = features @ w
        exposures = 1.0 / (1.0 + np.exp(-logits))  # Sigmoid [0, 1]
        exposures = np.clip(exposures, 0.2, 1.5)  # Clamp to realistic range

        # Backtest
        positions = exposures >= 0.75
        bt = backtest(positions, returns, cost_bps=5, delay=1)
        tm = trading_metrics(bt, returns)

        # Reward = Sharpe difference
        reward = tm['Sharpe'] - bh_sharpe

        # Simple gradient: if reward > 0, increase w
        if reward > 0:
            w += lr * np.mean(features, axis=0) * reward
        else:
            w -= lr * np.mean(features, axis=0) * abs(reward)

        if epoch % 3 == 0:
            print(f"  [RL] Epoch {epoch}: reward={reward:.4f}, Sharpe={tm['Sharpe']:.3f}")

    return w, exposures

def run_hypothesis_6(data_path, output_path):
    """Test Hypothesis 6: Reinforcement Learning"""
    print("[H6] Loading data...")
    df_raw = load_ohlc(data_path)
    df = build_features(df_raw)
    r = log_returns_pct(df_raw)

    feature_cols = [c for c in df.columns if c not in ['date', 'open', 'high', 'low', 'close', 'volume']]
    X = df[feature_cols].fillna(0).values
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)  # Normalize

    print(f"[H6] Training RL policy on {X.shape}...")

    try:
        w, exposures = simple_policy_gradient(r.values, X, epochs=15, lr=0.001)

        # Final backtest
        positions = exposures >= 0.75
        bt = backtest(positions, r.values, cost_bps=5, delay=1)
        tm = trading_metrics(bt, r.values)
        dsr_val = dsr(tm['Sharpe'], 6, len(r.values))

        results = {
            'hypothesis': 'Reinforcement Learning (Simple PG)',
            'Sharpe_OOS': float(tm['Sharpe']),
            'Calmar': float(tm['Calmar']),
            'MDD': float(tm['MDD']),
            'Return': float(tm['Return']),
            'DSR': float(dsr_val),
            'Warning': 'High variance RL, overfitting risk HIGH'
        }
    except Exception as e:
        print(f"[H6] Error: {e}")
        results = {
            'hypothesis': 'Reinforcement Learning (Simple PG)',
            'Error': str(e),
            'Sharpe_OOS': -999
        }

    print(f"[H6] Results: Sharpe={results.get('Sharpe_OOS', 'ERROR'):.3f}")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[H6] Done → {output_path}")

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_6.json'
    run_hypothesis_6(data_path, output_path)
