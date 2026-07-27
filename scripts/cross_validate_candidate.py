#!/usr/bin/env python3
"""
Test de confirmation hors-echantillon pour UN candidat "quasi-PASS" d'une
iteration de brute force ML, sur 3 indices externes jamais touches par le
protocole (Russell 2000, S&P 500, DAX) — testes EN PARALLELE (un process par
indice) pour diviser le temps total par ~3 par rapport a un run sequentiel.

Usage:
  python3 scripts/cross_validate_candidate.py <iteration> <id>

Definition du candidat prise TELLE QUELLE depuis scripts/iterations/iterN.py
(memes hyperparametres, memes features) — AUCUNE modification, AUCUN tuning.
C'est un test de confirmation, pas une etape de selection : le but est de
verifier si le signal replique sur un marche different, pas de l'ameliorer.

Le resultat est append-only dans results/cross_market_confirmations.md
(committe) — ce fichier ne doit JAMAIS servir a orienter la conception des
iterations suivantes (pas de retuning retroactif sur un "quasi-PASS").
"""
import sys
import os
import json
import importlib
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ProcessPoolExecutor, as_completed

# 3 indices testes en parallele (1 process chacun) ; cap BLAS/OpenMP a 1
# thread/process pour eviter l'oversubscription des 4 coeurs disponibles,
# meme principe que scripts/ml_brute_force.py.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(ROOT / "finance" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report
from prediction import build_features, triple_barrier_labels, walk_forward_proba, backtest, trading_metrics

T0 = 750
REFIT_EVERY = 21
EMBARGO = 21
H = 5
VOL_SPAN = 20
BARRIER_MULT = 1.5
COST_BPS = 5.0

INDICES = {
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}

# Fixes au moment du submit() pour que chaque worker sache quel candidat
# reevaluer sans avoir a pickler la factory (lambda) elle-meme.
ITERATION = None
STRAT_ID = None


def test_one_index(idx_name, fname):
    """Tourne dans un process separe : recharge le candidat depuis
    scripts/iterations/iterN.py (fork, deja en memoire) et l'evalue sur UN
    indice. Retourne (idx_name, ligne_de_rapport)."""
    mod = importlib.import_module(f"iterations.iter{ITERATION}")
    _, features, factory = mod.STRATEGIES[STRAT_ID]

    path = ROOT / "data" / fname
    if not path.exists():
        return idx_name, f"- {idx_name}: fichier absent, skip"

    df = load_ohlc(str(path))
    quality_report(df)
    df = df.set_index("date")
    close = df["close"].astype(float)
    logp = np.log(close)
    r_fwd = (logp.shift(-1) - logp).values
    X = build_features(df)
    y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
    y.index = df.index
    n = len(df)
    if n <= T0 + 100:
        return idx_name, f"- {idx_name}: historique trop court ({n} lignes), skip"

    missing = [f for f in features if f not in X.columns]
    if missing:
        return idx_name, f"- {idx_name}: features manquantes {missing}, skip"

    X_subset = X[features]
    proba = walk_forward_proba(X_subset, y, factory, t0=T0, refit_every=REFIT_EVERY,
                                embargo=EMBARGO, standardize=True)
    pos = np.where(np.isfinite(proba), np.where(proba > 0.5, 1.0, -1.0), 0.0)
    pnl = backtest(pos, r_fwd, COST_BPS)
    oos = np.arange(T0, n)
    metr = trading_metrics(pnl[oos])
    sharpe_ann = metr["sharpe_daily"] * np.sqrt(252)
    return idx_name, f"- {idx_name}: n={n}, OOS obs={len(oos)}, Sharpe ann = {sharpe_ann:.3f}"


def main():
    global ITERATION, STRAT_ID

    if len(sys.argv) < 3:
        print("Usage: python3 scripts/cross_validate_candidate.py <iteration> <id>")
        sys.exit(1)

    ITERATION = int(sys.argv[1])
    STRAT_ID = int(sys.argv[2])

    mod = importlib.import_module(f"iterations.iter{ITERATION}")
    name, features, factory = mod.STRATEGIES[STRAT_ID]

    orig_path = ROOT / "results" / f"iter{ITERATION}" / f"strategy_{STRAT_ID:03d}.json"
    orig = json.loads(orig_path.read_text()) if orig_path.exists() else {}
    orig_design_ann = orig.get("design_sharpe", 0) * np.sqrt(252) if orig.get("design_sharpe") is not None else None
    orig_test_ann = orig.get("test_sharpe", 0) * np.sqrt(252) if orig.get("test_sharpe") is not None else None

    header = [
        f"## Itération {ITERATION}, id {STRAT_ID} — {name}",
        f"Testé le {datetime.now(timezone.utc).isoformat()}",
        f"Features: {features}",
        f"NDX (référence, design/test): design_ann={orig_design_ann}, test_ann={orig_test_ann}, "
        f"degradation={orig.get('degradation')}, dsr={orig.get('dsr')}",
        "",
        "Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :",
    ]
    for h in header:
        print(h)

    results_by_index = {}
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(test_one_index, idx_name, fname): idx_name
                   for idx_name, fname in INDICES.items()}
        for future in as_completed(futures):
            idx_name, line = future.result()
            results_by_index[idx_name] = line
            print(line, flush=True)

    # Ordre stable dans le log, independant de l'ordre de complétion
    body = [results_by_index[idx_name] for idx_name in INDICES]

    report = "\n".join(header + body) + "\n"
    log_path = ROOT / "results" / "cross_market_confirmations.md"
    with open(log_path, "a") as f:
        f.write(report + "\n---\n\n")
    print(f"\nAppended to {log_path}")


if __name__ == "__main__":
    main()
