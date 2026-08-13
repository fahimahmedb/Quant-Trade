# Audit adversarial — breadth nette hauts-bas, univers point-in-time

## 1. Recalcul de la breadth par un chemin de code disjoint

Le backtest calcule plus-hauts et plus-bas glissants par boucles NumPy ;
l'audit par `pandas` sur la fenêtre. Aucune ligne partagée.

| Date | Breadth backtest | Breadth audit | Écart |
|---|---|---|---|
| 2015-01-02 | +0.589041 | +0.589041 | 0.00e+00 |
| 2017-04-25 | +0.573171 | +0.573171 | 0.00e+00 |
| 2019-08-15 | +0.022222 | +0.022222 | 0.00e+00 |
| 2021-12-03 | +0.053191 | +0.053191 | 0.00e+00 |
| 2024-03-28 | +0.434343 | +0.434343 | 0.00e+00 |
| 2026-07-27 | +0.059406 | +0.059406 | 0.00e+00 |

- écart maximal : **0.00e+00**

**CONFORME — les deux chemins concordent à la précision machine.**

## 2. Anti-lookahead — mutation du futur

Prix postérieurs à l'indice 12808 (2020-10-09) multipliés par 7.

- breadth avant mutation : **+0.358696**
- breadth après mutation : **+0.358696**

**CONFORME — aucune fuite du futur.**

## 3. Le filtre d'appartenance change-t-il réellement le signal ?

- dates comparées : **6**
- dates où la breadth diffère : **6**
- couverture moyenne : **88.4%**

**CONFORME — le filtre point-in-time change effectivement le signal.**

## 4. Décalage de niveau entre les deux univers

Contrôle **exigé par le pré-enregistrement** : la porte de ce candidat a un
seuil absolu, elle n'est donc pas invariante par translation du signal. Le
mécanisme décrit au PREREG suppose que l'univers biaisé — composé de sociétés
ayant survécu jusqu'en 2026 — affiche une breadth nette **plus haute**.

Mesure faite **sur les mêmes dates** dans les deux univers ; comparer les
moyennes des deux rapports confondrait effet d'univers et effet de période,
leurs fenêtres n'étant pas les mêmes.

- dates communes : **1396**
- breadth moyenne, univers point-in-time : **+16.70 pts**
- breadth moyenne, univers biaisé : **+13.55 pts**
- décalage (biaisé − point-in-time) : **-3.15 pts**
- part des séances au-dessus du seuil, point-in-time : **81.2%**
- part des séances au-dessus du seuil, biaisé : **67.0%**

Le décalage est **négatif** : l'univers biaisé affiche une breadth nette plus
**basse** que l'univers réel — soit l'inverse du mécanisme décrit avant
calcul. Le mécanisme est donc **contredit**, et c'est consigné ici plutôt
que passé sous silence.

Ce contrôle ne conditionne aucun verdict : il mesure une quantité annoncée
d'avance comme pertinente, et la publie quel que soit son signe.

## 5. Causalité de la porte

- indices de position modifiée : **[np.int64(20)]** (porte active au seul indice 20)

**CONFORME — décalage d un jour.**

## Verdict de l'audit

**CONFORME — les contrôles de validité passent.**

Le contrôle 4 est une **mesure**, pas un test : il n'entre pas dans ce verdict.
