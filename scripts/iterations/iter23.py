"""
Itération 23 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 22 (FactorAnalysis+LogReg, OneClassSVM-augmented, Spline+
KNN, SGD perceptron calibré, Stacking(final=KNN)), itération 23 explore :

1. Pipeline(FactorAnalysis + KNeighborsClassifier) — facteurs latents
   (itération 22) jamais combinés à un classifieur géométrique (seul LogReg
   avait été testé en aval).
2. Pipeline(TruncatedSVD + KNeighborsClassifier) — SVD sans centrage
   (itération 18) jamais combinée à KNN (seul LogReg avait été testé en
   aval).
3. VotingClassifier(soft) : Pipeline(FactorAnalysis+LogReg) + GMMBayes
   (reimplémenté ci-dessous) + GaussianNB — premier comité incluant le
   classifieur génératif maison de l'itération 18.
4. StackingClassifier(final_estimator=GMMBayes) — méta-modèle génératif
   bayésien (au lieu de LogReg/RF/HistGB/GaussianNB/KNN déjà testés comme
   final_estimator), jamais essayé.
5. Pipeline(RobustScaler + Nystroem(rbf) + SGDClassifier(log_loss)) —
   mise à l'échelle résistante aux outliers jamais combinée à
   l'approximation de noyau RBF (Nystroem rbf seul testé en itération 12).

NOTE TECHNIQUE : la classe GMMBayesClassifier de l'itération 18 hérite de
(BaseEstimator, ClassifierMixin) dans cet ordre, ce qui — avec la version de
scikit-learn de cet environnement (système de "tags" SLEP006) — l'empêche
d'être reconnue comme un classifieur par VotingClassifier/StackingClassifier
(is_classifier() renvoie False, erreur "should be a classifier"). L'ordre
correct pour l'héritage coopératif des tags est (ClassifierMixin,
BaseEstimator) — voir la classe redéfinie ci-dessous. Cette correction ne
change AUCUN comportement de fit/predict (donc n'invalide pas les résultats
déjà obtenus en itération 18/20, qui n'utilisaient pas Voting/Stacking) ;
c'est un pur correctif de compatibilité, pas une nouvelle hypothèse.

Idée écartée avant inclusion : BaggingClassifier(Pipeline(FactorAnalysis+
LogisticRegression)) — 14s/fit à n=9000 (8 estimateurs), bien trop coûteux
pour un bucket de 10 (FactorAnalysis a un coût par fit sensiblement plus
élevé que Spline/PCA/TruncatedSVD, cf. mesure isolée à 1.7-1.9s/fit).

Vitesse vérifiée sur n=9000 : toutes les familles retenues <3.8s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
import numpy as np
from sklearn.decomposition import FactorAnalysis, TruncatedSVD
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier, StackingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import RobustScaler
from sklearn.kernel_approximation import Nystroem
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import Pipeline

SEED = 42


class GMMBayesClassifier(ClassifierMixin, BaseEstimator):
    """Classifieur bayesien generatif (un GaussianMixture par classe),
    reimplemente depuis l'iteration 18 avec l'ordre d'heritage corrige
    (ClassifierMixin avant BaseEstimator) pour etre reconnu par
    VotingClassifier/StackingClassifier -- voir note technique ci-dessus."""

    def __init__(self, n_components=2, random_state=SEED):
        self.n_components = n_components
        self.random_state = random_state

    def fit(self, X, y):
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        self.gmms_ = {}
        self.priors_ = {}
        for c in self.classes_:
            Xc = X[y == c]
            gmm = GaussianMixture(n_components=self.n_components, random_state=self.random_state)
            gmm.fit(Xc)
            self.gmms_[c] = gmm
            self.priors_[c] = len(Xc) / len(X)
        return self

    def predict_proba(self, X):
        scores = np.zeros((len(X), len(self.classes_)))
        for i, c in enumerate(self.classes_):
            scores[:, i] = self.gmms_[c].score_samples(X) + np.log(self.priors_[c])
        scores -= scores.max(axis=1, keepdims=True)
        probs = np.exp(scores)
        probs /= probs.sum(axis=1, keepdims=True)
        return probs

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]


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
    # Pipeline(FactorAnalysis + KNeighborsClassifier) (1-10)
    1: ("FactorAnalysis_KNN_A", F_A, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    2: ("FactorAnalysis_KNN_B_c1", F_B, lambda: Pipeline([("fa", FactorAnalysis(n_components=1, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    3: ("FactorAnalysis_KNN_C", F_C, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    4: ("FactorAnalysis_KNN_D", F_D, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    5: ("FactorAnalysis_KNN_E_c1", F_E, lambda: Pipeline([("fa", FactorAnalysis(n_components=1, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))])),
    6: ("FactorAnalysis_KNN_F", F_F, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    7: ("FactorAnalysis_KNN_G", F_G, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    8: ("FactorAnalysis_KNN_H", F_H, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    9: ("FactorAnalysis_KNN_I", F_I, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    10: ("FactorAnalysis_KNN_wide_K_c3", F_K, lambda: Pipeline([("fa", FactorAnalysis(n_components=3, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),

    # Pipeline(TruncatedSVD + KNeighborsClassifier) (11-20)
    11: ("TruncSVD_KNN_A", F_A, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    12: ("TruncSVD_KNN_B_c1", F_B, lambda: Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    13: ("TruncSVD_KNN_C", F_C, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    14: ("TruncSVD_KNN_D", F_D, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    15: ("TruncSVD_KNN_E_c1", F_E, lambda: Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))])),
    16: ("TruncSVD_KNN_F", F_F, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    17: ("TruncSVD_KNN_G", F_G, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),
    18: ("TruncSVD_KNN_H", F_H, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))])),
    19: ("TruncSVD_KNN_I", F_I, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))])),
    20: ("TruncSVD_KNN_wide_K_c3", F_K, lambda: Pipeline([("svd", TruncatedSVD(n_components=3, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))])),

    # VotingClassifier(soft) : FactorAnalysis+LogReg + GMMBayes + GaussianNB (21-30)
    21: ("VotingFA_GMM_NB_A", F_A, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    22: ("VotingFA_GMM_NB_B", F_B, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    23: ("VotingFA_GMM_NB_C", F_C, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    24: ("VotingFA_GMM_NB_D_weighted", F_D, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", weights=[1, 2, 1], n_jobs=1)),
    25: ("VotingFA_GMM_NB_E", F_E, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    26: ("VotingFA_GMM_NB_F", F_F, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    27: ("VotingFA_GMM_NB_G", F_G, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=1)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    28: ("VotingFA_GMM_NB_H", F_H, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),
    29: ("VotingFA_GMM_NB_I_weighted", F_I, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=2, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", weights=[2, 1, 1], n_jobs=1)),
    30: ("VotingFA_GMM_NB_wide_K", F_K, lambda: VotingClassifier(estimators=[("fa", Pipeline([("f", FactorAnalysis(n_components=3, random_state=SEED)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("gmm", GMMBayesClassifier(n_components=2)), ("nb", GaussianNB())], voting="soft", n_jobs=1)),

    # StackingClassifier(final_estimator=GMMBayes) (31-40)
    31: ("StackGMMBayes_A", F_A, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=2), cv=3, n_jobs=1)),
    32: ("StackGMMBayes_B", F_B, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=2), cv=3, n_jobs=1)),
    33: ("StackGMMBayes_C_c1", F_C, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=1), cv=3, n_jobs=1)),
    34: ("StackGMMBayes_D", F_D, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=2), cv=3, n_jobs=1)),
    35: ("StackGMMBayes_E", F_E, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=2), cv=5, n_jobs=1)),
    36: ("StackGMMBayes_F", F_F, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=2), cv=3, n_jobs=1)),
    37: ("StackGMMBayes_G_3base", F_G, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))], final_estimator=GMMBayesClassifier(n_components=2), cv=3, n_jobs=1)),
    38: ("StackGMMBayes_H", F_H, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=2), cv=3, n_jobs=1)),
    39: ("StackGMMBayes_I_c1", F_I, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=1), cv=3, n_jobs=1)),
    40: ("StackGMMBayes_wide_K", F_K, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GMMBayesClassifier(n_components=2), cv=3, n_jobs=1)),

    # Pipeline(RobustScaler + Nystroem(rbf) + SGDClassifier(log_loss)) (41-50)
    41: ("RobustScaler_Nystroem_SGD_A", F_A, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    42: ("RobustScaler_Nystroem_SGD_B_n30", F_B, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=30, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    43: ("RobustScaler_Nystroem_SGD_C", F_C, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-3, random_state=SEED))])),
    44: ("RobustScaler_Nystroem_SGD_D_n80", F_D, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=80, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    45: ("RobustScaler_Nystroem_SGD_E", F_E, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-5, random_state=SEED))])),
    46: ("RobustScaler_Nystroem_SGD_F", F_F, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="modified_huber", alpha=1e-4, random_state=SEED))])),
    47: ("RobustScaler_Nystroem_SGD_G_quantrange", F_G, lambda: Pipeline([("rs", RobustScaler(quantile_range=(10.0, 90.0))), ("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    48: ("RobustScaler_Nystroem_SGD_H", F_H, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=60, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
    49: ("RobustScaler_Nystroem_SGD_I", F_I, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=50, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, penalty="elasticnet", random_state=SEED))])),
    50: ("RobustScaler_Nystroem_SGD_wide_K", F_K, lambda: Pipeline([("rs", RobustScaler()), ("ny", Nystroem(kernel="rbf", n_components=80, random_state=SEED)), ("sgd", SGDClassifier(loss="log_loss", alpha=1e-4, random_state=SEED))])),
}
