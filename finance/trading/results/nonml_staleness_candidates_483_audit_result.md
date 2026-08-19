# Audit indépendant — #523, les 2 candidats du #483

Route distincte du backtest : réimplémentation propre de `classer()` (fichier PREREG lu en entier, pas seulement 12 lignes), et `grep -c` externe pour confirmer que l'axe d'évaluation du #518 (« le chiffre cité par le #485 ») est bien absent de tout vocabulaire lié à `MOTS`.

## `coverage_wording_fix`

- classement recalculé (route indépendante) : **RÉSULTAT ATTENDU**, déclaration lue : « outillage documentaire »
- toujours orphelin : **OUI**
- MAL CLASSÉ tient (recalculé indépendamment) : **OUI**
- accord avec le rapport publié : **OUI**

## `duplicate_sweep_coverage`

- classement recalculé (route indépendante) : **RÉSULTAT ATTENDU**, déclaration lue : « outillage documentaire »
- toujours orphelin : **OUI**
- MAL CLASSÉ tient (recalculé indépendamment) : **OUI**
- accord avec le rapport publié : **OUI**

## L'axe du #518, confirmé par grep externe sur le fichier réel

- occurrences de « le chiffre cité par le #485 » dans le backlog entier : **1**
- présence confirmée : **OUI** — l'expression employée au #518 pour caractériser son propre axe d'évaluation existe bien littéralement dans le backlog.

**PASS** — la route indépendante (relecture PREREG complète + grep externe) reproduit les conclusions du backtest pour les 2 candidats.
