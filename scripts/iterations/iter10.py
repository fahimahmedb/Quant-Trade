"""
Itération 10 — 50 nouvelles hypothèses (univers figé a priori).

Après 7 itérations de familles/combinaisons de classifieurs et 2 de
prétraitement/contraintes, itération 10 explore ce qui reste :

1. SelectKBest + LogisticRegression : sélection AUTOMATIQUE des meilleures
   features parmi un LARGE pool (~14 colonnes), au lieu des petits sous-
   ensembles choisis à la main dans toutes les itérations précédentes —
   hypothèse structurellement différente (l'algorithme décide quoi garder).
2. AdaBoost(GaussianNB) : boosting avec un classifieur probabiliste faible
   comme base (jamais combiné — AdaBoost n'avait utilisé que des arbres/
   modèles linéaires comme base).
3. Bagging(LDA/QDA) : ensemble de discriminants — jamais combinés (LDA/QDA
   toujours testés seuls jusqu'ici). (NB : Bagging(SVC) testé et écarté —
   SVC est déjà coûteux seul, multiplié par n_estimators=6-10 dans un
   Bagging sur des centaines de fenêtres walk-forward, un seul essai a
   dépassé 5 min sans terminer ; remplacé par des discriminants, fit
   fermé quasi instantané.)
4. CalibratedClassifierCV(Bagging(DecisionTree)) : recalibration d'un
   ensemble déjà probabiliste — teste si la calibration post-hoc change
   la qualité du signal.
5. RadiusNeighborsClassifier : géométrique, différent de KNN (rayon fixe
   plutôt que k voisins fixe) — jamais testé, gestion des points isolés
   via outlier_label.
6. SelectKBest(mutual_info) + RandomForest : sélection automatique +
   classifieur non linéaire.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier, RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import RadiusNeighborsClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

SEED = 42

# Large pool de features pour la selection automatique (SelectKBest)
F_POOL = ["mom_10", "mom_20", "vol_10", "vol_20", "vol_ratio", "rsi_14", "macd_rel",
          "bb_pctb", "atr_rel", "stoch_k", "drawdown_60", "fracdiff_04",
          "ma_ratio_20", "ret_1"]

F_A = ["mom_10", "vol_20", "rsi_14"]
F_B = ["mom_10", "vol_ratio", "atr_rel", "mom_20"]
F_C = ["mom_20", "ma_ratio_50", "vol_10", "stoch_k"]
F_D = ["drawdown_60", "vol_20", "rsi_14", "fracdiff_04"]
F_E = ["fracdiff_04", "mom_10", "vol_10"]
F_G = ["mom_10", "mom_20", "vol_20", "atr_rel", "stoch_k"]
F_H = ["ret_1", "ret_2", "ret_3", "drawdown_60", "vol_10"]
F_I = ["parkinson_5", "mom_10", "vol_20", "rsi_14", "macd_rel"]
F_J = ["ret_5", "ret_10", "ma_ratio_20", "bb_pctb"]

STRATEGIES = {
    # SelectKBest + LogisticRegression - selection automatique (1-10)
    1: ("SelectK5_f_Log_C1", F_POOL, lambda: Pipeline([("sel", SelectKBest(f_classif, k=5)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("SelectK3_f_Log_C1", F_POOL, lambda: Pipeline([("sel", SelectKBest(f_classif, k=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    3: ("SelectK8_f_Log_C05", F_POOL, lambda: Pipeline([("sel", SelectKBest(f_classif, k=8)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    4: ("SelectK5_mi_Log_C1", F_POOL, lambda: Pipeline([("sel", SelectKBest(mutual_info_classif, k=5)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("SelectK3_mi_Log_C2", F_POOL, lambda: Pipeline([("sel", SelectKBest(mutual_info_classif, k=3)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    6: ("SelectK10_f_Log_C01", F_POOL, lambda: Pipeline([("sel", SelectKBest(f_classif, k=10)), ("lr", LogisticRegression(C=0.1, max_iter=1000, random_state=SEED))])),
    7: ("SelectK4_f_Log_C10", F_POOL, lambda: Pipeline([("sel", SelectKBest(f_classif, k=4)), ("lr", LogisticRegression(C=10.0, max_iter=1000, random_state=SEED))])),
    8: ("SelectK6_mi_Log_C05", F_POOL, lambda: Pipeline([("sel", SelectKBest(mutual_info_classif, k=6)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    9: ("SelectK7_f_Log_C02", F_POOL, lambda: Pipeline([("sel", SelectKBest(f_classif, k=7)), ("lr", LogisticRegression(C=0.2, max_iter=1000, random_state=SEED))])),
    10: ("SelectK2_mi_Log_C1", F_POOL, lambda: Pipeline([("sel", SelectKBest(mutual_info_classif, k=2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # AdaBoost(GaussianNB) - boosting avec base probabiliste (11-20)
    11: ("AdaBoost_NB_A", F_A, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=30, learning_rate=0.5, random_state=SEED)),
    12: ("AdaBoost_NB_B", F_B, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=50, learning_rate=0.3, random_state=SEED)),
    13: ("AdaBoost_NB_C", F_C, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=20, learning_rate=1.0, random_state=SEED)),
    14: ("AdaBoost_NB_D", F_D, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=40, learning_rate=0.2, random_state=SEED)),
    15: ("AdaBoost_NB_E", F_E, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=30, learning_rate=0.5, random_state=SEED)),
    16: ("AdaBoost_NB_G", F_G, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=25, learning_rate=0.8, random_state=SEED)),
    17: ("AdaBoost_NB_H", F_H, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=35, learning_rate=0.4, random_state=SEED)),
    18: ("AdaBoost_NB_I", F_I, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=45, learning_rate=0.3, random_state=SEED)),
    19: ("AdaBoost_NB_J", F_J, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=30, learning_rate=0.6, random_state=SEED)),
    20: ("AdaBoost_NB_wide", F_POOL, lambda: AdaBoostClassifier(estimator=GaussianNB(), n_estimators=30, learning_rate=0.5, random_state=SEED)),

    # Bagging(LDA/QDA) - ensemble de discriminants (21-30)
    21: ("Bagging_LDA_A", F_A, lambda: BaggingClassifier(estimator=LinearDiscriminantAnalysis(), n_estimators=15, random_state=SEED, n_jobs=1)),
    22: ("Bagging_QDA_B_reg01", F_B, lambda: BaggingClassifier(estimator=QuadraticDiscriminantAnalysis(reg_param=0.1), n_estimators=15, random_state=SEED, n_jobs=1)),
    23: ("Bagging_LDA_C_ms08", F_C, lambda: BaggingClassifier(estimator=LinearDiscriminantAnalysis(), n_estimators=20, max_samples=0.8, random_state=SEED, n_jobs=1)),
    24: ("Bagging_QDA_D_reg03", F_D, lambda: BaggingClassifier(estimator=QuadraticDiscriminantAnalysis(reg_param=0.3), n_estimators=15, random_state=SEED, n_jobs=1)),
    25: ("Bagging_LDA_E_shrink", F_E, lambda: BaggingClassifier(estimator=LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto"), n_estimators=15, random_state=SEED, n_jobs=1)),
    26: ("Bagging_LDA_G", F_G, lambda: BaggingClassifier(estimator=LinearDiscriminantAnalysis(), n_estimators=20, random_state=SEED, n_jobs=1)),
    27: ("Bagging_QDA_H_reg05", F_H, lambda: BaggingClassifier(estimator=QuadraticDiscriminantAnalysis(reg_param=0.5), n_estimators=15, max_samples=0.7, random_state=SEED, n_jobs=1)),
    28: ("Bagging_LDA_I", F_I, lambda: BaggingClassifier(estimator=LinearDiscriminantAnalysis(), n_estimators=15, random_state=SEED, n_jobs=1)),
    29: ("Bagging_QDA_J_reg00", F_J, lambda: BaggingClassifier(estimator=QuadraticDiscriminantAnalysis(reg_param=0.0), n_estimators=15, random_state=SEED, n_jobs=1)),
    30: ("Bagging_LDA_wide", F_POOL, lambda: BaggingClassifier(estimator=LinearDiscriminantAnalysis(), n_estimators=15, random_state=SEED, n_jobs=1)),

    # CalibratedClassifierCV(Bagging(DecisionTree)) - recalibration (31-38)
    31: ("CalibBaggingDT_sigmoid_A", F_A, lambda: CalibratedClassifierCV(BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=4, random_state=SEED), n_estimators=20, random_state=SEED, n_jobs=1), cv=3, method="sigmoid")),
    32: ("CalibBaggingDT_isotonic_B", F_B, lambda: CalibratedClassifierCV(BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=3, random_state=SEED), n_estimators=20, random_state=SEED, n_jobs=1), cv=3, method="isotonic")),
    33: ("CalibBaggingDT_sigmoid_C", F_C, lambda: CalibratedClassifierCV(BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=5, random_state=SEED), n_estimators=15, random_state=SEED, n_jobs=1), cv=3, method="sigmoid")),
    34: ("CalibBaggingDT_isotonic_D", F_D, lambda: CalibratedClassifierCV(BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=4, random_state=SEED), n_estimators=20, random_state=SEED, n_jobs=1), cv=3, method="isotonic")),
    35: ("CalibBaggingDT_sigmoid_G", F_G, lambda: CalibratedClassifierCV(BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=3, random_state=SEED), n_estimators=25, random_state=SEED, n_jobs=1), cv=3, method="sigmoid")),
    36: ("CalibBaggingDT_isotonic_H", F_H, lambda: CalibratedClassifierCV(BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=6, random_state=SEED), n_estimators=15, random_state=SEED, n_jobs=1), cv=3, method="isotonic")),
    37: ("CalibBaggingDT_sigmoid_I", F_I, lambda: CalibratedClassifierCV(BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=4, random_state=SEED), n_estimators=20, random_state=SEED, n_jobs=1), cv=3, method="sigmoid")),
    38: ("CalibBaggingDT_isotonic_J", F_J, lambda: CalibratedClassifierCV(BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=3, random_state=SEED), n_estimators=20, random_state=SEED, n_jobs=1), cv=3, method="isotonic")),

    # RadiusNeighborsClassifier - geometrique, rayon fixe (outliers geres) (39-50)
    39: ("RadiusNeighbors_r1_A", F_A, lambda: RadiusNeighborsClassifier(radius=1.0, outlier_label=0, weights="distance")),
    40: ("RadiusNeighbors_r15_B", F_B, lambda: RadiusNeighborsClassifier(radius=1.5, outlier_label=0, weights="distance")),
    41: ("RadiusNeighbors_r2_C", F_C, lambda: RadiusNeighborsClassifier(radius=2.0, outlier_label=0, weights="uniform")),
    42: ("RadiusNeighbors_r08_D", F_D, lambda: RadiusNeighborsClassifier(radius=0.8, outlier_label=0, weights="distance")),
    43: ("RadiusNeighbors_r12_E", F_E, lambda: RadiusNeighborsClassifier(radius=1.2, outlier_label=0, weights="distance")),
    44: ("RadiusNeighbors_r2_G", F_G, lambda: RadiusNeighborsClassifier(radius=2.0, outlier_label=0, weights="distance")),
    45: ("RadiusNeighbors_r1_H", F_H, lambda: RadiusNeighborsClassifier(radius=1.0, outlier_label=0, weights="uniform")),
    46: ("RadiusNeighbors_r25_I", F_I, lambda: RadiusNeighborsClassifier(radius=2.5, outlier_label=0, weights="distance")),
    47: ("RadiusNeighbors_r15_J", F_J, lambda: RadiusNeighborsClassifier(radius=1.5, outlier_label=0, weights="uniform")),
    48: ("SelectK4_mi_RF_A", F_POOL, lambda: Pipeline([("sel", SelectKBest(mutual_info_classif, k=4)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    49: ("SelectK6_f_RF_B", F_POOL, lambda: Pipeline([("sel", SelectKBest(f_classif, k=6)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    50: ("SelectK8_mi_RF_C", F_POOL, lambda: Pipeline([("sel", SelectKBest(mutual_info_classif, k=8)), ("rf", RandomForestClassifier(n_estimators=120, max_depth=5, random_state=SEED, n_jobs=1))])),
}
