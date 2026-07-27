"""
Itération 18 — 50 nouvelles hypothèses (univers figé a priori).

Après l'itération 17 (RobustScaler, PCA blanchie, ExtraTrees bootstrap, SGD
squared_hinge), itération 18 explore :

1. Pipeline(TruncatedSVD + LogisticRegression) — décomposition en valeurs
   singulières SANS centrage préalable des données (contrairement à PCA,
   déjà testée en itérations 8/17), jamais utilisée.
2. AdaBoostClassifier(LogisticRegression) — apprenant faible LINÉAIRE pour
   le boosting, jamais essayé (tous les AdaBoost précédents utilisaient un
   arbre/NB comme base : stump, RF, ET, GaussianNB).
3. StackingClassifier(final_estimator=GaussianNB) — méta-modèle génératif/
   probabiliste plutôt que discriminant (LogReg, RF, HistGB avaient déjà
   été utilisés comme final_estimator en itérations 5/11/14), jamais
   essayé.
4. Pipeline(Binarizer + ComplementNB) — seuillage binaire simple (0/1) au
   lieu de la discrétisation en quantiles de KBinsDiscretizer (itération
   14) avant Naive Bayes — approche de discrétisation différente.
5. GMMBayesClassifier — classifieur maison (classe ci-dessous) : un
   GaussianMixture distinct est ajusté par classe (hausse/baisse), la
   prédiction se fait par ratio de vraisemblance pondéré par les priors
   (classifieur bayésien génératif complet). Distinct de GMMFeaturize
   (itération 13, qui exposait les probabilités GMM comme features d'un
   classifieur discriminant en aval) : ici le GMM EST le classifieur.

Vitesse vérifiée sur n=9000 : toutes les familles <0.8s/fit.

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, StackingClassifier
from sklearn.naive_bayes import GaussianNB, ComplementNB
from sklearn.preprocessing import Binarizer
from sklearn.mixture import GaussianMixture
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.pipeline import Pipeline

SEED = 42


class GMMBayesClassifier(BaseEstimator, ClassifierMixin):
    """Classifieur bayesien generatif : un GaussianMixture distinct par
    classe, prediction par ratio de vraisemblance pondere par les priors.
    Jamais utilise jusqu'ici (GMMFeaturize en iteration 13 exposait les
    probabilites GMM comme features d'un classifieur discriminant en aval ;
    ici le GMM EST directement le classifieur)."""

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
    # Pipeline(TruncatedSVD + LogisticRegression) (1-10)
    1: ("TruncSVD_Log_A", F_A, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("TruncSVD_Log_B_c1", F_B, lambda: Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    3: ("TruncSVD_Log_C", F_C, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    4: ("TruncSVD_Log_D", F_D, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("TruncSVD_Log_E_c1", F_E, lambda: Pipeline([("svd", TruncatedSVD(n_components=1, random_state=SEED)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    6: ("TruncSVD_Log_F", F_F, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    7: ("TruncSVD_Log_G", F_G, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    8: ("TruncSVD_Log_H", F_H, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    9: ("TruncSVD_Log_I", F_I, lambda: Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    10: ("TruncSVD_Log_wide_K_c3", F_K, lambda: Pipeline([("svd", TruncatedSVD(n_components=3, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),

    # AdaBoostClassifier(LogisticRegression) (11-20)
    11: ("AdaBoost_LogReg_A", F_A, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=30, random_state=SEED)),
    12: ("AdaBoost_LogReg_B_n50", F_B, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=50, random_state=SEED)),
    13: ("AdaBoost_LogReg_C", F_C, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=0.5, max_iter=500, random_state=SEED), n_estimators=30, random_state=SEED)),
    14: ("AdaBoost_LogReg_D_lr05", F_D, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=30, learning_rate=0.5, random_state=SEED)),
    15: ("AdaBoost_LogReg_E", F_E, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=30, random_state=SEED)),
    16: ("AdaBoost_LogReg_F", F_F, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=30, random_state=SEED)),
    17: ("AdaBoost_LogReg_G_n50", F_G, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=50, random_state=SEED)),
    18: ("AdaBoost_LogReg_H", F_H, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=30, random_state=SEED)),
    19: ("AdaBoost_LogReg_I_lr03", F_I, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=30, learning_rate=0.3, random_state=SEED)),
    20: ("AdaBoost_LogReg_wide_K", F_K, lambda: AdaBoostClassifier(estimator=LogisticRegression(C=1.0, max_iter=500, random_state=SEED), n_estimators=40, random_state=SEED)),

    # StackingClassifier(final_estimator=GaussianNB) (21-30)
    21: ("StackGaussianNB_A", F_A, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=3, n_jobs=1)),
    22: ("StackGaussianNB_B", F_B, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=3, n_jobs=1)),
    23: ("StackGaussianNB_3base_C", F_C, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("svd_lr", Pipeline([("svd", TruncatedSVD(n_components=2, random_state=SEED)), ("lr2", LogisticRegression(max_iter=1000, random_state=SEED))]))], final_estimator=GaussianNB(), cv=3, n_jobs=1)),
    24: ("StackGaussianNB_D", F_D, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=3, n_jobs=1)),
    25: ("StackGaussianNB_E", F_E, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=3, n_jobs=1)),
    26: ("StackGaussianNB_F", F_F, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=3, n_jobs=1)),
    27: ("StackGaussianNB_G_cv5", F_G, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=5, n_jobs=1)),
    28: ("StackGaussianNB_H", F_H, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=3, n_jobs=1)),
    29: ("StackGaussianNB_I", F_I, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=3, n_jobs=1)),
    30: ("StackGaussianNB_wide_K", F_K, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=GaussianNB(), cv=3, n_jobs=1)),

    # Pipeline(Binarizer + ComplementNB) (31-40)
    31: ("Binarizer_ComplNB_A", F_A, lambda: Pipeline([("bin", Binarizer(threshold=0.0)), ("nb", ComplementNB())])),
    32: ("Binarizer_ComplNB_B_t05", F_B, lambda: Pipeline([("bin", Binarizer(threshold=0.5)), ("nb", ComplementNB())])),
    33: ("Binarizer_ComplNB_C", F_C, lambda: Pipeline([("bin", Binarizer(threshold=0.0)), ("nb", ComplementNB())])),
    34: ("Binarizer_ComplNB_D_tneg05", F_D, lambda: Pipeline([("bin", Binarizer(threshold=-0.5)), ("nb", ComplementNB())])),
    35: ("Binarizer_ComplNB_E", F_E, lambda: Pipeline([("bin", Binarizer(threshold=0.0)), ("nb", ComplementNB())])),
    36: ("Binarizer_ComplNB_F", F_F, lambda: Pipeline([("bin", Binarizer(threshold=0.0)), ("nb", ComplementNB())])),
    37: ("Binarizer_ComplNB_G_t05", F_G, lambda: Pipeline([("bin", Binarizer(threshold=0.5)), ("nb", ComplementNB())])),
    38: ("Binarizer_ComplNB_H", F_H, lambda: Pipeline([("bin", Binarizer(threshold=0.0)), ("nb", ComplementNB())])),
    39: ("Binarizer_ComplNB_I_tneg05", F_I, lambda: Pipeline([("bin", Binarizer(threshold=-0.5)), ("nb", ComplementNB())])),
    40: ("Binarizer_ComplNB_wide_K", F_K, lambda: Pipeline([("bin", Binarizer(threshold=0.0)), ("nb", ComplementNB())])),

    # GMMBayesClassifier (classifieur generatif maison) (41-50)
    41: ("GMMBayes_A", F_A, lambda: GMMBayesClassifier(n_components=2)),
    42: ("GMMBayes_B_c1", F_B, lambda: GMMBayesClassifier(n_components=1)),
    43: ("GMMBayes_C", F_C, lambda: GMMBayesClassifier(n_components=2)),
    44: ("GMMBayes_D_c3", F_D, lambda: GMMBayesClassifier(n_components=3)),
    45: ("GMMBayes_E", F_E, lambda: GMMBayesClassifier(n_components=2)),
    46: ("GMMBayes_F_c1", F_F, lambda: GMMBayesClassifier(n_components=1)),
    47: ("GMMBayes_G", F_G, lambda: GMMBayesClassifier(n_components=2)),
    48: ("GMMBayes_H_c3", F_H, lambda: GMMBayesClassifier(n_components=3)),
    49: ("GMMBayes_I", F_I, lambda: GMMBayesClassifier(n_components=2)),
    50: ("GMMBayes_wide_K", F_K, lambda: GMMBayesClassifier(n_components=2)),
}
