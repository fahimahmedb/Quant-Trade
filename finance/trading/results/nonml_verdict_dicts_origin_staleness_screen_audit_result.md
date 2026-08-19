# Audit indépendant — #529, screen de staleness des 2 dictionnaires VERDICTS d'origine

Route distincte du backtest : `grep -c` externe sur un extrait de section isolé par indices de ligne (pas de découpage regex en mémoire unique), même filtre explicite sur la phrase générique de la « Dette restante » que l'audit du #528.

## Recompte des marqueurs, par grep externe

| Script | Radical | Marqueur trouvé (hors dette générique) |
|---|---|---|
| `nonml_citer_451_definition_backtest.py` | `citer_451_definition` | oui |
| `nonml_duplicate_sweep_coverage_audit.py` | `duplicate_sweep_coverage` | oui |
| `nonml_marker_emitted_by_scripts_backtest.py` | `marker_emitted_by_scripts` | oui |
| `nonml_prereg_convention_coverage_backtest.py` | `prereg_convention_coverage` | oui |
| `nonml_protocol_inventory_audit.py` | `protocol_inventory` | oui |
| `nonml_repo_magnitudes_recount_backtest.py` | `repo_magnitudes_recount` | oui |
| `nonml_reproducibility_campaign_v2_backtest.py` | `reproducibility_campaign_v2` | oui |
| `nonml_reproducibility_sample_backtest.py` | `reproducibility_sample` | oui |
| `nonml_reproducibility_sample_lot2_backtest.py` | `reproducibility_sample_lot2` | non |

- scripts avec marqueur trouvé (hors dette générique), route grep externe : **8**

## Comparaison avec le backtest

Le backtest (#529) applique en plus un garde-fou de distance anti-collision (le radical le plus proche du marqueur, parmi tous les radicaux connus, doit être celui du script examiné) : c'est cette étape supplémentaire qui explique que certains scripts marqués ici « oui » (present quelque part dans une section contenant leur radical ET un marqueur) soient en réalité des collisions de proximité (un marqueur sur un autre sujet de la même section) une fois cette distance appliquée -- exactement ce que le backtest a trouvé pour les 5 mêmes candidats préliminaires déclarés dans le PREREG.

- les 4 radicaux distincts retenus par le backtest (`repo_magnitudes_recount` compte deux fois, une par dictionnaire) sont bien parmi les scripts marqués « oui » ici : **OUI**

## Le dictionnaire `VERDICTS` des deux scripts d'origine, confirmé inchangé par le commit du #529

- `nonml_hardcoded_figures_sweep_backtest.py` ou `nonml_conditional_sections_sweep_backtest.py` touché par le commit du #529 : **NON**

> Confirme qu'aucune correction n'a été appliquée aux dictionnaires d'origine — cohérent avec 0 contradiction confirmée par les deux routes.

**PASS** — la route indépendante (grep externe par section isolée, sans la logique de distance en mémoire) retrouve les mêmes 4 radicaux candidats que le backtest, et confirme qu'aucun des deux dictionnaires `VERDICTS` d'origine n'a été modifié par ce commit.
