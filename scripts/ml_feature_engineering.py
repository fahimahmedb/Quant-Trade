#!/usr/bin/env python3
"""
ML Feature Engineering for S5-OV Enhancement
==============================================
Create rich feature set from OHLCV data
Goal: ML learns when S5-OV thrives vs struggles
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "finance" / "src"))
from data_loader import load_ohlc, log_returns_pct

def build_features(df, r):
    """Build comprehensive feature set for ML"""
    # Align lengths (log_returns is one shorter)
    min_len = min(len(df), len(r))
    df_aligned = df.iloc[:min_len].copy()
    r_aligned = r.iloc[:min_len].copy()

    features = pd.DataFrame(index=df_aligned.index)

    close = df_aligned['close'].values
    high = df_aligned['high'].values
    low = df_aligned['low'].values
    returns = r_aligned.values

    # Handle missing volume
    volume = np.ones(len(df_aligned))

    # ===== TREND FEATURES =====
    features['ema_50'] = df_aligned['close'].ewm(span=50).mean().values
    features['ema_200'] = df_aligned['close'].ewm(span=200).mean().values
    features['ema_ratio'] = features['ema_50'] / features['ema_200']
    features['ema_dist'] = (features['ema_50'] - features['ema_200']) / features['ema_200']

    features['sma_20'] = df_aligned['close'].rolling(20).mean().values
    features['sma_50'] = df_aligned['close'].rolling(50).mean().values

    # ===== VOLATILITY FEATURES =====
    features['vol_20'] = r_aligned.rolling(20).std().values
    features['vol_50'] = r_aligned.rolling(50).std().values
    features['vol_ratio'] = features['vol_20'] / features['vol_50']

    # Vol percentile (for overlay mechanism)
    features['vol_percentile'] = r_aligned.rolling(252).apply(
        lambda x: (x[-1] - x.quantile(0.25)) / (x.quantile(0.75) - x.quantile(0.25))
        if x.quantile(0.75) > x.quantile(0.25) else 0.5
    ).values

    # ===== MOMENTUM FEATURES =====
    features['roc_5'] = (close - np.roll(close, 5)) / np.roll(close, 5)  # 5-day ROC
    features['roc_20'] = (close - np.roll(close, 20)) / np.roll(close, 20)
    features['roc_252'] = (close - np.roll(close, 252)) / np.roll(close, 252)  # 1-year

    features['momentum_5'] = pd.Series(returns).rolling(5).sum().values
    features['momentum_20'] = pd.Series(returns).rolling(20).sum().values

    # ===== MEAN REVERSION FEATURES =====
    features['zscore_20'] = (close - features['sma_20']) / features['vol_20']
    features['zscore_50'] = (close - features['sma_50']) / features['vol_50']

    # ===== RANGE & VOLATILITY STRUCTURE =====
    features['atr_14'] = (
        pd.Series(high - low).rolling(14).mean() +
        pd.Series(np.abs(high - np.roll(close, 1))).rolling(14).mean() +
        pd.Series(np.abs(low - np.roll(close, 1))).rolling(14).mean()
    ) / 3.0

    features['range_pct'] = (high - low) / close

    # ===== VOLUME FEATURES =====
    features['volume_sma'] = pd.Series(volume).rolling(20).mean().values
    features['volume_ratio'] = volume / features['volume_sma']

    # ===== RETURN DISTRIBUTION =====
    features['skew_20'] = pd.Series(returns).rolling(20).skew().values
    features['kurt_20'] = pd.Series(returns).rolling(20).kurt().values

    # ===== DIRECTION & STRENGTH =====
    features['returns'] = returns
    features['abs_returns'] = np.abs(returns)

    # ===== REGIME INDICATORS =====
    # Bull/bear based on SMA
    features['in_bull'] = (features['ema_50'] > features['ema_200']).astype(float)

    # Strong trend
    features['trend_strength'] = np.abs(features['ema_dist'])

    # Volatility regime
    features['high_vol'] = (features['vol_20'] > features['vol_20'].quantile(0.75)).astype(float)
    features['low_vol'] = (features['vol_20'] < features['vol_20'].quantile(0.25)).astype(float)

    # Recent performance
    features['ret_5d'] = pd.Series(returns).rolling(5).sum().values
    features['ret_20d'] = pd.Series(returns).rolling(20).sum().values

    return features.fillna(0)

def build_labels(signal, returns, r, window=5, cost_bps=5):
    """
    Build labels: 1 if S5-OV will outperform next window, 0 otherwise
    """
    def backtest_window(pos, ret):
        pnl = pos * ret
        turn = np.abs(np.diff(pos, prepend=0))
        return np.sum(pnl - turn * (cost_bps / 1e4))

    labels = np.zeros(len(signal))

    for i in range(len(signal) - window):
        # What S5-OV achieves in next window
        s5_pnl = backtest_window(signal[i:i+window], returns[i:i+window])

        # What neutral position (cash) gets
        cash_pnl = backtest_window(np.zeros(window), returns[i:i+window])

        # Label: 1 if S5-OV better than cash
        labels[i] = 1.0 if s5_pnl > cash_pnl else 0.0

    return labels

print("Building feature set...")
df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)

features = build_features(df, r)

# S5-OV signal
ema50 = df['close'].ewm(span=50).mean()
ema200 = df['close'].ewm(span=200).mean()
signal_base = np.where(ema50 > ema200, 1.0, 0.0)

# Vol overlay
vol_20 = r.rolling(20).std()
vol_low = vol_20.quantile(0.25)
vol_high = vol_20.quantile(0.75)
overlay_mult = np.ones(len(df))
for i in range(len(df)):
    if pd.notna(vol_20.iloc[i]):
        if vol_20.iloc[i] < vol_low:
            overlay_mult[i] = 1.5
        elif vol_20.iloc[i] > vol_high:
            overlay_mult[i] = 0.3

signal_s5ov = signal_base * overlay_mult

# Labels: when S5-OV is profitable
labels = build_labels(signal_s5ov, r.values, r)

# Save
features['s5ov_signal'] = signal_s5ov
features['label_s5ov_profitable'] = labels
features = features.fillna(0)

features.to_csv('/tmp/claude-0/-home-user-Quant-Trade/d40e7f44-8dba-572d-ba27-6c7a61ed28ed/scratchpad/ml_features.csv', index=False)

print(f"✅ Features created: {features.shape[0]} obs, {features.shape[1]} features")
print(f"Label distribution: {(labels == 1).sum()} profitable / {len(labels)} total ({(labels == 1).mean()*100:.1f}%)")
print(f"Saved to: /tmp/claude-0/-home-user-Quant-Trade/d40e7f44-8dba-572d-ba27-6c7a61ed28ed/scratchpad/ml_features.csv")
