# Audit adversarial — breadth de faiblesse, univers point-in-time

## 1. Recalcul de la breadth par un chemin de code disjoint

Le backtest calcule plus-hauts et plus-bas glissants par boucles NumPy ;
l'audit par `pandas` sur la fenêtre. Aucune ligne partagée.

| Date | Breadth backtest | Breadth audit | Écart |
|---|---|---|---|
| 2015-01-02 | +0.000000 | +0.000000 | 0.00e+00 |
| 2017-04-25 | +0.073171 | +0.073171 | 0.00e+00 |
| 2019-08-15 | +0.100000 | +0.100000 | 0.00e+00 |
| 2021-12-03 | +0.180851 | +0.180851 | 0.00e+00 |
| 2024-03-28 | +0.030303 | +0.030303 | 0.00e+00 |
| 2026-07-27 | +0.069307 | +0.069307 | 0.00e+00 |

- écart maximal : **0.00e+00**

**CONFORME — les deux chemins concordent à la précision machine.**

## 2. Anti-lookahead — mutation du futur

Prix postérieurs à l'indice 12808 (2020-10-09) multipliés par 7.

- breadth avant mutation : **+0.010870**
- breadth après mutation : **+0.010870**

**CONFORME — aucune fuite du futur.**

## 3. Le filtre d'appartenance change-t-il réellement le signal ?

- dates comparées : **6**
- dates où la breadth diffère : **6**
- couverture moyenne : **88.4%**

**CONFORME — le filtre point-in-time change effectivement le signal.**

## 4. Décalage de niveau entre les deux univers

Contrôle **exigé par le pré-enregistrement**, sans mécanisme annoncé —
abstention motivée depuis le #409. Mesuré, publié, non interprété.

Mesure faite **sur les mêmes dates** dans les deux univers ; comparer les
moyennes des deux rapports confondrait effet d'univers et effet de période,
leurs fenêtres n'étant pas les mêmes.

- dates communes : **1396**
- breadth moyenne, univers point-in-time : **+8.91 pts**
- breadth moyenne, univers biaisé : **+6.95 pts**
- décalage (biaisé − point-in-time) : **-1.96 pts**
- part des séances au-dessus du seuil, point-in-time : **0.6%**
- part des séances au-dessus du seuil, biaisé : **0.4%**

Aucune interprétation n'est proposée : la mesure est publiée telle quelle.

Ce contrôle ne conditionne aucun verdict : il mesure une quantité annoncée
d'avance comme pertinente, et la publie quel que soit son signe.

## 5. Causalité de la porte

- indices de position modifiée : **[np.int64(20)]** (porte active au seul indice 20)

**CONFORME — décalage d un jour.**

## 6. Pourquoi la porte effective ne s'ouvre jamais

Constat **lu sur les chiffres du backtest**, pas une hypothèse
pré-enregistrée : la porte brute s'ouvre, mais l'exposition finale ne dépasse
jamais 1,0×. Explication candidate, vérifiable directement — les deux
conditions sont **anti-corrélées par construction** : la breadth de faiblesse
culmine quand la volatilité est haute, et c'est exactement là que
`20 % / vol` tombe sous 1,0 et se fait clipper au plancher.

Mesure de l'exposition **avant clip** sur les séances où la porte brute est
ouverte :

- séances à porte brute ouverte : **13**
- dont exposition avant clip < 1,0 : **13**
- exposition médiane avant clip, porte ouverte : **0.521×**
- exposition médiane avant clip, toutes séances : **1.096×**

**Explication confirmée** : sur *toutes* les séances où la condition de
capitulation est remplie, le vol-targeting demande déjà moins de 1,0× et le
clip ramène l'exposition au plancher. Les deux briques de cette stratégie
s'annulent mutuellement — ce n'est pas un accident d'échantillon mais une
propriété de sa construction, qui vaut donc aussi pour le cycle d'origine.

## Verdict de l'audit

**CONFORME — les contrôles de validité passent.**

Le contrôle 4 est une **mesure**, pas un test : il n'entre pas dans ce verdict.
