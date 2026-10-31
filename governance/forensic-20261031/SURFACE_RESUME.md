# Reprise active — historique de surface

STATUT : IN_PROGRESS. L’Owner a autorisé explicitement la reprise. L’audit global et la simplification ne sont pas terminés. Ne pas interrompre la chronologie après un checkpoint intermédiaire.

Méthode retenue : historique de surface systématique, chronologique, journée active par journée active. La lecture profonde de toutes les versions documentaires n’est pas le critère de fin. Cible finale : une branche code et une branche projet/gouvernance ; aucune branche supprimée ou migrée pendant cette phase forensic.

## Reprendre sans recommencer

Les **40 premières journées actives** sont traitées à la surface jusqu’au **30 septembre inclus** : **2 123 commits** plus les traces GitHub datées associées. Prochaine journée active : **1 octobre 2026**. Dernier checkpoint : `surface/CHECKPOINT_2026-09-27_2026-09-30.md`.

Les 6 393 commits et 111 journées calendaires sont indexés, pas tous revus. 13 471 occurrences de sources au total, dont 969 sans date exploitable. Ne pas compter plusieurs représentations comme événements indépendants.

État durable : `restaurant-stock/` hors périmètre ; Rail C paper/shadow adopté sans autorité capital ; SAFE_RAIL/HISTORICAL_PIT/CI_ONLY restent distincts ; `REAL_CAPITAL` et `FIXED_COST_BASE` sont des inconnus économiques décisifs ; `REAL_CAPITAL_AUTHORIZED = FALSE`.

Data : le workflow `data feeds` est owner-approved et planifié depuis la branche par défaut, mais checkout/exécute la branche data dédiée. Il collecte des données publiques append-only et n’envoie aucun ordre. Les commits automatiques `quant-data-feeds` doivent être compressés en une seule capacité `SCHEDULED_DATA_COLLECTION`.

Science : les résultats négatifs sont des sorties à conserver. La correction Weather R3 du 30 septembre supersède les labels prospectifs antérieurs : sans bridge gelé `theta_W -> theta_P`, aucune étiquette prospective inconditionnelle ; utiliser une frontière de transport et un `SHADOW_CONTINUATION_SIGNAL`.

Pattern de continuité : petite surface de reprise vivante + handoffs/checkpoints/règles canoniques + preuves exact-head + statuts d’autorité explicites. Réutiliser les archives existantes ; ne pas recommencer la collecte.

Poursuivre depuis le **1 octobre**, puis dans l’ordre. Toutes les **4 journées actives**, publier un checkpoint durable et continuer immédiatement. Terminer ensuite la carte des capacités et le plan des deux branches. Aucun essai rejoué, aucun runtime modifié, aucun nettoyage destructif pendant cette phase.
