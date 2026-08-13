# Balayage des portes de capitulation neutralisées par le plancher 1,0× (pré-enregistré)

Diagnostic, pas une stratégie. Cherche les candidats dont la structure interdit
à l'overlay de s'activer : une porte qui s'ouvre en régime de faiblesse combinée
à un vol-targeting dont le plancher est l'exposition neutre.

Seuil d'inactivité **repris tel quel du #410** : exposition > 1,0× sur moins de 2 % des séances.

## Volet A — détection statique

- scripts `nonml_*_backtest.py` examinés : **284**
- illisibles : **0**
- portant la structure `clip(…, 1.0, …)` : **62**

**Couverture 100 %** — critère 1 du pré-enregistrement atteint.

## Volet B — mesure empirique de l'activation

- candidats mesurés : **60**, dont **55** au schéma indiciel et **5** au schéma **panier** (extension #425)
- candidats détectés mais **non mesurés** faute de `.npz` : **2**

Ce second chiffre est un **résultat du cycle**, pas une excuse : il quantifie
exactement ce que la lacune mesurée au #406 coûte à ce diagnostic.

Sur un panier, l'exposition n'est pas stockée : elle est **récupérée par division**
`pnl_gross_ov / pnl_gross_bh`, la jambe candidate valant `exposition × jambe de
référence` (identité établie et vérifiée au #402, contrôle 1b). Les séances à
dénominateur quasi nul sont exclues et comptées, jamais remplacées par un défaut.

| Candidat panier | Exposition > 1,0× | Séances exclues (dénominateur nul) |
|---|---|---|
| `lowvol_trend_vol_targeting_overlay` | 61.50 % | 1 |
| `momentum_consistency_trend_vol_targeting_15_overlay` | 20.98 % | 0 |
| `momentum_consistency_trend_vol_targeting_overlay` | 44.76 % | 0 |
| `winners_trend_vol_targeting_overlay` | 35.25 % | 0 |
| `winners_trend_vol_targeting_overlay_pit_universe` | 60.12 % | 0 |

Non mesurés :

- `rebound_speed_breadth_vol_targeting_overlay` (verdict au rapport : FAIL)
- `vix_regime_vol_targeting_overlay` (verdict au rapport : FAIL)

### Candidats mesurés, par activation croissante

| Candidat | Séances à exposition > 1,0× | Schéma | Verdict au rapport |
|---|---|---|---|
| `weakness_breadth_vol_targeting_overlay` | 0.00 % ← **inactif** | indiciel | PASS |
| `weakness_breadth_vol_targeting_overlay_pit_universe` | 0.00 % ← **inactif** | indiciel | PASS |
| `santa_vol_targeting_overlay` | 1.70 % ← **inactif** | indiciel | PASS |
| `internal_breadth_vol_targeting_overlay` | 5.13 % | indiciel | FAIL |
| `variance_ratio_vol_targeting_overlay` | 19.57 % | indiciel | PASS |
| `momentum_consistency_trend_vol_targeting_15_overlay` | 20.98 % | panier | FAIL |
| `kurtosis_nu_combined_vol_targeting_overlay` | 21.29 % | indiciel | PASS |
| `deep_drawdown_breadth_vol_targeting_overlay` | 21.52 % | indiciel | PASS |
| `dispersion_trend_vol_targeting_overlay` | 22.38 % | indiciel | PASS |
| `market_concentration_vol_targeting_overlay` | 23.32 % | indiciel | PASS |
| `arch_clustering_vol_targeting_overlay` | 24.04 % | indiciel | PASS |
| `dispersion_vol_targeting_overlay` | 24.77 % | indiciel | PASS |
| `yield_curve_slope_vol_targeting_overlay` | 25.59 % | indiciel | PASS |
| `range_position_vol_targeting_overlay` | 25.78 % | indiciel | PASS |
| `deep_drawdown_breadth_vol_targeting_overlay_pit_universe` | 25.82 % | indiciel | PASS |
| `student_t_tail_vol_targeting_overlay` | 25.89 % | indiciel | PASS |
| `ljung_box_clustering_vol_targeting_overlay` | 27.63 % | indiciel | PASS |
| `kurtosis_vol_targeting_overlay` | 27.80 % | indiciel | PASS |
| `smallcap_proxy_outperformance_breadth_overlay` | 28.09 % | indiciel | PASS |
| `acf_lag1_vol_targeting_overlay` | 28.10 % | indiciel | FAIL |
| `dispersion_vol_targeting_overlay_pit_universe` | 28.92 % | indiciel | FAIL |
| `trend_lowvol_vol_targeting_overlay` | 30.12 % | indiciel | FAIL |
| `skewness_vol_targeting_overlay` | 30.28 % | indiciel | FAIL |
| `breadth_vol_targeting_overlay` | 30.94 % | indiciel | PASS |
| `vol_of_vol_vol_targeting_overlay` | 31.12 % | indiciel | PASS |
| `momentum_dispersion_vol_targeting_overlay_pit_universe` | 32.06 % | indiciel | PASS |
| `momentum_dispersion_trend_and_overlay` | 32.13 % | indiciel | PASS |
| `beta_dispersion_vol_targeting_overlay` | 34.37 % | indiciel | FAIL |
| `parkinson_c2c_ratio_vol_targeting_overlay` | 34.41 % | indiciel | FAIL |
| `momentum_decile_spread_vol_targeting_overlay_pit_universe` | 34.82 % | indiciel | PASS |
| `winners_trend_vol_targeting_overlay` | 35.25 % | panier | PASS |
| `bollinger_width_vol_targeting_overlay` | 35.54 % | indiciel | FAIL |
| `daily_advance_breadth_vol_targeting_overlay` | 35.58 % | indiciel | FAIL |
| `smallcap_proxy_outperformance_breadth_overlay_pit_universe` | 36.07 % | indiciel | PASS |
| `drawdown_depth_vol_targeting_overlay` | 36.16 % | indiciel | FAIL |
| `market_concentration_vol_targeting_overlay_pit_universe` | 36.41 % | indiciel | PASS |
| `range_position_vol_targeting_overlay_pit_universe` | 36.82 % | indiciel | FAIL |
| `momentum_dispersion_vol_targeting_overlay` | 36.97 % | indiciel | PASS |
| `gap_risk_vol_targeting_overlay` | 37.23 % | indiciel | FAIL |
| `correlation_regime_vol_targeting_overlay` | 37.55 % | indiciel | FAIL |
| `calendar_vol_targeting_overlay` | 37.55 % | indiciel | PASS |
| `momentum_decile_spread_vol_targeting_overlay` | 37.98 % | indiciel | PASS |
| `gjr_forecast_gate_vol_targeting_overlay` | 39.13 % | indiciel | PASS |
| `lowvol_regime_vol_targeting_overlay` | 39.76 % | indiciel | FAIL |
| `ensemble_vote_vol_targeting_overlay` | 39.93 % | indiciel | PASS |
| `january_barometer_vol_targeting_overlay` | 40.64 % | indiciel | PASS |
| `trend_vol_targeting_overlay` | 42.05 % | indiciel | PASS |
| `net_breadth_vol_targeting_overlay` | 44.40 % | indiciel | PASS |
| `momentum_consistency_trend_vol_targeting_overlay` | 44.76 % | panier | FAIL |
| `goldencross_vol_targeting_overlay` | 48.77 % | indiciel | FAIL |
| `slope_vol_targeting_overlay` | 51.76 % | indiciel | PASS |
| `sma200_momentum_breadth_and_overlay` | 52.52 % | indiciel | PASS |
| `momentum_breadth_vol_targeting_overlay` | 53.66 % | indiciel | PASS |
| `sma200_breadth_vol_targeting_overlay` | 54.97 % | indiciel | PASS |
| `multimarket_breadth_vol_targeting_overlay` | 56.54 % | indiciel | PASS |
| `winners_trend_vol_targeting_overlay_pit_universe` | 60.12 % | panier | FAIL |
| `momentum_breadth_vol_targeting_overlay_pit_universe` | 60.98 % | indiciel | PASS |
| `lowvol_trend_vol_targeting_overlay` | 61.50 % | panier | FAIL |
| `sma200_breadth_vol_targeting_overlay_pit_universe` | 62.40 % | indiciel | PASS |
| `net_breadth_vol_targeting_overlay_pit_universe` | 62.88 % | indiciel | PASS |

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
