"""
Itération 27 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 26 (Bagging(Spline+NB), Voting/Stacking avec MLP(tanh),
HistGB/RF sur nouvelles combinaisons de features), itération 27 introduit
une idée STRUCTURELLE jamais explorée : un comité "à vues de features"
(feature-view ensemble), où chaque membre de base ne voit qu'un SOUS-
ENSEMBLE sémantique des 10 features larges (momentum / volatilité /
retour-à-la-moyenne) au lieu de toutes les recevoir — jusqu'ici, TOUS les
Voting/Stacking du projet donnaient les mêmes features à chaque membre.

1. VotingClassifier(soft) à 3 membres "à vues" : Pipeline(ColumnSelect
   momentum [mom_10, mom_20] + LogReg), Pipeline(ColumnSelect volatilité
   [vol_10, vol_20, atr_rel] + LogReg), Pipeline(ColumnSelect retour-a-la-
   moyenne [rsi_14, macd_rel, bb_pctb, stoch_k, ma_ratio_20] + LogReg).
   Classe ColumnSelect (ci-dessous) : transformer maison trivial qui
   sélectionne un sous-ensemble fixe de colonnes par position.
2. StackingClassifier avec les mêmes 3 membres "à vues" comme base,
   final_estimator=LogisticRegression — le méta-modèle apprend à combiner
   les 3 avis spécialisés plutôt que 3 avis sur les mêmes données.
3. Pipeline(TruncatedSVD + GaussianNB) — SVD sans centrage (itération 18)
   jamais combinée à Naive Bayes.
4. Pipeline(FactorAnalysis + GaussianNB) — facteurs latents (itération 22)
   jamais combinés à Naive Bayes.
5. VotingClassifier(soft) : GMMBayes (réimplémenté, cf. itération 23) +
   Pipeline(SplineTransformer+LogReg) + RandomForest — comité mélangeant
   générative/spline/arbres, jamais assemblé.

Vitesse vérifiée sur n=9000 : StackingClassifier(vues) le plus coûteux à
~4.3s/fit (bucket réduit à 6 variantes en conséquence) ; toutes les autres
familles <3.3s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
import numpy as np
from sklearn.decomposition import TruncatedSVD, FactorAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import VotingClassifier, StackingClassifier, RandomForestClassifier
from sklearn.preprocessing import SplineTransformer
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import Pipeline

SEED = 42


class ColumnSelect(BaseEstimator, TransformerMixin):
    """Selectionne un sous-ensemble fixe de colonnes par position -- permet
    a chaque membre d'un comite de ne voir qu'une VUE partielle des features
    (jamais fait jusqu'ici : tous les Voting/Stacking precedents donnaient
    les memes features a chaque membre)."""

    def __init__(self, indices=None):
        self.indices = indices

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[:, self.indices]


class GMMBayesClassifier(ClassifierMixin, BaseEstimator):
    """Classifieur bayesien generatif (cf. iteration 18/23), ordre d'heritage
    corrige pour compatibilite Voting/Stacking."""

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


# Feature large fixe pour les strategies "a vues" : indices positionnels
# [0]=mom_10 [1]=mom_20 [2]=vol_10 [3]=vol_20 [4]=rsi_14 [5]=macd_rel
# [6]=bb_pctb [7]=atr_rel [8]=stoch_k [9]=ma_ratio_20
F_VIEWS = ["mom_10", "mom_20", "vol_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "atr_rel", "stoch_k", "ma_ratio_20"]
MOM_IDX = [0, 1]
VOL_IDX = [2, 3, 7]
MR_IDX = [4, 5, 6, 8, 9]

F_A = ["mom_10", "vol_10", "rsi_14"]
F_B = ["mom_20", "vol_ratio", "macd_rel"]
F_C = ["ma_ratio_20", "stoch_k", "atr_rel"]
F_D = ["fracdiff_04", "parkinson_5", "vol_20"]
F_E = ["ret_1", "ret_2", "drawdown_60"]
F_F = ["mom_10", "mom_20", "bb_pctb"]
F_G = ["ma_ratio_50", "vol_10", "rsi_14", "stoch_k"]
F_H = ["ret_3", "ret_5", "vol_ratio", "atr_rel"]
F_I = ["fracdiff_04", "mom_10", "macd_rel", "bb_pctb"]
F_K = ["mom_10", "mom_20", "vol_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "atr_rel", "stoch_k", "ma_ratio_20"]


def _views_voting(weights=None):
    return VotingClassifier(estimators=[
        ("mom", Pipeline([("cs", ColumnSelect(MOM_IDX)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])),
        ("vol", Pipeline([("cs", ColumnSelect(VOL_IDX)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])),
        ("mr", Pipeline([("cs", ColumnSelect(MR_IDX)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])),
    ], voting="soft", weights=weights, n_jobs=1)


def _views_stacking(cv=2):
    return StackingClassifier(estimators=[
        ("mom", Pipeline([("cs", ColumnSelect(MOM_IDX)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])),
        ("vol", Pipeline([("cs", ColumnSelect(VOL_IDX)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])),
        ("mr", Pipeline([("cs", ColumnSelect(MR_IDX)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])),
    ], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), cv=cv, n_jobs=1)


STRATEGIES = {
    # VotingClassifier "a vues" (momentum/volatilite/retour-a-la-moyenne) (1-12)
    1: ("VotingViews_1", F_VIEWS, lambda: _views_voting()),
    2: ("VotingViews_2_weighted_mom", F_VIEWS, lambda: _views_voting(weights=[2, 1, 1])),
    3: ("VotingViews_3_weighted_vol", F_VIEWS, lambda: _views_voting(weights=[1, 2, 1])),
    4: ("VotingViews_4_weighted_mr", F_VIEWS, lambda: _views_voting(weights=[1, 1, 2])),
    5: ("VotingViews_5", F_VIEWS, lambda: _views_voting()),
    6: ("VotingViews_6_weighted", F_VIEWS, lambda: _views_voting(weights=[1, 2, 2])),
    7: ("VotingViews_7", F_VIEWS, lambda: _views_voting()),
    8: ("VotingViews_8_weighted", F_VIEWS, lambda: _views_voting(weights=[3, 1, 1])),
    9: ("VotingViews_9", F_VIEWS, lambda: _views_voting()),
    10: ("VotingViews_10_weighted", F_VIEWS, lambda: _views_voting(weights=[1, 1, 3])),
    11: ("VotingViews_11", F_VIEWS, lambda: _views_voting()),
    12: ("VotingViews_12_weighted", F_VIEWS, lambda: _views_voting(weights=[1, 3, 1])),

    # StackingClassifier "a vues" (13-18)
    13: ("StackViews_1", F_VIEWS, lambda: _views_stacking(cv=2)),
    14: ("StackViews_2", F_VIEWS, lambda: _views_stacking(cv=2)),
    15: ("StackViews_3_cv3", F_VIEWS, lambda: _views_stacking(cv=3)),
    16: ("StackViews_4", F_VIEWS, lambda: _views_stacking(cv=2)),
    17: ("StackViews_5", F_VIEWS, lambda: _views_stacking(cv=2)),
    18: ("StackViews_6_cv3", F_VIEWS, lambda: _views_stacking(cv=3)),

    # Pipeline(TruncatedSVD + GaussianNB) (19-32)
    19: ("TruncSVD_NB_A", F_A, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    20: ("TruncSVD_NB_B_c1", F_B, lambda: Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("nb", GaussianNB())])),
    21: ("TruncSVD_NB_C", F_C, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    22: ("TruncSVD_NB_D", F_D, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    23: ("TruncSVD_NB_E_c1", F_E, lambda: Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("nb", GaussianNB())])),
    24: ("TruncSVD_NB_F", F_F, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    25: ("TruncSVD_NB_G", F_G, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    26: ("TruncSVD_NB_H", F_H, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    27: ("TruncSVD_NB_I", F_I, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    28: ("TruncSVD_NB_wide_K_c3", F_K, lambda: Pipeline([("svd", TruncatedSVD(n_components=3, random_state=SEED)), ("nb", GaussianNB())])),
    29: ("TruncSVD_NB_A2", F_A, lambda: Pipeline([("svd", TruncatedSVD(n_components=3, random_state=SEED)), ("nb", GaussianNB())])),
    30: ("TruncSVD_NB_C2", F_C, lambda: Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("nb", GaussianNB())])),
    31: ("TruncSVD_NB_F2", F_F, lambda: Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("nb", GaussianNB())])),
    32: ("TruncSVD_NB_wide_K2", F_K, lambda: Pipeline([("svd", TruncatedSVD(n_components=4, random_state=SEED)), ("nb", GaussianNB())])),

    # Pipeline(FactorAnalysis + GaussianNB) (33-40)
    33: ("FA_NB_A", F_A, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    34: ("FA_NB_B_c1", F_B, lambda: Pipeline([("fa", FactorAnalysis(n_components=1, random_state=SEED)), ("nb", GaussianNB())])),
    35: ("FA_NB_C", F_C, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    36: ("FA_NB_D", F_D, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    37: ("FA_NB_E_c1", F_E, lambda: Pipeline([("fa", FactorAnalysis(n_components=1, random_state=SEED)), ("nb", GaussianNB())])),
    38: ("FA_NB_G", F_G, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    39: ("FA_NB_I", F_I, lambda: Pipeline([("fa", FactorAnalysis(n_components=2, random_state=SEED)), ("nb", GaussianNB())])),
    40: ("FA_NB_wide_K_c3", F_K, lambda: Pipeline([("fa", FactorAnalysis(n_components=3, random_state=SEED)), ("nb", GaussianNB())])),

    # VotingClassifier(soft) : GMMBayes + Spline+LogReg + RandomForest (41-50)
    41: ("VotingGMM_Spline_RF_A", F_A, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    42: ("VotingGMM_Spline_RF_B", F_B, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=4, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    43: ("VotingGMM_Spline_RF_C", F_C, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", weights=[1, 1, 2], n_jobs=1)),
    44: ("VotingGMM_Spline_RF_D", F_D, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    45: ("VotingGMM_Spline_RF_E", F_E, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=1)), ("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    46: ("VotingGMM_Spline_RF_F", F_F, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", weights=[2, 1, 1], n_jobs=1)),
    47: ("VotingGMM_Spline_RF_G", F_G, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    48: ("VotingGMM_Spline_RF_H", F_H, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
    49: ("VotingGMM_Spline_RF_I", F_I, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=5, degree=3)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1))], voting="soft", weights=[1, 2, 1], n_jobs=1)),
    50: ("VotingGMM_Spline_RF_wide_K", F_K, lambda: VotingClassifier(estimators=[("gmm", GMMBayesClassifier(n_components=2)), ("spl", Pipeline([("s", SplineTransformer(n_knots=4, degree=2)), ("lr", LogisticRegression(max_iter=1000, random_state=SEED))])), ("rf", RandomForestClassifier(n_estimators=80, max_depth=4, random_state=SEED, n_jobs=1))], voting="soft", n_jobs=1)),
}
