# Reprise active — historique de surface

STATUT : IN_PROGRESS. L’Owner a autorisé explicitement la reprise. L’audit global et la simplification ne sont pas terminés. Ne pas interrompre la chronologie après un checkpoint intermédiaire.

Méthode retenue : historique de surface systématique, chronologique, journée active par journée active. La lecture profonde de toutes les versions documentaires n’est pas le critère de fin. Cible finale : une branche code et une branche projet/gouvernance ; aucune branche supprimée ou migrée pendant cette phase forensic.

## Reprendre sans recommencer

Les **32 premières journées actives** sont traitées à la surface jusqu’au **20 septembre inclus** : **1 484 commits** plus les traces GitHub datées associées. Prochaine journée active : **21 septembre 2026**. Dernier checkpoint : `surface/CHECKPOINT_2026-09-17_2026-09-20.md`.

Les 6 393 commits et 111 journées calendaires sont indexés, pas tous revus. 13 471 occurrences de sources au total, dont 969 sans date exploitable. Ne pas compter plusieurs représentations comme événements indépendants.

Conclusions durables : `restaurant-stock/` reste hors périmètre ; les métriques/labels ne valent pas autorité seuls ; les FAIL et contaminations restent mémorisés. Le noyau Quant se structure en gouvernance/science, whole-system code et Evidence/Data. PR #16 est mergée dans la lignée Blue ; PR #17 est fermée sans merge ; PR #18 est mergée dans une lignée Astra ; Gate A est exact-head green sur `e5c4c720...`. La fuite de visibilité du 18 septembre est irréversible pour la fenêtre touchée. `t0` reste distinct d'un CI vert et n'est pas déduit automatiquement.

Pattern de continuité à préserver : feature-plans + handoffs + checkpoints/règles canoniques + preuves exact-head + statuts d'autorité explicites. Réutiliser les archives existantes ; ne pas recommencer la collecte.

Poursuivre depuis le **21 septembre**, puis dans l’ordre. Toutes les **4 journées actives**, publier un checkpoint durable et continuer immédiatement. Terminer ensuite la carte des capacités et le plan des deux branches. Aucun essai rejoué, aucun runtime modifié, aucun nettoyage destructif pendant cette phase.
