# Quant-Trade — Prime de risque de variance NASDAQ-100

Moteur de prévision de volatilité + stratégie short-variance conditionnelle,
validés en walk-forward hors échantillon (2004→2026). Résultats détaillés et
limites : [`reports/RESULTS.md`](reports/RESULTS.md).

## Pipeline

```
scripts/01_qc_data.py              # QC croisé des sources, assemblage master.parquet
scripts/02_vrp_diagnostics.py      # la prime existe-t-elle ? (VRP inconditionnelle)
scripts/03_vol_forecast.py         # 8 modèles de vol, walk-forward, QLIKE + DM (~1 min)
scripts/04_vrp_strategy.py         # stratégies conditionnelles vs benchmark
scripts/05_ablation.py             # le modèle paie-t-il, ou juste la règle ? + bootstrap
scripts/06_risk_calibration.py     # PIT/Kupiec/Christoffersen — v1 (rejetée)
scripts/06b_risk_calibration_skewt.py  # v2 skew-t Hansen (calibrée)
scripts/07_options_replication.py  # réplique tradeable: straddle ATM delta-hedgé
scripts/08_validation_straddle.py  # DSR, bootstrap, filtre tendance (échec compté)
```

Exécution dans l'ordre ; les scripts écrivent leurs sorties intermédiaires
dans `data/*.parquet`. Dépendances : `numpy pandas scipy statsmodels arch pyarrow`.

## Données

`data/` contient les CSV bruts (Yahoo, CBOE, FRED) téléchargés le 2026-07-13,
committés pour reproductibilité. Re-téléchargement : voir les URLs dans
`scripts/01_qc_data.py` et l'historique du dépôt.

## Résumé des chiffres (hors échantillon, net de 0,5 pt de vol de coûts)

- Prime de variance NASDAQ-100 : +158 pts de variance, t Newey-West = 4,6.
- Vol 21j : HAR-X bat GARCH(1,1), QLIKE 0,238 vs 0,271, DM = −4,04 (p<0,001).
- Swap de variance idéalisé, sizing `prop` : Sharpe 0,58 vs 0,36, DSR 0,77 (< 0,95).
- **Réplique tradeable (straddle ATM delta-hedgé, sizing `prop`) : Sharpe 0,78,
  pire mois −7,2 pts de vol, DSR(N=13) = 0,967 ✓** — le straddle ne vend pas
  les ailes, son gamma s'éteint loin du strike (pire mois −53 vs −187 en uncond).
- Moteur de risque skew-t : PIT calibré (KS p=0,28), VaR 5 %/1 % non rejetées.
- Reste à faire avant paper-trading : valider sur chaînes d'options réelles
  (ici marks Black-Scholes, IV ≈ VXN×0,95).
