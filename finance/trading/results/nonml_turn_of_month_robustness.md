# Robustesse — Effet tournant de mois (grille de plausibilité, PAS un retuning)

Fenêtre pré-enregistrée (4j/3j) au centre de la grille ; ±1 jour testé pour vérifier un plateau. Le verdict PASS officiel reste celui de 4j/3j (`results/nonml_turn_of_month_result.md`) — ceci est diagnostique uniquement.

| Fenêtre (derniers/premiers) | Nb marchés où ToM bat BH (/5) |
|---|---|
| 3j / 2j | 3/5 |
| 4j / 3j | 4/5 ← spécification pré-enregistrée |
| 5j / 4j | 3/5 |

**Lecture** : si les résultats voisins (3j/2j et 5j/4j) restent proches de 4/5 ou 5/5, l'effet est un plateau plausible, pas un pic isolé sur la définition académique exacte. Un effondrement à 0-1/5 sur les fenêtres voisines indiquerait au contraire une définition très fragile.
