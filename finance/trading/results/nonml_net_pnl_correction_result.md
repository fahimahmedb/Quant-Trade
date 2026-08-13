# Correction de `net_pnl` dans le balayage de doublons (pré-enregistré)

**Cycle de MODIFICATION.** Contrairement aux #442-#444 qui ne faisaient que
lire, celui-ci change du code et régénère un rapport publié. La ligne changée,
l'effet attendu et le critère d'échec étaient déclarés avant toute mesure.

## La modification

Suppression des **lignes 40-42** de `nonml_pnl_duplicate_sweep_backtest.py` :

```python
if {"pnl_candidate", "turn_candidate"} <= files:
    return (np.asarray(d["pnl_candidate"], dtype=float)
            - np.asarray(d["turn_candidate"], dtype=float) * c), "candidat+turnover"
```

`pnl_candidate` est enregistré **déjà net** par ses producteurs ; cette branche
soustrayait les coûts une seconde fois. La branche suivante (« candidat seul »)
le lit correctement — supprimer suffit, sans rien réécrire.

**`git diff` : 3 suppressions, 0 insertion**, toutes dans l'intervalle annoncé.

## Ce qui change dans les séries

- séries lues **avant** : **218**
- séries lues **après** : **218**
- séries **modifiées** : **1**
- séries apparues / disparues : **0** / **0**

| Série modifiée | schéma avant | schéma après | écart à `pnl_candidate` après |
|---|---|---|---|
| `nonml_dollar_neutral_composite_pit` | candidat+turnover | candidat seul | **0.0e+00** |

L'écart nul n'est pas « petit » : la série lue est désormais **exactement**
`pnl_candidate`, comme le critère 3 l'exigeait.

## Ce qui change dans les groupes de doublons

| | Avant | Après | Identique |
|---|---|---|---|
| paires **exactes** | 3 | 3 | **oui** |
| paires **quasi** (corr ≥ 0.9999) | 1 | 1 | **oui** |
| **groupes** de doublons | 3 | 3 | **oui** |

**Aucun appariement ne bouge.** La prédiction du pré-enregistrement est
**vérifiée** : la série corrigée n'était appariée à rien avant, et ne l'est
pas davantage après.

C'est le résultat **ennuyeux** des deux possibles, et il était annoncé comme
tel. L'autre — un doublon masqué par le défaut — aurait été plus important
que la correction elle-même ; il n'a pas eu lieu.

## Le rapport publié du balayage — avant / après

Ré-exécuter le balayage réécrit `results/nonml_pnl_duplicate_sweep_result.md`.
Le pré-enregistrement l'annonçait et engageait à publier **chaque** ligne
modifiée.

- lignes avant : **96** — lignes après : **92** (écart -4)
- lignes **modifiées** : **10**

**1 ligne imputable à la correction ; 9 à la dérive du
dépôt** — le rapport était **périmé avant ce cycle** : il datait
d'un état où le dépôt comptait moins de scripts. Régénérer l'a rafraîchi,
indépendamment de ma modification.

| Ligne | Cause | Avant | Après |
|---|---|---|---|
| 28 | dérive | `| scripts de backtest non-ML du dépôt | **284** |` | `| scripts de backtest non-ML du dépôt | **298** |` |
| 29 | dérive | `| **couverture non-ML** | **73.2 %** |` | `| **couverture non-ML** | **69.8 %** |` |
| 31 | dérive | `**La soustraction 284 − 208 ne compte rien de réel** : les deux` | `**La soustraction 298 − 208 ne compte rien de réel** : les deux` |
| 36 | dérive | `> **99** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` | `> **113** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` |
| 43 | dérive | `| FAIL | **90** |` | `| FAIL | **91** |` |
| 44 | dérive | `| PASS | **2** |` | `| PASS | **4** |` |
| 45 | dérive | `| indéterminé | **6** |` | `| indéterminé | **17** |` |
| 48 | dérive | `Les **90** FAIL ne peuvent pas changer de verdict, mais un doublon` | `Les **91** FAIL ne peuvent pas changer de verdict, mais un doublon` |
| 50 | dérive | `**2** PASS sont les deux candidats écartés au #427 avec leur raison` | `**4** PASS sont les deux candidats écartés au #427 avec leur raison` |
| 58 | **correction** | `Répartition par schéma : indiciel (182), panier (21), deux jambes (13), candidat+turnover (1), ` | `Répartition par schéma : indiciel (182), panier (21), deux jambes (13), candidat seul (2).` |

Confondre les deux causes aurait été facile et faux : neuf de ces dix lignes
auraient bougé **sans que je touche à rien**, par simple ré-exécution. C'est
le phénomène des rapports dépendants du dépôt (#436-#439), rencontré ici
pour la première fois **au cours d'une modification** — où il brouille
précisément la lecture de l'effet réel.

### Une incohérence exposée par le rafraîchissement

Le rapport régénéré contient désormais :

> **4** PASS sont les deux candidats écartés au #427 avec leur raison

Le compte est **calculé**, la prose (« les deux ») est **figée**. Tant que
le compte valait 2, la phrase était juste ; la dérive du dépôt l'a rendue
fausse. Ce n'est **pas** un effet de ma correction.

**Je ne la corrige pas ici.** Le pré-enregistrement n'autorisait qu'une
modification, aux lignes 40-42 d'un autre fichier ; toucher à cette
phrase serait une modification non déclarée — exactement ce que le
régime de modification annoncé interdit. Elle est **inscrite à la file**.

## Verdict

Critère pré-enregistré, quatre points :

| | Point | État |
|---|---|---|
| 1 | `git diff` = 3 suppressions, 0 insertion, dans l'intervalle | ✔ |
| 2 | chaque différence identifiée et publiée | ✔ |
| 3 | lecture exacte de `pnl_candidate` après correction | ✔ |
| 4 | audit indépendant retrouve les groupes | voir `nonml_net_pnl_correction_audit.md` |

**Le verdict final est celui de l'audit** : le point 4 ne peut pas être
auto-attesté par le script qui applique la correction.

## Portée — ce que ce cycle ne fait pas

- **Aucun verdict de stratégie n'est recalculé.** Les rapports de stratégie
  n'utilisent pas cette fonction ; elle ne sert qu'aux balayages.
- `nonml_leaders_trend_union_pnl_persistence_audit.py` (second D du #444) est
  corrigé **par ricochet** puisqu'il appelle `sw.main()`. Son rapport n'est
  **pas** régénéré ici — ce serait une modification non déclarée.
- Les **3 consommateurs de catégorie C** du #444 restent inchangés : lacune de
  couverture, pas défaut.
