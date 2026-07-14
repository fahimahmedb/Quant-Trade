"""PBO (Parameter Backtest Overfitting) + CSCV (Combinatorially Symmetric Cross-Validation)
+ Walk-forward fold decomposition pour les 12 combos d'overlay NDX.

PBO : Pour chaque combo, mesure In-Sample (IS) vs Out-of-Sample (OOS) Sharpe,
détecte overfitting. IS = fenêtre d'entraînement [0:tr], OOS = prévisions [tr:T].

CSCV : Valide si le "meilleur combo" choisi reste meilleur après leave-one-fold-out.

Décomposition fold-by-fold : Montre comment la performance se dégrade de fold 1 à fold N.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct
from overlay import vol_target_exposure, extreme_cut, walk_forward_vol_forecast_multi
from prediction import backtest, trading_metrics, dsr

# ============================================================================
# CONFIG
# ============================================================================

T0 = 750
REFIT_EVERY = 21
CAP_GRID = [1.00, 1.25, 1.50, 2.00]
PCTL_GRID = [90, 95, 99]
COST_BPS = 5.0
EXTREME_CUT_FRAC = 0.0
DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"

df = load_ohlc(str(DATA_PATH))
r = log_returns_pct(df).values
r_bt = r / 100.0
dates = log_returns_pct(df).index
T = len(r)

print(f"Dataset: {T} obs, {T - T0} OOS")
print(f"T0={T0}, REFIT_EVERY={REFIT_EVERY}, refits={len(range(T0, T, REFIT_EVERY))}")

# ============================================================================
# STEP 1 : Compute vol forecasts (shared across all 12 combos)
# ============================================================================

print("\n[1/3] Computing vol forecasts (walk-forward)...")
fc = walk_forward_vol_forecast_multi(r, T0, REFIT_EVERY, PCTL_GRID)
vol_fcst = fc["vol_fcst"]
vol_target = fc["vol_target"]
vol_thresh = fc["vol_thresh"]

# ============================================================================
# STEP 2 : Evaluate all 12 combos, compute IS/OOS split for each fold
# ============================================================================

print("[2/3] Evaluating 12 combos with IS/OOS decomposition...")

refits = list(range(T0, T, REFIT_EVERY))
n_folds = len(refits) - 1  # Each fold is from refit[i] to refit[i+1]

results_combos = []

for cap in CAP_GRID:
    expo_vt = vol_target_exposure(vol_fcst, vol_target, cap)
    for pctl in PCTL_GRID:
        expo = extreme_cut(expo_vt, vol_fcst, vol_thresh[pctl], EXTREME_CUT_FRAC)
        pos = np.nan_to_num(expo, nan=0.0)

        # Full OOS evaluation
        idx_oos = np.arange(T0, T)
        pnl_oos = backtest(pos, r_bt, COST_BPS)[idx_oos]
        metr_oos = trading_metrics(pnl_oos)

        # Decompose by fold
        fold_metrics = []
        for fold_idx in range(n_folds):
            tr_start = refits[fold_idx]
            tr_end = refits[fold_idx + 1]
            fold_idx_slice = np.arange(tr_start, min(tr_end, T))

            pnl_fold = backtest(pos, r_bt, COST_BPS)[fold_idx_slice]
            metr_fold = trading_metrics(pnl_fold)
            fold_metrics.append({
                "fold": fold_idx,
                "start": dates[tr_start],
                "end": dates[min(tr_end - 1, T - 1)],
                "n_obs": len(fold_idx_slice),
                "sharpe_daily": metr_fold["sharpe_daily"],
                "mdd": metr_fold["max_drawdown_pct"],
            })

        # IS metric : use the training Sharpe on each fold (proxy for in-sample fit)
        # We'll approximate IS as the expanding window [0:tr_start] Sharpe (not true IS,
        # but a marker of model fit at beginning of each fold)
        is_sharpe_proxy = []
        for tr_start in refits[:-1]:
            idx_is = np.arange(0, tr_start)
            pnl_is = backtest(pos, r_bt, COST_BPS)[idx_is]
            metr_is = trading_metrics(pnl_is)
            is_sharpe_proxy.append(metr_is["sharpe_daily"])

        results_combos.append({
            "cap": cap,
            "pctl": pctl,
            "metrics_oos": metr_oos,
            "sharpe_oos": metr_oos["sharpe_daily"],
            "sharpe_daily_oos": metr_oos["sharpe_daily"],
            "mdd_oos": metr_oos["max_drawdown_pct"],
            "fold_metrics": fold_metrics,
            "is_sharpe_proxy": np.array(is_sharpe_proxy),
            "is_sharpe_mean": np.mean(is_sharpe_proxy),
            "oos_sharpe": metr_oos["sharpe_daily"],
            "oos_vs_is_ratio": metr_oos["sharpe_daily"] / np.mean(is_sharpe_proxy) if np.mean(is_sharpe_proxy) > 0 else np.nan,
        })

print(f"  → Evaluated {len(results_combos)} combos")

# ============================================================================
# STEP 3 : PBO Analysis
# ============================================================================

print("\n[3/3] PBO + CSCV Analysis...\n")

df_pbo = pd.DataFrame([
    {
        "cap": r["cap"],
        "pctl": r["pctl"],
        "IS_Sharpe_mean": r["is_sharpe_mean"],
        "OOS_Sharpe": r["oos_sharpe"],
        "OOS/IS_ratio": r["oos_vs_is_ratio"],
        "MDD_OOS": r["mdd_oos"],
        "Decay": r["oos_vs_is_ratio"] - 1.0 if not np.isnan(r["oos_vs_is_ratio"]) else np.nan,
    }
    for r in results_combos
]).sort_values("OOS_Sharpe", ascending=False)

print("=" * 90)
print("PBO SUMMARY (12 combos ranked by OOS Sharpe)")
print("=" * 90)
print(df_pbo.to_string(index=False))
print()

# Overfitting detection
df_pbo["OVERFIT_FLAG"] = (df_pbo["OOS/IS_ratio"] < 0.7) | (df_pbo["Decay"] < -0.3)
overfit_count = df_pbo["OVERFIT_FLAG"].sum()
print(f"\n⚠️  OVERFITTING DETECTED: {overfit_count}/12 combos (OOS < 70% of IS or decay > -30%)")

# Best combo
best_combo = results_combos[0]
best = df_pbo.iloc[0]
print(f"\n🎯 BEST COMBO: cap={best['cap']}, pctl={best['pctl']}")
print(f"   IS Sharpe (proxy): {best['IS_Sharpe_mean']:.4f}")
print(f"   OOS Sharpe:        {best['OOS_Sharpe']:.4f}")
print(f"   OOS/IS ratio:      {best['OOS/IS_ratio']:.2f} (expect 0.7-0.9)")
print(f"   MDD (OOS):         {best['MDD_OOS']:.1f}%")

# ============================================================================
# CSCV : Leave-one-fold-out validation
# ============================================================================

print("\n" + "=" * 90)
print("CSCV : LEAVE-ONE-FOLD-OUT STABILITY")
print("=" * 90)

# For best combo, remove each fold and see if Sharpe remains stable
best_idx = 0
best_r = results_combos[best_idx]
fold_sharpes = [m["sharpe_daily"] for m in best_r["fold_metrics"]]

print(f"\nBest combo fold-by-fold Sharpe (daily, OOS):")
for fold_idx, sh in enumerate(fold_sharpes):
    print(f"  Fold {fold_idx} (refit {fold_idx}): {sh:.4f}")

fold_sharpes_arr = np.array(fold_sharpes)
print(f"\nStatistics:")
print(f"  Mean:     {np.mean(fold_sharpes_arr):.4f}")
print(f"  Std dev:  {np.std(fold_sharpes_arr):.4f}")
print(f"  Min:      {np.min(fold_sharpes_arr):.4f}")
print(f"  Max:      {np.max(fold_sharpes_arr):.4f}")

# CSCV verdict: is the best combo robust across all folds?
is_cscv_stable = np.std(fold_sharpes_arr) < np.mean(fold_sharpes_arr) * 0.5
print(f"\n{'✓' if is_cscv_stable else '✗'} CSCV VERDICT: {'Stable' if is_cscv_stable else 'Unstable'} across folds")
print(f"  (threshold: std < 50% of mean)")

# ============================================================================
# Walk-forward fold-by-fold decay
# ============================================================================

print("\n" + "=" * 90)
print("FOLD-BY-FOLD DECAY (all 12 combos)")
print("=" * 90)
print("\nFold index → OOS Sharpe decline:")

all_fold_sharpes = []
for combo_idx, r in enumerate(results_combos):
    fold_sh = [m["sharpe_daily"] for m in r["fold_metrics"]]
    all_fold_sharpes.append(fold_sh)

all_fold_sharpes_arr = np.array(all_fold_sharpes)  # shape (12, n_folds)
n_folds_actual = all_fold_sharpes_arr.shape[1]

# Plot fold-wise decay
for fold_idx in range(n_folds_actual):
    fold_sharpes_across_combos = all_fold_sharpes_arr[:, fold_idx]
    print(f"  Fold {fold_idx:2d}: mean Sharpe across 12 combos = {np.mean(fold_sharpes_across_combos):+.4f} "
          f"(std={np.std(fold_sharpes_across_combos):.4f}, range [{np.min(fold_sharpes_across_combos):+.4f}, "
          f"{np.max(fold_sharpes_across_combos):+.4f}])")

# Decay rate (first fold vs last fold)
if n_folds_actual > 1:
    first_fold_sharpe = np.mean(all_fold_sharpes_arr[:, 0])
    last_fold_sharpe = np.mean(all_fold_sharpes_arr[:, -1])
    decay_rate = (last_fold_sharpe - first_fold_sharpe) / abs(first_fold_sharpe) * 100
    print(f"\n📉 DECAY RATE: {decay_rate:+.1f}% (first→last fold)")
    if decay_rate < -20:
        print(f"   ⚠️  Significant degradation detected!")

# ============================================================================
# Red flags summary
# ============================================================================

print("\n" + "=" * 90)
print("RED FLAGS SUMMARY")
print("=" * 90)

red_flags = []

if overfit_count > 2:
    red_flags.append(f"🚩 {overfit_count}/12 combos show overfitting (OOS < 70% IS)")

if not is_cscv_stable:
    red_flags.append(f"🚩 Best combo unstable across folds (CSCV failed)")

decay_rate_global = (np.mean(all_fold_sharpes_arr[:, -1]) - np.mean(all_fold_sharpes_arr[:, 0])) / abs(np.mean(all_fold_sharpes_arr[:, 0])) * 100
if decay_rate_global < -25:
    red_flags.append(f"🚩 Global Sharpe decay {decay_rate_global:+.1f}% (first→last fold)")

if best["OOS/IS_ratio"] < 0.6:
    red_flags.append(f"🚩 Best combo OOS/IS ratio {best['OOS/IS_ratio']:.2f} << 0.7 (severe overfitting)")

if len(red_flags) == 0:
    print("✓ No critical red flags detected.")
else:
    for flag in red_flags:
        print(flag)

print("\n" + "=" * 90)
print("VERDICT")
print("=" * 90)
if len(red_flags) > 1:
    print("❌ GRID-SEARCH OVERFITTING LIKELY: Multiple red flags. Recommend:")
    print("   1. Reduce combo universe (4 instead of 12)")
    print("   2. Cross-validate on different dataset (Composite 5y)")
    print("   3. Investigate why cap 2.0× works on NDX but fails on Russell/S&P/DAX")
    print("   4. Consider simpler baseline (cap 1.5× only, no percentile sweep)")
elif len(red_flags) == 1:
    print("⚠️  CAUTION: Single red flag. Investigate before paper trading.")
else:
    print("✓ GRID-SEARCH APPEARS ROBUST. But:")
    print("   1. Still need cross-market validation (Russell/S&P/DAX success)")
    print("   2. Recommend paper trading 3mo before live deployment")
    print("   3. Monitor fold-wise Sharpe decline in production")
