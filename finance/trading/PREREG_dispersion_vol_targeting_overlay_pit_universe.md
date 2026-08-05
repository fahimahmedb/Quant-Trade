# Pré-enregistrement — Porte dispersion cross-sectionnelle (#78) sous univers point-in-time réel

**Committé AVANT tout calcul.** Cycle #270 du backlog non-ML.

## Contexte et motivation

Suite à la proposition documentée dans le backlog après le #269 : le
#78 (dispersion cross-sectionnelle NDX-100 comme porte du mécanisme
hiérarchique vol-targeting sur l'INDICE, PASS, Sharpe +0,68→+0,71) est
calculé sur le panneau de 99 titres **membres 2026** appliqué
rétroactivement à la période 2021-2026 (seule période où
`data/pead/prices/*.json` existe) — jamais vérifié contre la
composition réelle du NDX-100 à chaque date. Contrairement aux
candidats stock-SELECTION déjà vérifiés (#4/#73/#82 survivent, #258/
#261 échouent), le #78 ne sélectionne aucun titre : il calcule une
STATISTIQUE AGRÉGÉE (écart-type cross-sectionnel des rendements
quotidiens) utilisée comme porte binaire sur l'exposition à l'INDICE.

## Hypothèse de sens (déclarée AVANT tout calcul, Règle 2)

**Aucune prédiction directionnelle a priori.** Contrairement à la
sélection de titres (où utiliser la liste 2026 rétroactivement est
presque tautologique — on ne peut sélectionner que de futurs
survivants), l'effet d'un panneau restreint aux survivants sur une
statistique de DISPERSION n'a pas de sens évident : les survivants
2026 sont plus homogènes en performance (tous ont prospéré) mais pas
nécessairement moins dispersés au jour le jour (deux titres tech en
forte croissance peuvent avoir des rendements quotidiens très
différents). Ce cycle teste empiriquement, sans biais de confirmation
déclaré à l'avance.

## Univers et données

`data/pead/prices_pit/*.json` (178 tickers exploitables, réutilisé sans
modification depuis #264-266/#268-269, aucune nouvelle donnée).
Composition historique via `ndx100_membership.tickers_as_of_date` — à
CHAQUE jour de bourse (pas seulement aux dates de rebalancement, la
dispersion est une série QUOTIDIENNE, pas rebalancée mensuellement),
seuls les titres réellement membres du NDX-100 ce jour-là entrent dans
le calcul de l'écart-type cross-sectionnel. `data/nasdaq100_daily.txt`
pour l'indice (inchangé, déjà utilisé au #78).

## Méthode (réutilisation stricte du #78, Règle 7)

Identique au #78 : `Dispersion(t) = écart-type cross-sectionnel des
rendements log quotidiens des titres RÉELLEMENT membres au jour t (au
lieu des 99 membres 2026)`, `MIN_LISTED=10`, porte = `Dispersion(t) ≥
médiane glissante MEDIAN_WINDOW=252j`, mécanisme vol-targeting
identique (`VOL_WINDOW=20`, `TARGET_VOL_ANNUAL=0.20`, `CAP=2.0`,
`COST_BPS=5.0`). Échantillon restreint à la période où le signal PIT
est disponible (comme au #78 pour le signal 2026 — leçon du #77).

## Référence et critère de succès (renforcé, identique au #78 original)

Référence = Buy&Hold NDX-100 (identique au #78 original).

## Risques déclarés à l'avance

1. Le panneau PIT (178 tickers, composition variable) couvre 2015-2026
   contre 2021-2026 pour le panneau 2026 fixe — l'échantillon testable
   pourrait différer sensiblement en longueur, ce qui affecterait la
   comparabilité directe des deux versions (attendu, signalé si observé,
   pas corrigé après coup).
2. Recalculer une dispersion quotidienne (pas mensuelle) sur un univers
   dont la taille change à CHAQUE changement de composition introduit
   une possible discontinuité artificielle de l'écart-type au moment
   des changements de membres — limite reconnue à l'avance, non corrigée
   si observée (ce serait un raffinement non pré-enregistré).
3. Aucune garantie de robustesse sur MEDIAN_WINDOW — testée en grille de
   plausibilité seulement si PASS (Règle anti-snooping).

## Anti-cheat

Ce fichier committé et poussé AVANT tout calcul. Sortie attendue :
`results/nonml_dispersion_vol_targeting_overlay_pit_universe_result.md`.
Script : `scripts/nonml_dispersion_vol_targeting_overlay_pit_universe_backtest.py`.
