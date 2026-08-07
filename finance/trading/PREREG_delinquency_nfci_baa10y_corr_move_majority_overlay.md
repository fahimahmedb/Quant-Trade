# Pré-enregistrement — Panel élargi à 5 signaux (défaut carte + NFCI + BAA10Y + corrélation NDX-DAX + MOVE), vote majoritaire ≥4/5

**Committé AVANT tout calcul.** Cycle #363 du backlog non-ML.

## 1. Contexte et hypothèse

Suite directe de la famille de portes combinées macro-externes
(#296 ET 2/2→PASS NET, #298 OU→FAIL, #301 majorité ≥2/3→PASS NET,
#303 sizing continu→PASS, #304 panel élargi à 4 signaux majorité
≥3/4→**PASS NET, 5/5, meilleur score Règle 9 de la famille à 3/5**).
Chaque élargissement du panel avec un signal économiquement DISTINCT
a soit maintenu soit amélioré la généralisation au niveau 1 ET à la
Règle 9 (2/5→2/5→2/5→3/5 en Règle 9 au fil des panels 3→3→3→4
signaux).

**Nouvelle extension** : ajouter le **MOVE** (#357, volatilité
implicite obligataire, PASS 4/5, **1er PASS niveau 1 depuis le
Bitcoin**, et candidat avec la **meilleure couverture de scénarios de
crise de tout le backlog** — dot-com/2008/COVID/2022 tous couverts et
passés à la Règle 9 du #358) au panel déjà validé à 4 signaux (défaut
carte #286, NFCI #291, BAA10Y #199, corrélation NDX-DAX #193).
**Justification économique** : le MOVE ajoute une DIMENSION
CATÉGORIELLEMENT DISTINCTE du panel existant — la volatilité implicite
du marché des TAUX (incertitude de politique monétaire), alors que les
4 signaux déjà présents couvrent l'endettement des ménages, les
conditions financières agrégées, le prix du risque de crédit
obligataire et la contagion internationale cross-marché — AUCUN
d'entre eux ne mesure la volatilité/incertitude implicite anticipée
par le marché des options sur taux. Ce cycle teste si cette 5e
dimension, économiquement non redondante, continue la tendance
observée (diversification du panel → meilleure généralisation).

## 2. Données

Aucune nouvelle donnée. Réutilisation STRICTE (Règle 7) de toutes les
fonctions déjà validées, sans aucune modification :
`build_delinquency_series`/`load_delinquency_lag` (#286),
`build_nfci_series`/`load_nfci_lag` (#291), `load_baa10y_lag` (#199),
`build_corr_series`/`load_corr_lag` (#193),
`load_move_series`/`load_move_lag` (#357),
`expanding_tercile_gate_high` (générique, #296).

**Fenêtre testable réduite** (conséquence mécanique attendue, déclarée
à l'avance) : le MOVE démarre le 12/11/2002 (source Yahoo Finance),
plus tardif que le calendrier commun NDX-DAX déjà contraignant du
panel à 4 (~31/01/2000). **Vérifié avant calcul** : la fenêtre
commune aux 5 séries sur NDX passe de 6651 à 5951 séances (début
13/11/2002 au lieu de 31/01/2000) — réduction mécanique attendue, pas
un bug, cohérente avec la discipline déjà appliquée au #304.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
convention que toute la famille de portes combinées.

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `Votes(t)` = nombre de signaux (0 à 5) dans leur tercile expanding
  le plus HAUT parmi {défaut carte, NFCI, BAA10Y, corrélation NDX-DAX,
  MOVE}, chacun calculé avec sa fonction/décalage de publication
  propre déjà validée (aucune modification).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `Votes(t) ≥ 4` (**convention "n-1 sur n" du panel, réutilisée à
  l'identique des #301 [2/3] et #304 [3/4]** — pas un nouveau seuil
  choisi pour ce cycle), `1,0x` sinon. **Jamais de levier**. Coûts
  5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (extension mécanique d'un panel déjà validé, aucun
nouveau paramètre, aucun balayage de seuil de vote).

## 6. Prédiction déclarée à l'avance (Règle 2)

**PASS anticipé** (contrairement à la plupart des cycles récents où
la prédiction reste ouverte) : la tendance observée sur 4 extensions
consécutives du panel (#296/#301/#303/#304) est que la diversification
économique du panel **maintient ou améliore** la généralisation, sans
jamais dégrader le niveau 1 en dessous d'un PASS. Le MOVE lui-même est
un PASS niveau 1 solide (4/5) avec la meilleure couverture de crise du
backlog. Résultat rapporté tel quel, sans retuning après calcul —
**si cette prédiction est réfutée, ce sera rapporté aussi honnêtement
qu'une confirmation**.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le seuil `Votes≥4` est plus strict que `Votes≥3` (panel à 4) en
   proportion relative légèrement supérieure (80% contre 75%) — un
   temps d'activation mécaniquement plus faible pourrait réduire la
   protection effective en période de stress réel.
2. La fenêtre testable réduite (5951 contre 6651 séances) exclut la
   totalité de la bulle internet (2000-2002) du calcul du tercile
   expanding pour ce panel précis — moins de diversité de régimes dans
   l'historique de référence du seuil.
3. Le MOVE lui-même a déjà FAIL la Règle 9 (2/5, #358, coûts/SPA/DSR
   en échec) — rien ne garantit qu'il apporte une valeur ajoutée nette
   au panel une fois combiné, même s'il est solide seul au niveau 1.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_delinquency_nfci_baa10y_corr_move_majority_overlay_backtest.py`,
`scripts/nonml_delinquency_nfci_baa10y_corr_move_majority_overlay_audit.py`,
`results/nonml_delinquency_nfci_baa10y_corr_move_majority_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
