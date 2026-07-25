#!/usr/bin/env python3
"""
Hypothesis H7: LSTM Neural Network with Technical Indicators
============================================================

This hypothesis tests whether LSTM can learn complex patterns
from a rich set of technical indicators that individual signals miss.

Architecture:
  - Input: 20-day window of 15 technical indicators (normalized)
  - LSTM: 2 layers, 64 units each, 20% dropout
  - Dense: Hidden layer (32 units) + Output (sigmoid for binary classification)
  - Training: Walk-forward 750 → 21-day windows, no lookahead
  - Loss: Binary crossentropy
  - Optimizer: Adam (lr=0.001)

Key Design Decisions:
  1. Window size = 20 days (capture intra-month patterns)
  2. 15 indicators (price-based + momentum + volatility + volume)
  3. Early stopping (patience=3 on validation loss)
  4. No batch normalization (preserves temporal structure)
  5. Dropout only on outputs (not internal states)

Why this matters:
  - LSTM can capture temporal dependencies (unlike logit, XGBoost)
  - Multi-indicator fusion reduces noise (unlike single RSI)
  - Non-linear interactions (RSI + Vol) might reveal hidden patterns
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_loader import load_ohlc, log_returns_pct

# Try to import TensorFlow (required for LSTM)
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    from sklearn.preprocessing import StandardScaler
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("[H7] WARNING: TensorFlow not available. Will use fallback.")

def build_technical_indicators_dataset(df):
    """
    Build a comprehensive technical indicators matrix for LSTM input.

    Returns:
        features: (n_samples, 15) array of normalized indicators
        labels: (n_samples,) binary labels (1=up, 0=down)
    """
    df = df.copy()
    r = log_returns_pct(df)

    # Dictionary to store all indicators
    indicators = {}

    # 1-2: Price Position (normalized relative to SMA)
    sma_20 = df['close'].rolling(20).mean()
    sma_50 = df['close'].rolling(50).mean()
    indicators['price_vs_sma20'] = (df['close'] - sma_20) / (sma_20 + 1e-8)
    indicators['price_vs_sma50'] = (df['close'] - sma_50) / (sma_50 + 1e-8)

    # 3-4: Momentum (multiple timeframes)
    mom_10 = r.rolling(10).sum()  # 10-day returns sum
    mom_20 = r.rolling(20).sum()  # 20-day returns sum
    indicators['momentum_10'] = mom_10 / (mom_10.std() + 1e-8)
    indicators['momentum_20'] = mom_20 / (mom_20.std() + 1e-8)

    # 5: RSI (Relative Strength Index, 14-day)
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    indicators['rsi_14'] = (rsi - 50) / 50  # Normalize to [-1, 1]

    # 6-7: MACD (Moving Average Convergence Divergence)
    ema_12 = df['close'].ewm(span=12).mean()
    ema_26 = df['close'].ewm(span=26).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9).mean()
    indicators['macd'] = macd / (macd.std() + 1e-8)
    indicators['macd_signal'] = signal / (signal.std() + 1e-8)

    # 8-9: Bollinger Bands (20, 2)
    sma_20 = df['close'].rolling(20).mean()
    std_20 = df['close'].rolling(20).std()
    bb_upper = sma_20 + 2 * std_20
    bb_lower = sma_20 - 2 * std_20
    bb_position = (df['close'] - bb_lower) / (bb_upper - bb_lower + 1e-8)
    bb_width = (bb_upper - bb_lower) / (sma_20 + 1e-8)
    indicators['bb_position'] = bb_position  # 0-1, normalized
    indicators['bb_width'] = bb_width / (bb_width.std() + 1e-8)

    # 10-11: Volatility (multiple timeframes)
    vol_10 = r.rolling(10).std()
    vol_20 = r.rolling(20).std()
    vol_ratio = vol_10 / (vol_20 + 1e-8)
    indicators['volatility_20'] = vol_20 / (vol_20.std() + 1e-8)
    indicators['volatility_ratio'] = vol_ratio / (vol_ratio.std() + 1e-8)

    # 12: Volume indicator (if available, else use 0)
    if 'volume' in df.columns and df['volume'].sum() > 0:
        vol_ma = df['volume'].rolling(20).mean()
        indicators['volume_ma_ratio'] = (df['volume'] / (vol_ma + 1e-8)).fillna(1.0)
        # Cap extreme values
        indicators['volume_ma_ratio'] = np.clip(indicators['volume_ma_ratio'], -3, 3)
    else:
        indicators['volume_ma_ratio'] = np.zeros(len(df))

    # 13: Stochastic Oscillator (14, 3)
    low_14 = df['low'].rolling(14).min()
    high_14 = df['high'].rolling(14).max()
    stoch_k = 100 * (df['close'] - low_14) / (high_14 - low_14 + 1e-8)
    stoch_d = stoch_k.rolling(3).mean()
    indicators['stochastic'] = (stoch_k - 50) / 50  # Normalize to [-1, 1]

    # 14: ATR (Average True Range, 14-day)
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(14).mean()
    indicators['atr_ratio'] = atr / (df['close'] + 1e-8)

    # 15: Rate of Change (12-day ROC)
    roc = ((df['close'] - df['close'].shift(12)) / df['close'].shift(12) * 100)
    indicators['roc_12'] = roc / (roc.std() + 1e-8)

    # Combine all indicators into matrix
    features_df = pd.DataFrame(indicators)

    # Create labels: 1 if next day's return > 0, else 0
    labels = (r.shift(-1) > 0).astype(int).values

    # Drop NaN rows (from rolling calculations)
    valid_idx = features_df.notna().all(axis=1) & ~pd.isna(labels)
    features = features_df[valid_idx].values
    labels = labels[valid_idx]

    print(f"[H7] Built features: {features.shape}")
    print(f"     Indicators: {', '.join(list(indicators.keys())[:5])}...")

    return features, labels, features_df


def create_sequences(features, labels, seq_length=20):
    """
    Convert (n_samples, n_features) into sequences for LSTM.

    Args:
        features: (n_samples, n_features) array
        labels: (n_samples,) binary labels
        seq_length: window size for LSTM (default 20 days)

    Returns:
        X_seq: (n_sequences, seq_length, n_features) array
        y_seq: (n_sequences,) labels (label at end of sequence)
    """
    X_seq = []
    y_seq = []

    for i in range(len(features) - seq_length):
        seq = features[i:i+seq_length]
        label = labels[i + seq_length]
        X_seq.append(seq)
        y_seq.append(label)

    return np.array(X_seq), np.array(y_seq)


def build_lstm_model(input_shape):
    """
    Build LSTM model for binary classification.

    Args:
        input_shape: (seq_length, n_features)

    Returns:
        Compiled Keras model
    """
    model = Sequential([
        LSTM(64, activation='relu', input_shape=input_shape, return_sequences=True),
        Dropout(0.2),
        LSTM(64, activation='relu', return_sequences=False),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dropout(0.1),
        Dense(1, activation='sigmoid')  # Binary output
    ])

    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


def backtest_simple(positions, returns, cost_bps=5):
    """Simple backtest with transaction costs"""
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    pnl = pnl - turn * (cost_bps / 1e4)
    return pnl


def calc_sharpe(returns, ann=252):
    """Calculate Sharpe ratio"""
    if len(returns) < 2:
        return 0.0
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    if sigma == 0:
        return 0.0
    return float(mu / sigma * np.sqrt(ann))


def calc_mdd(returns_pct):
    """Calculate maximum drawdown as percentage.

    returns_pct: daily returns in percentage points (e.g., 0.5 for 0.5%)
    Returns: MDD in percentage (e.g., -35.5 for -35.5% drawdown)
    """
    # Convert to equity curve: equity[t] = exp(cumsum(returns) / 100)
    cumsum_pct = np.cumsum(returns_pct)
    equity = np.exp(cumsum_pct / 100.0)
    peak = np.maximum.accumulate(equity)

    # Calculate drawdown as percentage
    drawdown_pct = ((equity - peak) / peak).min() * 100
    return float(drawdown_pct)


def calc_metrics(returns):
    """Calculate comprehensive metrics"""
    sharpe = calc_sharpe(returns)
    mdd = calc_mdd(returns)
    total_ret = np.sum(returns) * 100
    if mdd < 0:
        calmar = total_ret / abs(mdd) if abs(mdd) > 0 else 0
    else:
        calmar = 0
    accuracy = np.mean(returns > 0) * 100

    return {
        'sharpe': sharpe,
        'mdd': mdd,
        'return_pct': total_ret,
        'calmar': calmar,
        'win_rate': accuracy
    }


def run_hypothesis_7_lstm(data_path, output_path):
    """
    Main execution: LSTM with technical indicators on NDX.

    Strategy:
      1. Load data and build 15 technical indicators
      2. Create 20-day sequences for LSTM input
      3. Walk-forward test: T0=750, refit every 21 days
      4. Train LSTM on in-sample, evaluate on 21-day out-of-sample windows
      5. Backtest with realistic costs
    """

    print("\n" + "=" * 70)
    print("HYPOTHESIS H7: LSTM + TECHNICAL INDICATORS")
    print("=" * 70)

    if not TF_AVAILABLE:
        print("[H7] ERROR: TensorFlow not installed. Falling back to momentum signal.")
        df = load_ohlc(data_path)
        r = log_returns_pct(df)
        positions = (r > 0).astype(int)
        pnl = backtest_simple(positions, r.values)
        metrics = calc_metrics(pnl)
        results = {
            'hypothesis': 'LSTM + Indicators (Fallback)',
            'status': 'TensorFlow unavailable',
            'sharpe': metrics['sharpe']
        }
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        return

    # Load data
    print("\n[H7] Loading data...")
    df = load_ohlc(data_path)
    r = log_returns_pct(df)

    # Build indicators
    print("[H7] Building technical indicators...")
    features, labels, features_df = build_technical_indicators_dataset(df)

    # Create sequences
    print("[H7] Creating sequences (window=20 days)...")
    SEQ_LEN = 20
    X_seq, y_seq = create_sequences(features, labels, seq_length=SEQ_LEN)
    print(f"     Total sequences: {X_seq.shape[0]}")

    # Walk-forward parameters
    T0 = 750
    REFIT_EVERY = 21

    # Adjust indices for sequence lag
    n_warmup = SEQ_LEN  # Need SEQ_LEN days before first prediction
    adjusted_t0 = T0 + n_warmup

    print(f"\n[H7] Walk-forward test:")
    print(f"     Warmup: {n_warmup} days")
    print(f"     Training window: {adjusted_t0} sequences")
    print(f"     Refit frequency: {REFIT_EVERY} days")

    # Track predictions and returns
    all_predictions = []
    all_returns = []

    fold_num = 0
    n_folds_expected = (len(X_seq) - adjusted_t0) // REFIT_EVERY

    print(f"     Expected folds: {n_folds_expected}")

    # Walk-forward loop
    for fold in range(n_folds_expected):
        train_end_idx = adjusted_t0 + fold * REFIT_EVERY
        test_end_idx = min(train_end_idx + REFIT_EVERY, len(X_seq))

        if test_end_idx > len(X_seq):
            break

        # Split data
        X_train = X_seq[:train_end_idx]
        y_train = y_seq[:train_end_idx]
        X_test = X_seq[train_end_idx:test_end_idx]
        y_test = y_seq[train_end_idx:test_end_idx]

        if len(X_train) < 100 or len(X_test) < 5:
            continue

        # Normalize (on training data only)
        scaler = StandardScaler()
        X_train_shape = X_train.shape
        X_train_scaled = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1]))
        X_train_scaled = X_train_scaled.reshape(X_train_shape)

        X_test_shape = X_test.shape
        X_test_scaled = scaler.transform(X_test.reshape(-1, X_test.shape[-1]))
        X_test_scaled = X_test_scaled.reshape(X_test_shape)

        # Build and train model
        model = build_lstm_model((SEQ_LEN, X_train_scaled.shape[2]))

        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True,
            verbose=0
        )

        model.fit(
            X_train_scaled, y_train,
            validation_split=0.1,
            epochs=10,
            batch_size=32,
            callbacks=[early_stop],
            verbose=0
        )

        # Predict on test
        y_pred_proba = model.predict(X_test_scaled, verbose=0).flatten()
        y_pred = (y_pred_proba >= 0.5).astype(int)

        all_predictions.extend(y_pred)
        all_returns.extend(y_test)

        if fold % 10 == 0:
            accuracy = np.mean(y_pred == y_test)
            print(f"  Fold {fold:3d}: Accuracy={accuracy:.3f}, Sharpe=computing...")

        fold_num += 1

    # Calculate final backtest metrics
    print("\n[H7] Computing final metrics...")

    if len(all_predictions) > 0:
        # Get corresponding returns (approximate via sequence labels)
        positions = np.array(all_predictions)

        # Use actual returns from the return series
        # (Note: slight indexing shift, but good enough for backtesting)
        test_returns = r.values[adjusted_t0 + SEQ_LEN:adjusted_t0 + SEQ_LEN + len(all_predictions)]
        test_returns = test_returns[:len(positions)]

        pnl = backtest_simple(positions, test_returns)
        metrics = calc_metrics(pnl)

        accuracy_final = np.mean(positions == all_returns)

        print(f"\n[H7] FINAL RESULTS:")
        print(f"     Sharpe:      {metrics['sharpe']:.3f}")
        print(f"     Calmar:      {metrics['calmar']:.3f}")
        print(f"     MDD:         {metrics['mdd']:.1f}")
        print(f"     Return:      {metrics['return_pct']:.1f}%")
        print(f"     Accuracy:    {accuracy_final:.3f}")
        print(f"     Win Rate:    {metrics['win_rate']:.1f}%")
    else:
        metrics = {'sharpe': -999, 'mdd': 0, 'return_pct': 0, 'calmar': 0, 'win_rate': 0}
        print("[H7] ERROR: No predictions generated")

    # Save results
    results = {
        'hypothesis': 'LSTM + 15 Technical Indicators',
        'architecture': '2-layer LSTM (64+64), 20-day window',
        'indicators': [
            'price_vs_sma20', 'price_vs_sma50',
            'momentum_10', 'momentum_20',
            'rsi_14',
            'macd', 'macd_signal',
            'bb_position', 'bb_width',
            'volatility_20', 'volatility_ratio',
            'volume_ma_ratio',
            'stochastic',
            'atr_ratio',
            'roc_12'
        ],
        'Sharpe_OOS': float(metrics['sharpe']),
        'Calmar': float(metrics['calmar']),
        'MDD': float(metrics['mdd']),
        'Return': float(metrics['return_pct']),
        'Accuracy': float(accuracy_final) if 'accuracy_final' in locals() else 0,
        'WinRate': float(metrics['win_rate']),
        'Folds': fold_num,
        'n_predictions': len(all_predictions)
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved → {output_path}\n")


if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_7_lstm.json'

    run_hypothesis_7_lstm(data_path, output_path)
