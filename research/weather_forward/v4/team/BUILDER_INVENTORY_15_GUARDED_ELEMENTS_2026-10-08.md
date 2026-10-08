# Inventaire indépendant des quinze éléments du rapport structurel (Builder, 2026-10-08)

```text
DOCUMENT_STATUS = BUILDER_WORKING_NOTE_NOT_AN_OWNER_DECISION
PURPOSE = comparateur pour le tableau G du rapport Astra lot 3 (aucune autorité, aucun gel)
```

Source unique : champ `fields.exact_metric_or_artifact` du manifeste de sortie D2 gelé, `research/weather_forward/v4/a2_operation/frozen/output_manifest_d2_v1.json`, blob `7651de7e718a276b596f2256aff0877e771e5d6d` (tête de `builder/weather-v4-a2-lot2-tooling-2026-10-07` @ `51f49c81d843e57111135df283b06368cc1546bf`). Extraction par script, dans l'ordre de la chaîne gelée, séparateur `; ` après le préfixe `STRUCTURAL_REPORT_ONLY:`.

| # | Élément | Domaine ou règle |
|---|---|---|
| 1 | validation_state | NON_VÉRIFIÉ ici (enum du harnais) |
| 2 | permit_or_deny_state | NON_VÉRIFIÉ ici |
| 3 | quarantine_state | NON_VÉRIFIÉ ici |
| 4 | release_state | NON_VÉRIFIÉ ici |
| 5 | completion_state | NON_VÉRIFIÉ ici |
| 6 | stop_reason | NON_VÉRIFIÉ ici (`StopReason`) |
| 7 | detail_code | NON_VÉRIFIÉ ici (78 codes finaux du §14.5) |
| 8 | input_manifest_reference | NON_VÉRIFIÉ ici |
| 9 | output_manifest_reference | NON_VÉRIFIÉ ici |
| 10 | policy_reference | NON_VÉRIFIÉ ici |
| 11 | construction_authority_reference | NON_VÉRIFIÉ ici |
| 12 | execution_authority_reference | NON_VÉRIFIÉ ici |
| 13 | actor_role_bindings | NON_VÉRIFIÉ ici |
| 14 | acknowledged_log_record_references | NON_VÉRIFIÉ ici |
| 15 | structural_linkage_status | domaine fermé proposé par Codex (Q13 : `LINKED` / `NOT_LINKED` / `INDETERMINATE`), non ratifié ; E §C.1 le ferme à deux valeurs pour D2 : `INPUT_LINKED_RELEASE_NOT_ATTEMPTED`, `INPUT_AND_RELEASE_LINKED` |

Le compte est 15 (ni 14 ni 16). Les colonnes de domaine ne sont pas remplies : le faire demande la lecture du §14.5 et de `contract.py`, laissée à la comparaison avec le tableau G d'Astra. Observation à vérifier par Astra : pour D2, E ferme `structural_linkage_status` à deux valeurs, alors que le projet Q13 (route D1) en propose trois ; les deux domaines ne doivent pas être confondus.
