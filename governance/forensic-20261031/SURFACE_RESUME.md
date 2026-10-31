# Reprise active — historique de surface

STATUT : IN_PROGRESS. L’Owner a autorisé explicitement la reprise. L’audit global et la simplification ne sont pas terminés. Ne pas interrompre la chronologie après un checkpoint intermédiaire.

Méthode retenue : historique de surface systématique, chronologique, journée active par journée active. La lecture profonde de toutes les versions documentaires n’est pas le critère de fin. Cible finale : une branche code et une branche projet/gouvernance ; aucune branche supprimée ou migrée pendant cette phase forensic.

## Reprendre sans recommencer

Lire `resume.json`, `surface/coverage.json`, `surface/days.json`, les récits de surface et le dernier checkpoint durable. Les **28 premières journées actives** sont désormais traitées à la surface, jusqu’au **15 septembre inclus** : **1 030 commits** du corpus principal plus les traces GitHub datées associées. Prochaine journée active : **17 septembre 2026**.

Dernier checkpoint durable : `surface/CHECKPOINT_2026-09-12_2026-09-15.md`.

Les 6 393 commits et 111 journées calendaires sont indexés, pas tous revus. 13 471 occurrences de sources au total, dont 969 sans date exploitable. Ne pas compter plusieurs représentations comme événements indépendants.

Conclusions déjà durables : les labels `PASS`/`FINAL`/`DEPLOYMENT READY` ne valent pas autorité seuls ; les FAIL et fermetures de familles doivent être conservés ; une idée doit être prouvée nouvelle avant admission ; `restaurant-stock/` est hors périmètre. Depuis le 12 septembre, le noyau Quant se recompose en trois familles : gouvernance/science, whole-system runtime/code et Evidence/Data. Les PR #12/#13 sont fermées sans merge mais portent des invariants V1 à préserver ; Builder C Evidence/PIT a un exact-head green sur `b8f7dff...` ; le census SEC reste rouge à cette date. Le pattern durable `feature-plans` + `handoffs` + checkpoints/règles canoniques doit être réutilisé pour empêcher les pertes de mémoire.

Utiliser les archives et scripts antérieurs ; ne pas recommencer le miroir ou la collecte initiale. Les anciens rapports d’octobre restent des preuves à réutiliser quand la chronologie y arrivera.

Poursuivre depuis le **17 septembre**, puis chaque journée dans l’ordre. Toutes les **4 journées actives**, publier un checkpoint durable et continuer immédiatement. Terminer ensuite la carte des capacités et le plan des deux branches. Ne pas sélectionner le tronc par nom/date/ascendance seule. Aucun essai rejoué, aucun runtime modifié, aucun nettoyage destructif.
