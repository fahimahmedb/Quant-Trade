"""
Itération 11 — 50 nouvelles hypothèses (univers figé a priori).

Après 8 itérations de familles/combinaisons de classifieurs et de
prétraitement, itération 11 explore :

1. StackingClassifier avec RandomForest comme méta-modèle final (au lieu
   de LogisticRegression dans toutes les itérations précédentes) — méta-
   apprentissage non linéaire des prédictions des modèles de base.
2. VotingClassifier(soft) incluant KNeighborsClassifier comme membre —
   jamais inclus dans un comité de vote jusqu'ici.
3. Pipeline(PolynomialFeatures degré 2 + RandomForest) — features
   quadratiques/interactions analysées par un modèle non linéaire, jamais
   combiné (iter7 avait testé poly+LogReg uniquement).
4. VotingClassifier(soft) incluant RadiusNeighborsClassifier — comité
   avec un membre géométrique à rayon fixe.
5. Pipeline(QuantileTransformer + RandomForest) — normalisation par rang
   suivie d'un classifieur non linéaire, jamais combiné (iter8 avait
   testé QuantileTransformer+LogReg uniquement).

(NB : deux idées testées et écartées avant lancement — Bagging(MLP,
solver='lbfgs') pour contourner le bug de l'itération 9 : lbfgs ne
converge pas en un temps raisonnable ici. AdaBoost(QDA) : QDA ne
supporte pas sample_weight, erreur immédiate. Bagging(RandomForest/
ExtraTrees) : plus de 150s sans terminer une seule fenêtre walk-forward
sur la variante la plus légère — trop coûteux, cumul de deux ensembles.)

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.ensemble import StackingClassifier, VotingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import PolynomialFeatures, QuantileTransformer
from sklearn.pipeline import Pipeline

SEED = 42

F_A = ["mom_10", "vol_20", "rsi_14"]
F_B = ["mom_10", "vol_ratio", "atr_rel", "mom_20"]
F_C = ["mom_20", "ma_ratio_50", "vol_10", "stoch_k"]
F_D = ["drawdown_60", "vol_20", "rsi_14", "fracdiff_04"]
F_E = ["fracdiff_04", "mom_10", "vol_10"]
F_G = ["mom_10", "mom_20", "vol_20", "atr_rel", "stoch_k"]
F_H = ["ret_1", "ret_2", "ret_3", "drawdown_60", "vol_10"]
F_I = ["parkinson_5", "mom_10", "vol_20", "rsi_14", "macd_rel"]
F_J = ["ret_5", "ret_10", "ma_ratio_20", "bb_pctb"]
F_K = ["mom_10", "mom_20", "vol_10", "vol_20", "rsi_14", "macd_rel", "bb_pctb", "atr_rel", "stoch_k"]

STRATEGIES = {
    # StackingClassifier avec meta-modele RandomForest (1-10)
    1: ("StackRF_Log_NB_A", F_A, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    2: ("StackRF_3base_B", F_B, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED))], final_estimator=RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    3: ("StackRF_ET_NB_C", F_C, lambda: StackingClassifier(estimators=[("et", ExtraTreesClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], final_estimator=RandomForestClassifier(n_estimators=40, max_depth=4, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    4: ("StackRF_3base_D", F_D, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("dt", DecisionTreeClassifier(max_depth=5, random_state=SEED)), ("nb", GaussianNB())], final_estimator=RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    5: ("StackRF_LDA_E", F_E, lambda: StackingClassifier(estimators=[("lda", LinearDiscriminantAnalysis()), ("nb", GaussianNB())], final_estimator=RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    6: ("StackRF_3base_G", F_G, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=3, random_state=SEED))], final_estimator=RandomForestClassifier(n_estimators=60, max_depth=4, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    7: ("StackRF_H", F_H, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    8: ("StackRF_I", F_I, lambda: StackingClassifier(estimators=[("et", ExtraTreesClassifier(n_estimators=50, max_depth=4, random_state=SEED, n_jobs=1)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))], final_estimator=RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    9: ("StackRF_J", F_J, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=RandomForestClassifier(n_estimators=40, max_depth=5, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),
    10: ("StackRF_wide_K", F_K, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED))], final_estimator=RandomForestClassifier(n_estimators=60, max_depth=4, random_state=SEED, n_jobs=1), cv=3, n_jobs=1)),

    # VotingClassifier(soft) avec KNeighbors membre (11-20)
    11: ("VotingKNN_Log_A", F_A, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))], voting="soft", n_jobs=1)),
    12: ("VotingKNN_NB_B", F_B, lambda: VotingClassifier(estimators=[("nb", GaussianNB()), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))], voting="soft", n_jobs=1)),
    13: ("VotingKNN_3way_C", F_C, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))], voting="soft", n_jobs=1)),
    14: ("VotingKNN_RF_D", F_D, lambda: VotingClassifier(estimators=[("rf", RandomForestClassifier(n_estimators=60, max_depth=4, random_state=SEED, n_jobs=1)), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))], voting="soft", n_jobs=1)),
    15: ("VotingKNN_weighted_E", F_E, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))], voting="soft", weights=[2, 1], n_jobs=1)),
    16: ("VotingKNN_3way_G", F_G, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))], voting="soft", n_jobs=1)),
    17: ("VotingKNN_H", F_H, lambda: VotingClassifier(estimators=[("nb", GaussianNB()), ("knn", KNeighborsClassifier(n_neighbors=5, n_jobs=1))], voting="soft", n_jobs=1)),
    18: ("VotingKNN_3way_I", F_I, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("knn", KNeighborsClassifier(n_neighbors=20, n_jobs=1))], voting="soft", n_jobs=1)),
    19: ("VotingKNN_J", F_J, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=10, n_jobs=1))], voting="soft", n_jobs=1)),
    20: ("VotingKNN_wide_K", F_K, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("knn", KNeighborsClassifier(n_neighbors=15, n_jobs=1))], voting="soft", n_jobs=1)),

    # Pipeline(PolynomialFeatures degre 2 + RandomForest) (21-30)
    21: ("Poly2_RF_A", F_A, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    22: ("Poly2_RF_B_d4", F_B, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    23: ("Poly2_interact_RF_C", F_C, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    24: ("Poly2_RF_D_d5", F_D, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("rf", RandomForestClassifier(n_estimators=120, max_depth=5, random_state=SEED, n_jobs=1))])),
    25: ("Poly2_RF_E", F_E, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("rf", RandomForestClassifier(n_estimators=80, max_depth=3, random_state=SEED, n_jobs=1))])),
    26: ("Poly2_interact_RF_G", F_G, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    27: ("Poly2_RF_H", F_H, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    28: ("Poly2_RF_I_d6", F_I, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=6, random_state=SEED, n_jobs=1))])),
    29: ("Poly2_interact_RF_J", F_J, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)), ("rf", RandomForestClassifier(n_estimators=80, max_depth=3, random_state=SEED, n_jobs=1))])),
    30: ("Poly2_RF_wide_K", F_K, lambda: Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),

    # VotingClassifier(soft) avec RadiusNeighbors membre (31-40)
    31: ("VotingRadius_Log_A", F_A, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("rn", RadiusNeighborsClassifier(radius=1.5, outlier_label=0))], voting="soft", n_jobs=1)),
    32: ("VotingRadius_NB_B", F_B, lambda: VotingClassifier(estimators=[("nb", GaussianNB()), ("rn", RadiusNeighborsClassifier(radius=1.0, outlier_label=0))], voting="soft", n_jobs=1)),
    33: ("VotingRadius_3way_C", F_C, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("rn", RadiusNeighborsClassifier(radius=2.0, outlier_label=0))], voting="soft", n_jobs=1)),
    34: ("VotingRadius_D", F_D, lambda: VotingClassifier(estimators=[("rf", RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1)), ("rn", RadiusNeighborsClassifier(radius=1.2, outlier_label=0))], voting="soft", n_jobs=1)),
    35: ("VotingRadius_E", F_E, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("rn", RadiusNeighborsClassifier(radius=1.0, outlier_label=0))], voting="soft", n_jobs=1)),
    36: ("VotingRadius_3way_G", F_G, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)), ("rn", RadiusNeighborsClassifier(radius=2.0, outlier_label=0))], voting="soft", n_jobs=1)),
    37: ("VotingRadius_H", F_H, lambda: VotingClassifier(estimators=[("nb", GaussianNB()), ("rn", RadiusNeighborsClassifier(radius=1.0, outlier_label=0))], voting="soft", n_jobs=1)),
    38: ("VotingRadius_3way_I", F_I, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("rn", RadiusNeighborsClassifier(radius=2.5, outlier_label=0))], voting="soft", n_jobs=1)),
    39: ("VotingRadius_J", F_J, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)), ("rn", RadiusNeighborsClassifier(radius=1.5, outlier_label=0))], voting="soft", n_jobs=1)),
    40: ("VotingRadius_wide_K", F_K, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("rn", RadiusNeighborsClassifier(radius=2.0, outlier_label=0))], voting="soft", n_jobs=1)),

    # Pipeline(QuantileTransformer + RandomForest/ExtraTrees) (41-50)
    41: ("QuantUniform_RF_A", F_A, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    42: ("QuantNormal_ET_B", F_B, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("et", ExtraTreesClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    43: ("QuantUniform_RF_C_d4", F_C, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    44: ("QuantNormal_RF_D", F_D, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=80, max_depth=3, random_state=SEED, n_jobs=1))])),
    45: ("QuantUniform_ET_E", F_E, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("et", ExtraTreesClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
    46: ("QuantNormal_RF_G", F_G, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    47: ("QuantUniform_RF_H", F_H, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=5, random_state=SEED, n_jobs=1))])),
    48: ("QuantNormal_ET_I", F_I, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("et", ExtraTreesClassifier(n_estimators=80, max_depth=3, random_state=SEED, n_jobs=1))])),
    49: ("QuantUniform_RF_J", F_J, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="uniform", n_quantiles=200, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=3, random_state=SEED, n_jobs=1))])),
    50: ("QuantNormal_RF_wide_K", F_K, lambda: Pipeline([("qt", QuantileTransformer(output_distribution="normal", n_quantiles=200, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=SEED, n_jobs=1))])),
}
