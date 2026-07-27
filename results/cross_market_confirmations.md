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

## Itération 12, id 25 — FeatAgg_RF_E
Testé le 2026-07-27T17:38:54.419985+00:00
Features: ['ret_1', 'ret_2', 'drawdown_60']
NDX (référence, design/test): design_ann=0.613728044812006, test_ann=0.743816001415767, degradation=-0.13008795660376088, dsr=0.6348826674954036

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.462
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.445
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.334

---

## Itération 15, id 5 — AdaBoost_ExtraTree_E_lr05
Testé le 2026-07-27T18:18:57.697079+00:00
Features: ['ret_1', 'ret_2', 'drawdown_60']
NDX (référence, design/test): design_ann=0.6197997842387163, test_ann=0.657660396569257, degradation=-0.03786061233054073, dsr=0.6124064401998373

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.304
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.405
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.381

---

## Itération 16, id 45 — QDA_reg_E_01
Testé le 2026-07-27T18:26:34.871241+00:00
Features: ['ret_1', 'ret_2', 'drawdown_60']
NDX (référence, design/test): design_ann=0.6880947117844516, test_ann=0.8178694686016672, degradation=-0.1297747568172156, dsr=0.6773579447026421

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.281
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.177
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.071

---

## Itération 20, id 5 — Spline_Log_E
Testé le 2026-07-27T19:09:26.841908+00:00
Features: ['ret_1', 'ret_2', 'drawdown_60']
NDX (référence, design/test): design_ann=0.6670307663057312, test_ann=0.5589102078174775, degradation=0.10812055848825375, dsr=0.6054692478834104

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.456
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.265
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.258

---

## Itération 20, id 10 — Spline_Log_J_k4
Testé le 2026-07-27T19:10:36.513362+00:00
Features: ['parkinson_5', 'drawdown_60', 'ma_ratio_20']
NDX (référence, design/test): design_ann=0.6842936633240476, test_ann=0.6921421224923241, degradation=-0.007848459168276457, dsr=0.6360145817548242

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.316
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.354
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.272

---

