# Audit adversarial — concentration du marché (HHI), univers point-in-time

## 1. Recalcul du signal par un chemin de code disjoint

Le backtest calcule le HHI par indexation matricielle NumPy ;
l'audit par `pandas.shift` et Series indexées par ticker. Aucune ligne partagée.

| Date | Signal backtest | Signal audit | Écart |
|---|---|---|---|
| 2015-01-02 | 0.024228 | 0.024228 | 0.00e+00 |
| 2017-04-25 | 0.023275 | 0.023275 | 0.00e+00 |
| 2019-08-15 | 0.032176 | 0.032176 | 0.00e+00 |
| 2021-12-03 | 0.045475 | 0.045475 | 0.00e+00 |
| 2024-03-28 | 0.028381 | 0.028381 | 0.00e+00 |
| 2026-07-27 | 0.034919 | 0.034919 | 0.00e+00 |

- écart maximal : **0.00e+00**

**CONFORME — les deux chemins concordent à la précision machine.**

## 2. Anti-lookahead — mutation du futur

Prix postérieurs à l'indice 12808 (2020-10-09) multipliés par 7.

- signal avant mutation : **0.028474**
- signal après mutation : **0.028474**

**CONFORME — aucune fuite du futur.**

## 3. Le filtre d'appartenance change-t-il réellement le signal ?

- dates comparées : **6**
- dates où le signal diffère : **6**
- couverture moyenne : **88.2%**

**CONFORME — le filtre point-in-time change effectivement le signal.**

## 4. Décalage de niveau entre les deux univers

Contrôle **exigé par le pré-enregistrement**, qui signalait un point
**arithmétique** — le HHI dépend du nombre de titres retenus, son minimum
valant `1/n` — en précisant qu'il s'agit d'une propriété de la formule et non
d'une hypothèse sur le marché, et qu'aucune prédiction n'en était tirée. Niveau
**et** dispersion sont donc mesurés, comme annoncé.

Mesure faite **sur les mêmes dates** dans les deux univers ; comparer les
moyennes des deux rapports confondrait effet d'univers et effet de période,
leurs fenêtres n'étant pas les mêmes.

- dates communes : **1336**
- signal moyen, univers point-in-time : **0.0433**
- signal moyen, univers biaisé : **0.0478**
- décalage (biaisé − point-in-time) : **+0.0045**
- écart-type du signal, point-in-time : **0.0370**
- écart-type du signal, biaisé : **0.0509**

Le signal est en moyenne **plus bas** sur
l'univers point-in-time, et sa **dispersion est plus faible**
(0.0370 contre 0.0509).

Sur le point arithmétique annoncé : l'univers point-in-time retient **moins**
de titres (90 en moyenne), ce qui **relève** le plancher `1/n` du HHI.
Le niveau mesuré étant pourtant plus bas, l'effet de plancher ne domine pas —
constat factuel, sans interprétation économique proposée.

Ce contrôle ne conditionne aucun verdict : il mesure une quantité annoncée
d'avance comme pertinente, et la publie quel que soit son signe.

## 5. Causalité de la porte

- indices de position modifiée : **[np.int64(20)]** (porte active au seul indice 20)

**CONFORME — décalage d un jour.**

## 6. Attribution — univers ou période ?

**Contrôle PRÉ-ENREGISTRÉ.** La fenêtre a changé en même temps que l'univers
(2645 séances depuis 2016 contre 1385 au cycle d'origine). Le calcul
point-in-time est restreint à la fenêtre d'origine pour isoler l'effet
d'univers. Ne conditionne aucun verdict.

- séances retenues (PIT, depuis 2021-01-01) : **1386**

| | Sharpe ann. | Rendement total net |
|---|---|---|
| Overlay — origine, univers biaisé | +0.71 | +152.5% |
| Overlay — PIT, **fenêtre comparable** | +0.67 | +142.5% |
| Buy&Hold — même fenêtre | +0.66 | +129.0% |

La jambe Buy & Hold étant identique dans les deux univers, tout écart entre
les deux premières lignes est imputable à l'**univers** du signal.

## Verdict de l'audit

**CONFORME — les contrôles de validité passent.**

Le contrôle 4 est une **mesure**, pas un test : il n'entre pas dans ce verdict.
