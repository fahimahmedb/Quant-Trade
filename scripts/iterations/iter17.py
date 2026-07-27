"""
Itération 17 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 16 (Normalizer par observation, SGD hinge calibré,
Bagging(SGD), QDA régularisée), itération 17 explore :

1. Pipeline(RobustScaler + LogisticRegression) — mise à l'échelle par
   médiane/IQR (résistante aux outliers), jamais utilisée jusqu'ici (seul
   StandardScaler, MinMaxScaler, QuantileTransformer, PowerTransformer et
   Normalizer avaient été testés). Motivation spécifique au projet :
   l'Étape A a établi des queues épaisses (ν≈4,8) sur les rendements — un
   scaler robuste aux outliers est une hypothèse mieux motivée qu'un
   scaler standard sur ce type de distribution.
2. Pipeline(RobustScaler + KNeighborsClassifier) — même motivation pour un
   classifieur géométrique, dont les distances sont sensibles aux valeurs
   extrêmes.
3. Pipeline(PCA(whiten=True) + LogisticRegression) — composantes PCA
   blanchies (variance unitaire, décorrélées), distinct de la PCA "brute"
   déjà testée en itération 8.
4. ExtraTreesClassifier(bootstrap=True) — ExtraTrees a bootstrap=False par
   défaut (et avait toujours été utilisé ainsi jusqu'ici) ; activer le
   bootstrap change le compromis biais/variance de l'ensemble, jamais
   exploré.
5. CalibratedClassifierCV(SGDClassifier(loss="squared_hinge")) — perte
   SGD supplémentaire jamais testée (log_loss et modified_huber en
   itération 4, hinge en itération 16).

Vitesse vérifiée sur n=9000 : toutes les familles <0.2s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.calibration import CalibratedClassifierCV
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
    # Pipeline(RobustScaler + LogisticRegression) (1-10)
    1: ("RobustScaler_Log_A", F_A, lambda: Pipeline([("rs", RobustScaler()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("RobustScaler_Log_B", F_B, lambda: Pipeline([("rs", RobustScaler()), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    3: ("RobustScaler_Log_C", F_C, lambda: Pipeline([("rs", RobustScaler()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    4: ("RobustScaler_Log_D_quantrange", F_D, lambda: Pipeline([("rs", RobustScaler(quantile_range=(10.0, 90.0))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("RobustScaler_Log_E", F_E, lambda: Pipeline([("rs", RobustScaler()), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    6: ("RobustScaler_Log_F", F_F, lambda: Pipeline([("rs", RobustScaler()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    7: ("RobustScaler_Log_G_quantrange", F_G, lambda: Pipeline([("rs", RobustScaler(quantile_range=(15.0, 85.0))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    8: ("RobustScaler_Log_H", F_H, lambda: Pipeline([("rs", RobustScaler()), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    9: ("RobustScaler_Log_I", F_I, lambda: Pipeline([("rs", RobustScaler()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    10: ("RobustScaler_Log_wide_K", F_K, lambda: Pipeline([("rs", RobustScaler()), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(RobustScaler + KNeighborsClassifier) (11-20)
    11: ("RobustScaler_KNN_A", F_A, lambda: Pipeline([("rs", RobustScaler()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    12: ("RobustScaler_KNN_B", F_B, lambda: Pipeline([("rs", RobustScaler()), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    13: ("RobustScaler_KNN_C", F_C, lambda: Pipeline([("rs", RobustScaler()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    14: ("RobustScaler_KNN_D_quantrange", F_D, lambda: Pipeline([("rs", RobustScaler(quantile_range=(10.0, 90.0))), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    15: ("RobustScaler_KNN_E", F_E, lambda: Pipeline([("rs", RobustScaler()), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))])),
    16: ("RobustScaler_KNN_F", F_F, lambda: Pipeline([("rs", RobustScaler()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    17: ("RobustScaler_KNN_G", F_G, lambda: Pipeline([("rs", RobustScaler()), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    18: ("RobustScaler_KNN_H", F_H, lambda: Pipeline([("rs", RobustScaler()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    19: ("RobustScaler_KNN_I_quantrange", F_I, lambda: Pipeline([("rs", RobustScaler(quantile_range=(15.0, 85.0))), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    20: ("RobustScaler_KNN_wide_K", F_K, lambda: Pipeline([("rs", RobustScaler()), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),

    # Pipeline(PCA(whiten=True) + LogisticRegression) (21-30)
    21: ("PCAwhiten_Log_A", F_A, lambda: Pipeline([("pca", PCA(n_components=2, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    22: ("PCAwhiten_Log_B_c1", F_B, lambda: Pipeline([("pca", PCA(n_components=1, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    23: ("PCAwhiten_Log_C", F_C, lambda: Pipeline([("pca", PCA(n_components=2, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    24: ("PCAwhiten_Log_D", F_D, lambda: Pipeline([("pca", PCA(n_components=2, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    25: ("PCAwhiten_Log_E_c1", F_E, lambda: Pipeline([("pca", PCA(n_components=1, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    26: ("PCAwhiten_Log_F", F_F, lambda: Pipeline([("pca", PCA(n_components=2, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    27: ("PCAwhiten_Log_G", F_G, lambda: Pipeline([("pca", PCA(n_components=2, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    28: ("PCAwhiten_Log_H", F_H, lambda: Pipeline([("pca", PCA(n_components=2, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    29: ("PCAwhiten_Log_I", F_I, lambda: Pipeline([("pca", PCA(n_components=2, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    30: ("PCAwhiten_Log_wide_K_c3", F_K, lambda: Pipeline([("pca", PCA(n_components=3, whiten=True, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # ExtraTreesClassifier(bootstrap=True) (31-40)
    31: ("ExtraTrees_bootstrap_A", F_A, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=3, bootstrap=True, random_state=SEED, n_jobs=1)),
    32: ("ExtraTrees_bootstrap_B_n150", F_B, lambda: ExtraTreesClassifier(n_estimators=150, max_depth=3, bootstrap=True, random_state=SEED, n_jobs=1)),
    33: ("ExtraTrees_bootstrap_C", F_C, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=4, bootstrap=True, random_state=SEED, n_jobs=1)),
    34: ("ExtraTrees_bootstrap_D_oob", F_D, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=3, bootstrap=True, max_samples=0.7, random_state=SEED, n_jobs=1)),
    35: ("ExtraTrees_bootstrap_E", F_E, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=3, bootstrap=True, random_state=SEED, n_jobs=1)),
    36: ("ExtraTrees_bootstrap_F", F_F, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=4, bootstrap=True, random_state=SEED, n_jobs=1)),
    37: ("ExtraTrees_bootstrap_G_maxsamp", F_G, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=3, bootstrap=True, max_samples=0.6, random_state=SEED, n_jobs=1)),
    38: ("ExtraTrees_bootstrap_H", F_H, lambda: ExtraTreesClassifier(n_estimators=120, max_depth=4, bootstrap=True, random_state=SEED, n_jobs=1)),
    39: ("ExtraTrees_bootstrap_I", F_I, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=3, bootstrap=True, random_state=SEED, n_jobs=1)),
    40: ("ExtraTrees_bootstrap_wide_K", F_K, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=4, bootstrap=True, random_state=SEED, n_jobs=1)),

    # CalibratedClassifierCV(SGDClassifier(loss="squared_hinge")) (41-50)
    41: ("CalibSGD_sqhinge_A", F_A, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-4, random_state=SEED), cv=3)),
    42: ("CalibSGD_sqhinge_B", F_B, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-3, random_state=SEED), cv=3)),
    43: ("CalibSGD_sqhinge_C", F_C, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-4, random_state=SEED), cv=3)),
    44: ("CalibSGD_sqhinge_D_cv5", F_D, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-4, random_state=SEED), cv=5)),
    45: ("CalibSGD_sqhinge_E", F_E, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-5, random_state=SEED), cv=3)),
    46: ("CalibSGD_sqhinge_F_elastic", F_F, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-4, penalty="elasticnet", random_state=SEED), cv=3)),
    47: ("CalibSGD_sqhinge_G", F_G, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-4, random_state=SEED), cv=3)),
    48: ("CalibSGD_sqhinge_H", F_H, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-3, random_state=SEED), cv=3)),
    49: ("CalibSGD_sqhinge_I_cv5", F_I, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-4, random_state=SEED), cv=5)),
    50: ("CalibSGD_sqhinge_wide_K", F_K, lambda: CalibratedClassifierCV(SGDClassifier(loss="squared_hinge", alpha=1e-4, random_state=SEED), cv=3)),
}
