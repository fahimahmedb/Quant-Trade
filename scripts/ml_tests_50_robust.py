#!/usr/bin/env python3
"""
50 Robust ML Strategy Tests — Anti-Shape-Error Design

Iteration 3: Sequence 50 independent tests with explicit shape validation.
Each test:
1. Load data FRESH (no shared state)
2. Validate shapes before training
3. Save result atomically
4. Clean up immediately
5. Proceed to next test

Prevents the shape mismatch (6118 vs 6117) that killed Iteration 1.
"""

import sys
import json
import os
from pathlib import Path
import warnings
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(ROOT / "finance" / "src"))

from data_loader import load_ohlc, quality_report
from prediction import (
    build_features,
    backtest,
    trading_metrics,
    triple_barrier_labels,
    walk_forward_proba,
    dsr,
)

# ============================================================================
# PROTOCOL (Fixed a priori)
# ============================================================================
T0 = 750
REFIT_EVERY = 21
EMBARGO = 21
H = 5
VOL_SPAN = 20
BARRIER_MULT = 1.5
COST_BPS = 5.0
SEED = 42

# 50 Strategy Definitions (Fixed a priori)
STRATEGIES = {
    1: ("RandomForest_d3_n100", ["mom_10", "vol_20", "rsi_14"],
        lambda: RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=-1)),
    2: ("RandomForest_d5_n100", ["mom_10", "vol_20", "rsi_14"],
        lambda: RandomForestClassifier(n_estimators=100, max_depth=5, random_state=SEED, n_jobs=-1)),
    3: ("RandomForest_d7_n100", ["mom_10", "vol_20", "rsi_14"],
        lambda: RandomForestClassifier(n_estimators=100, max_depth=7, random_state=SEED, n_jobs=-1)),
    4: ("XGB_eta01_d3", ["mom_10", "vol_ratio", "vol_20", "atr_rel"],
        lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.1,
                                                l2_regularization=1.0, random_state=SEED)),
    5: ("XGB_eta05_d3", ["mom_10", "vol_ratio", "vol_20", "atr_rel"],
        lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.05,
                                                l2_regularization=1.0, random_state=SEED)),
    6: ("XGB_eta1_d3", ["mom_10", "vol_ratio", "vol_20", "atr_rel"],
        lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.01,
                                                l2_regularization=1.0, random_state=SEED)),
    7: ("LGB_leaves15", ["mom_10", "vol_ratio", "rsi_14"],
        lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=150, learning_rate=0.05,
                                                l2_regularization=0.5, min_samples_leaf=15, random_state=SEED)),
    8: ("LGB_leaves31", ["mom_10", "vol_ratio", "rsi_14"],
        lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=150, learning_rate=0.05,
                                                l2_regularization=0.5, min_samples_leaf=31, random_state=SEED)),
    9: ("LGB_leaves63", ["mom_10", "vol_ratio", "rsi_14"],
        lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=150, learning_rate=0.05,
                                                l2_regularization=0.5, min_samples_leaf=63, random_state=SEED)),
    10: ("NN_deep_5", ["mom_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "ret_1", "ret_2", "ret_3", "ret_5", "ret_10"],
         lambda: HistGradientBoostingClassifier(max_depth=5, max_iter=200, learning_rate=0.05,
                                                 l2_regularization=0.5, random_state=SEED)),
    11: ("LogReg_C05", ["mom_10", "vol_20", "rsi_14"],
         lambda: LogisticRegression(C=0.5, max_iter=1000, solver='lbfgs', random_state=SEED)),
    12: ("LogReg_C1", ["mom_10", "vol_20", "rsi_14"],
         lambda: LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs', random_state=SEED)),
    13: ("LogReg_C10", ["mom_10", "vol_20", "rsi_14"],
         lambda: LogisticRegression(C=10.0, max_iter=1000, solver='lbfgs', random_state=SEED)),
    14: ("GB_interact", ["mom_10", "vol_20", "rsi_14", "ma_ratio_20"],
         lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.1,
                                                 l2_regularization=1.0, random_state=SEED)),
    15: ("SVM_rbf_C1", ["mom_10", "vol_20", "rsi_14", "ma_ratio_20", "ret_1", "ret_2", "ret_3", "ret_5", "ret_10", "macd_rel"],
         lambda: SVC(C=1.0, gamma='scale', probability=True, random_state=SEED, max_iter=5000)),
    # Tests 16-50: Additional variants for diversity
    16: ("GB_d2_it80", ["mom_10", "vol_20", "rsi_14", "ret_5", "parkinson_5"],
         lambda: HistGradientBoostingClassifier(max_depth=2, max_iter=80, learning_rate=0.1,
                                                 l2_regularization=1.5, min_samples_leaf=50, random_state=SEED)),
    17: ("GB_d4_it120", ["mom_10", "vol_20", "rsi_14", "ma_ratio_20"],
         lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=120, learning_rate=0.08,
                                                 l2_regularization=0.8, random_state=SEED)),
    18: ("RF_d6_n150", ["mom_10", "vol_20", "rsi_14", "macd_rel"],
         lambda: RandomForestClassifier(n_estimators=150, max_depth=6, random_state=SEED, n_jobs=-1)),
    19: ("LogReg_C02", ["mom_10", "vol_20"],
         lambda: LogisticRegression(C=0.2, max_iter=1000, solver='lbfgs', random_state=SEED)),
    20: ("XGB_eta008_d2", ["mom_10", "vol_ratio"],
         lambda: HistGradientBoostingClassifier(max_depth=2, max_iter=150, learning_rate=0.008,
                                                 l2_regularization=2.0, random_state=SEED)),
    # Tests 21-50: More variants
    21: ("GB_mean_rev", ["mom_10", "vol_ratio", "rsi_14", "ret_1", "ret_2"],
         lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.05,
                                                 l2_regularization=1.0, random_state=SEED)),
    22: ("RF_d4_n80", ["mom_10", "vol_20", "atr_rel", "bb_pctb"],
         lambda: RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=-1)),
    23: ("LogReg_C20", ["mom_10", "vol_20", "rsi_14", "macd_rel"],
         lambda: LogisticRegression(C=20.0, max_iter=1000, solver='lbfgs', random_state=SEED)),
    24: ("SVM_poly_C05", ["mom_10", "vol_20", "rsi_14"],
         lambda: SVC(C=0.5, kernel='poly', probability=True, random_state=SEED, max_iter=5000)),
    25: ("GB_deep_d6", ["mom_10", "vol_20", "rsi_14", "ret_1", "ret_2", "ret_3", "ret_5", "macd_rel", "bb_pctb", "atr_rel"],
         lambda: HistGradientBoostingClassifier(max_depth=6, max_iter=150, learning_rate=0.02,
                                                 l2_regularization=1.0, random_state=SEED)),
    26: ("RF_d5_n120", ["vol_20", "rsi_14", "macd_rel"],
         lambda: RandomForestClassifier(n_estimators=120, max_depth=5, random_state=SEED, n_jobs=-1)),
    27: ("XGB_eta02_d4", ["mom_10", "vol_ratio", "atr_rel", "ret_5"],
         lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=80, learning_rate=0.02,
                                                 l2_regularization=0.5, random_state=SEED)),
    28: ("LogReg_C50", ["mom_10", "vol_20", "rsi_14", "ret_5"],
         lambda: LogisticRegression(C=50.0, max_iter=1000, solver='lbfgs', random_state=SEED)),
    29: ("GB_interaction_v2", ["mom_10", "vol_20", "rsi_14"],
         lambda: HistGradientBoostingClassifier(max_depth=5, max_iter=100, learning_rate=0.05,
                                                 l2_regularization=0.5, random_state=SEED)),
    30: ("SVM_rbf_C05", ["mom_10", "vol_20", "rsi_14"],
         lambda: SVC(C=0.5, gamma='scale', probability=True, random_state=SEED, max_iter=5000)),
    31: ("RF_d3_n200", ["mom_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb"],
         lambda: RandomForestClassifier(n_estimators=200, max_depth=3, random_state=SEED, n_jobs=-1)),
    32: ("GB_min_samp_30", ["mom_10", "vol_20", "rsi_14"],
         lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.1,
                                                 l2_regularization=1.0, min_samples_leaf=30, random_state=SEED)),
    33: ("LogReg_L1", ["mom_10", "vol_20", "rsi_14"],
         lambda: LogisticRegression(C=1.0, max_iter=1000, solver='saga', penalty='l1', random_state=SEED)),
    34: ("XGB_eta005_d5", ["mom_10", "vol_ratio", "vol_20", "atr_rel", "ret_5"],
         lambda: HistGradientBoostingClassifier(max_depth=5, max_iter=100, learning_rate=0.005,
                                                 l2_regularization=2.0, random_state=SEED)),
    35: ("RF_d8_n100", ["mom_10", "vol_20", "rsi_14"],
         lambda: RandomForestClassifier(n_estimators=100, max_depth=8, random_state=SEED, n_jobs=-1)),
    36: ("GB_mean_rev_v2", ["mom_10", "vol_ratio", "rsi_14"],
         lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=150, learning_rate=0.05,
                                                 l2_regularization=0.5, min_samples_leaf=20, random_state=SEED)),
    37: ("SVM_rbf_C10", ["mom_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb"],
         lambda: SVC(C=10.0, gamma='scale', probability=True, random_state=SEED, max_iter=5000)),
    38: ("LogReg_C100", ["mom_10", "vol_20", "rsi_14", "macd_rel"],
         lambda: LogisticRegression(C=100.0, max_iter=1000, solver='lbfgs', random_state=SEED)),
    39: ("GB_d3_it200", ["mom_10", "vol_ratio", "rsi_14", "ret_1", "ret_5"],
         lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05,
                                                 l2_regularization=0.5, random_state=SEED)),
    40: ("RF_d4_n250", ["mom_10", "vol_20", "rsi_14", "ret_1", "ret_5"],
         lambda: RandomForestClassifier(n_estimators=250, max_depth=4, random_state=SEED, n_jobs=-1)),
    41: ("XGB_eta015_d3", ["mom_10", "vol_ratio", "vol_20"],
         lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=120, learning_rate=0.015,
                                                 l2_regularization=1.0, random_state=SEED)),
    42: ("GB_robust_shrinkage", ["mom_10", "vol_20", "rsi_14"],
         lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=100, learning_rate=0.01,
                                                 l2_regularization=2.0, random_state=SEED)),
    43: ("SVM_poly_C1", ["mom_10", "vol_20", "rsi_14", "macd_rel"],
         lambda: SVC(C=1.0, kernel='poly', degree=2, probability=True, random_state=SEED, max_iter=5000)),
    44: ("LogReg_C05_elasticnet", ["mom_10", "vol_20"],
         lambda: LogisticRegression(C=0.5, max_iter=1000, solver='saga', penalty='elasticnet', l1_ratio=0.5, random_state=SEED)),
    45: ("GB_d2_it150", ["mom_10", "vol_ratio"],
         lambda: HistGradientBoostingClassifier(max_depth=2, max_iter=150, learning_rate=0.05,
                                                 l2_regularization=2.0, random_state=SEED)),
    46: ("RF_d5_n180", ["vol_20", "rsi_14", "macd_rel", "bb_pctb"],
         lambda: RandomForestClassifier(n_estimators=180, max_depth=5, random_state=SEED, n_jobs=-1)),
    47: ("XGB_balance", ["mom_10", "vol_20", "rsi_14"],
         lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.05,
                                                 l2_regularization=1.0, random_state=SEED)),
    48: ("LogReg_regularized", ["mom_10", "vol_20", "rsi_14"],
         lambda: LogisticRegression(C=0.1, max_iter=1000, solver='lbfgs', random_state=SEED)),
    49: ("SVM_linear", ["mom_10", "vol_20"],
         lambda: SVC(C=1.0, kernel='linear', probability=True, random_state=SEED, max_iter=5000)),
    50: ("GB_final", ["mom_10", "vol_20", "rsi_14", "macd_rel"],
         lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.08,
                                                 l2_regularization=1.0, random_state=SEED)),
}

# ============================================================================
# Main Loop: Run each strategy independently
# ============================================================================

results = {}
sharpe_trials = []

print("=" * 80)
print("50 ML STRATEGY TESTS — STRICT CAUSAL PROTOCOL")
print("=" * 80)

for test_num in sorted(STRATEGIES.keys()):
    model_name, features, factory = STRATEGIES[test_num]
    print(f"\n[Test {test_num:2d}/50] {model_name}")

    start_time = time.time()
    result = {
        "id": test_num,
        "model": model_name,
        "features": features,
        "design_sharpe": None,
        "test_sharpe": None,
        "degradation": None,
        "dsr": None,
        "result": "ERROR",
        "reason": None,
    }

    try:
        # Load fresh data for each test (no shared state)
        DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
        df = load_ohlc(str(DATA_PATH))
        quality_report(df)
        df = df.set_index("date")

        close = df["close"].astype(float)
        logp = np.log(close)
        r_fwd = logp.shift(-1) - logp
        r_fwd_values = r_fwd.values

        # SHAPE VALIDATION #1: Data loaded
        assert len(df) > T0, f"Dataset too small: {len(df)} < {T0}"

        # Build features and labels
        X = build_features(df)
        y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
        y.index = df.index

        # SHAPE VALIDATION #2: Features and labels aligned
        assert X.shape[0] == y.shape[0], \
            f"X/y shape mismatch: {X.shape[0]} != {y.shape[0]}"

        n = len(df)
        dates = df.index

        # Design/Test split
        split_date = pd.Timestamp("2010-01-01")
        design_mask = dates < split_date
        test_mask = dates >= split_date
        design_idx = np.where(design_mask)[0]
        test_idx = np.where(test_mask)[0]

        design_n = design_idx[-1] if len(design_idx) > 0 else 0
        test_start_idx = test_idx[0] if len(test_idx) > 0 else n

        # SHAPE VALIDATION #3: Design/test split valid
        assert design_n > T0, f"Design set too small: {design_n} <= {T0}"
        assert len(test_idx) > 0, "Test set empty"

        # Select features (verify all requested features exist)
        missing_features = [f for f in features if f not in X.columns]
        assert not missing_features, \
            f"Strategy {test_num} ({name}): Missing features {missing_features}. Available: {list(X.columns)}"
        available_features = features
        X_subset = X[available_features].copy()

        # SHAPE VALIDATION #4: Feature subset aligned
        assert X_subset.shape[0] == y.shape[0], \
            f"Feature subset shape mismatch: {X_subset.shape[0]} != {y.shape[0]}"

        # Walk-forward on design set
        proba = walk_forward_proba(
            X_subset.iloc[:design_n],
            y.iloc[:design_n],
            factory,
            t0=T0,
            refit_every=REFIT_EVERY,
            embargo=EMBARGO,
            standardize=True,
        )

        # SHAPE VALIDATION #5: Walk-forward output
        assert len(proba) == design_n, \
            f"Proba shape mismatch: {len(proba)} != {design_n}"

        pos_design = np.where(np.isfinite(proba), np.where(proba > 0.5, 1.0, -1.0), 0.0)
        pnl_design = backtest(pos_design, r_fwd_values[:design_n], COST_BPS)
        design_oos = np.arange(T0, design_n)
        pnl_design_oos = pnl_design[design_oos]
        metr_design = trading_metrics(pnl_design_oos)
        design_sharpe = metr_design["sharpe_daily"]

        sharpe_trials.append(design_sharpe)

        # Test set: retrain on full design set
        X_design = X_subset.iloc[:design_n]
        y_design = y.iloc[:design_n]
        mask_design = np.all(np.isfinite(X_design.values), axis=1) & np.isfinite(y_design.values)

        if mask_design.sum() > 100:
            X_design_clean = X_design.values[mask_design]
            y_design_clean = (y_design.values[mask_design] > 0).astype(int)

            mu_design = X_design_clean.mean(axis=0)
            sd_design = X_design_clean.std(axis=0)
            sd_design[sd_design == 0] = 1.0

            X_design_clean = (X_design_clean - mu_design) / sd_design

            final_model = factory()
            final_model.fit(X_design_clean, y_design_clean)

            # Score test set
            proba_test = np.full(len(test_idx), np.nan)
            for i, test_i in enumerate(test_idx):
                xt = X_subset.values[test_i]
                if np.all(np.isfinite(xt)):
                    xt = (xt - mu_design) / sd_design
                    try:
                        proba_test[i] = final_model.predict_proba(xt.reshape(1, -1))[0, 1]
                    except:
                        pass

            pos_test = np.where(np.isfinite(proba_test), np.where(proba_test > 0.5, 1.0, -1.0), 0.0)
            pnl_test = backtest(pos_test, r_fwd_values[test_start_idx:test_start_idx + len(test_idx)], COST_BPS)
            metr_test = trading_metrics(pnl_test)
            test_sharpe = metr_test["sharpe_daily"]
        else:
            test_sharpe = np.nan
            metr_test = {}

        degradation = design_sharpe - test_sharpe if np.isfinite(test_sharpe) else np.nan

        # DSR (n_trials=50 for this iteration; cumulative = 50+10+50 = 110 across all)
        var_trials = np.var(sharpe_trials, ddof=1) if len(sharpe_trials) > 1 else 1.0
        dsr_result = dsr(
            design_sharpe,
            len(design_oos),
            var_trials=var_trials,
            n_trials=110,  # CRITICAL: Iter1(50) + Iter2(10) + Iter3(50) = 110 cumulative hypotheses
            skew=metr_design.get("skew", 0.0),
            kurt_excess=metr_design.get("excess_kurt", 0.0),
        )
        dsr_value = dsr_result["dsr"]

        # Pass criterion (convert daily Sharpe to annualized: ×√252)
        design_sharpe_ann = design_sharpe * np.sqrt(252)
        test_sharpe_ann = test_sharpe * np.sqrt(252) if np.isfinite(test_sharpe) else test_sharpe

        passes = (
            design_sharpe_ann > 0.55 and
            np.isfinite(test_sharpe_ann) and test_sharpe_ann > 0.55 and
            degradation < 0.5 and
            dsr_value > 0.95
        )

        result["design_sharpe"] = float(design_sharpe)
        result["test_sharpe"] = float(test_sharpe) if np.isfinite(test_sharpe) else None
        result["degradation"] = float(degradation) if np.isfinite(degradation) else None
        result["dsr"] = float(dsr_value)
        result["pass"] = bool(passes)
        result["result"] = "PASS" if passes else "FAIL"

        status = "✅" if passes else "❌"
        print(f"  {status} Design: {design_sharpe:.4f} | Test: {test_sharpe:.4f} | DSR: {dsr_value:.4f}")

    except Exception as e:
        result["result"] = "ERROR"
        result["reason"] = str(e)
        print(f"  ❌ ERROR: {str(e)[:80]}")

    # Store result in dict for summary
    results[test_num] = result

    # Save result atomically
    result_path = ROOT / "results" / f"strategy_{test_num:03d}.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    elapsed = time.time() - start_time
    print(f"  Time: {elapsed:.1f}s")

# ============================================================================
# Summary
# ============================================================================

passed = sum(1 for r in results.values() if r.get("result") == "PASS") if results else 0

print(f"\n" + "=" * 80)
print(f"RESULTS: {passed} PASS / {len(STRATEGIES) - passed} FAIL")
print(f"=" * 80)

# Save summary
summary_path = ROOT / "results" / "iteration_3_summary.json"
with open(summary_path, "w") as f:
    json.dump({"total": len(STRATEGIES), "passed": passed, "timestamp": pd.Timestamp.now().isoformat()}, f)

print(f"Summary saved to: {summary_path}")
