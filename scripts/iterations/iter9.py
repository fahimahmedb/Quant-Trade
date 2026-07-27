"""
Itération 9 — 50 nouvelles hypothèses (univers figé a priori).

Après 6 itérations de familles de classifieurs et 2 de prétraitement/
contraintes, itération 9 explore des COMBINAISONS STRUCTURELLES pas encore
essayées :

1. Bagging(LogisticRegression) : ensemble de régressions logistiques —
   réduit la variance d'un modèle linéaire par agrégation bootstrap
   (jamais combiné jusqu'ici). (NB : Bagging(MLPClassifier) a été testé et
   écarté — BaggingClassifier transmet le bootstrap via sample_weight à
   MLPClassifier, dont le SGD par mini-lots peut tomber de façon
   déterministe sur un lot à poids tous nuls avec ce seed, provoquant un
   ZeroDivisionError systématique à chaque fenêtre walk-forward.)
2. Bagging(KNeighborsClassifier) : ensemble de KNN — réduit la variance
   inhérente au KNN sur de petits échantillons de features financières.
3. StackingClassifier(passthrough=True) : variante structurelle du
   stacking d'iter5 — le méta-modèle voit à la fois les prédictions des
   modèles de base ET les features brutes originales (au lieu des seules
   prédictions), hypothèse différente de la combinaison de signaux.
4. HistGradientBoostingClassifier avec balayage de max_leaf_nodes et
   l2_regularization — hyperparamètres structurels jamais variés
   systématiquement dans les itérations précédentes (seuls depth/iter/lr
   avaient été balayés).
5. VotingClassifier(soft) à comité plus large (4-5 membres hétérogènes
   au lieu de 2-3 dans iter5) — teste si la diversité d'un plus grand
   comité aide.

(NB : VotingClassifier(voting="hard") a été testé/écarté : ni predict_proba
ni decision_function, incompatible avec CalibratedClassifierCV — pas de
variante hard-voting viable dans ce pipeline.)

Protocole inchangé (T0=750, refit=21j, embargo=21j, H=5j, barrière 1.5*sigma,
coûts 5bps, split design/test 2010-01-01).
"""
from sklearn.ensemble import BaggingClassifier, StackingClassifier, VotingClassifier, HistGradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

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

STRATEGIES = {
    # Bagging(LogisticRegression) - ensemble de modeles lineaires (1-12)
    1: ("Bagging_Log_C1_A", F_A, lambda: BaggingClassifier(estimator=LogisticRegression(C=1.0, max_iter=1000, random_state=SEED), n_estimators=10, random_state=SEED, n_jobs=1)),
    2: ("Bagging_Log_C05_B", F_B, lambda: BaggingClassifier(estimator=LogisticRegression(C=0.5, max_iter=1000, random_state=SEED), n_estimators=10, random_state=SEED, n_jobs=1)),
    3: ("Bagging_Log_C1_C_ms08", F_C, lambda: BaggingClassifier(estimator=LogisticRegression(C=1.0, max_iter=1000, random_state=SEED), n_estimators=12, max_samples=0.8, random_state=SEED, n_jobs=1)),
    4: ("Bagging_Log_C10_D", F_D, lambda: BaggingClassifier(estimator=LogisticRegression(C=10.0, max_iter=1000, random_state=SEED), n_estimators=10, random_state=SEED, n_jobs=1)),
    5: ("Bagging_Log_C02_E", F_E, lambda: BaggingClassifier(estimator=LogisticRegression(C=0.2, max_iter=1000, random_state=SEED), n_estimators=10, random_state=SEED, n_jobs=1)),
    6: ("Bagging_Log_C1_G", F_G, lambda: BaggingClassifier(estimator=LogisticRegression(C=1.0, max_iter=1000, random_state=SEED), n_estimators=15, random_state=SEED, n_jobs=1)),
    7: ("Bagging_Log_C5_H", F_H, lambda: BaggingClassifier(estimator=LogisticRegression(C=5.0, max_iter=1000, random_state=SEED), n_estimators=10, random_state=SEED, n_jobs=1)),
    8: ("Bagging_Log_C1_I_mf07", F_I, lambda: BaggingClassifier(estimator=LogisticRegression(C=1.0, max_iter=1000, random_state=SEED), n_estimators=10, max_features=0.7, random_state=SEED, n_jobs=1)),
    9: ("Bagging_Log_C02_K", F_K, lambda: BaggingClassifier(estimator=LogisticRegression(C=0.2, max_iter=1000, random_state=SEED), n_estimators=10, random_state=SEED, n_jobs=1)),
    10: ("Bagging_Log_C1_J", F_J, lambda: BaggingClassifier(estimator=LogisticRegression(C=1.0, max_iter=1000, random_state=SEED), n_estimators=10, random_state=SEED, n_jobs=1)),
    11: ("Bagging_Log_C50_F", F_F, lambda: BaggingClassifier(estimator=LogisticRegression(C=50.0, max_iter=1000, random_state=SEED), n_estimators=10, random_state=SEED, n_jobs=1)),
    12: ("Bagging_Log_C1_K_ms07", F_K, lambda: BaggingClassifier(estimator=LogisticRegression(C=1.0, max_iter=1000, random_state=SEED), n_estimators=12, max_samples=0.7, random_state=SEED, n_jobs=1)),

    # Bagging(KNeighborsClassifier) - reduit la variance du KNN (13-22)
    13: ("Bagging_KNN5_A", F_A, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=5, n_jobs=1), n_estimators=10, random_state=SEED, n_jobs=1)),
    14: ("Bagging_KNN10_B", F_B, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), n_estimators=10, random_state=SEED, n_jobs=1)),
    15: ("Bagging_KNN15_C_ms07", F_C, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=15, n_jobs=1), n_estimators=10, max_samples=0.7, random_state=SEED, n_jobs=1)),
    16: ("Bagging_KNN5_D", F_D, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=5, n_jobs=1), n_estimators=15, random_state=SEED, n_jobs=1)),
    17: ("Bagging_KNN20_G", F_G, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=20, n_jobs=1), n_estimators=10, random_state=SEED, n_jobs=1)),
    18: ("Bagging_KNN10_H", F_H, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), n_estimators=10, random_state=SEED, n_jobs=1)),
    19: ("Bagging_KNN30_K", F_K, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=30, n_jobs=1), n_estimators=10, random_state=SEED, n_jobs=1)),
    20: ("Bagging_KNN5_I", F_I, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=5, n_jobs=1), n_estimators=12, random_state=SEED, n_jobs=1)),
    21: ("Bagging_KNN10_J", F_J, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=10, n_jobs=1), n_estimators=10, random_state=SEED, n_jobs=1)),
    22: ("Bagging_KNN15_F", F_F, lambda: BaggingClassifier(estimator=KNeighborsClassifier(n_neighbors=15, n_jobs=1), n_estimators=10, random_state=SEED, n_jobs=1)),

    # StackingClassifier(passthrough=True) - meta-modele voit aussi les features brutes (23-32)
    23: ("StackPass_Log_NB_A", F_A, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    24: ("StackPass_RF_Log_B", F_B, lambda: StackingClassifier(estimators=[("rf", RandomForestClassifier(n_estimators=60, max_depth=4, random_state=SEED, n_jobs=1)), ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    25: ("StackPass_3base_D", F_D, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED))], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    26: ("StackPass_ET_NB_G", F_G, lambda: StackingClassifier(estimators=[("et", ExtraTreesClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    27: ("StackPass_3base_H", F_H, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("dt", DecisionTreeClassifier(max_depth=5, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    28: ("StackPass_LDA_RF_I", F_I, lambda: StackingClassifier(estimators=[("lda", LinearDiscriminantAnalysis()), ("rf", RandomForestClassifier(n_estimators=60, max_depth=4, random_state=SEED, n_jobs=1))], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    29: ("StackPass_3base_J", F_J, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("rf", RandomForestClassifier(n_estimators=50, max_depth=6, random_state=SEED, n_jobs=1))], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    30: ("StackPass_RF_NB_K", F_K, lambda: StackingClassifier(estimators=[("rf", RandomForestClassifier(n_estimators=80, max_depth=5, random_state=SEED, n_jobs=1)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    31: ("StackPass_3base_E", F_E, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=3, random_state=SEED))], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),
    32: ("StackPass_3base_F", F_F, lambda: StackingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)), ("nb", GaussianNB())], final_estimator=LogisticRegression(max_iter=1000, random_state=SEED), passthrough=True, cv=3, n_jobs=1)),

    # HistGradientBoosting - balayage max_leaf_nodes/l2_regularization (33-42)
    33: ("HistGB_leaves8_l2_0", F_A, lambda: HistGradientBoostingClassifier(max_leaf_nodes=8, l2_regularization=0.0, max_iter=100, learning_rate=0.05, random_state=SEED)),
    34: ("HistGB_leaves15_l2_2", F_B, lambda: HistGradientBoostingClassifier(max_leaf_nodes=15, l2_regularization=2.0, max_iter=100, learning_rate=0.05, random_state=SEED)),
    35: ("HistGB_leaves31_l2_5", F_C, lambda: HistGradientBoostingClassifier(max_leaf_nodes=31, l2_regularization=5.0, max_iter=100, learning_rate=0.03, random_state=SEED)),
    36: ("HistGB_leaves4_l2_1", F_D, lambda: HistGradientBoostingClassifier(max_leaf_nodes=4, l2_regularization=1.0, max_iter=150, learning_rate=0.05, random_state=SEED)),
    37: ("HistGB_leaves63_l2_10", F_G, lambda: HistGradientBoostingClassifier(max_leaf_nodes=63, l2_regularization=10.0, max_iter=80, learning_rate=0.05, random_state=SEED)),
    38: ("HistGB_leaves10_l2_05", F_H, lambda: HistGradientBoostingClassifier(max_leaf_nodes=10, l2_regularization=0.5, max_iter=120, learning_rate=0.05, random_state=SEED)),
    39: ("HistGB_leaves20_l2_3", F_I, lambda: HistGradientBoostingClassifier(max_leaf_nodes=20, l2_regularization=3.0, max_iter=100, learning_rate=0.05, random_state=SEED)),
    40: ("HistGB_leaves6_l2_15", F_J, lambda: HistGradientBoostingClassifier(max_leaf_nodes=6, l2_regularization=1.5, max_iter=100, learning_rate=0.08, random_state=SEED)),
    41: ("HistGB_leaves31_l2_0", F_K, lambda: HistGradientBoostingClassifier(max_leaf_nodes=31, l2_regularization=0.0, max_iter=100, learning_rate=0.03, random_state=SEED)),
    42: ("HistGB_leaves12_l2_4", F_E, lambda: HistGradientBoostingClassifier(max_leaf_nodes=12, l2_regularization=4.0, max_iter=100, learning_rate=0.05, random_state=SEED)),

    # VotingClassifier(soft) a comite plus large (4-5 membres) (43-50)
    43: ("Voting5_A", F_A, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1)), ("lda", LinearDiscriminantAnalysis())], voting="soft", n_jobs=1)),
    44: ("Voting4_B", F_B, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("rf", RandomForestClassifier(n_estimators=60, max_depth=4, random_state=SEED, n_jobs=1)), ("dt", DecisionTreeClassifier(max_depth=3, random_state=SEED))], voting="soft", n_jobs=1)),
    45: ("Voting5_weighted_D", F_D, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1)), ("lda", LinearDiscriminantAnalysis())], voting="soft", weights=[2, 1, 1, 2, 1], n_jobs=1)),
    46: ("Voting4_G", F_G, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=0.5, max_iter=1000, random_state=SEED)), ("et", ExtraTreesClassifier(n_estimators=60, max_depth=3, random_state=SEED, n_jobs=1)), ("nb", GaussianNB()), ("lda", LinearDiscriminantAnalysis())], voting="soft", n_jobs=1)),
    47: ("Voting5_H", F_H, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=5, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=50, max_depth=4, random_state=SEED, n_jobs=1)), ("lda", LinearDiscriminantAnalysis())], voting="soft", n_jobs=1)),
    48: ("Voting4_K", F_K, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("rf", RandomForestClassifier(n_estimators=80, max_depth=5, random_state=SEED, n_jobs=1)), ("lda", LinearDiscriminantAnalysis())], voting="soft", n_jobs=1)),
    49: ("Voting5_J", F_J, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=3, random_state=SEED)), ("rf", RandomForestClassifier(n_estimators=50, max_depth=3, random_state=SEED, n_jobs=1)), ("lda", LinearDiscriminantAnalysis())], voting="soft", n_jobs=1)),
    50: ("Voting4_F", F_F, lambda: VotingClassifier(estimators=[("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)), ("nb", GaussianNB()), ("dt", DecisionTreeClassifier(max_depth=4, random_state=SEED)), ("lda", LinearDiscriminantAnalysis())], voting="soft", n_jobs=1)),
}
