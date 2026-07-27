"""
Itération 13 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 12 (encodages/projections non supervisés), itération 13
explore des familles encore jamais essayées, filtrées au préalable par un
test de vitesse sur sous-échantillon (règle apprise des itérations 10-11 :
tout ce qui refait un fit coûteux à chaque fenêtre walk-forward, sur ~450
réestimations, explose le temps total) :

1. ExtraTreeClassifier autonome (non ensembliste) — un seul arbre
   extrêmement randomisé (splitter="random"), jamais utilisé seul (seule sa
   version ensembliste ExtraTreesClassifier avait été testée).
2. Pipeline(SparseRandomProjection + LogisticRegression) — projection
   aléatoire creuse (distribution différente de GaussianRandomProjection,
   déjà testée en itération 12), jamais combinée à un classifieur.
3. Pipeline(GMMFeaturize + LogisticRegression) — petit transformer maison
   (classe GMMFeaturize ci-dessous) qui expose les probabilités
   d'appartenance aux composantes d'un GaussianMixture comme features
   d'entrée d'une régression logistique — assignation "douce" (probabiliste),
   à distinguer des distances aux centroïdes KMeans/MiniBatchKMeans déjà
   testées (itération 8, ci-dessous en 5).
4. BaggingClassifier(NearestCentroid) — jamais essayé (NearestCentroid avait
   été testé seul et via CalibratedClassifierCV, mais pas en ensemble
   bagged).
5. Pipeline(MiniBatchKMeans-distance + LogisticRegression) — variante
   stochastique/mini-batch de l'approche KMeans-distance de l'itération 8
   (algorithme distinct, mais conceptuellement proche : bucket réduit à 5
   variantes plutôt que 10).

Idées testées puis ÉCARTÉES avant inclusion (vitesse mesurée sur 3000-6000
lignes, extrapolée à ~450 réestimations sur l'historique NDX complet) :
- Birch-distance + LogisticRegression : ~18s pour UN fit sur 3000 lignes
  (vs <1s pour KMeans/MiniBatchKMeans) → des dizaines de minutes par
  stratégie, même problème que Bagging(RF/ET/SVC) en itérations 10-11.
- NuSVC(probability=True) / CalibratedClassifierCV(SVC(kernel="rbf")) :
  temps de fit ~O(n^2), extrapolé à plusieurs minutes par stratégie sur les
  grandes fenêtres de fin d'échantillon (n≈10000) — même limite que
  Bagging(SVC) en itération 10. `probability=True` sur SVC/NuSVC est aussi
  déprécié depuis sklearn 1.9.
- LogisticRegressionCV (sélection C par validation croisée interne à
  chaque réestimation) : 2.08s (n=3000) -> 8.6s (n=6000), extrapolé à
  ~25s/fit sur les plus grandes fenêtres, soit environ 1h pour une seule
  stratégie sur l'historique complet — trop coûteux pour un bucket de 10.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.tree import ExtraTreeClassifier
from sklearn.random_projection import SparseRandomProjection
from sklearn.linear_model import LogisticRegression
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.cluster import MiniBatchKMeans
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

SEED = 42


class GMMFeaturize(BaseEstimator, TransformerMixin):
    """Remplace les features brutes par les probabilites d'appartenance
    (predict_proba) a un GaussianMixture ajuste sur la fenetre d'entrainement
    -- assignation douce, jamais utilisee jusqu'ici (KMeans/MiniBatchKMeans
    donnent des distances, pas des probabilites)."""

    def __init__(self, n_components=3, random_state=SEED):
        self.n_components = n_components
        self.random_state = random_state

    def fit(self, X, y=None):
        self.gmm_ = GaussianMixture(n_components=self.n_components, random_state=self.random_state)
        self.gmm_.fit(X)
        return self

    def transform(self, X):
        return self.gmm_.predict_proba(X)


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
    # ExtraTreeClassifier autonome, non ensembliste (1-15)
    1: ("ExtraTree1_A", F_A, lambda: ExtraTreeClassifier(max_depth=3, random_state=SEED)),
    2: ("ExtraTree1_B_d4", F_B, lambda: ExtraTreeClassifier(max_depth=4, random_state=SEED)),
    3: ("ExtraTree1_C", F_C, lambda: ExtraTreeClassifier(max_depth=3, random_state=SEED)),
    4: ("ExtraTree1_D_d5", F_D, lambda: ExtraTreeClassifier(max_depth=5, random_state=SEED)),
    5: ("ExtraTree1_E_minleaf", F_E, lambda: ExtraTreeClassifier(max_depth=4, min_samples_leaf=20, random_state=SEED)),
    6: ("ExtraTree1_F", F_F, lambda: ExtraTreeClassifier(max_depth=3, random_state=SEED)),
    7: ("ExtraTree1_G_d6", F_G, lambda: ExtraTreeClassifier(max_depth=6, random_state=SEED)),
    8: ("ExtraTree1_H", F_H, lambda: ExtraTreeClassifier(max_depth=4, random_state=SEED)),
    9: ("ExtraTree1_I_minleaf", F_I, lambda: ExtraTreeClassifier(max_depth=5, min_samples_leaf=30, random_state=SEED)),
    10: ("ExtraTree1_J", F_J, lambda: ExtraTreeClassifier(max_depth=3, random_state=SEED)),
    11: ("ExtraTree1_wide_K", F_K, lambda: ExtraTreeClassifier(max_depth=4, random_state=SEED)),
    12: ("ExtraTree1_wide_K_d6", F_K, lambda: ExtraTreeClassifier(max_depth=6, random_state=SEED)),
    13: ("ExtraTree1_A_minleaf50", F_A, lambda: ExtraTreeClassifier(max_depth=5, min_samples_leaf=50, random_state=SEED)),
    14: ("ExtraTree1_D_minsplit", F_D, lambda: ExtraTreeClassifier(max_depth=4, min_samples_split=40, random_state=SEED)),
    15: ("ExtraTree1_G_minsplit", F_G, lambda: ExtraTreeClassifier(max_depth=5, min_samples_split=60, random_state=SEED)),

    # Pipeline(SparseRandomProjection + LogisticRegression) (16-25)
    16: ("SparseRP_Log_A", F_A, lambda: Pipeline([("srp", SparseRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    17: ("SparseRP_Log_B", F_B, lambda: Pipeline([("srp", SparseRandomProjection(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    18: ("SparseRP_Log_C", F_C, lambda: Pipeline([("srp", SparseRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    19: ("SparseRP_Log_D", F_D, lambda: Pipeline([("srp", SparseRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    20: ("SparseRP_Log_E", F_E, lambda: Pipeline([("srp", SparseRandomProjection(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    21: ("SparseRP_Log_F", F_F, lambda: Pipeline([("srp", SparseRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    22: ("SparseRP_Log_G", F_G, lambda: Pipeline([("srp", SparseRandomProjection(n_components=4, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    23: ("SparseRP_Log_H", F_H, lambda: Pipeline([("srp", SparseRandomProjection(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    24: ("SparseRP_Log_I", F_I, lambda: Pipeline([("srp", SparseRandomProjection(n_components=4, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    25: ("SparseRP_Log_wide_K", F_K, lambda: Pipeline([("srp", SparseRandomProjection(n_components=5, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # Pipeline(GMMFeaturize + LogisticRegression) (26-35)
    26: ("GMMFeat_Log_A", F_A, lambda: Pipeline([("gmm", GMMFeaturize(n_components=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    27: ("GMMFeat_Log_B_c2", F_B, lambda: Pipeline([("gmm", GMMFeaturize(n_components=2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    28: ("GMMFeat_Log_C", F_C, lambda: Pipeline([("gmm", GMMFeaturize(n_components=3)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    29: ("GMMFeat_Log_D_c4", F_D, lambda: Pipeline([("gmm", GMMFeaturize(n_components=4)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    30: ("GMMFeat_Log_E", F_E, lambda: Pipeline([("gmm", GMMFeaturize(n_components=3)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    31: ("GMMFeat_Log_F", F_F, lambda: Pipeline([("gmm", GMMFeaturize(n_components=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    32: ("GMMFeat_Log_G_c2", F_G, lambda: Pipeline([("gmm", GMMFeaturize(n_components=2)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    33: ("GMMFeat_Log_H", F_H, lambda: Pipeline([("gmm", GMMFeaturize(n_components=3)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    34: ("GMMFeat_Log_I_c4", F_I, lambda: Pipeline([("gmm", GMMFeaturize(n_components=4)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    35: ("GMMFeat_Log_wide_K", F_K, lambda: Pipeline([("gmm", GMMFeaturize(n_components=4)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # BaggingClassifier(NearestCentroid) (36-45)
    36: ("Bagging_NC_A", F_A, lambda: BaggingClassifier(estimator=NearestCentroid(), n_estimators=20, random_state=SEED)),
    37: ("Bagging_NC_B_n30", F_B, lambda: BaggingClassifier(estimator=NearestCentroid(), n_estimators=30, random_state=SEED)),
    38: ("Bagging_NC_C", F_C, lambda: BaggingClassifier(estimator=NearestCentroid(), n_estimators=20, random_state=SEED)),
    39: ("Bagging_NC_D_manhattan", F_D, lambda: BaggingClassifier(estimator=NearestCentroid(metric="manhattan"), n_estimators=20, random_state=SEED)),
    40: ("Bagging_NC_E", F_E, lambda: BaggingClassifier(estimator=NearestCentroid(), n_estimators=25, random_state=SEED)),
    41: ("Bagging_NC_F", F_F, lambda: BaggingClassifier(estimator=NearestCentroid(), n_estimators=20, random_state=SEED)),
    42: ("Bagging_NC_G_n40", F_G, lambda: BaggingClassifier(estimator=NearestCentroid(), n_estimators=40, random_state=SEED)),
    43: ("Bagging_NC_H", F_H, lambda: BaggingClassifier(estimator=NearestCentroid(), n_estimators=20, random_state=SEED)),
    44: ("Bagging_NC_I_manhattan", F_I, lambda: BaggingClassifier(estimator=NearestCentroid(metric="manhattan"), n_estimators=25, random_state=SEED)),
    45: ("Bagging_NC_wide_K", F_K, lambda: BaggingClassifier(estimator=NearestCentroid(), n_estimators=30, random_state=SEED)),

    # Pipeline(MiniBatchKMeans-distance + LogisticRegression) (46-50)
    46: ("MBKMeans_Log_A", F_A, lambda: Pipeline([("mbk", MiniBatchKMeans(n_clusters=4, random_state=SEED, n_init=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    47: ("MBKMeans_Log_E_c3", F_E, lambda: Pipeline([("mbk", MiniBatchKMeans(n_clusters=3, random_state=SEED, n_init=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    48: ("MBKMeans_Log_G", F_G, lambda: Pipeline([("mbk", MiniBatchKMeans(n_clusters=4, random_state=SEED, n_init=3)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    49: ("MBKMeans_Log_J_c5", F_J, lambda: Pipeline([("mbk", MiniBatchKMeans(n_clusters=5, random_state=SEED, n_init=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    50: ("MBKMeans_Log_wide_K", F_K, lambda: Pipeline([("mbk", MiniBatchKMeans(n_clusters=4, random_state=SEED, n_init=3)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
}
