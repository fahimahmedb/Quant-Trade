"""
Itération 20 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 19 (LOF-augmented, SelectFromModel(RF), KBinsDiscretizer
onehot, Bagging(ExtraTree bootstrap), PowerTransformer+LogReg), itération 20
explore :

1. Pipeline(SplineTransformer + LogisticRegression) — expansion en base de
   splines (B-splines cubiques), transformation non linéaire jamais
   utilisée (distincte de PolynomialFeatures, itérations 7/11 : les splines
   capturent des relations non linéaires locales et lisses plutôt que des
   interactions polynomiales globales).
2. BaggingClassifier(GMMBayesClassifier, n_estimators=5) — mise en bagging
   du classifieur génératif maison introduit en itération 18 (GMMBayes),
   pour tester si moyenner plusieurs GMM sur des rééchantillonnages
   bootstrap stabilise ses prédictions. Bucket réduit à 5 estimateurs/6
   variantes (coût ~2s/fit à n=9000, cumul de deux méthodes génératives).
3. Pipeline(Nystroem(kernel="cosine") + SGDClassifier(log_loss)) — noyau
   cosinus jamais utilisé pour l'approximation de noyau (rbf et poly
   testés en itération 12).
4. Pipeline(RobustScaler + CalibratedClassifierCV(RidgeClassifierCV)) —
   RidgeClassifierCV à sélection automatique d'alpha (itération 14) combiné
   pour la première fois à une mise à l'échelle résistante aux outliers
   (motivé par les queues épaisses ν≈4,8 établies en Étape A).
5. Pipeline(SplineTransformer + CalibratedClassifierCV(RidgeClassifierCV)) —
   association classique splines + régression ridge (lissage régularisé),
   distincte de Spline+LogReg (1) par le modèle en aval.

Vitesse vérifiée sur n=9000 : toutes les familles <2.2s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.preprocessing import SplineTransformer, RobustScaler
from sklearn.linear_model import LogisticRegression, RidgeClassifierCV, SGDClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.kernel_approximation import Nystroem
from sklearn.pipeline import Pipeline

from .iter18 import GMMBayesClassifier

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
    # Pipeline(SplineTransformer + LogisticRegression) (1-12)
    1: ("Spline_Log_A", F_A, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("Spline_Log_B_k4", F_B, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    3: ("Spline_Log_C", F_C, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    4: ("Spline_Log_D_deg2", F_D, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("Spline_Log_E", F_E, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    6: ("Spline_Log_F_k6", F_F, lambda: Pipeline([("spl", SplineTransformer(n_knots=6, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    7: ("Spline_Log_G", F_G, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    8: ("Spline_Log_H_deg2", F_H, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    9: ("Spline_Log_I", F_I, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    10: ("Spline_Log_J_k4", F_J, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    11: ("Spline_Log_wide_K", F_K, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    12: ("Spline_Log_wide_K_k4", F_K, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # BaggingClassifier(GMMBayesClassifier) (13-18)
    13: ("Bagging_GMMBayes_A", F_A, lambda: BaggingClassifier(estimator=GMMBayesClassifier(n_components=2), n_estimators=5, random_state=SEED)),
    14: ("Bagging_GMMBayes_C", F_C, lambda: BaggingClassifier(estimator=GMMBayesClassifier(n_components=2), n_estimators=5, random_state=SEED)),
    15: ("Bagging_GMMBayes_E", F_E, lambda: BaggingClassifier(estimator=GMMBayesClassifier(n_components=2), n_estimators=5, random_state=SEED)),
    16: ("Bagging_GMMBayes_G", F_G, lambda: BaggingClassifier(estimator=GMMBayesClassifier(n_components=1), n_estimators=5, random_state=SEED)),
    17: ("Bagging_GMMBayes_I", F_I, lambda: BaggingClassifier(estimator=GMMBayesClassifier(n_components=2), n_estimators=5, random_state=SEED)),
    18: ("Bagging_GMMBayes_wide_K", F_K, lambda: BaggingClassifier(estimator=GMMBayesClassifier(n_components=2), n_estimators=5, random_state=SEED)),

    # Pipeline(Nystroem(cosine) + SGDClassifier(log_loss)) (19-30)
    19: ("Nystroem_cosine_SGD_A", F_A, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    20: ("Nystroem_cosine_SGD_B_n30", F_B, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=30, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    21: ("Nystroem_cosine_SGD_C", F_C, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-3, random_state=SEED))])),
    22: ("Nystroem_cosine_SGD_D_n80", F_D, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=80, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    23: ("Nystroem_cosine_SGD_E", F_E, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-5, random_state=SEED))])),
    24: ("Nystroem_cosine_SGD_F", F_F, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    25: ("Nystroem_cosine_SGD_G", F_G, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="modified_huber", alpha=1e-4, random_state=SEED))])),
    26: ("Nystroem_cosine_SGD_H", F_H, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=60, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    27: ("Nystroem_cosine_SGD_I", F_I, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, penalty="elasticnet", random_state=SEED))])),
    28: ("Nystroem_cosine_SGD_J_n30", F_J, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=30, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    29: ("Nystroem_cosine_SGD_wide_K", F_K, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=80, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    30: ("Nystroem_cosine_SGD_wide_K_n100", F_K, lambda: Pipeline([("ny", Nystroem(kernel="cosine", n_components=100, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),

    # Pipeline(RobustScaler + CalibratedClassifierCV(RidgeClassifierCV)) (31-40)
    31: ("RobustScaler_CalibRidgeCV_A", F_A, lambda: Pipeline([("rs", RobustScaler()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    32: ("RobustScaler_CalibRidgeCV_B", F_B, lambda: Pipeline([("rs", RobustScaler()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.01, 0.1, 1.0, 10.0)), cv=3))])),
    33: ("RobustScaler_CalibRidgeCV_C", F_C, lambda: Pipeline([("rs", RobustScaler()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    34: ("RobustScaler_CalibRidgeCV_D_quantrange", F_D, lambda: Pipeline([("rs", RobustScaler(quantile_range=(10.0, 90.0))), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    35: ("RobustScaler_CalibRidgeCV_E", F_E, lambda: Pipeline([("rs", RobustScaler()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=5))])),
    36: ("RobustScaler_CalibRidgeCV_F", F_F, lambda: Pipeline([("rs", RobustScaler()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    37: ("RobustScaler_CalibRidgeCV_G", F_G, lambda: Pipeline([("rs", RobustScaler()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.01, 0.1, 1.0, 10.0, 100.0)), cv=3))])),
    38: ("RobustScaler_CalibRidgeCV_H", F_H, lambda: Pipeline([("rs", RobustScaler()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    39: ("RobustScaler_CalibRidgeCV_I_quantrange", F_I, lambda: Pipeline([("rs", RobustScaler(quantile_range=(15.0, 85.0))), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    40: ("RobustScaler_CalibRidgeCV_wide_K", F_K, lambda: Pipeline([("rs", RobustScaler()), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),

    # Pipeline(SplineTransformer + CalibratedClassifierCV(RidgeClassifierCV)) (41-50)
    41: ("Spline_CalibRidgeCV_A", F_A, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    42: ("Spline_CalibRidgeCV_B_k4", F_B, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    43: ("Spline_CalibRidgeCV_C", F_C, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.01, 0.1, 1.0, 10.0)), cv=3))])),
    44: ("Spline_CalibRidgeCV_D_deg2", F_D, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    45: ("Spline_CalibRidgeCV_E", F_E, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=5))])),
    46: ("Spline_CalibRidgeCV_F_k6", F_F, lambda: Pipeline([("spl", SplineTransformer(n_knots=6, degree=3)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    47: ("Spline_CalibRidgeCV_G", F_G, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    48: ("Spline_CalibRidgeCV_H_deg2", F_H, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
    49: ("Spline_CalibRidgeCV_I", F_I, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.01, 0.1, 1.0, 10.0)), cv=3))])),
    50: ("Spline_CalibRidgeCV_wide_K", F_K, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=2)), ("ridge", CalibratedClassifierCV(RidgeClassifierCV(alphas=(0.1, 1.0, 10.0)), cv=3))])),
}
