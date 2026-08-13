# Audit — lecture du schéma panier par le volet B du balayage #415 (pré-enregistré)

Cycle d'**outillage**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre de stratégie touché.

## Deux écarts au pré-enregistrement, signalés avant les résultats

### 1. Le nombre de candidats panier était faux

Le pré-enregistrement annonçait **3** candidats panier parmi les 7 non mesurés,
chiffre repris du #424 sans re-vérification. Le décompte direct en donne **5**.
La prédiction chiffrée « couverture 55 → 58 » était donc construite sur un
décompte inexact ; je le publie plutôt que d'ajuster la prédiction après coup.

### 2. Le contrôle de validation visait la mauvaise grandeur

Le pré-enregistrement voulait comparer l'activation récupérée au chiffre publié
« Overlay actif X % du temps ». **Ces deux grandeurs ne mesurent pas la même chose.**
Lecture des scripts : « Overlay actif » vaut `trend_aligned.mean()`, la fraction de
séances où la **porte** est ouverte ; l'activation du balayage est la fraction de
séances où l'**exposition dépasse 1,0×**. Une porte ouverte laisse passer une
exposition qui reste au plancher quand la volatilité est déjà à la cible.

La tolérance de **1 point n'est pas modifiée**. Le contrôle est appliqué là où la
comparaison est définie — les rapports publiant `plancher 1,0× X % du temps`, dont
le complément est exactement la grandeur mesurée. Les autres sont listés comme
**non contrôlables** plutôt que comparés à une grandeur qui ne leur correspond pas.

- candidats panier avec chiffre publié **comparable** : **1**
- candidats panier dont le chiffre publié est **non comparable** : **4**

- `lowvol_trend_vol_targeting_overlay` — Overlay actif 61,5 % (tendance haussière) : mesure la porte, pas l'exposition.
- `momentum_consistency_trend_vol_targeting_overlay` — Overlay actif 72,8 % (tendance haussière) : mesure la porte, pas l'exposition.
- `winners_trend_vol_targeting_overlay` — Overlay actif 61,1 % (tendance haussière) : mesure la porte, pas l'exposition.
- `winners_trend_vol_targeting_overlay_pit_universe` — Overlay actif 67,0 % : mesure la porte, pas l'exposition.

## Contrôle 2 — validation contre un chiffre déjà publié

> Tolérance fixée avant calcul : **1 point de pourcentage**.

| Candidat | Attendu (rapport) | Récupéré (division) | Écart | Verdict |
|---|---|---|---|---|
| `momentum_consistency_trend_vol_targeting_15_overlay` | 21.0 % | 20.98 % | 0.02 pt | OK |

**Contrôle passé** — écart maximal **0.02 point**, sous la tolérance.
La récupération de l'exposition par division retrouve un chiffre produit
indépendamment par le script du candidat, à partir de la variable `exposure`
elle-même. L'identité `ov = exposition × bh` tient sur données réelles.

Un seul candidat porte ce contrôle. C'est peu, et je ne le présente pas comme
davantage : il valide la **méthode** de récupération, pas chacun des résultats.

## Contrôle 1 — non-régression sur les activations déjà mesurées

- activations relevées avant l'extension : **55**
- candidats disparus du balayage : **0**
- activations **modifiées** : **0**

**0 régression.** L'extension n'a touché que la branche panier.

## Contrôle 3 — couverture du volet B

| | Avant | Après |
|---|---|---|
| candidats structurés (volet A) | 62 | 62 |
| **mesurés** (volet B) | 55 | **60** |
| dont schéma indiciel | 55 | 55 |
| dont schéma panier | 0 | **5** |
| non mesurés | 7 | **2** |

Restent non mesurés, faute de `.npz` — pas d'une limite d'outil :

- `rebound_speed_breadth_vol_targeting_overlay`
- `vix_regime_vol_targeting_overlay`

## Effet sur le diagnostic du balayage

| Candidat panier | Exposition > 1,0× | Inactif (< 2 %) | Verdict au rapport |
|---|---|---|---|
| `momentum_consistency_trend_vol_targeting_15_overlay` | 20.98 % | non | FAIL |
| `winners_trend_vol_targeting_overlay` | 35.25 % | non | PASS |
| `momentum_consistency_trend_vol_targeting_overlay` | 44.76 % | non | FAIL |
| `winners_trend_vol_targeting_overlay_pit_universe` | 60.12 % | non | FAIL |
| `lowvol_trend_vol_targeting_overlay` | 61.50 % | non | FAIL |

- nouveaux candidats **structurellement inactifs** : **0**
- nouveaux **PASS vides** : **0**

Aucun PASS vide révélé par l'extension : ces candidats prennent des positions
effectivement distinctes de leur référence. Le cas isolé du #410 le reste.

### Observation faite après calcul — la distinction porte/exposition était réelle

Signalée comme **post-hoc**, elle n'est pas un contrôle réussi : la classification
« comparable / non comparable » a été fixée avant de lancer le calcul.

| Candidat | « Overlay actif » publié (porte) | Exposition > 1,0× mesurée | Écart |
|---|---|---|---|
| `lowvol_trend_vol_targeting_overlay` | 61.5 % | 61.50 % | 0.00 pt |
| `momentum_consistency_trend_vol_targeting_overlay` | 72.8 % | 44.76 % | 28.04 pt |
| `winners_trend_vol_targeting_overlay` | 61.1 % | 35.25 % | 25.85 pt |
| `winners_trend_vol_targeting_overlay_pit_universe` | 67.0 % | 60.12 % | 6.88 pt |

Trois des quatre écarts dépassent largement le point de pourcentage. Avoir comparé
l'activation à ces chiffres, comme le pré-enregistrement le prévoyait, aurait
produit un **échec de validation qui n'aurait rien dit de la méthode** — seulement
que deux grandeurs différentes diffèrent. Le quatrième coïncide au centième près :
sur ce candidat, la porte ouverte implique une exposition au-dessus du plancher.
C'est une propriété de ce candidat, pas une validation de plus.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| candidats panier mesurés | 3 (décompte faux) | 5 | ✔ |
| écart maximal à un chiffre publié | ≤ 1 pt | 0.02 pt | ✔ |
| régressions | 0 | 0 | ✔ |
| couverture publiée | oui | 60/62 | ✔ |

**Extension validée.** Le volet B couvre désormais **60/62**
candidats au lieu de 55. La prédiction déductive « écart ≤ 1 point,
0 régression » est **vérifiée** ; sa partie chiffrée « couverture 55 → 58 »
est **fausse dans son chiffre** — la couverture atteint 60, parce que le
décompte de départ était erroné, non parce que la méthode a mieux marché.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
