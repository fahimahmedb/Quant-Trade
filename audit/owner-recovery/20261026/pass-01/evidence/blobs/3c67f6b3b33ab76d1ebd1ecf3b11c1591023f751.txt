# Décision Owner partielle — Weather V4 A2
## Intégration documentaire uniquement, sans fixture

Date de préparation : 2026-10-05  
Date de ratification initiale (§2) : 2026-10-06T00:04:40+02:00 — Europe/Paris  
Date de ratification complémentaire (§8) : 2026-10-06T08:12:30+02:00 — Europe/Paris  
Autorité déclarante : PROJECT_OWNER — utilisateur de cette conversation  
Statut du document : PARTIALLY_RATIFIED_WITH_BLOCKERS  
Effet actuel : ratification documentaire des clauses déterminées de §§2 et 8, sous leurs réserves ; aucune autorisation d'exécution.

Cette décision enregistre la ratification initiale de §2 puis la ratification complémentaire de §8 dans cette conversation. Les approbations et leur portée sont consignées en §§7 et 9. Les réserves, preuves manquantes et prérequis techniques demeurent bloquants. Aucune ratification finale de configuration ni permission technique ou d'exécution n'est accordée.

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

Cette décision enregistre la ratification documentaire de §§2 et 8. Les valeurs et critères de §8 sont approuvés sous leurs réserves ; les conditions factuelles et techniques restent non établies. Elle n'authentifie aucun acteur opérationnel, n'accorde aucune permission par action et n'autorise aucun travail technique. Les déclarations non attribuées du dossier initial restent historiques ; les associations documentaires de §8 et le périmètre de §9 font foi après la ratification complémentaire.

État effectif après ratification :
```text
DRAFT_ACCEPTED_FOR_OWNER_DECISION = TRUE
OWNER_CONFIGURATION_DECISION = PARTIALLY_RATIFIED_WITH_BLOCKERS
RATIFIED_SCOPE = SECTIONS_2_AND_8_DOCUMENTARY_ONLY_SUBJECT_TO_ALL_RECORDED_RESERVATIONS
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

## 8. Configuration documentaire renseignée ratifiée — 2026-10-06

STATUT_DE_CETTE_SECTION = RATIFIED_DOCUMENTARY_CONFIGURATION_WITH_RESERVATIONS  
SECTION_8_RATIFIED = TRUE  
OWNER_CONFIGURATION_DECISION = PARTIALLY_RATIFIED_WITH_BLOCKERS  
A2_EXECUTION_AUTHORIZED = FALSE  
BUILDER_AUTHORIZED = FALSE  
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE

Cette section fournit les valeurs documentaires ratifiées par Owner, sous toutes les réserves qu'elle contient. Elle ne modifie pas le contenu des §§2.1–2.5 et n'accorde aucun droit technique. Les plafonds approuvés concernent une seule opération structurelle minimale future ; ils ne sont ni mesurés, ni dérivés d'un benchmark, ni actuellement imposés par le harnais. Les mentions « proposé » conservées dans les tableaux désignent les choix maintenant ratifiés documentairement ; les tokens ne constituent toujours pas des identités techniques authentifiées.

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
SECTION_8_RATIFIED = TRUE
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

Prochaine action : établir les preuves documentaires selon §8.6 dans le périmètre autorisé et documenter les capacités ou limites des moyens externes. La ratification des valeurs seule ne produit pas CLEAR et ne débloque ni calcul des digests, Builder, trusted root ni exécution.

## 9. Ratification complémentaire de la section 8

Autorité déclarante : PROJECT_OWNER, utilisateur de cette conversation.  
Message d'approbation : « Je ratifie ».  
Date de soumission : 2026-10-06T08:12:30+02:00 — Europe/Paris.  
Objet exact présenté : §8 publiée au commit `9c0edb58ece7568bb56a5b67bd03a2e7abd4f29a`, fichier `research/weather_forward/v4/owner/OWNER_V4_A2_PARTIAL_CONFIGURATION_DECISION_2026-10-06.md`, blob `3fe5bb949fe9108aff0827595f4b72dbbc8bf5d4`.

L'approbation suit la proposition explicite de ratifier §8 avec ses réserves et toutes les autorisations techniques et A2 maintenues à FALSE. Elle ratifie les associations documentaires d'acteurs et tokens, les permissions candidates sans grant, les plafonds, la destination, la rétention conditionnée aux capacités réelles, les responsabilités, la méthode et le format de preuve CLEAR/disclosure, la politique de recalcul et le plan de transition non exécuté.

Aucun chiffre, token, critère ou périmètre technique de §§8.1–8.8 n'est changé par cette ratification. Les propositions deviennent des choix documentaires approuvés ; les faits restent à établir. La référence publiée de §8 rend ces règles externes identifiables exactement, sans inclure automatiquement chaque règle dans la canonicalisation du harnais.

En particulier :
- identité documentaire != identité technique authentifiée ;
- READ_INPUT et RELEASE_OUTPUT restent UNRESOLVED ;
- leakage input/output et disclosure restent UNRESOLVED ;
- quarantine reste BLOCKED_PENDING_OWNER_REVIEW ;
- aucune preuve d'ACL, de purge complète, de mesure/arrêt des ressources ou d'intégrité du code chargé n'est déclarée ;
- la rétention de 30 jours conserve toutes ses réserves sur les capacités réelles et les versions historiques ;
- la version cible est un token documentaire, pas un commit implémenté ;
- la ratification de méthode ne vaut pas application ni conclusion CLEAR ;
- le contenu canonique n'est pas complètement figé et aucun digest de manifest/policy n'est calculé.

```text
SECTION_8_RATIFIED = TRUE
OWNER_CONFIGURATION_DECISION = PARTIALLY_RATIFIED_WITH_BLOCKERS
DOCUMENTARY_VALUES_RATIFIED = TRUE
FINAL_CONFIGURATION_RATIFIED = FALSE
CANONICAL_CONTENT_FULLY_FROZEN = FALSE
DIGESTS = PENDING_FROZEN_CONTENT_AND_COMPUTATION
CLEAR = NOT_ESTABLISHED
READ_INPUT_AUTHORIZATION_STATE = UNRESOLVED
RELEASE_OUTPUT_AUTHORIZATION_STATE = UNRESOLVED
A2_RESEARCH_FIXTURE_AUTHORIZED = FALSE
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

L'enregistrement reste documentaire, sans signature cryptographique ou grant opérationnel. La publication modifie uniquement le présent fichier Owner, sans merge ni modification de source. Aucun import/appel du harnais, test, fixture, calcul d'identité ou activation de root n'est effectué.

NEXT_SAFE_ACTION = TARGETED_DOCUMENTARY_EVIDENCE_REVIEW_UNDER_EXISTING_A1_SCOPE_ONLY

## 10. Attestation documentaire ciblée — preuves de §8.6

Date : 2026-10-06.  
MISSION = DOCUMENTARY_EVIDENCE_PREPARATION_ONLY.  
SNAPSHOT = 6bba1e2fc4b44d817726187d8aa62182efe1ec3c.  
Émetteur : assistant ayant participé à la préparation de la configuration.  
ASTRA_INDEPENDENT_DOCUMENTARY_REVIEW = NOT_PERFORMED_BY_THIS_ATTESTATION.

Cette attestation prépare les preuves et évalue leur complétude. Elle n'est pas une signature Astra ni un nouveau PASS indépendant. Elle ne modifie aucune clause ratifiée. Les accès sont limités aux lectures/publications de gouvernance ; aucun accès opérationnel, fixture ou payload.

### 10.1 Sources vérifiées

Tous les chemins sont relatifs à research/weather_forward/v4/.

| Source | Commit exact | Chemin et section | Blob retourné par Git |
|---|---|---|---|
| Décision ratifiée | `6bba1e2fc4b44d817726187d8aa62182efe1ec3c` | `owner/OWNER_V4_A2_PARTIAL_CONFIGURATION_DECISION_2026-10-06.md`, §§2, 8–9 | `0d018b7527ea6957bdf2e3395810ef5ac0c1777a` |
| Déclarations de manifests/policy | `92088b83dd47799c6d413bb747138c05fdb0e420` | `blue/BLUE_V4_A1_DOCUMENTATION_2026-10-04.md`, §§13.4–13.8 | `44eff971f29b50f2d514b0e02917ad7cff9bb3f7` |
| Autorité/provenance A1 | `728cf23e7d69a373306f3c1a3fb5d11240210cda` | `owner/OWNER_V4_PHASE_GATE_A1_DECISION_2026-10-04.md`, §§3–5 et 9–10 | `483907e4f719ec8bcb3851af0f184690cea96279` |
| Interfaces et motifs | `78d537de681363ed83a6c7787aba4319f3c73c4d` | `a2_harness/harness.py`, _assess_input_read, _assess_output_release, _complete_with_required_log | `00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4` |

Les blobs sont des identités retournées par le dépôt, pas des digests calculés pendant cette mission. La source des interfaces a été lue comme texte ; aucun import, appel ou test. Aucun audit D5 clos n'est relancé.

### 10.2 Matrice des critères ratifiés

| Critère de §8.6 | Preuve examinée | Constat | Limitation / preuve absente |
|---|---|---|---|
| 1 — input/provenance | Owner §2.2 ; Blue §13.4 ; A1 exact | Exactement quatre champs permis : document_commit_sha, document_path, document_blob_sha, authorized_documentary_scope_reference. Le commit, chemin et blob A1 référencés sont résolus | Vérification de la spécification uniquement ; aucune instance créée ou inspectée |
| 2 — output/motifs | Owner §2.3 ; Blue §13.5 ; interfaces exactes | Quinze éléments structurels ; observations, performance économique, préférences et textes libres exclus. Deux motifs de succès identifiés textuellement ci-dessous | Aucun résultat/rapport réel ; inventaire complet des diagnostics de refus/erreur divulgables absent |
| 3 — liaisons | Owner §§8.1–8.2 et 8.7–8.8 ; Blue §§13.6–13.7 | Les acteurs documentaires, rôles/actions, IDs de manifests et version cible sont explicites ; approbateur distinct du destinataire | Identités dérivées non calculées ; autorité d'exécution absente ; autorisations UNRESOLVED ; IDs de journal non fixés ; configuration finale non figée ; identité technique non authentifiée |
| 4 — inventaire des expositions | Méthode Owner §8.6 ; sources de §10.1 | Les références utilisées pour cette attestation sont exactes | Aucun inventaire fourni par le destinataire ni preuve de couverture des expositions pertinentes. Une source consultée n'est pas une preuve de disclosure à Owner |
| 5 — cumul pour tuple exact | Owner §§8.1 et 8.6–8.7 | Tuple univoque reproduit ci-dessous ; aucun destinataire déduit du seul rôle | Historique pertinent absent ; évaluation cumulative Astra et justification CLEAR non fournies ; aucun ledger créé ou appelé |
| 6 — conclusion/provenance/limites | Présente matrice et sources | Constats et inconnues séparés ; aucune ratification substituée à la preuve | Signature/revue documentaire Astra non produite par le préparateur. Le précédent PASS technique ne porte pas sur cette nouvelle évaluation |

### 10.3 Portée du constat et motifs

L'entrée déclarée n'admet que les quatre références de gouvernance de §2.2 ; les 20 champs interdits restent exclus. Les noms de catégories interdites, tels que PnL ou cadence, ne sont pas des valeurs opérationnelles admises.

Constat étayé : **aucun contenu opérationnel n'est admis par la spécification examinée**. Cela ne certifie ni l'absence de données dans un futur objet ni l'enforcement du contenu. Aucune ouverture de payload n'est nécessaire ou autorisée pour ce constat documentaire.

La sortie déclarée reste limitée aux quinze éléments de §2.3. Le harnais ne produit pas ce rapport, ne sanitise pas un payload et ne réalise pas un export. Les contraintes de visibilité et de transport restent externes.

La source porte les deux motifs de succès avant logging :
- INPUT_READ_ELIGIBLE_PENDING_REQUIRED_LOG ;
- OUTPUT_RELEASE_ELIGIBLE_PENDING_REQUIRED_LOG.

La finalisation remplace textuellement PENDING_REQUIRED_LOG par LOGGED_AND_COMPLETED. Les motifs finaux attendus sont donc, par **déduction statique non exécutée** :
- INPUT_READ_ELIGIBLE_LOGGED_AND_COMPLETED ;
- OUTPUT_RELEASE_ELIGIBLE_LOGGED_AND_COMPLETED.

Ces codes décrivent un résultat structurel, sans mesure économique ou opérationnelle. Cette liste n'est pas une allowlist exhaustive ratifiée : les diagnostics de refus/erreur non recensés ne sont pas déclarés sûrs à divulguer. Leur inventaire ciblé reste à compléter à partir de la source autorisée, sans exécution.

### 10.4 Disclosure cumulative

```text
output_id = A2-DOC-OUT-STRUCTURAL-REPORT-V1
recipient_actor_id = project-owner.weather-v4.a2.doc-integration.v1
recipient_role = RESEARCH_VIEWER
```

Le tuple correspond à la configuration ratifiée. Il ne prouve aucune réception, exposition passée, authentification ou release.

Il manque un inventaire borné des informations pertinentes déjà reçues par ce destinataire, les sources/couverture de cet inventaire, ses inconnues matérielles et l'appréciation du cumul ancien + proposé par l'évaluateur désigné. Les seules références de §10.1 ne constituent pas un historique d'exposition.

Une histoire vide, non fournie ou non couverte reste UNRESOLVED. Aucune absence d'exposition ou absence de BLOCKED global n'est inférée. Tout BLOCKED global constaté ultérieurement conserve sa priorité.

### 10.5 Inconnues et résolution minimale

| Inconnue | Effet | Résolution documentaire minimale |
|---|---|---|
| Expositions pertinentes d'Owner | Empêche la preuve des critères 4–5 | Inventaire borné fourni/attesté par Owner, références, couverture et inconnues |
| Évaluation indépendante désignée | Critère 6 non complet | Revue documentaire ciblée d'Astra sur ces preuves, sans fixtures, digests ni runtime |
| Motifs de refus/erreur divulgables | Critère 2 partiellement étayé | Liste finie issue de la source et appréciation documentaire des motifs |
| Bindings finaux et journal | Critère 3 partiellement documenté | Distinguer contenu/références documentaires, valeurs dérivées non calculées, futurs grants et preuves d'exécution ; aucun placeholder soumis à une API |
| ACL, purge, mesure/arrêt, identité chargée | Prérequis externes non vérifiés | Références à des capacités déjà attestées ; sinon blocage et éventuelle autorité technique distincte |

Si le critère 3 est interprété comme exigeant des digests ou permissions effectives pour obtenir une conclusion documentaire avant leur calcul/activation, il crée une dépendance incompatible avec le scope courant. Cette interprétation doit être clarifiée documentairement ; cette attestation ne modifie ni ne dispense le critère. Aucun calcul ou grant opérationnel n'est demandé pour combler artificiellement une preuve documentaire.

Ces actions restent ciblées : aucune nouvelle matrice générale, reprise A1 ou recheck D5. Les moyens externes ne sont pas construits ou certifiés ici.

### 10.6 Conclusion

Les frontières de la spécification input/output sont étayées. Les preuves exigées ne sont pas complètes, principalement pour le cumul, les bindings finaux et la revue indépendante. La conclusion CLEAR ne peut pas être établie.

```text
ATTESTATION_RESULT = CLEAR_NOT_ESTABLISHED
CLEAR_DOCUMENTARY_BASIS_ESTABLISHED = FALSE
ASTRA_INDEPENDENT_DOCUMENTARY_REVIEW = NOT_PERFORMED_BY_THIS_ATTESTATION
INPUT_SPECIFICATION_SCOPE = DOCUMENTARY_ONLY_SUPPORTED_BY_REVIEWED_TEXT
OUTPUT_SPECIFICATION_SCOPE = STRUCTURAL_ONLY_SUPPORTED_BY_REVIEWED_TEXT
INPUT_LEAKAGE_ASSESSMENT = UNRESOLVED
OUTPUT_LEAKAGE_ASSESSMENT = UNRESOLVED
CUMULATIVE_DISCLOSURE = UNRESOLVED
QUARANTINE = BLOCKED_PENDING_OWNER_REVIEW
SECTION_8_RATIFIED = TRUE
DIGESTS = PENDING_FROZEN_CONTENT_AND_COMPUTATION
HARNESS_IMPORTED = NO
HARNESS_CALLS = NONE
TESTS_RUN = NO
MANIFEST_POLICY_DIGESTS_COMPUTED = NO
FIXTURES_CREATED = NONE
FIXTURES_ACCESSED = NONE
REAL_DATA_ACCESSED = NONE
REAL_OPERATIONAL_METADATA_ACCESSED = NONE
OPERATIONAL_ENDPOINTS_QUERIED = NONE
OPERATIONAL_CREDENTIALS_USED = NONE
RUNTIME_CODE_MODIFIED = NO
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
BUILDER_AUTHORIZED = FALSE
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED
```

NEXT_SAFE_ACTION = PREPARE_BOUNDED_OWNER_DISCLOSURE_INVENTORY_AND_TARGETED_DOCUMENTARY_REVIEW_ONLY

## 11. Ratification de l'attestation documentaire §10

Autorité déclarante : PROJECT_OWNER, utilisateur de cette conversation.  
Approbation : « Je ratifie ».  
Date de soumission : 2026-10-06T08:22:15+02:00 — Europe/Paris.  
Objet ratifié : §10 au commit `7ea1aecc7d47b9ceadfc64b3190646c689c9d4fc`, fichier Owner existant, blob `eb0f51b7d5c397a018aa858d88e45a9c848d6745`.

Owner accepte l'attestation préparatoire, ses constats, ses limites et sa conclusion CLEAR_NOT_ESTABLISHED. Cette ratification ne transforme pas une inconnue en preuve, ne vaut pas signature ou revue indépendante d'Astra et ne dispense aucun critère de §8.6. Le contenu de §10 demeure inchangé.

La preuve d'un inventaire borné des disclosures pertinentes, l'évaluation indépendante désignée, les bindings documentaires complets et le périmètre des diagnostics divulgables restent à établir. La dépendance du critère 3 aux valeurs dérivées et aux futurs grants doit être clarifiée documentairement ; cette ratification n'accorde ni calcul de digest ni permission opérationnelle pour la contourner.

```text
SECTION_10_ATTESTATION_OWNER_RATIFIED = TRUE
ATTESTATION_RESULT = CLEAR_NOT_ESTABLISHED
CLEAR_DOCUMENTARY_BASIS_ESTABLISHED = FALSE
ASTRA_INDEPENDENT_DOCUMENTARY_REVIEW = NOT_PERFORMED_BY_THIS_ATTESTATION
INPUT_LEAKAGE_ASSESSMENT = UNRESOLVED
OUTPUT_LEAKAGE_ASSESSMENT = UNRESOLVED
CUMULATIVE_DISCLOSURE = UNRESOLVED
QUARANTINE = BLOCKED_PENDING_OWNER_REVIEW
SECTION_8_RATIFIED = TRUE
OWNER_CONFIGURATION_DECISION = PARTIALLY_RATIFIED_WITH_BLOCKERS
DIGESTS = PENDING_FROZEN_CONTENT_AND_COMPUTATION
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

Cette publication est documentaire uniquement : aucun changement de source, import/appel du harnais, test, calcul d'identité, création/inspection de fixture ou activation de root. Aucun merge.

NEXT_SAFE_ACTION = PREPARE_BOUNDED_OWNER_DISCLOSURE_INVENTORY_AND_TARGETED_DOCUMENTARY_REVIEW_ONLY

## 12. Désignation Owner du moyen de mesure et d'arrêt des ressources — 2026-10-07

Autorité déclarante : PROJECT_OWNER, utilisateur de cette conversation.  
Date d'enregistrement : 2026-10-07T02:46+02:00 — Europe/Paris (heure de rédaction ; l'horodatage exact des messages Owner n'est pas disponible).  
Rédaction : assistant documentaire de cette conversation, à la demande expresse d'Owner (« Tu peux le faire toi ? »). Ni Blue, ni Astra, ni Builder.  
Statut : DÉSIGNATION DOCUMENTAIRE. Aucun accès à l'hôte, aucune vérification, aucune autorisation technique.

### 12.1 Objet

§8.3 exige, avant tout grant, d'identifier le moyen existant et autorisé de mesure et d'arrêt, sa sémantique mémoire et son responsable. Le dossier Blue (branche `blue/weather-v4-a2-consolidated-preparation-2026-10-06`, commit `8ee801a3c8d7f5dc56601ed17f23d1ce8303f6fe`, §14.6) enregistre ces contrôles NOT_VERIFIED. La présente section désigne le moyen. Elle ne modifie aucune valeur de §8.3 et ne rouvre aucun choix ratifié.

### 12.2 Déclarations Owner enregistrées

Owner a déclaré dans cette conversation, le 2026-10-07 :

- l'hôte désigné est sa VM Oracle Cloud existante, celle que le dépôt nomme `quant-p0-targer` (2 OCPU ARM, 12 Go) ;
- système : Ubuntu (version non précisée) ;
- « rien d'important tourne sur cette vm et aucune donnée » ;
- aucun terminal disponible pour l'instant ;
- sur la règle antérieure citée ci-dessous : « On oublie l'ancien projet c'était des données de marchés donc pas utilisé par quant p0 ».

Ces déclarations sont attribuées, non vérifiées. L'absence de données réelles et de credentials opérationnels sur l'hôte sera constatée lors de la vérification autorisée.

### 12.3 Règle antérieure sur l'hôte

Deux documents du dépôt, au commit `021c869987f48e63bb5835557970675530bbfa72`, indiquent que `quant-p0-targer` est la cible de qualification P0 et n'est pas utilisé pour Weather :

- `research/weather_forward/WEATHER_V3_BLUE_WORK_BREAKDOWN_2026-10-02.md`, §5.5, blob `41fea7bceca640f81f807eefcbd11db804067532` ;
- `research/weather_forward/WEATHER_V2_D4_CONVERGENCE_LEDGER_2026-10-01.md`, règle de calcul 5, blob `25771529d836138bbfc1d3f149b24d1a0cc4ec1c`.

Owner déclare cette restriction sans objet, l'hôte n'étant plus utilisé par P0 (§12.2). Effet enregistré ici : la restriction ne fait plus obstacle à l'usage de l'hôte pour le contrôle des ressources A2. Les deux documents historiques restent inchangés. Cette section ne modifie pas le statut général de P0 dans les fichiers de gouvernance ; une telle mise à jour relève d'une décision distincte.

### 12.4 Moyen désigné et correspondance avec §8.3

Contrôle externe au harnais, appliqué par systemd sur l'hôte désigné : unité transitoire `systemd-run`, exécutée sous un utilisateur dédié sans privilège (nom proposé : `a2runner`). Les propriétés ci-dessous sont la correspondance technique proposée ; leur valeur exacte est établie lors de la vérification autorisée.

| Limite §8.3 | Mécanisme candidat | Sémantique retenue |
|---|---|---|
| 60 s écoulées | `RuntimeMaxSec=60` | Arrêt de l'unité entière au-delà |
| 5 s CPU, un processus, aucun enfant | `LimitCPU=5` ; `TasksMax` | Temps user + système du processus, tous threads ; création d'enfant refusée |
| 128 MiB | `MemoryMax=128M` ; `MemorySwapMax=0` | Mémoire réelle du cgroup de l'unité (pic mesuré), sans swap ; pas la mémoire virtuelle |
| 1 MiB d'artefacts, temporaires inclus | Un seul système de fichiers temporaire de 1 MiB comme unique emplacement inscriptible ; `ProtectSystem=strict` ; `ProtectHome=yes` | Le traitement exact de `/tmp`, `/var/tmp` et `/dev/shm` est établi lors de la vérification |
| 64 KiB de sortie | Sortie écrite dans un fichier de l'emplacement inscriptible ; taille contrôlée après l'arrêt | Tout dépassement vaut STOP |
| 0 appel réseau | `PrivateNetwork=yes` | Aucune interface hors boucle locale |
| Mesure | Comptabilité de l'unité systemd ; à défaut, `memory.peak` du cgroup | Disponibilité selon les versions de systemd et du noyau, à constater |
| 0 EUR | Hôte existant | Aucun provisionnement, achat ou engagement |

Responsable des contrôles : PROJECT_OWNER, opérateur de l'hôte, en cohérence avec ses fonctions de §8.1. Blue reste exécutant et orchestrateur des évaluations ; Astra reste approbateur.

Les valeurs mesurées sont des preuves de contrôle. Elles ne deviennent pas des champs du rapport structurel et ne sont pas transformées en résultat économique (§8.3).

### 12.5 Points ouverts, non tranchés

- **Visibilité de l'opérateur.** Owner opère l'hôte et est aussi l'unique destinataire. La sortie de l'opération réelle ne doit pas s'afficher dans le terminal de l'opérateur avant la release : seuls le code de sortie et les mesures de contrôle lui sont montrés. Le mode exact relève du futur package d'intégration.
- **Accès sudo** de l'opérateur, à confirmer.
- **Versions** d'Ubuntu, de systemd et du noyau ; cgroup v2 actif ; disponibilité de la mesure du pic mémoire.
- **Modifications de l'hôte** (utilisateur dédié, fichiers copiés) : à consigner lors de leur réalisation autorisée.
- **Identité du code chargé.** Moyen candidat pour §8.8 : comparer, sur l'hôte, `git hash-object` des fichiers du harnais avec les blobs revus enregistrés au §14.1 du dossier Blue. Candidat seulement ; aucune affirmation d'intégrité n'est faite.

### 12.6 Plan de vérification proposé, non autorisé

Exécutable seulement sous autorisation Owner explicite, lorsqu'un terminal est disponible. Il n'importe ni n'exécute le harnais ; seuls des scripts factices sont utilisés.

1. Constater l'environnement : versions d'Ubuntu, de systemd, du noyau et de Python ; cgroup v2 ; architecture ; absence de données réelles et de credentials opérationnels.
2. Créer l'utilisateur dédié sans privilège et vérifier qu'il ne lit pas les autres répertoires.
3. Tests de dépassement, chacun devant aboutir à l'arrêt ou au refus attendu : attente de 120 s ; boucle CPU ; allocation de 200 MiB ; création d'un processus enfant ; connexion réseau ; écriture de 2 MiB ; sortie de 100 KiB.
4. Témoin positif : un script conforme rapporte sa durée, son temps CPU et son pic mémoire.
5. Facultatif, pour §8.8 : comparaison des identités de fichiers du harnais copiés avec les blobs revus.

Les transcripts de ces tests constitueraient la preuve de `CONTROL_VERIFIED`. Un dépassement non arrêté vaut échec du contrôle et STOP.

### 12.7 États

```text
RESOURCE_CONTROL_MEANS_DESIGNATED = TRUE
RESOURCE_CONTROL_HOST = OWNER_EXISTING_ORACLE_CLOUD_VM_QUANT_P0_TARGER_UBUNTU
RESOURCE_CONTROL_MECHANISM = SYSTEMD_TRANSIENT_UNIT_EXTERNAL_TO_HARNESS
RESOURCE_CONTROL_RESPONSIBLE = PROJECT_OWNER
MEMORY_SEMANTICS = CGROUP_UNIT_REAL_MEMORY_PEAK_NO_SWAP
PRIOR_HOST_RESTRICTION = DECLARED_OBSOLETE_BY_OWNER_P0_NO_LONGER_USING_HOST
P0_GOVERNANCE_STATUS_CHANGED_BY_THIS_SECTION = NO
CONTROL_IMPLEMENTED = NOT_VERIFIED
CONTROL_VERIFIED = NOT_VERIFIED
CONTROL_VERIFICATION_AUTHORIZED = FALSE
HOST_ACCESSED = NO
SECTION_8_VALUES_CHANGED = NO
CLEAR = NOT_ESTABLISHED
QUARANTINE = BLOCKED_PENDING_OWNER_REVIEW
DIGESTS = PENDING_FROZEN_CONTENT_AND_COMPUTATION
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

Publication documentaire uniquement : ajout de cette section au fichier Owner, sans merge, sans modification d'une autre section ou d'un autre fichier, sans accès à l'hôte, test, import ou appel du harnais, calcul d'identité ou fixture. La revue documentaire d'Astra n'en dépend pas.

NEXT_SAFE_ACTION = OWNER_AUTHORIZED_CONTROL_VERIFICATION_WHEN_TERMINAL_AVAILABLE_INDEPENDENT_OF_ASTRA_REVIEW
