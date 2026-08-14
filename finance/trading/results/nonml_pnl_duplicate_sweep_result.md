# Balayage des doublons de P&L du backlog (pré-enregistré)

Diagnostic, pas une stratégie. Reconstruit le P&L net de **tous** les
`results/*_pnl.npz` du dépôt et cherche les paires identiques ou quasi
identiques. Critères fixés avant exécution : égalité exacte
(`np.array_equal`) ou corrélation ≥ 0.9999.

## Couverture

- fichiers `*_pnl.npz` trouvés : **219**
- P&L reconstruits : **219**
- schémas non reconnus ou séries inexploitables : **0**

**100 % des fichiers trouvés ont été relus** — critère 1 du pré-enregistrement
atteint. Ce taux ne mesure pas la couverture du dépôt : voir juste en dessous.

### Ce que « 100 % » recouvre — et ce qu'il ne recouvre pas

Le taux ci-dessus dit que **tous les fichiers trouvés ont pu être relus**. Il ne
dit pas que le balayage voit tout le dépôt, ni que toutes les séries lues sont
des candidats non-ML. Les deux précisions manquaient jusqu'au cycle #428 :

| | Nombre |
|---|---|
| séries lues (`results/*_pnl.npz`) | **219** |
| dont candidats non-ML (`nonml_*`) | **209** |
| dont séries **ML / Étape D** | **10** |
| scripts de backtest non-ML du dépôt | **305** |
| **couverture non-ML** | **68.5 %** |

**La soustraction 305 − 209 ne compte rien de réel** : les deux
ensembles ne se correspondent pas un à un. Certains `.npz` portent le nom d'une
**variante** (`*_pit_universe`, `*_russell2000`…) sans script homonyme — il y en a
**23**. La différence ensembliste est donc la seule mesure valide :

> **119** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et
> échappent à toute détection de doublon.

Leur verdict publié, compté et non supposé :

| Verdict des scripts sans `.npz` | Nombre |
|---|---|
| FAIL | **93** |
| PASS | **4** |
| indéterminé | **20** |
| sans rapport | **2** |

Les **93** FAIL ne peuvent pas changer de verdict, mais un doublon
parmi eux gonflerait tout de même le décompte d'hypothèses testées. Les
Les **4** PASS sans `.npz` sont nommés ici plutôt
qu'affirmés — la version précédente les disait « les deux candidats écartés
au #427 », phrase figée qu'un compte calculé a fini par démentir (#446) :

- `marker_emitted_by_scripts`
- `six_reports_regeneration`
- `verdict_detector_complete`
- `verdict_rule_propagation`


Le balayage lit `results/*_pnl.npz` **sans filtre de préfixe** : les 10 séries
ML / Étape D sont comparées aux candidats non-ML. C'est voulu — un doublon
inter-familles est une information — mais il faut le savoir pour lire les groupes
ci-dessous, dont l'un associe précisément une série d'Étape D à un candidat non-ML.

Répartition par schéma : indiciel (183), panier (21), deux jambes (13), candidat seul (2).

## Doublons exacts

- paires à P&L **bit-à-bit identique** : **3**
- groupes de doublons : **3**
- entrées surnuméraires (essais comptés en trop) : **3**

- **groupe de 2** : `etape_D_overlay_optimized`, `nonml_etape_d_garch_defensive_overlay`
- **groupe de 2** : `nonml_leaders_trend_union_overlay`, `nonml_sma200_leaders_overlay`
- **groupe de 2** : `nonml_leaders_trend_union_overlay_pit_universe`, `nonml_sma200_leaders_overlay_pit_universe`

## Quasi-doublons (corrélation ≥ seuil, non identiques)

- paires signalées : **1**

| Candidat A | Candidat B | Corrélation |
|---|---|---|
| `nonml_momentum_breadth_vol_targeting_overlay` | `nonml_sma200_momentum_breadth_and_overlay` | 0.99990654 |

Ces paires **ne sont pas comptées comme doublons** à ce stade : le critère 2
du pré-enregistrement impose de les confirmer ou de les rejeter par lecture
des deux scripts. Voir l'audit.

## Effet sur le décompte d'essais

Le backlog compte actuellement **372** essais dans le calcul du DSR.
Les doublons exacts en rendent **3** surnuméraires, soit un
décompte corrigé de **369** avant examen des quasi-doublons.

**Aucune correction n'est appliquée dans ce cycle**, conformément au
pré-enregistrement : rejouer les batteries avec un `n_trials` corrigé après
avoir vu quels candidats en bénéficieraient serait précisément ce que le
protocole interdit. Le décompte corrigé est publié, son usage est un cycle
distinct à déclarer.
