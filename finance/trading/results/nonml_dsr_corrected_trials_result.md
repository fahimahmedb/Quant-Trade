# Le DSR avec un décompte d'essais corrigé des doublons (pré-enregistré)

**Piste A.** La question vers laquelle toute la discipline anti-snooping du
dépôt pointe depuis le début, et que 450 cycles n'avaient pas posée.

## Le décompte d'essais

| | Valeur |
|---|---|
| **N_brut** — séries reconstructibles, sans déduplication | **209** |
| **N_distinct** — après fusion des doublons exacts | **207** |
| écart | **2** |

- `var_trials` sous N_brut : **0.000137**
- `var_trials` sous N_distinct : **0.000134**

**2** groupes de doublons exacts fusionnés :

- `nonml_leaders_trend_union_overlay`, `nonml_sma200_leaders_overlay`
- `nonml_leaders_trend_union_overlay_pit_universe`, `nonml_sma200_leaders_overlay_pit_universe`

## Le sens de la correction, redit ici

Dédupliquer **réduit** N, ce qui **abaisse** le seuil `SR0`, donc **augmente**
le DSR. **La correction est favorable aux candidats** — elle n'est pas un
durcissement déguisé.

## Les PASS évalués

Candidats de l'univers portant un **PASS** : **100**

| Candidat | Sharpe ann. | DSR (N_brut) | DSR (N_distinct) |
|---|---|---|---|
| `nonml_january_effect_lowprice_overlay` | +1.42 | 0.9833 | 0.9839 |
| `nonml_momentum_turnover_doublesort` | +1.42 | 0.9728 | 0.9737 |
| `nonml_amihud_illiquidity_tilt` | +1.31 | 0.9632 | 0.9643 |
| `nonml_defensive_diversification_bond_overlay` | +0.77 | 0.9478 | 0.9519 |
| `nonml_winners_trend_vol_targeting_overlay` | +1.15 | 0.9303 | 0.9323 |
| `nonml_parkinson_vol_targeting_overlay` | +0.75 | 0.9252 | 0.9306 |
| `nonml_garman_klass_vol_targeting_overlay` | +0.74 | 0.9229 | 0.9284 |
| `nonml_yang_zhang_vol_targeting_overlay` | +0.74 | 0.9225 | 0.9280 |
| `nonml_diversification_bond_weekly_rebalance_stack` | +0.74 | 0.9086 | 0.9147 |
| `nonml_vol_targeting_20_overlay` | +0.73 | 0.9082 | 0.9145 |
| `nonml_short_term_momentum` | +1.09 | 0.9090 | 0.9114 |
| `nonml_diversification_bond_triple_engine_stack` | +0.73 | 0.9043 | 0.9106 |
| `nonml_rogers_satchell_vol_targeting_overlay` | +0.72 | 0.9022 | 0.9088 |
| `nonml_january_effect_lowprice_overlay_pit_universe` | +0.88 | 0.8926 | 0.8964 |
| `nonml_weekly_rebalance_dual_engine` | +0.72 | 0.8892 | 0.8962 |
| `nonml_defensive_calmar_vol_targeting_overlay` | +0.71 | 0.8886 | 0.8959 |
| `nonml_momentum_12_1` | +1.08 | 0.8840 | 0.8865 |
| `nonml_leaders_vol_targeting_20_overlay` | +1.09 | 0.8831 | 0.8856 |
| `nonml_leaders_trend_union_overlay` | +1.05 | 0.8696 | 0.8723 |
| `nonml_sma200_leaders_overlay` | +1.05 | 0.8696 | 0.8723 |
| `nonml_inflation_breakeven_overlay` | +0.74 | 0.8627 | 0.8692 |
| `nonml_dual_engine_defensive_overlay` | +0.69 | 0.8566 | 0.8650 |
| `nonml_market_concentration_vol_targeting_overlay_pit_universe` | +0.85 | 0.8553 | 0.8598 |
| `nonml_leaders_index52w_high_overlay` | +1.02 | 0.8548 | 0.8578 |
| `nonml_momentum_decile_spread_vol_targeting_overlay_pit_universe` | +0.84 | 0.8499 | 0.8545 |
| … | | | *(75 autres non listés)* |

**Non évaluables : 20** — listés, pas écartés en silence :

- `nonml_cash_rate_correction_44_crossmarket_russell2000` — aucun rapport à son nom
- `nonml_cash_rate_correction_44_crossmarket_sp500` — aucun rapport à son nom
- `nonml_cash_rate_correction_44_weekly_rebalance_ndx` — aucun rapport à son nom
- `nonml_cash_rate_correction_44_weekly_rebalance_russell2000` — aucun rapport à son nom
- `nonml_diversification_bond_overlay_crossmarket_russell2000` — aucun rapport à son nom
- `nonml_diversification_bond_overlay_crossmarket_sp500` — aucun rapport à son nom
- `nonml_etape_d_garch_defensive_overlay` — aucun rapport à son nom
- `nonml_ewma_defensive_overlay` — aucun rapport à son nom
- `nonml_gjr_calm_regime_overlay_dax` — aucun rapport à son nom
- `nonml_gjr_calm_regime_overlay_ndx` — aucun rapport à son nom
- *(10 autres)*

## Combien franchissent DSR > 0.95 ?

| Décompte | Survivants |
|---|---|
| N_brut = 209 | **3** |
| N_distinct = 207 | **4** |

Survivants sous le décompte corrigé :

- `nonml_january_effect_lowprice_overlay` — Sharpe +1.42, DSR 0.9839
- `nonml_momentum_turnover_doublesort` — Sharpe +1.42, DSR 0.9737
- `nonml_amihud_illiquidity_tilt` — Sharpe +1.31, DSR 0.9643
- `nonml_defensive_diversification_bond_overlay` — Sharpe +0.77, DSR 0.9519

## Lecture

**La correction déplace 1 verdict(s).** L'écart entre les deux
décomptes est de **2** essais sur **209**, soit
**1.0 %**.

**Ma prédiction est réfutée.** J'annonçais qu'aucun verdict ne changerait ;
**1** a changé. Je le note comme une prédiction fausse, pas
comme une découverte.

Mais il faut regarder **de combien**. Le verdict qui bascule est
`nonml_defensive_diversification_bond_overlay`, à **DSR 0.9519** — soit
**+0.0019** au-dessus du seuil, après une réduction de N
de **1.0 %**.

> **Ce n'est pas un sauvetage, c'est un candidat posé sur la barre.** Un
> résultat qui bascule quand on retire 2 essais sur 209 rebasculera au
> premier essai ajouté. À lire en sachant que la barre a **baissé**, pas
> que la stratégie s'est améliorée.

## Ce que ce cycle ne prouve pas

- **Un DSR élevé sur un univers d'essais mal défini ne prouve rien.** L'univers
  retenu ici est celui des séries sauvegardées, qui n'est pas l'ensemble des
  hypothèses réellement essayées au cours du projet — il est **plus petit**.
  Un N sous-estimé rend le test **trop indulgent**.
- **Aucune stratégie n'est promue** par ce cycle, quel que soit son DSR.
- Aucun essai n'est retiré d'aucun décompte publié.

### Deux groupes ici, trois au #445 — l'écart est explicable

Le balayage du #445 trouvait **3** groupes de doublons exacts ; ce cycle en
fusionne **2**. La différence n'est pas une contradiction : le troisième
groupe associe `etape_D_overlay_optimized` — un nom **sans préfixe** `nonml_`,
donc hors de l'univers d'essais non-ML déclaré ici. Le balayage lit tout le
dossier ; ce cycle ne compte que les candidats non-ML.

Je le signale parce qu'un lecteur comparant les deux chiffres y verrait
légitimement une incohérence — et que la série de cycles #449-#453 a montré
qu'un chiffre non expliqué finit par être recopié faux.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).