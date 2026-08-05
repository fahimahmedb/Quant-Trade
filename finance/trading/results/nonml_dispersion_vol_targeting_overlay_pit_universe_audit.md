# Audit adversarial — Porte dispersion cross-sectionnelle, univers point-in-time

## 1. Recalcul indépendant de la dispersion PIT à un échantillon de dates

| Date | Dispersion (original) | Dispersion (recalcul indépendant) | Écart |
|---|---|---|---|
| 2015-01-02 | 0.008851 | 0.008851 | 0.00e+00 |
| 2016-08-04 | 0.019118 | 0.019118 | 0.00e+00 |
| 2018-03-08 | 0.015340 | 0.015340 | 0.00e+00 |
| 2019-10-09 | 0.008061 | 0.008061 | 0.00e+00 |
| 2021-05-12 | 0.016733 | 0.016733 | 0.00e+00 |
| 2022-12-12 | 0.020978 | 0.020978 | 0.00e+00 |
| 2024-07-18 | 0.017085 | 0.017085 | 0.00e+00 |
| 2026-02-23 | 0.031376 | 0.031376 | 0.00e+00 |

**OK — dispersion PIT confirmée par recalcul indépendant.**

## 2. Vérification de l'absence de contamination pré-2015

Nombre de valeurs de dispersion NON-NaN avant 2015-01-01 : 0 (sur 11355 dates disponibles dans le panneau PIT avant cette date).
**OK — aucune dispersion calculée hors couverture de composition (bug du masque NaN corrigé).**

## 3. Test anti-lookahead (perturbation du futur)

Mutation appliquée à partir de 2022-06-01, contrôle à 2018-06-01 (bien antérieure, dans la période où la dispersion PIT est calculée).
Écart de dispersion à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
