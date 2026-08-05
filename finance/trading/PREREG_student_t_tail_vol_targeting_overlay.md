# Pré-enregistrement — Porte de queue Student-t (ν glissant, MLE) pour le vol-targeting

**Committé AVANT tout calcul.** Cycle #237 du backlog non-ML. Backlog "à
faire" épuisé après le #236 (HAR-P, FAIL) ; ce cycle reprend la 2e des 3
pistes proposées à la clôture du #235.

## Hypothèse

`diagnostics.py::fit_student_t` (Étape A, ajustement Student-t par
maximum de vraisemblance sur les rendements bruts, ν = degrés de liberté)
n'a jamais été réutilisé comme signal tradable — seule la kurtosis
empirique (moment brut, #219, PASS 4/5) a testé l'épaisseur des queues
jusqu'ici. Ce cycle teste si le ν issu d'un ajustement PARAMÉTRIQUE par
MV (plus robuste aux valeurs extrêmes individuelles qu'un moment brut
d'ordre 4, cf. la remarque du docstring sur le ν non conditionnel de
l'Étape A) apporte un signal de régime distinct.

**Distinction explicite avec le #219 (déjà testé, PASS 4/5)** : la
kurtosis empirique est un moment brut (`E[(x-μ)⁴]/σ⁴ - 3`), très sensible
aux quelques observations les plus extrêmes de la fenêtre ; ν(MLE) est
l'estimateur du paramètre de forme d'une distribution paramétrique
complète, pondérant différemment la masse des queues via la
vraisemblance plutôt qu'un moment d'ordre 4 brut — les deux peuvent
diverger sur des fenêtres avec un petit nombre d'outliers isolés. Un
résultat similaire au #219 (PASS) confirmerait la robustesse du signal de
queue de manière indépendante de l'estimateur ; un résultat different
serait informatif sur la sensibilité du #219 à ses quelques observations
extrêmes.

**Direction déclarée à l'avance (Règle 2)** : porte active (amplification
autorisée) quand `ν(t) >= médiane glissante 252j de ν`, c'est-à-dire des
queues MOINS épaisses que la norme récente (plus proche de la normale) —
même logique "calme=amplifier" que les #216/#219/#220/#223.

## Définitions et alignement causal (déclarées avant calcul)

- `ν(t)` = `fit_student_t(r[t-252:t])["nu"]` (fenêtre de 252 rendements
  STRICTEMENT antérieurs à `t`, MLE via `scipy.stats.t.fit`).
- **Ré-estimation périodique tous les REFIT_EVERY=21 jours** (valeur et
  convention réutilisées du GJR-t/HAR-P, #165/#234/#236, Règle 7),
  déclarée à l'avance pour raison de coût de calcul : `scipy.stats.t.fit`
  est un MLE numérique (~20-30ms/appel), une ré-estimation quotidienne
  sur l'historique complet des 5 marchés (~40 000 séances-marché)
  prendrait plusieurs dizaines de minutes contre quelques dizaines de
  secondes en ré-estimation tous les 21 jours — ν est maintenu constant
  entre deux ré-estimations (fonction en escalier), comme pour les
  coefficients HAR/GJR-t entre deux refits.
- `MEDIAN_WINDOW=252` réutilisé à l'identique des #78/#100/#216/#218-
  #223/#234 (Règle 7).
- Porte = `ν(t) >= rolling_median_252j(ν)(t)`.
- `Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, `1.0x` sinon — mécanisme #46 standard INCHANGÉ (VOL_WINDOW=20,
  TARGET_VOL_ANNUAL=0,20, CAP=2.0, COST_BPS=5 bps, Règle 7).
- Échantillon testable à partir de la ~504e séance (252 fenêtre d'ajustement
  + 252 médiane glissante), même ordre de grandeur que les autres portes
  de moments statistiques (#218-#223).

## Univers et période

Les 5 marchés standards du backlog (Composite, NDX, Russell 2000, S&P
500, DAX) — même périmètre que toute la lignée de portes #47-#223.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur au moins **4 des 5 marchés**, l'overlay doit battre Buy & Hold À LA
FOIS en Sharpe annualisé ET en rendement total net de coûts (règle
renforcée identique à toute la lignée #46-#236).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La ré-estimation périodique (21j) au lieu d'une fenêtre glissante
   quotidienne (comme la kurtosis pandas du #219) pourrait rendre le
   signal moins réactif, produisant un profil plus proche des estimateurs
   à mémoire longue (ATR #233, HAR-P #236, tous deux FAIL) que de la
   kurtosis quotidienne (#219, PASS).
2. `scipy.stats.t.fit` peut mal converger sur des fenêtres avec très peu
   de variance (proche de la constante) ou produire des ν aberrants sur
   de petits échantillons (252 obs) — aucun garde-fou de correction ne
   sera ajouté après avoir vu un résultat ; un ν aberrant isolé serait
   rapporté tel quel comme limite de l'estimateur.
3. Si le signal reproduit trop fidèlement celui du #219 (corrélation
   quasi parfaite), l'apport informationnel serait nul malgré un PASS —
   à documenter honnêtement si observé.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts :
`scripts/nonml_student_t_tail_vol_targeting_overlay_backtest.py` (nouveau)
et `scripts/nonml_student_t_tail_vol_targeting_overlay_audit.py`.
Vérification via `nonml_anti_cheat_check.py
student_t_tail_vol_targeting_overlay`.
