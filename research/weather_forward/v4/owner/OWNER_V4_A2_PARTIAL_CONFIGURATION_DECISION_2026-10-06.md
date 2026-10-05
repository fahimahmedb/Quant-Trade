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
