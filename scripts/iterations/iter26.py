"""
Itération 26 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 25 (retour sur MLPClassifier : tanh/logistic/sgd
adaptatif, QuantileTransformer/Spline en amont), itération 26 explore :

1. BaggingClassifier(Pipeline(SplineTransformer+GaussianNB)) — version
   "bagged" du pipeline de l'itération 24 (bucket 5), même logique que les
   Bagging(Spline+LogReg) de l'itération 21 et Bagging(TruncSVD+KNN) de
   l'itération 24.
2. VotingClassifier(soft) : MLPClassifier(tanh) + LogisticRegression +
   RandomForest — MLPClassifier n'avait JAMAIS été inclus dans un comité de
   vote jusqu'ici (seul son usage autonome avait été testé, itérations 4 et
   25).
3. StackingClassifier avec MLPClassifier(tanh) comme modèle de BASE (aux
   côtés de GaussianNB), final_estimator=LogisticRegression — MLPClassifier
   n'avait jamais non plus été utilisé comme membre de base d'un stacking.
4-5. Pipeline(HistGradientBoostingClassifier / RandomForestClassifier) sur
   des combinaisons de features ENCORE JAMAIS assemblées ensemble dans une
   même stratégie (mais tirées du même jeu de 20 colonnes déjà établi par
   build_features() — aucune nouvelle feature n'existe à ce stade,
   confirmé par relecture de X.columns) — nouvelle hypothèse au sens où le
   pari (quelle combinaison de signaux) diffère, même si les deux familles
   de modèles sont déjà connues comme parmi les plus performantes du
   projet.

Vitesse vérifiée sur n=9000 : toutes les familles retenues <1.1s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.preprocessing import SplineTransformer
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import BaggingClassifier, VotingClassifier, StackingClassifier, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

SEED = 42

# Nouvelles combinaisons de features (jamais assemblees ensemble jusqu'ici)
F_L = ["mom_10", "atr_rel", "drawdown_60"]
F_M = ["vol_ratio", "bb_pctb", "ma_ratio_50"]
F_N = ["stoch_k", "fracdiff_04", "ret_1"]
F_O = ["macd_rel", "parkinson_5", "mom_20", "ret_2"]
F_P = ["rsi_14", "vol_10", "ma_ratio_20", "ret_3"]
F_Q = ["drawdown_60", "vol_20", "atr_rel", "stoch_k", "ret_5"]
F_R = ["ma_ratio_50", "bb_pctb", "macd_rel", "fracdiff_04"]
F_S = ["ret_10", "vol_ratio", "mom_10", "parkinson_5"]
F_T = ["mom_20", "rsi_14", "drawdown_60", "ma_ratio_20", "vol_ratio"]
F_U = ["atr_rel", "stoch_k", "bb_pctb", "ret_1", "ret_2", "ret_3"]

F_A = ["mom_10", "vol_10", "rsi_14"]
F_E = ["ret_1", "ret_2", "drawdown_60"]
F_K = ["mom_10", "mom_20", "vol_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "atr_rel", "stoch_k", "ma_ratio_20"]

STRATEGIES = {
    # BaggingClassifier(Pipeline(SplineTransformer+GaussianNB)) (1-10)
    1: ("Bagging_Spline_NB_A", F_A, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),
    2: ("Bagging_Spline_NB_L", F_L, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),
    3: ("Bagging_Spline_NB_E", F_E, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),
    4: ("Bagging_Spline_NB_M_n15", F_M, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())]), n_estimators=15, random_state=SEED)),
    5: ("Bagging_Spline_NB_N", F_N, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),
    6: ("Bagging_Spline_NB_O", F_O, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),
    7: ("Bagging_Spline_NB_P", F_P, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),
    8: ("Bagging_Spline_NB_Q", F_Q, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),
    9: ("Bagging_Spline_NB_R", F_R, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),
    10: ("Bagging_Spline_NB_wide_K", F_K, lambda: BaggingClassifier(estimator=Pipeline([("spl", SplineTransformer(n_knots=4, degree=2)), ("nb", GaussianNB())]), n_estimators=10, random_state=SEED)),

    # VotingClassifier(soft) : MLP(tanh) + LogReg + RandomForest (11-20)
    11: ("VotingMLP_Log_RF_A", F_A, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    12: ("VotingMLP_Log_RF_L", F_L, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(8,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    13: ("VotingMLP_Log_RF_E", F_E, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    14: ("VotingMLP_Log_RF_M_weighted", F_M, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", weights=[2, 1, 1], n_jobs=1)),
    15: ("VotingMLP_Log_RF_N", F_N, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    16: ("VotingMLP_Log_RF_O", F_O, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16, 8), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    17: ("VotingMLP_Log_RF_P", F_P, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    18: ("VotingMLP_Log_RF_Q", F_Q, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", weights=[1, 1, 2], n_jobs=1)),
    19: ("VotingMLP_Log_RF_R", F_R, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    20: ("VotingMLP_Log_RF_wide_K", F_K, lambda: VotingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(32, 16), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),

    # StackingClassifier avec MLP(tanh) comme base + GaussianNB, final=LogReg (21-30)
    21: ("StackMLPbase_A", F_A, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    22: ("StackMLPbase_L", F_L, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(8,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    23: ("StackMLPbase_E", F_E, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    24: ("StackMLPbase_M_cv5", F_M, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=5, n_jobs=1)),
    25: ("StackMLPbase_N", F_N, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    26: ("StackMLPbase_O_3base", F_O, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB()), ("rf", RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1))], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    27: ("StackMLPbase_P", F_P, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16, 8), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    28: ("StackMLPbase_Q", F_Q, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    29: ("StackMLPbase_R", F_R, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(16,), activation="tanh", alpha=1e-3, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    30: ("StackMLPbase_wide_K", F_K, lambda: StackingClassifier(estimators=[("mlp", MLPClassifier(hidden_layer_sizes=(32, 16), activation="tanh", alpha=1e-2, max_iter=300, early_stopping=True, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),

    # HistGradientBoostingClassifier sur nouvelles combinaisons de features (31-40)
    31: ("HistGB_newfeat_L", F_L, lambda: HistGradientBoostingClassifier(max_iter=60, max_depth=3, random_state=SEED)),
    32: ("HistGB_newfeat_M", F_M, lambda: HistGradientBoostingClassifier(max_iter=60, max_depth=3, random_state=SEED)),
    33: ("HistGB_newfeat_N", F_N, lambda: HistGradientBoostingClassifier(max_iter=60, max_depth=4, random_state=SEED)),
    34: ("HistGB_newfeat_O", F_O, lambda: HistGradientBoostingClassifier(max_iter=80, max_depth=3, random_state=SEED)),
    35: ("HistGB_newfeat_P", F_P, lambda: HistGradientBoostingClassifier(max_iter=60, max_depth=3, random_state=SEED)),
    36: ("HistGB_newfeat_Q", F_Q, lambda: HistGradientBoostingClassifier(max_iter=60, max_depth=4, random_state=SEED)),
    37: ("HistGB_newfeat_R", F_R, lambda: HistGradientBoostingClassifier(max_iter=80, max_depth=3, random_state=SEED)),
    38: ("HistGB_newfeat_S", F_S, lambda: HistGradientBoostingClassifier(max_iter=60, max_depth=3, random_state=SEED)),
    39: ("HistGB_newfeat_T", F_T, lambda: HistGradientBoostingClassifier(max_iter=60, max_depth=4, random_state=SEED)),
    40: ("HistGB_newfeat_U", F_U, lambda: HistGradientBoostingClassifier(max_iter=80, max_depth=3, random_state=SEED)),

    # RandomForestClassifier sur nouvelles combinaisons de features (41-50)
    41: ("RF_newfeat_L", F_L, lambda: RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1)),
    42: ("RF_newfeat_M", F_M, lambda: RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1)),
    43: ("RF_newfeat_N", F_N, lambda: RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1)),
    44: ("RF_newfeat_O", F_O, lambda: RandomForestClassifier(n_estimators=120, max_depth=4, random_state=SEED, n_jobs=1)),
    45: ("RF_newfeat_P", F_P, lambda: RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1)),
    46: ("RF_newfeat_Q", F_Q, lambda: RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1)),
    47: ("RF_newfeat_R", F_R, lambda: RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1)),
    48: ("RF_newfeat_S", F_S, lambda: RandomForestClassifier(n_estimators=120, max_depth=4, random_state=SEED, n_jobs=1)),
    49: ("RF_newfeat_T", F_T, lambda: RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1)),
    50: ("RF_newfeat_U", F_U, lambda: RandomForestClassifier(n_estimators=100, max_depth=5, random_state=SEED, n_jobs=1)),
}
