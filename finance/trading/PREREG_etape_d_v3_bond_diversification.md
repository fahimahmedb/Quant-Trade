# Pré-enregistrement — Formaliser le #134 comme script officiel Étape D

**Committé AVANT tout calcul.** Cycle #144 du backlog non-ML.
**Formalisation d'infrastructure (PAS un nouveau candidat indépendant,
pas de nouvelle batterie Règle 9)** — le mécanisme du #134 a déjà été
validé (PASS niveau 1, 4/5 Règle 9, meilleur score du backlog non-ML)
dans `finance/trading/`. Ce cycle l'intègre au script officiel
`scripts/run_etape_d_v3_bond_diversification.py`, dans le MÊME style et
la MÊME structure que `run_etape_d.py`/`run_etape_d_v2.py` déjà
présents dans le repo, pour qu'il soit visible et ré-exécutable au même
niveau que les autres livrables Étape D documentés dans CLAUDE.md.

## Objet

Reproduit dans `scripts/` (racine `finance/trading/`, PAS le dossier
`scripts/` du backlog expérimental) les résultats DÉJÀ obtenus au #134
(NDX) et au #143 (Composite), avec le même format de rapport que
`run_etape_d.py` : tableau Sharpe/Sortino/Calmar/MDD/rendement
annualisé/DSR, et le critère de succès EXPLICITE déjà utilisé par le
projet (réduction MDD >25% relatif ET rendement ann. conservé ≥80% de
Buy&Hold).

## Définition (fixée ici, aucun nouveau paramètre)

- Univers de 3 variantes (N=3 pour le DSR, comme `run_etape_d.py`) :
  BuyHold, VolTarget-Défensif (#115, `TARGET_VOL_ANNUAL=20%`,
  `VOL_WINDOW=20j`, `CAP=1.0` jamais de levier), VolTarget-Défensif +
  Diversification obligataire (#134, proxy DGS10, duration modifiée 10
  ans).
- Jeux de données : Composite (5 ans) et NDX (40 ans) — les mêmes deux
  déjà utilisés par `run_etape_d.py`.
- Coûts : 5 bps aller-retour (identique à tout le repo).
- Aucun retuning : reproduit EXACTEMENT les paramètres déjà validés du
  #115/#134, pas de nouvelle recherche de paramètres.

## Ce que ce cycle NE fait PAS

Ne change AUCUN verdict Règle 9 déjà rendu sur le #134 (backlog
non-ML) — cette formalisation intègre le résultat à l'infrastructure
officielle du projet, elle ne le re-valide pas sous un nouveau
protocole. Le critère de succès rapporté ici est celui, DIFFÉRENT et
DÉJÀ EXISTANT, de l'Étape D du projet (MDD -25%/rendement ≥80%), pas le
critère Sharpe+rendement standard ni la Règle 9 du backlog non-ML.

## Anti-cheat

Ce fichier committé avant `run_etape_d_v3_bond_diversification.py`.
Aucune nouvelle donnée, aucun nouveau paramètre.
