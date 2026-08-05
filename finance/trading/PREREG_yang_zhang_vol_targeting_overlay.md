# Pré-enregistrement — Overlay de vol-targeting, estimateur Yang-Zhang (2000)

**Committé AVANT tout calcul.** Cycle #222 du backlog non-ML. Idée #222
proposée au cycle #221, première ligne "à faire" de ce cycle.

## Hypothèse

Le #46 utilise l'écart-type close-to-close, le #50 l'estimateur
Parkinson, le #215 l'estimateur Garman-Klass, le #221 l'estimateur
Rogers-Satchell (drift-independent) — tous les trois estimateurs
range-based ignorent le SAUT clôture-veille→ouverture-du-jour (overnight
gap), limite documentée dans chacun de ces PREREG. L'estimateur de
**Yang & Zhang (2000)** est l'estimateur range-based le plus complet de
la littérature classique : il combine explicitement (a) la variance des
rendements OVERNIGHT (clôture-veille→ouverture), (b) la variance des
rendements ouverture→clôture, et (c) la composante Rogers-Satchell
intra-séance (drift-independent), pondérées par un facteur `k` qui
minimise la variance de l'estimateur combiné. C'est le seul des 4
estimateurs de cette lignée à capturer À LA FOIS le saut overnight ET la
robustesse au drift intra-séance.

Formule (par fenêtre glissante de `n=VOL_WINDOW` séances) :
- `o_i = ln(Open_i / Close_{i-1})` (rendement overnight)
- `c_i = ln(Close_i / Open_i)` (rendement ouverture→clôture)
- `rs_i` = variance Rogers-Satchell par barre (formule du #221)
- `k = 0.34 / (1.34 + (n+1)/(n-1))`
- `σ²_YZ = Var(o_i) + k·Var(c_i) + (1-k)·Mean(rs_i)` sur la fenêtre,
  `Var()` utilisant la moyenne empirique de la fenêtre (ddof=1), PAS une
  moyenne supposée nulle (contrairement à Parkinson/Garman-Klass/RS qui
  utilisent des formules par-barre sans estimation de moyenne).

## Univers et période

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — OHLC déjà en
local, aucun nouveau fetch.

## Mécanisme (identique aux #46/#50/#215/#221, seul l'estimateur change)

`Position(t) = clip(20% / vol_YangZhang_20j(t-1), 0.0, 2.0x)` — CAP et
TARGET_VOL_ANNUAL réutilisés à l'identique du #46 (Règle 7).
`VOL_WINDOW=20` réutilisé également pour `n` dans la formule YZ. Coût 5
bps aller-retour. Alignement causal : `vol_YangZhang(t)` est calculé sur
les barres `[t-VOL_WINDOW+1, t]` (n'utilise que des données connues à la
clôture du jour t), appliqué directement à `r(t)=log(close(t+1)/close(t))`
sans décalage supplémentaire (déjà causal par construction, contrairement
aux #46/#50/#215/#221 qui appliquent un décalage explicite d'un jour
après coup — équivalent au final).

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#221).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La composante overnight ajoute une variance supplémentaire qui
   pourrait AUGMENTER l'exposition moyenne au-delà de celle du #221
   (Rogers-Satchell), avec le même risque de dégradation du MDD déjà
   observé pour le #215 (Garman-Klass) sur Composite/S&P 500.
2. Le poids `k` (calibré pour minimiser la variance de l'estimateur, pas
   pour maximiser un critère de trading) pourrait donner un résultat très
   proche des #215/#221 plutôt qu'une amélioration nette, comme déjà
   observé pour le #221 vs le #215.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_yang_zhang_vol_targeting_overlay_backtest.py` (nouveau,
fonction `yang_zhang_vol_ann_lagged` gardée locale au script, contrairement
aux estimateurs précédents ajoutés à `data_loader.py`, car elle calcule
directement une SÉRIE DE VOLATILITÉ DÉJÀ FENÊTRÉE et décalée, pas une
variance par barre indépendante réutilisable telle quelle). Vérification
via `nonml_anti_cheat_check.py yang_zhang_vol_targeting_overlay`.
