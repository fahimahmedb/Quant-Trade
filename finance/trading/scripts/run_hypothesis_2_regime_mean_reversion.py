#!/usr/bin/env python3
"""
Hypothesis 2: Regime-Aware Mean Reversion + Momentum Switching
Switch signal based on vol tercile (low=MR, mid=momentum, high=defensive)
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_loader import load_ohlc, log_returns_pct
from prediction import backtest, trading_metrics, dsr

def run_hypothesis_2(data_path, output_path):
    """Test Hypothesis 2: Regime-Aware Switching"""
    print("[H2] Loading data...")
    df_raw = load_ohlc(data_path)
    r = log_returns_pct(df_raw)

    # Volatility terciles (rolling 20-day)
    vol_20 = r.rolling(20).std()
    vol_terciles = vol_20.quantile([1/3, 2/3])

    # Features
    rsi_period = 14
    delta = df_raw['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    mom_12 = df_raw['close'].ewm(span=12).mean()
    mom_26 = df_raw['close'].ewm(span=26).mean()
    momentum = mom_12 > mom_26

    # Signal by regime
    predictions = []
    for i in range(21, min(len(df_raw), len(vol_20))):
        v = vol_20.iloc[i]

        if v < vol_terciles.iloc[0]:  # Low vol → mean reversion
            if rsi.iloc[i] > 70:
                pred = 0  # Short (oversold → revert)
            elif rsi.iloc[i] < 30:
                pred = 1  # Long (overbought → revert)
            else:
                pred = 0.5  # Neutral
        elif v < vol_terciles.iloc[1]:  # Mid vol → momentum
            pred = 1.0 if momentum.iloc[i] else 0.0
        else:  # High vol → defensive (hold neutral)
            pred = 0.5

        predictions.append(pred)

    # Pad with neutral
    predictions = [0.5] * 21 + predictions

    # Backtest
    positions = np.array(predictions) >= 0.5
    r_fwd = r.values
    bt = backtest(positions, r_fwd, cost_bps=5, delay=1)
    tm = trading_metrics(bt, r_fwd)

    dsr_val = dsr(tm['Sharpe'], 6, len(r_fwd))
    accuracy = np.mean(positions)  # Approximation (long ratio)

    results = {
        'hypothesis': 'Regime-Aware Mean Reversion + Momentum',
        'Sharpe_OOS': float(tm['Sharpe']),
        'Calmar': float(tm['Calmar']),
        'MDD': float(tm['MDD']),
        'Return': float(tm['Return']),
        'Long_Ratio': float(accuracy),
        'DSR': float(dsr_val),
    }

    print(f"[H2] Results: Sharpe={results['Sharpe_OOS']:.3f}, DSR={results['DSR']:.3f}")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[H2] Done → {output_path}")

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_2.json'
    run_hypothesis_2(data_path, output_path)
