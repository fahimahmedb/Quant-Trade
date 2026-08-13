# Campagne de reproductibilité v3 — classification par test sentinelle (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

Les campagnes v1 et v2 ont échoué en tentant de reconnaître « le rapport
compte-t-il le dépôt ? » par des **motifs de code**. Ici la propriété est
**testée** : on ajoute au dépôt des fichiers neutres, on ré-exécute, et on
regarde si le rapport bouge. Aucune orthographe n'intervient.

## Tirage

- vivier **entier** (aucune exclusion syntaxique) : **290**
- graine, fixée au pré-enregistrement : **20260819**
- taille : **24**, délai **300 s**

**Les 84 tirages des #434-#437 ne sont pas réutilisés** — troisième remise à
zéro.

- `bollinger_width_vol_targeting_overlay`
- `breadth_vol_targeting_overlay`
- `chicago_fed_activity_overlay`
- `day_of_week`
- `delinquency_nfci_baa10y_corr_move_majority_overlay`
- `dispersion_trend_vol_targeting_overlay`
- `diversification_bond_overlay_composite`
- `friday_monday_overlay`
- `gjr_trend_gated_vol_managed`
- `gold_price_overlay`
- `insider_selling_pressure_overlay`
- `january_smallcap`
- `leaders_tom_overlay`
- `lowvol_tom_halloween_union_overlay`
- `momentum12_1_sma200_overlay`
- `momentum_52w_high`
- `net_breadth_vol_targeting_overlay_pit_universe`
- `protocol_inventory`
- `rate_volatility_regime_overlay`
- `reproducibility_sample_lot2`
- `skew_index_overlay`
- `skewness_vol_targeting_overlay`
- `sma200_leaders_overlay_pit_universe`
- `trend_vol_targeting_overlay`

## Résultat

| | Nombre |
|---|---|
| **identiques** octet à octet | **22** |
| divergences **structurelles** (le rapport compte le dépôt) | **1** |
| divergences **SUBSTANTIELLES** | **0** |
| non concluants | **1** |

### Divergences structurelles

| Script | Lignes différentes | Verdict du test sentinelle |
|---|---|---|
| `protocol_inventory` | 59 | le rapport change quand le dépôt gagne des fichiers neutres |

**`protocol_inventory` — premières lignes divergentes :**

```
- - rapports anti-cheat examinés : **330**
+ - rapports anti-cheat examinés : **340**
- - rapports de résultat examinés : **287**
+ - rapports de résultat examinés : **296**
- - sans trace de batterie (fichier dédié **ni** mention interne) : **33**
+ - sans trace de batterie (fichier dédié **ni** mention interne) : **29**
```

### Non concluants

| Script | Raison | Détail |
|---|---|---|
| `reproducibility_sample_lot2` | délai > 300 s | — |

### Identiques

| Script | Durée |
|---|---|
| `bollinger_width_vol_targeting_overlay` | 2.4 s |
| `breadth_vol_targeting_overlay` | 1.9 s |
| `chicago_fed_activity_overlay` | 7.8 s |
| `day_of_week` | 2.6 s |
| `delinquency_nfci_baa10y_corr_move_majority_overlay` | 21.7 s |
| `dispersion_trend_vol_targeting_overlay` | 1.9 s |
| `diversification_bond_overlay_composite` | 1.5 s |
| `friday_monday_overlay` | 2.4 s |
| `gjr_trend_gated_vol_managed` | 212.1 s |
| `gold_price_overlay` | 5.0 s |
| `insider_selling_pressure_overlay` | 3.1 s |
| `january_smallcap` | 1.4 s |
| `leaders_tom_overlay` | 1.5 s |
| `lowvol_tom_halloween_union_overlay` | 1.5 s |
| `momentum12_1_sma200_overlay` | 1.8 s |
| `momentum_52w_high` | 1.7 s |
| `net_breadth_vol_targeting_overlay_pit_universe` | 6.4 s |
| `rate_volatility_regime_overlay` | 11.3 s |
| `skew_index_overlay` | 7.0 s |
| `skewness_vol_targeting_overlay` | 27.6 s |
| `sma200_leaders_overlay_pit_universe` | 5.4 s |
| `trend_vol_targeting_overlay` | 2.2 s |

## Borne

La borne porte sur les divergences **substantielles uniquement** : les
structurelles sont comptées, listées et **exclues du dénominateur**, règle fixée
au pré-enregistrement avant tout tirage.

- tirages retenus **ce lot** : **22** (22 identiques + 0 substantielles)
- tirages retenus **aux #438 + #440** : **47**

| | Dénominateur | Borne à 95 % |
|---|---|---|
| cumul #438 + #440 | 47 | 6,2 % |
| ce lot seul | 22 | 12.7 % |
| **cumul #438 + #440 + #441** | **69** | **4.2 %** |

Sur un vivier de **290**, il reste de la place pour **~12** divergences substantielles non détectées.

Le cumul est légitime : les **trois** lots sont **disjoints par construction** et
classés par la **même règle**, fixée au #438 avant tout tirage.

## Contrôle des sentinelles

- fichiers sentinelles subsistant : **0** ✔

## Portée

Ce lot couvre **24** scripts sur **290**, soit
**8.3 %**, par tirage aléatoire à graine fixée.
