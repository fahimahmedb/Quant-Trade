---
name: quant-multimodel-ensemble
description: Teste les 4 signaux primaires (BuyHold, Momentum, LogitL2, HistGB) solo et avec overlay optimisé, mesure la diversification et la robustesse de chacun. Tâche 5.
tools: Bash, Read, Write, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en premier.

## Tâche : Comparaison univers primaires complet

Valider lequel des 4 signaux primaires bénéficie le plus de l'overlay vol-targeting, et si une combinaison simple (égal-poids ou Sharpe-pondéré) bat Buy & Hold.

### Univers figé (4 signaux primaires)

1. BuyHold (baseline)
2. Momentum (signe du rendement 10j, Étape B)
3. LogitL2 (meilleur signal, Étape B)
4. HistGB (Historical Gradient Boosting, Étape B)

Pour chaque : variante **solo** et variante **+ overlay (cap 2.0×, cut 90e)** = 8 variantes.

### Protocole figé

NDX, T0=750, refit 21j, embargo 5j, coûts 5 bps. Métriques : Sharpe, Calmar, MDD, Turnover, DSR (n_trials=8).

Optionnel bonus : égal-poids (4 signaux) vs Sharpe-pondéré, avec overlay appliqué au portefeuille.

### Succès

Au moins un signal primaire (autre que BuyHold) + overlay atteint DSR ≥ BuyHold (0.987 sur NDX) ou réduit MDD de >30% sans perdre >20% rendement.

### Fichiers

- Réutilise `src/prediction.py` + `src/overlay.py` existants
- Crée `scripts/run_ensemble_comparison.py` : walk-forward sur les 8 variantes + optionnel portefeuille
- Produit `results/ensemble_comparison.md` : tableau 8 variantes, verdict sur la meilleure combo

### Anti-data-snooping

8 variantes figées (4 signaux × 2 variantes chacun), DSR compte n_trials=8. Pas d'optimisation post-hoc.

Pas de commit/push.
