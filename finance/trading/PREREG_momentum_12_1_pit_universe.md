# Pré-enregistrement — Momentum 12-1 (#73) sous univers point-in-time réel

**Committé AVANT tout calcul.** Cycle #265 du backlog non-ML.

## Contexte et motivation

Le #264 a découvert que les deux candidats de la catégorie volume
(#258 momentum+turnover, #261 Amihud illiquidité) basculent NETTEMENT
en FAIL sous l'univers point-in-time réel — contrairement au #38 dont
l'edge avait survécu à la même correction. Question laissée ouverte par
le #264 : le #258 est un DOUBLE tri (momentum #73 PUIS turnover) — sa
chute sous PIT pourrait provenir (a) du momentum lui-même (#73, jamais
vérifié sous PIT), (b) du second tri turnover spécifiquement, ou (c)
des deux. **Ce cycle isole la question (a)** en testant le #73 SEUL
(sans le second tri) sous l'univers point-in-time — jamais fait
jusqu'ici, alors que l'infrastructure (composition PIT, prix PIT) existe
depuis le #163 et que #73 est utilisé comme brique de base de 3 autres
cycles du backlog (#74, #79, #258).

## Univers et données

`data/pead/prices_pit/*.json` (178 tickers exploitables, déjà utilisé
au #264, aucune nouvelle donnée — le volume n'est PAS nécessaire ici,
#73 est un signal prix pur). Composition historique via
`ndx100_membership.tickers_as_of_date`, ancrage 2015-01-01 (identique
au #163/#264).

## Méthode (réutilisation stricte du #73, Règle 7)

`momentum(t) = close(t-SKIP)/close(t-LOOKBACK) - 1`, SKIP=21,
LOOKBACK=252 (identiques au #73), tercile supérieur PARMI les titres
réellement membres du NDX-100 à la date de rebalancement (au lieu du
tercile parmi les 99 membres 2026 appliqués rétroactivement).
Rebalancement mensuel (REBAL_EVERY=21, identique). Construction causale
dès le départ (`lag_one_day`, comme pour tous les scripts depuis le
balayage #252-260 — #73 lui-même est un cas particulier déjà vérifié
"non affecté" par le bug même barre le 01/08/2026, SKIP=21j excluant
déjà close(t), donc `lag_one_day` ici n'est qu'une précaution
supplémentaire cohérente avec la convention actuelle, pas une
correction d'un défaut connu).

## Référence et critère de succès (renforcé, identique au #73 original)

Référence = **Buy&Hold équipondéré de l'univers PIT réel** (même
convention que la référence du #73 original, reconstruite sur le même
univers PIT pour une comparaison cohérente — pas la référence du #258,
mécanisme différent).

## Hypothèse

Aucune prédiction chiffrée. Deux issues informatives : (1) si #73 SURVIT
au PIT (comme #38), alors la chute du #258 est spécifiquement imputable
au second tri turnover — la survivorship n'est pas un problème général
des signaux stock-selection de ce backlog ; (2) si #73 ÉCHOUE déjà seul,
la construction "12-1 mois" elle-même serait partiellement
survivorship-biaisée, ce qui reclasserait aussi #74/#79/#82(?)/#83 comme
suspects (mais ne serait pas re-testé dans CE cycle, Règle 2 — un
constat, pas une nouvelle vague de tests automatique).

## Anti-cheat

Ce fichier committé et poussé AVANT tout calcul. Sortie attendue :
`results/nonml_momentum_12_1_pit_universe_result.md`. Script :
`scripts/nonml_momentum_12_1_pit_universe_backtest.py`.
