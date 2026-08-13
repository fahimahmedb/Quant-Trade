# Campagne de reproductibilité v3 — classification par test sentinelle (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

Les campagnes v1 et v2 ont échoué en tentant de reconnaître « le rapport
compte-t-il le dépôt ? » par des **motifs de code**. Ici la propriété est
**testée** : on ajoute au dépôt des fichiers neutres, on ré-exécute, et on
regarde si le rapport bouge. Aucune orthographe n'intervient.

## Tirage

- vivier **entier** (aucune exclusion syntaxique) : **289**
- graine, fixée au pré-enregistrement : **20260817**
- taille : **24**, délai **300 s**

**Les 84 tirages des #434-#437 ne sont pas réutilisés** — troisième remise à
zéro.

- `auto_loan_delinquency_overlay`
- `cash_rate_correction_44_crossmarket`
- `conditional_weekend_overlay`
- `credit_card_delinquency_overlay`
- `cross_market_correlation_ndx_russell_overlay`
- `day_of_week_overlay`
- `defensive_diversification_bond_overlay`
- `delinquency_nfci_combined_overlay`
- `dry_bulk_shipping_overlay`
- `dual_momentum_ndx_bond_rotation`
- `empty_pass_basket_extension`
- `failed_breakout_overlay`
- `golden_cross_overlay`
- `inflation_breakeven_overlay`
- `long_rate_level_regime_overlay`
- `lowvol_sma200_overlay`
- `momentum_consistency_pit_universe`
- `santa_vol_targeting_overlay`
- `skewness_vol_targeting_overlay`
- `sma200_slope_overlay`
- `smallcap_proxy_outperformance_breadth_overlay`
- `trend_vol_targeting_overlay`
- `us_germany_rate_differential_overlay`
- `winners_tom_overlay`

## Résultat

| | Nombre |
|---|---|
| **identiques** octet à octet | **23** |
| divergences **structurelles** (le rapport compte le dépôt) | **1** |
| divergences **SUBSTANTIELLES** | **0** |
| non concluants | **0** |

### Divergences structurelles

| Script | Lignes différentes | Verdict du test sentinelle |
|---|---|---|
| `empty_pass_basket_extension` | 26 | le rapport change quand le dépôt gagne des fichiers neutres |

**`empty_pass_basket_extension` — premières lignes divergentes :**

```
- - fichiers `nonml_*_pnl.npz` : **174**
+ - fichiers `nonml_*_pnl.npz` : **208**
- - schéma **panier**, traités par ce cycle : **14**
+ - schéma **panier**, traités par ce cycle : **21**
- - schéma indiciel, déjà traités au #417 : **145**
+ - schéma indiciel, déjà traités au #417 : **172**
```

### Identiques

| Script | Durée |
|---|---|
| `auto_loan_delinquency_overlay` | 6.3 s |
| `cash_rate_correction_44_crossmarket` | 1.7 s |
| `conditional_weekend_overlay` | 2.1 s |
| `credit_card_delinquency_overlay` | 6.0 s |
| `cross_market_correlation_ndx_russell_overlay` | 7.3 s |
| `day_of_week_overlay` | 2.2 s |
| `defensive_diversification_bond_overlay` | 1.4 s |
| `delinquency_nfci_combined_overlay` | 10.6 s |
| `dry_bulk_shipping_overlay` | 3.0 s |
| `dual_momentum_ndx_bond_rotation` | 1.6 s |
| `failed_breakout_overlay` | 2.3 s |
| `golden_cross_overlay` | 2.4 s |
| `inflation_breakeven_overlay` | 5.0 s |
| `long_rate_level_regime_overlay` | 2.5 s |
| `lowvol_sma200_overlay` | 1.8 s |
| `momentum_consistency_pit_universe` | 4.1 s |
| `santa_vol_targeting_overlay` | 2.4 s |
| `skewness_vol_targeting_overlay` | 27.2 s |
| `sma200_slope_overlay` | 2.1 s |
| `smallcap_proxy_outperformance_breadth_overlay` | 2.0 s |
| `trend_vol_targeting_overlay` | 2.1 s |
| `us_germany_rate_differential_overlay` | 8.7 s |
| `winners_tom_overlay` | 1.6 s |

## Borne

La borne porte sur les divergences **substantielles uniquement** : les
structurelles sont comptées, listées et **exclues du dénominateur**, règle fixée
au pré-enregistrement avant tout tirage.

- tirages retenus au dénominateur : **23** (23 identiques + 0 substantielles)
- **borne à 95 % : p ≤ 12.2 %**

Sur un vivier de **289**, il reste de la place pour **~35** divergences substantielles non détectées.

## Contrôle des sentinelles

- fichiers sentinelles subsistant : **0** ✔

## Portée

Ce lot couvre **24** scripts sur **289**, soit
**8.3 %**, par tirage aléatoire à graine fixée.
