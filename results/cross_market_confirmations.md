## Itération 3, id 31 — RF_d3_n200
Testé le 2026-07-27 (manuel, hors automatisation — script one-off avant généralisation)
Features: [mom_10, vol_20, rsi_14, macd_rel, bb_pctb]
NDX (référence, design/test): design_ann=0.556, test_ann=0.601, degradation=-0.045, dsr=0.891

Confirmation hors-échantillon (zéro tuning, définition figée) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.413
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.419
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.168

Verdict : signal réplique en DIRECTION et magnitude raisonnable sur Russell 2000
et S&P 500 (~70-75% de l'amplitude NDX). Plus faible sur DAX mais toujours
positif. Pas une preuve d'edge réel (aucun test de significativité formel sur
ces Sharpes externes), mais plus rassurant qu'un pattern typique de faux
positif (qui montrerait des signes incohérents ou des Sharpes proches de zéro
sur des marchés non liés).
---

