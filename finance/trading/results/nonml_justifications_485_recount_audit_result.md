# Audit indépendant — #517, recompte des justifications du #485

Route de calcul différente du backtest : bornes de section retrouvées
par `grep -n` sur les en-têtes plutôt que par découpage regex en
mémoire ; présence de chaque nom testée par simple `in` sur le bloc de
lignes plutôt que par une fenêtre de proximité à un marqueur.

## Recalcul vs publié

| Grandeur | Recalculée | Publiée | Accord |
|---|---|---|---|
| 5 noms == tableau attendu | OUI | OUI | **OUI** |
| script du #511 hors des 5 | OUI | OUI | **OUI** |
| cycles #511-#516 avec la phrase | 6 | 6 | **OUI** |

| couverture stricte (présence brute, sans fenêtre de proximité) | 5/5 | 4/5 (règle de proximité) | **voir note** |

> Cette dernière ligne n'est **pas** un désaccord : la route de
> l'audit teste une présence **brute** du nom dans la section (plus
> permissive que la fenêtre de 400 caractères du backtest), donc
> **5/5** ici est attendu même si le backtest, avec sa règle plus
> stricte, publie 4/5 avant sa note de couverture élargie en prose.
> Les deux routes s'accordent sur le fond : les 5 noms apparaissent
> tous dans #488 ou #493.

- `protocol_inventory_audit` : présent dans #493 = **True**, présent dans #488 = **False**
- `marker_emitted_by_scripts` : présent dans #493 = **True**, présent dans #488 = **False**
- `pnl_duplicate_sweep_audit` : présent dans #493 = **False**, présent dans #488 = **True**
- `pnl_persistence_exposed_pass_audit` : présent dans #493 = **True**, présent dans #488 = **False**
- `reproducibility_campaign_v3_lot2_audit` : présent dans #493 = **True**, présent dans #488 = **False**

**PASS** — les grandeurs vérifiables à l'identique par cette route indépendante sont reproduites.
