"""
Itération 12 — 50 nouvelles hypothèses (univers figé a priori).

Après 9 itérations dominées par des ensembles d'arbres, du voting/stacking et
des reparamétrisations de scaler (Quantile/MinMax/StandardScaler), itération
12 explore des familles de transformation/représentation jamais essayées
jusqu'ici, combinées à des classifieurs simples et rapides :

1. Pipeline(RandomTreesEmbedding + LogisticRegression) — encodage non
   supervisé des features en index de feuilles (forêt aléatoire non
   supervisée) puis modèle linéaire sur cette représentation à haute
   dimension éparse. Jamais utilisé (RandomTreesEmbedding absent de toutes
   les itérations précédentes).
2. Pipeline(Nystroem(rbf) + SGDClassifier(log_loss)) — approximation de
   noyau RBF (feature map explicite) suivie d'un classifieur linéaire
   entraîné par SGD, alternative rapide à un SVM à noyau (dont la version
   bagged s'était révélée trop lente en itération 10).
3. Pipeline(FeatureAgglomeration + RandomForest) — réduction de dimension
   par clustering hiérarchique des features (corrélation), distincte de la
   projection linéaire de la PCA déjà testée (itération 8).
4. Pipeline(GaussianRandomProjection + LogisticRegression) — réduction de
   dimension par projection aléatoire (lemme de Johnson-Lindenstrauss),
   jamais combinée à un classifieur jusqu'ici.
5. Pipeline(KBinsDiscretizer + CategoricalNB) — discrétisation en quantiles
   puis Naive Bayes catégoriel, jamais essayé (seuls Gaussian/Bernoulli/
   Multinomial/Complement NB avaient été testés sur features continues/
   binarisées).
6. Pipeline(PowerTransformer Yeo-Johnson + KNeighborsClassifier) —
   normalisation par transformation de puissance (distincte du rang de
   QuantileTransformer), combinée à un classifieur géométrique (KNN avait
   été testé mais jamais avec ce preprocessing).

Vitesse vérifiée au préalable sur un sous-échantillon (toutes les familles
<1s/fit) — pas de risque de répéter le problème Bagging(RF/ET/SVC) des
itérations 10-11 (nested ensembles ou noyau exact trop coûteux).

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.ensemble import RandomTreesEmbedding, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.kernel_approximation import Nystroem
from sklearn.cluster import FeatureAgglomeration
from sklearn.random_projection import GaussianRandomProjection
from sklearn.preprocessing import KBinsDiscretizer, PowerTransformer
from sklearn.naive_bayes import CategoricalNB
from sklearn.neighbors import KNeighborsClassifier
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
    # Pipeline(RandomTreesEmbedding + LogisticRegression) (1-10)
    1: ("RTE_Log_A", F_A, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=20, max_depth=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("RTE_Log_B_d4", F_B, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=30, max_depth=4, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    3: ("RTE_Log_C", F_C, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=20, max_depth=3, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    4: ("RTE_Log_D_n40", F_D, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=40, max_depth=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("RTE_Log_E", F_E, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=20, max_depth=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    6: ("RTE_Log_F_d5", F_F, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=25, max_depth=5, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    7: ("RTE_Log_G", F_G, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=20, max_depth=3, random_state=SEED)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    8: ("RTE_Log_H", F_H, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=30, max_depth=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    9: ("RTE_Log_I", F_I, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=20, max_depth=4, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    10: ("RTE_Log_wide_K", F_K, lambda: Pipeline([("rte", RandomTreesEmbedding(n_estimators=30, max_depth=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(Nystroem(rbf) + SGDClassifier(log_loss)) (11-20)
    11: ("Nystroem_SGD_A", F_A, lambda: Pipeline([("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    12: ("Nystroem_SGD_B_g05", F_B, lambda: Pipeline([("ny", Nystroem(kernel="rbf", gamma=0.5, n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    13: ("Nystroem_SGD_C", F_C, lambda: Pipeline([("ny", Nystroem(kernel="rbf", n_components=30, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-3, random_state=SEED))])),
    14: ("Nystroem_SGD_D_n80", F_D, lambda: Pipeline([("ny", Nystroem(kernel="rbf", n_components=80, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    15: ("Nystroem_SGD_E", F_E, lambda: Pipeline([("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-5, random_state=SEED))])),
    16: ("Nystroem_SGD_F", F_F, lambda: Pipeline([("ny", Nystroem(kernel="poly", degree=2, n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    17: ("Nystroem_SGD_G", F_G, lambda: Pipeline([("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="modified_huber", alpha=1e-4, random_state=SEED))])),
    18: ("Nystroem_SGD_H", F_H, lambda: Pipeline([("ny", Nystroem(kernel="rbf", gamma=0.2, n_components=60, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    19: ("Nystroem_SGD_I", F_I, lambda: Pipeline([("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, penalty="elasticnet", random_state=SEED))])),
    20: ("Nystroem_SGD_wide_K", F_K, lambda: Pipeline([("ny", Nystroem(kernel="rbf", n_components=80, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),

    # Pipeline(FeatureAgglomeration + RandomForest) (21-30)
    21: ("FeatAgg_RF_A", F_A, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=2)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    22: ("FeatAgg_RF_B_d4", F_B, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=2)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    23: ("FeatAgg_RF_C", F_C, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=2)), ("rf", RandomForestClassifier(n_estimators=80, max_depth=3, random_state=SEED, n_jobs=1))])),
    24: ("FeatAgg_RF_D_n120", F_D, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=2)), ("rf", RandomForestClassifier(n_estimators=120, max_depth=5, random_state=SEED, n_jobs=1))])),
    25: ("FeatAgg_RF_E", F_E, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=2)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    26: ("FeatAgg_RF_F", F_F, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=2)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    27: ("FeatAgg_RF_G_c3", F_G, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=3)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    28: ("FeatAgg_RF_H_c3", F_H, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=3)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    29: ("FeatAgg_RF_I_c3", F_I, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=3)), ("rf", RandomForestClassifier(n_estimators=80, max_depth=3, random_state=SEED, n_jobs=1))])),
    30: ("FeatAgg_RF_wide_K_c4", F_K, lambda: Pipeline([("fa", FeatureAgglomeration(n_clusters=4)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),

    # Pipeline(GaussianRandomProjection + LogisticRegression) (31-40)
    31: ("GRP_Log_A", F_A, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    32: ("GRP_Log_B", F_B, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    33: ("GRP_Log_C", F_C, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    34: ("GRP_Log_D", F_D, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    35: ("GRP_Log_E", F_E, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    36: ("GRP_Log_F", F_F, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    37: ("GRP_Log_G", F_G, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=4, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    38: ("GRP_Log_H", F_H, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    39: ("GRP_Log_I", F_I, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=4, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    40: ("GRP_Log_wide_K", F_K, lambda: Pipeline([("grp", GaussianRandomProjection(n_components=5, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(KBinsDiscretizer + CategoricalNB) (41-45)
    41: ("KBins_CatNB_A", F_A, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", CategoricalNB())])),
    42: ("KBins_CatNB_D_b7", F_D, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=7, encode="ordinal", strategy="quantile")), ("nb", CategoricalNB())])),
    43: ("KBins_CatNB_G", F_G, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", CategoricalNB())])),
    44: ("KBins_CatNB_J_b4", F_J, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="uniform")), ("nb", CategoricalNB())])),
    45: ("KBins_CatNB_wide_K", F_K, lambda: Pipeline([("kb", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")), ("nb", CategoricalNB())])),

    # Pipeline(PowerTransformer Yeo-Johnson + KNeighborsClassifier) (46-50)
    46: ("PowerYJ_KNN_A", F_A, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    47: ("PowerYJ_KNN_E_k15", F_E, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    48: ("PowerYJ_KNN_G", F_G, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    49: ("PowerYJ_KNN_J_k5", F_J, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))])),
    50: ("PowerYJ_KNN_wide_K", F_K, lambda: Pipeline([("pt", PowerTransformer(method="yeo-johnson")), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
}
