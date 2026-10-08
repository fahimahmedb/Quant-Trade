# Boucle d'exploitation de l'équipe A2 — règles de fonctionnement (2026-10-08)

Règles opérationnelles de la file de travail, sans effet sur la réserve permanente. Ajoutées après un temps perdu constaté : Q7 terminée à 00:13, repérée à 00:38.

1. **Premier geste à chaque réveil :** `python3 research/weather_forward/v4/team/a2_team_status.py`. Un nouveau commit sur une branche d'équipe est un signal, même quand l'événement reçu se présente comme une simple fin de CI.
2. **Jamais de fin de tour avec une tâche `READY`.** On la prend, ou on écrit la raison précise du blocage dans la file.
3. **Toute session enfant lancée arme un seul rappel +25 min** (`send_later`) qui vérifie `get_session`, puis se réarme tant qu'elle n'est pas finie. Toute promesse de délai faite à l'autre agent est doublée d'un rappel.
4. **Fin d'une session enfant :** commentaire sur la PR #22 obligatoire (`[A2-TEAM] DE: …`, références exactes). Sans lui, le rappel du point 3 fait foi.
5. **Deux cerveaux, pas une chaîne :**
   - avant l'exécution d'un lot, le contrôleur écrit en une demi-page ce qu'il ferait autrement et le risque principal ; le pilote tranche et consigne l'écart ;
   - pendant que l'un exécute, l'autre a une tâche préparatoire distincte dans la file (pas d'attente) ;
   - le contrôleur ne se limite pas à relire : il produit la partie indépendante (tests adverses, recoupement, contre-lecture).
6. **Mesure :** la fiche de reprise note, par lot, le délai entre la fin d'une tâche et la prise de la suivante. Au-delà de 10 minutes sans cause (quota, Owner), c'est un défaut à corriger.
7. **Codex réfléchit et organise à parts égales.** Le pilote d'un lot tient la file : il en choisit l'ordre, y inscrit les tâches des deux agents et les justifie par la valeur attendue pour l'objectif du projet. Codex pilote P2 (planification) : il rédige la feuille de route et la file ; je l'exécute sauf objection écrite avant exécution. Comme Codex ne peut pas publier, il livre chaque nouvelle version de la file en bloc de code avec son SHA-256, et je la publie à l'identique après vérification. Le pilote suivant (moi) reprend la file de Codex comme base et ne la réécrit pas sans objection motivée.
