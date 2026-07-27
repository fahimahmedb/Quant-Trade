#!/usr/bin/env python3
"""
Détecte les candidats "quasi-PASS" d'une itération terminée : tous les
critères de performance passent (design_ann>0.55, test_ann>0.55,
degradation<0.5) sauf le DSR (seuil 0.95, correction multi-tests). Critère
fixé a priori, identique pour toutes les itérations — ne change jamais en
fonction de ce qu'on observe.

Usage: python3 scripts/find_near_miss.py <iteration>
Affiche un ID par ligne (rien si aucun candidat).
"""
import sys
import json
import glob
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0].parent

DESIGN_ANN_MIN = 0.55
TEST_ANN_MIN = 0.55
DEGRADATION_MAX = 0.5


def main():
    iteration = int(sys.argv[1])
    iter_dir = ROOT / "results" / f"iter{iteration}"

    for f in sorted(glob.glob(str(iter_dir / "strategy_*.json"))):
        d = json.load(open(f))
        if d.get("result") == "PASS":
            continue  # deja un vrai PASS, pas un quasi-PASS
        design_sharpe = d.get("design_sharpe")
        test_sharpe = d.get("test_sharpe")
        degradation = d.get("degradation")
        if design_sharpe is None or test_sharpe is None or degradation is None:
            continue
        design_ann = design_sharpe * math.sqrt(252)
        test_ann = test_sharpe * math.sqrt(252)
        if design_ann > DESIGN_ANN_MIN and test_ann > TEST_ANN_MIN and degradation < DEGRADATION_MAX:
            print(d["id"])


if __name__ == "__main__":
    main()
