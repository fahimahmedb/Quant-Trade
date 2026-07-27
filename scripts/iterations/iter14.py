"""
Itération 14 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 13 (arbre autonome, projections aléatoires, GMM-features,
Bagging(NearestCentroid), MiniBatchKMeans), itération 14 explore :

1. CalibratedClassifierCV(RidgeClassifierCV) — RidgeClassifier avec
   sélection automatique de l'hyperparamètre alpha par validation croisée
   interne à chaque réestimation (RidgeClassifierCV, forme fermée via SVD
   -> quasi-instantané, contrairement à LogisticRegressionCV qui avait été
   écarté en itération 13 pour coût O(n^2)). RidgeClassifier "fixe" avait
   déjà été testé via CalibratedClassifierCV (itération 7) mais jamais la
   version à alpha auto-sélectionné.
2. Pipeline(IsoForestAugment + LogisticRegression) — petit transformer
   maison (classe IsoForestAugment ci-dessous) qui ajoute le score
   d'anomalie d'un IsolationForest comme feature supplémentaire avant une
   régression logistique — jamais utilisé (aucune itération précédente
   n'exploite un signal de détection d'anomalie).
3. BaggingClassifier(GaussianNB) — jamais essayé (Bagging avait déjà été
   combiné à Tree/LDA/QDA/LogReg/KNN/NearestCentroid, mais pas encore à
   GaussianNB).
4. Pipeline(KBinsDiscretizer + MultinomialNB/ComplementNB) — ces deux NB
   avaient été testées avec MinMaxScaler (itération 8, features continues
   dans [0,1]), jamais avec une vraie discrétisation en comptages ordinaux
   (usage plus canonique de Multinomial/ComplementNB).
5. StackingClassifier(final_estimator=HistGradientBoostingClassifier,
   config légère max_iter=20/max_depth=2/cv=2) — méta-modèle non linéaire
   distinct de RandomForest (itération 11) et LogisticRegression (toutes
   les itérations précédentes). Configuration allégée après mesure de
   vitesse (version par défaut : ~9s/fit extrapolé sur grande fenêtre,
   trop coûteuse pour 10 variantes ; version légère : <0.6s/fit à n=9000).

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
import numpy as np
from sklearn.linear_model import RidgeClassifierCV, LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import IsolationForest, BaggingClassifier, StackingClassifier, HistGradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB, ComplementNB
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

SEED = 42


class IsoForestAugment(BaseEstimator, TransformerMixin):
    """Ajoute le score d'anomalie (score_samples) d'un IsolationForest comme
    colonne supplementaire aux features brutes -- jamais utilise jusqu'ici."""

    def __init__(self, n_estimators=50, random_state=SEED):
        self.n_estimators = n_estimators
        self.random_state = random_state

    def fit(self, X, y=None):
        self.iso_ = IsolationForest(n_estimators=self.n_estimators, random_state=self.random_state, n_jobs=1)
        self.iso_.fit(X)
        return self

    def transform(self, X):
        score = self.iso_.score_samples(X).reshape(-1, 1)
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
    # CalibratedClassifierCV(RidgeClassifierCV) (1-10)
    1: ("CalibRidgeCV_A", F_A, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3)),
    2: ("CalibRidgeCV_B_wide", F_B, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.01, 0.1, 1.0, 10.0, 100.0)), cv=3)),
    3: ("CalibRidgeCV_C", F_C, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3)),
    4: ("CalibRidgeCV_D_cv5", F_D, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=5)),
    5: ("CalibRidgeCV_E", F_E, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3)),
    6: ("CalibRidgeCV_F", F_F, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.01, 0.1, 1.0, 10.0)), cv=3)),
    7: ("CalibRidgeCV_G", F_G, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3)),
    8: ("CalibRidgeCV_H_cv5", F_H, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=5)),
    9: ("CalibRidgeCV_I", F_I, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.01, 0.1, 1.0, 10.0)), cv=3)),
    10: ("CalibRidgeCV_wide_K", F_K, lambda: CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0, 100.0)), cv=3)),

    # Pipeline(IsoForestAugment + LogisticRegression) (11-20)
    11: ("IsoForestAug_Log_A", F_A, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=50)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    12: ("IsoForestAug_Log_B_n80", F_B, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=80)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    13: ("IsoForestAug_Log_C", F_C, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=50)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    14: ("IsoForestAug_Log_D", F_D, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=50)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    15: ("IsoForestAug_Log_E", F_E, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=50)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    16: ("IsoForestAug_Log_F_n30", F_F, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=30)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    17: ("IsoForestAug_Log_G", F_G, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=50)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    18: ("IsoForestAug_Log_H", F_H, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=50)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    19: ("IsoForestAug_Log_I", F_I, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=80)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    20: ("IsoForestAug_Log_wide_K", F_K, lambda: Pipeline([("iso", IsoForestAugment(n_estimators=50)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # BaggingClassifier(GaussianNB) (21-30)
    21: ("Bagging_GNB_A", F_A, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=20, random_state=SEED)),
    22: ("Bagging_GNB_B_n30", F_B, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=30, random_state=SEED)),
    23: ("Bagging_GNB_C", F_C, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=20, random_state=SEED)),
    24: ("Bagging_GNB_D", F_D, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=25, random_state=SEED)),
    25: ("Bagging_GNB_E", F_E, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=20, random_state=SEED)),
    26: ("Bagging_GNB_F_n40", F_F, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=40, random_state=SEED)),
    27: ("Bagging_GNB_G", F_G, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=20, random_state=SEED)),
    28: ("Bagging_GNB_H", F_H, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=25, random_state=SEED)),
    29: ("Bagging_GNB_I", F_I, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=20, random_state=SEED)),
    30: ("Bagging_GNB_wide_K", F_K, lambda: BaggingClassifier(estimator=GaussianNB(), n_estimators=30, random_state=SEED)),

    # Pipeline(KBinsDiscretizer + MultinomialNB/ComplementNB) (31-40)
    31: ("KBins_MultiNB_A", F_A, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", MultinomialNB())])),
    32: ("KBins_MultiNB_B_b7", F_B, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=7, encode="ordinal", strategy="quantile")), ("nb", MultinomialNB())])),
    33: ("KBins_MultiNB_C", F_C, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", MultinomialNB())])),
    34: ("KBins_MultiNB_D_uniform", F_D, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="uniform")), ("nb", MultinomialNB())])),
    35: ("KBins_MultiNB_wide_K", F_K, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", MultinomialNB())])),
    36: ("KBins_ComplNB_E", F_E, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", ComplementNB())])),
    37: ("KBins_ComplNB_F_b7", F_F, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=7, encode="ordinal", strategy="quantile")), ("nb", ComplementNB())])),
    38: ("KBins_ComplNB_G", F_G, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", ComplementNB())])),
    39: ("KBins_ComplNB_J_uniform", F_J, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="uniform")), ("nb", ComplementNB())])),
    40: ("KBins_ComplNB_wide_K", F_K, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", ComplementNB())])),

    # StackingClassifier(final_estimator=HistGradientBoostingClassifier, config legere) (41-50)
    41: ("StackHistGB_A", F_A, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=20, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
    42: ("StackHistGB_B", F_B, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=20, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
    43: ("StackHistGB_3base_C", F_C, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", CalibratedClassifierCV(RidgeClassifierCV(), cv=2))], final_estimator=HistGradientBoostingClassifier(max_iter=20, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
    44: ("StackHistGB_D_iter30", F_D, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=30, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
    45: ("StackHistGB_E", F_E, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=20, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
    46: ("StackHistGB_F", F_F, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=20, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
    47: ("StackHistGB_G_depth3", F_G, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=20, max_depth=3, random_state=SEED), cv=2, n_jobs=1)),
    48: ("StackHistGB_H", F_H, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=20, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
    49: ("StackHistGB_I", F_I, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=20, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
    50: ("StackHistGB_wide_K", F_K, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=HistGradientBoostingClassifier(max_iter=30, max_depth=2, random_state=SEED), cv=2, n_jobs=1)),
}
