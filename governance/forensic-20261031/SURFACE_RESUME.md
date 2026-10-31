# Reprise active — historique de surface

STATUT : IN_PROGRESS. L’Owner a autorisé explicitement la reprise. L’audit global et la simplification ne sont pas terminés. Ne pas interrompre la chronologie après un checkpoint intermédiaire.

## Curseur durable

Les **52 premières journées actives** sont traitées jusqu’au **12 octobre inclus** : **2 762 commits** plus les traces GitHub datées associées. Prochaine journée active : **13 octobre 2026**. Dernier checkpoint : `surface/CHECKPOINT_2026-10-09_2026-10-12.md`.

Méthode : `CHRONOLOGICAL_SURFACE`. Toutes les quatre journées actives, publier un checkpoint puis continuer. Les 6 393 commits / 111 journées / 13 471 occurrences restent l’inventaire initial ; indexé n’est pas relu intégralement.

## État réutilisable

- `restaurant-stock/` est hors périmètre Quant.
- `SCHEDULED_DATA_COLLECTION` représente la collecte planifiée ; les snapshots automatiques ne sont pas des modules.
- Rails : `SAFE_RAIL_PROSPECTIVE`, `FAST_RAIL_C_PAPER_SHADOW`, `HISTORICAL_PIT_VALIDATION`, `CI_ONLY_AUDIT_SURFACES`.
- `REAL_CAPITAL_AUTHORIZED = FALSE`; `REAL_CAPITAL` et `FIXED_COST_BASE` restent inconnus décisifs.
- Weather R3 du 30 septembre supersède l’ancien label prospectif inconditionnel.
- Weather V4 A2 reste une lignée d’états : root candidate présent au 8 octobre mais `E_EFFECTIVE = FALSE`; aucune activation démontrée.

Nouveau rail à compresser : `EDGE_LAB_SINGLE_USE_RESEARCH_LOOP`. Préserver réservations atomiques, receipt single-use, outcome provenance et non-rerun ; ne pas conserver chaque heartbeat comme architecture.

État scientifique durable :
- F1 Stage A = discovery persistée, pas confirmation ; historique privé antérieur reste `UNKNOWN` si non récupéré.
- F1 Stage B scellé = `FAMILY_STATUS_REJECT`; aucune cellule alternative ni seuil relâché, pas de rerun/retune post-outcome.
- F2 = `BLOCKED_DATA_PERMISSION`, malgré exact-head CI vert sur la décision documentaire.
- EURUSD-RANGE-GRID-001 = harness/proxy gelé avant accès aux prix ; un éventuel positif ne vaut pas autorité live.

Règles : `PRE_OP_PASS != EXECUTION_AUTHORITY`, `RATIFIED_AUTHORITY != EFFECTIVE_AUTHORITY`, `DISCOVERY != CONFIRMATION`, `CI_SUCCESS != PERMISSION`, `PROXY_POSITIVE != LIVE_AUTHORITY`, `SEALED_REJECT -> PRESERVE, DO_NOT_RETUNE`.

Poursuivre depuis le **13 octobre**, puis 14, 15 et 16. Publier le prochain checkpoint et continuer immédiatement. Aucun nettoyage destructif, runtime produit ou essai scientifique rejoué pendant cette reconstruction.
