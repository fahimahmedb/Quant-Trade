---
name: quant-integrated-pipeline
description: Intègre les trois composantes (B=signal, meta-labeling=filtre, D=overlay) en pipeline complète et mesure l'effet synergique sur NDX. Combinaison validée des meilleures variantes trouvées (LogitL2 secondaire + cap 2.0× cut 90e).
tools: Bash, Read, Write, Edit, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en premier.

## Tâche : Pipeline intégrée B → meta-labeling → overlay

Valider que les trois étapes combinées réduisent le drawdown du signal actif lui-même (pas juste Buy & Hold).

### Architecture

1. **Signal primaire** : LogitL2 (de Étape B, meilleur signal trouvé)
2. **Filtre secondaire** : meta-labeling avec LogitL2 comme secondaire (meilleure variante, DSR 0.866)
3. **Gestion exposition** : overlay vol-targeting (cap 2.0×, cut 90e percentile, trouvée meilleure combo)
4. Position finale : signe(LogitL2) × confiance_meta_labeling × exposition_overlay

### Protocole figé

- Walk-forward NDX, T0=750, refit 21j, embargo 5j, coûts 5 bps
- 5 variantes testées (univers figé) :
  1. Buy & Hold (baseline)
  2. LogitL2 seul (Étape B)
  3. LogitL2 + meta-labeling (Étape B + filtre)
  4. LogitL2 + overlay (Étape B + gestion risque)
  5. LogitL2 + meta-labeling + overlay (pipeline complète)
- Métriques : Sharpe, Sortino, Calmar, MDD, Turnover, DSR (n_trials=5)

### Succès

Pipeline complète réduit MDD du signal LogitL2 de façon matérielle (ex. si LogitL2 solo a MDD −70%, combo devrait descendre vers −50%) sans perdre trop de rendement.

### Fichiers

- Crée ou modifie `src/integrated_pipeline.py` : orchestrateur qui combine les 3 composantes
- Crée `scripts/run_integrated_pipeline.py` : walk-forward complet NDX
- Produit `results/integrated_pipeline.md` : tableau 5×variantes + verdict

### Anti-data-snooping

5 variantes figées avant évaluation, DSR compte n_trials=5.

Pas de commit/push — dépose les fichiers.
