# Audit adversarial — Effet du changement d'heure DST

## 1. Vérification des règles contre des dates DST historiques connues (sourcées indépendamment)

| Année | Région | Calculé (printemps) | Connu | Calculé (automne) | Connu | Accord |
|---|---|---|---|---|---|---|
| 1970 | US | 1970-04-26 | 1970-04-26 | 1970-10-25 | 1970-10-25 | OUI |
| 1974 | US | 1974-01-06 | 1974-01-06 | 1974-10-27 | 1974-10-27 | OUI |
| 1975 | US | 1975-02-23 | 1975-02-23 | 1975-10-26 | 1975-10-26 | OUI |
| 1986 | US | 1986-04-27 | 1986-04-27 | 1986-10-26 | 1986-10-26 | OUI |
| 1987 | US | 1987-04-05 | 1987-04-05 | 1987-10-25 | 1987-10-25 | OUI |
| 2006 | US | 2006-04-02 | 2006-04-02 | 2006-10-29 | 2006-10-29 | OUI |
| 2007 | US | 2007-03-11 | 2007-03-11 | 2007-11-04 | 2007-11-04 | OUI |
| 2020 | US | 2020-03-08 | 2020-03-08 | 2020-11-01 | 2020-11-01 | OUI |
| 2026 | US | 2026-03-08 | 2026-03-08 | 2026-11-01 | 2026-11-01 | OUI |
| 1999 | EU | 1999-03-28 | 1999-03-28 | 1999-10-31 | 1999-10-31 | OUI |
| 2007 | EU | 2007-03-25 | 2007-03-25 | 2007-10-28 | 2007-10-28 | OUI |
| 2020 | EU | 2020-03-29 | 2020-03-29 | 2020-10-25 | 2020-10-25 | OUI |
| 2026 | EU | 2026-03-29 | 2026-03-29 | 2026-10-25 | 2026-10-25 | OUI |

**OK — les 9 dates de contrôle (7 US + 2 EU, couvrant chaque régime de règle) correspondent exactement aux dates historiques documentées indépendamment.**

## 2. Recalcul indépendant du masque (boucle Python pure, sans numpy vectorisé)

| Marché | % temps coupé | Occurrences | Désaccords |
|---|---|---|---|
| Composite (5 ans) | 0.88% | 11 | 0 |
| NDX (40 ans) | 0.81% | 83 | 0 |
| Russell 2000 | 0.81% | 79 | 0 |
| S&P 500 | 0.80% | 114 | 0 |
| DAX | 0.80% | 54 | 0 |

**OK — recalcul indépendant (boucle pure, sans vectorisation) identique (0 désaccord).**

## 3. Absence de fuite par construction

Le masque `dst_monday_mask` ne dépend QUE de la date et de règles calendaires officielles publiques (jamais du prix, du volume ni d'aucune donnée de marché) — aucune fuite temporelle possible par construction.
