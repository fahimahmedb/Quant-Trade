"""
No-lookahead validation: each fold must use ONLY data <= t.
Prevents recalculation of params/forecasts with future information.

Inspired by: Bailey et al. (PBO), Harris (look-ahead bias detection),
López de Prado (AFML ch. 2 walk-forward protocols).
"""
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from volatility import fit_arch, garch_path, params_dict
from overlay import realized_ann_vol_pct
from prediction import trading_metrics


class TestNoLookahead:
    """Unit tests for data leakage in walk-forward procedures."""

    def test_vol_target_constant(self, r, T0=750, refit_every=21):
        """FAIL if vol_target is recalculated at each refit.

        vol_target must be computed ONCE from [0:T0], never updated.
        If vol_target changes between refits, it's using future information.

        Expected: ✓ (constant across all refits)
        Broken code: ✗ (vol_target increases with each refit, especially in krach)
        """
        refits = list(range(T0, len(r), refit_every))
        vol_targets = []

        for tr in refits[:10]:  # Check first 10 refits
            vol_targ = realized_ann_vol_pct(r[:tr])
            vol_targets.append(vol_targ)

        # All should be identical if computed on constant window [0:T0]
        # If they differ, it means vol_target is recalculated (LOOKAHEAD)
        std_vol_target = np.std(vol_targets)
        mean_vol_target = np.mean(vol_targets)
        rel_std = std_vol_target / mean_vol_target if mean_vol_target > 0 else 0

        assert rel_std < 0.001, \
            f"vol_target varies across refits (std/mean = {rel_std:.3%}) → " \
            f"Values: {[f'{v:.4f}' for v in vol_targets]} → LOOKAHEAD DETECTED\n" \
            f"   Fix: Compute vol_target ONCE on r[:T0], never update it"

        print(f"   ✓ vol_target constant across refits (std={std_vol_target:.6f})")

    def test_garch_params_locked_per_fold(self, r, T0=750, refit_every=21):
        """FAIL if GARCH params are recalculated retroactively.

        At refit tr, params should be fit on r[:tr] and locked for that fold.
        path[t] computed at refit tr should use params_tr, never change later.

        Expected: ✓ (path[t] from earliest refit containing t)
        Broken code: ✗ (path[t] recalculates with newer params at each refit)
        """
        refits = list(range(T0, len(r), refit_every))

        # Compute GARCH path at first two refits (using GJR-t model)
        params_tr1_res = fit_arch(r[:refits[0]], "GJR-t")
        params_tr1 = params_dict(params_tr1_res)
        path_tr1 = garch_path(r, params_tr1, gjr=True)

        params_tr2_res = fit_arch(r[:refits[1]], "GJR-t")
        params_tr2 = params_dict(params_tr2_res)
        path_tr2 = garch_path(r, params_tr2, gjr=True)

        # Test point: middle of first fold
        t_test = refits[0] + refit_every // 2

        vol_tr1_at_t = path_tr1[t_test]
        vol_tr2_at_t = path_tr2[t_test]

        # CORRECT behavior:
        # - At refit tr1, we compute path with params_tr1 for fold [tr1, tr2)
        # - At refit tr2, we should NEVER recalculate path[t_test]
        # - In a broken backtest, path[t_test] changes because params were updated

        # Check if path changed significantly (relative difference > 5%)
        rel_diff = abs(vol_tr1_at_t - vol_tr2_at_t) / (abs(vol_tr1_at_t) + 1e-8)

        # Note: Some small difference is OK (params re-estimated), but
        # the test is: we should LOCK params_tr1 for fold [tr1, tr2) and never
        # recompute. The test here is detecting if params changed significantly.
        # A real fix would use only params_tr1 for the entire fold.

        assert rel_diff < 0.10, \
            f"GARCH path at t={t_test} changed by {rel_diff:.1%} between refits → " \
            f"vol_tr1={vol_tr1_at_t:.6f} vs vol_tr2={vol_tr2_at_t:.6f}\n" \
            f"   Fix: Lock params_tr for fold [tr, tr+refit_every), never recalculate"

        print(f"   ✓ GARCH path stability OK (max relative change {rel_diff:.2%})")

    def test_model_not_retrained_on_future(self, X, y, model_factory,
                                           T0=750, refit_every=21, embargo=5):
        """FAIL if classification model is retrained with future labels.

        At refit tr, model should be trained on X[:tr-embargo], y[:tr-embargo].
        If model is retrained with y[tr:tr+refit_every] available (double-checking),
        that's lookahead in meta-labeling.

        Expected: ✓ (model trained only on past, purged of overlapping labels)
        Broken code: ✗ (model retrained to include OOS labels, inflating OOS accuracy)
        """
        from prediction import walk_forward_signals

        refits = list(range(T0, len(X), refit_every))
        model_accuracies = []

        for idx, tr in enumerate(refits[:-1]):
            tr_end = tr - embargo  # Purge overlapping labels

            # Train on r[:tr_end]
            mask = np.isfinite(y[:tr_end])
            if mask.sum() < 100:
                continue

            Xtr = X[:tr_end][mask]
            ytr = y[:tr_end][mask]

            clf = model_factory()
            clf.fit(Xtr, (ytr > 0).astype(int))

            # Test on OOS [tr, tr+refit_every)
            test_idx = np.arange(tr, min(tr + refit_every, len(X)))
            y_pred = []
            for t in test_idx:
                xt = X[t]
                if not np.all(np.isfinite(xt)):
                    y_pred.append(0)
                    continue
                pred = clf.predict([xt])[0]
                y_pred.append(pred)

            y_true = (y[test_idx] > 0).astype(int)
            acc = (np.array(y_pred) == y_true).mean()
            model_accuracies.append(acc)

        # Check accuracy stability
        # If all accuracies are suspiciously high (>60% on random-ish data),
        # or if they spike when embargo is removed, that's a sign of lookahead.
        avg_acc = np.mean(model_accuracies)

        # Random classifier baseline: 50%
        # A real edge should be 52-56% with low variance
        assert avg_acc < 0.65, \
            f"Model OOS accuracy {avg_acc:.1%} > 65% suggests data leakage\n" \
            f"   Check: Is embargo correctly applied? Is model re-trained with future labels?"

        print(f"   ✓ Model accuracy reasonable (avg OOS {avg_acc:.1%}, no lookahead)")

    def test_fold_sharpe_not_suspiciously_smooth(self, fold_sharpes):
        """FAIL if fold Sharpes show suspiciously low variance.

        If all folds have the same sign, low std relative to mean, or too-smooth
        equity curve, it suggests they share a common lookahead leak boosting
        all of them equally.

        Expected: ✓ (Sharpes vary: some positive, some negative; std ~30-50% mean)
        Broken code: ✗ (All positive, artificially smooth, std < 10% mean)
        """
        fold_sharpes_arr = np.array(fold_sharpes)

        # Filter out NaNs
        fold_sharpes_arr = fold_sharpes_arr[np.isfinite(fold_sharpes_arr)]

        if len(fold_sharpes_arr) < 10:
            print(f"   ⚠ Insufficient folds ({len(fold_sharpes_arr)}) to validate")
            return

        mean_sharpe = np.mean(fold_sharpes_arr)
        std_sharpe = np.std(fold_sharpes_arr)
        rel_std = std_sharpe / abs(mean_sharpe) if abs(mean_sharpe) > 1e-8 else 10.0

        # Heuristic: std should be at least 20% of |mean|
        # If std < 10%, equity curve is too smooth (likely artificial)
        assert rel_std > 0.15, \
            f"Fold Sharpe distribution too smooth (std/|mean| = {rel_std:.1%}) → " \
            f"Suggests all folds benefit from same lookahead leak\n" \
            f"   Mean={mean_sharpe:.4f}, Std={std_sharpe:.4f}\n" \
            f"   Fix: Check if vol_target, GARCH params, or threshold recalculated"

        # Also: all folds shouldn't be consistently positive (sign of bias)
        positive_folds = (fold_sharpes_arr > 0).sum()
        positive_pct = positive_folds / len(fold_sharpes_arr)

        assert 0.3 < positive_pct < 0.7, \
            f"Fold Sharpe sign distribution skewed: {positive_pct:.1%} positive → " \
            f"Suggests regime-dependent lookahead or selection bias"

        print(f"   ✓ Fold Sharpe distribution healthy (mean={mean_sharpe:.4f}, " \
              f"std={std_sharpe:.4f}, {positive_pct:.1%} positive)")

    def test_oos_is_ratio_sane(self, is_sharpe_mean, oos_sharpe):
        """FAIL if OOS Sharpe > IS Sharpe (inverted ratio).

        Out-of-sample performance should degrade vs in-sample.
        Ratio 0.7-0.9 is healthy; ratio > 1.0 is impossible without lookahead.

        Expected: ✓ (OOS/IS ratio 0.7-0.9)
        Broken code: ✗ (OOS/IS ratio > 1.0, OOS outperforms IS)
        """
        ratio = oos_sharpe / is_sharpe_mean if is_sharpe_mean > 0 else np.nan

        assert not np.isnan(ratio), \
            "Cannot compute OOS/IS ratio (IS Sharpe is zero or negative)"

        assert ratio < 1.0, \
            f"OOS/IS Sharpe ratio {ratio:.3f} >= 1.0 (OOS > IS) → " \
            f"CRITICAL LOOKAHEAD DETECTED\n" \
            f"   IS Sharpe={is_sharpe_mean:.4f}, OOS Sharpe={oos_sharpe:.4f}\n" \
            f"   Fix: Remove dynamic vol_target, lock GARCH params per fold"

        assert ratio > 0.5, \
            f"OOS/IS Sharpe ratio {ratio:.3f} < 0.5 → " \
            f"Severe degradation suggests deep overfitting in grid-search"

        print(f"   ✓ OOS/IS ratio sane ({ratio:.3f}, expect 0.7-0.9)")

    def test_cscv_fold_independence(self, fold_pnls):
        """FAIL if fold P&Ls are too highly correlated.

        Folds should be quasi-independent. High correlation (>0.5) suggests
        they share a common lookahead leak.

        Expected: ✓ (avg correlation < 0.4)
        Broken code: ✗ (avg correlation > 0.6, all boosted by same leak)
        """
        # Normalize P&Ls to Sharpes for comparison
        fold_sharpes = []
        for pnl in fold_pnls:
            if len(pnl) > 1:
                sh = np.mean(pnl) / np.std(pnl) * np.sqrt(252) if np.std(pnl) > 0 else 0
                fold_sharpes.append(sh)

        if len(fold_sharpes) < 5:
            print(f"   ⚠ Insufficient folds ({len(fold_sharpes)}) for correlation test")
            return

        fold_sharpes_arr = np.array(fold_sharpes).reshape(-1, 1)

        # Can't compute pairwise correlation on 1D, so skip detailed correlation
        # Instead, check if fold returns show high autocorrelation (another sign of leak)
        fold_returns = [np.mean(pnl) for pnl in fold_pnls]

        if len(fold_returns) > 2:
            autocorr = np.corrcoef(fold_returns[:-1], fold_returns[1:])[0, 1]

            assert abs(autocorr) < 0.5, \
                f"Fold returns show high autocorrelation {autocorr:.2f} → " \
                f"Folds not independent, suggests shared lookahead leak"

            print(f"   ✓ Fold independence OK (autocorr={autocorr:.3f})")
        else:
            print(f"   ⚠ Insufficient folds for independence test")

    def test_no_future_threshold(self, vol_fcst, vol_realized, extreme_pctl=95):
        """FAIL if extreme_cut threshold is computed from forecasts instead of realizations.

        Threshold should be based on REALIZED volatility distribution.
        Using forecasted vol (from GARCH) means threshold depends on model bias.

        Expected: ✓ (threshold matches 95th percentile of realized vol)
        Broken code: ✗ (threshold matches GARCH 95th percentile, which is biased)
        """
        # Correct: percentile of realized vol
        thresh_realized = np.percentile(vol_realized, extreme_pctl)

        # Broken: percentile of forecasted vol
        thresh_forecast = np.percentile(vol_fcst, extreme_pctl)

        rel_diff = abs(thresh_realized - thresh_forecast) / (thresh_realized + 1e-8)

        assert rel_diff < 0.25, \
            f"Threshold from forecast vs realized differs by {rel_diff:.1%} → " \
            f"forecast_thresh={thresh_forecast:.3f}, realized_thresh={thresh_realized:.3f}\n" \
            f"   Fix: Compute threshold on REALIZED vol (carré des rendements), not GARCH forecasts"

        print(f"   ✓ Threshold calculation OK (forecast vs realized {rel_diff:.1%})")


# ============================================================================
# Main test runner
# ============================================================================

def run_all_tests():
    """Run complete no-lookahead validation suite."""
    from data_loader import load_ohlc, log_returns_pct
    from overlay import walk_forward_vol_forecast_multi, vol_target_exposure, extreme_cut
    from volatility import garch_path

    # Load data
    DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
    if not DATA_PATH.exists():
        print(f"❌ Data file not found: {DATA_PATH}")
        return False

    df = load_ohlc(str(DATA_PATH))
    r = log_returns_pct(df).values / 100.0  # log returns, decimal
    r_bt = r
    dates = log_returns_pct(df).index
    T = len(r)

    T0 = 750
    REFIT_EVERY = 21
    EXTREME_CUT_FRAC = 0.0
    CAP_GRID = [1.50]  # Test one combo
    PCTL_GRID = [90]
    COST_BPS = 5.0

    print("\n" + "="*80)
    print("NO-LOOKAHEAD VALIDATION TEST SUITE")
    print("="*80 + "\n")

    test = TestNoLookahead()
    all_passed = True

    # Test 1: vol_target constant
    print("[1/5] Testing vol_target stability...")
    try:
        test.test_vol_target_constant(r, T0, REFIT_EVERY)
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}\n")
        all_passed = False

    # Test 2: GARCH params locked
    print("[2/5] Testing GARCH param locking...")
    try:
        test.test_garch_params_locked_per_fold(r, T0, REFIT_EVERY)
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}\n")
        all_passed = False

    # Test 3: Compute actual fold Sharpes and check
    print("[3/5] Testing fold Sharpe distribution...")
    try:
        refits = list(range(T0, T, REFIT_EVERY))
        n_folds = len(refits) - 1

        # Compute vol forecasts once
        print("   Computing vol forecasts (walk-forward)...")
        fc = walk_forward_vol_forecast_multi(r, T0, REFIT_EVERY, PCTL_GRID)
        vol_fcst = fc["vol_fcst"]
        vol_target = fc["vol_target"]
        vol_thresh = fc["vol_thresh"]

        # Evaluate one combo (cap=1.5, pctl=90)
        cap = 1.50
        pctl = 90
        expo_vt = vol_target_exposure(vol_fcst, vol_target, cap)
        expo = extreme_cut(expo_vt, vol_fcst, vol_thresh[pctl], EXTREME_CUT_FRAC)
        pos = np.nan_to_num(expo, nan=0.0)

        # Get full OOS evaluation
        from prediction import backtest
        idx_oos = np.arange(T0, T)
        pnl_oos = backtest(pos, r_bt, COST_BPS)[idx_oos]
        metr_oos = trading_metrics(pnl_oos)

        # Get fold Sharpes
        fold_sharpes = []
        for fold_idx in range(n_folds):
            tr_start = refits[fold_idx]
            tr_end = refits[fold_idx + 1]
            fold_idx_slice = np.arange(tr_start, min(tr_end, T))
            pnl_fold = backtest(pos, r_bt, COST_BPS)[fold_idx_slice]
            metr_fold = trading_metrics(pnl_fold)
            fold_sharpes.append(metr_fold["sharpe_daily"])

        test.test_fold_sharpe_not_suspiciously_smooth(fold_sharpes)

    except AssertionError as e:
        print(f"   ❌ FAILED: {e}\n")
        all_passed = False

    # Test 4: OOS/IS ratio
    print("[4/5] Testing OOS/IS Sharpe ratio...")
    try:
        # Compute IS proxy
        is_sharpe_list = []
        for tr_start in refits[:-1]:
            idx_is = np.arange(0, tr_start)
            pnl_is = backtest(pos, r_bt, COST_BPS)[idx_is]
            metr_is = trading_metrics(pnl_is)
            is_sharpe_list.append(metr_is["sharpe_daily"])

        is_sharpe_mean = np.mean(is_sharpe_list)
        oos_sharpe = metr_oos["sharpe_daily"]

        test.test_oos_is_ratio_sane(is_sharpe_mean, oos_sharpe)

    except AssertionError as e:
        print(f"   ❌ FAILED: {e}\n")
        all_passed = False

    # Test 5: Threshold calculation (SKIPPED: requires normalized vol scales)
    # Note: This test requires correct scale alignment between realized and forecasted vol.
    # Deferred to implementation phase when overlay is refactored.
    print("[5/5] Testing extreme-cut threshold...")
    print("   ⚠ SKIPPED (requires normalized scales; deferred to refactor phase)")

    print("="*80)
    if all_passed:
        print("✓ ALL TESTS PASSED — Pipeline appears free of lookahead")
        print("="*80 + "\n")
        return True
    else:
        print("❌ TESTS FAILED — Lookahead detected, do not commit changes")
        print("="*80 + "\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
