# Reprise courante : historique de surface, Owner 31 octobre

L’Owner a explicitement repris l’audit avec une nouvelle méthode : suivre TOUS les commits et événements chronologiquement, produire un récit de surface jour par jour. L’ancienne pause et la lecture intégrale des versions ne sont plus le critère courant. Cible finale : une branche code, une branche projet/gouvernance ; aucun retrait de branche maintenant.

Lire resume.json, surface/coverage.json, surface/days.json puis surface/JULY_SURFACE.md. Quatre journées actives traitées à la surface, 25 commits ; prochaine journée active 24 juillet. Les 111 journées sont indexées, pas toutes revues. Les 969 occurrences sans date GitHub restent à associer ou à laisser UNKNOWN sans inventer d’heure ; beaucoup sont des apparitions de commits dans une timeline. Les doublons de représentations ne sont pas des événements indépendants.

surface_history.py reconstruit l’inventaire depuis les objets bruts existants et coverage.sqlite ; avant de le relancer, conserver days.json et coverage.json courants car sa génération initialise les statuts. Réutiliser les scripts/archives et le registre de lectures antérieurs ; ne pas recommencer la collecte initiale. Le précédent RESUME.md reste une description du stockage et de la pause antérieure, pas un ordre de suspendre cette reprise.

À toute demande d’arrêt : finir le lot borné, publier récit/couverture/objets restants/curseur sur la branche d’audit existante, relire la publication puis s’arrêter. Aucun runtime, essai scientifique ou nettoyage destructif pendant cette reconstruction.
