# Reprise active — historique de surface

STATUT : IN_PROGRESS. L’Owner a autorisé explicitement la reprise. L’audit global et la simplification ne sont pas terminés. Ne pas interrompre la chronologie après un checkpoint intermédiaire.

Méthode retenue : historique de surface systématique, chronologique, journée active par journée active. La lecture profonde de toutes les versions documentaires n’est pas le critère de fin. Cible finale : une branche code et une branche projet/gouvernance ; aucune branche supprimée ou migrée pendant cette phase forensic.

## Reprendre sans recommencer

Les **36 premières journées actives** sont traitées à la surface jusqu’au **25 septembre inclus** : **1 905 commits** plus les traces GitHub datées associées. Prochaine journée active : **27 septembre 2026**. Dernier checkpoint : `surface/CHECKPOINT_2026-09-21_2026-09-25.md`.

Les 6 393 commits et 111 journées calendaires sont indexés, pas tous revus. 13 471 occurrences de sources au total, dont 969 sans date exploitable. Ne pas compter plusieurs représentations comme événements indépendants.

Conclusions durables : `restaurant-stock/` reste hors périmètre ; les labels et métriques ne valent pas autorité seuls ; les FAIL, contaminations et conclusions supersédées restent mémorisés. PR #16 et PR #18 sont intégrées dans leurs lignées respectives ; PR #17, #19 et #20 sont fermées sans merge / CI-only selon leur rôle ; Gate B et t0 ne sont pas inférés d’un CI vert.

Économie : la fermeture R3 fondée sur une illustration 10k est `SUPERSEDED`. Le dépôt suppose 1M de capital de simulation mais ne prouve aucun capital réel. `REAL_CAPITAL` et `FIXED_COST_BASE` restent `UNKNOWN_DECISIVE`; `REAL_CAPITAL_AUTHORIZED = FALSE`.

Recherche : Rail C fast research est adopté par Blue le 25 septembre sur `bd197126...`, en paper/shadow, budget 10 itérations / 200 trials / 5 agents, sans toucher le rail sûr ; transfert au rail sûr à `FORWARD_PASS` avec décision Owner. La PR #21 reste une proposition non mergée et le cleanup n’est pas validé par l’adoption. Une voie `HISTORICAL_PIT_VALIDATION` existe séparément et doit rester firewalled de la prospective lineage.

Pattern de continuité à préserver : une petite surface de reprise vivante (mission, état, réacquisition) + handoffs/checkpoints/règles canoniques + preuves exact-head + statuts d’autorité explicites. Réutiliser les archives existantes ; ne pas recommencer la collecte.

Poursuivre depuis le **27 septembre**, puis dans l’ordre. Toutes les **4 journées actives**, publier un checkpoint durable et continuer immédiatement. Terminer ensuite la carte des capacités et le plan des deux branches. Aucun essai rejoué, aucun runtime modifié, aucun nettoyage destructif pendant cette phase.
