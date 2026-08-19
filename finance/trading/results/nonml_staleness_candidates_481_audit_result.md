# Audit indépendant — #524, les 2 reclassements MASQUANT → ANODIN

Route distincte du backtest : `grep -n` externe (pas d'AST) pour
retrouver les occurrences de la variable, et `git show` pour
vérifier le diff réellement committé du dictionnaire `V` et
l'absence de tout diff sur le rapport du #481.

## Occurrences de chaque variable, par grep externe

### `nonml_battery_coverage_backtest.py` — `indet`

- occurrences dans un `L.append(` (grep externe) : [147, 162]
- ligne de la garde `if indet:` (grep externe) : 159
- première référence en `L.append(` avant la garde : **OUI** (l.147)

> Confirme, par une route indépendante, qu'une référence inconditionnelle à `indet` existe **avant** la garde — le MASQUANT ne peut pas tenir.

### `nonml_net_pnl_correction_backtest.py` — `incoh`

- occurrences dans un `L.append(` (grep externe) : [278]
- ligne de la garde `if incoh:` (grep externe) : 281
- première référence en `L.append(` avant la garde : **OUI** (l.278)

> Confirme, par une route indépendante, qu'une référence inconditionnelle à `incoh` existe **avant** la garde — le MASQUANT ne peut pas tenir.

## Le diff committé, vérifié via `git show`

- le commit de réparation touche-t-il le rapport `nonml_guards_without_witness_result.md` : **NON**

> Confirme que le rapport du #481 n'a pas été régénéré ni committé, comme annoncé — seul le dictionnaire `V` a changé.

**PASS** — la route indépendante (grep externe + git show) confirme les 2 reclassements et l'absence de régénération du rapport.
