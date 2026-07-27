"""
Itération 8 — 50 nouvelles hypothèses (univers figé a priori).

Après 5 itérations de familles de classifieurs et 1 itération de formes
fonctionnelles (poly/PCA+LogReg), itération 8 explore le PRÉTRAITEMENT et
les CONTRAINTES DE DOMAINE plutôt qu'encore un nouveau classifieur :

1. QuantileTransformer + LogisticRegression : normalisation par rang
   (uniforme/gaussienne) au lieu du z-score classique — hypothèse que la
   relation est mieux capturée après aplatissement des queues épaisses
   (déjà établies en Étape A) que par une standardisation linéaire.
2. PCA + RandomForest/ExtraTrees : réduction de dimension non supervisée
   suivie d'un classifieur NON linéaire (contrairement à iter7 qui
   utilisait PCA+LogReg) — teste si la variance résiduelle après PCA a
   une structure non linéaire exploitable.
3. KMeans (distance aux centroïdes) + LogisticRegression : représentation
   par distance aux clusters plutôt que les features brutes — hypothèse
   de régimes de marché discrets.
4. HistGradientBoostingClassifier avec contraintes monotones : impose
   des priors financiers explicites (momentum haussier -> proba de hausse
   croissante) plutôt que de laisser le modèle apprendre librement.
5. MinMaxScaler + ComplementNB/MultinomialNB : Naive Bayes sur features
   non-négatives (jamais testé, GaussianNB et BernoulliNB déjà essayés).

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.naive_bayes import ComplementNB, MultinomialNB
from sklearn.preprocessing import QuantileTransformer, MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

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
F_K = ["mom_10", "mom_20", "vol_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "atr_rel", "stoch_k"]

# +1 = hausse de la feature associee a hausse de la proba de hausse (prior financier)
# -1 = hausse de la feature associee a baisse de la proba de hausse
#  0 = pas de contrainte
MONO = {
    "mom_10": 1, "mom_20": 1, "ret_1": 1, "ret_2": 1, "ret_3": 1, "ret_5": 1, "ret_10": 1,
    "rsi_14": 1, "macd_rel": 1, "ma_ratio_20": 1, "ma_ratio_50": 1, "stoch_k": 1,
    "vol_20": 0, "vol_10": 0, "vol_ratio": 0, "atr_rel": 0, "parkinson_5": 0,
    "bb_pctb": 1, "fracdiff_04": 1, "drawdown_60": -1,
}


def mono_cst(features):
    return [MONO.get(f, 0) for f in features]


STRATEGIES = {
    # QuantileTransformer + LogisticRegression - normalisation par rang (1-12)
    1: ("QuantUniform_Log_A_C1", F_A, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    2: ("QuantNormal_Log_A_C1", F_A, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    3: ("QuantUniform_Log_B_C05", F_B, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    4: ("QuantNormal_Log_C_C1", F_C, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    5: ("QuantUniform_Log_D_C10", F_D, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=10.0, max_iter=1000, random_state=SEED))])),
    6: ("QuantNormal_Log_E_C02", F_E, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=0.2, max_iter=1000, random_state=SEED))])),
    7: ("QuantUniform_Log_G_C1", F_G, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    8: ("QuantNormal_Log_H_C1", F_H, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    9: ("QuantUniform_Log_I_C05", F_I, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    10: ("QuantNormal_Log_J_C1", F_J, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    11: ("QuantUniform_Log_K_C1", F_K, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    12: ("QuantNormal_Log_K_C02", F_K, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("lr", LogisticRegression(C=0.2, max_iter=1000, random_state=SEED))])),

    # PCA + RandomForest/ExtraTrees - reduction dim + non-lineaire (13-24)
    13: ("PCA2_RF_K_d3", F_K, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    14: ("PCA3_RF_K_d4", F_K, lambda: Pipeline([("pca", PCA(n_components=3, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    15: ("PCA4_ET_K_d3", F_K, lambda: Pipeline([("pca", PCA(n_components=4, random_state=SEED)), ("et", ExtraTreesClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    16: ("PCA2_RF_A_d2", F_A, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=80, max_depth=2, random_state=SEED, n_jobs=1))])),
    17: ("PCA3_ET_G_d4", F_G, lambda: Pipeline([("pca", PCA(n_components=3, random_state=SEED)), ("et", ExtraTreesClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    18: ("PCA2_RF_H_d3", F_H, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    19: ("PCA5_RF_K_d5", F_K, lambda: Pipeline([("pca", PCA(n_components=5, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=150, max_depth=5, random_state=SEED, n_jobs=1))])),
    20: ("PCA1_ET_K_d3", F_K, lambda: Pipeline([("pca", PCA(n_components=1, random_state=SEED)), ("et", ExtraTreesClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    21: ("PCA2_RF_C_d3", F_C, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    22: ("PCA3_RF_I_d4", F_I, lambda: Pipeline([("pca", PCA(n_components=3, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    23: ("PCA2_ET_J_d2", F_J, lambda: Pipeline([("pca", PCA(n_components=2, random_state=SEED)), ("et", ExtraTreesClassifier(n_estimators=80, max_depth=2, random_state=SEED, n_jobs=1))])),
    24: ("PCA4_RF_K_d6", F_K, lambda: Pipeline([("pca", PCA(n_components=4, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=120, max_depth=6, random_state=SEED, n_jobs=1))])),

    # KMeans (distance aux centroides) + LogisticRegression - regimes discrets (25-34)
    25: ("KMeans3_Log_K", F_K, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=3, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    26: ("KMeans5_Log_K", F_K, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=5, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    27: ("KMeans4_Log_A", F_A, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=4, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    28: ("KMeans3_Log_G", F_G, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=3, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED))])),
    29: ("KMeans6_Log_K", F_K, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=6, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    30: ("KMeans4_Log_H", F_H, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=4, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    31: ("KMeans2_Log_D", F_D, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=2, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    32: ("KMeans5_Log_C", F_C, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=5, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED))])),
    33: ("KMeans3_Log_I", F_I, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=3, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))])),
    34: ("KMeans4_Log_K_C01", F_K, lambda: Pipeline([("sc", StandardScaler()), ("km", KMeans(n_clusters=4, random_state=SEED, n_init=10)), ("lr", LogisticRegression(C=0.1, max_iter=1000, random_state=SEED))])),

    # HistGradientBoosting avec contraintes monotones - priors financiers (35-42)
    35: ("HistGB_mono_A", F_A, lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.05, monotonic_cst=mono_cst(F_A), random_state=SEED)),
    36: ("HistGB_mono_B", F_B, lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.05, monotonic_cst=mono_cst(F_B), random_state=SEED)),
    37: ("HistGB_mono_G", F_G, lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=120, learning_rate=0.03, monotonic_cst=mono_cst(F_G), random_state=SEED)),
    38: ("HistGB_mono_H", F_H, lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.08, monotonic_cst=mono_cst(F_H), random_state=SEED)),
    39: ("HistGB_mono_I", F_I, lambda: HistGradientBoostingClassifier(max_depth=4, max_iter=150, learning_rate=0.02, monotonic_cst=mono_cst(F_I), random_state=SEED)),
    40: ("HistGB_mono_K", F_K, lambda: HistGradientBoostingClassifier(max_depth=5, max_iter=100, learning_rate=0.05, monotonic_cst=mono_cst(F_K), random_state=SEED)),
    41: ("HistGB_mono_D", F_D, lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=80, learning_rate=0.1, monotonic_cst=mono_cst(F_D), random_state=SEED)),
    42: ("HistGB_mono_J", F_J, lambda: HistGradientBoostingClassifier(max_depth=2, max_iter=150, learning_rate=0.05, monotonic_cst=mono_cst(F_J), random_state=SEED)),

    # MinMaxScaler + ComplementNB/MultinomialNB - NB sur features non-negatives (43-50)
    43: ("MinMax_ComplementNB_A", F_A, lambda: Pipeline([("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    44: ("MinMax_MultinomialNB_A", F_A, lambda: Pipeline([("mm", MinMaxScaler()), ("nb", MultinomialNB())])),
    45: ("MinMax_ComplementNB_B", F_B, lambda: Pipeline([("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    46: ("MinMax_MultinomialNB_C", F_C, lambda: Pipeline([("mm", MinMaxScaler()), ("nb", MultinomialNB())])),
    47: ("MinMax_ComplementNB_G", F_G, lambda: Pipeline([("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    48: ("MinMax_MultinomialNB_H", F_H, lambda: Pipeline([("mm", MinMaxScaler()), ("nb", MultinomialNB())])),
    49: ("MinMax_ComplementNB_K", F_K, lambda: Pipeline([("mm", MinMaxScaler()), ("nb", ComplementNB())])),
    50: ("MinMax_MultinomialNB_K", F_K, lambda: Pipeline([("mm", MinMaxScaler()), ("nb", MultinomialNB())])),
}
