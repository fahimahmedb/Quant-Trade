---
name: quant-backtest-indices
description: Backteste le meilleur pipeline validé (LogitL2+overlay optimisé) sur 3 indices externes (Russell 2000, S&P 500, DAX) pour valider la robustesse cross-market. Tâche 4.
tools: Bash, Read, Write, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en premier.

## Tâche : Backtester sur indices externes

Valider que le meilleur pipeline trouvé sur NDX (LogitL2 + overlay cap 2.0× cut 90e) se généralise à d'autres marchés/indices.

### Indices cibles

1. Russell 2000 (small-cap US) — télécharger ou utiliser source gratuite
2. S&P 500 (large-cap US) — télécharger ou utiliser source gratuite
3. DAX (large-cap Allemagne) — télécharger ou utiliser source gratuite

### Protocole figé

Même que NDX : T0=750, refit 21j, embargo 5j, triple-barrier H=5j ±1.5σ, coûts 5 bps.

Pour chaque indice : 
- Buy & Hold (baseline)
- LogitL2 seul
- LogitL2 + overlay (cap 2.0×, cut 90e)

Métriques : Sharpe, Calmar, MDD, rendement ann., DSR (n_trials=3).

### Succès

Pipeline LogitL2+overlay réduit MDD vs Buy & Hold sur **au moins 2/3 indices** de façon matérielle (>20% relatif), sans perdre l'essentiel du rendement (≥80% de BH).

### Fichiers

- Crée/modifie scripts pour télécharger et valider les 3 indices
- Crée `scripts/run_backtest_indices.py` (run pipeline sur les 3)
- Produit `results/backtest_indices.md` (3 tableaux, un par indice, + verdict cross-market)

### Anti-data-snooping

Univers figé : 3 indices, 3 variantes chacun = 9 tests. DSR compte n_trials=3 par indice (ne pas combiner statistiquement).

Pas de commit/push — dépose les fichiers.
