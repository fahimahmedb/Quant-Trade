# Pré-enregistrement — Momentum de constance (#82) sous univers point-in-time réel

**Committé AVANT tout calcul.** Cycle #266 du backlog non-ML.

## Contexte et motivation

Trois constructions de momentum stock-level sont validées dans ce
backlog : 52w-high (#4, base du #38 — SURVIT au PIT, cycle #163), 12-1
mois académique (#73 — SURVIT au PIT, cycle #265) et momentum de
constance (#82 — jamais vérifié sous PIT). Complète le tableau des trois
constructions de momentum "pures prix" (aucune n'utilise le volume,
contrairement aux #258/#261 qui ont ÉCHOUÉ au PIT au #264). Teste si le
schéma "signal prix pur survit, raffinement basé sur le volume échoue"
se généralise à la 3e construction, ou si #82 fait exception.

## Univers et données

`data/pead/prices_pit/*.json` (178 tickers, réutilisé sans modification
depuis #264/#265). Composition historique via
`ndx100_membership.tickers_as_of_date`, ancrage 2015-01-01 (identique
aux cycles précédents).

## Méthode (réutilisation stricte du #82, Règle 7)

Signal = fraction des 12 derniers blocs de 21j avec rendement positif
(N_BLOCKS=12, REBAL_EVERY=21, identiques au #82), tercile supérieur
PARMI les titres réellement membres du NDX-100 à la date de
rebalancement. Construction causale dès le départ (`lag_one_day`) — #82
a déjà été vérifié affecté MARGINALEMENT par le bug même barre le
01/08/2026 (Sharpe +0,67→+0,64 sur l'univers d'origine, contamination
limitée à 1/21 d'un seul bloc sur 12) ; ce cycle applique la même
convention causale dès le départ, pas une nouvelle correction.

## Référence et critère de succès (renforcé, identique au #82 original)

Référence = Buy&Hold équipondéré de l'univers PIT réel (même convention
que la référence originale du #82, reconstruite sur l'univers PIT pour
une comparaison cohérente).

## Hypothèse

Par analogie avec #4/#38 et #73 (tous deux survivent), on anticipe que
#82 (signal prix pur, comme les deux autres) survit également — mais
aucune garantie, rapporté tel quel. Si #82 survivait ET #258/#261
échouaient, la lecture "signal prix pur robuste / raffinement volume
fragile" se généraliserait aux 3 constructions de momentum du backlog,
pas seulement 2 sur 3.

## Anti-cheat

Ce fichier committé et poussé AVANT tout calcul. Sortie attendue :
`results/nonml_momentum_consistency_pit_universe_result.md`. Script :
`scripts/nonml_momentum_consistency_pit_universe_backtest.py`.
