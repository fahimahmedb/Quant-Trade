#!/usr/bin/env python3
"""
Hypothesis 1: Technical Indicators Ensemble + XGBoost
Tester si une rich palette d'indicateurs techniques + XGBoost beat Buy&Hold
"""
import sys
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_loader import load_ohlc, log_returns_pct
from prediction import build_features, triple_barrier_labels, walk_forward_signals, backtest, trading_metrics, dsr
from diagnostics import fit_student_t

def build_technical_ensemble_features(df):
    """Extended technical indicators for XGBoost"""
    df = df.copy()
    r = log_returns_pct(df)

    # Momentum (5, 10, 20 days)
    df['mom_5'] = r.rolling(5).sum()
    df['mom_10'] = r.rolling(10).sum()
    df['mom_20'] = r.rolling(20).sum()

    # RSI (14 days)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = df['close'].ewm(span=12).mean()
    ema26 = df['close'].ewm(span=26).mean()
    df['macd'] = ema12 - ema26
    df['signal_line'] = df['macd'].ewm(span=9).mean()
    df['macd_hist'] = df['macd'] - df['signal_line']

    # Bollinger Bands (20, 2)
    sma20 = df['close'].rolling(20).mean()
    std20 = df['close'].rolling(20).std()
    df['bb_upper'] = sma20 + (2 * std20)
    df['bb_lower'] = sma20 - (2 * std20)
    df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # ATR (14 days)
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['atr'] = true_range.rolling(14).mean()

    # Stochastic (14, 3)
    low14 = df['low'].rolling(14).min()
    high14 = df['high'].rolling(14).max()
    df['stoch_k'] = 100 * (df['close'] - low14) / (high14 - low14)
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()

    # ADX (14)
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    true_range_sum = true_range.rolling(14).sum()
    plus_di = 100 * (plus_dm.rolling(14).sum() / true_range_sum)
    minus_di = 100 * (minus_dm.rolling(14).sum() / true_range_sum)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    df['adx'] = dx.rolling(14).mean()

    # CCI (20)
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(20).mean()
    mad = (tp - sma_tp).abs().rolling(20).mean()
    df['cci'] = (tp - sma_tp) / (0.015 * mad)

    # Williams %R (14)
    df['williams_r'] = -100 * (high14 - df['close']) / (high14 - low14)

    # Volume indicators
    df['volume_ma'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / (df['volume_ma'] + 1e-8)

    # Price-based
    df['close_sma20'] = df['close'] / (df['close'].rolling(20).mean() + 1e-8)
    df['close_sma50'] = df['close'] / (df['close'].rolling(50).mean() + 1e-8)

    # Volatility (rolling std)
    df['vol_20'] = r.rolling(20).std()
    df['vol_60'] = r.rolling(60).std()

    # Drop NaN
    df = df.dropna()
    return df

def run_hypothesis_1(data_path, output_path):
    """Test Hypothesis 1: Technical Ensemble + XGBoost"""
    print("[H1] Loading data...")
    df_raw = load_ohlc(data_path)
    df = build_technical_ensemble_features(df_raw)

    print(f"[H1] Data shape: {df.shape}")

    # Triple barrier labels (H=5, ±1.5σ)
    df_with_labels = triple_barrier_labels(df, horizon=5, vol_span=20, mult=1.5)

    # Features for model (exclude price/date columns)
    feature_cols = [c for c in df_with_labels.columns
                    if c not in ['date', 'open', 'high', 'low', 'close', 'volume', 'label', 'weight']]

    print(f"[H1] Features: {len(feature_cols)}")

    # Walk-forward test
    T0 = 750
    REFIT_EVERY = 21
    predictions_all = []
    metrics_list = []

    for fold, (train_idx, test_idx) in enumerate(walk_forward_signals(len(df_with_labels), T0, REFIT_EVERY)):
        if fold % 10 == 0:
            print(f"[H1] Fold {fold}/{len(df_with_labels) // REFIT_EVERY}")

        X_train = df_with_labels.iloc[train_idx][feature_cols].fillna(0)
        y_train = df_with_labels.iloc[train_idx]['label'].values

        X_test = df_with_labels.iloc[test_idx][feature_cols].fillna(0)
        y_test = df_with_labels.iloc[test_idx]['label'].values

        # Standardize
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train XGBoost (gradient boosting)
        model = GradientBoostingClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
        model.fit(X_train_scaled, y_train)

        # Predict probabilities
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = (y_proba >= 0.5).astype(int)

        # Store predictions
        for idx, (true_idx, prob, pred) in enumerate(zip(test_idx, y_proba, y_pred)):
            predictions_all.append({
                'idx': true_idx,
                'date': df_with_labels.iloc[true_idx]['date'],
                'prob_up': prob,
                'pred': pred,
                'actual': y_test[idx]
            })

        # Accuracy on this fold
        accuracy = (y_pred == y_test).mean()
        metrics_list.append({'fold': fold, 'accuracy': accuracy})

    # Compile results
    pred_df = pd.DataFrame(predictions_all)
    pred_df = pred_df.sort_values('idx').reset_index(drop=True)

    # Convert to returns for backtest
    r_forward = log_returns_pct(df_raw).iloc[pred_df['idx'].values].values

    # Backtest with signal
    positions = (pred_df['prob_up'].values >= 0.5).astype(int)  # Long only
    bt = backtest(positions, r_forward, cost_bps=5, delay=1)
    tm = trading_metrics(bt, r_forward)

    # DSR calculation
    n_trials = 6  # We tested 6 hypotheses
    dsr_val = dsr(tm['Sharpe'], n_trials, len(r_forward))

    results = {
        'hypothesis': 'Technical Ensemble + XGBoost',
        'Sharpe_OOS': float(tm['Sharpe']),
        'Calmar': float(tm['Calmar']),
        'MDD': float(tm['MDD']),
        'Return': float(tm['Return']),
        'Accuracy': float(pred_df['pred'].eq(pred_df['actual']).mean()),
        'Profit_Factor': float(tm.get('ProfitFactor', 0)),
        'DSR': float(dsr_val),
        'N_features': len(feature_cols),
        'N_predictions': len(predictions_all),
        'predictions_sample': pred_df.head(100).to_dict(orient='records')
    }

    print(f"[H1] Results: Sharpe={results['Sharpe_OOS']:.3f}, DSR={results['DSR']:.3f}, Accuracy={results['Accuracy']:.3f}")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"[H1] Done → {output_path}")

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_1.json'
    run_hypothesis_1(data_path, output_path)
