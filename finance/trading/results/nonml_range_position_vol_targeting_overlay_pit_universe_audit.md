# Audit adversarial — position moyenne dans le range annuel, univers point-in-time

## 1. Recalcul du signal par un chemin de code disjoint

Le backtest calcule la position dans le range par boucles NumPy ;
l'audit par `pandas` sur la fenêtre. Aucune ligne partagée.

| Date | Signal backtest | Signal audit | Écart |
|---|---|---|---|
| 2015-01-02 | 0.738512 | 0.738512 | 0.00e+00 |
| 2017-04-25 | 0.800567 | 0.800567 | 0.00e+00 |
| 2019-08-15 | 0.565557 | 0.565557 | 0.00e+00 |
| 2021-12-03 | 0.539569 | 0.539569 | 0.00e+00 |
| 2024-03-28 | 0.712734 | 0.712734 | 0.00e+00 |
| 2026-07-27 | 0.515416 | 0.515416 | 0.00e+00 |

- écart maximal : **0.00e+00**

**CONFORME — les deux chemins concordent à la précision machine.**

## 2. Anti-lookahead — mutation du futur

Prix postérieurs à l'indice 12808 (2020-10-09) multipliés par 7.

- signal avant mutation : **0.780160**
- signal après mutation : **0.780160**

**CONFORME — aucune fuite du futur.**

## 3. Le filtre d'appartenance change-t-il réellement le signal ?

- dates comparées : **6**
- dates où le signal diffère : **6**
- couverture moyenne : **87.6%**

**CONFORME — le filtre point-in-time change effectivement le signal.**

## 4. Décalage de niveau entre les deux univers

Contrôle **exigé par le pré-enregistrement**. Contrairement aux #407 et #408,
**aucun mécanisme n'a été annoncé** : mes deux dernières hypothèses de ce type
ont été contredites par la mesure, et une troisième n'aurait pas eu de meilleure
base. La quantité est donc mesurée et publiée **sans hypothèse à confirmer ou
infirmer** — ce qui la rend moins informative, et c'est le prix assumé de
l'abstention.

Mesure faite **sur les mêmes dates** dans les deux univers ; comparer les
moyennes des deux rapports confondrait effet d'univers et effet de période,
leurs fenêtres n'étant pas les mêmes.

- dates communes : **1144**
- signal moyen, univers point-in-time : **0.5352**
- signal moyen, univers biaisé : **0.5718**
- décalage (biaisé − point-in-time) : **+0.0366**
- écart-type du signal, point-in-time : **0.1342**
- écart-type du signal, biaisé : **0.1499**

Le signal est en moyenne **plus bas** sur
l'univers point-in-time que sur l'univers biaisé. Aucune interprétation n'est
proposée : la mesure est publiée telle quelle.

Ce contrôle ne conditionne aucun verdict : il mesure une quantité annoncée
d'avance comme pertinente, et la publie quel que soit son signe.

## 5. Causalité de la porte

- indices de position modifiée : **[np.int64(20)]** (porte active au seul indice 20)

**CONFORME — décalage d un jour.**

## Verdict de l'audit

**CONFORME — les contrôles de validité passent.**

Le contrôle 4 est une **mesure**, pas un test : il n'entre pas dans ce verdict.
