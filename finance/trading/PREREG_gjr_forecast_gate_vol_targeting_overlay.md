# Pré-enregistrement — Overlay vol-targeting gaté par la prévision GJR-t walk-forward

**Committé AVANT tout calcul.** Cycle #234 du backlog non-ML.

## Hypothèse et distinction avec le #165/#166 (déjà testés)

Le #165 (`walk_forward_vol_forecast`, GJR-t, Étape C) a REMPLACÉ
l'estimateur de vol RÉALISÉE du mécanisme #46 par la vol PRÉVUE —
PASS niveau 1 sur NDX mais Règle 9 2/5 (SPA échoue, l'edge de rendement
vient presque entièrement de l'exposition moyenne, pas d'un excès de
rendement journalier). Le #166 a montré que ce remplacement ne
généralise PAS aux autres marchés une fois le financement réaliste
appliqué (Règle 10). Ce cycle teste une hypothèse **mécaniquement
distincte** : au lieu de remplacer l'estimateur, utiliser la PRÉVISION
GJR-t comme **PORTE** du mécanisme hiérarchique standard #46 (qui
continue d'utiliser la vol RÉALISÉE close-to-close comme dénominateur,
inchangée) — teste si un régime de calme ANTICIPÉ (prévu par un modèle
externe déjà validé au SPA à l'Étape C) est un meilleur filtre pour
décider QUAND amplifier l'exposition réalisée-vol que les 12 types de
porte déjà testés (tendance/calendrier/breadth/dispersion/moments/
second-ordre/clustering), tous construits à partir de statistiques
PASSÉES plutôt que d'une prévision.

**Direction déclarée à l'avance (Règle 2)** : porte active (amplification
de l'exposition réalisée-vol du #46 autorisée) quand `vol_prévue_GJR-t(t)
<= médiane glissante 252j de vol_prévue_GJR-t`, c'est-à-dire un régime de
calme ANTICIPÉ par le modèle par rapport à sa propre norme récente — même
logique "calme=amplifier" que les #216/#219/#220/#223.

## Définitions et alignement causal (déclarées avant calcul)

- `vol_prévue_GJR-t(t)` = sortie de `overlay.py::walk_forward_vol_forecast`
  (T0=750, REFIT_EVERY=21, modèle GJR-t — paramètres et fonction
  réutilisés à l'identique du #165, Règle 7 ; walk-forward déjà causal
  par construction, aucune modification).
- `MEDIAN_WINDOW=252` réutilisé à l'identique des #78/#100/#216/#218-
  #223 (Règle 7).
- Porte = `vol_prévue_GJR-t(t) <= rolling_median_252j(vol_prévue_GJR-t)(t)`.
- `Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, `1.0x` sinon — mécanisme #46 standard INCHANGÉ (VOL_WINDOW=20,
  TARGET_VOL_ANNUAL=0,20, CAP=2.0, Règle 7).

## Univers et période

**NDX (40 ans) uniquement** — même périmètre que le #165 (modèle GJR-t
validé au SPA h=1 spécifiquement sur ce marché à l'Étape C ; généraliser
à d'autres marchés nécessiterait de ré-exécuter l'Étape C sur chacun,
comme fait séparément au #166, hors périmètre de ce cycle). Échantillon
testable à partir de `T0 + MEDIAN_WINDOW ≈ 1002`e séance.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur la fenêtre OOS commune (t≥1002), l'overlay doit battre Buy & Hold
ET en Sharpe annualisé ET en rendement total net de coûts (règle
renforcée identique à toute la lignée #46-#233). Un seul marché testé
(NDX) — le seuil "≥4/5" ne s'applique pas ; verdict binaire sur ce
marché unique, comme le #165/#193 (première évaluation d'un signal
avant extension éventuelle).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le #165 a déjà montré que l'edge brut du signal GJR-t (utilisé comme
   estimateur) vient presque entièrement de l'exposition moyenne induite,
   pas d'un excès de rendement journalier (SPA p=1,0000) — en porte
   plutôt qu'estimateur, ce même signal pourrait souffrir du même
   manque de significativité sous-jacente.
2. Le nombre de ré-estimations GJR-t (~450 sur NDX) introduit un coût de
   calcul non-trivial mais déjà validé comme faisable en un cycle par le
   #165 — déclaré à l'avance pour ne pas être interprété comme un
   changement de spécification après coup si le calcul est long.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_gjr_forecast_gate_vol_targeting_overlay_backtest.py`
(nouveau, réutilise `overlay.py::walk_forward_vol_forecast` sans
modification). Vérification via `nonml_anti_cheat_check.py
gjr_forecast_gate_vol_targeting_overlay`.
