"""
Itération 25 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 24 (PolynomialFeatures degré 3, Bagging(TruncSVD+KNN),
Nystroem(sigmoid)+SGD, Voting(SVD+FA+RF), Spline+GaussianNB), itération 25
revient sur MLPClassifier (itération 4) avec des hyperparamètres jamais
balayés :

Note de protocole : `scripts/ml_brute_force.py` applique TOUJOURS
standardize=True (StandardScaler implicite calé sur la fenêtre
d'entraînement) avant d'appeler la factory, quelle que soit la stratégie —
donc MLPClassifier reçoit déjà des features centrées-réduites même sans
scaler explicite dans la définition. Un Pipeline avec un autre scaler
(QuantileTransformer, SplineTransformer...) s'applique EN PLUS de ce
standardize implicite, ce qui reste une transformation distincte.

1. MLPClassifier(activation="tanh") — toutes les itérations précédentes de
   MLP utilisaient l'activation par défaut ("relu"), jamais tanh (plage
   [-1,1], naturellement adaptée à des features déjà centrées-réduites).
2. MLPClassifier(activation="logistic") — activation sigmoïde ([0,1]),
   jamais testée non plus.
3. MLPClassifier(solver="sgd", learning_rate="adaptive", momentum=0.9) —
   solveur SGD avec momentum et taux d'apprentissage adaptatif, au lieu du
   solveur "adam" par défaut utilisé dans toutes les itérations précédentes.
4. Pipeline(QuantileTransformer(uniform) + MLPClassifier) — distribution
   d'entrée uniforme plutôt que gaussienne standardisée, jamais combinée à
   un réseau de neurones (MLP toujours utilisé nu jusqu'ici).
5. Pipeline(SplineTransformer + MLPClassifier) — base de splines jamais
   combinée à un réseau de neurones (LogReg/RidgeCV/HistGB/KNN/GaussianNB
   testés en itérations 20-24).

Vitesse vérifiée sur n=9000 : toutes les familles <0.7s/fit — pas de risque
de répéter les problèmes de convergence lente rencontrés avec
Bagging(MLP, solver=lbfgs) en itération 9 (ici MLP reste non embagué).

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import QuantileTransformer, SplineTransformer
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
    # MLPClassifier(activation="tanh") (1-12)
    1: ("MLP_tanh_8_A", F_A, lambda: MLPClassifier(hidden_layer_sizes=(8,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    2: ("MLP_tanh_16_B", F_B, lambda: MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    3: ("MLP_tanh_8_8_C", F_C, lambda: MLPClassifier(hidden_layer_sizes=(8, 8), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    4: ("MLP_tanh_16_8_D", F_D, lambda: MLPClassifier(hidden_layer_sizes=(16, 8), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    5: ("MLP_tanh_32_E", F_E, lambda: MLPClassifier(hidden_layer_sizes=(32,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    6: ("MLP_tanh_16_16_F", F_F, lambda: MLPClassifier(hidden_layer_sizes=(16, 16), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    7: ("MLP_tanh_8_G", F_G, lambda: MLPClassifier(hidden_layer_sizes=(8,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    8: ("MLP_tanh_16_H", F_H, lambda: MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    9: ("MLP_tanh_8_4_highreg_I", F_I, lambda: MLPClassifier(hidden_layer_sizes=(8, 4), activation="tanh", alpha=1e-1, max_iter=300, early_stopping=True, random_state=SEED)),
    10: ("MLP_tanh_32_J", F_J, lambda: MLPClassifier(hidden_layer_sizes=(32,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    11: ("MLP_tanh_wide_K_16", F_K, lambda: MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    12: ("MLP_tanh_wide_K_32_16", F_K, lambda: MLPClassifier(hidden_layer_sizes=(32, 16), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),

    # MLPClassifier(activation="logistic") (13-24)
    13: ("MLP_logistic_8_A", F_A, lambda: MLPClassifier(hidden_layer_sizes=(8,), activation="logistic", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    14: ("MLP_logistic_16_B", F_B, lambda: MLPClassifier(hidden_layer_sizes=(16,), activation="logistic", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    15: ("MLP_logistic_8_8_C", F_C, lambda: MLPClassifier(hidden_layer_sizes=(8, 8), activation="logistic", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    16: ("MLP_logistic_16_8_D", F_D, lambda: MLPClassifier(hidden_layer_sizes=(16, 8), activation="logistic", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    17: ("MLP_logistic_32_E", F_E, lambda: MLPClassifier(hidden_layer_sizes=(32,), activation="logistic", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    18: ("MLP_logistic_16_16_F", F_F, lambda: MLPClassifier(hidden_layer_sizes=(16, 16), activation="logistic", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    19: ("MLP_logistic_8_G", F_G, lambda: MLPClassifier(hidden_layer_sizes=(8,), activation="logistic", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    20: ("MLP_logistic_16_H", F_H, lambda: MLPClassifier(hidden_layer_sizes=(16,), activation="logistic", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    21: ("MLP_logistic_8_4_highreg_I", F_I, lambda: MLPClassifier(hidden_layer_sizes=(8, 4), activation="logistic", alpha=1e-1, max_iter=300, early_stopping=True, random_state=SEED)),
    22: ("MLP_logistic_32_J", F_J, lambda: MLPClassifier(hidden_layer_sizes=(32,), activation="logistic", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    23: ("MLP_logistic_wide_K_16", F_K, lambda: MLPClassifier(hidden_layer_sizes=(16,), activation="logistic", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    24: ("MLP_logistic_wide_K_32_16", F_K, lambda: MLPClassifier(hidden_layer_sizes=(32, 16), activation="logistic", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),

    # MLPClassifier(solver="sgd", learning_rate="adaptive", momentum=0.9) (25-34)
    25: ("MLP_sgd_adaptive_8_A", F_A, lambda: MLPClassifier(hidden_layer_sizes=(8,), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    26: ("MLP_sgd_adaptive_16_B", F_B, lambda: MLPClassifier(hidden_layer_sizes=(16,), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    27: ("MLP_sgd_adaptive_8_8_C", F_C, lambda: MLPClassifier(hidden_layer_sizes=(8, 8), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    28: ("MLP_sgd_adaptive_D", F_D, lambda: MLPClassifier(hidden_layer_sizes=(16,), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    29: ("MLP_sgd_adaptive_32_E", F_E, lambda: MLPClassifier(hidden_layer_sizes=(32,), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    30: ("MLP_sgd_adaptive_F", F_F, lambda: MLPClassifier(hidden_layer_sizes=(16,), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    31: ("MLP_sgd_adaptive_G_nesterov", F_G, lambda: MLPClassifier(hidden_layer_sizes=(16,), solver="sgd", learning_rate="adaptive", momentum=0.9, nesterovs_momentum=True, alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    32: ("MLP_sgd_adaptive_H", F_H, lambda: MLPClassifier(hidden_layer_sizes=(16,), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    33: ("MLP_sgd_adaptive_I", F_I, lambda: MLPClassifier(hidden_layer_sizes=(16, 8), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    34: ("MLP_sgd_adaptive_wide_K", F_K, lambda: MLPClassifier(hidden_layer_sizes=(16,), solver="sgd", learning_rate="adaptive", momentum=0.9, alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),

    # Pipeline(QuantileTransformer(uniform) + MLPClassifier) (35-42)
    35: ("QuantUniform_MLP_A", F_A, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("mlp", MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    36: ("QuantUniform_MLP_B", F_B, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("mlp", MLPClassifier(hidden_layer_sizes=(8,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    37: ("QuantUniform_MLP_C", F_C, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("mlp", MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    38: ("QuantUniform_MLP_D", F_D, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("mlp", MLPClassifier(hidden_layer_sizes=(16, 8), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED))])),
    39: ("QuantUniform_MLP_E", F_E, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("mlp", MLPClassifier(hidden_layer_sizes=(32,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    40: ("QuantUniform_MLP_F", F_F, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("mlp", MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    41: ("QuantUniform_MLP_I", F_I, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("mlp", MLPClassifier(hidden_layer_sizes=(16, 16), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED))])),
    42: ("QuantUniform_MLP_wide_K", F_K, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("mlp", MLPClassifier(hidden_layer_sizes=(32, 16), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED))])),

    # Pipeline(SplineTransformer + MLPClassifier) (43-50)
    43: ("Spline_MLP_A", F_A, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("mlp", MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    44: ("Spline_MLP_B_k4", F_B, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("mlp", MLPClassifier(hidden_layer_sizes=(8,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    45: ("Spline_MLP_C", F_C, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("mlp", MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED))])),
    46: ("Spline_MLP_D_deg2", F_D, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("mlp", MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    47: ("Spline_MLP_E", F_E, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("mlp", MLPClassifier(hidden_layer_sizes=(32,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED))])),
    48: ("Spline_MLP_G", F_G, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("mlp", MLPClassifier(hidden_layer_sizes=(16, 8), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED))])),
    49: ("Spline_MLP_I", F_I, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("mlp", MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED))])),
    50: ("Spline_MLP_wide_K", F_K, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=2)), ("mlp", MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED))])),
}
