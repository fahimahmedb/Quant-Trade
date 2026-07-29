# Pré-enregistrement — Overlay levé "January Barometer" (Hirsch)

**Committé AVANT tout calcul.** Cycle #59 du backlog non-ML.

## Hypothèse

Le "January Barometer" (Yale Hirsch, *Stock Trader's Almanac*) postule
que le rendement du mois de janvier prédit le signe du rendement du
reste de l'année ("as goes January, so goes the year"). Un overlay qui
reste investi 1,0x en permanence (comme Buy&Hold) mais AMPLIFIE
l'exposition de février à décembre UNIQUEMENT les années où janvier a
été positif pourrait battre Buy&Hold, sur le même principe structurel
que les overlays calendaires déjà validés (ToM #8, Halloween #17), mais
ici la décision est prise UNE FOIS PAR AN (pas de façon récurrente
intra-mois).

## Définition (fixée ici, avant tout résultat, sur la base de la
littérature — PAS un ajustement sur les données du projet)

- Rendement de janvier de l'année Y = clôture(dernier jour de bourse de
  janvier, Y) / clôture(dernier jour de bourse de décembre, Y-1) − 1
  (définition standard du "January effect", nécessite une clôture de
  décembre de l'année précédente → la première année civile de chaque
  échantillon est exclue faute de données antérieures).
- Si rendement de janvier(Y) > 0 : position = **CAP = 2,0x** du 1er
  février au 31 décembre de l'année Y.
- Sinon : position = **1,0x** du 1er février au 31 décembre de l'année Y.
- Le mois de janvier lui-même reste toujours à **1,0x** (pas de pari sur
  janvier, seulement sur le reste de l'année conditionnellement à
  janvier).
- Décision prise à la clôture du dernier jour de janvier (connue à cette
  date), appliquée aux rendements de février à décembre de la même
  année — aucune fuite possible par construction (l'année N+1 n'affecte
  jamais l'année N).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition (2 transitions par an : entrée en février, retour à 1,0x
  en janvier suivant si le signal change).
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`), mais le
Composite (5 ans, ~4-5 observations annuelles de janvier) et le DAX/S&P
500/Russell 2000 (historique plus court que NDX) fourniront un nombre
d'observations bien plus faible que NDX (40 ans, ~40 observations
annuelles) — **prudence méthodologique déclarée a priori** : un signal
annuel avec si peu d'observations sur les marchés à historique court est
statistiquement fragile par construction, le résultat NDX (40 ans) est
le plus informatif des cinq.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2,0x identique à tous les cycles précédents,
définition du rendement de janvier fixée a priori, aucune grille testée
avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_january_barometer_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py january_barometer_overlay`.
