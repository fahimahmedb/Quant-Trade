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

## Itération 8, id 8 — QuantNormal_Log_H_C1
Testé le 2026-07-27T14:53:14.843572+00:00
Features: ['ret_1', 'ret_2', 'ret_3', 'drawdown_60', 'vol_10']
NDX (référence, design/test): design_ann=0.5668365731266053, test_ann=0.6634780567393965, degradation=-0.09664148361279123, dsr=0.7083168582954891

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.415
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.358
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.254

---

## Itération 8, id 30 — KMeans4_Log_H
Testé le 2026-07-27T14:56:23.494909+00:00
Features: ['ret_1', 'ret_2', 'ret_3', 'drawdown_60', 'vol_10']
NDX (référence, design/test): design_ann=0.5769518889752009, test_ann=0.6743154319583491, degradation=-0.09736354298314816, dsr=0.7239694663353409

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.451
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.609
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.306

---

## Itération 10, id 11 — AdaBoost_NB_A
Testé le 2026-07-27T16:46:05.744659+00:00
Features: ['mom_10', 'vol_20', 'rsi_14']
NDX (référence, design/test): design_ann=0.5544522596561617, test_ann=0.678500548082332, degradation=-0.12404828842617022, dsr=0.6224429437216422

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.266
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.276
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.104

---

## Itération 11, id 37 — VotingRadius_H
Testé le 2026-07-27T17:23:10.833845+00:00
Features: ['ret_1', 'ret_2', 'ret_3', 'drawdown_60', 'vol_10']
NDX (référence, design/test): design_ann=0.5701775014815623, test_ann=0.6547873741902173, degradation=-0.08460987270865497, dsr=0.6202716157339122

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.245
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.153
- DAX: n=6777, OOS obs=6027, Sharpe ann = -0.152

---

