"""
Itération 5 — 50 nouvelles hypothèses (univers figé a priori).

Itérations précédentes couvraient : RandomForest/HistGB/LogReg/SVM (iter3),
ExtraTrees/AdaBoost/Bagging/GaussianNB/LDA/QDA/KNN/MLP/SGD (iter4). Aucune
n'a testé le GradientBoostingClassifier classique de sklearn (implémentation
distincte de HistGradientBoosting — arbres peu profonds séquentiels sur les
résidus, pas d'histogrammes), ni les méta-ensembles combinant plusieurs
modèles primaires (Voting, Stacking), ni les modèles linéaires calibrés a
posteriori (CalibratedClassifierCV sur LinearSVC / PassiveAggressive — ces
deux n'exposent pas predict_proba nativement).

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01) — seule la famille de modèles varie.
"""
from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

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

STRATEGIES = {
    # GradientBoostingClassifier classique (1-10) — distinct de HistGB (iter3)
    1: ("GBM_d2_n100_lr01", F_A, lambda: GradientBoostingClassifier(n_estimators=100, max_depth=2, learning_rate=0.1, random_state=SEED)),
    2: ("GBM_d3_n150_lr005", F_A, lambda: GradientBoostingClassifier(n_estimators=150, max_depth=3, learning_rate=0.05, random_state=SEED)),
    3: ("GBM_d2_n200_lr002_sub08", F_B, lambda: GradientBoostingClassifier(n_estimators=200, max_depth=2, learning_rate=0.02, subsample=0.8, random_state=SEED)),
    4: ("GBM_d4_n80_lr01_msl30", F_C, lambda: GradientBoostingClassifier(n_estimators=80, max_depth=4, learning_rate=0.1, min_samples_leaf=30, random_state=SEED)),
    5: ("GBM_d3_n120_lr01_sub07", F_D, lambda: GradientBoostingClassifier(n_estimators=120, max_depth=3, learning_rate=0.1, subsample=0.7, random_state=SEED)),
    6: ("GBM_d2_n250_lr005_msl50", F_G, lambda: GradientBoostingClassifier(n_estimators=250, max_depth=2, learning_rate=0.05, min_samples_leaf=50, random_state=SEED)),
    7: ("GBM_d5_n60_lr02", F_E, lambda: GradientBoostingClassifier(n_estimators=60, max_depth=5, learning_rate=0.2, random_state=SEED)),
    8: ("GBM_d3_n100_lr01_sub05", F_H, lambda: GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, subsample=0.5, random_state=SEED)),
    9: ("GBM_d2_n180_lr008_msl20", F_I, lambda: GradientBoostingClassifier(n_estimators=180, max_depth=2, learning_rate=0.08, min_samples_leaf=20, random_state=SEED)),
    10: ("GBM_d4_n70_lr015", F_J, lambda: GradientBoostingClassifier(n_estimators=70, max_depth=4, learning_rate=0.15, random_state=SEED)),

    # VotingClassifier (soft) — meta-ensemble de 3 modeles primaires (11-20)
    11: ("Voting_Log_NB_Tree_A", F_A, lambda: VotingClassifier(estimators=[
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
            ("nb", GaussianNB()),
            ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)),
        ], voting="soft", n_jobs=1)),
    12: ("Voting_Log_NB_Tree_B", F_B, lambda: VotingClassifier(estimators=[
            ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)),
            ("nb", GaussianNB()),
            ("dt", DecisionTreeClassifier(max_depth=6, random_state=SEED)),
        ], voting="soft", n_jobs=1)),
    13: ("Voting_weighted_D", F_D, lambda: VotingClassifier(estimators=[
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
            ("nb", GaussianNB()),
            ("dt", DecisionTreeClassifier(max_depth=3, random_state=SEED)),
        ], voting="soft", weights=[2, 1, 1], n_jobs=1)),
    14: ("Voting_RF_Log_C", F_C, lambda: VotingClassifier(estimators=[
            ("rf", RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1)),
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
        ], voting="soft", n_jobs=1)),
    15: ("Voting_RF_NB_G", F_G, lambda: VotingClassifier(estimators=[
            ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1)),
            ("nb", GaussianNB()),
        ], voting="soft", n_jobs=1)),
    16: ("Voting_3way_E", F_E, lambda: VotingClassifier(estimators=[
            ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)),
            ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)),
            ("nb", GaussianNB()),
        ], voting="soft", weights=[1, 2, 1], n_jobs=1)),
    17: ("Voting_3way_H", F_H, lambda: VotingClassifier(estimators=[
            ("lr", LogisticRegression(C=0.2, max_iter=1000, random_state=SEED)),
            ("dt", DecisionTreeClassifier(max_depth=5, random_state=SEED)),
            ("nb", GaussianNB()),
        ], voting="soft", n_jobs=1)),
    18: ("Voting_3way_I", F_I, lambda: VotingClassifier(estimators=[
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
            ("rf", RandomForestClassifier(n_estimators=100, max_depth=5, random_state=SEED, n_jobs=1)),
            ("dt", DecisionTreeClassifier(max_depth=2, random_state=SEED)),
        ], voting="soft", n_jobs=1)),
    19: ("Voting_3way_J", F_J, lambda: VotingClassifier(estimators=[
            ("lr", LogisticRegression(C=5.0, max_iter=1000, random_state=SEED)),
            ("nb", GaussianNB()),
            ("rf", RandomForestClassifier(n_estimators=50, max_depth=6, random_state=SEED, n_jobs=1)),
        ], voting="soft", weights=[1, 1, 2], n_jobs=1)),
    20: ("Voting_3way_F", F_F, lambda: VotingClassifier(estimators=[
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
            ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)),
            ("nb", GaussianNB()),
        ], voting="soft", n_jobs=1)),

    # CalibratedClassifierCV(LinearSVC) — SVM lineaire calibre, pas predict_proba natif (21-32)
    21: ("CalibLinearSVC_C01", F_A, lambda: CalibratedClassifierCV(LinearSVC(C=0.1, max_iter=5000, random_state=SEED), cv=3, method="sigmoid")),
    22: ("CalibLinearSVC_C1", F_A, lambda: CalibratedClassifierCV(LinearSVC(C=1.0, max_iter=5000, random_state=SEED), cv=3, method="sigmoid")),
    23: ("CalibLinearSVC_C10_iso", F_B, lambda: CalibratedClassifierCV(LinearSVC(C=10.0, max_iter=5000, random_state=SEED), cv=3, method="isotonic")),
    24: ("CalibLinearSVC_C005", F_C, lambda: CalibratedClassifierCV(LinearSVC(C=0.05, max_iter=5000, random_state=SEED), cv=3, method="sigmoid")),
    25: ("CalibLinearSVC_hinge_D", F_D, lambda: CalibratedClassifierCV(LinearSVC(C=1.0, loss="hinge", max_iter=5000, random_state=SEED), cv=3, method="sigmoid")),
    26: ("CalibLinearSVC_l1_E", F_E, lambda: CalibratedClassifierCV(LinearSVC(C=0.5, penalty="l1", dual=False, max_iter=5000, random_state=SEED), cv=3, method="sigmoid")),
    27: ("CalibLinearSVC_C50_F", F_F, lambda: CalibratedClassifierCV(LinearSVC(C=50.0, max_iter=5000, random_state=SEED), cv=3, method="isotonic")),
    28: ("CalibLinearSVC_C02_G", F_G, lambda: CalibratedClassifierCV(LinearSVC(C=0.2, max_iter=5000, random_state=SEED), cv=3, method="sigmoid")),
    29: ("CalibLinearSVC_C2_H", F_H, lambda: CalibratedClassifierCV(LinearSVC(C=2.0, max_iter=5000, random_state=SEED), cv=3, method="sigmoid")),
    30: ("CalibLinearSVC_C1_iso_I", F_I, lambda: CalibratedClassifierCV(LinearSVC(C=1.0, max_iter=5000, random_state=SEED), cv=3, method="isotonic")),
    31: ("CalibLinearSVC_C01_J", F_J, lambda: CalibratedClassifierCV(LinearSVC(C=0.1, max_iter=5000, random_state=SEED), cv=3, method="sigmoid")),
    32: ("CalibLinearSVC_C100_A", F_A, lambda: CalibratedClassifierCV(LinearSVC(C=100.0, max_iter=5000, random_state=SEED), cv=3, method="isotonic")),

    # CalibratedClassifierCV(PassiveAggressiveClassifier) — en ligne, calibre (33-41)
    33: ("CalibPA_C1", F_A, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=1.0, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    34: ("CalibPA_C01", F_B, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=0.1, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    35: ("CalibPA_C10_iso", F_C, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=10.0, max_iter=1000, random_state=SEED), cv=3, method="isotonic")),
    36: ("CalibPA_squaredhinge", F_D, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=1.0, loss="squared_hinge", max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    37: ("CalibPA_C005", F_E, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=0.05, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    38: ("CalibPA_C50_F", F_F, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=50.0, max_iter=1000, random_state=SEED), cv=3, method="isotonic")),
    39: ("CalibPA_C02_G", F_G, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=0.2, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    40: ("CalibPA_C2_H", F_H, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=2.0, max_iter=1000, random_state=SEED), cv=3, method="sigmoid")),
    41: ("CalibPA_C1_iso_I", F_I, lambda: CalibratedClassifierCV(PassiveAggressiveClassifier(C=1.0, max_iter=1000, random_state=SEED), cv=3, method="isotonic")),

    # StackingClassifier — meta-modele appris sur les predictions des bases (42-50)
    42: ("Stack_Log_NB_final_Log_A", F_A, lambda: StackingClassifier(estimators=[
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
            ("nb", GaussianNB()),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    43: ("Stack_RF_Log_final_Log_B", F_B, lambda: StackingClassifier(estimators=[
            ("rf", RandomForestClassifier(n_estimators=60, max_depth=4, random_state=SEED, n_jobs=1)),
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    44: ("Stack_3base_final_Log_D", F_D, lambda: StackingClassifier(estimators=[
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
            ("nb", GaussianNB()),
            ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    45: ("Stack_RF_NB_final_Log_G", F_G, lambda: StackingClassifier(estimators=[
            ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1)),
            ("nb", GaussianNB()),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    46: ("Stack_3base_final_Log_H", F_H, lambda: StackingClassifier(estimators=[
            ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)),
            ("dt", DecisionTreeClassifier(max_depth=5, random_state=SEED)),
            ("nb", GaussianNB()),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    47: ("Stack_RF_Log_final_Log_I", F_I, lambda: StackingClassifier(estimators=[
            ("rf", RandomForestClassifier(n_estimators=80, max_depth=5, random_state=SEED, n_jobs=1)),
            ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    48: ("Stack_3base_final_Log_J", F_J, lambda: StackingClassifier(estimators=[
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
            ("nb", GaussianNB()),
            ("rf", RandomForestClassifier(n_estimators=50, max_depth=6, random_state=SEED, n_jobs=1)),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    49: ("Stack_RF_NB_final_Log_E", F_E, lambda: StackingClassifier(estimators=[
            ("rf", RandomForestClassifier(n_estimators=60, max_depth=4, random_state=SEED, n_jobs=1)),
            ("nb", GaussianNB()),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
    50: ("Stack_3base_final_Log_F", F_F, lambda: StackingClassifier(estimators=[
            ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)),
            ("dt", DecisionTreeClassifier(max_depth=3, random_state=SEED)),
            ("nb", GaussianNB()),
        ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=3, n_jobs=1)),
}
