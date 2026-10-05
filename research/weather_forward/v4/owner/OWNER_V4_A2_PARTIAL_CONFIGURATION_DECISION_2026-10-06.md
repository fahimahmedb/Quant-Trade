# Décision Owner partielle — Weather V4 A2
## Intégration documentaire uniquement, sans fixture

Date de préparation : 2026-10-05  
Date de ratification : 2026-10-06T00:04:40+02:00 — Europe/Paris  
Autorité déclarante : PROJECT_OWNER — utilisateur de cette conversation  
Statut du document : PARTIALLY_RATIFIED_WITH_BLOCKERS  
Effet actuel : ratification documentaire limitée aux clauses déterminées de §2 ; aucune autorisation d'exécution.

Cette décision enregistre le « Oui » d'Owner en réponse au projet exact présenté dans cette conversation. La ratification porte uniquement sur les clauses déterminées de §2, sous les réserves des §§1 et 3–6. Les sections 3 et 4 restent bloquantes. La portée ne comprend ni ratification finale de configuration ni permission technique ou d'exécution. L'approbation et son contexte sont consignés en §7.

## 1. Base exacte et portée

Dépôt : fahimahmedb/Quant-Trade.

| Référence | Identité exacte | Utilisation |
|---|---|---|
| Autorité documentaire A1 | Commit `728cf23e7d69a373306f3c1a3fb5d11240210cda` ; `research/weather_forward/v4/owner/OWNER_V4_PHASE_GATE_A1_DECISION_2026-10-04.md` ; blob `483907e4f719ec8bcb3851af0f184690cea96279` | §§3–4 : spécification documentaire ; §§5, 9–10 : autorité distincte, STOP et limites |
| Configuration candidate Blue | Commit `92088b83dd47799c6d413bb747138c05fdb0e420` ; `research/weather_forward/v4/blue/BLUE_V4_A1_DOCUMENTATION_2026-10-04.md` ; blob `44eff971f29b50f2d514b0e02917ad7cff9bb3f7` | §13 uniquement ; contenu historique conservé |
| Revue Astra | `31215914a7e11daa20ca0189d859bb69827a055c` | Preuve de revue indépendante de réparation et de tests bornés ; aucune autorité d'exécution |
| Harnais de référence | `78d537de681363ed83a6c7787aba4319f3c73c4d` | Schémas et interfaces examinés ; version future activée encore à réconcilier |
| Construction historique | `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c` | Autorité de construction ; distincte de l'autorité documentaire A1 et de toute future autorité d'exécution |

Cette décision ne modifie ni le verdict Astra ni les décisions économiques ni le registre canonique historique. Aucun audit D5 ni test du harnais n'est relancé.

## 2. Contenu ratifié partiellement

Seules les clauses suivantes constituent la base documentaire approuvée. Elles ne constituent pas un gel complet des manifests ou de la policy.

### 2.1 Mode, objectif et limites

```text
A2_INTEGRATION_MODE = DOCUMENTATION_ONLY_NO_FIXTURE
FIXTURE_REQUIRED_FOR_IMMEDIATE_MODE = FALSE
```

L'opération candidate future est limitée à une évaluation `evaluate_input_read`, suivie d'une évaluation `evaluate_output_release` seulement si le premier résultat satisfait les attentes approuvées, puis à la vérification des décisions et de la liaison au journal acquitté. Aucun retry, cible supplémentaire ou extension automatique n'est admis.

Ces interfaces évaluent les déclarations, les bindings et les autorisations. Elles ne lisent pas le document référencé, ne construisent pas un rapport et n'effectuent aucun export. L'expression « rapport structurel » désigne ici le périmètre d'information proposé ; elle n'ajoute aucun parseur, sérialiseur ou transport au harnais.

La preuve recherchée reste : policy et manifests exacts + acteurs et autorisations exacts → décisions du harnais → liaison exacte au journal acquitté. Elle n'établit aucune faisabilité de payload ou de source, ni aucune conclusion économique.

Sont exclus : fixture ou objet de test, payload, données ou métadonnées opérationnelles réelles, endpoints opérationnels, credentials opérationnels, observation, cadence, latence, disponibilité, sélection ou classement de source/station/ville/modèle, capture, backtest, PnL, paper trading, live trading et capital. Aucun objet structurel précédemment testé n'est promu en fixture A2.

### 2.2 Sous-ensemble déterminé du candidat InputManifest

Référence normative de ces propositions : dossier Blue au commit exact ci-dessus, §13.4. Les valeurs ci-dessous sont retenues pour la configuration documentaire ; la conclusion de leakage reste ouverte.

| Champ réel | Valeur soumise à ratification |
|---|---|
| `input_id` | `A2-DOC-IN-OWNER-A1-V1` |
| `manifest_version_identity` | `A2-DOC-INTEGRATION-MANIFEST-V1` |
| `input_classification` | `InputClassification.DOCUMENTATION_ONLY` |
| `source_provenance_class` | Chaîne exacte de §13.4 référençant le commit A1, son chemin et son blob |
| `exact_permitted_fields` | `document_commit_sha`, `document_path`, `document_blob_sha`, `authorized_documentary_scope_reference` |
| `exact_prohibited_fields` | Les 20 noms exacts de §13.4, reproduits ci-dessous |
| `permitted_reader_roles` | `Role.EXECUTOR` uniquement ; aucune identité attribuée |
| `raw_values_visible` | `VisibilityState.VISIBLE`, limité aux quatre références documentaires permises |
| `timestamps_visible` | `VisibilityState.HIDDEN` |
| `frequency_or_count_information_visible` | `VisibilityState.HIDDEN` |
| `longitudinal_observation_allowed` | `PermissionState.DENIED` |
| `aggregation_allowed` | `PermissionState.DENIED` |
| `cross_source_comparison_allowed` | `PermissionState.DENIED` |
| `access_logging_requirement` | `RequirementState.REQUIRED` |
| `quarantine_on_ambiguity` | `RequirementState.REQUIRED` |
| `owner_approval_required` | `RequirementState.REQUIRED` ; cette déclaration n'est pas une preuve d'approbation opérationnelle |

Les 20 champs interdits sont :
`document_body`, `fixture_payload`, `real_observation`, `real_technical_metadata`, `operational_endpoint`, `operational_credential`, `actual_timestamp`, `cadence`, `latency`, `availability`, `delivery_pattern`, `efficacy`, `economic_outcome`, `performance_distribution`, `pnl`, `ranking`, `source_preference`, `station_preference`, `city_preference`, `model_preference`.

`efficacy_leakage_assessment` reste `LeakageAssessment.UNRESOLVED`. Son remplacement par `CLEAR` exige une justification documentée sur le périmètre figé. Ratification documentaire et résultat factuel de cette évaluation restent distincts.

Ces déclarations sont liées par l'identité du manifest ; le harnais n'inspecte pas un payload pour faire respecter l'allowlist, la visibilité ou la provenance.

### 2.3 Sous-ensemble déterminé du candidat OutputManifest

Référence : dossier Blue exact, §13.5.

| Champ réel | Valeur soumise à ratification |
|---|---|
| `output_id` | `A2-DOC-OUT-STRUCTURAL-REPORT-V1` |
| `manifest_version_identity` | `A2-DOC-INTEGRATION-MANIFEST-V1` |
| `output_type` | `DOCUMENTATION_ONLY_STRUCTURAL_REPORT` |
| `exact_metric_or_artifact` | Chaîne exacte `STRUCTURAL_REPORT_ONLY: ...` de §13.5 ; contenu limité aux 15 éléments ci-dessous |
| `granularity` | Chaîne exacte `ONE_DOCUMENTARY_OPERATION; ...` de §13.5 |
| `permitted_recipients` | `Role.RESEARCH_VIEWER` uniquement ; acteur encore non désigné |
| `release_approval_requirement` | `RequirementState.REQUIRED` |

Les éléments de sortie permis sont :
`validation_state`, `permit_or_deny_state`, `quarantine_state`, `release_state`, `completion_state`, `stop_reason`, `detail_code`, `input_manifest_reference`, `output_manifest_reference`, `policy_reference`, `construction_authority_reference`, `execution_authority_reference`, `actor_role_bindings`, `acknowledged_log_record_references`, `structural_linkage_status`.

Les codes de motif doivent être fixes, structurels et examinés ; aucune trace libre, observation, mesure, préférence, information économique ou assertion dérivée d'un payload n'est admise.

Les champs ouverts restent : `exportability = UNRESOLVED`, `quarantine_status = BLOCKED_PENDING_OWNER_REVIEW`, `cumulative_disclosure_risk = UNRESOLVED`, `efficacy_leakage_assessment = UNRESOLVED`, contenu final de `retention_rule` et de `incident_if_unexpected_information_revealed`. Cette décision partielle ne produit aucun `CLEAR` et ne lève pas la quarantaine.

### 2.4 Politique, acteurs et permissions : exigences déterminées

Référence : dossier Blue exact, §§13.6–13.8.

- Label documentaire de policy : `A2-DOC-GOVERNANCE-POLICY-V1`. Ce label n'est pas un champ supplémentaire de HarnessPolicy.
- Autorité de construction proposée dans `expected_owner_authority_sha` : `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c`, jamais remplacée implicitement par A1, Astra PASS ou une autorité d'exécution.
- Identité du composant proposée : `research/weather_forward/v4/a2_harness`.
- IDs input/output et token de version du manifest : ceux des sections 2.2–2.3.
- Classe admise : `DOCUMENTATION_ONLY` uniquement.
- Classes interdites : `NON_ECONOMIC_SYNTHETIC`, `REAL_TECHNICAL_METADATA`, `PROHIBITED`, `UNKNOWN`.
- `fixture_provenance_contract = None` ; aucun contrat d'admission de fixture.
- Référence de logique examinée : `78d537de681363ed83a6c7787aba4319f3c73c4d`. Le binding de version après une éventuelle transition n'est pas encore ratifié.
- Binding de destinataire : un acteur exact associé à `Role.RESEARCH_VIEWER`, à désigner ; aucun placeholder n'est une autorisation.
- Lecture candidate : `Role.EXECUTOR` et `Action.READ_INPUT`. Release candidate : `Role.RELEASE_APPROVER` et `Action.RELEASE_OUTPUT`. Les autorisations effectives, leurs IDs et leur autorité restent non attribués.
- `RELEASE_APPROVER != OUTPUT_RECIPIENT`. L'exécutant peut aussi être lecteur ; les autres combinaisons restent à décider selon le contrat. Aucun besoin de cinq acteurs tous distincts n'est créé.
- Une déclaration de rôle ne vaut jamais permission. Tout futur droit doit être lié à l'acteur, au rôle, à l'action et à l'autorité exacts.

Aucune policy complète, identité structurelle, autorisation par action ou version activée n'est ratifiée par cette liste partielle.

### 2.5 Fail-closed, journal et STOP

Les états et conditions de refus existants sont conservés : autorité absente, identité ou binding discordant, provenance ambiguë, état non résolu ou bloqué, information inattendue, destinataire non autorisé, absence d'approbation indépendante, défaut d'acquittement ou de liaison exacte au journal, ressources non résolues ou dépassées imposent le refus et l'arrêt de la séquence.

La priorité globale `BLOCKED` est conservée. Une histoire de disclosure vide ne vaut pas `CLEAR` ; toute évaluation doit viser le tuple exact output/destinataire/rôle et reposer sur des preuves admissibles.

Un futur succès exige l'acknowledgement exactement vrai et un enregistrement unique, exactement concordant en contenu et contexte. Le journal retourné par la lecture doit être transmis à l'évaluation de release ; cette séquence est une contrainte documentaire, pas un prérequis automatique implémenté.

STOP signifie : cesser la séquence, bloquer la release, conserver seulement une référence d'incident sûre et recourir au mécanisme de quarantaine déjà autorisé. Aucune reprise automatique, construction de mécanisme ou inspection dangereuse n'est permise. Responsable, conservation, confinement et autorité de reprise restent à fixer.

Le journal en mémoire ne prouve pas une conservation durable, des ACL, une immutabilité opérationnelle ou un contrôle des expositions. Les enums de ressources ne prouvent pas l'application de plafonds numériques. Aucune capacité absente n'est présentée comme implémentée.

## 3. Choix documentaires et preuves encore bloquants

| Point ouvert | Résolution minimale attendue | Action bloquée |
|---|---|---|
| Leakage input et output | Évaluation documentée du périmètre final ; critères et preuves justifiant toute conclusion CLEAR | Gel permissif des manifests ; intégration positive |
| Contenu canonique complet | Finalisation des champs ouverts et des chaînes exactes ; cohérence avec les sous-ensembles approuvés | Calcul des identités finales |
| Acteurs et combinaisons | Identités exactes du lecteur/exécutant, approbateur, destinataire et fonctions Owner ; combinaisons explicitement admises | Attribution des droits et release |
| Permissions par action | IDs, acteurs/rôles/actions, conditions et autorité future exacts ; aucune permission déduite d'un titre | Toute évaluation permissive |
| Exportabilité et destination | Décision explicite sur la valeur du champ et la destination ; aucune exportation réelle dans ce mode | Finalisation output et permissions de release |
| Disclosure cumulative et quarantaine | État justifié pour le tuple exact ; histoire pertinente et critères de levée ; BLOCKED prioritaire | Toute release |
| Durée et ressources | Plafonds applicables de durée, CPU/calcul, mémoire, stockage, sorties et accès ; moyen de contrôle et procédure de STOP | Autorisation opérationnelle |
| Rétention et garde des preuves | Texte final des règles, destinataires/lecteurs, custodian et durée ; limite de durabilité explicitée | Finalisation output et dispositif de preuve |
| Incident/quarantaine | Responsable, mécanisme autorisé, escalade et autorité de reprise explicitement désignés | Toute opération sans traitement approuvé |
| Exigences non supportées | Disposition explicite : obligation documentaire compatible, réduction du scope, ou implementation distinctement autorisée | Ratification finale et éventuel travail technique |
| Trusted root et version | Plan choisi, autorité distincte, portée du changement et reconciliation entre référence examinée et version activée | Toute activation et chemin permissif |

Ces lignes sont des choix ou preuves à résoudre dans le dossier existant, pas une liste de nouveaux fichiers obligatoires. Les 279 tests et leur revue ne remplacent aucune de ces résolutions.

## 4. Prérequis techniques non autorisés

```text
DIGESTS = PENDING_FROZEN_CONTENT_AND_COMPUTATION
PRODUCTION_TRUSTED_ROOT = ABSENT_OR_NOT_AVAILABLE_FOR_A2
TRUSTED_ROOT_TRANSITION_REQUIRED = TRUE
FUTURE_ACTION_REQUIRES_SEPARATE_AUTHORIZATION = TRUE
```

Owner ratifie le contenu ; les digests sont dérivés. Aucun digest n'est choisi, calculé ou attribué par cette décision.

Ordre technique proposé, soumis à une autorisation exacte distincte :
1. Résoudre les choix et preuves ; figer le contenu canonique final.
2. Calculer et vérifier les identités input/output selon les fonctions existantes, puis les incorporer à la policy.
3. Calculer et vérifier l'identité de policy ; enregistrer les bindings exacts et les références documentaires externes.
4. Faire ratifier la configuration finale et cadrer séparément la transition technique requise.
5. Seulement sous autorité appropriée : changement de source de trusted root, réconciliation de version et vérification ciblée de la transition.
6. Seulement sous un grant explicite d'exécution : envisager les deux évaluations bornées.

La root future doit lier l'autorité d'exécution, l'autorité de construction, le composant/version et le digest de policy. La root injectée pendant les tests ne peut pas la remplacer. Cette décision ne fournit pas l'autorité d'exécution et ne justifie aucun état AUTHORIZED.

Toute version de transition doit être identifiée sans inventer de SHA auto-référentiel. Une modification des champs canoniques de policy/version implique recalcul et revalidation des bindings avant usage.

Une comparaison de tokens de version ne prouve pas à elle seule l'intégrité du code effectivement chargé. La vérification de cette intégrité, les tests de transition et les moyens externes éventuellement nécessaires doivent être cadrés dans leur propre périmètre autorisé.

## 5. Canonicalisation et références externes

La règle de référence est celle de `a2_harness/harness.py` au commit `78d537de681363ed83a6c7787aba4319f3c73c4d`, blob `00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4` :
JSON avec `ensure_ascii=True`, séparateurs `(",", ":")`, clés triées, UTF-8, SHA-256 et préfixe `sha256:`. Les tris de tuples suivent les fonctions existantes ; aucune normalisation libre des chaînes n'est ajoutée.

- Identité input : les 17 champs réels et `manifest_kind = InputManifest`.
- Identité output : les 13 champs réels et `manifest_kind = OutputManifest`.
- Identité policy : les 12 champs réels et `contract_kind = HarnessPolicy`, dont les identités input/output et le destinataire exact.
- `OutputManifest.retention_rule` et `incident_if_unexpected_information_revealed` sont couvertes par l'identité output. Modifier leur texte ou une référence incluse change cette identité.
- Une procédure externe non représentée dans ces champs n'est pas automatiquement couverte par les digests du harnais. Son approbation et sa référence exacte restent nécessaires selon le scope.
- Une modification d'un champ couvert exige recalcul de l'identité concernée et des bindings dépendants avant usage. Une modification d'une règle externe hors canonicalisation exige revue/ratification de cette règle, sans nécessairement modifier les digests du harnais.

Format d'une référence documentaire externe :
`repository + document_path + commit_SHA + section_or_artifact_identity`.

| Règle documentaire existante | Référence exacte disponible | Ce qui reste ouvert |
|---|---|---|
| Périmètre A1 et interdictions | Quant-Trade ; chemin Owner A1 de §1 ; commit `728cf23e7d69a373306f3c1a3fb5d11240210cda` ; §§3–5 et 9 | Aucun droit A2 n'en est déduit |
| Proposition STOP/quarantaine/journal | Quant-Trade ; chemin Blue de §1 ; commit `92088b83dd47799c6d413bb747138c05fdb0e420` ; §13.10 | Responsable, mécanisme, garde et reprise ; les valeurs de proposition ne sont pas toutes ratifiées |
| Durée/ressources/rétention | Même référence Blue ; §13.10, table des ressources et §13.11 | Valeurs et moyen de contrôle restent OWNER_DECISION_REQUIRED |
| Transition de trusted root | Même référence Blue ; §13.9 | Autorité, changement, version et verification non autorisés |
| Présente décision Owner partielle | Approbation conversationnelle du 2026-10-06T00:04:40+02:00, §7 ; fichier Owner et branche indiqués ci-dessous | Le SHA du commit qui contient ce fichier est fourni par la publication ; aucune auto-référence SHA n'est inventée |

Les références aux propositions Blue servent à localiser les exigences et les inconnues ; elles ne rendent pas ces propositions opérationnellement approuvées.

## 6. Effet d'autorité et états

Cette décision enregistre la ratification partielle d'Owner. Les clauses déterminées de §2 sont approuvées sans modification des §§2.1–2.5 ; les réserves, blocages et limites des autres sections restent applicables. Elle n'attribue aucun acteur opérationnel ni permission par action et n'autorise aucun travail technique.

État effectif après ratification :
```text
DRAFT_ACCEPTED_FOR_OWNER_DECISION = TRUE
OWNER_CONFIGURATION_DECISION = PARTIALLY_RATIFIED_WITH_BLOCKERS
RATIFIED_SCOPE = SECTION_2_ONLY_SUBJECT_TO_SECTIONS_1_AND_3_TO_6
DIGESTS = PENDING_FROZEN_CONTENT_AND_COMPUTATION
FINAL_CONFIGURATION_RATIFIED = FALSE
CANONICAL_CONTENT_FULLY_FROZEN = FALSE
```

Invariants conservés :
```text
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
BUILDER_AUTHORIZED = FALSE
A2_RESEARCH_FIXTURE_AUTHORIZED = FALSE
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
REAL_DATA_ACCESS_AUTHORIZED = FALSE
REAL_METADATA_ACCESS_AUTHORIZED = FALSE
OPERATIONAL_ENDPOINT_ACCESS_AUTHORIZED = FALSE
OPERATIONAL_CREDENTIAL_USE_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED
```

Travail effectué pour cette décision : lecture des textes de gouvernance et des règles de canonicalisation au SHA exact ; rédaction documentaire uniquement. Aucun import ou appel du harnais, test, création/inspection de fixture, calcul d'identité de manifest/policy ou activation de root.

## 7. Ratification enregistrée et publication documentaire

- Autorité déclarante : **PROJECT_OWNER — utilisateur de cette conversation**.
- Approbation reçue : **« Oui »**.
- Date de soumission : **2026-10-06T00:04:40+02:00 — Europe/Paris**.
- Contexte : réponse au message présentant le projet de décision partielle et son lien, dont le statut était `PENDING_EXPLICIT_RATIFICATION`. Ce contexte limite l'approbation à la ratification documentaire partielle préparée.
- Contenu approuvé : **§2, sous les réserves des §§1 et 3–6**. Le texte des §§2.1–2.5 est identique au projet approuvé.
- Exécution / Builder / trusted root : **NON AUTORISÉS**.
- Cet enregistrement ne constitue pas une signature cryptographique ni une preuve d'authentification d'acteur opérationnel. Il ne remplit aucun champ d'autorisation du harnais.

Publication documentaire :
- Dépôt : `fahimahmedb/Quant-Trade`.
- Branche : `owner/weather-v4-a2-partial-configuration-decision-2026-10-06`.
- Parent attendu : `92088b83dd47799c6d413bb747138c05fdb0e420`.
- Fichier : `research/weather_forward/v4/owner/OWNER_V4_A2_PARTIAL_CONFIGURATION_DECISION_2026-10-06.md`.
- Portée du commit : cette décision documentaire uniquement ; aucun merge ni modification du harnais ou de la trusted root.
- Le SHA exact et l'identité du blob sont ceux retournés et vérifiés après publication. Ils ne sont pas précomputés à l'intérieur de leur propre fichier.

Prochaine action : résoudre les items bloquants de §3 dans le dossier existant, sous le périmètre documentaire A1, puis soumettre les décisions ou preuves nouvelles à Owner. Le calcul des identités, Builder, toute transition de root et toute exécution restent soumis à une autorité distincte non accordée ici. Aucune boucle générale Blue → Astra n'est déclenchée ; une revue indépendante ultérieure peut viser un changement technique ou une preuve nouvelle, sous autorité appropriée.

## 8. Configuration renseignée proposée — 2026-10-06

STATUT_DE_CETTE_SECTION = PROPOSED_FOR_OWNER_RATIFICATION  
SECTION_8_RATIFIED = FALSE  
OWNER_CONFIGURATION_DECISION = PARTIALLY_RATIFIED_WITH_BLOCKERS  
A2_EXECUTION_AUTHORIZED = FALSE  
BUILDER_AUTHORIZED = FALSE  
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE

Cette section fournit des valeurs concrètes pour décision. Elle ne modifie pas les clauses déjà ratifiées de §2 et n'accorde aucun droit technique. Les plafonds sont des propositions choisies pour une seule opération structurelle minimale ; ils ne sont ni mesurés, ni dérivés d'un benchmark, ni actuellement imposés par le harnais.

### 8.1 Acteurs et responsabilités

Owner a choisi « Blue / Astra / toi » dans cette conversation le 2026-10-06 : Blue exécutant/lecteur, Astra approbateur et Owner destinataire. Les identifiants ci-dessous sont les tokens documentaires exacts proposés pour ces acteurs déjà désignés ; ils n'attestent pas une identité technique ou une session authentifiée.

| Fonction | Acteur désigné | Token actor_id proposé | Rôle / responsabilité |
|---|---|---|---|
| Exécutant et lecteur | Blue, Research Design Authority | `blue.weather-v4.a2.doc-integration.v1` | `Role.EXECUTOR` ; orchestration bornée et déclaration de lecture |
| Évaluateur documentaire et approbateur | Astra, revue indépendante | `astra.weather-v4.a2.doc-integration.v1` | `Role.RELEASE_APPROVER` ; revue CLEAR/disclosure et approbation indépendante |
| Destinataire | PROJECT_OWNER, utilisateur ayant ratifié §2 | `project-owner.weather-v4.a2.doc-integration.v1` | `Role.RESEARCH_VIEWER` ; seul destinataire proposé |
| Autorité Owner / incident / quarantaine / garde | Même PROJECT_OWNER | Même token documentaire | Fonctions externes ; aucun nouvel enum Role inventé |

L'exécutant peut être le lecteur. L'approbateur est distinct du destinataire et de l'exécutant dans cette proposition. L'indépendance d'Astra exclut sa participation à la future implémentation Builder. Un remplacement d'acteur nécessite décision explicite et révision des bindings concernés.

Blue peut orchestrer les deux évaluations ; la seconde porte la déclaration et l'autorisation de l'approbateur. L'acceptation de ces déclarations ne prouve pas qu'Astra est le processus appelant. L'autorisation documentaire, son origine et la correspondance de session doivent être vérifiées séparément avant toute opération ; le harnais n'authentifie pas ces acteurs.

### 8.2 Permissions candidates par action

| Déclaration / action | Acteur | Identifiant proposé | État actuel et futur conditionnel |
|---|---|---|---|
| `READ_INPUT` | Blue / EXECUTOR | `a2-doc-v1-read-input-blue` | `UNRESOLVED` ; futur AUTHORIZED seulement sous grant Owner exact |
| `RELEASE_OUTPUT` | Astra / RELEASE_APPROVER | `a2-doc-v1-release-output-astra` | `UNRESOLVED` ; futur AUTHORIZED seulement sous grant Owner exact et preuves requises |
| Mapping destinataire | Owner / RESEARCH_VIEWER | Token Owner de §8.1 | Une seule paire actor_id/rôle dans la policy ; aucune transmission actuellement autorisée |
| Admission de fixture et autres actions | Aucun | Aucun | Interdites pour ce mode |

Dans les deux ActionAuthorization, `authority_sha` sera le SHA exact de la future autorité d'exécution liée à la root. Il n'est pas remplacé par le présent commit, A1, le PASS ou un placeholder. Aucune action n'est actuellement autorisée.

### 8.3 Plafonds proposés et unité de contrôle

| Paramètre | Valeur proposée | Périmètre |
|---|---|---|
| Durée maximale | 60 secondes écoulées | Processus futur contenant les deux évaluations et leur vérification ; revue Owner/Astra préalable exclue |
| CPU | 5 secondes CPU cumulées ; au plus un processus du harnais | Temps user + système de ce processus, tous ses threads ; aucun processus enfant |
| Mémoire | 128 MiB = 134 217 728 octets | Pic de mémoire du processus selon le moyen de mesure ratifié |
| Stockage des artefacts de l'opération | 1 MiB = 1 048 576 octets | Total des artefacts structurels locaux écrits, y compris temporaires |
| Volume total des sorties | 64 KiB = 65 536 octets UTF-8 | Décisions, journal, vérification et diagnostics cumulés |
| Appels d'évaluation | Une lecture et une release au maximum | Release omise si la lecture échoue ; aucun retry |
| Appels opérationnels / réseau du processus | 0 | Aucun endpoint, credential ou accès réel |
| Dépense nouvelle autorisée | 0 EUR | Aucun achat, abonnement, provisionnement ou engagement |
| Accès | Blue, Astra et Owner seulement dans leurs fonctions | Aucune extension implicite aux autres acteurs |

Ces limites sont des contraintes externes. ResourceBoundaryState ne mesure ni CPU, ni mémoire, ni temps. Avant tout grant, il faut identifier le moyen existant et autorisé de mesure/arrêt, sa sémantique mémoire et son responsable. Si ce moyen manque ou nécessite construction, STOP et autorisation technique distincte. Aucun mécanisme nouveau n'est installé par cette section.

Le contrôle futur de ressources ne mesure pas la cadence/latence d'une source ; aucune mesure chiffrée de ressource ne doit être transformée en résultat économique ou en champ de rapport non admis.

### 8.4 Destination et conservation proposées

Destination documentaire exacte de la preuve conservée : le fichier natif existant `OWNER_A2_PARTIAL_CONFIGURATION_DECISION_2026-10-06.md`, identité `libfile_4f09286d65ac8191a6e343b85aff696e`, dans une section future intitulée `EVIDENCE_A2_DOC_INTEGRATION_V1`. Cette section de preuve n'est pas créée maintenant. Le custodian est PROJECT_OWNER ; aucune publication des preuves sur GitHub ni partage externe n'est proposé.

Cette destination est un choix de garde documentaire, pas un champ OutputManifest.destination et pas une preuve d'ACL. Vérifier avant toute conservation que les accès effectifs correspondent aux acteurs approuvés ; sinon STOP. La publication du présent texte de gouvernance ne publie aucun résultat futur.

Rétention proposée des enregistrements et motifs structurels : 30 jours calendaires à compter de la clôture de l'opération autorisée. À échéance, Owner retire les enregistrements de la section de preuve selon les capacités disponibles et bloque leur consultation. Les décisions de gouvernance historiques ne sont pas soumises à cette purge. L'absence de mécanisme de suppression effectivement vérifié, notamment pour les versions historiques, interdit de revendiquer une suppression complète : Owner doit ratifier une règle compatible avec les capacités constatées avant conservation. Une extension pour incident exige une décision explicite.

Texte canonique proposé pour `OutputManifest.retention_rule` :
```text
STRUCTURAL_EVIDENCE_ONLY; 30 calendar days from authorized operation closure; custodian PROJECT_OWNER; evidence destination existing Owner document libfile_4f09286d65ac8191a6e343b85aff696e / EVIDENCE_A2_DOC_INTEGRATION_V1; no public release; retention and deletion capabilities verified before custody; no automatic extension; governance decisions retained separately
```

`exportability = PermissionState.ALLOWED` est proposé uniquement comme condition de l'évaluation de release pour le destinataire Owner exact. Ce choix ne permet aucun export effectif : transport et conservation requièrent une portée documentaire explicitement accordée dans le futur grant. Les deux API ne réalisent ni écriture de fichier ni transmission.

### 8.5 Incidents et quarantaine

Responsable proposé : PROJECT_OWNER ; autorité de quarantaine et de reprise : PROJECT_OWNER. Blue ou Astra doit immédiatement arrêter sa séquence et avertir Owner par le canal de gouvernance déjà utilisé. Aucun message n'est envoyé maintenant.

Mesures proposées : bloquer la release, ne pas diffuser le contenu impliqué, conserver seulement une classe d'incident et une référence sûre, suspendre l'usage des éléments concernés, ne pas inspecter un payload pour investiguer. Aucun retry ou reprise automatique. Les effets externes reposent sur un mécanisme déjà autorisé ; sa disponibilité doit être établie avant toute opération.

Texte canonique proposé pour `incident_if_unexpected_information_revealed` :
```text
STOP; DENY and BLOCKED release; withhold affected content through an already-authorized mechanism; record safe incident class/reference only; escalate to PROJECT_OWNER; no payload investigation, retry or automatic resume; separate exact Owner direction required before recovery
```

### 8.6 Méthode d'évaluation CLEAR et disclosure

Évaluateur proposé : Astra. Owner ratifie la méthode ; Astra produit un constat documentaire motivé, lié aux versions et identités exactes. Ce constat ne certifie aucun payload, source, rapport effectivement généré ou isolation déployée.

Critères cumulatifs :
1. Input limité aux quatre références documentaires approuvées ; provenance A1 exact commit/chemin/blob vérifiée ; aucune observation ou métadonnée opérationnelle admise.
2. Output limité aux quinze éléments de §2.3 ; motifs et codes de détail examinés dans leur source exacte ; pas de texte libre, chiffre économique, préférence ou assertion issue d'un payload.
3. Acteurs, destinataire, manifests, policy, autorisations et journal explicitement liés ; aucun placeholder opérationnel et aucune différence matérielle non revue.
4. Pour la disclosure, inventaire borné des informations pertinentes déjà divulguées au destinataire, fourni dans le périmètre de gouvernance autorisé ; références exactes et inconnues explicites. Aucun endpoint, historique opérationnel ou payload n'est consulté pour le compléter.
5. Évaluer le cumul ancien + proposé pour le tuple exact `output_id + recipient_actor_id + recipient_role`. Une histoire vide, non fournie ou matériellement inconnue reste UNRESOLVED ; tout BLOCKED global prévaut.
6. Documenter chaque conclusion : critère, référence vérifiée, périmètre, constat et limitation. Une ratification ou une simple déclaration de sécurité n'est pas la preuve.

Preuve minimale attendue : tableau de ces six critères et références, résultat input/output séparé, revue du cumul pour le tuple Owner exact, justification des inconnues non matérielles éventuelles et signature documentaire d'Astra par son identité de gouvernance. Les références se limitent aux textes autorisés ; aucune preuve d'existence ou de construction de fixture n'est demandée.

Toute ambiguïté matérielle, exposition non évaluée, valeur hors allowlist ou preuve manquante entraîne UNRESOLVED/BLOCKED, maintien de la quarantaine et absence de release. Aucune attestation CLEAR n'est produite par cette section.

Valeurs présentes : leakage input/output UNRESOLVED ; disclosure output et ledger UNRESOLVED ; quarantaine BLOCKED_PENDING_OWNER_REVIEW. Valeurs futures CLEAR uniquement après preuves et revue correspondantes ; aucun remplacement automatique.

### 8.7 Policy complète candidate et recalcul

La base de §2 est conservée. La paire destinataire proposée est exactement `(project-owner.weather-v4.a2.doc-integration.v1, Role.RESEARCH_VIEWER)`. Les valeurs de rétention et d'incident sont celles de §§8.4–8.5. Les autres champs déterminés restent ceux de §2 et des chaînes exactes du dossier Blue au commit `92088b83dd47799c6d413bb747138c05fdb0e420`.

Version cible documentaire proposée : `weather-v4-a2-doc-integration-v1`. C'est un token de version future, pas un commit déjà existant. Il remplacera le binding de version candidat seulement après ratification explicite ; il doit être identique dans HarnessPolicy, AuthorityBinding et TrustedExecutionPolicyRoot. La référence de logique examinée reste `78d537de681363ed83a6c7787aba4319f3c73c4d`.

Freeze permis seulement après ratification des propositions, constats documentaires requis, résolution des valeurs canoniques et disposition des limites techniques. Les 17 champs input, 13 output et 12 policy doivent être explicitement fixés avant computation.

Calcul futur, non autorisé ici : input et output selon les fonctions existantes, insertion des deux identités dans policy, calcul de policy, vérification indépendante de la canonicalisation et enregistrement des bindings. Aucun digest n'est calculé ou attribué.

Tout changement canonique, notamment actor/rôle destinataire, exportabilité, états CLEAR, version, texte de rétention ou d'incident, impose recalcul de l'identité concernée et des bindings dépendants. Les durées/ressources/accès hors champs canoniques sont liés séparément à cette §8 au commit exact qui la publie. Le texte de rétention et sa référence de destination sont couverts par le digest output ; aucune exception implicite.

### 8.8 Transition de trusted root proposée, non autorisée

Périmètre technique futur proposé : `research/weather_forward/v4/a2_harness/trusted_root.py` uniquement, pour les deux constantes de root/autorité, leurs annotations appropriées et le resolver. Aucun setter caller, injection de root de test, modification de contract.py/harness.py, nouvel endpoint ou élargissement de classes/actions.

La root cible devra contenir :
- execution_policy_authority_sha : SHA exact de la future autorité Owner d'exécution, pas de la présente décision partielle ;
- expected_construction_authority_sha : `37e3b25f17a7c5d3b3bc8d37df730aa988585b6c` ;
- expected_harness_identity : `research/weather_forward/v4/a2_harness` ;
- expected_harness_version_or_commit_identity : token cible proposé ci-dessus, une fois ratifié ;
- expected_policy_identity : digest dérivé final de policy.

Critères de réconciliation : commit de transition exact enregistré après construction autorisée ; diff confiné au périmètre ; autres sources examinées inchangées ou STOP ; lien à la logique revue à 78d537de ; contenu de root lié à l'autorité et au digest finaux ; aucune affirmation d'intégrité du code chargé fondée sur le seul token.

Preuves attendues sous autorité distincte : revue indépendante du diff et des bindings, vérification de la politique figée et des identities ; vérification bornée des mismatches, des refus et de la liaison au journal, ainsi que du chemin positif si autorisé. Aucun audit général D5 répété sans changement pertinent.

STOP si changement hors périmètre, autorité/digest/version discordant, racine non indépendante, identité chargée non justifiée selon la règle retenue, défaut de journal, contrôle de ressources absent ou besoin d'infrastructure non autorisée. La branche actuelle conserve une root absente et deny-all.

```text
TRUSTED_ROOT_TRANSITION = REQUIRES_SEPARATE_TECHNICAL_AND_BUILDER_AUTHORIZATION
DIGESTS = PENDING_FROZEN_CONTENT_AND_COMPUTATION
SECTION_8_RATIFIED = FALSE
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
BUILDER_AUTHORIZED = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED
```

Prochaine action : Owner ratifie, ajuste ou refuse les valeurs proposées de §8 ; les preuves documentaires sont ensuite établies dans le scope autorisé. La ratification des valeurs seule ne produit pas CLEAR et ne débloque ni calculation, Builder, trusted root ni exécution.
