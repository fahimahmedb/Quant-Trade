# Témoin (permutation + négatif/positif) du détecteur D528 (pré-enregistré)

## La population

- radicaux connus (`finance/trading/scripts/nonml_*.py`) : **1039**
- sections du backlog (`## Backlog #NNN`) : **350**
- occurrences de marqueur (5 motifs) : **164**

| Marqueur | Occurrences |
|---|---|
| « rétracté » | 35 |
| « FAUSSE » | 3 |
| « n'est pas un défaut » | 1 |
| « contredit » | 22 |
| « réfuté » | 103 |

## Taux réel vs taux nul (permutation)

- `A_réel` (marqueurs réels) : **0.4390** (72/164)
- `A_nul` (moyenne sur 20 tirages, seed=529) : **0.5765**
- taux nul par tirage : 0.518, 0.530, 0.555, 0.640, 0.610, 0.579, 0.567, 0.561, 0.549, 0.549, 0.567, 0.579, 0.628, 0.628, 0.591, 0.579, 0.555, 0.610, 0.543, 0.591
- **lift = A_réel / A_nul = 0.76**

> Seuil fixé à **3** avant tout calcul. Lift < 3 : le filtre de proximité seul **ne discrimine pas** sur l'univers élargi.

## Témoins négatifs

### 1. `nonml_battery_backfill_lot_audit.py` — exclusion de la phrase générique de dette

- **NON écarté (problème)**
  - #528, « rétracté », distance 151

### 2. Collision de sous-chaîne `reproducibility_sample` — avec vs sans le tri par longueur

Sur les mêmes occurrences que le témoin positif ci-dessous, comparaison du radical retenu **avec** le tri par longueur décroissante (D528 tel que corrigé au #528) et **sans** (ordre alphabétique, reproduisant le bug d'audit du #528).

| Section | Marqueur | D528 (corrigé) | Naïf (alphabétique) | Collision évitée |
|---|---|---|---|---|
| #482 | « n'est pas un défaut » | `reproducibility_sample_lot3` | `reproducibility_sample` | oui |

- collisions évitées : **1/1**

- témoins négatifs corrects : **1/2**

## Témoin positif

- `nonml_reproducibility_sample_lot3_audit.py` : correctement retenu
  - #482, « n'est pas un défaut », distance 42

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| Lift < 3 | oui | 0.76 | **vérifiée** |
| 2/2 témoins négatifs écartés | 2 | 1 | **réfutée** |
| Témoin positif retenu | oui | True | **vérifiée** |

## Critères de succès

1. Population dénombrée et publiée — **OUI**.
2. A_réel, A_nul, lift publiés avec formule et seuil — **OUI**.
3. 2/2 témoins négatifs correctement écartés — **NON**.
4. 1/1 témoin positif correctement retenu — **OUI**.
5. Résultat honnête publié quel que soit le sens du lift — **OUI**.
6. Aucun script de marché exécuté — **OUI**.

**FAIL** — le critère porte sur le **procédé** : mesurer honnêtement, pas sur le sens du lift.

Simulation 300 € et robustesse **sans objet** : cycle de mesure de dépôt, aucune position.
