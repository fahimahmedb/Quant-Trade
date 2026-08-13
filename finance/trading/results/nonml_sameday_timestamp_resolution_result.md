# Résolution par horodatage des candidats « du jour même » (pré-enregistré)

Cycle d'**infrastructure de protocole**. Aucune stratégie nouvelle, aucun
paramètre touché, **aucun verdict de niveau 1 modifié**.

La batterie `nonml_pass_validation_battery.py` a été ajoutée au dépôt le
**2026-07-29 17:56:16 UTC**. Le #431 comparait des **dates** ; ce cycle compare des
**horodatages à la seconde**, ce qui tranche exactement.

## Classification des candidats du jour même

- candidats tombant le **2026-07-29** : **17**

| Catégorie | Nombre |
|---|---|
| horodatage **antérieur** ⇒ antériorité, blanchi | **17** |
| horodatage **postérieur** ⇒ dette réelle | **0** |
| horodatage **exactement égal** ⇒ indécidable | **0** |

### Blanchis — publiés avant l'existence de la règle

| Candidat | Rapport ajouté à | Écart avant la règle |
|---|---|---|
| `winners_trend_vol_targeting_overlay` | 01:55:39 | −16 h 0 min |
| `breadth_confirmation_overlay` | 02:15:46 | −15 h 40 min |
| `sma50_trend_overlay` | 03:33:41 | −14 h 22 min |
| `intl_breadth_confirmation_overlay` | 03:41:28 | −14 h 14 min |
| `santa_claus_rally_overlay` | 03:44:44 | −14 h 11 min |
| `tom_decomposition_overlay` | 05:55:09 | −12 h 1 min |
| `santa_vol_targeting_overlay` | 06:16:47 | −11 h 39 min |
| `momentum_12_1` | 06:35:40 | −11 h 20 min |
| `dispersion_trend_vol_targeting_overlay` | 08:55:54 | −9 h 0 min |
| `january_effect_lowprice_overlay` | 10:35:32 | −7 h 20 min |
| `intraday_range_regime_overlay` | 10:56:31 | −6 h 59 min |
| `momentum_breadth_vol_targeting_overlay` | 12:55:31 | −5 h 0 min |
| `sma200_breadth_vol_targeting_overlay` | 13:15:03 | −4 h 41 min |
| `net_breadth_vol_targeting_overlay` | 13:35:18 | −4 h 20 min |
| `sma200_momentum_breadth_and_overlay` | 13:55:14 | −4 h 1 min |
| `multimarket_breadth_vol_targeting_overlay` | 15:14:45 | −2 h 41 min |
| `momentum_dispersion_trend_and_overlay` | 16:06:41 | −1 h 49 min |

## Lecture

Le #431 avait compté ces candidats à part plutôt que de les ranger « du côté qui
m'arrange » — c'était le bon réflexe. Mais le #432 concluait « non tranchable par
la date seule » et **s'arrêtait là**, alors que l'horodatage était disponible.
La formule était vraie au mot près et la conclusion prématurée.

**Aucun des candidats du jour même n'est en dette.** Tous ont été publiés
avant l'ajout de la batterie : ils relèvent de l'antériorité, comme les 10
déjà classés ainsi au #431. La dette de la Règle 9 reste celle du #432,
désormais soldée.
