#!/usr/bin/env python3
"""
ML Models to Enhance S5-OV Signal
=================================
Test ensemble, gradient boosting to learn when S5-OV is strongest
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "finance" / "src"))
from data_loader import load_ohlc, log_returns_pct

print("\n" + "="*80)
print("ML ENHANCEMENT OF S5-OV SIGNAL")
print("="*80)

# Load data
df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)

min_len = min(len(df), len(r))
df = df.iloc[:min_len].copy()
r = r.iloc[:min_len].copy()

print(f"Data loaded: {len(df)} observations")

# =============================================================================
# Build Simple Feature Set (avoiding index issues)
# =============================================================================

features = {}

# Trend
ema50 = df['close'].ewm(span=50).mean().values
ema200 = df['close'].ewm(span=200).mean().values
features['ema_trend'] = ema50 / ema200

# Volatility
vol_20 = np.std([r.iloc[max(0, i-20):i+1].mean() for i in range(len(r))])
features['vol_level'] = pd.Series(r).rolling(20).std().values

# Momentum (simple)
features['momentum_5d'] = [np.sum(r.iloc[max(0,i-5):i+1]) if i > 0 else 0 for i in range(len(r))]
features['momentum_20d'] = [np.sum(r.iloc[max(0,i-20):i+1]) if i > 0 else 0 for i in range(len(r))]

# Mean reversion signal
sma20 = pd.Series(df['close']).rolling(20).mean().values
features['zscore'] = (df['close'].values - sma20) / (pd.Series(r).rolling(20).std().values + 1e-6)

# S5-OV base signal
features['s5ov_signal'] = np.where(ema50 > ema200, 1.0, 0.0)

# Create DataFrame
X = pd.DataFrame(features)
X = X.fillna(0)

print(f"Features created: {X.shape[1]} features, {X.shape[0]} observations")
print(f"Feature columns: {list(X.columns)}")

# =============================================================================
# Label: When S5-OV is profitable in next 5 days
# =============================================================================

def backtest_window(pos, ret, cost_bps=5):
    if len(pos) == 0:
        return 0
    pnl = pos * ret
    turn = np.abs(np.diff(pos, prepend=0))
    return np.sum(pnl - turn * (cost_bps / 1e4))

# Vol overlay for S5-OV
vol_20_series = pd.Series(r).rolling(20).std()
vol_low = vol_20_series.quantile(0.25)
vol_high = vol_20_series.quantile(0.75)

signal_base = features['s5ov_signal']
overlay = np.ones(len(signal_base))
for i in range(len(overlay)):
    if pd.notna(vol_20_series.iloc[i]):
        if vol_20_series.iloc[i] < vol_low:
            overlay[i] = 1.5
        elif vol_20_series.iloc[i] > vol_high:
            overlay[i] = 0.3

signal_s5ov = signal_base * overlay

# Labels (was S5-OV profitable in last 5 days?)
labels = np.zeros(len(signal_s5ov))
for i in range(5, len(signal_s5ov)):
    pnl = backtest_window(signal_s5ov[i-5:i], r.values[i-5:i])
    labels[i] = 1.0 if pnl > 0 else 0.0

print(f"\nLabel distribution: {(labels==1).sum()}/{len(labels)} profitable windows ({(labels==1).mean()*100:.1f}%)")

# =============================================================================
# Train/Test Split (Walk-Forward: first 70% train, last 30% test)
# =============================================================================

split_idx = int(0.7 * len(X))
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = labels[:split_idx], labels[split_idx:]

print(f"\nTrain/Test split: {len(X_train)} train, {len(X_test)} test")

# =============================================================================
# Model 1: Gradient Boosting (XGBoost-like but simple)
# =============================================================================

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, roc_auc_score

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
    gb_model.fit(X_train_scaled, y_train.astype(int))

    y_pred_gb = gb_model.predict(X_test_scaled)
    y_prob_gb = gb_model.predict_proba(X_test_scaled)[:, 1]

    acc_gb = accuracy_score(y_test, y_pred_gb)
    auc_gb = roc_auc_score(y_test, y_prob_gb) if len(np.unique(y_test)) > 1 else 0.5

    print(f"\n[GradientBoosting] Accuracy: {acc_gb:.3f}, AUC: {auc_gb:.3f}")

    # Feature importance
    importance = gb_model.feature_importances_
    top_features = sorted(zip(X.columns, importance), key=lambda x: x[1], reverse=True)[:5]
    print(f"  Top features: {', '.join([f'{name}:{imp:.3f}' for name, imp in top_features])}")

except Exception as e:
    print(f"GradientBoosting failed: {e}")

# =============================================================================
# Model 2: Random Forest
# =============================================================================

try:
    from sklearn.ensemble import RandomForestClassifier

    rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf_model.fit(X_train_scaled, y_train.astype(int))

    y_pred_rf = rf_model.predict(X_test_scaled)
    y_prob_rf = rf_model.predict_proba(X_test_scaled)[:, 1]

    acc_rf = accuracy_score(y_test, y_pred_rf)
    auc_rf = roc_auc_score(y_test, y_prob_rf) if len(np.unique(y_test)) > 1 else 0.5

    print(f"\n[RandomForest] Accuracy: {acc_rf:.3f}, AUC: {auc_rf:.3f}")

    importance_rf = rf_model.feature_importances_
    top_features_rf = sorted(zip(X.columns, importance_rf), key=lambda x: x[1], reverse=True)[:5]
    print(f"  Top features: {', '.join([f'{name}:{imp:.3f}' for name, imp in top_features_rf])}")

except Exception as e:
    print(f"RandomForest failed: {e}")

print("\n✅ ML Enhancement phase complete\n")
