# Audit adversarial — Porte breadth SMA200, univers point-in-time

## 1. Recalcul indépendant de la breadth PIT à un échantillon de dates

| Date | Breadth (original) | Breadth (recalcul indépendant) | Écart |
|---|---|---|---|
| 2015-01-02 | 0.808219 | 0.808219 | 0.00e+00 |
| 2016-08-04 | 0.725000 | 0.725000 | 0.00e+00 |
| 2018-03-08 | 0.771084 | 0.771084 | 0.00e+00 |
| 2019-10-09 | 0.602273 | 0.602273 | 0.00e+00 |
| 2021-05-12 | 0.695652 | 0.695652 | 0.00e+00 |
| 2022-12-12 | 0.536082 | 0.536082 | 0.00e+00 |
| 2024-07-18 | 0.717172 | 0.717172 | 0.00e+00 |
| 2026-02-23 | 0.495050 | 0.495050 | 0.00e+00 |

**OK — breadth PIT confirmée par recalcul indépendant.**

## 2. Vérification de l'absence de contamination pré-2015

Nombre de valeurs de breadth NON-NaN avant 2015-01-01 : 0 (sur 11355 dates disponibles dans le panneau PIT avant cette date).
**OK — aucune breadth calculée hors couverture de composition.**

## 3. Test anti-lookahead (perturbation du futur)

Mutation appliquée à partir de 2022-06-01, contrôle à 2018-06-01.
Écart de breadth à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
