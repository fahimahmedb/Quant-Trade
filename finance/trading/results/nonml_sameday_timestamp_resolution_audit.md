# Audit — résolution par horodatage des candidats « du jour même » (pré-enregistré)

Recalcul **indépendant** : cet audit n'importe rien du script de résolution.
Il redérive chaque horodatage par une invocation git **différente**
(`rev-list` au lieu de `log --diff-filter=A`) et compare les deux classements.

## Contrôle 1 — les deux façons de lire l'horodatage concordent

| Candidat | Heure au rapport | Heure redérivée | Accord |
|---|---|---|---|
| `winners_trend_vol_targeting_overlay` | 01:55:39 | 01:55:39 | ✔ |
| `breadth_confirmation_overlay` | 02:15:46 | 02:15:46 | ✔ |
| `sma50_trend_overlay` | 03:33:41 | 03:33:41 | ✔ |
| `intl_breadth_confirmation_overlay` | 03:41:28 | 03:41:28 | ✔ |
| `santa_claus_rally_overlay` | 03:44:44 | 03:44:44 | ✔ |
| `tom_decomposition_overlay` | 05:55:09 | 05:55:09 | ✔ |
| `santa_vol_targeting_overlay` | 06:16:47 | 06:16:47 | ✔ |
| `momentum_12_1` | 06:35:40 | 06:35:40 | ✔ |
| `dispersion_trend_vol_targeting_overlay` | 08:55:54 | 08:55:54 | ✔ |
| `january_effect_lowprice_overlay` | 10:35:32 | 10:35:32 | ✔ |
| `intraday_range_regime_overlay` | 10:56:31 | 10:56:31 | ✔ |
| `momentum_breadth_vol_targeting_overlay` | 12:55:31 | 12:55:31 | ✔ |
| `sma200_breadth_vol_targeting_overlay` | 13:15:03 | 13:15:03 | ✔ |
| `net_breadth_vol_targeting_overlay` | 13:35:18 | 13:35:18 | ✔ |
| `sma200_momentum_breadth_and_overlay` | 13:55:14 | 13:55:14 | ✔ |
| `multimarket_breadth_vol_targeting_overlay` | 15:14:45 | 15:14:45 | ✔ |
| `momentum_dispersion_trend_and_overlay` | 16:06:41 | 16:06:41 | ✔ |

**17/17 en accord.**
L'horodatage ne dépend pas de la manière de l'interroger — le classement ne
repose donc pas sur une particularité d'une seule commande git.

## Contrôle 2 — la marge du cas le plus serré

- règle ajoutée à : **17:56:16 UTC**
- candidat le plus tardif : `momentum_dispersion_trend_and_overlay`, **1 h 49 min** avant la règle

La marge la plus serrée dépasse **une heure**. Le classement ne tient pas à
quelques secondes d'horodatage, ni à un décalage de fuseau : il serait
inchangé même si l'un des deux repères était décalé de plusieurs dizaines
de minutes.

## Contrôle 3 — pourquoi la date d'**ajout**, et pas la dernière modification

Un lecteur pourrait objecter qu'un rapport ajouté avant la règle mais **révisé**
après devrait compter comme dette. Mesure faite :

- rapports **modifiés** après l'ajout de la règle : **17** / 17

**Ce chiffre ne doit pas être lu comme une dette**, et c'est important de le dire :
mes propres cycles récents ont touché plusieurs de ces fichiers — le #427 y a
ajouté une sauvegarde de P&L, le #430 une colonne « Séances test. ». Retenir la
dernière modification ferait apparaître comme « publiés après la règle » des
rapports que j'ai moi-même édités hier pour des raisons d'outillage.

Le critère pré-enregistré est la **publication** — le commit d'ajout — et c'est le
seul qui réponde à la question posée : ce PASS existait-il avant que la règle
n'existe ? Je le note plutôt que de laisser l'objection sans réponse.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| candidats classés | 17/17 | 17/17 | ✔ |
| concordance des deux lectures | totale | 17/17 | ✔ |
| candidats en dette soumis à la batterie | tous | 0 en dette → aucun à soumettre | ✔ |
| verdicts de niveau 1 modifiés | 0 | 0 | ✔ |

**Les 17 sont blanchis.** Aucun n'est en dette : tous ont été publiés avant que
la batterie n'existe, le plus tardif de près de deux heures.

La clause « tout candidat en dette est soumis à la batterie dans ce cycle »
était **conditionnelle et n'a pas été déclenchée**. Elle avait été écrite avant
que les noms soient connus, ce qui était son objet : je ne pouvais pas choisir
après coup d'y soustraire un candidat gênant.

La prédiction déductive sur le DSR **n'a donc pas été mise à l'épreuve**. Je ne
la compte ni comme vérifiée ni comme démentie.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
