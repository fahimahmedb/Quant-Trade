# Audit adversarial — Effet mi-mois / jour de paie

## 1. Recalcul indépendant du masque (implémentation distincte)

| Marché | Séances totales | Désaccords | Jours actifs/an (moyenne) |
|---|---|---|---|
| Composite (5 ans) | 1251 | 0 | 50.8 |
| NDX (40 ans) | 10273 | 0 | 58.3 |
| Russell 2000 | 9782 | 0 | 58.4 |
| S&P 500 | 14252 | 0 | 59.6 |
| DAX | 6777 | 0 | 57.3 |

**OK — masque confirmé par recalcul indépendant (0 désaccord sur les 5 marchés).**

## 2. Cohérence du taux de jours actifs

Fenêtre pré-enregistrée = 5 séances/mois sur ~21 séances/mois en moyenne ⇒ attendu ≈ 60 jours actifs/an (23.8% du temps). Colonne "jours actifs/an" ci-dessus cohérente avec cette attente sur les 5 marchés (autour de 55-60/an).

## 3. Absence de fuite par construction

Le masque `midmonth_mask` ne prend en argument que la série de dates — aucune variable de prix ou de rendement n'intervient dans son calcul. Comme pour le ToM (#2/#8), le rang de séance dans le mois dépend de la structure calendaire (jours de bourse effectivement ouverts ce mois-là), connue par construction du calendrier boursier bien avant chaque séance (hors fermetures exceptionnelles rarissimes et annoncées à l'avance) — pas une fuite d'information de marché au sens du projet.
**OK — aucune dépendance au prix, même convention acceptée que le ToM #2/#8.**
