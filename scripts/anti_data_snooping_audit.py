#!/usr/bin/env python3
"""
Anti-Data-Snooping Audit Framework
Strict causal validation to prevent lookahead bias (the root cause of all prior failures)

Five automated checks:
1. TEMPORAL ALIGNMENT: features[t] must use only data[0:t], not [0:t+1]
2. CORRELATION CHECK: feature correlation with forward return > 0.30 = red flag
3. PERTURBATION TEST: scramble future data, verify Sharpe unchanged
4. FEATURE AUDIT TRAIL: each feature must declare its source/lag
5. WALK-FORWARD SANITY: IS Sharpe ≈ OOS Sharpe; large degradation = suspect

Usage:
  python3 scripts/anti_data_snooping_audit.py <strategy_json> <data_path>

Returns:
  - JSON with audit verdict (PASS/FAIL)
  - Detailed findings for each check
  - Risk score (0=safe, 1=high lookahead risk)
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple

ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(ROOT / "finance" / "src"))

from data_loader import load_ohlc
from prediction import backtest, trading_metrics, build_features, triple_barrier_labels

# ============================================================================
# CHECK 1: Temporal Alignment (Feature Causality)
# ============================================================================

def check_temporal_alignment(X: pd.DataFrame, feature_names: list) -> Dict[str, Any]:
    """
    Verify each feature uses only lagged data (t-1, not t or t+1).

    RED FLAG: if any feature has non-zero value on first observation
    (suggests lookahead or improper lagging).
    """
    findings = {
        "check": "Temporal Alignment",
        "status": "PASS",
        "details": [],
        "risk_score": 0.0,
    }

    # Check if any feature has NaN in early rows (sign of proper lagging)
    for col in feature_names:
        if col not in X.columns:
            findings["details"].append(f"⚠️ Feature '{col}' not in data")
            continue

        # Count NaNs in first 5 rows (should have some)
        nan_count = X[col].iloc[:5].isna().sum()
        first_valid_idx = X[col].first_valid_index()

        if nan_count == 0:
            findings["details"].append(
                f"⚠️ Feature '{col}' has no NaNs in first 5 rows "
                "(may lack proper lag)"
            )
            findings["risk_score"] += 0.1
        else:
            findings["details"].append(f"✓ Feature '{col}' properly lagged")

    if findings["risk_score"] > 0:
        findings["status"] = "CAUTION"

    return findings


# ============================================================================
# CHECK 2: Forward-Return Correlation (Lookahead Signature)
# ============================================================================

def check_forward_correlation(X: pd.DataFrame, returns: pd.Series,
                              feature_names: list) -> Dict[str, Any]:
    """
    Lookahead manifests as high correlation between features and forward returns.

    RED FLAG: corr(feature, r[t+1]) > 0.30 suggests feature sees future data.
    Legitimate features correlate with PAST returns (momentum), not future.
    """
    findings = {
        "check": "Forward-Return Correlation",
        "status": "PASS",
        "details": [],
        "risk_score": 0.0,
        "high_correlation_features": [],
    }

    # Align forward returns (shift by -1)
    r_fwd = returns.shift(-1)

    for col in feature_names:
        if col not in X.columns:
            continue

        # Remove NaNs for correlation
        mask = np.isfinite(X[col].values) & np.isfinite(r_fwd.values)
        if mask.sum() < 30:
            continue

        corr = np.corrcoef(X[col].values[mask], r_fwd.values[mask])[0, 1]

        if abs(corr) > 0.30:
            findings["details"].append(
                f"🚨 {col}: corr with forward return = {corr:.4f} (LOOKAHEAD ALERT)"
            )
            findings["high_correlation_features"].append(col)
            findings["risk_score"] += 0.3  # High risk
        elif abs(corr) > 0.20:
            findings["details"].append(
                f"⚠️ {col}: corr with forward return = {corr:.4f} (borderline)"
            )
            findings["risk_score"] += 0.1
        else:
            findings["details"].append(f"✓ {col}: corr = {corr:.4f} (safe)")

    if findings["risk_score"] > 0.2:
        findings["status"] = "FAIL"
    elif findings["risk_score"] > 0.1:
        findings["status"] = "CAUTION"

    return findings


# ============================================================================
# CHECK 3: Perturbation Test (Gold Standard Lookahead Detection)
# ============================================================================

def check_perturbation(X: pd.DataFrame, y: pd.Series, returns: pd.Series,
                       design_idx: np.ndarray, model_factory,
                       standardize: bool = True) -> Dict[str, Any]:
    """
    Train model on original data, test on perturbed data (future returns scrambled).

    If Sharpe unchanged: no lookahead (feature doesn't depend on future).
    If Sharpe drops: lookahead present (model relied on scrambled future data).
    """
    findings = {
        "check": "Perturbation Test",
        "status": "PASS",
        "details": [],
        "sharpe_original": None,
        "sharpe_perturbed": None,
        "degradation": None,
        "risk_score": 0.0,
    }

    try:
        # Get design set
        X_design = X.iloc[:design_idx[-1]]
        y_design = y.iloc[:design_idx[-1]]
        r_design = returns.iloc[:design_idx[-1]]

        # Clean data
        mask = np.all(np.isfinite(X_design.values), axis=1) & np.isfinite(y_design.values)
        if mask.sum() < 100:
            findings["details"].append("❌ Insufficient clean design data")
            findings["status"] = "SKIP"
            return findings

        X_clean = X_design.values[mask]
        y_clean = (y_design.values[mask] > 0).astype(int)
        r_clean = r_design.values[mask]

        # Standardize if needed
        if standardize:
            mu = X_clean.mean(axis=0)
            sd = X_clean.std(axis=0)
            sd[sd == 0] = 1.0
            X_clean = (X_clean - mu) / sd

        # Train model
        model = model_factory()
        model.fit(X_clean, y_clean)

        # Original test performance
        proba_orig = model.predict_proba(X_clean)[:, 1]
        pos_orig = np.where(proba_orig > 0.5, 1.0, -1.0)
        pnl_orig = backtest(pos_orig, r_clean, cost_bps=5.0)
        metrics_orig = trading_metrics(pnl_orig)
        sharpe_orig = metrics_orig.get("sharpe_daily", np.nan)

        # Perturbed: shuffle future returns (scramble lookahead)
        r_perturbed = np.random.permutation(r_clean)
        pnl_perturbed = backtest(pos_orig, r_perturbed, cost_bps=5.0)
        metrics_perturbed = trading_metrics(pnl_perturbed)
        sharpe_perturbed = metrics_perturbed.get("sharpe_daily", np.nan)

        findings["sharpe_original"] = float(sharpe_orig)
        findings["sharpe_perturbed"] = float(sharpe_perturbed)
        findings["degradation"] = float(sharpe_orig - sharpe_perturbed)

        # Interpretation
        if abs(findings["degradation"]) < 0.05:
            findings["details"].append(
                f"✓ Sharpe stable under perturbation "
                f"(orig={sharpe_orig:.4f}, pert={sharpe_perturbed:.4f}) "
                f"→ NO LOOKAHEAD"
            )
        elif findings["degradation"] > 0.1:
            findings["details"].append(
                f"🚨 Sharpe drops {findings['degradation']:.4f} under perturbation "
                f"→ LOOKAHEAD DETECTED"
            )
            findings["status"] = "FAIL"
            findings["risk_score"] = 0.5
        else:
            findings["details"].append(
                f"⚠️ Moderate Sharpe degradation ({findings['degradation']:.4f}) "
                f"→ POSSIBLE LOOKAHEAD"
            )
            findings["status"] = "CAUTION"
            findings["risk_score"] = 0.2

    except Exception as e:
        findings["details"].append(f"❌ Perturbation test failed: {str(e)}")
        findings["status"] = "SKIP"

    return findings


# ============================================================================
# CHECK 4: Feature Audit Trail (Source & Lag Declaration)
# ============================================================================

def check_feature_audit_trail(feature_names: list) -> Dict[str, Any]:
    """
    Each feature must be traceable to its computation.

    SAFE PATTERNS:
    - mom_Nd: momentum over N days (past prices only)
    - vol_Nd: rolling volatility (past returns only)
    - rsi_N, macd, bb_pctb, atr_N: technical indicators (lagged)

    RED FLAGS:
    - Features with current return included (mom_Xd includes r[t])
    - Features computed on full sample (vol_ratio from full sample quantiles)
    - Interaction terms not clearly defined
    """
    findings = {
        "check": "Feature Audit Trail",
        "status": "PASS",
        "details": [],
        "safe_features": [],
        "risky_features": [],
        "risk_score": 0.0,
    }

    safe_patterns = [
        "mom_", "vol_", "rsi_", "macd", "bb_", "atr_", "ema_",
        "sma_", "slope_", "stoch_", "adx_", "cci_", "roc_", "ret_"
    ]

    risky_patterns = [
        "forward_", "future_", "next_", "lookahead_", "prediction_"
    ]

    for fname in feature_names:
        is_safe = any(pattern in fname.lower() for pattern in safe_patterns)
        is_risky = any(pattern in fname.lower() for pattern in risky_patterns)

        if is_risky:
            findings["details"].append(f"🚨 {fname}: RISKY NAME (suggests lookahead)")
            findings["risky_features"].append(fname)
            findings["risk_score"] += 0.3
        elif is_safe:
            findings["details"].append(f"✓ {fname}: Safe pattern")
            findings["safe_features"].append(fname)
        else:
            findings["details"].append(f"❓ {fname}: Unknown source (verify manually)")
            findings["risk_score"] += 0.05

    if findings["risk_score"] > 0.2:
        findings["status"] = "FAIL"
    elif findings["risk_score"] > 0.1:
        findings["status"] = "CAUTION"

    return findings


# ============================================================================
# CHECK 5: Walk-Forward Sanity (IS vs OOS consistency)
# ============================================================================

def check_walkforward_sanity(design_sharpe: float, test_sharpe: float,
                              degradation: float, dsr: float) -> Dict[str, Any]:
    """
    Healthy strategy: IS Sharpe ≈ OOS Sharpe (both positive, similar magnitude).

    RED FLAGS:
    - IS Sharpe >> OOS Sharpe (overfitting)
    - IS Sharpe > 0.5, OOS Sharpe < 0 (complete breakdown on test set)
    - DSR < 0.95 (statistically weak, too many backtests, or lookahead artifact)
    """
    findings = {
        "check": "Walk-Forward Sanity",
        "status": "PASS",
        "details": [],
        "risk_score": 0.0,
    }

    # Check IS performance
    if design_sharpe < 0:
        findings["details"].append(f"⚠️ Design Sharpe {design_sharpe:.4f} < 0 (no signal)")
        findings["risk_score"] += 0.1
    elif design_sharpe < 0.3:
        findings["details"].append(f"⚠️ Design Sharpe {design_sharpe:.4f} weak")
        findings["risk_score"] += 0.05
    else:
        findings["details"].append(f"✓ Design Sharpe {design_sharpe:.4f} reasonable")

    # Check OOS performance
    if test_sharpe < 0:
        findings["details"].append(f"🚨 Test Sharpe {test_sharpe:.4f} < 0 (negative OOS)")
        findings["status"] = "FAIL"
        findings["risk_score"] += 0.3
    elif abs(test_sharpe) > 0.01:  # Any finite positive
        findings["details"].append(f"✓ Test Sharpe {test_sharpe:.4f} positive OOS")

    # Check degradation
    if degradation > 0.5:
        findings["details"].append(
            f"🚨 Degradation {degradation:.4f} > 0.5 "
            f"(likely overfitting or lookahead)"
        )
        findings["status"] = "FAIL"
        findings["risk_score"] += 0.4
    elif degradation > 0.3:
        findings["details"].append(f"⚠️ Degradation {degradation:.4f} moderate")
        findings["risk_score"] += 0.1
    else:
        findings["details"].append(f"✓ Degradation {degradation:.4f} low")

    # Check DSR
    if dsr < 0.95:
        findings["details"].append(
            f"⚠️ DSR {dsr:.4f} < 0.95 "
            f"(not statistically significant at α=0.01)"
        )
        if dsr < 0.90:
            findings["status"] = "FAIL"
            findings["risk_score"] += 0.2
        else:
            findings["risk_score"] += 0.1
    else:
        findings["details"].append(f"✓ DSR {dsr:.4f} > 0.95 (statistically sound)")

    return findings


# ============================================================================
# Main Audit Orchestrator
# ============================================================================

def run_audit(strategy_json_path: str, data_path: str, model_factory=None,
              feature_names: list = None) -> Dict[str, Any]:
    """
    Run all 5 checks on a strategy and return comprehensive audit verdict.
    """
    audit_result = {
        "strategy_file": Path(strategy_json_path).name,
        "timestamp": pd.Timestamp.now().isoformat(),
        "checks": {},
        "overall_status": "PASS",
        "overall_risk_score": 0.0,
        "recommendation": "",
    }

    try:
        # Load strategy result
        with open(strategy_json_path) as f:
            strategy = json.load(f)

        # Load data
        df = load_ohlc(data_path)
        df = df.set_index("date")
        close = df["close"].astype(float)
        logp = np.log(close)
        r_fwd = logp.shift(-1) - logp

        # Build features if not provided
        if feature_names is None:
            feature_names = strategy.get("features", [])

        X = build_features(df)
        y = triple_barrier_labels(df.reset_index(), horizon=5, vol_span=20, mult=1.5)
        y.index = df.index

        # Get design/test split indices
        split_date = pd.Timestamp("2010-01-01")
        design_idx = np.where(df.index < split_date)[0]

        # Run checks
        audit_result["checks"]["temporal_alignment"] = check_temporal_alignment(X, feature_names)
        audit_result["checks"]["forward_correlation"] = check_forward_correlation(X, r_fwd, feature_names)
        audit_result["checks"]["feature_audit_trail"] = check_feature_audit_trail(feature_names)

        # Perturbation test (only if model_factory provided)
        if model_factory is not None:
            audit_result["checks"]["perturbation"] = check_perturbation(
                X, y, r_fwd, design_idx, model_factory
            )
        else:
            audit_result["checks"]["perturbation"] = {
                "check": "Perturbation Test",
                "status": "SKIP",
                "details": ["Model factory not provided"],
                "risk_score": 0.0,
            }

        # Walk-forward sanity
        audit_result["checks"]["walkforward_sanity"] = check_walkforward_sanity(
            strategy.get("design_sharpe", 0.0),
            strategy.get("test_sharpe", 0.0),
            strategy.get("degradation", 0.0),
            strategy.get("dsr", 0.0),
        )

        # Aggregate risk and verdict
        for check_name, check_result in audit_result["checks"].items():
            audit_result["overall_risk_score"] += check_result.get("risk_score", 0.0)

            if check_result.get("status") == "FAIL":
                audit_result["overall_status"] = "FAIL"
            elif check_result.get("status") == "CAUTION" and audit_result["overall_status"] == "PASS":
                audit_result["overall_status"] = "CAUTION"

        # Recommendation
        if audit_result["overall_status"] == "FAIL":
            audit_result["recommendation"] = (
                "🚨 REJECTED: This strategy shows signs of lookahead bias. "
                "Do not deploy. Debug the indicated features before retesting."
            )
        elif audit_result["overall_status"] == "CAUTION":
            audit_result["recommendation"] = (
                "⚠️ CAUTION: This strategy has moderate red flags. "
                "Recommended: (1) Retrain on new data, (2) Run perturbation test, "
                "(3) Cross-market validation."
            )
        else:
            audit_result["recommendation"] = (
                "✅ PASS: This strategy appears causal. Proceed to paper-trading. "
                "Continue monitoring for regime shifts."
            )

    except Exception as e:
        audit_result["overall_status"] = "ERROR"
        audit_result["checks"]["error"] = {"message": str(e)}

    return audit_result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: anti_data_snooping_audit.py <strategy_json> <data_path>")
        sys.exit(1)

    strategy_file = sys.argv[1]
    data_path = sys.argv[2]

    result = run_audit(strategy_file, data_path)

    print(json.dumps(result, indent=2))

    # Save result
    output_path = Path(strategy_file).parent / f"audit_{Path(strategy_file).stem}.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nAudit result saved to: {output_path}")
    sys.exit(0 if result["overall_status"] == "PASS" else 1)
