# Analyse de sensibilité DSR (Règle 9e) — cycle #116

var_trials (échelle journalière, 48 Sharpe extraits du backlog) = 0.001046. n_trials = 110 (taille du backlog, comme toute la batterie Règle 9).

## 1. Sharpe minimal requis (DSR=0,95) par candidat déjà testé

| Candidat | Séances (T) | Sharpe journalier requis | Sharpe ANNUALISÉ requis | Sharpe annualisé RÉEL obtenu |
|---|---|---|---|---|
| #111 drawdown profond | 1385 | 0.1277 | 2.03 | +0.69 |
| #112 spread décile momentum | 1385 | 0.1277 | 2.03 | +0.72 |
| #113 vote majoritaire | 1385 | 0.1277 | 2.03 | +0.73 |
| #114 pente courbe des taux | 10252 | 0.0995 | 1.58 | +0.54 |
| #115 défensif Calmar | 10252 | 0.0996 | 1.58 | +0.71 |

Le Sharpe annualisé requis dépasse le Sharpe RÉELLEMENT obtenu d'un facteur 2.2x à 3.0x selon le candidat (plus l'échantillon T est court, plus le facteur requis est élevé).

## 2. Comparaison à des repères académiques (fixés avant ce calcul, voir PREREG)

| Repère | Sharpe annualisé typique |
|---|---|
| Prime de risque actions US, long terme | 0.40-0.50 |
| Facteurs Fama-French (value/momentum) | 0.30-0.50 |
| CTA / trend-following systematique | 0.50-0.80 |
| Meilleurs fonds quant. multi-strategies (exception, freq. differente) | >2.00 (cas exceptionnel) |

Le Sharpe annualisé REQUIS par la Règle 9e pour ces candidats (1.58 à 2.03) est **supérieur à TOUS les repères académiques standards** (prime de risque, facteurs, CTA), et se rapproche seulement de la catégorie "fonds quantitatifs d'exception" -- qui opèrent à une fréquence et une diversification sans rapport avec un signal quotidien unique sur un seul indice.

## 3. Interprétation (ne change RIEN à la Règle 9e ni aux verdicts #111-115 déjà rendus)

Deux lectures possibles, non tranchées ici :

1. **La barre est correctement calibrée et ce type de stratégie (overlay directionnel quotidien sur un seul indice, mécanisme déterministe non-ML) n'a simplement pas l'edge nécessaire pour survivre à une correction honnête de n_trials=110** -- cohérent avec la conclusion de l'Étape B (aucun signal ne bat Buy&Hold à DSR>0,95) et de la validation SPA/DSR familiale du 29/07.
2. **n_trials=110 (comptage brut des lignes du backlog) surestime le nombre réel d'essais INDÉPENDANTS** -- beaucoup des 110 hypothèses sont des variations mineures d'un même mécanisme (la famille vol-targeting hiérarchique comptait déjà ~15 membres fortement corrélés, cf. audit du 29/07). Une correction par FAMILLE (comme le SPA à 13 membres) plutôt que par ligne de backlog serait méthodologiquement plus juste, mais réduirait aussi mécaniquement la sévérité du test -- **tout changement dans ce sens nécessite une justification explicite et l'accord de l'utilisateur, pas une décision unilatérale prise ici pour obtenir un résultat plus favorable.**

**Recommandation (pas une décision) : la Règle 9e reste inchangée pour l'instant.** Le point 2 mérite d'être posé explicitement à l'utilisateur plutôt que résolu silencieusement dans un sens ou l'autre.
