# Reprise active — historique de surface

STATUT : IN_PROGRESS. L’Owner a autorisé explicitement la reprise. L’audit global et la simplification ne sont pas terminés. Ne pas interrompre la chronologie après un checkpoint intermédiaire.

## Curseur durable

Les **48 premières journées actives** sont traitées jusqu’au **8 octobre inclus** : **2 449 commits** plus les traces GitHub datées associées. Prochaine journée active : **9 octobre 2026**. Dernier checkpoint : `surface/CHECKPOINT_2026-10-05_2026-10-08.md`.

Méthode : `CHRONOLOGICAL_SURFACE`. Toutes les quatre journées actives, publier un checkpoint puis continuer. Les 6 393 commits / 111 journées / 13 471 occurrences restent l’inventaire initial ; indexé n’est pas relu intégralement.

## État réutilisable

- `restaurant-stock/` est hors périmètre Quant.
- `SCHEDULED_DATA_COLLECTION` représente la collecte planifiée ; les snapshots automatiques ne sont pas des modules.
- Rails : `SAFE_RAIL_PROSPECTIVE`, `FAST_RAIL_C_PAPER_SHADOW`, `HISTORICAL_PIT_VALIDATION`, `CI_ONLY_AUDIT_SURFACES`.
- `REAL_CAPITAL_AUTHORIZED = FALSE`; `REAL_CAPITAL` et `FIXED_COST_BASE` restent inconnus décisifs.
- Weather R3 du 30 septembre supersède l’ancien label prospectif inconditionnel.

Weather V4 A2 doit être reconstruit comme **une lignée d’états**, pas comme une architecture par branche : design/contract → scope Owner → harness Builder → audit Astra → repair → ratification Owner → trusted-root candidate → independent review → éventuelle autorité effective/activation.

Au 8 octobre : root candidate présent ; Astra lot3 = `BLOCKED_INCOMPLETE_EVIDENCE`; `E_EFFECTIVE = FALSE`; aucune activation, release, levée de quarantaine ou merge n’est démontrée. Règles : `PRE_OP_PASS != EXECUTION_AUTHORITY`, `RATIFIED_AUTHORITY != EFFECTIVE_AUTHORITY`, tests reproduits + root candidat != activation.

Les détails non résolus du 1 octobre et de quatre commits non-feed du 6 octobre restent `UNKNOWN_DETAIL_NOT_BLOCKING` ; ne pas recommencer l’audit pour les combler sauf si cela change une décision de réutilisation.

Poursuivre depuis le **9 octobre**, puis 10, 11 et 12 octobre. Publier le prochain checkpoint et continuer immédiatement. Aucun nettoyage destructif, runtime produit ou essai scientifique rejoué pendant cette reconstruction.
