# Pré-enregistrement — Porte combinée (ET) kurtosis + ν Student-t pour le vol-targeting

**Committé AVANT tout calcul.** Cycle #240 du backlog non-ML. Backlog "à
faire" épuisé après le #239 ; ce cycle reprend la 2e des 3 pistes
proposées à la clôture du #238.

## Hypothèse

Deux portes de queue déjà validées séparément dans ce backlog par des
constructions méthodologiquement distinctes — kurtosis empirique glissante
(#219, PASS 4/5, seul DAX échoue) et ν glissant par MLE Student-t (#237,
PASS 4/5, seul DAX échoue, mais audit ayant révélé une fragilité
numérique de l'estimateur, cf. #238) — n'ont jamais été COMBINÉES. Ce
cycle teste une construction jamais essayée dans ce backlog : exiger
l'ACCORD des deux signaux (porte ET) plutôt qu'un seul, sur l'hypothèse
que deux mesures indépendantes de l'épaisseur des queues convergeant vers
le même diagnostic de régime "calme" constituent un signal plus fiable
qu'une seule (et, incidemment, que le bruit d'estimation documenté sur le
ν du #237 soit partiellement filtré par l'exigence de double confirmation).

**Direction déclarée à l'avance (Règle 2)** : porte active
`= calm_kurtosis_mask(r) AND calm_nu_mask(r)`, où chaque sous-porte
reprend EXACTEMENT sa propre définition déjà validée (#219 : kurtosis
glissante ≤ sa médiane 252j ; #237 : ν glissant ≥ sa médiane 252j) —
aucune des deux définitions n'est modifiée, seule leur combinaison
logique est nouvelle.

## Définitions et alignement causal (déclarées avant calcul)

- Réutilise `calm_kurtosis_mask` (`nonml_kurtosis_vol_targeting_overlay_
  backtest.py`, KURT_WINDOW=252, MEDIAN_WINDOW=252) et `calm_nu_mask`
  (`nonml_student_t_tail_vol_targeting_overlay_backtest.py`, NU_WINDOW=252,
  REFIT_EVERY=21, MEDIAN_WINDOW=252) SANS AUCUNE MODIFICATION (Règle 7),
  importées directement.
- `Position(t) = clip(20% / vol_close-to-close_20j(t-1), 1.0, 2.0x)` si
  porte combinée active, `1.0x` sinon — mécanisme #46 standard INCHANGÉ
  (VOL_WINDOW=20, CAP=2.0, COST_BPS=5 bps, Règle 7).
- Échantillon testable à partir de la 504e séance (borne la plus stricte
  des deux sous-portes, `NU_WINDOW + MEDIAN_WINDOW`, identique au #237).

## Univers et période

Les 5 marchés standards du backlog (Composite, NDX, Russell 2000, S&P
500, DAX) — même périmètre que #219 et #237.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur au moins **4 des 5 marchés**, l'overlay doit battre Buy & Hold À LA
FOIS en Sharpe annualisé ET en rendement total net de coûts (règle
renforcée identique à toute la lignée #46-#239).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La porte ET est mathématiquement PLUS RESTRICTIVE que chacune de ses
   deux composantes (active seulement quand les deux s'accordent) — elle
   pourrait réduire le temps d'exposition amplifiée au point de ne plus
   capter suffisamment de rendement, même si la qualité du signal
   s'améliore (même risque générique que toute conjonction de portes).
2. Si les deux signaux sont fortement corrélés (les deux mesurent
   l'épaisseur des queues), la porte ET pourrait être presque identique à
   chacune des deux prises séparément, sans apport réel — à documenter
   honnêtement si observé (comparaison du %j actif combiné vs individuel).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts :
`scripts/nonml_kurtosis_nu_combined_vol_targeting_overlay_backtest.py`
(nouveau, importe les deux fonctions de porte existantes sans les modifier)
et `scripts/nonml_kurtosis_nu_combined_vol_targeting_overlay_audit.py`.
Vérification via `nonml_anti_cheat_check.py
kurtosis_nu_combined_vol_targeting_overlay`.
