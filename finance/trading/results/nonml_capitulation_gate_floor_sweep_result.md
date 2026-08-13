# Balayage des portes de capitulation neutralisées par le plancher 1,0× (pré-enregistré)

Diagnostic, pas une stratégie. Cherche les candidats dont la structure interdit
à l'overlay de s'activer : une porte qui s'ouvre en régime de faiblesse combinée
à un vol-targeting dont le plancher est l'exposition neutre.

Seuil d'inactivité **repris tel quel du #410** : exposition > 1,0× sur moins de 2 % des séances.

## Volet A — détection statique

- scripts `nonml_*_backtest.py` examinés : **282**
- illisibles : **0**
- portant la structure `clip(…, 1.0, …)` : **62**

**Couverture 100 %** — critère 1 du pré-enregistrement atteint.

## Volet B — mesure empirique de l'activation

- candidats mesurés (`.npz` au schéma `pos` disponible) : **42**
- candidats détectés mais **non mesurés** faute de `.npz` : **20**

Ce second chiffre est un **résultat du cycle**, pas une excuse : il quantifie
exactement ce que la lacune mesurée au #406 coûte à ce diagnostic.

Non mesurés :

- `acf_lag1_vol_targeting_overlay` (verdict au rapport : FAIL)
- `beta_dispersion_vol_targeting_overlay` (verdict au rapport : FAIL)
- `bollinger_width_vol_targeting_overlay` (verdict au rapport : FAIL)
- `correlation_regime_vol_targeting_overlay` (verdict au rapport : FAIL)
- `daily_advance_breadth_vol_targeting_overlay` (verdict au rapport : FAIL)
- `drawdown_depth_vol_targeting_overlay` (verdict au rapport : FAIL)
- `gap_risk_vol_targeting_overlay` (verdict au rapport : FAIL)
- `goldencross_vol_targeting_overlay` (verdict au rapport : FAIL)
- `internal_breadth_vol_targeting_overlay` (verdict au rapport : FAIL)
- `lowvol_regime_vol_targeting_overlay` (verdict au rapport : FAIL)
- `lowvol_trend_vol_targeting_overlay` (verdict au rapport : FAIL)
- `momentum_consistency_trend_vol_targeting_15_overlay` (verdict au rapport : FAIL)
- `momentum_consistency_trend_vol_targeting_overlay` (verdict au rapport : FAIL)
- `parkinson_c2c_ratio_vol_targeting_overlay` (verdict au rapport : FAIL)
- `rebound_speed_breadth_vol_targeting_overlay` (verdict au rapport : FAIL)
- `skewness_vol_targeting_overlay` (verdict au rapport : FAIL)
- `trend_lowvol_vol_targeting_overlay` (verdict au rapport : FAIL)
- `vix_regime_vol_targeting_overlay` (verdict au rapport : FAIL)
- `winners_trend_vol_targeting_overlay` (verdict au rapport : PASS)
- `winners_trend_vol_targeting_overlay_pit_universe` (verdict au rapport : FAIL)

### Candidats mesurés, par activation croissante

| Candidat | Séances à exposition > 1,0× | Verdict au rapport |
|---|---|---|
| `weakness_breadth_vol_targeting_overlay` | 0.00 % ← **inactif** | PASS |
| `weakness_breadth_vol_targeting_overlay_pit_universe` | 0.00 % ← **inactif** | PASS |
| `santa_vol_targeting_overlay` | 1.70 % ← **inactif** | PASS |
| `variance_ratio_vol_targeting_overlay` | 19.57 % | PASS |
| `kurtosis_nu_combined_vol_targeting_overlay` | 21.29 % | PASS |
| `deep_drawdown_breadth_vol_targeting_overlay` | 21.52 % | PASS |
| `dispersion_trend_vol_targeting_overlay` | 22.38 % | PASS |
| `market_concentration_vol_targeting_overlay` | 23.32 % | PASS |
| `arch_clustering_vol_targeting_overlay` | 24.04 % | PASS |
| `dispersion_vol_targeting_overlay` | 24.77 % | PASS |
| `yield_curve_slope_vol_targeting_overlay` | 25.59 % | PASS |
| `range_position_vol_targeting_overlay` | 25.78 % | PASS |
| `deep_drawdown_breadth_vol_targeting_overlay_pit_universe` | 25.82 % | PASS |
| `student_t_tail_vol_targeting_overlay` | 25.89 % | PASS |
| `ljung_box_clustering_vol_targeting_overlay` | 27.63 % | PASS |
| `kurtosis_vol_targeting_overlay` | 27.80 % | PASS |
| `smallcap_proxy_outperformance_breadth_overlay` | 28.09 % | PASS |
| `dispersion_vol_targeting_overlay_pit_universe` | 28.92 % | FAIL |
| `breadth_vol_targeting_overlay` | 30.94 % | PASS |
| `vol_of_vol_vol_targeting_overlay` | 31.12 % | PASS |
| `momentum_dispersion_vol_targeting_overlay_pit_universe` | 32.06 % | PASS |
| `momentum_dispersion_trend_and_overlay` | 32.13 % | PASS |
| `momentum_decile_spread_vol_targeting_overlay_pit_universe` | 34.82 % | PASS |
| `smallcap_proxy_outperformance_breadth_overlay_pit_universe` | 36.07 % | PASS |
| `market_concentration_vol_targeting_overlay_pit_universe` | 36.41 % | PASS |
| `range_position_vol_targeting_overlay_pit_universe` | 36.82 % | FAIL |
| `momentum_dispersion_vol_targeting_overlay` | 36.97 % | PASS |
| `calendar_vol_targeting_overlay` | 37.55 % | PASS |
| `momentum_decile_spread_vol_targeting_overlay` | 37.98 % | PASS |
| `gjr_forecast_gate_vol_targeting_overlay` | 39.13 % | PASS |
| `ensemble_vote_vol_targeting_overlay` | 39.93 % | PASS |
| `january_barometer_vol_targeting_overlay` | 40.64 % | PASS |
| `trend_vol_targeting_overlay` | 42.05 % | PASS |
| `net_breadth_vol_targeting_overlay` | 44.40 % | PASS |
| `slope_vol_targeting_overlay` | 51.76 % | PASS |
| `sma200_momentum_breadth_and_overlay` | 52.52 % | PASS |
| `momentum_breadth_vol_targeting_overlay` | 53.66 % | PASS |
| `sma200_breadth_vol_targeting_overlay` | 54.97 % | PASS |
| `multimarket_breadth_vol_targeting_overlay` | 56.54 % | PASS |
| `momentum_breadth_vol_targeting_overlay_pit_universe` | 60.98 % | PASS |
| `sma200_breadth_vol_targeting_overlay_pit_universe` | 62.40 % | PASS |
| `net_breadth_vol_targeting_overlay_pit_universe` | 62.88 % | PASS |

## Verdict du balayage

- candidats structurellement **inactifs** (< 2 %) : **3**
- dont **PASS vides** : **3**

- `santa_vol_targeting_overlay` — activation 1.70 %, rapport : PASS
- `weakness_breadth_vol_targeting_overlay` — activation 0.00 %, rapport : PASS
- `weakness_breadth_vol_targeting_overlay_pit_universe` — activation 0.00 %, rapport : PASS

Chacun doit être **confirmé par lecture** de son script et de son rapport
avant toute conclusion — critère 2 du pré-enregistrement. Voir l'audit.

**Aucune correction du backlog n'est appliquée ici**, conformément au
pré-enregistrement : requalifier des PASS est une seconde opération, à déclarer
séparément.
