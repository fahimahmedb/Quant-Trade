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

## Itération 20, id 12 — Spline_Log_wide_K_k4
Testé le 2026-07-27T19:12:01.219040+00:00
Features: ['mom_10', 'mom_20', 'vol_10', 'vol_20', 'rsi_14', 'macd_rel', 'bb_pctb', 'atr_rel', 'stoch_k', 'ma_ratio_20']
NDX (référence, design/test): design_ann=0.5775523040395075, test_ann=0.6911413032248928, degradation=-0.11358899918538513, dsr=0.44197008721629966

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.310
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.150
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.302

---

## Itération 21, id 30 — Spline_HistGB_wide_K
Testé le 2026-07-27T19:31:23.925775+00:00
Features: ['mom_10', 'mom_20', 'vol_10', 'vol_20', 'rsi_14', 'macd_rel', 'bb_pctb', 'atr_rel', 'stoch_k', 'ma_ratio_20']
NDX (référence, design/test): design_ann=0.746178139503473, test_ann=0.672316598883673, degradation=0.07386154061979998, dsr=0.7276152052459088

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = -0.001
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.435
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.062

---

## Itération 21, id 6 — Bagging_SplineLog_J
Testé le 2026-07-27T19:33:40.011703+00:00
Features: ['parkinson_5', 'drawdown_60', 'ma_ratio_20']
NDX (référence, design/test): design_ann=0.6692871282857332, test_ann=0.6924681157405145, degradation=-0.023180987454781275, dsr=0.5979644533250145

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.416
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.399
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.296

---

## Itération 21, id 1 — Bagging_SplineLog_A
Testé le 2026-07-27T19:37:08.865965+00:00
Features: ['mom_10', 'vol_10', 'rsi_14']
NDX (référence, design/test): design_ann=0.5963264428707835, test_ann=0.8759881892310772, degradation=-0.2796617463602937, dsr=0.46410926684137044

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.465
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.403
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.321

---

## Itération 21, id 19 — VotingSpline_RF_NB_wide_K
Testé le 2026-07-27T19:41:05.387760+00:00
Features: ['mom_10', 'mom_20', 'vol_10', 'vol_20', 'rsi_14', 'macd_rel', 'bb_pctb', 'atr_rel', 'stoch_k', 'ma_ratio_20']
NDX (référence, design/test): design_ann=0.5698786581349033, test_ann=0.692143640492012, degradation=-0.12226498235710868, dsr=0.41590665987033193

Confirmation hors-échantillon (zéro tuning, définition figée, 3 indices en parallèle) :
- Russell 2000: n=9782, OOS obs=9032, Sharpe ann = 0.197
- S&P 500: n=14252, OOS obs=13502, Sharpe ann = 0.270
- DAX: n=6777, OOS obs=6027, Sharpe ann = 0.318

---

