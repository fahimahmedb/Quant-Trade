#!/usr/bin/env python3
"""
Runner générique de brute force ML — remplace ml_tests_50_robust.py à partir
de l'itération 4.

Pourquoi ce runner existe : ml_tests_50_robust.py indexait ses checkpoints
uniquement par ID de test (strategy_001.json .. strategy_050.json), sans
notion d'itération. Réutiliser ce script pour une itération 4 avec de
nouvelles définitions de stratégies aurait fait "sauter" silencieusement
les nouveaux tests dont l'ID coïncide avec un ancien fichier déjà résolu
(design_sharpe non-null), en gardant le résultat obsolète d'un modèle
totalement différent. Ce runner isole chaque itération dans son propre
dossier results/iter{N}/ pour éliminer cette collision, et calcule
n_trials dynamiquement (au lieu d'une constante à remonter à la main à
chaque itération, ce qui sous-estimerait la pénalité DSR si on l'oublie).

Usage:
  python3 scripts/ml_brute_force.py <N>       # lance/reprend l'itération N
  N_WORKERS=3 python3 scripts/ml_brute_force.py 4

Chaque itération N doit déclarer son univers figé a priori dans
scripts/iterations/iterN.py (dict STRATEGIES: id -> (nom, features, factory)).
"""
import sys
import json
import os
import glob
import importlib
from pathlib import Path
import warnings
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(ROOT / "finance" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

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
# PROTOCOL (Fixed a priori — inchangé depuis l'itération 3)
# ============================================================================
T0 = 750
REFIT_EVERY = 21
EMBARGO = 21
H = 5
VOL_SPAN = 20
BARRIER_MULT = 1.5
COST_BPS = 5.0

if len(sys.argv) < 2:
    print("Usage: python3 scripts/ml_brute_force.py <iteration_number>")
    sys.exit(1)

ITERATION = int(sys.argv[1])
strategies_mod = importlib.import_module(f"iterations.iter{ITERATION}")
STRATEGIES = strategies_mod.STRATEGIES

ITER_DIR = ROOT / "results" / f"iter{ITERATION}"
ITER_DIR.mkdir(parents=True, exist_ok=True)

N_WORKERS = int(os.environ.get("N_WORKERS", "3"))


def run_strategy(test_num):
    model_name, features, factory = STRATEGIES[test_num]
    result_path = ITER_DIR / f"strategy_{test_num:03d}.json"
    print(f"\n[Iter{ITERATION} Test {test_num:2d}/{len(STRATEGIES)}] {model_name}", flush=True)

    start_time = time.time()
    result = {
        "id": test_num,
        "iteration": ITERATION,
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
        DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
        df = load_ohlc(str(DATA_PATH))
        quality_report(df)
        df = df.set_index("date")

        close = df["close"].astype(float)
        logp = np.log(close)
        r_fwd = logp.shift(-1) - logp
        r_fwd_values = r_fwd.values

        assert len(df) > T0, f"Dataset too small: {len(df)} < {T0}"

        X = build_features(df)
        y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
        y.index = df.index

        assert X.shape[0] == y.shape[0], \
            f"X/y shape mismatch: {X.shape[0]} != {y.shape[0]}"

        n = len(df)
        dates = df.index

        split_date = pd.Timestamp("2010-01-01")
        design_mask = dates < split_date
        test_mask = dates >= split_date
        design_idx = np.where(design_mask)[0]
        test_idx = np.where(test_mask)[0]

        design_n = len(design_idx)
        test_start_idx = test_idx[0] if len(test_idx) > 0 else n

        assert design_n > T0, f"Design set too small: {design_n} <= {T0}"
        assert len(test_idx) > 0, "Test set empty"

        missing_features = [f for f in features if f not in X.columns]
        assert not missing_features, \
            f"Strategy {test_num} ({model_name}): Missing features {missing_features}. Available: {list(X.columns)}"
        X_subset = X[features].copy()

        assert X_subset.shape[0] == y.shape[0], \
            f"Feature subset shape mismatch: {X_subset.shape[0]} != {y.shape[0]}"

        proba = walk_forward_proba(
            X_subset.iloc[:design_n],
            y.iloc[:design_n],
            factory,
            t0=T0,
            refit_every=REFIT_EVERY,
            embargo=EMBARGO,
            standardize=True,
        )

        assert len(proba) == design_n, \
            f"Proba shape mismatch: {len(proba)} != {design_n}"

        pos_design = np.where(np.isfinite(proba), np.where(proba > 0.5, 1.0, -1.0), 0.0)
        pnl_design = backtest(pos_design, r_fwd_values[:design_n], COST_BPS)
        design_oos = np.arange(T0, design_n)
        pnl_design_oos = pnl_design[design_oos]
        metr_design = trading_metrics(pnl_design_oos)
        design_sharpe = metr_design["sharpe_daily"]

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

            proba_test = np.full(len(test_idx), np.nan)
            for i, test_i in enumerate(test_idx):
                xt = X_subset.values[test_i]
                if np.all(np.isfinite(xt)):
                    xt = (xt - mu_design) / sd_design
                    try:
                        proba_test[i] = final_model.predict_proba(xt.reshape(1, -1))[0, 1]
                    except Exception:
                        pass

            pos_test = np.where(np.isfinite(proba_test), np.where(proba_test > 0.5, 1.0, -1.0), 0.0)
            pnl_test = backtest(pos_test, r_fwd_values[test_start_idx:test_start_idx + len(test_idx)], COST_BPS)
            metr_test = trading_metrics(pnl_test)
            test_sharpe = metr_test["sharpe_daily"]
        else:
            test_sharpe = np.nan

        degradation_ann = (design_sharpe - test_sharpe) * np.sqrt(252) if np.isfinite(test_sharpe) else np.nan

        result["design_sharpe"] = float(design_sharpe)
        result["test_sharpe"] = float(test_sharpe) if np.isfinite(test_sharpe) else None
        result["degradation"] = float(degradation_ann) if np.isfinite(degradation_ann) else None
        result["_n_design_oos"] = int(len(design_oos))
        result["_skew"] = float(metr_design.get("skew", 0.0))
        result["_kurt_excess"] = float(metr_design.get("excess_kurt", 0.0))
        result["result"] = "PENDING_DSR"

        print(f"  [{test_num:2d}] Design: {design_sharpe:.4f} daily ({design_sharpe*np.sqrt(252):.3f} ann) | "
              f"Test: {test_sharpe:.4f} daily ({test_sharpe*np.sqrt(252) if np.isfinite(test_sharpe) else float('nan'):.3f} ann)", flush=True)

    except Exception as e:
        result["result"] = "ERROR"
        result["reason"] = str(e)
        print(f"  ❌ [{test_num:2d}] ERROR: {str(e)[:80]}", flush=True)

    elapsed = time.time() - start_time
    print(f"  [{test_num:2d}] Time: {elapsed:.1f}s", flush=True)

    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    return test_num, result


def load_prior_pooled_sharpes():
    """Pool design Sharpes from every strategy ever evaluated (legacy iter1-3
    flat scheme + legacy iter1-2 aggregate + every results/iterN/ directory
    other than the current one), so n_trials/var_trials reflect the TRUE
    cumulative count of hypotheses tried on this dataset — no manual bump."""
    pooled = []

    legacy_aggregate = ROOT / "results" / "ml_tests_results.json"
    if legacy_aggregate.exists():
        with open(legacy_aggregate) as f:
            prior = json.load(f)
        pooled += [v["design_sharpe"] for v in prior.values() if v.get("design_sharpe") is not None]

    for f in glob.glob(str(ROOT / "results" / "strategy_*.json")):
        with open(f) as fh:
            d = json.load(fh)
        if d.get("design_sharpe") is not None:
            pooled.append(d["design_sharpe"])

    for d in glob.glob(str(ROOT / "results" / "iter*")):
        dirname = Path(d).name
        try:
            n = int(dirname.replace("iter", ""))
        except ValueError:
            continue
        if n == ITERATION:
            continue
        for f in glob.glob(str(Path(d) / "strategy_*.json")):
            with open(f) as fh:
                dd = json.load(fh)
            if dd.get("design_sharpe") is not None:
                pooled.append(dd["design_sharpe"])

    return pooled


def main():
    results = {}

    print("=" * 80)
    print(f"ITERATION {ITERATION} — {len(STRATEGIES)} ML STRATEGY TESTS — STRICT CAUSAL PROTOCOL")
    print(f"Parallel workers: {N_WORKERS}")
    print("=" * 80)

    todo = []
    for test_num in sorted(STRATEGIES.keys()):
        result_path = ITER_DIR / f"strategy_{test_num:03d}.json"
        if result_path.exists():
            with open(result_path) as f:
                existing = json.load(f)
            if existing.get("design_sharpe") is not None:
                results[test_num] = existing
                print(f"[Test {test_num:2d}/{len(STRATEGIES)}] {STRATEGIES[test_num][0]} — SKIP (already computed, resuming)")
                continue
        todo.append(test_num)

    print(f"{len(todo)} strategies remaining, {N_WORKERS} in parallel")

    if todo:
        with ProcessPoolExecutor(max_workers=N_WORKERS) as executor:
            futures = {executor.submit(run_strategy, tn): tn for tn in todo}
            for future in as_completed(futures):
                tn, result = future.result()
                results[tn] = result

    print("\n" + "=" * 80)
    print("PASS 2/2: DSR over pooled trials + pass/fail")
    print("=" * 80)

    pooled_sharpes = [r["design_sharpe"] for r in results.values() if r.get("design_sharpe") is not None]
    pooled_sharpes += load_prior_pooled_sharpes()

    var_trials = np.var(pooled_sharpes, ddof=1) if len(pooled_sharpes) > 1 else np.nan
    n_trials = len(pooled_sharpes)  # dynamique — plus de constante a remonter a la main
    print(f"Pooled trials for variance estimate: {n_trials} (var={var_trials:.6e})")

    for test_num in sorted(STRATEGIES.keys()):
        result = results[test_num]
        if result.get("design_sharpe") is None or "_n_design_oos" not in result:
            continue

        design_sharpe = result["design_sharpe"]
        dsr_result = dsr(
            design_sharpe,
            result["_n_design_oos"],
            var_trials=var_trials,
            n_trials=n_trials,
            skew=result["_skew"],
            kurt_excess=result["_kurt_excess"],
        )
        dsr_value = dsr_result["dsr"]

        design_sharpe_ann = design_sharpe * np.sqrt(252)
        test_sharpe = result["test_sharpe"]
        test_sharpe_ann = test_sharpe * np.sqrt(252) if test_sharpe is not None else float("nan")
        degradation_ann = result["degradation"]

        passes = (
            design_sharpe_ann > 0.55 and
            test_sharpe is not None and test_sharpe_ann > 0.55 and
            degradation_ann is not None and degradation_ann < 0.5 and
            dsr_value > 0.95
        )

        result["dsr"] = float(dsr_value)
        result["pass"] = bool(passes)
        result["result"] = "PASS" if passes else "FAIL"
        for k in ("_n_design_oos", "_skew", "_kurt_excess"):
            result.pop(k, None)

        status = "✅" if passes else "❌"
        print(f"  [{test_num:2d}] {status} Design_ann: {design_sharpe_ann:.3f} | "
              f"Test_ann: {test_sharpe_ann:.3f} | DSR: {dsr_value:.4f}")

        result_path = ITER_DIR / f"strategy_{test_num:03d}.json"
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)

    passed = sum(1 for r in results.values() if r.get("result") == "PASS")

    print(f"\n" + "=" * 80)
    print(f"ITERATION {ITERATION} RESULTS: {passed} PASS / {len(STRATEGIES) - passed} FAIL/ERROR")
    print(f"=" * 80)

    summary_path = ROOT / "results" / f"iteration_{ITERATION}_summary.json"
    with open(summary_path, "w") as f:
        json.dump({"total": len(STRATEGIES), "passed": passed, "n_trials_pooled": n_trials,
                   "timestamp": pd.Timestamp.now().isoformat()}, f)

    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
