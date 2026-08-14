# La couverture réelle de la convention « un `PREREG_` par entrée » (pré-enregistré)

Les **#461** et **#462** reposent tous deux sur cette convention sans
l'avoir éprouvée : ils apparient entrée et rapport en supposant qu'une
entrée cite **un** `PREREG_<nom>.md` et que le rapport est
`results/nonml_<nom>_result.md`.

## Le résultat

- entrées de backlog : **284**
- citant **exactement un** `PREREG_` : **171** (**60,2 %**)
- citant **aucun** : **104**
- citant **plusieurs** : **9**

- citations **pendantes** (fichier absent) : **0**
- entrées conformes **sans rapport** correspondant : **70**
- `PREREG_` du dépôt **cités par aucune entrée** : **230** sur **440**

## « Hors convention » n'est pas « en infraction »

Le pré-enregistrement l'exige, et le résultat le rend nécessaire.

Les **104** entrées qui ne citent aucun `PREREG_` **ne sont pas
fautives pour autant** : la convention est née **en cours de route**, et
les premières entrées du backlog décrivent des **stratégies** — lignes de
tableau, résultats de backtests de marché — pas des cycles de
vérification appuyés sur un pré-enregistrement nommé.

> **Un compte n'est pas un reproche.** Ce rapport mesure une *couverture*,
> il ne prononce aucune infraction — sauf pour les citations pendantes
> ci-dessous, qui, elles, sont des défauts réels.

## Les citations pendantes — les seuls défauts réels

**Aucune.** Chaque `PREREG_` cité par une entrée existe dans le dépôt.

## Entrées conformes dont le rapport attendu est absent

La convention promet **deux** choses. La première tient toujours (voir
ci-dessus) ; celle-ci est la seconde.

**70** sous la règle déclarée — **et ce chiffre
surestime.** Décomposé :

| Cas | Nombre |
|---|---|
| le rapport **existe sous un autre nom** | **60** |
| **aucun** fichier ne porte ce `<nom>` | **10** |

> **Classification ajoutée APRÈS avoir vu le chiffre**, et signalée
> comme telle. Elle n'ôte rien du compte de tête — mais la publier
> comme **70 rapports manquants** serait une accusation fausse.

La cause est une **convention de nom que ma règle ignorait** : les
cycles de **batterie** publient `nonml_<nom>.md`, sans suffixe
`_result`, parce que leur `<nom>` se termine déjà par
`_pass_validation_battery`. **Le rapport est là ; c'est mon attente qui
était mal formée.**

### Les seuls cas sans aucun fichier

| Entrée | `<nom>` |
|---|---|
| #164 | `short_term_momentum_pit_universe` |
| #163 | `leaders_index52w_high_overlay_pit_universe` |
| #252 | `short_term_momentum_pit_universe_causal` |
| #253 | `leaders_overlays_same_bar_correction` |
| #254 | `leaders_calendar_overlays_same_bar_correction` |
| #255 | `lowvol_trend_vol_targeting_same_bar_correction` |
| #257 | `sma200_overlays_same_bar_correction` |
| #260 | `leaders_index52w_high_overlay_battery_causal_refresh` |
| #263 | `meilleurs_candidats_guide_deploiement_v2` |
| #273 | `dispersion_battery_caduc_et_guide_v3` |

### Ceux dont le rapport existe autrement *(extrait de 10)*

| Entrée | Attendu | Trouvé |
|---|---|---|
| #188 | `nonml_leaders_index52w_high_overlay_pass_validation_battery_result.md` | `nonml_leaders_index52w_high_overlay_pass_validation_battery.md` |
| #189 | `nonml_presidential_cycle_overlay_pass_validation_battery_result.md` | `nonml_presidential_cycle_overlay_pass_validation_battery.md` |
| #190 | `nonml_halloween_postelection_multiplicative_overlay_pass_validation_battery_result.md` | `nonml_halloween_postelection_multiplicative_overlay_pass_validation_battery.md` |
| #194 | `nonml_cross_market_correlation_ndx_dax_overlay_pass_validation_battery_result.md` | `nonml_cross_market_correlation_ndx_dax_overlay_pass_validation_battery.md` |
| #201 | `nonml_inflation_breakeven_overlay_pass_validation_battery_result.md` | `nonml_inflation_breakeven_overlay_pass_validation_battery.md` |
| #207 | `nonml_vol_targeting_20_overlay_pass_validation_battery_result.md` | `nonml_vol_targeting_20_overlay_pass_validation_battery.md` |
| #208 | `nonml_trend_vol_targeting_overlay_pass_validation_battery_result.md` | `nonml_trend_vol_targeting_overlay_pass_validation_battery.md` |
| #209 | `nonml_parkinson_vol_targeting_overlay_pass_validation_battery_result.md` | `nonml_parkinson_vol_targeting_overlay_pass_validation_battery.md` |
| #210 | `nonml_calendar_vol_targeting_overlay_pass_validation_battery_result.md` | `nonml_calendar_vol_targeting_overlay_pass_validation_battery.md` |
| #211 | `nonml_breadth_vol_targeting_overlay_pass_validation_battery_result.md` | `nonml_breadth_vol_targeting_overlay_pass_validation_battery.md` |
| … | *et 50 autres* | |

## Entrées citant plusieurs `PREREG_`

Ni conformes ni fautives : elles **renvoient** à d'autres cycles.
Un instrument qui exige « exactement un » les écarte — c'est ce que
font les #461 et #462, et **c'est une part de leur périmètre perdu**.

| Entrée | `PREREG_` cités |
|---|---|
| #165 | `gjr_trend_gated_vol_managed`, `gjr_vol_managed_crossmarket`, `gjr_vol_managed_weekly_rebalance`, `volatility_managed_portfolio_gjr` |
| #215 | `gap_risk_vol_targeting_overlay`, `garman_klass_vol_targeting_overlay`, `variance_ratio_vol_targeting_overlay` |
| #218 | `kurtosis_vol_targeting_overlay`, `skewness_vol_targeting_overlay`, `vol_of_vol_vol_targeting_overlay` |
| #221 | `arch_clustering_vol_targeting_overlay`, `rogers_satchell_vol_targeting_overlay`, `yang_zhang_vol_targeting_overlay` |
| #312 | `january_barometer_overlay_pass_validation_battery`, `leaders_vol_targeting_20_overlay_pass_validation_battery`, `market_concentration_vol_targeting_overlay_pass_validation_battery`, `momentum_dispersion_vol_targeting_overlay_pass_validation_battery`, `range_position_vol_targeting_overlay_pass_validation_battery`, `sma200_leaders_overlay_pass_validation_battery`, `sma200_slope_overlay_pass_validation_battery`, `sma200_trend_overlay_pass_validation_battery` |
| #321 | `capacity_utilization_overlay`, `continuing_claims_overlay`, `corporate_profits_overlay`, `durable_goods_orders_overlay`, `epu_overlay`, `federal_deficit_overlay`, `manufacturing_hours_overlay`, `natural_gas_price_overlay`, `nonfarm_payrolls_overlay`, `savings_rate_overlay`, `trade_balance_overlay` |
| #332 | `macro_combo_and_breakeven_claims_trade_overlay`, `macro_combo_breakeven_claims_trade_overlay` |
| #334 | `job_openings_overlay`, `macro_combo_and_breakeven_claims_trade_overlay_pass_validation_battery` |
| #336 | `cpi_inflation_overlay`, `cpi_inflation_overlay_pass_validation_battery`, `ppi_inflation_overlay`, `real_gdp_overlay` |

## Les `PREREG_` orphelins

**230** pré-enregistrement(s) sur **440**
ne sont cités par aucune entrée **sous la forme `PREREG_<nom>.md`**.

> **« Non cité sous cette forme » n'est pas « jamais mentionné ».**
> Diagnostic ajouté après coup, même statut que le précédent.

| Cas | Nombre |
|---|---|
| `<nom>` **apparaît** ailleurs dans le backlog | **206** |
| `<nom>` **absent** de tout le backlog | **24** |

Le second chiffre est le seul qui désigne une trace réellement
orpheline : un pré-enregistrement dont **aucune entrée ne parle**.

Les **24** premiers, par ordre alphabétique :

- `PREREG_correlation_regime_episodes_149.md`
- `PREREG_etape_d_v3_add_149.md`
- `PREREG_etape_d_v3_add_crossmarket.md`
- `PREREG_leaders_index52w_high_overlay_extended_history.md`
- `PREREG_leaders_vol_targeting_20_overlay_pit_universe.md`
- `PREREG_log1p_double_conversion_correction.md`
- `PREREG_lowvol_sma200_overlay_pit_universe.md`
- `PREREG_market_concentration_vol_targeting_overlay_pit_universe.md`
- `PREREG_ml_exogenous_features_rates_crossmarket.md`
- `PREREG_ml_meta_labeling_logitl2_ndx.md`
- `PREREG_ml_regularized_architecture.md`
- `PREREG_momentum_decile_spread_vol_targeting_overlay_pit_universe.md`
- `PREREG_momentum_dispersion_vol_targeting_overlay_pit_universe.md`
- `PREREG_n_trials_dependence_correction.md`
- `PREREG_net_breadth_vol_targeting_overlay_pit_universe.md`
- *… et 9 autres*

## Ce que cela fait aux #461 et #462

L'engagement 1 était de le dire si le résultat les affaiblissait.

Leur règle d'appariement — « exactement un `PREREG_` » — laisse de côté
**113** entrées sur **284**. Sur l'univers qu'ils déclaraient
(#443-#460) la convention est parfaitement suivie, et leurs chiffres y
sont valides ; **c'est leur robustesse qui l'est moins** : élargir la
borne vers l'arrière n'élargit pas autant qu'il y paraît, et le #462
l'avait signalé sans le chiffrer. **C'est maintenant chiffré.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| moins de la moitié citent exactement un `PREREG_` | < 50 % | 60,2 % | **réfutée** |
| zéro citation pendante | 0 | 0 | **vérifiée** |
| au moins un `PREREG_` orphelin | ≥ 1 | 230 | **vérifiée** |

**La prédiction 1 est réfutée dans le sens flatteur** — la convention
est mieux suivie que je ne le croyais. Le pré-enregistrement m'oblige
alors à **douter d'abord de mon comptage** (leçons #458 et #462) :
le découpage employé est celui des #461/#462, et il classe **284**
entrées — un total invraisemblable signalerait un titre mal reconnu.

## Critères de succès

1. **284/284** entrées classées — **OUI**.
2. Citations pendantes listées nominativement — **OUI**.
3. `PREREG_` orphelins listés nominativement — **OUI**.
4. Distinction « hors convention » / « en infraction » explicitée — **OUI**.

**PASS** — le critère porte sur le procédé.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucune entrée ni aucun nom.
- Il ne **réécrit** aucun verdict.
- Il ne **rejoue** aucun script : lecture seule, donc **aucun effet de
  bord** à annuler, contrairement au #463.


> **Rapport dépendant du dépôt** — il décrit l'état du backlog à la date
> de son exécution (cycles #436-#438).