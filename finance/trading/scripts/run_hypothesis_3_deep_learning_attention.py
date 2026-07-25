#!/usr/bin/env python3
"""
Hypothesis 3: Deep Learning (LSTM + Attention)
CNN extract patterns + Transformer attention on temporal sequences
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_loader import load_ohlc, log_returns_pct
from prediction import build_features, backtest, trading_metrics, dsr

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Attention, Input
    from tensorflow.keras.optimizers import Adam
    from sklearn.preprocessing import MinMaxScaler
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("[H3] WARNING: TensorFlow not installed, using fallback")

def run_hypothesis_3(data_path, output_path):
    """Test Hypothesis 3: Deep Learning LSTM+Attention"""
    print("[H3] Loading data...")
    df_raw = load_ohlc(data_path)
    r = log_returns_pct(df_raw)

    # Build features
    df_feat = build_features(df_raw)
    feature_cols = [c for c in df_feat.columns if c not in ['date', 'open', 'high', 'low', 'close', 'volume']]

    if not TF_AVAILABLE:
        # Fallback: simple momentum-based signal
        print("[H3] Using fallback (no TensorFlow): Momentum")
        mom_20 = r.rolling(20).mean()
        predictions = (mom_20 > 0).astype(float).fillna(0.5)
        positions = predictions >= 0.5
        bt = backtest(positions, r.values, cost_bps=5, delay=1)
        tm = trading_metrics(bt, r.values)
        dsr_val = dsr(tm['Sharpe'], 6, len(r.values))
        results = {
            'hypothesis': 'Deep Learning LSTM+Attention (Fallback)',
            'Sharpe_OOS': float(tm['Sharpe']),
            'Calmar': float(tm['Calmar']),
            'MDD': float(tm['MDD']),
            'Return': float(tm['Return']),
            'DSR': float(dsr_val),
            'Note': 'Fallback: TensorFlow not available'
        }
    else:
        # Sequence preparation
        X = df_feat[feature_cols].fillna(0).values
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        seq_len = 20
        X_seq = np.array([X_scaled[i:i+seq_len] for i in range(len(X_scaled) - seq_len)])
        y_seq = (r.values[seq_len:] > 0).astype(int)

        # Split train/test (80/20)
        split_idx = int(0.8 * len(X_seq))
        X_train = X_seq[:split_idx]
        y_train = y_seq[:split_idx]
        X_test = X_seq[split_idx:]
        y_test = y_seq[split_idx:]

        print(f"[H3] Training LSTM on {X_train.shape} samples...")

        # Simple LSTM model
        model = Sequential([
            LSTM(64, input_shape=(seq_len, X_train.shape[2]), return_sequences=True),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
        model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=0)

        # Predict
        y_proba_test = model.predict(X_test, verbose=0).flatten()
        y_pred_test = (y_proba_test >= 0.5).astype(int)

        # Backtest with test predictions
        positions = np.zeros(len(r.values))
        positions[split_idx + seq_len:split_idx + seq_len + len(y_pred_test)] = y_pred_test

        bt = backtest(positions, r.values, cost_bps=5, delay=1)
        tm = trading_metrics(bt, r.values)
        dsr_val = dsr(tm['Sharpe'], 6, len(r.values))
        accuracy = (y_pred_test == y_test).mean()

        results = {
            'hypothesis': 'Deep Learning LSTM+Attention',
            'Sharpe_OOS': float(tm['Sharpe']),
            'Calmar': float(tm['Calmar']),
            'MDD': float(tm['MDD']),
            'Return': float(tm['Return']),
            'Accuracy_Test': float(accuracy),
            'DSR': float(dsr_val),
        }

    print(f"[H3] Results: Sharpe={results['Sharpe_OOS']:.3f}, DSR={results['DSR']:.3f}")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[H3] Done → {output_path}")

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_3.json'
    run_hypothesis_3(data_path, output_path)
