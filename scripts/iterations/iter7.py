"""
Itération 7 — 50 nouvelles hypothèses (univers figé a priori).

Itérations 3-6 ont couvert la quasi-totalité des classifieurs sklearn
usuels. Itération 7 explore deux axes différents des précédentes :

1. Modèles linéaires/géométriques calibrés jamais essayés :
   RidgeClassifier (linéaire, régularisation L2, pas de predict_proba
   natif), Perceptron (linéaire online, pas de predict_proba natif),
   NearestCentroid (géométrique — distance au centroïde de classe,
   fondamentalement différent des arbres/linéaires/probabilistes déjà
   testés). Tous calibrés via CalibratedClassifierCV.

2. Forme fonctionnelle différente plutôt que famille de modèle
   différente : Pipeline(PolynomialFeatures degré 2 + LogisticRegression)
   teste l'hypothèse que la relation features->direction est quadratique/
   avec interactions plutôt que linéaire ; Pipeline(PCA + LogisticRegression)
   teste l'hypothèse qu'une réduction de dimension non supervisée avant
   classification linéaire capture mieux le signal que les features brutes.
   Ces deux pipelines sont des hypothèses nouvelles même si le classifieur
   final (LogisticRegression) a déjà été testé sur les features brutes.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.linear_model import RidgeClassifier, Perceptron, LogisticRegression
from sklearn.neighbors import NearestCentroid
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

SEED = 42

F_A = ["mom_10", "vol_20", "rsi_14"]
F_B = ["mom_10", "vol_ratio", "atr_rel", "mom_20"]
F_C = ["mom_20", "ma_ratio_50", "vol_10", "stoch_k"]
F_D = ["drawdown_60", "vol_20", "rsi_14", "fracdiff_04"]
F_E = ["fracdiff_04", "mom_10", "vol_10"]
F_F = ["stoch_k", "macd_rel", "bb_pctb", "ma_ratio_50"]
F_G = ["mom_10", "mom_20", "vol_20", "atr_rel", "stoch_k"]
F_H = ["ret_1", "ret_2", "ret_3", "drawdown_60", "vol_10"]
F_I = ["parkinson_5", "mom_10", "vol_20", "rsi_14", "macd_rel"]
F_J = ["ret_5", "ret_10", "ma_ratio_20", "bb_pctb"]
F_K = ["mom_10", "mom_20", "vol_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "atr_rel", "stoch_k"]
F_L = ["ret_1", "ret_2", "ret_3", "ret_5", "drawdown_60", "fracdiff_04", "ma_ratio_20", "ma_ratio_50"]

STRATEGIES = {
    # CalibratedClassifierCV(RidgeClassifier) - lineaire L2, pas predict_proba natif (1-8)
    1: ("CalibRidge_a01_A", F_A, lambda: CalibratedClassifierCV(RidgeClassifier(alpha=0.1, random_state=SEED), cv=3, method="sigmoid")),
    2: ("CalibRidge_a1_A", F_A, lambda: CalibratedClassifierCV(RidgeClassifier(alpha=1.0, random_state=SEED), cv=3, method="sigmoid")),
    3: ("CalibRidge_a10_iso_B", F_B, lambda: CalibratedClassifierCV(RidgeClassifier(alpha=10.0, random_state=SEED), cv=3, method="isotonic")),
    4: ("CalibRidge_a001_C", F_C, lambda: CalibratedClassifierCV(RidgeClassifier(alpha=0.01, random_state=SEED), cv=3, method="sigmoid")),
    5: ("CalibRidge_a50_D", F_D, lambda: CalibratedClassifierCV(RidgeClassifier(alpha=50.0, random_state=SEED), cv=3, method="sigmoid")),
    6: ("CalibRidge_a1_iso_G", F_G, lambda: CalibratedClassifierCV(RidgeClassifier(alpha=1.0, random_state=SEED), cv=3, method="isotonic")),
    7: ("CalibRidge_a5_H", F_H, lambda: CalibratedClassifierCV(RidgeClassifier(alpha=5.0, random_state=SEED), cv=3, method="sigmoid")),
    8: ("CalibRidge_a02_K", F_K, lambda: CalibratedClassifierCV(RidgeClassifier(alpha=0.2, random_state=SEED), cv=3, method="sigmoid")),

    # CalibratedClassifierCV(Perceptron) - lineaire online, pas predict_proba natif (9-16)
    9: ("CalibPerceptron_A", F_A, lambda: CalibratedClassifierCV(Perceptron(alpha=1e-4, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    10: ("CalibPerceptron_B", F_B, lambda: CalibratedClassifierCV(Perceptron(alpha=1e-3, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    11: ("CalibPerceptron_l2_C", F_C, lambda: CalibratedClassifierCV(Perceptron(penalty="l2", alpha=1e-3, max_iter=1000, random_state=SEED), cv=3, method="isotonic")),
    12: ("CalibPerceptron_l1_D", F_D, lambda: CalibratedClassifierCV(Perceptron(penalty="l1", alpha=1e-3, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    13: ("CalibPerceptron_elastic_E", F_E, lambda: CalibratedClassifierCV(Perceptron(penalty="elasticnet", alpha=1e-3, l1_ratio=0.3, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    14: ("CalibPerceptron_H", F_H, lambda: CalibratedClassifierCV(Perceptron(alpha=1e-2, max_iter=1000, random_state=SEED), cv=3, method="isotonic")),
    15: ("CalibPerceptron_I", F_I, lambda: CalibratedClassifierCV(Perceptron(alpha=1e-5, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    16: ("CalibPerceptron_K", F_K, lambda: CalibratedClassifierCV(Perceptron(alpha=1e-3, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),

    # CalibratedClassifierCV(NearestCentroid) - geometrique, distance au centroide (17-22)
    17: ("CalibNearestCentroid_A", F_A, lambda: CalibratedClassifierCV(NearestCentroid(), cv=3, method="sigmoid")),
    18: ("CalibNearestCentroid_manhattan_B", F_B, lambda: CalibratedClassifierCV(NearestCentroid(metric="manhattan"), cv=3, method="sigmoid")),
    19: ("CalibNearestCentroid_shrink_C", F_C, lambda: CalibratedClassifierCV(NearestCentroid(shrink_threshold=0.2), cv=3, method="isotonic")),
    20: ("CalibNearestCentroid_D", F_D, lambda: CalibratedClassifierCV(NearestCentroid(), cv=3, method="sigmoid")),
    21: ("CalibNearestCentroid_shrink_H", F_H, lambda: CalibratedClassifierCV(NearestCentroid(shrink_threshold=0.5), cv=3, method="sigmoid")),
    22: ("CalibNearestCentroid_K", F_K, lambda: CalibratedClassifierCV(NearestCentroid(), cv=3, method="isotonic")),

    # Pipeline(PolynomialFeatures degre 2 + LogisticRegression) - forme quadratique/interactions (23-36)
    23: ("Poly2_Log_A_C1", F_A, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    24: ("Poly2_Log_A_C01", F_A, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=0.1, max_iter=1000, random_state=SEED))])),
    25: ("Poly2_Log_B_C1", F_B, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    26: ("Poly2_interact_C_C1", F_C, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    27: ("Poly2_Log_D_C05", F_D, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    28: ("Poly2_interact_E_C1", F_E, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    29: ("Poly2_Log_F_C10", F_F, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=10.0, max_iter=1000, random_state=SEED))])),
    30: ("Poly2_Log_G_C1", F_G, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    31: ("Poly2_interact_H_C1", F_H, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    32: ("Poly2_Log_I_C02", F_I, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=0.2, max_iter=1000, random_state=SEED))])),
    33: ("Poly2_Log_J_C1", F_J, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    34: ("Poly2_interact_A_C5", F_A, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=5.0, max_iter=1000, random_state=SEED))])),
    35: ("Poly2_Log_E_C02", F_E, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=0.2, max_iter=1000, random_state=SEED))])),
    36: ("Poly2_Log_D_C10", F_D, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("lr", LogisticRegression(C=10.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(PCA + LogisticRegression) - reduction de dimension non supervisee (37-50)
    37: ("PCA2_Log_K_C1", F_K, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    38: ("PCA3_Log_K_C1", F_K, lambda: Pipeline([("pca", PCA(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    39: ("PCA4_Log_K_C05", F_K, lambda: Pipeline([("pca", PCA(n_components=4, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    40: ("PCA2_Log_L_C1", F_L, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    41: ("PCA3_Log_L_C1", F_L, lambda: Pipeline([("pca", PCA(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    42: ("PCA5_Log_L_C02", F_L, lambda: Pipeline([("pca", PCA(n_components=5, random_state=SEED)), ("lr", LogisticRegression(C=0.2, max_iter=1000, random_state=SEED))])),
    43: ("PCA1_Log_K_C1", F_K, lambda: Pipeline([("pca", PCA(n_components=1, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    44: ("PCA2_Log_A_C1", F_A, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    45: ("PCA2_Log_G_C1", F_G, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    46: ("PCA3_Log_G_C10", F_G, lambda: Pipeline([("pca", PCA(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=10.0, max_iter=1000, random_state=SEED))])),
    47: ("PCA4_Log_K_C1", F_K, lambda: Pipeline([("pca", PCA(n_components=4, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    48: ("PCA6_Log_K_C05", F_K, lambda: Pipeline([("pca", PCA(n_components=6, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    49: ("PCA2_Log_H_C1", F_H, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    50: ("PCA3_Log_L_C005", F_L, lambda: Pipeline([("pca", PCA(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=0.05, max_iter=1000, random_state=SEED))])),
}
