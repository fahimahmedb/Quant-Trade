# Reprise active — historique de surface

STATUT : IN_PROGRESS. L’Owner a autorisé explicitement la reprise. L’audit global et la simplification ne sont pas terminés. Ne pas interrompre la chronologie après un checkpoint intermédiaire.

Méthode retenue : historique de surface systématique, chronologique, journée active par journée active. La lecture profonde de toutes les versions documentaires n’est pas le critère de fin. Cible finale : une branche code et une branche projet/gouvernance ; aucune branche supprimée ou migrée pendant cette phase forensic.

## Reprendre sans recommencer

Lire `resume.json`, `surface/coverage.json`, `surface/days.json`, les récits de surface et le dernier checkpoint durable. Les journées actives **13, 14, 15, 20, 24, 25, 26, 27, 28, 29 juillet ; 4, 5, 6, 7, 13 août ; 1 septembre** sont désormais traitées à la surface : **706 commits** du corpus principal plus les traces GitHub datées associées. Prochaine journée active : **2 septembre 2026**.

Dernier checkpoint durable : `surface/CHECKPOINT_2026-08-06_2026-09-01.md`.

Les 6 393 commits et 111 journées calendaires sont indexés, pas tous revus. 13 471 occurrences de sources au total, dont 969 sans date exploitable dans ce registre ; beaucoup sont des apparitions de commits dans des timelines. Les associer via le SHA lorsque possible tout en conservant l’absence d’heure GitHub, sinon UNKNOWN. Ne pas compter plusieurs représentations comme événements indépendants.

Conclusions déjà durables : les labels `PASS`/`FINAL`/`DEPLOYMENT READY` ne valent pas autorité seuls ; les FAIL et fermetures de familles doivent être conservés comme connaissance négative ; une idée de recherche doit être vérifiée comme nouvelle avant admission ; `restaurant-stock/` est un sous-projet autonome hors périmètre Quant-Trade et prouve que récence/présence dans le dépôt ne suffit pas à sélectionner le tronc.

Utiliser les archives et scripts antérieurs ; ne pas recommencer le miroir ou la collecte initiale. Les 52 lectures documentaires et 7 discussions de la méthode profonde sont conservées séparément et ne mesurent pas la couverture de surface. Les anciens rapports d’octobre restent des preuves à réutiliser quand la chronologie y arrivera.

`surface_history.py` reconstruit les traces depuis raw et coverage.sqlite. Sa génération initialise days.json/coverage.json : sauvegarder et réappliquer les statuts courants avant toute régénération, ne pas effacer les journées traitées. Le script et le récit sont publiés ici ; les gros objets bruts restent dans les archives GitHub déjà vérifiées. `RESUME.md` décrit leur restauration et les limites de collecte, mais son ancienne méthode/pause est remplacée pour le parcours courant par le présent fichier et `resume.json`.

Poursuivre depuis le **2 septembre**, puis chaque journée dans l’ordre, rattacher demandes/décisions/code/tests rapportés/intégrations/retraits et références ; approfondir seulement les ambiguïtés utiles à la réutilisation. Toutes les **4 journées actives**, publier un checkpoint durable de reprise puis continuer immédiatement. Terminer ensuite la carte des capacités et le plan des deux branches. Ne pas sélectionner le tronc par nom/date/ascendance seule. Aucun essai rejoué, aucun runtime modifié, aucun nettoyage destructif.

À une future demande d’arrêt : terminer uniquement le lot borné en cours, publier récit/objets traités/objets restants/curseur, relire les publications puis s’arrêter. Le dernier checkpoint publié et vérifié est l’autorité de reprise de la méthode de surface.
