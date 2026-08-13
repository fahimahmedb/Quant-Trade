# Audit adversarial — breadth « petites caps » proxy, univers point-in-time

## 1. Recalcul de la breadth par un chemin de code disjoint

Le backtest calcule la volatilité idiosyncratique par une boucle NumPy sur
fenêtres glissantes ; l'audit la recalcule par `pandas.rolling(60).std()` et
refait les médianes transversales à la main.

| Date | Breadth backtest | Breadth audit | Écart |
|---|---|---|---|
| 2015-01-02 | 0.4324 | 0.4324 | 0.00e+00 |
| 2017-04-25 | 0.4878 | 0.4878 | 0.00e+00 |
| 2019-08-15 | 0.4667 | 0.4667 | 0.00e+00 |
| 2021-12-03 | 0.4255 | 0.4255 | 0.00e+00 |
| 2024-03-28 | 0.5000 | 0.5000 | 0.00e+00 |
| 2026-07-27 | 0.4118 | 0.4118 | 0.00e+00 |

- écart maximal : **0.00e+00**

**CONFORME — les deux chemins concordent à la précision machine.**

## 2. Anti-lookahead — mutation du futur

Les prix postérieurs à l'indice 12808 (2020-10-09) sont multipliés
par 7. La breadth calculée **à** cette date doit être strictement inchangée.

- breadth avant mutation : **0.608696**
- breadth après mutation : **0.608696**

**CONFORME — aucune fuite du futur.**

## 3. Le filtre d'appartenance a-t-il réellement un effet ?

Un filtre qui ne change rien ne filtre rien. La breadth est recalculée en
forçant l'univers à **tous** les tickers disponibles : elle doit alors différer
de la version point-in-time, sinon le portage serait cosmétique.

- dates comparées : **6**
- dates où la breadth diffère : **6**
- couverture moyenne rapportée par le backtest : **88.2%**

**CONFORME — le filtre point-in-time change effectivement le signal.**

## 4. Causalité de la porte

`combined_position` consomme `gate_aligned[:-1]` : la porte appliquée au
rendement du jour t est celle observée en t−1. Vérifié sur une porte
synthétique n'ayant qu'un seul jour actif.

- indices de position modifiée : **[np.int64(20)]** (porte active au seul indice 20)

**CONFORME — décalage d un jour, aucune décision prise sur le rendement du jour même.**

## Verdict de l'audit

**CONFORME — les quatre contrôles passent.**
