"""
Itération 19 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 18 (TruncatedSVD, AdaBoost(LogReg), Stacking(GaussianNB),
Binarizer+ComplementNB, GMMBayesClassifier), itération 19 explore :

1. Pipeline(LOFAugment + LogisticRegression) — petit transformer maison
   (classe LOFAugment ci-dessous) qui ajoute le score de LocalOutlierFactor
   (en mode novelty=True, utilisable en walk-forward) comme feature
   supplémentaire — signal d'anomalie LOCAL (densité relative aux voisins),
   distinct du score IsolationForest (global, itération 14).
2. Pipeline(SelectFromModel(RandomForest) + LogisticRegression) —
   sélection de features par importance embarquée d'une forêt aléatoire,
   philosophie différente de la sélection univariée SelectKBest
   (itérations 10/15, basée sur des tests statistiques indépendants par
   feature).
3. Pipeline(KBinsDiscretizer(encode="onehot-dense") + LogisticRegression) —
   discrétisation en quantiles suivie d'un ENCODAGE ONE-HOT (permet à un
   modèle linéaire d'apprendre une relation en marches d'escalier/non
   linéaire), distinct de l'encodage ordinal utilisé avec les Naive Bayes
   (itérations 12/14).
4. BaggingClassifier(ExtraTreeClassifier, bootstrap=True) — ensemble bagged
   explicite d'arbres extrêmement randomisés (bootstrap au niveau de
   l'ensemble), distinct de ExtraTreesClassifier standard (bootstrap=False
   par défaut, itérations précédentes) et de sa variante bootstrap=True
   testée en itération 17 (qui reste un ExtraTreesClassifier, pas un
   Bagging générique).
5. Pipeline(PowerTransformer Yeo-Johnson + LogisticRegression) — cette
   normalisation avait été combinée à KNN (itération 12) mais jamais à un
   modèle linéaire.

Vitesse vérifiée sur n=9000 : toutes les familles <0.5s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier
from sklearn.tree import ExtraTreeClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import KBinsDiscretizer, PowerTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

SEED = 42


class LOFAugment(BaseEstimator, TransformerMixin):
    """Ajoute le score de LocalOutlierFactor (novelty=True, decision_function)
    comme colonne supplementaire -- signal d'anomalie LOCAL (densite relative
    aux voisins), distinct du score global d'IsolationForest (iteration 14)."""

    def __init__(self, n_neighbors=20):
        self.n_neighbors = n_neighbors

    def fit(self, X, y=None):
        self.lof_ = LocalOutlierFactor(n_neighbors=self.n_neighbors, novelty=True)
        self.lof_.fit(X)
        return self

    def transform(self, X):
        score = self.lof_.decision_function(X).reshape(-1, 1)
        return np.hstack([X, score])


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
    # Pipeline(LOFAugment + LogisticRegression) (1-10)
    1: ("LOFAugment_Log_A", F_A, lambda: Pipeline([("lof", LOFAugment(n_neighbors=20)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("LOFAugment_Log_B_n30", F_B, lambda: Pipeline([("lof", LOFAugment(n_neighbors=30)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    3: ("LOFAugment_Log_C", F_C, lambda: Pipeline([("lof", LOFAugment(n_neighbors=20)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    4: ("LOFAugment_Log_D", F_D, lambda: Pipeline([("lof", LOFAugment(n_neighbors=20)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("LOFAugment_Log_E_n10", F_E, lambda: Pipeline([("lof", LOFAugment(n_neighbors=10)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    6: ("LOFAugment_Log_F", F_F, lambda: Pipeline([("lof", LOFAugment(n_neighbors=20)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    7: ("LOFAugment_Log_G", F_G, lambda: Pipeline([("lof", LOFAugment(n_neighbors=20)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    8: ("LOFAugment_Log_H", F_H, lambda: Pipeline([("lof", LOFAugment(n_neighbors=20)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    9: ("LOFAugment_Log_I_n30", F_I, lambda: Pipeline([("lof", LOFAugment(n_neighbors=30)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    10: ("LOFAugment_Log_wide_K", F_K, lambda: Pipeline([("lof", LOFAugment(n_neighbors=20)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(SelectFromModel(RandomForest) + LogisticRegression) (11-20)
    11: ("SelectFromRF_Log_A", F_A, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    12: ("SelectFromRF_Log_B", F_B, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    13: ("SelectFromRF_Log_C", F_C, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    14: ("SelectFromRF_Log_D_n80", F_D, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    15: ("SelectFromRF_Log_E", F_E, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    16: ("SelectFromRF_Log_F", F_F, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    17: ("SelectFromRF_Log_G_median", F_G, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1), threshold="median")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    18: ("SelectFromRF_Log_H", F_H, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    19: ("SelectFromRF_Log_I", F_I, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    20: ("SelectFromRF_Log_wide_K", F_K, lambda: Pipeline([("sfm", SelectFromModel(RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1))), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(KBinsDiscretizer(onehot-dense) + LogisticRegression) (21-30)
    21: ("KBinsOneHot_Log_A", F_A, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="onehot-dense", strategy="quantile")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    22: ("KBinsOneHot_Log_B_b7", F_B, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=7, encode="onehot-dense", strategy="quantile")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    23: ("KBinsOneHot_Log_C", F_C, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="onehot-dense", strategy="quantile")), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    24: ("KBinsOneHot_Log_D_uniform", F_D, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=4, encode="onehot-dense", strategy="uniform")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    25: ("KBinsOneHot_Log_E", F_E, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="onehot-dense", strategy="quantile")), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    26: ("KBinsOneHot_Log_F", F_F, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="onehot-dense", strategy="quantile")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    27: ("KBinsOneHot_Log_G_b7", F_G, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=7, encode="onehot-dense", strategy="quantile")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    28: ("KBinsOneHot_Log_H", F_H, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="onehot-dense", strategy="quantile")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    29: ("KBinsOneHot_Log_I_uniform", F_I, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=4, encode="onehot-dense", strategy="uniform")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    30: ("KBinsOneHot_Log_wide_K", F_K, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="onehot-dense", strategy="quantile")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # BaggingClassifier(ExtraTreeClassifier, bootstrap=True) (31-40)
    31: ("Bagging_ExtraTree_A", F_A, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=30, bootstrap=True, random_state=SEED)),
    32: ("Bagging_ExtraTree_B_n50", F_B, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=50, bootstrap=True, random_state=SEED)),
    33: ("Bagging_ExtraTree_C", F_C, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=4, random_state=SEED), n_estimators=30, bootstrap=True, random_state=SEED)),
    34: ("Bagging_ExtraTree_D_maxsamp", F_D, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=30, bootstrap=True, max_samples=0.7, random_state=SEED)),
    35: ("Bagging_ExtraTree_E", F_E, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=30, bootstrap=True, random_state=SEED)),
    36: ("Bagging_ExtraTree_F", F_F, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=30, bootstrap=True, random_state=SEED)),
    37: ("Bagging_ExtraTree_G", F_G, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=4, random_state=SEED), n_estimators=30, bootstrap=True, random_state=SEED)),
    38: ("Bagging_ExtraTree_H", F_H, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=30, bootstrap=True, random_state=SEED)),
    39: ("Bagging_ExtraTree_I_maxsamp", F_I, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=3, random_state=SEED), n_estimators=30, bootstrap=True, max_samples=0.6, random_state=SEED)),
    40: ("Bagging_ExtraTree_wide_K", F_K, lambda: BaggingClassifier(estimator=ExtraTreeClassifier(max_depth=4, random_state=SEED), n_estimators=30, bootstrap=True, random_state=SEED)),

    # Pipeline(PowerTransformer Yeo-Johnson + LogisticRegression) (41-50)
    41: ("PowerYJ_Log_A", F_A, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    42: ("PowerYJ_Log_B", F_B, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    43: ("PowerYJ_Log_C", F_C, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    44: ("PowerYJ_Log_D", F_D, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    45: ("PowerYJ_Log_E", F_E, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    46: ("PowerYJ_Log_F", F_F, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    47: ("PowerYJ_Log_G", F_G, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    48: ("PowerYJ_Log_H", F_H, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    49: ("PowerYJ_Log_I", F_I, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    50: ("PowerYJ_Log_wide_K", F_K, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
}
