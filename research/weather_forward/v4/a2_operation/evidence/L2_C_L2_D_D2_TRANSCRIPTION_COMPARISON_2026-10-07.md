# Builder — preuve de comparaison des transcriptions L2-C / L2-D (route D2)

Date : 2026-10-07. Branche : `builder/weather-v4-a2-lot2-tooling-2026-10-07`. Parent de la publication des fichiers : `1910994f3141d20b10547a0f35e73d012b011a38`; commit des fichiers : `13d9143cb4659cb51a122a4a7ea398e6ccf074a4`.

Le nom `frozen/` ne vaut pas gel. Un gel est la ratification Owner du fichier exact publié (L2-C, L2-D). Aucun digest de ces contenus réels n'est calculé.

## Fichiers

| Fichier | Blob Git | Champs |
|---|---|---|
| `a2_operation/frozen/input_manifest_d2_v1.json` | `f85205f33a232de6fabd83c17c52a25d4634e374` | 17 |
| `a2_operation/frozen/output_manifest_d2_v1.json` | `7651de7e718a276b596f2256aff0877e771e5d6d` | 13 |
| `a2_operation/identity/transcribe_frozen_from_dossier.py` (générateur) | `90f1eec6ea847c0e7447b4bb6d4cb6e202dbdd8e` | — |

Source : dossier Blue D, commit `49d3d0033dd5088ebe6ed93937d283b0a5b83a63`, blob `c3271812aa7ad67747916afa0c64344aec36590d`, §14.2A et §14.2B. Le générateur refuse tout dossier dont le blob diffère.

## Transitions

- Input : une seule transition, `efficacy_leakage_assessment` : `UNRESOLVED` (D) devient `CLEAR`, sur le constat Astra `INPUT_LEAKAGE_FINDING = CLEAR_SUPPORTED` (`52e5ff27583f3480ea443acdf6b358d3a44242f5`), adopté par Owner. Les seize autres valeurs sont identiques à D.
- Output : aucune transition. `exportability = ALLOWED`, `quarantine_status = BLOCKED_PENDING_OWNER_REVIEW`, `cumulative_disclosure_risk = UNRESOLVED`, `efficacy_leakage_assessment = UNRESOLVED`, `release_approval_requirement = REQUIRED`.
- Aucun champ ajouté ni retiré. Conventions du format `A2_FROZEN_CONTENT_V1` : enums par nom de membre sans préfixe de classe, tuples en tableaux dans l'ordre du dossier, texte exact entre les accents graves.

## Vérifications effectuées

| Vérification | Méthode | Résultat |
|---|---|---|
| Régénération | Le générateur relancé produit des octets identiques aux deux fichiers | Identique |
| Structure | `identity_stdlib.canonical_payload` (validation de structure et d'enums, sans appel de hachage) | 17 et 13 champs acceptés |
| Retranscription à l'aveugle | Agent de la session Builder, sans voir les fichiers publiés ni le générateur ; analyse du dossier par sa propre méthode | Égalité JSON et égalité octet par octet de chaque chaîne (longueurs 207, 359, 177, 367, 277) |
| Recoupement avec les autres sources | Autre agent de la session Builder | EXACT sur 14 contrôles (liste ci-dessous) |

Recoupement : `retention_rule` égal à Owner O §8.4 et à la citation du §4.2 de l'acte Owner D2 (367 caractères) ; `incident_if_unexpected_information_revealed` égal à O §8.5 (277) ; 20 champs interdits, 4 champs permis et rôle de lecteur égaux à O §2.2 ; 15 éléments de `exact_metric_or_artifact` égaux à O §2.3 et au dossier B §13.5 ; `granularity` égal à B §13.5 ; `source_provenance_class` égal à B §13.4 avec le commit, le chemin et le blob A1 qui se résolvent dans Git (`728cf23e…`, `483907e4…`) ; autres états égaux à O §2.2/§2.3 et à l'acte Owner D2 §4.

## Limites

- Les deux agents de vérification appartiennent à la session Builder : ce n'est pas une revue indépendante. L'indépendance relève d'Astra au lot 3.
- Le dossier B §13.5 conserve des valeurs de brouillon plus anciennes pour l'exportabilité, la rétention et l'incident. Elles n'ont servi qu'à comparer `exact_metric_or_artifact` et `granularity`, les autres valeurs suivant O et D.
- Les fichiers n'ont pas été chargés dans les classes du harnais et aucun appel `evaluate_*` n'a eu lieu.

```text
INPUT_TRANSCRIPTION_PUBLISHED = TRUE
OUTPUT_D2_TRANSCRIPTION_PUBLISHED = TRUE
INPUT_CONTENT_FROZEN = FALSE
OUTPUT_CONTENT_FROZEN = FALSE
REAL_MANIFEST_IDENTITIES_COMPUTED = FALSE
HARNESS_IMPORTED_FOR_THESE_FILES = NO
EXECUTION_AUTHORITY_E_ISSUED = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
NEXT_SAFE_ACTION = OWNER_FREEZE_ACTS_L2_C_AND_L2_D_ON_THE_EXACT_PUBLISHED_FILES
```
