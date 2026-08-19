# Audit indépendant — #519, bilan des témoins et usages de `en_gras_dans`

Route distincte du backtest : `grep -rl` en processus externe (pas
de lecture Python + regex interne) pour recompter les appelants, et
relecture directe du rapport source du #515
(`nonml_untested_detectors_lift_result.md`) pour vérifier que le
lift de D501 (1,5) y est bien publié tel quel, sans passer par le
backtest de ce cycle.

## Recompte des appelants de `en_gras_dans`, par `grep -rl`

- fichiers trouvés (hors définition et hors ce script) : **3**
  - `nonml_borrowed_figures_confrontation_audit.py`
  - `nonml_contextual_confrontation_backtest.py`
  - `nonml_untested_detectors_lift_backtest.py`

- nombre publié par le backtest : **3**
- accord : **OUI**

## Le lift de D501 (1,5), retrouvé dans sa source (#515), pas recopié

- occurrences de `lift` suivies d'un nombre dans le rapport du #515 : ['6,4', '12,1']
- le rapport du #515 contient-il littéralement « 1,5 » : **OUI**

**PASS** — la route indépendante (grep externe + relecture directe de la source du #515) reproduit les grandeurs publiées par le backtest.
