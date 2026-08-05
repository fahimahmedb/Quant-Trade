# Analyse informative — Sharpe Buy&Hold et taux de succès dans la lignée d'estimateurs/portes #215-243

Périmètre : 16 cycles homogènes (garman_klass, gap_risk, variance_ratio, skewness, kurtosis, vol_of_vol, rogers_satchell, yang_zhang, arch_clustering, ewma, atr, har, student_t_tail, parkinson_c2c_ratio, kurtosis_nu_combined, ljung_box_clustering), #234 exclu (NDX seul, non comparable). PAS un backtest — agrège des résultats déjà committés.

| Marché | Sharpe BH ann. (#245) | PASS (deux jambes) / total | Taux de succès |
|---|---|---|---|
| Composite (5 ans) | +0.52 | 9/16 | 56.2% |
| NDX (40 ans) | +0.53 | 15/16 | 93.8% |
| Russell 2000 | +0.34 | 12/16 | 75.0% |
| S&P 500 | +0.45 | 14/16 | 87.5% |
| DAX | +0.25 | 8/16 | 50.0% |

**Corrélation de Spearman (Sharpe BH vs taux de succès, n=5 marchés) : ρ = +0.700, p = 0.188.**

## Détail par cycle et par marché (PASS = Sharpe>BH ET Rdt>BH)

| Cycle | Composite | NDX | Russell | S&P | DAX |
|---|---|---|---|---|---|
| garman_klass | OUI | OUI | OUI | OUI | OUI |
| gap_risk | non | OUI | non | OUI | non |
| variance_ratio | OUI | OUI | OUI | OUI | non |
| skewness | non | OUI | OUI | OUI | non |
| kurtosis | OUI | OUI | OUI | OUI | non |
| vol_of_vol | OUI | OUI | non | OUI | OUI |
| rogers_satchell | OUI | OUI | OUI | OUI | OUI |
| yang_zhang | OUI | OUI | OUI | OUI | OUI |
| arch_clustering | non | OUI | OUI | OUI | OUI |
| ewma | non | OUI | OUI | OUI | OUI |
| atr | non | non | OUI | OUI | OUI |
| har | non | OUI | non | non | OUI |
| student_t_tail | OUI | OUI | OUI | OUI | non |
| parkinson_c2c_ratio | non | OUI | non | non | non |
| kurtosis_nu_combined | OUI | OUI | OUI | OUI | non |
| ljung_box_clustering | OUI | OUI | OUI | OUI | non |

**Lecture honnête** : ρ=+0,7 (n=5, non significatif au sens strict avec un si petit échantillon, p à interpréter avec prudence) indique une association positive mais IMPARFAITE — NDX (Sharpe le plus élevé) et DAX (le plus faible) occupent bien les positions extrêmes dans les deux classements, cohérent avec l'hypothèse du #245, mais Composite (2e Sharpe le plus élevé) est un contre-exemple net (4e taux de succès sur 5) — plausiblement confondu par sa taille d'échantillon nettement plus courte (~1230 séances contre 6756-14231 pour les 4 autres marchés), qui a explicitement fait échouer plusieurs candidats de justesse (une seule jambe manquée : EWMA, ATR) ou nettement (HAR, échantillon le plus court après restriction du walk-forward). **Conclusion honnête** : l'hypothèse de travail du #245 (drift plus faible = ratio gain/coût moins favorable) est PARTIELLEMENT généralisée par cette analyse à plus grande échelle — elle explique probablement les deux extrêmes (NDX/DAX) mais pas la totalité du classement, où la taille d'échantillon semble être un facteur confondant au moins aussi important pour Composite spécifiquement.
