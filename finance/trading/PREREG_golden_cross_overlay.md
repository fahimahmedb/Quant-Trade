# Pré-enregistrement — Overlay levé "Golden Cross" (SMA50 > SMA200)

**Committé AVANT tout calcul.** Cycle #34 du backlog non-ML. Variante du
filtre de tendance #29 (prix vs SMA200, PASS 5/5) : signal alternatif
classique ("Golden Cross" / "Death Cross"), comparant une moyenne mobile
courte (50j) à la moyenne longue (200j) plutôt que le prix directement à
la moyenne longue — filtre plus lent à changer de régime (moins de
faux signaux, mais latence d'entrée/sortie plus grande).

## Hypothèse

Le croisement SMA50/SMA200 (Golden Cross = SMA50 au-dessus de SMA200,
Death Cross = l'inverse) est un signal de tendance plus lissé que la
comparaison prix/SMA200 du #29 — potentiellement moins de turnover et
une meilleure robustesse en évitant les faux signaux de prix ponctuels
au voisinage de la SMA200.

## Définition (fixée ici, avant tout résultat)

- SMA50 et SMA200 = moyennes mobiles simples des 50 et 200 dernières
  clôtures (fenêtres causales). Les 200 premières séances (sans SMA200
  valide) restent hors échantillon testable, comme au #29.
- Position = **1.0x en permanence**, SAUF si SMA50 au jour t est
  **strictement au-dessus** de SMA200 au jour t (Golden Cross actif), où
  position = **CAP = 2.0x**. Décision prise à la clôture de t, appliquée
  au rendement t→t+1.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique (sur le même sous-échantillon
  testable, à partir du 201e jour).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x et fenêtres SMA50/SMA200 fixées a
priori, cohérentes avec la définition standard "Golden Cross" de la
littérature, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_golden_cross_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py golden_cross_overlay`.
