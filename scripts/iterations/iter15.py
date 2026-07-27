"""
Itération 15 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 14 (Ridge calibré, anomalie, Bagging(NB), NB discrétisé,
Stacking->HistGB), itération 15 explore :

1. AdaBoostClassifier(ExtraTreeClassifier) — apprenant faible extrêmement
   randomisé (ExtraTreeClassifier, jamais utilisé comme base AdaBoost ;
   seul DecisionTreeClassifier "stump" et RF/ET (ensemblistes) l'avaient
   été).
2. Pipeline(SelectKBest + KNeighborsClassifier) — sélection de features
   univariée puis classifieur géométrique, jamais combinés (SelectKBest
   avait été associé à LogReg/RF en itération 10 uniquement).
3. Pipeline(SelectKBest + MinMaxScaler + ComplementNB) — sélection de
   features avant Naive Bayes, jamais combinés (ComplementNB avait été
   testé avec MinMaxScaler seul en itération 8, sans sélection préalable).
4. Pipeline(FeatureUnion(PCA, passthrough) + LogisticRegression) — AJOUTE
   les composantes PCA aux features brutes (augmentation) au lieu de les
   REMPLACER comme en itération 8 (Pipeline(PCA+LogReg) substituait
   entièrement les features) — structure de pipeline différente
   (FeatureUnion jamais utilisé jusqu'ici).
5. VotingClassifier(soft) à 3 membres purement linéaires/probabilistes
   (LogisticRegression + GaussianNB + CalibratedClassifierCV(RidgeClassifierCV))
   — comité sans aucun membre géométrique/arbre, jamais assemblé (itération
   11 utilisait des comités avec KNN/RadiusNeighbors comme membre).

Vitesse vérifiée sur la plus grande fenêtre d'entraînement réaliste
(n=9000, proche de la fin de l'historique NDX) : toutes les familles
<0.4s/fit, aucun risque de répéter les problèmes de coût des itérations
10-11 (Bagging(RF/ET/SVC), Birch, LogisticRegressionCV).

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.tree import ExtraTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, VotingClassifier
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import ComplementNB, GaussianNB
from sklearn.preprocessing import MinMaxScaler, FunctionTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.linear_model import LogisticRegression, RidgeClassifierCV
from sklearn.calibration import CalibratedClassifierCV

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
    # AdaBoostClassifier(ExtraTreeClassifier) (1-10)
    1: ("AdaBoost_ExtraTree_A", F_A, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=2, random_state=SEED), n_estimators=50, random_state=SEED)),
    2: ("AdaBoost_ExtraTree_B_n80", F_B, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=2, random_state=SEED), n_estimators=80, random_state=SEED)),
    3: ("AdaBoost_ExtraTree_C", F_C, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=50, random_state=SEED)),
    4: ("AdaBoost_ExtraTree_D", F_D, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=2, random_state=SEED), n_estimators=50, random_state=SEED)),
    5: ("AdaBoost_ExtraTree_E_lr05", F_E, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=2, random_state=SEED), n_estimators=50, learning_rate=0.5, random_state=SEED)),
    6: ("AdaBoost_ExtraTree_F", F_F, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=2, random_state=SEED), n_estimators=50, random_state=SEED)),
    7: ("AdaBoost_ExtraTree_G_d3", F_G, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=60, random_state=SEED)),
    8: ("AdaBoost_ExtraTree_H", F_H, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=2, random_state=SEED), n_estimators=50, random_state=SEED)),
    9: ("AdaBoost_ExtraTree_I_n100", F_I, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=2, random_state=SEED), n_estimators=100, random_state=SEED)),
    10: ("AdaBoost_ExtraTree_wide_K", F_K, lambda: AdaBoostClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=50, random_state=SEED)),

    # Pipeline(SelectKBest + KNeighborsClassifier) (11-20)
    11: ("SelectK_KNN_A", F_A, lambda: Pipeline([("skb", SelectKBest(f_classif, k=2)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    12: ("SelectK_KNN_B_mi", F_B, lambda: Pipeline([("skb", SelectKBest(mutual_info_classif, k=2)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    13: ("SelectK_KNN_C", F_C, lambda: Pipeline([("skb", SelectKBest(f_classif, k=2)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    14: ("SelectK_KNN_D", F_D, lambda: Pipeline([("skb", SelectKBest(f_classif, k=2)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    15: ("SelectK_KNN_E_mi", F_E, lambda: Pipeline([("skb", SelectKBest(mutual_info_classif, k=2)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    16: ("SelectK_KNN_F", F_F, lambda: Pipeline([("skb", SelectKBest(f_classif, k=2)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    17: ("SelectK_KNN_G_k3", F_G, lambda: Pipeline([("skb", SelectKBest(f_classif, k=3)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    18: ("SelectK_KNN_H", F_H, lambda: Pipeline([("skb", SelectKBest(f_classif, k=3)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    19: ("SelectK_KNN_I_mi_k3", F_I, lambda: Pipeline([("skb", SelectKBest(mutual_info_classif, k=3)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    20: ("SelectK_KNN_wide_K", F_K, lambda: Pipeline([("skb", SelectKBest(f_classif, k=4)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),

    # Pipeline(SelectKBest + MinMaxScaler + ComplementNB) (21-30)
    21: ("SelectK_ComplNB_A", F_A, lambda: Pipeline([("skb", SelectKBest(f_classif, k=2)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    22: ("SelectK_ComplNB_B_mi", F_B, lambda: Pipeline([("skb", SelectKBest(mutual_info_classif, k=2)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    23: ("SelectK_ComplNB_C", F_C, lambda: Pipeline([("skb", SelectKBest(f_classif, k=2)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    24: ("SelectK_ComplNB_D", F_D, lambda: Pipeline([("skb", SelectKBest(f_classif, k=2)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    25: ("SelectK_ComplNB_E_mi", F_E, lambda: Pipeline([("skb", SelectKBest(mutual_info_classif, k=2)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    26: ("SelectK_ComplNB_F", F_F, lambda: Pipeline([("skb", SelectKBest(f_classif, k=2)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    27: ("SelectK_ComplNB_G_k3", F_G, lambda: Pipeline([("skb", SelectKBest(f_classif, k=3)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    28: ("SelectK_ComplNB_H", F_H, lambda: Pipeline([("skb", SelectKBest(f_classif, k=3)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    29: ("SelectK_ComplNB_I_mi_k3", F_I, lambda: Pipeline([("skb", SelectKBest(mutual_info_classif, k=3)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    30: ("SelectK_ComplNB_wide_K", F_K, lambda: Pipeline([("skb", SelectKBest(f_classif, k=4)), ("mm", MinMaxScaler()), ("nb", ComplementNB())])),

    # Pipeline(FeatureUnion(PCA, passthrough) + LogisticRegression) (31-40)
    31: ("PCAUnion_Log_A", F_A, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=2, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    32: ("PCAUnion_Log_B_c1", F_B, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=1, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    33: ("PCAUnion_Log_C", F_C, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=2, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    34: ("PCAUnion_Log_D", F_D, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=2, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    35: ("PCAUnion_Log_E_c1", F_E, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=1, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    36: ("PCAUnion_Log_F", F_F, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=2, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    37: ("PCAUnion_Log_G", F_G, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=2, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    38: ("PCAUnion_Log_H", F_H, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=2, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    39: ("PCAUnion_Log_I", F_I, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=2, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    40: ("PCAUnion_Log_wide_K_c3", F_K, lambda: Pipeline([("fu", FeatureUnion([("pca", PCA(n_components=3, random_state=SEED)), ("id", FunctionTransformer())])), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # VotingClassifier(soft) : comite purement lineaire/probabiliste (41-50)
    41: ("VotingLinNB_A", F_A, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", n_jobs=1)),
    42: ("VotingLinNB_B_weighted", F_B, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", weights=[2, 1, 1], n_jobs=1)),
    43: ("VotingLinNB_C", F_C, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", n_jobs=1)),
    44: ("VotingLinNB_D", F_D, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", n_jobs=1)),
    45: ("VotingLinNB_E", F_E, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", n_jobs=1)),
    46: ("VotingLinNB_F_2way", F_F, lambda: VotingClassifier(estimators=[("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", n_jobs=1)),
    47: ("VotingLinNB_G", F_G, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", n_jobs=1)),
    48: ("VotingLinNB_H_weighted", F_H, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", weights=[1, 1, 2], n_jobs=1)),
    49: ("VotingLinNB_I", F_I, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", n_jobs=1)),
    50: ("VotingLinNB_wide_K", F_K, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(), cv=3))], voting="soft", n_jobs=1)),
}
