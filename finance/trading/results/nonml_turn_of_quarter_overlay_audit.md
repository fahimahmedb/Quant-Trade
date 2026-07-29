# Audit adversarial — Overlay levé turn-of-quarter

## 1. Recalcul indépendant (balayage séquentiel via datetime standard)

| Marché | Écart masque (nb j.) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque confirmé par recalcul indépendant.**

## 2. Vérification du nombre de jours actifs par an (doit être ≈ 4×(LAST_N_DAYS+FIRST_N_DAYS)=28)

| Marché | Nb jours actifs total | Nb années | Moyenne j./an |
|---|---|---|---|
| Composite (5 ans) | 143 | 6 | 23.83 |
| NDX (40 ans) | 1144 | 42 | 27.24 |
| Russell 2000 | 1092 | 40 | 27.30 |
| S&P 500 | 1585 | 57 | 27.81 |
| DAX | 749 | 28 | 26.75 |

## 3. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — comportement stable (le calendrier n'est pas une donnée de marché, aucune fuite possible par construction).**

**Lecture économique du FAIL — correction d'une erreur de caractérisation dans le PREREG** : le pré-enregistrement de ce cycle affirmait à tort que le #8 (ToM en overlay, 12 fenêtres/an) avait été "reclassé FAIL sous la règle renforcée" — c'est en réalité le **#2** (stratégie ToM classique, hors overlay) qui a été reclassé FAIL ; le **#8 est un authentique PASS (4/5)**, voir `results/nonml_tom_overlay_result.md`. Cette confusion de motivation n'affecte PAS la définition, les paramètres ni le critère de succès du #65 (repris à l'identique du #8, correctement exécutés), donc le résultat FAIL (3/5) reste valide -- mais la lecture correcte est : restreindre la fenêtre ToM du #8 (PASS 4/5, 12 occurrences/an) aux seuls changements de trimestre (4 occurrences/an) **DÉGRADE** le résultat (3/5) au lieu de le renforcer. Cela suggère que les 8 changements de mois ORDINAIRES (non trimestriels) contribuent eux aussi à l'edge du #8, contrairement à l'hypothèse pré-enregistrée d'un effet de rebalancement institutionnel concentré aux trimestres.
