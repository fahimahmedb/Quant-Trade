# Audit — double conversion logarithmique introduite par la correction #392

La correction d'agrégation de panier (#392) a appliqué deux transformations à
**34 scripts**. Justes pour un panier, elles sont fausses là où le
P&L reste en unités logarithmiques. Cet audit cherche les deux défauts
possibles, sur **tous** les scripts du dépôt et pas seulement ceux du commit —
un critère de détection restreint à la liste attendue est précisément ce qui
m'avait fait manquer un foyer au #390 et un portage au #395.

## Défaut A — P&L logarithmique passé une seconde fois par `log1p`

Critère : le script construit `np.log(close[1:] / close[:-1])` (rendements log
de l'indice) **et** appelle `trading_metrics(np.log1p(...))`.

- scripts examinés : **807**
- scripts atteints : **2**

- `nonml_log1p_double_conversion_audit.py`
- `nonml_smallcap_proxy_outperformance_breadth_overlay_backtest.py`

## Défaut B — rendements simples alimentant un SIGNAL

Le message du #392 annonçait exclure les scripts où `R` sert aussi à construire
le signal, « y changer R modifierait la stratégie, pas seulement la mesure ».
Ce contrôle vérifie l'annonce plutôt que de la croire : détection des noms
affectés depuis `(P / P.shift(1) - 1.0)` puis utilisés à l'intérieur d'une
fonction de signal, par `tokenize` et non par regex.

- scripts avec une série de rendements simples : **98**
- dont la série entre dans une fonction de signal : **8**

| Script | Nom | Ligne | Fonction |
|---|---|---|---|
| `nonml_amihud_illiquidity_tilt_pass_validation_battery.py` | `R` | 55 | `build_raw_series()` |
| `nonml_amihud_illiquidity_tilt_pass_validation_battery.py` | `R` | 56 | `build_raw_series()` |
| `nonml_amihud_illiquidity_tilt_pass_validation_battery.py` | `R` | 57 | `build_raw_series()` |
| `nonml_amihud_illiquidity_tilt_pass_validation_battery.py` | `R` | 61 | `build_raw_series()` |
| `nonml_dollar_neutral_composite_vol_targeted_pass_validation_battery.py` | `R` | 56 | `build_raw_series()` |
| `nonml_dollar_neutral_composite_vol_targeted_pass_validation_battery.py` | `R` | 57 | `build_raw_series()` |
| `nonml_dollar_neutral_composite_vol_targeted_pass_validation_battery.py` | `R` | 58 | `build_raw_series()` |
| `nonml_leaders_vol_targeting_20_overlay_pass_validation_battery.py` | `R` | 46 | `build_raw_series()` |
| `nonml_leaders_vol_targeting_20_overlay_pass_validation_battery.py` | `R` | 47 | `build_raw_series()` |
| `nonml_leaders_vol_targeting_20_overlay_pass_validation_battery.py` | `R` | 72 | `build_raw_series()` |
| `nonml_leaders_vol_targeting_20_overlay_pass_validation_battery.py` | `R` | 79 | `build_raw_series()` |
| `nonml_momentum_12_1_pit_universe_pass_validation_battery.py` | `R` | 51 | `build_raw_series()` |
| `nonml_momentum_12_1_pit_universe_pass_validation_battery.py` | `R` | 52 | `build_raw_series()` |
| `nonml_momentum_12_1_pit_universe_pass_validation_battery.py` | `R` | 53 | `build_raw_series()` |
| `nonml_momentum_consistency_pit_universe_pass_validation_battery.py` | `R` | 46 | `build_raw_series()` |
| `nonml_momentum_consistency_pit_universe_pass_validation_battery.py` | `R` | 47 | `build_raw_series()` |
| `nonml_momentum_consistency_pit_universe_pass_validation_battery.py` | `R` | 48 | `build_raw_series()` |
| `nonml_momentum_turnover_doublesort_pass_validation_battery.py` | `R` | 53 | `build_raw_series()` |
| `nonml_momentum_turnover_doublesort_pass_validation_battery.py` | `R` | 54 | `build_raw_series()` |
| `nonml_momentum_turnover_doublesort_pass_validation_battery.py` | `R` | 55 | `build_raw_series()` |
| `nonml_sma200_leaders_overlay_pass_validation_battery.py` | `R` | 49 | `build_raw_series()` |
| `nonml_sma200_leaders_overlay_pass_validation_battery.py` | `R` | 50 | `build_raw_series()` |
| `nonml_sma200_leaders_overlay_pass_validation_battery.py` | `R` | 83 | `build_raw_series()` |
| `nonml_sma200_leaders_overlay_pass_validation_battery.py` | `R` | 84 | `build_raw_series()` |
| `nonml_smallcap_proxy_outperformance_breadth_overlay_backtest.py` | `log_ret` | 65 | `compute_smallcap_breadth_series()` |
| `nonml_smallcap_proxy_outperformance_breadth_overlay_backtest.py` | `log_ret` | 69 | `compute_smallcap_breadth_series()` |

**Limite assumée de ce contrôle** : « fonction de signal » est reconnue par
son nom (heuristique), pas par une analyse de flot de données. Il peut donc
signaler à tort, et manquer une fonction de signal au nom inattendu. Chaque
cas signalé est à lire, pas à corriger mécaniquement — c'est exactement la
correction mécanique qui a créé ces défauts.
