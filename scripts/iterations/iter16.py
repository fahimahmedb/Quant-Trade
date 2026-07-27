"""
Itération 16 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 15 (AdaBoost(ExtraTree), SelectKBest+KNN/ComplementNB,
FeatureUnion(PCA+passthrough), comité linéaire/NB), itération 16 explore :

1. Pipeline(Normalizer + LogisticRegression) — normalisation PAR
   OBSERVATION (chaque ligne mise à norme L2 unitaire), fondamentalement
   différente des normalisations PAR COLONNE déjà testées (StandardScaler,
   MinMaxScaler, QuantileTransformer, PowerTransformer) — jamais utilisée.
2. Pipeline(Normalizer + KNeighborsClassifier) — la normalisation par
   observation change la géométrie des distances utilisées par KNN d'une
   façon qualitativement différente d'une simple mise à l'échelle par
   colonne — jamais combinée.
3. CalibratedClassifierCV(SGDClassifier(loss="hinge")) — SGD avec perte
   hinge (SVM linéaire), jamais calibré (seules les pertes log_loss et
   modified_huber de SGDClassifier, qui ont nativement predict_proba,
   avaient été testées en itération 4).
4. BaggingClassifier(SGDClassifier(loss="log_loss")) — jamais essayé
   (SGDClassifier avait été testé seul, mais pas en ensemble bagged).
5. QuadraticDiscriminantAnalysis avec reg_param>0 (QDA régularisée/à
   rétrécissement) — QDA "pure" (reg_param=0) avait été testée en
   itération 4 ; la version régularisée a un compromis biais/variance
   différent, jamais explorée.

Vitesse vérifiée sur n=9000 : toutes les familles <2s/fit (Bagging(SGD)
réduit à 10 estimateurs plutôt que 20 pour rester sous ~1s/fit et éviter
de répéter le problème de coût cumulé des itérations 10-11).

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.preprocessing import Normalizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import BaggingClassifier
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
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
    # Pipeline(Normalizer + LogisticRegression) (1-10)
    1: ("Normalizer_Log_A", F_A, lambda: Pipeline([("norm", Normalizer()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("Normalizer_Log_B_l1", F_B, lambda: Pipeline([("norm", Normalizer(norm="l1")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    3: ("Normalizer_Log_C", F_C, lambda: Pipeline([("norm", Normalizer()), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    4: ("Normalizer_Log_D", F_D, lambda: Pipeline([("norm", Normalizer()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("Normalizer_Log_E_l1", F_E, lambda: Pipeline([("norm", Normalizer(norm="l1")), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    6: ("Normalizer_Log_F", F_F, lambda: Pipeline([("norm", Normalizer()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    7: ("Normalizer_Log_G", F_G, lambda: Pipeline([("norm", Normalizer()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    8: ("Normalizer_Log_H_max", F_H, lambda: Pipeline([("norm", Normalizer(norm="max")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    9: ("Normalizer_Log_I", F_I, lambda: Pipeline([("norm", Normalizer()), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    10: ("Normalizer_Log_wide_K", F_K, lambda: Pipeline([("norm", Normalizer()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(Normalizer + KNeighborsClassifier) (11-20)
    11: ("Normalizer_KNN_A", F_A, lambda: Pipeline([("norm", Normalizer()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    12: ("Normalizer_KNN_B_l1", F_B, lambda: Pipeline([("norm", Normalizer(norm="l1")), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    13: ("Normalizer_KNN_C", F_C, lambda: Pipeline([("norm", Normalizer()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    14: ("Normalizer_KNN_D", F_D, lambda: Pipeline([("norm", Normalizer()), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    15: ("Normalizer_KNN_E", F_E, lambda: Pipeline([("norm", Normalizer()), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))])),
    16: ("Normalizer_KNN_F_max", F_F, lambda: Pipeline([("norm", Normalizer(norm="max")), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    17: ("Normalizer_KNN_G", F_G, lambda: Pipeline([("norm", Normalizer()), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    18: ("Normalizer_KNN_H", F_H, lambda: Pipeline([("norm", Normalizer()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    19: ("Normalizer_KNN_I_l1", F_I, lambda: Pipeline([("norm", Normalizer(norm="l1")), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    20: ("Normalizer_KNN_wide_K", F_K, lambda: Pipeline([("norm", Normalizer()), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),

    # CalibratedClassifierCV(SGDClassifier(loss="hinge")) (21-30)
    21: ("CalibSGD_hinge_A", F_A, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-4, random_state=SEED), cv=3)),
    22: ("CalibSGD_hinge_B", F_B, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-3, random_state=SEED), cv=3)),
    23: ("CalibSGD_hinge_C", F_C, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-4, random_state=SEED), cv=3)),
    24: ("CalibSGD_hinge_D_cv5", F_D, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-4, random_state=SEED), cv=5)),
    25: ("CalibSGD_hinge_E", F_E, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-5, random_state=SEED), cv=3)),
    26: ("CalibSGD_hinge_F_elastic", F_F, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-4, penalty="elasticnet", random_state=SEED), cv=3)),
    27: ("CalibSGD_hinge_G", F_G, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-4, random_state=SEED), cv=3)),
    28: ("CalibSGD_hinge_H", F_H, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-3, random_state=SEED), cv=3)),
    29: ("CalibSGD_hinge_I_cv5", F_I, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-4, random_state=SEED), cv=5)),
    30: ("CalibSGD_hinge_wide_K", F_K, lambda: CalibratedClassifierCV(SGDClassifier(loss="hinge", alpha=1e-4, random_state=SEED), cv=3)),

    # BaggingClassifier(SGDClassifier(loss="log_loss")) (31-40)
    31: ("Bagging_SGDlog_A", F_A, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED), n_estimators=10, random_state=SEED)),
    32: ("Bagging_SGDlog_B", F_B, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-3, random_state=SEED), n_estimators=10, random_state=SEED)),
    33: ("Bagging_SGDlog_C", F_C, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED), n_estimators=10, random_state=SEED)),
    34: ("Bagging_SGDlog_D_n15", F_D, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED), n_estimators=15, random_state=SEED)),
    35: ("Bagging_SGDlog_E", F_E, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-5, random_state=SEED), n_estimators=10, random_state=SEED)),
    36: ("Bagging_SGDlog_F", F_F, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED), n_estimators=10, random_state=SEED)),
    37: ("Bagging_SGDlog_G", F_G, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED), n_estimators=10, random_state=SEED)),
    38: ("Bagging_SGDlog_H", F_H, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-3, random_state=SEED), n_estimators=10, random_state=SEED)),
    39: ("Bagging_SGDlog_I", F_I, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED), n_estimators=10, random_state=SEED)),
    40: ("Bagging_SGDlog_wide_K", F_K, lambda: BaggingClassifier(estimator=SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED), n_estimators=10, random_state=SEED)),

    # QuadraticDiscriminantAnalysis regularisee (reg_param>0) (41-50)
    41: ("QDA_reg_A_02", F_A, lambda: QuadraticDiscriminantAnalysis(reg_param=0.2)),
    42: ("QDA_reg_B_05", F_B, lambda: QuadraticDiscriminantAnalysis(reg_param=0.5)),
    43: ("QDA_reg_C_02", F_C, lambda: QuadraticDiscriminantAnalysis(reg_param=0.2)),
    44: ("QDA_reg_D_03", F_D, lambda: QuadraticDiscriminantAnalysis(reg_param=0.3)),
    45: ("QDA_reg_E_01", F_E, lambda: QuadraticDiscriminantAnalysis(reg_param=0.1)),
    46: ("QDA_reg_F_05", F_F, lambda: QuadraticDiscriminantAnalysis(reg_param=0.5)),
    47: ("QDA_reg_G_02", F_G, lambda: QuadraticDiscriminantAnalysis(reg_param=0.2)),
    48: ("QDA_reg_H_03", F_H, lambda: QuadraticDiscriminantAnalysis(reg_param=0.3)),
    49: ("QDA_reg_I_01", F_I, lambda: QuadraticDiscriminantAnalysis(reg_param=0.1)),
    50: ("QDA_reg_wide_K_03", F_K, lambda: QuadraticDiscriminantAnalysis(reg_param=0.3)),
}
