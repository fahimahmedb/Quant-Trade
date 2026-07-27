"""
Itération 21 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 20 (SplineTransformer+LogReg/RidgeCV, Bagging(GMMBayes),
Nystroem(cosine)+SGD, RobustScaler+RidgeCV calibré), itération 21 explore
des combinaisons construites autour de la base de splines introduite en
itération 20, ainsi qu'un nouvel apprenant faible pour AdaBoost :

1. BaggingClassifier(Pipeline(SplineTransformer+LogisticRegression),
   n_estimators=8) — version "bagged" du pipeline spline de l'itération 20
   (bucket 1), pour tester si moyenner sur des rééchantillonnages stabilise
   les prédictions d'un modèle linéaire à base de splines.
2. VotingClassifier(soft) à 3 membres hétérogènes : Pipeline(Spline+LogReg)
   + RandomForest + GaussianNB — premier comité de vote incluant un membre
   à base de splines.
3. Pipeline(SplineTransformer + HistGradientBoostingClassifier léger) —
   base de splines suivie d'un modèle non linéaire (HistGB), jamais
   combinés (itération 20 utilisait uniquement LogReg/RidgeCV en aval).
4. AdaBoostClassifier(CalibratedClassifierCV(RidgeClassifierCV)) —
   apprenant faible linéaire régularisé (Ridge à alpha auto-sélectionné)
   pour le boosting, jamais essayé (AdaBoost avait déjà utilisé un stump,
   RF, ET, GaussianNB, LogReg comme base — jamais un Ridge calibré).
5. Pipeline(RobustScaler + SplineTransformer + LogisticRegression) —
   combine explicitement mise à l'échelle résistante aux outliers ET base
   de splines dans une seule chaîne, jamais assemblées ensemble (chacune
   testée séparément en itération 20).

Vitesse vérifiée sur n=9000 : toutes les familles <4s/fit (Bagging(Spline+
LogReg) réduit à 8 estimateurs et 8 variantes pour limiter le coût cumulé).

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.preprocessing import SplineTransformer, RobustScaler
from sklearn.linear_model import LogisticRegression, RidgeClassifierCV
from sklearn.ensemble import BaggingClassifier, VotingClassifier, AdaBoostClassifier, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline

SEED = 42

F_A = ["mom_10", "vol_10", "rsi_14"]
F_B = ["mom_20", "vol_ratio", "macd_rel"]
F_C = ["ma_ratio_20", "stoch_k", "atr_rel"]
F_D = ["fracdiff_04", "parkinson_5", "vol_20"]
F_E = ["ret_1", "ret_2", "drawdown_60"]
F_F = ["mom_10", "mom_20", "bb_pctb"]
F_G = ["ma_ratio_50", "vol_10", "rsi_14", "stoch_k"]
F_H = ["ret_3", "ret_5", "vol_ratio", "atr_rel"]
F_I = ["fracdiff_04", "mom_10", "macd_rel", "bb_pctb"]
F_J = ["parkinson_5", "drawdown_60", "ma_ratio_20"]
F_K = ["mom_10", "mom_20", "vol_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "atr_rel", "stoch_k", "ma_ratio_20"]

STRATEGIES = {
    # BaggingClassifier(Pipeline(Spline+LogReg)) (1-8)
    1: ("Bagging_SplineLog_A", F_A, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))]), n_estimators=8, random_state=SEED)),
    2: ("Bagging_SplineLog_C", F_C, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))]), n_estimators=8, random_state=SEED)),
    3: ("Bagging_SplineLog_E", F_E, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))]), n_estimators=8, random_state=SEED)),
    4: ("Bagging_SplineLog_G", F_G, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))]), n_estimators=8, random_state=SEED)),
    5: ("Bagging_SplineLog_I", F_I, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))]), n_estimators=8, random_state=SEED)),
    6: ("Bagging_SplineLog_J", F_J, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))]), n_estimators=8, random_state=SEED)),
    7: ("Bagging_SplineLog_wide_K", F_K, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))]), n_estimators=8, random_state=SEED)),
    8: ("Bagging_SplineLog_wide_K_n12", F_K, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=4, degree=2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))]), n_estimators=12, random_state=SEED)),

    # VotingClassifier(soft) : Spline+LogReg + RandomForest + GaussianNB (9-20)
    9: ("VotingSpline_RF_NB_A", F_A, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    10: ("VotingSpline_RF_NB_B", F_B, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    11: ("VotingSpline_RF_NB_C", F_C, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    12: ("VotingSpline_RF_NB_D_weighted", F_D, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", weights=[2, 1, 1], n_jobs=1)),
    13: ("VotingSpline_RF_NB_E", F_E, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    14: ("VotingSpline_RF_NB_F", F_F, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    15: ("VotingSpline_RF_NB_G", F_G, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    16: ("VotingSpline_RF_NB_H", F_H, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    17: ("VotingSpline_RF_NB_I_weighted", F_I, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", weights=[1, 1, 2], n_jobs=1)),
    18: ("VotingSpline_RF_NB_J", F_J, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=4, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    19: ("VotingSpline_RF_NB_wide_K", F_K, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    20: ("VotingSpline_RF_NB_wide_K_weighted", F_K, lambda: VotingClassifier(estimators=[("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], voting="soft", weights=[2, 2, 1], n_jobs=1)),

    # Pipeline(SplineTransformer + HistGradientBoostingClassifier leger) (21-30)
    21: ("Spline_HistGB_A", F_A, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=30, max_depth=3, random_state=SEED))])),
    22: ("Spline_HistGB_B", F_B, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=30, max_depth=3, random_state=SEED))])),
    23: ("Spline_HistGB_C_iter50", F_C, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=50, max_depth=3, random_state=SEED))])),
    24: ("Spline_HistGB_D", F_D, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=30, max_depth=2, random_state=SEED))])),
    25: ("Spline_HistGB_E", F_E, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=30, max_depth=3, random_state=SEED))])),
    26: ("Spline_HistGB_F", F_F, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=30, max_depth=3, random_state=SEED))])),
    27: ("Spline_HistGB_G_iter50", F_G, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=50, max_depth=3, random_state=SEED))])),
    28: ("Spline_HistGB_H", F_H, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=30, max_depth=2, random_state=SEED))])),
    29: ("Spline_HistGB_I", F_I, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("hgb", HistGradientBoostingClassifier(max_iter=30, max_depth=3, random_state=SEED))])),
    30: ("Spline_HistGB_wide_K", F_K, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=2)), ("hgb", HistGradientBoostingClassifier(max_iter=30, max_depth=3, random_state=SEED))])),

    # AdaBoostClassifier(CalibratedClassifierCV(RidgeClassifierCV)) (31-40)
    31: ("AdaBoost_CalibRidgeCV_A", F_A, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=20, random_state=SEED)),
    32: ("AdaBoost_CalibRidgeCV_B_n30", F_B, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=30, random_state=SEED)),
    33: ("AdaBoost_CalibRidgeCV_C", F_C, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.01, 0.1, 1.0, 10.0)), cv=3), n_estimators=20, random_state=SEED)),
    34: ("AdaBoost_CalibRidgeCV_D_lr05", F_D, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=20, learning_rate=0.5, random_state=SEED)),
    35: ("AdaBoost_CalibRidgeCV_E", F_E, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=20, random_state=SEED)),
    36: ("AdaBoost_CalibRidgeCV_F", F_F, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=20, random_state=SEED)),
    37: ("AdaBoost_CalibRidgeCV_G_n30", F_G, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=30, random_state=SEED)),
    38: ("AdaBoost_CalibRidgeCV_H", F_H, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=20, random_state=SEED)),
    39: ("AdaBoost_CalibRidgeCV_I_lr03", F_I, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=20, learning_rate=0.3, random_state=SEED)),
    40: ("AdaBoost_CalibRidgeCV_wide_K", F_K, lambda: AdaBoostClassifier(estimator=CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3), n_estimators=20, random_state=SEED)),

    # Pipeline(RobustScaler + SplineTransformer + LogisticRegression) (41-50)
    41: ("RobustScaler_Spline_Log_A", F_A, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    42: ("RobustScaler_Spline_Log_B", F_B, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    43: ("RobustScaler_Spline_Log_C", F_C, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    44: ("RobustScaler_Spline_Log_D_quantrange", F_D, lambda: Pipeline([("rs", RobustScaler(quantile_range=(10.0, 90.0))), ("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    45: ("RobustScaler_Spline_Log_E", F_E, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    46: ("RobustScaler_Spline_Log_F_k4", F_F, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=4, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    47: ("RobustScaler_Spline_Log_G", F_G, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    48: ("RobustScaler_Spline_Log_H", F_H, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    49: ("RobustScaler_Spline_Log_I", F_I, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    50: ("RobustScaler_Spline_Log_wide_K", F_K, lambda: Pipeline([("rs", RobustScaler()), ("spl", SplineTransformer(n_knots=4, degree=2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
}
