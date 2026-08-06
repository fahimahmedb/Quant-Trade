# Pré-enregistrement — Porte breadth de momentum (#94) sous univers point-in-time réel

**Committé AVANT tout calcul.** Cycle #274 du backlog non-ML.

## Contexte et motivation

Les cycles #270/#271 ont testé deux signaux de régime agrégés sous
univers point-in-time avec des résultats opposés : la dispersion
cross-sectionnelle (#78, FAIL) et la breadth SMA200 (#96, PASS). Le
backlog a explicitement mis en pause l'extension systématique aux 5
formes de breadth restantes après le #273 (valeur informative marginale
décroissante d'un balayage non ciblé). Ce cycle reprend la piste, mais
de façon CIBLÉE : il teste une hypothèse distinctive précise plutôt
qu'une extension aveugle.

## Hypothèse de sens (déclarée AVANT tout calcul, Règle 2)

**Hypothèse distinctive** : le #78 (dispersion) est un signal RAPIDE —
calculé sur les rendements du JOUR MÊME across les titres, sensible à
la composition exacte du panneau à chaque instant. Le #96 (breadth
SMA200) est un signal LENT — fraction de titres au-dessus d'une moyenne
mobile 200j, une statistique de tendance qui change progressivement. La
breadth de momentum (#94) est également un signal LENT (fraction de
titres avec momentum 12-1 mois positif, LOOKBACK=252j) — si la
distinction vitesse-du-signal explique la divergence #78/#96, le #94
devrait, comme le #96, **survivre** au PIT. **Prédiction explicite
avant calcul : #94 survit.** Si le #94 échoue au contraire, cela
réfuterait la distinction vitesse-du-signal comme explication et
confirmerait plutôt une dépendance cas par cas sans facteur simple
identifiable (comme déjà observé pour le trio momentum stock-selection
vs les candidats volume).

## Univers et données

`data/pead/prices_pit/*.json` (178 tickers, réutilisé sans modification
depuis les cycles #264-273, aucune nouvelle donnée). Composition
historique via `ndx100_membership.tickers_as_of_date`, couverture
2015-01-01+.

## Méthode (réutilisation stricte du #94, Règle 7)

Identique au #94 : `Breadth(t) = fraction des titres RÉELLEMENT membres
du NDX-100 au jour t (au lieu des 99 membres 2026) ayant un momentum
12-1 mois positif (SKIP=21j, LOOKBACK=252j, construction #73)`,
`BREADTH_THRESHOLD=0.50`, mécanisme vol-targeting identique
(`VOL_WINDOW=20`, `TARGET_VOL_ANNUAL=0.20`, `CAP=2.0`, `COST_BPS=5.0`).
Même garde-fou anti-contamination que #270/#271 (masquage explicite des
dates hors couverture 2015+, masque NaN avant toute comparaison de
seuil pour éviter le piège « NaN >= seuil renvoie False »).

## Référence et critère de succès (renforcé, identique au #94 original)

Référence = Buy&Hold NDX-100 (identique au #94 original).

## Risques déclarés à l'avance

1. Une seule confirmation (#94 survit comme prédit) ne prouverait pas
   la distinction vitesse-du-signal de façon définitive (n=2 lents
   testés) — rapporté comme une observation cohérente, pas une loi
   générale.
2. Ce cycle teste UN signal supplémentaire avec une hypothèse
   distinctive précise — pas une reprise de l'extension systématique
   mise en pause après le #273.

## Anti-cheat

Ce fichier committé et poussé AVANT tout calcul. Sortie attendue :
`results/nonml_momentum_breadth_vol_targeting_overlay_pit_universe_result.md`.
Script : `scripts/nonml_momentum_breadth_vol_targeting_overlay_pit_universe_backtest.py`.
