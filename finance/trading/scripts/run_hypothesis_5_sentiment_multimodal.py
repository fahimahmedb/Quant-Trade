#!/usr/bin/env python3
"""
Hypothesis 5: Sentiment + Multimodal Signals (Synthetic)
Without external data, we simulate sentiment-like signals from vol + price patterns
Risk: Overfitting if not careful
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_loader import load_ohlc, log_returns_pct
from prediction import backtest, trading_metrics, dsr

def run_hypothesis_5(data_path, output_path):
    """Test Hypothesis 5: Sentiment-like signals (synthetic)"""
    print("[H5] Loading data...")
    df_raw = load_ohlc(data_path)
    r = log_returns_pct(df_raw)

    # Synthetic "sentiment" factors
    vol_20 = r.rolling(20).std()
    vol_60 = r.rolling(60).std()
    vol_ratio = vol_20 / (vol_60 + 1e-8)

    # Price strength (distance from 50-day MA)
    sma50 = df_raw['close'].rolling(50).mean()
    price_strength = (df_raw['close'] - sma50) / (sma50 + 1e-8)

    # Momentum (20-day)
    momentum = r.rolling(20).sum()

    # RSI as fear/greed
    delta = df_raw['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    sentiment_rsi = (rsi - 50) / 50  # Normalize [-1, 1]

    # Composite score
    score = (
        0.3 * np.sign(momentum) +
        0.2 * sentiment_rsi +
        0.2 * price_strength / (abs(price_strength.max()) + 1e-8) +
        0.3 * np.sign(vol_ratio - 1.0)  # Vol expansion = concern
    )

    predictions = (score > 0).astype(float).fillna(0.5)
    positions = predictions >= 0.5

    # Backtest
    bt = backtest(positions, r.values, cost_bps=5, delay=1)
    tm = trading_metrics(bt, r.values)
    dsr_val = dsr(tm['Sharpe'], 6, len(r.values))

    results = {
        'hypothesis': 'Sentiment + Multimodal (Synthetic)',
        'Sharpe_OOS': float(tm['Sharpe']),
        'Calmar': float(tm['Calmar']),
        'MDD': float(tm['MDD']),
        'Return': float(tm['Return']),
        'DSR': float(dsr_val),
        'Note': 'Synthetic sentiment from vol+price+RSI',
        'Risk': 'High overfitting risk without external data'
    }

    print(f"[H5] Results: Sharpe={results['Sharpe_OOS']:.3f}, DSR={results['DSR']:.3f}")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[H5] Done → {output_path}")

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_5.json'
    run_hypothesis_5(data_path, output_path)
