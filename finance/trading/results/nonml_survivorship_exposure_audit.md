# Audit — exposition du backlog au biais du survivant

**Audit de synthèse, non pré-enregistré** : aucun calcul nouveau, uniquement la
confrontation de résultats déjà committés. Aucun paramètre, aucun seuil.

## Le problème

Les stratégies au niveau titre s'appuient sur `data/pead/prices/`, construit à
partir de la **liste NDX-100 telle qu'elle existe en 2026**. Remonter le temps
avec cette liste ne retient que des sociétés ayant survécu et prospéré jusqu'à
aujourd'hui : c'est un **biais du survivant**, qui gonfle mécaniquement la
performance de tout portefeuille construit sur cet univers — y compris la
référence Buy&Hold, mais pas nécessairement dans les mêmes proportions que la
stratégie testée.

Le dépôt contient une alternative propre, `data/pead/prices_pit/` +
`volume_pit/`, où l'appartenance à l'indice est **point-in-time**.

## Ce que disent les paires existantes

Sept stratégies possèdent les deux versions :

| Stratégie | univers 2026 | point-in-time |
|---|---|---|
| `amihud_illiquidity_tilt` | PASS | **FAIL** |
| `dispersion_vol_targeting_overlay` | PASS | **FAIL** |
| `momentum_turnover_doublesort` | PASS | **FAIL** |
| `momentum_12_1` | PASS | PASS |
| `momentum_breadth_vol_targeting_overlay` | PASS | PASS |
| `sma200_breadth_vol_targeting_overlay` | PASS | PASS |
| `momentum_consistency` | FAIL | FAIL |

**3 PASS sur 6 tombent en passant à l'univers point-in-time. Aucun ne s'améliore.**
La direction est unanime — comme pour les deux bugs de la campagne #375-#392.

## Exposition résiduelle

| | |
|---|---|
| stratégies au niveau titre sur l'univers 2026 | **45** |
| dont **sans** contrepartie point-in-time | **38** |
| dont **PASS** et sans contrepartie | **15** |

Les 15 PASS non testés sur ce plan :
`deep_drawdown_breadth_vol_targeting_overlay`, `january_effect_lowprice_overlay`,
`leaders_index52w_high_overlay`, `leaders_trend_union_overlay`,
`leaders_vol_targeting_20_overlay`, `lowvol_sma200_overlay`,
`market_concentration_vol_targeting_overlay`,
`momentum_decile_spread_vol_targeting_overlay`,
`momentum_dispersion_vol_targeting_overlay`, `net_breadth_vol_targeting_overlay`,
`range_position_vol_targeting_overlay`, `sma200_leaders_overlay`,
`smallcap_proxy_outperformance_breadth_overlay`,
`weakness_breadth_vol_targeting_overlay`, `winners_trend_vol_targeting_overlay`.

## Lecture

Le taux observé est de **3 chutes sur 6 PASS testés**. L'extrapoler aux 15 non
testés donnerait un ordre de grandeur, mais ce serait une inférence sur un
échantillon de 6 — trop mince pour être avancée comme un chiffre. **Ce qui est
établi** : le biais existe, il est matériel, sa direction est systématiquement
défavorable, et **15 PASS y sont exposés sans avoir été vérifiés**.

Les données nécessaires (`prices_pit`, `volume_pit`, 214 tickers depuis 2005)
sont **déjà présentes dans le dépôt** : chaque vérification est un portage de
script, sans téléchargement.
