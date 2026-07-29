# Pré-enregistrement — Overlay levé "effet post-jour férié"

**Committé AVANT tout calcul.** Cycle #70 du backlog non-ML.

## Hypothèse

Les séances qui suivent une pause de marché prolongée (weekend allongé
par un jour férié, ou tout écart calendaire inhabituel entre deux
séances consécutives) montrent historiquement un comportement de
rendement différent des séances ordinaires (littérature du "holiday
effect" — Ariel 1990, Lakonishok & Smidt 1988 : les rendements des
séances pré/post-fériées sont statistiquement anormaux). Un overlay qui
reste investi 1,0x en permanence mais AMPLIFIE l'exposition sur ces
séances spécifiques pourrait battre Buy&Hold. Contrairement aux effets
calendaires déjà testés (ToM, Halloween, Santa Claus, jour-de-semaine),
ce signal est détectable directement à partir des ÉCARTS de la colonne
`date` elle-même (pas d'un calendrier de jours fériés externe), donc
sans dépendance à des données supplémentaires.

## Définition (fixée ici, avant tout résultat)

- Écart calendaire au jour t = `date(t) - date(t-1)` (en jours
  calendaires). Un écart ≥ `GAP_THRESHOLD=4` jours calendaires signale
  une pause de marché prolongée (weekend normal = 3 jours max
  vendredi→lundi ; un écart de 4+ jours implique un jour férié
  additionnel, un pont, ou une clôture exceptionnelle).
- Séance "post-jour férié" = la séance au jour t dont l'écart avec t-1
  est ≥ `GAP_THRESHOLD`.
- Position = **1,0x** en permanence, **CAP = 2,0x** le jour de la
  séance post-jour férié (day t) uniquement, **1,0x** sinon. Décision
  prise à la clôture du jour t-1 (l'écart calendaire est connu à
  l'avance, ce n'est pas une donnée de marché), appliquée au rendement
  t→t+1 (même convention `[1:]` que les autres overlays calendaires du
  backlog — ToM #8, Halloween #17, Santa Claus #64, jour-de-semaine
  #56).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (GAP_THRESHOLD=4j et CAP=2,0x fixés a priori sur
la base de la structure calendaire standard des marchés (weekend =
3 jours), aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_post_holiday_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py post_holiday_overlay`.
