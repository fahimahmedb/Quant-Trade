# Décision Owner — Weather V4 A2

## Adoption de la revue documentaire lot 1 et sélection de la route D2

PROJET — en attente de ratification explicite. Date : 2026-10-07 (Europe/Paris).

```text
DOCUMENT_STATUS = DRAFT_PENDING_EXPLICIT_OWNER_RATIFICATION
MISSION_CLASS = OWNER_ADOPTION_OF_ASTRA_LOT1_AND_D2_ROUTE_SELECTION_ONLY
EFFECT_BEFORE_RATIFICATION = NONE
```

Ce projet propose de consigner l'adoption du constat publié et le choix D2 pour préparation. Il ne modifie pas la revue Astra, ne produit aucun constat indépendant et ne ratifie aucun fichier canonique encore absent. Il ne révoque ni ne réémet les permissions déjà accordées pour le lot 2.

## 1. Références exactes

| Référence | Commit | Chemin ou référence | Blob |
|---|---|---|---|
| Revue Astra lot 1 | `52e5ff27583f3480ea443acdf6b358d3a44242f5` | `research/weather_forward/v4/audit/ASTRA_V4_A2_DOC_INTEGRATION_LOT1_REVIEW_2026-10-07.md` | `e5bfce1bb255fa20e4d7314685286a822ae867fe` |
| Cible immuable de cette revue | `77766db60eaca40f0cd9b1531cb65df3e080f2e5` | Dossier Blue, §§14.1–14.14, `research/weather_forward/v4/blue/BLUE_V4_A1_DOCUMENTATION_2026-10-04.md` | `c764f3999c6734ecd51822f7cd22eb011a76872c` |
| Version ratifiée de la décision lot 2 | `276fd995fe494e1734bba13827e6103864ce68da` | `research/weather_forward/v4/owner/OWNER_V4_A2_LOT2_TECHNICAL_AUTHORIZATION_DRAFT_2026-10-07.md` | `d9809d0cca1faa51b713f02e453b7233c7a16811` |
| Acte de ratification lot 2 et désignation Builder | `ccd4747e4bb9e2a4d93c552ba10e081f254af1e7` | `research/weather_forward/v4/owner/OWNER_V4_A2_LOT2_TECHNICAL_AUTHORIZATION_RATIFICATION_2026-10-07.md` | `705040cba9b75b188309672b73e7a6da615a444a` |
| Checkpoint Builder vérifié | `112933c5bd2dc511f91bd5500850c5a084eb772e` | Branche `builder/weather-v4-a2-lot2-tooling-2026-10-07` ; 18 fichiers nouveaux sous `research/weather_forward/v4/a2_operation/` | Identités par fichier à épingler dans le dossier technique ; aucun blob unique attribué au lot |
| Configuration documentaire D | `49d3d0033dd5088ebe6ed93937d283b0a5b83a63` | Dossier Blue, notamment §§14.2, 14.7–14.11, 14.14–14.15 | `c3271812aa7ad67747916afa0c64344aec36590d` |

Les branches `astra/weather-v4-a2-doc-integration-lot1-review-2026-10-07` et `claude/new-session-qr4nsz` pointent vers le même commit Astra. La création de l'alias ne change aucun commit, blob ou texte. Le nom de branche n'authentifie pas l'identité du reviewer.

**Discordance du checkpoint communiqué :** `112933c5eb6a688757dab729c6e97aa4d0fb02cd` n'est pas résolu par le dépôt consulté (réponse NOT_FOUND). Il n'est pas utilisé comme preuve ou autorité. Le HEAD retourné par Git et son parent sont respectivement `112933c5bd2dc511f91bd5500850c5a084eb772e` et `276fd995fe494e1734bba13827e6103864ce68da`. Cette discordance ne change pas l'autorité lot 2 résolue ; elle doit rester visible.

Le message du commit Astra rapporte une ratification antérieure de son texte. Le présent projet ne prétend pas vérifier un échange extérieur absent du dossier : il consigne, une fois ratifié, l'adoption et les choix décrits ici, sans demander de modifier ou de refaire ratifier la revue.

## 2. Constat adopté, sans extension

Le bloc de conclusion publié par Astra est repris avec ses noms exacts :

```text
INPUT_LEAKAGE_FINDING = CLEAR_SUPPORTED
OUTPUT_LEAKAGE_FINDING = UNRESOLVED
CUMULATIVE_DISCLOSURE_FINDING = UNRESOLVED
LEDGER_RECORDS_SUPPORTED = NONE
QUARANTINE_RECOMMENDATION = MAINTAIN
DIAGNOSTIC_SCOPE_FINDING = ACCEPTED
DIAGNOSTIC_CODES_EXCLUDED = NONE
CRITERION_3_INTERPRETATION = ACCEPTED
```

CLEAR_SUPPORTED est une conclusion documentaire attribuable à Astra, pas la valeur déjà appliquée à un InputManifest figé ni une permission d'exécution. La transition input revue ne concerne que `efficacy_leakage_assessment` ; les seize autres champs doivent rester identiques aux valeurs revues, sous les conditions L2-C.

Les réserves signalées dans le checkpoint sur F.1, les références et les formulations sont enregistrées comme réserves connues, sans correction du texte publié ni extension de son verdict. En particulier, la mention de `FIXTURE_PROVENANCE_CONTRACT_VALID` comme code final atteignable ne doit pas servir à élargir l'allowlist de diagnostics. La review reste une preuve documentaire avec ses limites ; aucun verdict technique n'est déduit de ces réserves.

L'adoption ne lève pas les exigences de l'acte ratifié lot 2, notamment les dispositions Owner L2-C/L2-D, les gels exacts, la méthode vérifiée, E, la vérification du candidat et les contrôles effectifs.

## 3. Choix D2 pour préparation uniquement

```text
D2_INPUT_ONLY_ROUTE = SELECTED_FOR_PREPARATION_ONLY_AFTER_RATIFICATION
D1_RELEASE_ROUTE = NOT_SELECTED_AND_CURRENT_PRECONDITIONS_NOT_SATISFIED
OUTPUT_MANIFEST_LEAKAGE = UNRESOLVED
OUTPUT_MANIFEST_CUMULATIVE_DISCLOSURE = UNRESOLVED
OUTPUT_MANIFEST_QUARANTINE = BLOCKED_PENDING_OWNER_REVIEW
RELEASE_OUTPUT = NOT_AUTHORIZED_BY_THIS_DECISION
```

D2 vise une seule évaluation future `evaluate_input_read`, sans `evaluate_output_release`, après satisfaction de ses prérequis propres et autorité lot 4. L'appel évalue des déclarations, bindings et autorisations ; il ne lit aucun document ou payload.

Le contenu output déclaré reste celui de D §14.2B, sous les dispositions et le gel L2-D. Sa fuite et son cumul ne passent pas à CLEAR ; sa quarantaine n'est pas levée. Sa présence dans la policy est nécessaire à READ_INPUT, même sans release.

La référence à « l'ancien output » désigne ici le contenu documentaire déjà déclaré dans l'OutputManifest. Elle ne prouve pas qu'un résultat runtime ancien existe, qu'il est détenu ou qu'un incident a eu lieu. Tout éventuel artefact historique effectivement quarantainé reste hors de cette opération : aucune ouverture, réutilisation ou release n'est accordée.

D1 demeure fermé dans l'état présent des constats. Une future transition D2 vers D1 ne peut pas être appliquée à la même opération sans les changements de contenus, gels, identités, policy, E, root et revue qu'elle rend nécessaires.

## 4. Custody, rétention et incident : aucune preuve positive inventée

```text
OWNER_DISPOSITION_CUSTODY = NO_POSITIVE_ASSERTION_BEYOND_AVAILABLE_EVIDENCE
OWNER_DISPOSITION_RETENTION = NO_VERIFIED_RETENTION_OR_DELETION_INFERRED
OWNER_DISPOSITION_INCIDENT = NO_INCIDENT_OR_INCIDENT_CLOSURE_INFERRED_FROM_SILENCE
CONTROL_EFFECTIVENESS = NOT_ESTABLISHED_BY_THIS_DECISION
```

Ces constats négatifs ne constituent pas une disposition positive des capacités requises par L2-C/L2-D. Ils ne déclarent pas les conditions de gel satisfaites.

La rétention canonique actuelle nomme la destination Owner existante. Sa compatibilité avec une garde locale non lue doit être expressément disposée comme prévu en L2-D ; le choix D2 ne suffit pas. Si le texte canonique doit changer, Owner ratifie la nouvelle chaîne avant gel. Ce changement affecte l'identité output, puis la policy et la root.

Le contenu éventuellement retenu, son canal de contrôle et l'absence de consultation doivent être définis et vérifiés dans leurs périmètres applicables. Owner est administrateur et destinataire : une retenue procédurale ne devient pas une ACL empêchant sa lecture. L'absence de release n'est ni une preuve de non-exposition, ni une preuve de suppression.

Les classes fixes d'incident et la règle d'absence de messages, repr ou traces libres restent à fixer sous E et les contrôles appropriés. Aucun incident n'est clos par ce projet, aucune investigation de payload n'est autorisée.

## 5. Continuation autorisée et dépendances conservées

Builder reste la session Claude Code désignée dans l'acte lot 2, distincte d'Astra et sans accès VM.

La continuation L2-A0/L2-B demeure couverte par l'autorité lot 2 ratifiée : outillage, runner, étalonnage et tests synthétiques hors ligne dans le périmètre exact. « Hors ligne » ne signifie pas « aucune exécution » : les calculs/tests synthétiques déjà autorisés ne sont ni interdits ni nouvellement autorisés par ce projet. Aucun calcul sur un contenu réel non figé ni appel sur le tuple réel complet autorisé n'est permis.

Les gels sont des actes documentaires Owner portant sur un contenu exact, pas des exécutions du harnais. Le présent projet ne réalise aucun gel. L'achèvement de L2-B ne dispense d'aucun prérequis, et son existence n'autorise aucun lancement sur la VM.

Dépendances conservées :

- L2-A0/L2-B avancent indépendamment des gels : préparer la qualification, terminer et vérifier la méthode, les runners et les tests autorisés.
- Traiter les dispositions Owner requises par L2-C/L2-D. Transcrire les contenus lorsqu'il est permis de le faire, puis ratifier chaque fichier exact pour son gel. Le gel input et le gel output restent indépendants ; aucun pré-audit Astra de tout L2-B n'est ajouté à ces conditions.
- Calculer chaque identité seulement lorsque son propre gel et sa méthode vérifiée existent. D2 exige **les deux identités**.
- Avec les deux identités, compléter les douze champs de policy, ratifier son gel et calculer son identité.
- Ensuite publier et ratifier E, couvrant READ_INPUT sous conditions ; D2 n'autorise pas RELEASE_OUTPUT.
- Construire le candidat root L2-H et effectuer les vérifications L2-I autorisées ; constituer L2-J.
- Faire réaliser la revue indépendante lot 3 sur les snapshots exacts.
- Obtenir la décision distincte lot 4 d'activation/opération et satisfaire les contrôles effectifs avant l'évaluation D2.

La qualification VM L2-A peut avancer en parallèle une fois la procédure et ses prérequis disponibles, par Owner seul. Le checkpoint Builder dit que la procédure n'est pas encore prête à exécuter ; aucun lancement n'est demandé ici.

Le projet ne crée pas une revue Astra supplémentaire obligatoire de L2-B avant les gels. La vérification de la méthode conditionne les calculs ; la revue indépendante du candidat et de ses preuves reste au lot 3. Un avis ciblé peut être demandé sur une lacune précise, sans devenir implicitement un nouveau gate global. Tout choix Owner ultérieur imposant une condition supplémentaire devra l'énoncer explicitement.

## 6. Non-autorisations et limites d'effet

```text
L2_C_FREEZE_PERFORMED_BY_THIS_DECISION = FALSE
L2_D_FREEZE_PERFORMED_BY_THIS_DECISION = FALSE
MANIFEST_AND_POLICY_DIGESTS_COMPUTED_BY_THIS_DECISION = FALSE
EXECUTION_AUTHORITY_E_ISSUED_BY_THIS_DECISION = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED_BY_THIS_DECISION = FALSE
ACTUAL_OPERATION_RESULT_CREATION_AUTHORIZED_BY_THIS_DECISION = FALSE
PROTECTED_PAYLOAD_ACCESS_AUTHORIZED = FALSE
HISTORICAL_QUARANTINED_ARTIFACT_REUSE_AUTHORIZED = FALSE
FIXTURE_GENERATION_AUTHORIZED = FALSE
FIXTURE_TESTING_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

L'interdiction de créer un résultat réel ne vise pas la transcription documentaire d'un OutputManifest ni les objets synthétiques déjà permis au lot 2. Les actions `E1_E5` n'ont pas de définition dans les références de cet acte ; ce libellé n'est pas utilisé pour inventer un nouveau périmètre. Les interdits opérationnels et expérimentaux existants restent applicables.

## 7. Effet proposé après ratification

La ratification de ce projet adopte le constat publié et sélectionne D2 pour préparation. Elle n'est ni un gel exact, ni un calcul, ni E, ni une activation, ni une permission de consulter un résultat. Les références de ratification seront enregistrées à leurs identités de publication sans auto-référence.

```text
NEXT_SAFE_ACTION = CONTINUE_L2_A0_L2_B_AND_PREPARE_REQUIRED_OWNER_DISPOSITIONS_FOR_D2
```
