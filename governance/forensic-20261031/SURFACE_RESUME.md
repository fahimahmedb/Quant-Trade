# Arrêt Owner — historique de surface

STATUT : PAUSED_BY_OWNER. L’Owner a demandé l’arrêt après le premier lot. L’audit global et la simplification ne sont pas terminés. Ne pas continuer automatiquement.

Méthode retenue : historique de surface systématique, chronologique, jour par jour. La lecture profonde de toutes les versions documentaires n’est plus le critère de fin. Cible finale : une branche code et une branche projet/gouvernance ; aucune branche supprimée ou migrée dans ce lot.

## Reprendre sans recommencer

Lire resume.json, surface/coverage.json, surface/days.json puis surface/JULY_SURFACE.md. Les 13, 14, 15 et 20 juillet sont traités à la surface : 25 commits et les traces GitHub datées associées. Prochaine journée active : **24 juillet 2026**. Quatre journées actives traitées, pas quatre journées consécutives ; les autres restent dans days.json avec leurs statuts.

Les 6 393 commits et 111 journées calendaires sont indexés, pas tous revus. 13 471 occurrences de sources au total, dont 969 sans date exploitable dans ce registre ; beaucoup sont des apparitions de commits dans des timelines. Les associer via le SHA lorsque possible tout en conservant l’absence d’heure GitHub, sinon UNKNOWN. Ne pas compter plusieurs représentations comme événements indépendants.

Utiliser les archives et scripts antérieurs ; ne pas recommencer le miroir ou la collecte initiale. Les 52 lectures documentaires et 7 discussions de la méthode profonde sont conservées séparément et ne mesurent pas la couverture de surface. Les anciens rapports d’octobre restent des preuves à réutiliser quand la chronologie y arrivera.

surface_history.py reconstruit les traces depuis raw et coverage.sqlite. Sa génération initialise days.json/coverage.json : **sauvegarder et réappliquer les statuts courants avant toute régénération**, ne pas effacer les journées traitées. Le script et le récit sont publiés ici ; les gros objets bruts restent dans les archives GitHub déjà vérifiées. RESUME.md décrit leur restauration et les limites de collecte, mais son ancienne méthode/pause est remplacée pour le parcours courant par le présent fichier et resume.json.

À la reprise autorisée : parcourir le 24 juillet, puis chaque journée dans l’ordre, rattacher demandes/décisions/code/tests rapportés/intégrations/retraits et références ; approfondir seulement les ambiguïtés utiles à la réutilisation. Terminer ensuite la carte des capacités et le plan des deux branches. Ne pas sélectionner le tronc par nom/date/ascendance seule. Aucun essai rejoué, aucun runtime modifié, aucun nettoyage destructif.

À la prochaine demande d’arrêt : terminer uniquement le lot borné, publier récit/objets traités/objets restants/curseur, relire les publications puis s’arrêter. Le commit contenant ce fichier est le checkpoint ; le routeur de la branche par défaut fournit son lien immuable.
