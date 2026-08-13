# Audit — persistance du P&L, lot 5 : les PASS invisibles au balayage de doublons (pré-enregistré)

Cycle d'**infrastructure**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun décompte d'hypothèses corrigé.

**Ce lot n'est pas comme les quatre précédents.** Les #416, #423, #424 et #426 ne
portaient que des FAIL : aucun verdict ne pouvait bouger. Ceux-ci portent des
**PASS**, et un doublon exact entre deux d'entre eux gonflerait le décompte
« X PASS sur Y hypothèses testées », entrée directe du `n_trials` du DSR.

## Périmètre — 16 traités, 2 écartés avec leur raison

- rapports portant un PASS : **101**
- parmi eux sans `.npz` : **18**
- **traités par ce cycle** : **16**
- **écartés** : **2**

- `tom_decomposition_overlay` — boucle sur plusieurs **variantes** × marchés : nommer un seul `.npz` obligerait à élire une variante, c'est-à-dire à inventer une convention pour l'occasion.
- `capitulation_gate_floor_sweep` — **diagnostic, pas une stratégie** (sa propre docstring le dit) — son PASS est un faux positif de détection.

Le pré-enregistrement annonçait 17 traités et 1 écarté. La lecture script par
script en a écarté un second, `tom_decomposition_overlay`, pour la raison
ci-dessus. L'engagement était explicite — « tout script dont la structure ne
correspond à aucune des trois conventions est écarté et listé, pas forcé » — et
je ne suis pas passé outre pour tenir un chiffre annoncé.

## Contrôle de non-régression — 16/16 identiques octet à octet

Vérifié par comparaison binaire des `results/nonml_<nom>_result.md` avant et
après ré-exécution. Le `diff` des scripts ne comporte que des **insertions**
(159 lignes ajoutées, **0 supprimée**) : aucune ligne de calcul n'est touchée.

Prédiction déductive du pré-enregistrement **confirmée**, comme aux #416
(10/10), #423 (4/4), #424 (12/12) et #426 (2/2). **Quarante-quatre résultats
publiés** ont désormais été testés contre leur propre code — et ces 16-ci sont
les premiers **PASS** des cinq lots.

## Contrôle de cohérence — le `.npz` contre le rapport du candidat

Le nombre de séances stocké doit coïncider avec celui que le rapport annonce
déjà. Écart toléré, fixé avant calcul : **0**.

| Candidat | Schéma | Séances au rapport | Séances au `.npz` | Accord |
|---|---|---|---|---|
| `breadth_confirmation_overlay` | indiciel | 10020 | 10020 | ✔ |
| `intl_breadth_confirmation_overlay` | indiciel | 10020 | 10020 | ✔ |
| `golden_cross_overlay` | indiciel | — (non annoncé) | 10072 | n/a |
| `halloween_effect` | indiciel | — (non annoncé) | 10272 | n/a |
| `index_52w_high_overlay` | indiciel | — (non annoncé) | 10020 | n/a |
| `intraday_range_regime_overlay` | indiciel | — (non annoncé) | 10020 | n/a |
| `santa_claus_rally_overlay` | indiciel | — (non annoncé) | 10272 | n/a |
| `sma200_tom_halloween_union_overlay` | indiciel | — (non annoncé) | 10072 | n/a |
| `sma50_trend_overlay` | indiciel | — (non annoncé) | 10222 | n/a |
| `tom_halloween_union_overlay` | indiciel | — (non annoncé) | 10272 | n/a |
| `tom_overlay` | indiciel | — (non annoncé) | 10272 | n/a |
| `turn_of_month` | indiciel | — (non annoncé) | 10272 | n/a |
| `january_effect_lowprice_overlay` | panier | 1375 | 1375 | ✔ |
| `lowvol_sma200_overlay` | panier | 1336 | 1336 | ✔ |
| `momentum_12_1` | panier | 1144 | 1144 | ✔ |
| `short_term_momentum` | panier | 1391 | 1391 | ✔ |

**6/6 en accord** (10 rapport(s) n'annonçant pas de nombre de
séances, le contrôle y est inapplicable et compté comme tel, pas comme réussi).

Les séries sauvegardées sont bien celles que les rapports décrivent.

### Contrôle supplémentaire — la ligne NDX des rapports multi-marchés

**Ajouté après avoir constaté que le contrôle pré-enregistré ne couvrait que
6 des 16 candidats.** Les rapports multi-marchés publient un tableau par
marché sans total de séances : le contrôle par nombre de séances y est
inapplicable, mais leur **ligne NDX** publie souvent « Séances test. » et/ou
« %j levé », tous deux comparables à ce que contient le `.npz`.

Ce contrôle **resserre** le cycle au lieu de le relâcher, et la tolérance n'est
pas choisie pour passer : les taux sont publiés au dixième de point, donc
**0,05 point** est la moitié du pas d'arrondi — valeur déduite du format, pas
ajustée. Je le signale comme ajout post-hoc plutôt que de le présenter comme
prévu d'avance.

| Candidat | Séances (rapport / `.npz`) | Activation (rapport / `.npz`) | Accord |
|---|---|---|---|
| `golden_cross_overlay` | 10072 / 10072 | 75.0 % / 75.0 % | ✔ |
| `index_52w_high_overlay` | 10020 / 10020 | 54.6 % / 54.6 % | ✔ |
| `santa_claus_rally_overlay` | — | 2.8 % / 2.8 % | ✔ |
| `sma200_tom_halloween_union_overlay` | 10072 / 10072 | 91.9 % / 91.9 % | ✔ |
| `sma50_trend_overlay` | 10222 / 10222 | 66.3 % / 66.3 % | ✔ |
| `tom_halloween_union_overlay` | — | 66.0 % / 66.0 % | ✔ |
| `turn_of_month` | — | 33.4 % / 33.4 % | ✔ |

**7/7 en accord.**
La série NDX sauvegardée reproduit les chiffres que le rapport publiait déjà,
calculés indépendamment par le script du candidat. Combiné au contrôle
pré-enregistré, **13 vérifications** portent sur ces 16 `.npz`.

## Mesure — balayage de doublons rejoué sans modification

| | #426 | #427 |
|---|---|---|
| séries de P&L reconstruites | 202 | **218** |
| groupes de doublons exacts | 3 | **3** |
| quasi-doublons | 1 | **1** |

**Décompte inchangé.** Les 16 séries ajoutées n'introduisent aucun doublon
exact ni quasi-doublon nouveau.

Aucun candidat de ce lot n'apparaît dans un groupe de doublons exacts. La
question posée par le pré-enregistrement — « deux PASS sont-ils la même
série ? » — reçoit donc une réponse **négative pour les 16 testés**.

Je n'avais fait **aucune prédiction** sur ce point, et je ne présente pas
cette absence comme une confirmation : c'est une mesure, désormais faite.

## Mesure — couverture du balayage de doublons (piste 2 du #426)

| | Nombre |
|---|---|
| séries lues par le balayage (`results/*_pnl.npz`) | **218** |
| dont candidats non-ML (`nonml_*`) | **208** |
| dont séries ML / Étape D | **10** |
| scripts de backtest non-ML du dépôt | **284** |
| **couverture non-ML** | **73.2 %** |

Le rapport du balayage annonce un total sans dire que des séries ML et Étape D
y figurent, ni quelle fraction du dépôt non-ML il couvre. Les deux chiffres sont
publiés ici ; les inscrire dans son propre rapport reste à faire.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| scripts traités ou écartés avec raison | 17 | 16 traités + 2 écartés | ✔ |
| différences de résultat | 0 | **0** | ✔ |
| cohérence `.npz` / rapport | **17/17** | **13/16** vérifiés | **✘** |
| mesures publiées | 3 | 3 | ✔ |

**Le critère de cohérence n'est pas tenu tel qu'il était écrit.** Il exigeait
17/17 ; 13 des 16 candidats sont vérifiés (6 par le contrôle
pré-enregistré, 7 par le contrôle supplémentaire). Je le marque en échec
plutôt que de recompter sur le sous-ensemble applicable — écrire « 6/6 ✔ » aurait
été exact au mot près et trompeur en pratique.

Les **3** candidats non vérifiés publient un tableau
multi-marchés qui n'annonce **ni** nombre de séances **ni** taux d'activation :

- `halloween_effect`
- `intraday_range_regime_overlay`
- `tom_overlay`

Leur `.npz` est produit et lisible ; il n'existe simplement aucun chiffre
déjà publié auquel le confronter. La lacune est dans le rapport d'origine,
et elle est notée plutôt que comblée par une valeur inventée ici.

La prédiction déductive « 0 différence » est **vérifiée** pour la cinquième fois
consécutive. Le chiffre de 17 traités n'est pas tenu non plus : 16 le sont, le
dix-septième étant écarté après lecture pour une raison publiée — ce que
l'engagement 2 prévoyait explicitement.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
