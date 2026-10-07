# Autorité d'exécution E et configuration finale, route D2 — RATIFIÉE (conditionnelle)

```text
DOCUMENT_STATUS = OWNER_EXECUTION_AUTHORITY_E_D2_RATIFIED_CONDITIONAL
E_EFFECT = NOT_IN_EFFECT_UNTIL_ALL_SECTION_B5_CONDITIONS_AND_LOT4_ACTIVATION_DECISION
```

Date : 2026-10-08T02:00+02:00 (Europe/Paris). Dépôt : `fahimahmedb/Quant-Trade`. Chemins relatifs à `research/weather_forward/v4/`.

## Ratification

Owner a écrit « Je ratifie le projet e » dans sa conversation avec la session Claude Code `session_016Mii9xHWUhsB3DEuB88zpz`, en réponse à la demande de ratification de la configuration finale et du projet E. Le message ne cite pas de commit ; il désigne le seul projet E existant : `owner/weather-v4-a2-execution-authority-draft-2026-10-08` @ `a56467a63805365deae2e64e8c35fccb0a2cf63b`, fichier `owner/OWNER_V4_A2_EXECUTION_AUTHORITY_E_DRAFT_D2_2026-10-08.md`, blob `53af1fb3c4d6059465fad7e23354e48c3dd2f2e9`. Il est interprété comme ratifiant le tableau A et la section B, avec les recommandations de la section C du projet, et l'identité de la policy dans le même acte. Cet enregistrement est le fichier E : son commit, consigné hors du fichier, est le SHA d'exécution inscrit dans la root, l'autorisation et le contexte.

## A. Configuration finale ratifiée

| Objet | Chemin | Blob | Identité | Gel |
|---|---|---|---|---|
| Input | `a2_operation/frozen/input_manifest_d2_v1.json` | `f85205f33a232de6fabd83c17c52a25d4634e374` | `sha256:5c55b855b91a5c2b0bde86f3c0888905b500c086309a761ff454644d0cfbbd00` | acte `245f193edb158a6cee653f176ae7b93cf2f3ae80` |
| Output D2 | `a2_operation/frozen/output_manifest_d2_v1.json` | `7651de7e718a276b596f2256aff0877e771e5d6d` | `sha256:b8157e4e15b4e03813b0ff43d52a2319ea589fc9aab9429f1c2894bcce990976` | même acte |
| Policy | `a2_operation/frozen/harness_policy_d2_v1.json` | `6a1fa30fac327c0183b2931550bd4c730195529c` | `sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60` | acte `79f6e9290121869cece6d23a259249883b32941a` |

Fichiers sur la branche `builder/weather-v4-a2-lot2-tooling-2026-10-07` @ `51f49c81d843e57111135df283b06368cc1546bf`. Autorité de construction C : `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c`. Liaison : harnais `research/weather_forward/v4/a2_harness`, version `weather-v4-a2-doc-integration-v1`, manifest `A2-DOC-INTEGRATION-MANIFEST-V1`. Route D2 ; D1 fermée.

## B. Autorité d'exécution E (valeurs du point 4 : retenues telles que proposées)

1. **Objet et effet.** Autorité future et conditionnelle pour le binding de root et une seule opération D2, READ_INPUT seul. Elle ne prend effet que si toutes les conditions du point 5 sont réunies et si une décision Owner du lot 4 l'active. Son commit est consigné hors du fichier ; le même SHA complet de 40 caractères figure dans `execution_policy_authority_sha` de la root, dans `authority_sha` de l'autorisation et dans `execution_authority_sha` du contexte. E ne contient pas son propre SHA et ne nomme aucun commit candidat.
2. **Identités liées.** Le tableau A, C et les trois jetons de liaison.
3. **Actions.** READ_INPUT : `a2-doc-v1-read-input-blue`, acteur `blue.weather-v4.a2.doc-integration.v1`, rôle `EXECUTOR`, AUTHORIZED seulement à la prise d'effet. Aucune autorisation RELEASE_OUTPUT, aucun second appel (`release = null`, `output_record_id = null`). Déclarations inertes exigées par le schéma du script : destinataire `project-owner.weather-v4.a2.doc-integration.v1` (`RESEARCH_VIEWER`) et approbateur `astra.weather-v4.a2.doc-integration.v1` (`RELEASE_APPROVER`).
4. **Contexte (PROPOSÉ).**
   - journal initial vide ;
   - `INPUT_LOG_RECORD_ID = a2-doc-v1-d2-log-input-read-001` ;
   - `incident_identifier = null` (aucun incident existe ; une valeur fixe fabriquerait une référence) ;
   - fichier résultat `/srv/a2out/a2-doc-v1-d2-input-result-001.json` ; l'unicité tient au refus d'écraser ;
   - `accepted_detail_codes = ["INPUT_READ_ELIGIBLE_LOGGED_AND_COMPLETED"]` ;
   - référence d'incident externe, attribuée par Owner après l'événement : `a2-doc-v1-inc-NNN`, avec une seule classe, sans contenu ;
   - classes d'incident (vocabulaire fermé) : `A2_INC_STOP_30`, `A2_INC_EXCEPTION_40`, `A2_INC_OUTPUT_LIMIT_50`, `A2_INC_UNIT_ABNORMAL` (signal, timeout, OOM, erreur de lancement, code hors 0/30/40/50, y compris 10), `A2_INC_CONTROL_NONCONFORMITY`, `A2_INC_CUSTODY_BREACH`, `A2_INC_UNEXPECTED_INFORMATION_REVEALED` ;
   - interprétation : `*_EFFICACY_LEAKAGE_NOT_CLEAR` décrit l'état déclaré d'un manifest, jamais une fuite détectée.
5. **Conditions de prise d'effet (toutes requises).**
   - (a) PASS Astra du lot 3 sur les snapshots exacts du candidat, de l'outillage et du contexte, y compris le canal de contrôle et le contenu gardé ;
   - (b) contrôles L2-A réellement qualifiés (aujourd'hui reportés, non levés) ;
   - (c) capacités de rétention et de suppression vérifiées avant toute garde ;
   - (d) mécanisme d'incident disponible ;
   - (e) origine des autorisations et correspondance de session vérifiées ;
   - (f) code chargé constaté sur l'hôte contre les blobs approuvés (4 fichiers du harnais dont le `trusted_root.py` candidat, 7 sources d'opération, contexte, profil d'unité) ;
   - (g) dispositions A1 §5 attestées, sans génération de fixture ;
   - (h) canal de diagnostic limité au code accepté ci-dessus ;
   - (i) décision Owner d'activation nommant commit candidat, blobs, contexte, profil et chemins ;
   - (j) plafonds O §8.3 (60 s, 5 s de CPU, 128 Mio sans swap, 1 tâche, 1 Mio d'écriture, 64 Kio de résultat) et visibilité du point 6 ;
   - (k) une seule opération, sans retry.
   Sur D2, O §2.5 vise une évaluation de release effectivement tentée : l'absence de RELEASE_OUTPUT donne une fin normale (code 0), sans incident.
6. **Visibilité D2.** Le fichier résultat n'est jamais ouvert, hashé, copié ni transféré. L'opérateur voit seulement le code de sortie et les mesures systemd (stdout et stderr à null) : `0` fin normale, `30` STOP, `40` exception, `50` limite dépassée ; `10` est inatteignable sur D2 et vaudrait incident. Le fichier n'est écrit qu'au code 0 ; il contient exactement les 15 éléments, à valeurs déterminées par la configuration (dont `structural_linkage_status = "INPUT_LINKED_RELEASE_NOT_ATTEMPTED"`). Garde non lue, 30 jours calendaires au plus, sans extension ; la perte du tmpfs au redémarrage est consignée sans valoir purge.
7. **Portée.** Une écriture bornée sous `/srv/a2out` avec garde locale non lue. Aucun transfert, export ni accès GitHub.
8. **Exclusions.** E n'active pas la root et n'approuve aucune release. Elle n'autorise aucune autre cible, fixture, donnée réelle, collecte, endpoint, credential ou économie.

## C. Dispositions des six points du projet

1. `structural_linkage_status` : domaine fermé, contrainte documentaire de E : `INPUT_LINKED_RELEASE_NOT_ATTEMPTED` ou `INPUT_AND_RELEASE_LINKED`. Sur D2, seule la première valeur est atteignable. Le texte canonique des manifests est inchangé.
2. Contenu gardé : exactement les 15 éléments du rapport structurel.
3. Condition (b.5.c) bloquante : sans capacités vérifiées de rétention et de suppression, E reste sans effet et aucun résultat réel n'est créé ou gardé.
4. Les déclarations de destinataire et d'approbateur exigées par le schéma du script sont inertes sur D2.
5. La garde couvre tout fichier sous `/srv/a2out` ; l'existence d'un fichier ne se déduit pas du seul code de sortie.
6. E est identifiée par son commit de 40 caractères hexadécimaux, identique dans la root, l'autorisation et le contexte. L'identité de la policy (`sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60`) est ratifiée avec la configuration finale.

```text
OWNER_FINAL_CONFIGURATION_D2 = RATIFIED
EXECUTION_AUTHORITY_E_D2 = RATIFIED_CONDITIONAL_NOT_IN_EFFECT
TRUSTED_ROOT_CANDIDATE_CONSTRUCTION = AUTHORIZED_UNDER_LOT2_L2_H_ONLY
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
VM_ACTION_AUTHORIZED = FALSE
RELEASE_OUTPUT_AUTHORIZED = FALSE
D1_ROUTE = CLOSED_IN_CURRENT_STATE
ECONOMIC_AUTHORITY = 0
REAL_CAPITAL_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
NEXT_SAFE_ACTION = BUILDER_L2_H_TRUSTED_ROOT_CANDIDATE_USING_THE_COMMIT_OF_THIS_FILE_AS_E
```
