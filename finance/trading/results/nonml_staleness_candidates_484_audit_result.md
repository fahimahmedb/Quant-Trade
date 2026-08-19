# Audit indépendant — #525, les 2 reclassements MASQUANT → ANODIN

Route distincte du backtest : `grep -n` externe (pas d'AST) pour
retrouver les occurrences de la variable, et `git show` pour
vérifier le diff réellement committé du dictionnaire `V` et
l'absence de tout diff sur le rapport du #484. Même forme que
l'audit du #524.

## Occurrences de chaque variable, par grep externe

### `nonml_six_reports_regeneration_backtest.py` — `perdus`

- occurrences dans un `L.append(` (grep externe) : [231, 236]
- ligne de la garde `if perdus:` (grep externe) : 233
- première référence en `L.append(` avant la garde : **OUI** (l.231)

> Confirme, par une route indépendante, qu'une référence inconditionnelle à `perdus` existe **avant** la garde — le MASQUANT ne peut pas tenir.

### `nonml_sweep_pass_prose_fix_backtest.py` — `strategies`

- occurrences dans un `L.append(` (grep externe) : [133, 142]
- ligne de la garde `if strategies:` (grep externe) : 135
- première référence en `L.append(` avant la garde : **OUI** (l.133)

> Confirme, par une route indépendante, qu'une référence inconditionnelle à `strategies` existe **avant** la garde — le MASQUANT ne peut pas tenir.

## Le diff committé, vérifié via `git show`

- le commit de réparation touche-t-il le rapport `nonml_guards_witness_remainder_result.md` : **NON**

> Confirme que le rapport du #484 n'a pas été régénéré ni committé, comme annoncé — seul le dictionnaire `V` a changé.

**PASS** — la route indépendante (grep externe + git show) confirme les 2 reclassements et l'absence de régénération du rapport.
