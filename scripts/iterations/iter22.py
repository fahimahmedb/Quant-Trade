"""
Itération 22 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 21 (Bagging(Spline+LogReg), Voting(Spline+RF+NB), Spline+
HistGB, AdaBoost(RidgeCV calibré), RobustScaler+Spline+LogReg), itération 22
explore :

1. Pipeline(FactorAnalysis + LogisticRegression) — modèle probabiliste à
   facteurs latents, jamais utilisé (distinct de PCA/FeatureAgglomeration/
   TruncatedSVD/GaussianRandomProjection/SparseRandomProjection déjà
   testés : FactorAnalysis modélise explicitement un bruit résiduel par
   variable plutôt qu'une simple projection linéaire).
2. Pipeline(OCSVMAugment + LogisticRegression) — petit transformer maison
   (classe OCSVMAugment ci-dessous) qui ajoute le score de frontière d'un
   OneClassSVM comme feature supplémentaire — signal d'anomalie basé sur
   une frontière de décision à noyau RBF, distinct des scores
   IsolationForest (itération 14, global/arbre) et LocalOutlierFactor
   (itération 19, densité locale).
3. Pipeline(SplineTransformer + KNeighborsClassifier) — base de splines
   jamais combinée à un classifieur géométrique (LogReg/RidgeCV/HistGB/RF
   testés en itérations 20-21).
4. CalibratedClassifierCV(SGDClassifier(loss="perceptron")) — perte SGD
   supplémentaire jamais testée (log_loss, modified_huber, hinge,
   squared_hinge déjà couverts).
5. StackingClassifier(final_estimator=KNeighborsClassifier) — méta-modèle
   géométrique plutôt que discriminant/génératif (LogReg, RF, HistGB,
   GaussianNB déjà utilisés comme final_estimator), jamais essayé.

Vitesse vérifiée sur n=9000 : toutes les familles <1.8s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
import numpy as np
from sklearn.decomposition import FactorAnalysis
from sklearn.svm import OneClassSVM
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.preprocessing import SplineTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import StackingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

SEED = 42


class OCSVMAugment(BaseEstimator, TransformerMixin):
    """Ajoute le score de decision_function d'un OneClassSVM (noyau RBF)
    comme colonne supplementaire -- signal d'anomalie base sur une frontiere
    a noyau, distinct d'IsolationForest (iteration 14, global/arbre) et de
    LocalOutlierFactor (iteration 19, densite locale)."""

    def __init__(self, nu=0.1):
        self.nu = nu

    def fit(self, X, y=None):
        self.ocsvm_ = OneClassSVM(nu=self.nu, kernel="rbf")
        self.ocsvm_.fit(X)
        return self

    def transform(self, X):
        score = self.ocsvm_.decision_function(X).reshape(-1, 1)
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
    # Pipeline(FactorAnalysis + LogisticRegression) (1-10)
    1: ("FactorAnalysis_Log_A", F_A, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("FactorAnalysis_Log_B_c1", F_B, lambda: Pipeline([("fa", FactorAnalysis(n_components=1, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    3: ("FactorAnalysis_Log_C", F_C, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    4: ("FactorAnalysis_Log_D", F_D, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("FactorAnalysis_Log_E_c1", F_E, lambda: Pipeline([("fa", FactorAnalysis(n_components=1, random_state=SEED)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    6: ("FactorAnalysis_Log_F", F_F, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    7: ("FactorAnalysis_Log_G", F_G, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    8: ("FactorAnalysis_Log_H", F_H, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    9: ("FactorAnalysis_Log_I", F_I, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    10: ("FactorAnalysis_Log_wide_K_c3", F_K, lambda: Pipeline([("fa", FactorAnalysis(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(OCSVMAugment + LogisticRegression) (11-20)
    11: ("OCSVMAugment_Log_A", F_A, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.1)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    12: ("OCSVMAugment_Log_B_nu02", F_B, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    13: ("OCSVMAugment_Log_C", F_C, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.1)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    14: ("OCSVMAugment_Log_D", F_D, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.1)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    15: ("OCSVMAugment_Log_E_nu005", F_E, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.05)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    16: ("OCSVMAugment_Log_F", F_F, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.1)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    17: ("OCSVMAugment_Log_G", F_G, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.1)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    18: ("OCSVMAugment_Log_H", F_H, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.1)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    19: ("OCSVMAugment_Log_I_nu02", F_I, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    20: ("OCSVMAugment_Log_wide_K", F_K, lambda: Pipeline([("ocs", OCSVMAugment(nu=0.1)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(SplineTransformer + KNeighborsClassifier) (21-30)
    21: ("Spline_KNN_A", F_A, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    22: ("Spline_KNN_B_k15", F_B, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    23: ("Spline_KNN_C", F_C, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    24: ("Spline_KNN_D", F_D, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    25: ("Spline_KNN_E", F_E, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))])),
    26: ("Spline_KNN_F_deg2", F_F, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    27: ("Spline_KNN_G", F_G, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    28: ("Spline_KNN_H", F_H, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    29: ("Spline_KNN_I_k20", F_I, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    30: ("Spline_KNN_wide_K", F_K, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=2)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),

    # CalibratedClassifierCV(SGDClassifier(loss="perceptron")) (31-40)
    31: ("CalibSGD_perceptron_A", F_A, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-4, random_state=SEED), cv=3)),
    32: ("CalibSGD_perceptron_B", F_B, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-3, random_state=SEED), cv=3)),
    33: ("CalibSGD_perceptron_C", F_C, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-4, random_state=SEED), cv=3)),
    34: ("CalibSGD_perceptron_D_cv5", F_D, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-4, random_state=SEED), cv=5)),
    35: ("CalibSGD_perceptron_E", F_E, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-5, random_state=SEED), cv=3)),
    36: ("CalibSGD_perceptron_F_elastic", F_F, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-4, penalty="elasticnet", random_state=SEED), cv=3)),
    37: ("CalibSGD_perceptron_G", F_G, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-4, random_state=SEED), cv=3)),
    38: ("CalibSGD_perceptron_H", F_H, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-3, random_state=SEED), cv=3)),
    39: ("CalibSGD_perceptron_I_cv5", F_I, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-4, random_state=SEED), cv=5)),
    40: ("CalibSGD_perceptron_wide_K", F_K, lambda: CalibratedClassifierCV(SGDClassifier(loss="perceptron", alpha=1e-4, random_state=SEED), cv=3)),

    # StackingClassifier(final_estimator=KNeighborsClassifier) (41-50)
    41: ("StackKNN_A", F_A, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), cv=3, n_jobs=1)),
    42: ("StackKNN_B", F_B, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=15, n_jobs=1), cv=3, n_jobs=1)),
    43: ("StackKNN_3base_C", F_C, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("rf", KNeighborsClassifier(n_neighbors=10, n_jobs=1))], final_estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), cv=3, n_jobs=1)),
    44: ("StackKNN_D", F_D, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), cv=3, n_jobs=1)),
    45: ("StackKNN_E", F_E, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=5, n_jobs=1), cv=3, n_jobs=1)),
    46: ("StackKNN_F", F_F, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), cv=3, n_jobs=1)),
    47: ("StackKNN_G_cv5", F_G, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), cv=5, n_jobs=1)),
    48: ("StackKNN_H", F_H, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=15, n_jobs=1), cv=3, n_jobs=1)),
    49: ("StackKNN_I", F_I, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), cv=3, n_jobs=1)),
    50: ("StackKNN_wide_K", F_K, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=KNeighborsClassifier(n_neighbors=15, n_jobs=1), cv=3, n_jobs=1)),
}
