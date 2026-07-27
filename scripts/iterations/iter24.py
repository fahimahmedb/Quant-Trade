"""
Itération 24 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 23 (FactorAnalysis/TruncatedSVD+KNN, Voting/Stacking avec
GMMBayes, RobustScaler+Nystroem+SGD), itération 24 explore :

1. Pipeline(PolynomialFeatures(degree=3, interaction_only=True) +
   LogisticRegression) — interactions d'ordre 3 (triples produits de
   features), jamais testées (degré 2 seul en itérations 7/11). Restreint
   à interaction_only=True après mesure de vitesse : la version complète
   (avec puissances pures x^3, x^2y, etc.) coûte ~5.3s/fit à n=9000,
   extrapolée à ~24 min/stratégie sur l'historique complet — beaucoup trop
   pour un bucket de 10 ; la version interaction_only est ~14x plus rapide
   (0.37s/fit) pour une hypothèse tout aussi valide (interactions triples
   sans les puissances pures, déjà partiellement couvertes par les arbres).
2. BaggingClassifier(Pipeline(TruncatedSVD+KNeighborsClassifier)) — version
   "bagged" du pipeline de l'itération 23 (bucket 2), même logique que les
   Bagging(Spline+LogReg) de l'itération 21.
3. Pipeline(Nystroem(kernel="sigmoid") + SGDClassifier(log_loss)) — noyau
   sigmoïde jamais utilisé pour l'approximation de noyau (rbf, poly, cosine
   déjà testés en itérations 12/20).
4. VotingClassifier(soft) : Pipeline(TruncatedSVD+KNN) + Pipeline
   (FactorAnalysis+LogReg) + RandomForest — comité combinant les deux
   nouvelles familles de réduction de dimension de l'itération 23 avec un
   modèle d'arbres.
5. Pipeline(SplineTransformer + GaussianNB) — base de splines jamais
   combinée à Naive Bayes (LogReg/RidgeCV/HistGB/KNN testés en itérations
   20-22).

Vitesse vérifiée sur n=9000 : toutes les familles retenues <1.9s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.preprocessing import PolynomialFeatures, SplineTransformer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import TruncatedSVD, FactorAnalysis
from sklearn.ensemble import BaggingClassifier, VotingClassifier, RandomForestClassifier
from sklearn.kernel_approximation import Nystroem
from sklearn.naive_bayes import GaussianNB
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
    # Pipeline(PolynomialFeatures(degree=3, interaction_only=True) + LogReg) (1-10)
    1: ("Poly3_interact_Log_A", F_A, lambda: Pipeline([("poly", PolynomialFeatures(degree=3, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("Poly3_interact_Log_B", F_B, lambda: Pipeline([("poly", PolynomialFeatures(degree=3, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    3: ("Poly3_interact_Log_C", F_C, lambda: Pipeline([("poly", PolynomialFeatures(degree=3, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    4: ("Poly3_interact_Log_D", F_D, lambda: Pipeline([("poly", PolynomialFeatures(degree=3, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("Poly3_interact_Log_E", F_E, lambda: Pipeline([("poly", PolynomialFeatures(degree=3, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    6: ("Poly3_interact_Log_F", F_F, lambda: Pipeline([("poly", PolynomialFeatures(degree=3, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    7: ("Poly2_interact_Log_G_deg2", F_G, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    8: ("Poly2_interact_Log_H_deg2", F_H, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    9: ("Poly2_interact_Log_I_deg2", F_I, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    10: ("Poly2_interact_Log_J_deg2", F_J, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),

    # BaggingClassifier(Pipeline(TruncatedSVD+KNeighborsClassifier)) (11-20)
    11: ("Bagging_TruncSVD_KNN_A", F_A, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))]), n_estimators=10, random_state=SEED)),
    12: ("Bagging_TruncSVD_KNN_B", F_B, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))]), n_estimators=10, random_state=SEED)),
    13: ("Bagging_TruncSVD_KNN_C", F_C, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))]), n_estimators=10, random_state=SEED)),
    14: ("Bagging_TruncSVD_KNN_D_n15", F_D, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))]), n_estimators=15, random_state=SEED)),
    15: ("Bagging_TruncSVD_KNN_E", F_E, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))]), n_estimators=10, random_state=SEED)),
    16: ("Bagging_TruncSVD_KNN_F", F_F, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))]), n_estimators=10, random_state=SEED)),
    17: ("Bagging_TruncSVD_KNN_G", F_G, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))]), n_estimators=10, random_state=SEED)),
    18: ("Bagging_TruncSVD_KNN_H", F_H, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))]), n_estimators=10, random_state=SEED)),
    19: ("Bagging_TruncSVD_KNN_I", F_I, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))]), n_estimators=10, random_state=SEED)),
    20: ("Bagging_TruncSVD_KNN_wide_K", F_K, lambda: BaggingClassifier(estimator=Pipeline([("svd", TruncatedSVD(n_components=3, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))]), n_estimators=10, random_state=SEED)),

    # Pipeline(Nystroem(sigmoid) + SGDClassifier(log_loss)) (21-30)
    21: ("Nystroem_sigmoid_SGD_A", F_A, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    22: ("Nystroem_sigmoid_SGD_B_n30", F_B, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=30, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    23: ("Nystroem_sigmoid_SGD_C", F_C, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-3, random_state=SEED))])),
    24: ("Nystroem_sigmoid_SGD_D_n80", F_D, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=80, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    25: ("Nystroem_sigmoid_SGD_E", F_E, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-5, random_state=SEED))])),
    26: ("Nystroem_sigmoid_SGD_F", F_F, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="modified_huber", alpha=1e-4, random_state=SEED))])),
    27: ("Nystroem_sigmoid_SGD_G", F_G, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    28: ("Nystroem_sigmoid_SGD_H", F_H, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=60, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    29: ("Nystroem_sigmoid_SGD_I", F_I, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, penalty="elasticnet", random_state=SEED))])),
    30: ("Nystroem_sigmoid_SGD_wide_K", F_K, lambda: Pipeline([("ny", Nystroem(kernel="sigmoid", n_components=80, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),

    # VotingClassifier(soft) : TruncSVD+KNN + FactorAnalysis+LogReg + RandomForest (31-40)
    31: ("VotingSVD_FA_RF_A", F_A, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    32: ("VotingSVD_FA_RF_B", F_B, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    33: ("VotingSVD_FA_RF_C", F_C, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    34: ("VotingSVD_FA_RF_D_weighted", F_D, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", weights=[1, 1, 2], n_jobs=1)),
    35: ("VotingSVD_FA_RF_E", F_E, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=1, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    36: ("VotingSVD_FA_RF_F", F_F, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    37: ("VotingSVD_FA_RF_G", F_G, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    38: ("VotingSVD_FA_RF_H", F_H, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    39: ("VotingSVD_FA_RF_I", F_I, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    40: ("VotingSVD_FA_RF_wide_K", F_K, lambda: VotingClassifier(estimators=[("svdknn", Pipeline([("svd", TruncatedSVD(n_components=3, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])), ("fa", Pipeline([("f", FactorAnalysis(n_components=3, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),

    # Pipeline(SplineTransformer + GaussianNB) (41-50)
    41: ("Spline_GaussianNB_A", F_A, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())])),
    42: ("Spline_GaussianNB_B_k4", F_B, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=3)), ("nb", GaussianNB())])),
    43: ("Spline_GaussianNB_C", F_C, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())])),
    44: ("Spline_GaussianNB_D_deg2", F_D, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("nb", GaussianNB())])),
    45: ("Spline_GaussianNB_E", F_E, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())])),
    46: ("Spline_GaussianNB_F_k6", F_F, lambda: Pipeline([("spl", SplineTransformer(n_knots=6, degree=3)), ("nb", GaussianNB())])),
    47: ("Spline_GaussianNB_G", F_G, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())])),
    48: ("Spline_GaussianNB_H_deg2", F_H, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=2)), ("nb", GaussianNB())])),
    49: ("Spline_GaussianNB_I", F_I, lambda: Pipeline([("spl", SplineTransformer(n_knots=5, degree=3)), ("nb", GaussianNB())])),
    50: ("Spline_GaussianNB_wide_K_k4", F_K, lambda: Pipeline([("spl", SplineTransformer(n_knots=4, degree=2)), ("nb", GaussianNB())])),
}
