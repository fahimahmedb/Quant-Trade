# Pré-enregistrement — Overlay avance-retard cross-marché DAX→marchés US

**Committé AVANT tout calcul.** Cycle #278 du backlog non-ML.

## Hypothèse

Le marché allemand (DAX) clôture (~11h30 ET) plusieurs heures avant la
clôture des marchés actions US (~16h00 ET), avec un chevauchement de
session partiel (DAX ouvre ~3h00 ET, avant l'ouverture US à 9h30 ET, et
reste ouvert ~2h après cette ouverture). La littérature de spillover
intermarché documente une transmission de l'information/du sentiment de
risque d'un marché ouvert plus tôt vers un marché qui ouvre plus tard
dans la même fenêtre de risque global — ici testé comme une anomalie de
CONTINUATION (pas de retournement) : un DAX positif signale un
sentiment risk-on qui se propage aux marchés US le jour suivant.

Distinct du #193 (corrélation DAX-NDX 60j comme porte défensive de
RÉGIME, un signal bivarié appliqué symétriquement aux 5 marchés, pas un
signal directionnel dérivé du DAX seul) et du #192 (force relative
Russell/S&P, pas de décalage horaire ni de marché non-US).

## Définition (fixée ici, AVANT tout calcul)

- **Signal** : `DaxRet(D-1)` = rendement log close-to-close du DAX à la
  DERNIÈRE séance DAX disponible strictement avant la date cible D
  (alignement causal par `reindex(method="ffill")` puis `shift(1)`,
  technique déjà validée aux #175/#178/#186/#187/#191/#192/#193 — gère
  nativement les calendriers de jours fériés distincts DAX/US).
- **Position** : `CAP=2,0x` (réutilisé des #8/#26/#59/#193, Règle 7) si
  `DaxRet(D-1) > 0`, sinon `1,0x`. Design overlay directionnel (jamais
  sous 1,0x) — cohérent avec la nature "signal directionnel de
  continuation" du mécanisme, pas une porte défensive de type
  macro-externe (#175-#206, qui coupent à 0,5x).
- **Direction déclarée à l'avance** : CONTINUATION (DAX positif → lever
  les marchés US le jour suivant), pas retournement — cohérence avec le
  pattern de contagion risk-on/risk-off documenté, pas choisie après
  avoir vu le résultat.

## Univers et période

**Marchés CIBLES** : Composite, NDX-100, Russell 2000, S&P 500
(`data/*.txt`) — **4 marchés, PAS 5**. Le DAX est **exclu comme
cible** : appliquer son propre signal à lui-même mesurerait
l'autocorrélation sérielle du DAX (phénomène totalement distinct,
déjà hors du périmètre de ce test), pas un spillover cross-marché —
exclusion déclarée ICI, avant tout calcul, pas après avoir vu un
résultat défavorable sur DAX.

## Critère de succès (pré-enregistré, règle renforcée ADAPTÉE au
nombre de marchés)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 3 des 4 marchés cibles** (75%, proportion la
plus proche du seuil renforcé habituel ≥4/5=80% compte tenu du nombre
de marchés réduit à 4 par l'exclusion du DAX ci-dessus). n_trials=1
(une seule définition testée : fenêtre 1 jour, CAP=2,0x, direction
continuation — aucune grille).

## Anti-cheat

Ce fichier committé avant `nonml_dax_ndx_leadlag_overlay_backtest.py`.
Vérification prévue : recalcul indépendant de l'alignement causal
(boucle explicite/searchsorted, comme #193/#195), vérification qu'aucune
valeur DAX du jour D ou postérieure n'entre dans le signal du jour D
(anti-lookahead par perturbation du futur DAX, même esprit que
#175/#193). Sortie : `results/nonml_dax_ndx_leadlag_overlay_result.md`.
