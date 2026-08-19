# Audit indépendant — #526, traçabilité de la citation « 16 et 2 »

Route distincte du backtest : la section `## Backlog #463` est
extraite dans un fichier temporaire (bornes de ligne trouvées par
balayage Python simple, pas par regex de découpage), puis chaque
radical est compté par `grep -c` en processus externe.

## Recompte

- `FAUTIFS_463` retrouvés (sur 2) : **2**
- `SAINS_463` retrouvés (sur 16) : **0**
- total retrouvé : **2 / 18**

- accord avec le backtest (2 FAUTIFS trouvés, 0 SAINS trouvé) : **OUI**

## Le diff committé, vérifié via `git show`

- occurrences de clés `V` supprimées dans le diff : **1** (attendu : 1)
- le rapport `nonml_hardcoded_figures_remainder_result.md` est-il absent du commit : **OUI**

**PASS** — la route indépendante (extraction de section + grep -c externe, et git show) confirme le compte 2/18 et le diff borné à 1 entrée.
