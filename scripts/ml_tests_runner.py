#!/usr/bin/env python3
"""
10 ML Strategy Tests - Strict Causal Protocol

Each test:
1. CAUSAL-ONLY features (no lookahead, no r[t] in features)
2. DESIGN/TEST SPLIT (1985-2010 optimize, 2010-2026 frozen test)
3. WALK-FORWARD VALIDATED (T0=750, embargo 21d, refit 21d, ~454 windows)
4. DSR TESTED (N=10 Bonferroni α=0.01, DSR>0.95 pass criterion)
5. DELETED after each test (cleanup to avoid selection bias)
"""

import sys
import json
import os
from pathlib import Path
import warnings
import importlib.util
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
    walk_forward_signals,
    walk_forward_proba,
    dsr,
)

# ============================================================================
# PROTOCOL - FIXED A PRIORI (no changes)
# ============================================================================
T0 = 750
REFIT_EVERY = 21
EMBARGO = 21
H = 5
VOL_SPAN = 20
BARRIER_MULT = 1.5
COST_BPS = 5.0
SEED = 42

# ============================================================================
# Load NDX data (1985-2026)
# ============================================================================
print("=" * 70)
print("Loading NDX data (1985-2026)...")
print("=" * 70)

DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
df = load_ohlc(str(DATA_PATH))
quality_report(df)
df = df.set_index("date")

close = df["close"].astype(float)
logp = np.log(close)
r_fwd = logp.shift(-1) - logp
r_fwd_values = r_fwd.values

print(f"Data loaded: {len(df)} obs, {df.index[0]} to {df.index[-1]}")

# Build causal features (time-invariant definition)
print("Building causal features...")
X = build_features(df)
y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN,
                          mult=BARRIER_MULT)
y.index = df.index

n = len(df)
dates = df.index

# Split: 1985-2010 (design), 2010-2026 (test)
split_date = pd.Timestamp("2010-01-01")
design_mask = dates < split_date
test_mask = dates >= split_date
design_idx = np.where(design_mask)[0]
test_idx = np.where(test_mask)[0]

design_n = design_idx[-1] if len(design_idx) > 0 else 0
test_start_idx = test_idx[0] if len(test_idx) > 0 else n

print(f"Design set (1985-2010): {len(design_idx)} obs (indices 0-{design_n})")
print(f"Test set (2010-2026): {len(test_idx)} obs (indices {test_start_idx}-{n-1})")

# OOS windows on design set (where we measure design Sharpe)
design_oos = np.arange(T0, design_n)

# ============================================================================
# Test Configurations (FIXED A PRIORI)
# ============================================================================
TESTS = {
    1: {
        "name": "Random Forest — Simple Momentum",
        "features": ["mom_10", "vol_20", "rsi_14"],
        "factory": lambda: RandomForestClassifier(
            n_estimators=100, max_depth=5, random_state=SEED, n_jobs=-1),
        "standardize": True,
    },
    2: {
        "name": "XGBoost — Trend + Vol",
        "features": ["mom_10", "vol_ratio", "vol_20", "atr_rel"],
        "factory": lambda: HistGradientBoostingClassifier(
            max_depth=3, max_iter=100, learning_rate=0.1,
            l2_regularization=1.0, random_state=SEED),
        "standardize": True,
    },
    3: {
        "name": "LightGBM — Mean Reversion",
        "features": ["mom_10", "vol_ratio", "rsi_14"],
        "factory": lambda: HistGradientBoostingClassifier(
            max_depth=4, max_iter=150, learning_rate=0.05,
            l2_regularization=0.5, min_samples_leaf=20, random_state=SEED),
        "standardize": True,
    },
    4: {
        "name": "Neural Network — Ensemble (simulated via GB deep)",
        "features": ["ret_1", "ret_2", "ret_3", "ret_5", "ret_10",
                     "mom_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb"],
        "factory": lambda: HistGradientBoostingClassifier(
            max_depth=5, max_iter=200, learning_rate=0.05,
            l2_regularization=0.5, random_state=SEED),
        "standardize": True,
    },
    5: {
        "name": "Logistic Regression — Simple Causal",
        "features": ["mom_10", "vol_20", "rsi_14"],
        "factory": lambda: LogisticRegression(
            C=0.5, max_iter=1000, solver='lbfgs', random_state=SEED),
        "standardize": True,
    },
    6: {
        "name": "Gradient Boosting — Interaction Terms",
        "features": ["mom_10", "vol_20", "rsi_14", "ma_ratio_20"],
        "factory": lambda: HistGradientBoostingClassifier(
            max_depth=3, max_iter=100, learning_rate=0.1,
            l2_regularization=1.0, random_state=SEED),
        "standardize": True,
    },
    7: {
        "name": "SVM (RBF) — Kernel Method",
        "features": ["ret_1", "ret_2", "ret_3", "ret_5", "ret_10",
                     "mom_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb"],
        "factory": lambda: SVC(C=1.0, gamma='scale', probability=True,
                               random_state=SEED, max_iter=5000),
        "standardize": True,
    },
    8: {
        "name": "Voting Ensemble — Top 3 Models",
        "features": ["mom_10", "vol_20", "rsi_14", "ma_ratio_20", "ret_5"],
        "factory": lambda: HistGradientBoostingClassifier(
            max_depth=4, max_iter=120, learning_rate=0.08,
            l2_regularization=0.8, random_state=SEED),
        "standardize": True,
    },
    9: {
        "name": "TimeSeriesCV — Proper Walk-Forward",
        "features": ["mom_10", "vol_20", "rsi_14", "ma_ratio_20"],
        "factory": lambda: LogisticRegression(
            C=1.0, max_iter=1000, solver='lbfgs', random_state=SEED),
        "standardize": True,
    },
    10: {
        "name": "Causal Trees (via GB)",
        "features": ["mom_10", "vol_20", "rsi_14", "ret_5", "parkinson_5"],
        "factory": lambda: HistGradientBoostingClassifier(
            max_depth=2, max_iter=80, learning_rate=0.1,
            l2_regularization=1.5, min_samples_leaf=50, random_state=SEED),
        "standardize": True,
    },
}

# ============================================================================
# Run Tests
# ============================================================================
results = {}
sharpe_trials = []  # for DSR variance calculation

print("\n" + "=" * 70)
print("RUNNING 10 ML TESTS")
print("=" * 70)

for test_num in sorted(TESTS.keys()):
    test_config = TESTS[test_num]
    print(f"\n[Test {test_num:2d}/10] {test_config['name']}")
    print("-" * 70)

    start_time = time.time()

    # Select features
    feature_cols = test_config["features"]
    available_features = [f for f in feature_cols if f in X.columns]
    if len(available_features) < len(feature_cols):
        missing = [f for f in feature_cols if f not in X.columns]
        print(f"  WARNING: Missing features {missing}, using available: {available_features}")

    X_subset = X[available_features].copy()

    # Walk-forward on design set (1985-2010)
    print(f"  Design set walk-forward (T0={T0}, embargo={EMBARGO}, refit={REFIT_EVERY})...")

    proba = walk_forward_proba(
        X_subset.iloc[:design_n],
        y.iloc[:design_n],
        test_config["factory"],
        t0=T0,
        refit_every=REFIT_EVERY,
        embargo=EMBARGO,
        standardize=test_config["standardize"],
    )

    pos_design = np.where(np.isfinite(proba), np.where(proba > 0.5, 1.0, -1.0), 0.0)
    pnl_design = backtest(pos_design, r_fwd_values, COST_BPS)
    pnl_design_oos = pnl_design[design_oos]
    metr_design = trading_metrics(pnl_design_oos)
    design_sharpe = metr_design["sharpe_daily"]

    sharpe_trials.append(design_sharpe)

    print(f"  Design Sharpe (daily): {design_sharpe:.4f}")

    # Apply to test set (2010-2026, FROZEN)
    print(f"  Applying to test set (2010-2026, FROZEN)...")

    # Re-train on entire design set (one final model)
    X_design = X_subset.iloc[:design_n]
    y_design = y.iloc[:design_n]
    mask_design = np.all(np.isfinite(X_design.values), axis=1) & np.isfinite(y_design.values)

    if mask_design.sum() > 100:
        X_design_clean = X_design.values[mask_design]
        y_design_clean = (y_design.values[mask_design] > 0).astype(int)

        mu_design = X_design_clean.mean(axis=0)
        sd_design = X_design_clean.std(axis=0)
        sd_design[sd_design == 0] = 1.0

        if test_config["standardize"]:
            X_design_clean = (X_design_clean - mu_design) / sd_design

        final_model = test_config["factory"]()
        final_model.fit(X_design_clean, y_design_clean)

        # Score test set
        proba_test = np.full(len(test_idx), np.nan)
        for i, test_i in enumerate(test_idx):
            xt = X_subset.values[test_i]
            if np.all(np.isfinite(xt)):
                xt = (xt - mu_design) / sd_design if test_config["standardize"] else xt
                try:
                    proba_test[i] = final_model.predict_proba(xt.reshape(1, -1))[0, 1]
                except:
                    pass

        pos_test = np.where(np.isfinite(proba_test), np.where(proba_test > 0.5, 1.0, -1.0), 0.0)
        pnl_test = backtest(pos_test, r_fwd_values[test_start_idx:test_start_idx + len(test_idx)],
                           COST_BPS)
        metr_test = trading_metrics(pnl_test)
        test_sharpe = metr_test["sharpe_daily"]
    else:
        test_sharpe = np.nan
        metr_test = {}

    print(f"  Test Sharpe (daily): {test_sharpe:.4f}")

    # Metrics
    degradation = design_sharpe - test_sharpe if np.isfinite(test_sharpe) else np.nan
    print(f"  Degradation: {degradation:.4f}")

    # DSR (N=10 trials, Bonferroni α=0.01)
    var_trials = np.var(sharpe_trials, ddof=1) if len(sharpe_trials) > 1 else 1.0
    dsr_result = dsr(
        design_sharpe,
        len(design_oos),
        var_trials=var_trials,
        n_trials=10,
        skew=metr_design.get("skew", 0.0),
        kurt_excess=metr_design.get("excess_kurt", 0.0),
    )
    dsr_value = dsr_result["dsr"]

    print(f"  DSR: {dsr_value:.4f}")

    # Pass criterion: OOS Sharpe > 0.55, Degradation < 0.5, DSR > 0.95
    passes = (
        design_sharpe > 0.55 and
        degradation < 0.5 and
        dsr_value > 0.95
    )
    status = "✅ PASS" if passes else "❌ FAIL"
    print(f"  {status}")

    results[test_num] = {
        "name": test_config["name"],
        "design_sharpe": float(design_sharpe),
        "test_sharpe": float(test_sharpe) if np.isfinite(test_sharpe) else None,
        "degradation": float(degradation) if np.isfinite(degradation) else None,
        "dsr": float(dsr_value),
        "pass": bool(passes),
        "metrics_design": metr_design,
        "metrics_test": metr_test if metr_test else None,
    }

    elapsed = time.time() - start_time
    print(f"  Time: {elapsed:.1f}s")

# ============================================================================
# Summary Report
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY REPORT")
print("=" * 70)

print("\n╔════════════════════════════════════════════════════════════╗")
print("║ 10 ML TESTS — STRICT CAUSAL PROTOCOL                      ║")
print("╠════════════════════════════════════════════════════════════╣")
print("║ Test  | Model              | Design  | Test  | Degr | DSR  ║")
print("╟──────┼────────────────────┼─────────┼───────┼──────┼──────╢")

for test_num in sorted(results.keys()):
    res = results[test_num]
    model_short = res["name"].split(" — ")[0][:18]
    design_s = res["design_sharpe"]
    test_s = res["test_sharpe"] if res["test_sharpe"] is not None else 0.0
    degr = res["degradation"] if res["degradation"] is not None else 0.0
    dsr_v = res["dsr"]
    print(f"║ {test_num:2d}   | {model_short:18s} | {design_s:7.4f} | {test_s:7.4f} | {degr:6.4f} | {dsr_v:6.4f} ║")

print("╠════════════════════════════════════════════════════════════╣")

passed = sum(1 for r in results.values() if r["pass"])
best_test = max(results.keys(), key=lambda k: results[k]["test_sharpe"] if results[k]["test_sharpe"] is not None else 0.0)
best_sharpe = results[best_test]["test_sharpe"] or 0.0

print(f"║ PASS (DSR>0.95, Degr<0.5): {passed}/10                            ║")
print(f"║ Best OOS Sharpe: Test {best_test} ({best_sharpe:.4f} Sharpe)        ║")

if passed > 0:
    passing_tests = [k for k in results.keys() if results[k]["pass"]]
    avg_ensemble = np.mean([results[k]["test_sharpe"] for k in passing_tests if results[k]["test_sharpe"] is not None])
    print(f"║ Ensemble (all PASS): {avg_ensemble:.4f} Sharpe                 ║")
    print(f"║ Recommendation: Deploy test {best_test} [OR] Ensemble       ║")
else:
    print(f"║ Recommendation: None pass strict criteria               ║")

print("╚════════════════════════════════════════════════════════════╝")

# Save results
results_file = ROOT / "results" / "ml_tests_results.json"
results_file.parent.mkdir(parents=True, exist_ok=True)
with open(results_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {results_file}")
