# Audit indépendant — #516, nature des PASS post-basculement

Route de calcul différente du backtest : `git log --follow` par
fichier plutôt que le scan `--diff-filter=A` du dossier entier, pour
dater l'introduction de chaque script sans réutiliser son code.

## Recalcul vs publié

| Grandeur | Recalculée | Publiée | Accord |
|---|---|---|---|
| population régime | 68 | 68 | **OUI** |
| PASS | 61 | 61 | **OUI** |
| FAIL | 7 | 7 | **OUI** |
| PROCÉDURAL | 50 | 50 | **OUI** |
| SUBSTANTIEL | 11 | 11 | **OUI** |
| substantiels avant adoption | 10 | 10 | **OUI** |
| substantiels après adoption | 1 | 1 | **OUI** |

## Cohérence interne

- PROCÉDURAL + SUBSTANTIEL == PASS : **OUI** (50+11 vs 61)
- avant_adoption + après_adoption == SUBSTANTIEL : **OUI** (10+1 vs 11)

- scripts identifiés comme vraie exception (post-adoption) par cette route indépendante : **`nonml_self_inclusion_repair_backtest.py`**

**PASS** — tous les nombres publiés par le #516 sont reproduits par une route de calcul indépendante.
