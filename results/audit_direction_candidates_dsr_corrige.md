# Audit — DSR corrigé des candidats de direction cross-validés

n_trials utilisé = **1200** (taille réelle de la campagne de brute-force, voir `results/campaign_trial_variance.json` pour la provenance et les limites). var_trials (Sharpe quotidien, non annualisé) = **0.000390**, estimée sur 349/1200 essais dont les données brutes existent encore (iter4–10 ; iter11–27 ont perdu leurs fichiers individuels, gitignorés et éphémères — **proxy partiel, pas la population complète**, signalé et non masqué).

Les 20 candidats ci-dessous sont **TOUS** ceux déjà logués dans `cross_market_confirmations.md` (aucune sélection post-hoc pour ce rapport) — y compris ceux qui répliquent mal.

| Itération/id | Modèle | Russell DSR corr. | S&P500 DSR corr. | DAX DSR corr. | 3/3 > 0.95 ? |
|---|---|---|---|---|---|
| 3/31 | RF_d3_n200 | 0.000 | 0.000 | 0.000 | non |
| 8/8 | QuantNormal_Log_H_C1 | 0.000 | 0.000 | 0.000 | non |
| 8/30 | KMeans4_Log_H | 0.000 | 0.001 | 0.000 | non |
| 10/11 | AdaBoost_NB_A | 0.000 | 0.000 | 0.000 | non |
| 11/37 | VotingRadius_H | 0.000 | 0.000 | 0.000 | non |
| 12/25 | FeatAgg_RF_E | 0.000 | 0.000 | 0.000 | non |
| 15/5 | AdaBoost_ExtraTree_E_lr05 | 0.000 | 0.000 | 0.001 | non |
| 16/45 | QDA_reg_E_01 | 0.000 | 0.000 | 0.000 | non |
| 20/5 | Spline_Log_E | 0.000 | 0.000 | 0.000 | non |
| 20/10 | Spline_Log_J_k4 | 0.000 | 0.000 | 0.000 | non |
| 20/12 | Spline_Log_wide_K_k4 | 0.000 | 0.000 | 0.000 | non |
| 21/30 | Spline_HistGB_wide_K | 0.000 | 0.000 | 0.000 | non |
| 21/6 | Bagging_SplineLog_J | 0.000 | 0.000 | 0.000 | non |
| 21/1 | Bagging_SplineLog_A | 0.000 | 0.000 | 0.000 | non |
| 21/19 | VotingSpline_RF_NB_wide_K | 0.000 | 0.000 | 0.000 | non |
| 21/45 | RobustScaler_Spline_Log_E | 0.000 | 0.000 | 0.000 | non |
| 21/50 | RobustScaler_Spline_Log_wide_K | 0.000 | 0.000 | 0.000 | non |
| 25/50 | Spline_MLP_wide_K | 0.000 | 0.000 | 0.000 | non |
| 26/49 | RF_newfeat_T | 0.000 | 0.000 | 0.000 | non |
| 26/41 | RF_newfeat_L | 0.000 | 0.000 | 0.000 | non |

**0/20 candidats atteignent DSR corrigé > 0.95 simultanément sur les 3 marchés externes.**

**Lecture honnête** : le DSR corrigé ici utilise n_trials=1200 (la charge réelle de la campagne, pas la famille locale de 50 utilisée dans le log original) — c'est beaucoup plus sévère, et c'est le bon calcul (même erreur de raisonnement que celle déjà trouvée et corrigée pour l'overlay Étape D, cf. ADVERSARIAL_AUDIT_v2.md §1). Un DSR élevé ici signifierait qu'un signal a un Sharpe net-de-coûts sur un marché totalement externe qui est *statistiquement surprenant même après avoir payé le prix de 1200 tentatives* — c'est une barre volontairement très haute. Limite assumée : var_trials est estimée sur seulement 349/1200 essais (les fichiers bruts des itérations 11–27 ont été perdus, gitignorés et éphémères) — un vrai calcul définitif nécessiterait de relancer la campagne en conservant cette fois un résumé léger (Sharpe seul, pas les modèles) pour CHAQUE essai, committé, pas gitignoré.
