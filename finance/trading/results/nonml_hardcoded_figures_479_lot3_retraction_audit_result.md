# Audit indépendant — #527, rétractation appliquée à sa source

Route distincte du backtest : `git show` sur les deux révisions (avant/après le commit de réparation), lecture textuelle directe de l'entrée `V` — pas d'AST, pas d'import du module.

## L'entrée `V`, avant et après le commit de réparation

- avant (`e8690a6~1`) : **defaut**
- après (`e8690a6`) : **legitime**

- confirme la correction annoncée (defaut → legitime) : **OUI**

## Le diff, vérifié borné à 1 entrée

- entrées `V` supprimées dans le diff : **1** (attendu : 1)
- rapport `nonml_hardcoded_figures_remainder_result.md` absent du commit : **OUI**

**PASS** — la route indépendante (git show sur les deux révisions) confirme la correction et son périmètre borné.
