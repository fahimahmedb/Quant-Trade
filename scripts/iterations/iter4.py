"""
Itération 4 — 50 nouvelles hypothèses (univers figé a priori).

Familles de modèles jamais testées aux itérations 1-3 (RF/HistGB/LogReg/SVM
uniquement) : ExtraTrees, AdaBoost, Bagging, GaussianNB, LDA, QDA, KNN,
MLPClassifier (vrai réseau de neurones — l'"NN_deep_5" de l'itération 3
était en fait un HistGradientBoosting mal nommé), SGDClassifier (logistique
en ligne). Features jamais utilisées aux itérations précédentes incluses
pour diversité réelle : mom_20, ma_ratio_50, vol_10, drawdown_60, stoch_k,
fracdiff_04.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01) — seule la famille de modèles/
features varie, comme l'exige la discipline anti-data-snooping (extension
déclarée et comptée, cf. CLAUDE.md).
"""
from sklearn.ensemble import ExtraTreesClassifier, AdaBoostClassifier, BaggingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier

SEED = 42

F_A = ["mom_10", "vol_20", "rsi_14"]
F_B = ["mom_10", "vol_ratio", "atr_rel", "mom_20"]
F_C = ["mom_20", "ma_ratio_50", "vol_10", "stoch_k"]
F_D = ["drawdown_60", "vol_20", "rsi_14", "fracdiff_04"]
F_E = ["fracdiff_04", "mom_10", "vol_10"]
F_F = ["stoch_k", "macd_rel", "bb_pctb", "ma_ratio_50"]
F_G = ["mom_10", "mom_20", "vol_20", "atr_rel", "stoch_k"]
F_H = ["ret_1", "ret_2", "ret_3", "drawdown_60", "vol_10"]

STRATEGIES = {
    # ExtraTreesClassifier (1-6)
    1: ("ExtraTrees_d3_n100", F_A, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1)),
    2: ("ExtraTrees_d5_n150", F_A, lambda: ExtraTreesClassifier(n_estimators=150, max_depth=5, random_state=SEED, n_jobs=1)),
    3: ("ExtraTrees_d7_n100", F_B, lambda: ExtraTreesClassifier(n_estimators=100, max_depth=7, random_state=SEED, n_jobs=1)),
    4: ("ExtraTrees_d4_n200", F_C, lambda: ExtraTreesClassifier(n_estimators=200, max_depth=4, random_state=SEED, n_jobs=1)),
    5: ("ExtraTrees_d6_n120_msl20", F_D, lambda: ExtraTreesClassifier(n_estimators=120, max_depth=6, min_samples_leaf=20, random_state=SEED, n_jobs=1)),
    6: ("ExtraTrees_d3_n250_msl50", F_G, lambda: ExtraTreesClassifier(n_estimators=250, max_depth=3, min_samples_leaf=50, random_state=SEED, n_jobs=1)),

    # AdaBoostClassifier (7-11), weak learner = stump/shallow tree
    7: ("AdaBoost_d1_n50", F_A, lambda: AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1, random_state=SEED), n_estimators=50, learning_rate=1.0, random_state=SEED)),
    8: ("AdaBoost_d1_n150_lr05", F_B, lambda: AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1, random_state=SEED), n_estimators=150, learning_rate=0.5, random_state=SEED)),
    9: ("AdaBoost_d2_n100", F_D, lambda: AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=2, random_state=SEED), n_estimators=100, learning_rate=0.3, random_state=SEED)),
    10: ("AdaBoost_d3_n80_lr02", F_G, lambda: AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=3, random_state=SEED), n_estimators=80, learning_rate=0.2, random_state=SEED)),
    11: ("AdaBoost_d1_n200_lr01", F_C, lambda: AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1, random_state=SEED), n_estimators=200, learning_rate=0.1, random_state=SEED)),

    # BaggingClassifier (12-17)
    12: ("Bagging_n50_d3", F_A, lambda: BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=3, random_state=SEED), n_estimators=50, random_state=SEED, n_jobs=1)),
    13: ("Bagging_n100_d5_ms08", F_B, lambda: BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=5, random_state=SEED), n_estimators=100, max_samples=0.8, random_state=SEED, n_jobs=1)),
    14: ("Bagging_n80_d4_mf05", F_D, lambda: BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=4, random_state=SEED), n_estimators=80, max_features=0.5, random_state=SEED, n_jobs=1)),
    15: ("Bagging_n150_d2", F_E, lambda: BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=2, random_state=SEED), n_estimators=150, random_state=SEED, n_jobs=1)),
    16: ("Bagging_n60_d6_ms06", F_G, lambda: BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=6, random_state=SEED), n_estimators=60, max_samples=0.6, random_state=SEED, n_jobs=1)),
    17: ("Bagging_n120_d3_mf07", F_H, lambda: BaggingClassifier(estimator=DecisionTreeClassifier(max_depth=3, random_state=SEED), n_estimators=120, max_features=0.7, random_state=SEED, n_jobs=1)),

    # GaussianNB (18-21) — pas d'hyperparametres, on varie les features
    18: ("GaussianNB_A", F_A, lambda: GaussianNB()),
    19: ("GaussianNB_C", F_C, lambda: GaussianNB()),
    20: ("GaussianNB_D", F_D, lambda: GaussianNB()),
    21: ("GaussianNB_H", F_H, lambda: GaussianNB()),

    # LinearDiscriminantAnalysis (22-25)
    22: ("LDA_svd", F_A, lambda: LinearDiscriminantAnalysis(solver="svd")),
    23: ("LDA_lsqr_shrink_auto", F_B, lambda: LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
    24: ("LDA_eigen_shrink05", F_G, lambda: LinearDiscriminantAnalysis(solver="eigen", shrinkage=0.5)),
    25: ("LDA_lsqr_shrink02", F_E, lambda: LinearDiscriminantAnalysis(solver="lsqr", shrinkage=0.2)),

    # QuadraticDiscriminantAnalysis (26-29)
    26: ("QDA_reg00", F_A, lambda: QuadraticDiscriminantAnalysis(reg_param=0.0)),
    27: ("QDA_reg01", F_C, lambda: QuadraticDiscriminantAnalysis(reg_param=0.1)),
    28: ("QDA_reg03", F_D, lambda: QuadraticDiscriminantAnalysis(reg_param=0.3)),
    29: ("QDA_reg05", F_F, lambda: QuadraticDiscriminantAnalysis(reg_param=0.5)),

    # KNeighborsClassifier (30-35)
    30: ("KNN_k5", F_A, lambda: KNeighborsClassifier(n_neighbors=5, n_jobs=1)),
    31: ("KNN_k10", F_A, lambda: KNeighborsClassifier(n_neighbors=10, n_jobs=1)),
    32: ("KNN_k15", F_B, lambda: KNeighborsClassifier(n_neighbors=15, n_jobs=1)),
    33: ("KNN_k20", F_C, lambda: KNeighborsClassifier(n_neighbors=20, n_jobs=1)),
    34: ("KNN_k30", F_G, lambda: KNeighborsClassifier(n_neighbors=30, n_jobs=1)),
    35: ("KNN_k50_dist", F_H, lambda: KNeighborsClassifier(n_neighbors=50, weights="distance", n_jobs=1)),

    # MLPClassifier — vrai reseau de neurones (36-43)
    36: ("MLP_8", F_A, lambda: MLPClassifier(hidden_layer_sizes=(8,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    37: ("MLP_16", F_A, lambda: MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    38: ("MLP_8_8", F_B, lambda: MLPClassifier(hidden_layer_sizes=(8, 8), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    39: ("MLP_16_8", F_D, lambda: MLPClassifier(hidden_layer_sizes=(16, 8), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    40: ("MLP_32", F_G, lambda: MLPClassifier(hidden_layer_sizes=(32,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)),
    41: ("MLP_16_16", F_C, lambda: MLPClassifier(hidden_layer_sizes=(16, 16), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),
    42: ("MLP_8_4_highreg", F_E, lambda: MLPClassifier(hidden_layer_sizes=(8, 4), alpha=1e-1, max_iter=300, early_stopping=True, random_state=SEED)),
    43: ("MLP_32_16", F_H, lambda: MLPClassifier(hidden_layer_sizes=(32, 16), alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)),

    # SGDClassifier loss='log_loss' — logistique via descente stochastique (44-50)
    44: ("SGD_log_a0001", F_A, lambda: SGDClassifier(loss="log_loss", alpha=1e-4, max_iter=1000, random_state=SEED)),
    45: ("SGD_log_a001", F_A, lambda: SGDClassifier(loss="log_loss", alpha=1e-3, max_iter=1000, random_state=SEED)),
    46: ("SGD_log_a01_l1", F_B, lambda: SGDClassifier(loss="log_loss", alpha=1e-2, penalty="l1", max_iter=1000, random_state=SEED)),
    47: ("SGD_log_elastic", F_D, lambda: SGDClassifier(loss="log_loss", alpha=1e-3, penalty="elasticnet", l1_ratio=0.3, max_iter=1000, random_state=SEED)),
    48: ("SGD_modhuber_a0001", F_G, lambda: SGDClassifier(loss="modified_huber", alpha=1e-4, max_iter=1000, random_state=SEED)),
    49: ("SGD_log_a1_l1", F_F, lambda: SGDClassifier(loss="log_loss", alpha=1.0, penalty="l1", max_iter=1000, random_state=SEED)),
    50: ("SGD_modhuber_elastic", F_H, lambda: SGDClassifier(loss="modified_huber", alpha=1e-2, penalty="elasticnet", l1_ratio=0.5, max_iter=1000, random_state=SEED)),
}
