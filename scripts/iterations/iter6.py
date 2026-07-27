"""
Itération 6 — 50 nouvelles hypothèses (univers figé a priori).

Itérations 3-5 ont couvert la quasi-totalité des familles de classifieurs
scikit-learn usuelles (RF, ExtraTrees, Bagging, AdaBoost, GBM classique,
HistGBM, LogReg, SGD, SVM (rbf/poly/lineaire/calibre), PassiveAggressive
calibre, KNN, GaussianNB, LDA, QDA, MLP, Voting, Stacking) — toutes avec des
petits jeux de 3-5 features. Itération 6 explore ce qui reste :

1. DecisionTreeClassifier SEUL (jamais teste isolement, seulement comme
   estimateur de base dans Ada/Bagging/Voting/Stacking).
2. AdaBoost avec des estimateurs de base plus riches qu'un stump
   (RandomForest, ExtraTrees, LogisticRegression au lieu d'un arbre peu
   profond) — meme meta-algorithme, base radicalement differente.
3. Bagging de boosting (GradientBoosting/HistGB en base d'un Bagging) —
   combinaison meta jamais essayee.
4. BernoulliNB avec binarisation des features (modele evenementiel
   presence/absence de signal positif) — different de GaussianNB deja teste.
5. Jeux de features LARGES (8-9 colonnes au lieu de 3-5) sur des modeles
   deja connus (LogReg, RF) — hypothese distincte : est-ce que plus de
   features aide ou juste sur-ajuste.
6. CalibratedClassifierCV sur DecisionTreeClassifier seul.

Protocole inchange (T0=750, refit=21j, embargo=21j, H=5j, barriere 1.5*sigma,
couts 5bps, split design/test 2010-01-01).
"""
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.ensemble import BaggingClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.calibration import CalibratedClassifierCV

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
F_K = ["mom_10", "mom_20", "vol_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "atr_rel", "stoch_k"]  # large
F_L = ["ret_1", "ret_2", "ret_3", "ret_5", "drawdown_60", "fracdiff_04", "ma_ratio_20", "ma_ratio_50"]  # large

STRATEGIES = {
    # DecisionTreeClassifier seul, jamais teste isolement (1-8)
    1: ("DT_d3_gini", F_A, lambda: DecisionTreeClassifier(max_depth=3, criterion="gini", random_state=SEED)),
    2: ("DT_d5_entropy", F_A, lambda: DecisionTreeClassifier(max_depth=5, criterion="entropy", random_state=SEED)),
    3: ("DT_d4_msl30", F_B, lambda: DecisionTreeClassifier(max_depth=4, min_samples_leaf=30, random_state=SEED)),
    4: ("DT_d2_random_split", F_C, lambda: DecisionTreeClassifier(max_depth=2, splitter="random", random_state=SEED)),
    5: ("DT_d6_msl50", F_D, lambda: DecisionTreeClassifier(max_depth=6, min_samples_leaf=50, random_state=SEED)),
    6: ("DT_d3_entropy_msl20", F_G, lambda: DecisionTreeClassifier(max_depth=3, criterion="entropy", min_samples_leaf=20, random_state=SEED)),
    7: ("DT_d8", F_K, lambda: DecisionTreeClassifier(max_depth=8, min_samples_leaf=40, random_state=SEED)),
    8: ("DT_d4_msl15", F_H, lambda: DecisionTreeClassifier(max_depth=4, min_samples_leaf=15, random_state=SEED)),

    # AdaBoost avec base riche (pas juste un stump) (9-18)
    9: ("AdaBoost_baseRF_A", F_A, lambda: AdaBoostClassifier(estimator=RandomForestClassifier(n_estimators=15, max_depth=3, random_state=SEED, n_jobs=1), n_estimators=25, learning_rate=0.5, random_state=SEED)),
    10: ("AdaBoost_baseRF_B", F_B, lambda: AdaBoostClassifier(estimator=RandomForestClassifier(n_estimators=20, max_depth=2, random_state=SEED, n_jobs=1), n_estimators=20, learning_rate=0.3, random_state=SEED)),
    11: ("AdaBoost_baseET_C", F_C, lambda: AdaBoostClassifier(estimator=ExtraTreesClassifier(n_estimators=15, max_depth=3, random_state=SEED, n_jobs=1), n_estimators=25, learning_rate=0.5, random_state=SEED)),
    12: ("AdaBoost_baseET_D", F_D, lambda: AdaBoostClassifier(estimator=ExtraTreesClassifier(n_estimators=20, max_depth=2, random_state=SEED, n_jobs=1), n_estimators=20, learning_rate=1.0, random_state=SEED)),
    13: ("AdaBoost_baseLog_E", F_E, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=30, learning_rate=0.5, random_state=SEED)),
    14: ("AdaBoost_baseLog_F", F_F, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=0.5, max_iter=500, random_state=SEED), n_estimators=40, learning_rate=0.3, random_state=SEED)),
    15: ("AdaBoost_baseRF_G", F_G, lambda: AdaBoostClassifier(estimator=RandomForestClassifier(n_estimators=10, max_depth=4, random_state=SEED, n_jobs=1), n_estimators=30, learning_rate=0.2, random_state=SEED)),
    16: ("AdaBoost_baseET_H", F_H, lambda: AdaBoostClassifier(estimator=ExtraTreesClassifier(n_estimators=10, max_depth=4, random_state=SEED, n_jobs=1), n_estimators=30, learning_rate=0.2, random_state=SEED)),
    17: ("AdaBoost_baseLog_I", F_I, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=2.0, max_iter=500, random_state=SEED), n_estimators=25, learning_rate=1.0, random_state=SEED)),
    18: ("AdaBoost_baseRF_J", F_J, lambda: AdaBoostClassifier(estimator=RandomForestClassifier(n_estimators=15, max_depth=2, random_state=SEED, n_jobs=1), n_estimators=20, learning_rate=0.5, random_state=SEED)),

    # Bagging de boosting (meta jamais essaye) (19-26)
    19: ("Bagging_GBM_A", F_A, lambda: BaggingClassifier(estimator=GradientBoostingClassifier(n_estimators=20, max_depth=2, random_state=SEED), n_estimators=8, random_state=SEED, n_jobs=1)),
    20: ("Bagging_GBM_B", F_B, lambda: BaggingClassifier(estimator=GradientBoostingClassifier(n_estimators=25, max_depth=2, learning_rate=0.1, random_state=SEED), n_estimators=8, max_samples=0.8, random_state=SEED, n_jobs=1)),
    21: ("Bagging_HistGB_C", F_C, lambda: BaggingClassifier(estimator=HistGradientBoostingClassifier(max_iter=30, max_depth=3, random_state=SEED), n_estimators=8, random_state=SEED, n_jobs=1)),
    22: ("Bagging_HistGB_D", F_D, lambda: BaggingClassifier(estimator=HistGradientBoostingClassifier(max_iter=40, max_depth=2, learning_rate=0.1, random_state=SEED), n_estimators=6, max_samples=0.7, random_state=SEED, n_jobs=1)),
    23: ("Bagging_GBM_E", F_E, lambda: BaggingClassifier(estimator=GradientBoostingClassifier(n_estimators=20, max_depth=3, random_state=SEED), n_estimators=6, random_state=SEED, n_jobs=1)),
    24: ("Bagging_GBM_F_mf07", F_F, lambda: BaggingClassifier(estimator=GradientBoostingClassifier(n_estimators=20, max_depth=2, random_state=SEED), n_estimators=8, max_features=0.7, random_state=SEED, n_jobs=1)),
    25: ("Bagging_HistGB_G", F_G, lambda: BaggingClassifier(estimator=HistGradientBoostingClassifier(max_iter=30, max_depth=2, random_state=SEED), n_estimators=8, random_state=SEED, n_jobs=1)),
    26: ("Bagging_GBM_H", F_H, lambda: BaggingClassifier(estimator=GradientBoostingClassifier(n_estimators=15, max_depth=3, learning_rate=0.15, random_state=SEED), n_estimators=6, random_state=SEED, n_jobs=1)),

    # BernoulliNB - modele evenementiel (presence/absence de signal positif) (27-34)
    27: ("BernoulliNB_bin0_A", F_A, lambda: BernoulliNB(binarize=0.0)),
    28: ("BernoulliNB_bin0_B", F_B, lambda: BernoulliNB(binarize=0.0)),
    29: ("BernoulliNB_bin0_C", F_C, lambda: BernoulliNB(binarize=0.0)),
    30: ("BernoulliNB_bin0_D", F_D, lambda: BernoulliNB(binarize=0.0)),
    31: ("BernoulliNB_bin0_G", F_G, lambda: BernoulliNB(binarize=0.0)),
    32: ("BernoulliNB_bin0_H", F_H, lambda: BernoulliNB(binarize=0.0)),
    33: ("BernoulliNB_bin0_K", F_K, lambda: BernoulliNB(binarize=0.0)),
    34: ("BernoulliNB_bin0_L", F_L, lambda: BernoulliNB(binarize=0.0)),

    # Jeux de features LARGES (8-9 colonnes) sur modeles deja connus (35-42)
    35: ("LogReg_wide_K_C1", F_K, lambda: LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
    36: ("LogReg_wide_K_C01", F_K, lambda: LogisticRegression(C=0.1, max_iter=1000, random_state=SEED)),
    37: ("LogReg_wide_L_C1", F_L, lambda: LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
    38: ("LogReg_wide_L_C10", F_L, lambda: LogisticRegression(C=10.0, max_iter=1000, random_state=SEED)),
    39: ("RF_wide_K_d4", F_K, lambda: RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1)),
    40: ("RF_wide_K_d6", F_K, lambda: RandomForestClassifier(n_estimators=150, max_depth=6, random_state=SEED, n_jobs=1)),
    41: ("RF_wide_L_d4", F_L, lambda: RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1)),
    42: ("RF_wide_L_d8", F_L, lambda: RandomForestClassifier(n_estimators=120, max_depth=8, random_state=SEED, n_jobs=1)),

    # CalibratedClassifierCV(DecisionTreeClassifier) seul (43-50)
    43: ("CalibDT_sigmoid_A", F_A, lambda: CalibratedClassifierCV(DecisionTreeClassifier(max_depth=3, random_state=SEED), cv=3, method="sigmoid")),
    44: ("CalibDT_isotonic_B", F_B, lambda: CalibratedClassifierCV(DecisionTreeClassifier(max_depth=4, random_state=SEED), cv=3, method="isotonic")),
    45: ("CalibDT_sigmoid_C", F_C, lambda: CalibratedClassifierCV(DecisionTreeClassifier(max_depth=5, min_samples_leaf=20, random_state=SEED), cv=3, method="sigmoid")),
    46: ("CalibDT_isotonic_D", F_D, lambda: CalibratedClassifierCV(DecisionTreeClassifier(max_depth=6, min_samples_leaf=30, random_state=SEED), cv=3, method="isotonic")),
    47: ("CalibDT_sigmoid_E", F_E, lambda: CalibratedClassifierCV(DecisionTreeClassifier(max_depth=2, random_state=SEED), cv=3, method="sigmoid")),
    48: ("CalibDT_isotonic_G", F_G, lambda: CalibratedClassifierCV(DecisionTreeClassifier(max_depth=4, criterion="entropy", random_state=SEED), cv=3, method="isotonic")),
    49: ("CalibDT_sigmoid_K", F_K, lambda: CalibratedClassifierCV(DecisionTreeClassifier(max_depth=5, random_state=SEED), cv=3, method="sigmoid")),
    50: ("CalibDT_isotonic_L", F_L, lambda: CalibratedClassifierCV(DecisionTreeClassifier(max_depth=3, min_samples_leaf=25, random_state=SEED), cv=3, method="isotonic")),
}
