# Audit — Portefeuille L/S dollar-neutre composite (PIT)

## 1. Recalcul indépendant des 4 signaux bruts (échantillon)

| Date | Ticker | Écart max (4 signaux) |
|---|---|---|
| 2015-01-02 | AAL | 1.60e-16 |
| 2015-01-02 | CHKP | 6.18e-16 |
| 2015-01-02 | MELI | 5.55e-17 |
| 2015-01-02 | ROST | 8.15e-17 |
| 2016-06-03 | AAL | 2.64e-16 |
| 2016-06-03 | CHKP | 6.02e-16 |
| 2016-06-03 | MELI | 1.28e-16 |
| 2016-06-03 | ROST | 5.03e-17 |
| 2017-11-01 | AAL | 2.15e-16 |
| 2017-11-01 | CHKP | 3.96e-16 |
| 2017-11-01 | MELI | 5.55e-17 |
| 2017-11-01 | ROST | 5.55e-17 |
| 2019-04-05 | AAL | 2.26e-16 |
| 2019-04-05 | CHKP | 7.91e-16 |
| 2019-04-05 | MELI | 6.94e-17 |
| 2019-04-05 | ROST | 9.89e-17 |
| 2020-09-03 | AAL | 8.33e-17 |
| 2020-09-03 | CHKP | 4.68e-16 |
| 2020-09-03 | MELI | 8.33e-17 |
| 2020-09-03 | ROST | 2.08e-17 |
| 2022-02-03 | AAL | 1.46e-16 |
| 2022-02-03 | CHKP | 5.12e-16 |
| 2022-02-03 | GFS | 6.94e-18 |
| 2022-02-03 | MELI | 5.55e-17 |
| 2022-02-03 | ROST | 2.78e-17 |
| 2023-07-10 | AAL | 2.43e-16 |
| 2023-07-10 | CHKP | 5.52e-16 |
| 2023-07-10 | GFS | 2.08e-17 |
| 2023-07-10 | MELI | 5.90e-17 |
| 2023-07-10 | ROST | 1.16e-16 |
| 2024-12-06 | AAL | 1.25e-16 |
| 2024-12-06 | CHKP | 3.43e-16 |
| 2024-12-06 | GFS | 1.39e-17 |
| 2024-12-06 | MELI | 8.67e-17 |
| 2024-12-06 | ROST | 1.02e-16 |

**Écart max sur 35 points (date, ticker) vérifiés : 7.91e-16 — OK**

## 2. Neutralité dollar (Σw≈0) et exposition brute (Σ|w|=2) à chaque rebalancement actif

- Écart max |Σw| sur 139 rebalancements actifs : 1.82e-16 — **OK — dollar-neutre**
- Écart max |Σ|w|| - 2 : 6.66e-16 — **OK — exposition brute correcte**

## 3. Anti-lookahead (troncature à 11670 séances, marge de 21 séances avant la coupe)
- Écart max poids sur la zone valide, historique complet vs tronqué : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
