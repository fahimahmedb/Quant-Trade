# Reprise active — historique de surface

STATUT : IN_PROGRESS. L’Owner a autorisé explicitement la reprise. L’audit global et la simplification ne sont pas terminés. Ne pas interrompre la chronologie après un checkpoint intermédiaire.

Méthode retenue : historique de surface systématique, chronologique, journée active par journée active. La lecture profonde de toutes les versions documentaires n’est pas le critère de fin. Cible finale : une branche code et une branche projet/gouvernance ; aucune branche supprimée ou migrée pendant cette phase forensic.

## Reprendre sans recommencer

Les **44 premières journées actives** sont traitées à la surface jusqu’au **4 octobre inclus** : **2 232 commits** plus les traces GitHub datées associées. Prochaine journée active : **5 octobre 2026**. Dernier checkpoint : `surface/CHECKPOINT_2026-10-01_2026-10-04.md`.

Les 6 393 commits et 111 journées calendaires sont indexés, pas tous revus. 13 471 occurrences de sources au total, dont 969 sans date exploitable. Ne pas compter plusieurs représentations comme événements indépendants.

État durable : `restaurant-stock/` hors périmètre ; Rail C paper/shadow adopté sans autorité capital ; SAFE_RAIL/HISTORICAL_PIT/CI_ONLY restent distincts ; `REAL_CAPITAL` et `FIXED_COST_BASE` sont des inconnus économiques décisifs ; `REAL_CAPITAL_AUTHORIZED = FALSE`.

Data : le workflow `data feeds` est owner-approved et planifié depuis la branche par défaut, mais checkout/exécute la branche data dédiée. Les commits automatiques `quant-data-feeds` sont des observations append-only à compresser en une seule capacité `SCHEDULED_DATA_COLLECTION`, pas de nouveaux modules.

Science : la correction Weather R3 du 30 septembre supersède les labels prospectifs antérieurs. Weather V3 devient une campagne orchestrée le 2 octobre. Le 4 octobre, Astra persiste un pré-op audit PASS avec qualifications puis l’Owner n’autorise qu’une phase A1 documentation bornée : `PRE_OP_PASS != EXECUTION_AUTHORITY`.

Temporalité : les dates contenues dans les noms de branches ne font pas foi. Exemple vérifié : `codex/weather-v3-s0-finish-2026-10-03` a un head committé le 2 octobre. Utiliser les dates Git/événements primaires.

Inconnu conservé : le détail des 21 commits non-feed du 1 octobre reste `UNKNOWN_DETAIL_NOT_BLOCKING`; ne pas inventer de capacité ou d’autorité pour combler cette lacune.

Pattern de continuité : petite surface de reprise vivante + handoffs/checkpoints/règles canoniques + preuves exact-head + statuts d’autorité explicites. Réutiliser les archives existantes ; ne pas recommencer la collecte.

Poursuivre depuis le **5 octobre**, puis 6, 7 et 8 octobre. Toutes les **4 journées actives**, publier un checkpoint durable et continuer immédiatement. Aucun essai rejoué, aucun runtime modifié, aucun nettoyage destructif pendant cette phase.
