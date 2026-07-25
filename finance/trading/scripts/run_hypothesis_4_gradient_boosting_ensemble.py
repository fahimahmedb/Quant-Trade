#!/usr/bin/env python3
"""
Hypothesis 4: Gradient Boosting Ensemble (XGBoost + LightGBM + CatBoost)
Stack predictions from 3 gradient boosting models for robustness
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_loader import load_ohlc, log_returns_pct
from prediction import build_features, triple_barrier_labels, walk_forward_signals, backtest, trading_metrics, dsr

try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False

try:
    from catboost import CatBoostClassifier
    CB_AVAILABLE = True
except ImportError:
    CB_AVAILABLE = False

def run_hypothesis_4(data_path, output_path):
    """Test Hypothesis 4: Gradient Boosting Ensemble"""
    print("[H4] Loading data...")
    df_raw = load_ohlc(data_path)
    df = build_features(df_raw)
    df_with_labels = triple_barrier_labels(df, horizon=5, vol_span=20, mult=1.5)

    feature_cols = [c for c in df_with_labels.columns
                    if c not in ['date', 'open', 'high', 'low', 'close', 'volume', 'label', 'weight']]

    print(f"[H4] Testing with {len(feature_cols)} features")

    if not (XGB_AVAILABLE or LGB_AVAILABLE or CB_AVAILABLE):
        print("[H4] No gradient boosting libraries available, using fallback")
        r = log_returns_pct(df_raw)
        positions = (r > 0).astype(int)
        bt = backtest(positions, r.values, cost_bps=5, delay=1)
        tm = trading_metrics(bt, r.values)
        dsr_val = dsr(tm['Sharpe'], 6, len(r.values))
        results = {
            'hypothesis': 'Gradient Boosting Ensemble (Fallback)',
            'Sharpe_OOS': float(tm['Sharpe']),
            'Note': 'Libraries not available'
        }
    else:
        T0 = 750
        REFIT_EVERY = 21
        predictions_all = []
        probas_xgb = []
        probas_lgb = []
        probas_cb = []

        for fold, (train_idx, test_idx) in enumerate(walk_forward_signals(len(df_with_labels), T0, REFIT_EVERY)):
            if fold % 10 == 0:
                print(f"[H4] Fold {fold}")

            X_train = df_with_labels.iloc[train_idx][feature_cols].fillna(0)
            y_train = df_with_labels.iloc[train_idx]['label'].values
            X_test = df_with_labels.iloc[test_idx][feature_cols].fillna(0)
            y_test = df_with_labels.iloc[test_idx]['label'].values

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # XGBoost
            if XGB_AVAILABLE:
                xgb = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, use_label_encoder=False)
                xgb.fit(X_train_scaled, y_train, verbose=False)
                probas_xgb.extend(xgb.predict_proba(X_test_scaled)[:, 1])
            else:
                probas_xgb.extend([0.5] * len(test_idx))

            # LightGBM
            if LGB_AVAILABLE:
                lgb = LGBMClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, verbose=-1)
                lgb.fit(X_train_scaled, y_train)
                probas_lgb.extend(lgb.predict_proba(X_test_scaled)[:, 1])
            else:
                probas_lgb.extend([0.5] * len(test_idx))

            # CatBoost
            if CB_AVAILABLE:
                cb = CatBoostClassifier(iterations=100, max_depth=5, learning_rate=0.1, verbose=False, random_state=42)
                cb.fit(X_train_scaled, y_train)
                probas_cb.extend(cb.predict_proba(X_test_scaled)[:, 1])
            else:
                probas_cb.extend([0.5] * len(test_idx))

        # Ensemble: average probability
        ensemble_proba = (np.array(probas_xgb) + np.array(probas_lgb) + np.array(probas_cb)) / 3.0
        positions = ensemble_proba >= 0.5

        r_forward = log_returns_pct(df_raw).values
        bt = backtest(positions, r_forward, cost_bps=5, delay=1)
        tm = trading_metrics(bt, r_forward)
        dsr_val = dsr(tm['Sharpe'], 6, len(r_forward))

        results = {
            'hypothesis': 'Gradient Boosting Ensemble (XGB+LGB+CB)',
            'Sharpe_OOS': float(tm['Sharpe']),
            'Calmar': float(tm['Calmar']),
            'MDD': float(tm['MDD']),
            'Return': float(tm['Return']),
            'DSR': float(dsr_val),
            'Libraries': {
                'XGBoost': XGB_AVAILABLE,
                'LightGBM': LGB_AVAILABLE,
                'CatBoost': CB_AVAILABLE
            }
        }

    print(f"[H4] Results: Sharpe={results['Sharpe_OOS']:.3f}")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[H4] Done → {output_path}")

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_4.json'
    run_hypothesis_4(data_path, output_path)
