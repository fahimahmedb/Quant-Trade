# Pré-enregistrement — Overlay de vol-targeting, estimateur Rogers-Satchell (1991)

**Committé AVANT tout calcul.** Cycle #221 du backlog non-ML. Le
backlog "à faire" étant de nouveau épuisé (série #217-220 terminée), ce
cycle propose 3 nouvelles idées (#221-223, thème des estimateurs
range-based restants et du clustering de volatilité) et exécute
immédiatement la première.

## Hypothèse

Le #46 utilise l'écart-type close-to-close, le #50 l'estimateur
Parkinson (range haut/bas, ignore le mouvement ouverture→clôture), le
#215 l'estimateur Garman-Klass (range haut/bas + ouverture→clôture, mais
suppose un drift intra-séance NUL — limite documentée dans la
littérature originale). L'estimateur de **Rogers & Satchell (1991)** est
spécifiquement conçu pour être ROBUSTE À UN DRIFT NON NUL intra-séance
(contrairement à Parkinson et Garman-Klass), en utilisant les écarts
haut/bas et haut/bas RELATIFS À LA CLÔTURE ET À L'OUVERTURE séparément :
`RS_var = ln(H/C)·ln(H/O) + ln(L/C)·ln(L/O)`. Hypothèse : cet estimateur,
robuste à la tendance intra-séance (contexte pertinent sur des indices
actions à dérive positive de long terme), produit un mécanisme de
vol-targeting qui bat Buy & Hold en Sharpe ET en rendement total net de
coûts, comme les #46/#50/#215 déjà validés en PASS niveau 1.

## Univers et période

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — OHLC déjà en
local, aucun nouveau fetch.

## Mécanisme (identique aux #46/#50/#215, seul l'estimateur change)

`Position(t) = clip(20% / vol_RogersSatchell_20j(t-1), 0.0, 2.0x)` — CAP
et TARGET_VOL_ANNUAL réutilisés à l'identique du #46 (Règle 7).
`VOL_WINDOW=20` réutilisé également. Coût 5 bps aller-retour.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#220).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Rogers-Satchell, comme Parkinson et Garman-Klass, ne capture pas le
   saut entre la clôture de la veille et l'ouverture du jour (composante
   overnight) — seul le mouvement intra-séance est utilisé.
2. La robustesse au drift pourrait n'avoir qu'un effet marginal sur des
   séances quotidiennes où le drift intra-séance est faible en
   proportion du bruit — le résultat pourrait être très proche du #215
   (Garman-Klass) plutôt qu'apporter une information réellement nouvelle.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_rogers_satchell_vol_targeting_overlay_backtest.py`
(nouveau). Fonction `rogers_satchell_var_pct` ajoutée à `data_loader.py`
(aux côtés de `parkinson_var_pct` et `garman_klass_var_pct`, même
convention de sortie en %², alignée sur `df["date"].iloc[1:]`).
Vérification via `nonml_anti_cheat_check.py
rogers_satchell_vol_targeting_overlay`.
