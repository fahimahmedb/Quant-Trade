# BLUE — WEATHER V4 A1 DOCUMENTATION — 2026-10-04

ARTIFACT_TYPE = A1_DOCUMENTARY_CANDIDATE  
A1_DOCUMENTATION = READY_FOR_OWNER_REVIEW  
A1_DOCUMENTATION_SCOPE = AUTHORIZED  
THIS_DOCUMENT_APPROVES_FUTURE_EXECUTION = FALSE  
PROPOSED_MANIFESTS_AND_POLICIES_OWNER_RATIFIED = FALSE

## 1. Exact authority and authorized work

|Input authority|Exact SHA|Artifact and verified blob|
|---|---|---|
|Owner A1 decision; branch owner/weather-v4-phase-gate-a1-decision-2026-10-04|728cf23e7d69a373306f3c1a3fb5d11240210cda|research/weather_forward/v4/owner/OWNER_V4_PHASE_GATE_A1_DECISION_2026-10-04.md; 483907e4f719ec8bcb3851af0f184690cea96279|
|Blue phase-gate support|d669e603b87ac95c85c80861646de859df1b8819|research/weather_forward/v4/blue/BLUE_V4_PHASE_GATE_DECISION_SUPPORT_2026-10-04.md; db0ae4ba933041f0c1d89cb3a9f8fdbacb913aeb|
|Astra pre-op audit|926741e7a67cb80bccde0ff428f2837bb200cf19|research/weather_forward/v4/audit/ASTRA_V4_PRE_OP_CONTRACT_AUDIT_2026-10-04.md; 2f285b19dc6a61947ba7be78f48bb35425c71de6|

All exact commits/artifacts resolved independently. Owner branch HEAD equals 728cf23e…; parent is d669e603…; that support's parent is 926741e7…. These are documentary Git reads, not operational endpoint probes. Existing owner decisions, structural contract, audit qualifications, support artifacts and canonical registry are unchanged.

The owner selected Option A, authorized only A1 documentation, left A2 conditionally authorizable after prerequisite attestation, denied Option B for now, and declined C as the current path. This document implements the authorized documentation scope. It supplies proposed manifests/policies and a bounded evidence attestation; it is not an owner ratification of these proposals or a fixture/control test result.

PHASE_AUTHORIZATION = A1_ONLY_AT_INITIAL_GATE  
A2_EXECUTION_AUTHORIZED = FALSE  
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE  
A2_FIXTURE_TESTING_AUTHORIZED = FALSE  
OPTION_B_AUTHORIZED = FALSE  
BUILDER_AUTHORIZED = FALSE  
CAPTURE_AUTHORIZATION = NONE  
ECONOMIC_AUTHORITY = 0  
DATA_T0 = NOT_DECLARED  
EXPERIMENT_T0 = NOT_DECLARED

## 2. Harness attestation — documentary evidence only

A2_EXISTING_APPROVED_HARNESS = NOT_ATTESTED  
A2_PREREQUISITES_COMPLETE = FALSE  
A2_BLOCKER = HARNESS_NOT_ATTESTED_AND_REQUIRED_PREREQUISITES_UNRESOLVED

|Exact reviewed governance evidence|What it establishes|What it does not establish|
|---|---|---|
|Owner A1 decision §§4–5 at 728cf23e…|Requires existing explicitly approved offline harness, identity/version/approval and required controls before considering A2|No harness identity, version, approval authority/artifact or approved fixture-generation path supplied|
|Blue phase-gate support §§3–4, 6, 10 at d669e603…|An approved existing offline harness is a prerequisite; missing implementation cannot be created under this scope|No exact harness or approval attestation|
|Astra report §§4, 7–8 at 926741e7…|Structural fail-closed requirement, no established technical implementation/effectiveness, fixture provenance firewall|No harness/control certification or actual fixture approval|

This is a NOT_ATTESTED finding within the authorized evidence corpus, not a claim that no code or harness exists anywhere. Mere code, a test directory, past test success or an agent's recollection would not prove approval for this exact scope. No source-code, test/fixture inventory, executable, actual fixture, operational registry or endpoint was searched or inspected. No harness was run.

The harness-resolution activity stops here. Remaining A1 output is documentary specification only and does not require resolving or building a harness. Owner review may later supply an exact governance attestation identifying immutable harness/version/approval scope; this document does not authorize broader searching or testing.

If a later authorized assessment establishes that any harness, vault, isolation layer, access-control mechanism, collector or runtime/control component must be newly constructed:
A2_BLOCKER = SEPARATE_BUILDER_AUTHORIZATION_REQUIRED.
That conditional rule is not a finding that construction is currently necessary; construction need is NOT_ATTESTED. No Builder assigned.

## 3. Proposed PHASE_INPUT_MANIFEST

MANIFEST_TYPE = DOCUMENTARY_CANDIDATE  
MANIFEST_SCOPE = A1_ONLY  
FUTURE_EXECUTION_APPROVED = FALSE

The following schema and populated entries specify only already-authorized governance material. They instantiate no observational source, endpoint, city, station, model, cadence, universe, credentials, real technical metadata or fixture. Required unknown future values cannot be replaced by a permissive default.

### Exact schema semantics

|Field|Required type/meaning|
|---|---|
|input_id|Immutable documentary identifier; no identifier reuse for changed bytes|
|input_classification|DOCUMENTATION_ONLY / NON_ECONOMIC_SYNTHETIC / REAL_TECHNICAL_METADATA / PROHIBITED; only DOCUMENTATION_ONLY admitted in current A1|
|source_provenance_class|Exact governance authority/support/audit or governance Git object lineage; future synthetic lineage separately attested|
|exact_permitted_fields|Finite content/field allowlist and exact SHA/path/blob binding; no wildcard traversal into linked data/code|
|exact_prohibited_fields|All content outside the allowlist plus universal prohibited classes below|
|permitted_reader_roles|Explicit role-to-input class mapping; assignment grants no operational capability|
|raw_values_visible|Whether exact permitted documentary text/metadata is visible; cannot imply visibility of operational raw values|
|timestamps_visible|Governance document dates/version history only for A1; actual observational/network/delivery timestamps denied|
|frequency_or_count_information_visible|Only documentary integrity counts such as declared unresolved entries; no operational/event/frequency counts|
|longitudinal_observation_allowed|No operational observation; fixed authority versions may be compared for documentary consistency|
|aggregation_allowed|Only documentary authority/requirement/provenance aggregation|
|cross-source_comparison_allowed|Only comparison of these governance documents; no weather/market/data-provider comparison|
|efficacy_leakage_assessment|Pre-read scope assessment and STOP rule; unexpected outcome content must not be explored or summarized|
|access_logging_requirement|Document record fields in §7; operational access logging is not implemented/certified here|
|quarantine_on_ambiguity|Required STOP/no further read-use-release at ambiguous/prohibited content; record bounded incident|
|owner_approval_required|Current A1 owner authority binding; additional input/access requires separate exact authority|

### Populated documentary input entries

The shared restriction profile below is part of each row, not a default for other input classes.

|input_id|Exact binding|source_provenance_class|exact_permitted_fields|
|---|---|---|---|
|A1-IN-OWNER|728cf23e7d69a373306f3c1a3fb5d11240210cda; Owner A1 path/blob in §1|OWNER_GOVERNANCE_DECISION|Document text defining A1 permission, prohibitions, harness/prerequisite requirements and status|
|A1-IN-SUPPORT|d669e603b87ac95c85c80861646de859df1b8819; Blue support path/blob in §1|BLUE_GOVERNANCE_SUPPORT|Documentary A/B/C definitions, proposed manifest fields, roles, fixture policy, resource/stop/incident requirements; no option executed|
|A1-IN-AUDIT|926741e7a67cb80bccde0ff428f2837bb200cf19; Astra report path/blob in §1|INDEPENDENT_DOCUMENT_AUDIT|Recorded pre-op verdict and qualifications, exact audited identity, unresolved-register integrity and phase restrictions|
|A1-IN-GIT-AUTHORITY|The three exact authority commits above and Owner A1 branch; publication identity of this new artifact|GOVERNANCE_GIT_METADATA|Commit SHA, parent/tree SHA, path/blob identity and ref identity needed for authority and publication verification; no code/data/fixture blob content|

For EVERY populated entry:
- input_classification = DOCUMENTATION_ONLY.
- permitted_reader_roles = BLUE_A1_DOCUMENT_EXECUTOR, OWNER_REVIEWER, INDEPENDENT_DOCUMENT_REVIEWER within document scope. Blue is the currently authorized role; this does not invent real independent reviewers or operational actors.
- raw_values_visible = PERMITTED_DOCUMENT_TEXT_AND_ALLOWLISTED_GOVERNANCE_METADATA_ONLY.
- timestamps_visible = GOVERNANCE_DATES_ONLY.
- frequency_or_count_information_visible = DOCUMENT_INTEGRITY_COUNTS_ONLY.
- longitudinal_observation_allowed = NO_OPERATIONAL_OBSERVATION; exact governance history only.
- aggregation_allowed = DOCUMENTARY_REQUIREMENT_AND_AUTHORITY_MAPPING_ONLY.
- cross-source_comparison_allowed = GOVERNANCE_DOCUMENT_CONSISTENCY_ONLY.
- exact_prohibited_fields = real weather/market/trading/efficacy data; operational metadata/availability/timing/cadence/gaps/delivery; performance/rankings; operational credentials; fixtures/generator output/code execution; linked datasets/code/fixtures not opened merely because referenced.
- efficacy_leakage_assessment = AUTHORITY_TEXT_SCOPE_ONLY; unexpected efficacy-bearing material triggers STOP, not an expanded analysis.
- access_logging_requirement = §7 documentary record; quarantine_on_ambiguity = REQUIRED.
- owner_approval_required = SATISFIED_FOR_THIS_A1_DOCUMENT_SCOPE_BY_728cf23e…; any expansion remains unapproved.

Abstract future field classes only: fixture lineage/generator version, synthetic technical interface fields, restricted real technical field-presence/type classes. They have no populated record, actual content, operational identifier or A1 access permission. NON_ECONOMIC_SYNTHETIC is not admitted for actual inspection in A1; REAL_TECHNICAL_METADATA remains prohibited.

## 4. Proposed PHASE_OUTPUT_MANIFEST

This is a documentary candidate, not an operational release configuration. All logical output entries below are sections of this one Markdown file; they create no fixture, test result, response sample or runtime artifact.

### Exact output schema semantics

Every field is required. The shared restriction profile following the entries supplies explicit values for each row, not defaults for later A2/B outputs. Unknown future values prohibit the corresponding release.

|Field|Required type/meaning|
|---|---|
|output_id|Immutable logical output identifier bound to this artifact/version|
|output_type|DOCUMENTATION_ONLY for every current row; no technical finding or measured-result class admitted|
|exact_metric_or_artifact|Exact document section and defined documentary claim; no measured operational metric|
|granularity|Explicit maximum visible documentary detail; operational values and correlated proxies excluded|
|permitted_recipients|Finite authorized documentary role set; no implicit administrator/research exception|
|exportability|Exact permitted documentary destination/use; all other release paths denied|
|quarantine_status|Candidate/review state; ambiguous or prohibited content must be withheld|
|cumulative_disclosure_risk|Assessment including prior recipient knowledge, combined content and indirect disclosure|
|efficacy_leakage_assessment|Documentary-only assessment; unresolved efficacy risk blocks release|
|release_approval_requirement|Exact current A1 scope reference; later operational release requires separate authority|
|retention_rule|Governance record treatment and unresolved future retention choice; no invented period|
|incident_if_unexpected_information_revealed|Required STOP/quarantine/exposure/review mapping to §8|

### Populated documentary output entries

|output_id|exact_metric_or_artifact (output_type = DOCUMENTATION_ONLY for all rows)|granularity|
|---|---|---|
|A1-OUT-AUTHORITY|Documentary authority and scope receipt (§1)|Exact governance SHA/path/blob and permission semantics|
|A1-OUT-MANIFESTS|Input/output schema and admitted governance-only rows (§§3–4)|Field/class/role-level allow/prohibit semantics; no real-data examples|
|A1-OUT-CAPABILITIES|Abstract role/capability specification (§5)|Role-to-class access; actual future assignments unresolved|
|A1-OUT-FIXTURE-POLICY|Fixture admissibility/provenance specification (§6)|Construction-input/generator/version/log rules only|
|A1-OUT-LOG-INCIDENT|Logging, STOP, quarantine and reclassification specification (§§7–8)|Exact documentary fields and incident actions; no actual operational logs|
|A1-OUT-HARNESS-A2|Harness status and A2 prerequisite matrix (§§2, 9)|VERIFIED/UNRESOLVED/NOT_ATTESTED/NOT_APPLICABLE with cited documentary evidence, no technical test|
|A1-OUT-B-RESOURCES|Option B prerequisite and resource/time decision fields (§§10–11)|Dependency/permission boundaries; no request, credential, endpoint or numerical budget|

For EVERY output entry:
- permitted_recipients = OWNER_REVIEWER and independently assigned document reviewer; BLUE_A1_DOCUMENT_EXECUTOR may produce/check the document.
- exportability = authorized repository publication and owner handoff of this A1 document only; no messaging, operational export or data release.
- quarantine_status = PROPOSED_DOCUMENT_FOR_OWNER_REVIEW; unexpected prohibited information must be quarantined rather than included.
- cumulative_disclosure_risk = review all sections/previous documentary disclosures together; no operational time series, source ranking or efficacy summary may emerge by joining sections.
- efficacy_leakage_assessment = governed documentary statements only; unresolved ambiguity blocks affected publication/release.
- release_approval_requirement = A1 permits this documentary deliverable; owner must review before any further authority transition. Future A2/B releases require their own exact approval.
- retention_rule = committed governance history preserved under repository practices; operational log retention duration remains OWNER_DECISION_REQUIRED; no numeric duration invented.
- incident_if_unexpected_information_revealed = STOP and §8 actions; deletion never restores blindness.

Operational metric field: no measured availability, timing, latency, frequency, gap, delivery, profitability or efficacy metric is permitted. Documentary counts/statuses are integrity observations, not economic evidence.

## 5. Role/capability matrix and interface boundaries

These are abstract specifications, not actual appointments or implemented ACLs. Current document access is limited to the explicit input/output reader sets in §§3–4. Other role titles below describe future duties; a title alone grants no access. Research, custody or incident personnel would need an explicitly permitted documentary reader assignment before any current document view, and separate exact permissions before any later operational view.

|Role|A1 permitted capability|Prohibited / future unresolved|
|---|---|---|
|PHASE_OWNER / OWNER_REVIEWER|Review exact documents, select/ratify later bounded decisions|No phase implied by receipt/review; actual future resource/access assignments unresolved|
|BLUE_A1_DOCUMENT_EXECUTOR|Read allowlisted governance, author this specification and publish/verify its documentary identity|No operational execution, fixture inspection/generation, runtime, credential, harness or data access|
|CUSTODY_ADMIN|Conceptual duty: protect lineage/quarantine/logs; documentary design only now|No vault/key/admin/decrypt/operational capability provisioned; actual actor unresolved|
|RESEARCH_VIEWER|Approved documentary content only|No raw/intermediate observational/fixture/metadata view under A1|
|RELEASE_APPROVER|Conceptual independent review of scope/provenance/cumulative disclosure; documents only|No real release permission assigned; cannot grant A2/B/capture from a documentary result|
|INCIDENT_AUTHORITY|Conceptual STOP, bounded notice, exposure classification and request for precise owner instruction|No blanket authority to open quarantined data to investigate|
|INDEPENDENT_DOCUMENT_REVIEWER|Exact documentary consistency review when assigned|No claim of independent technical controls testing or operational access|

Access policy covers raw inputs, intermediates, logs, dashboards, error messages, debug traces, admin interfaces, key-management interfaces, indirect summaries and correlated metadata. Each future accessible class needs exact reader/recipient roles before access, not just export restrictions. If an administrator/agent/human sees efficacy-bearing information, suppressing an export cannot undo exposure.

A1 implements no vault, isolation, access controls, logging service or new harness. Its schema/interface documentation specifies fields, immutable provenance references, role boundaries, permitted projections and failure handling only. Actual field existence, parsing and interface behavior remain untested.

CAPTURE_IDENTITY != RESEARCH_IDENTITY remains the structural requirement for later applicable phases, not a deployed fact.
UNBLIND_IMPLEMENTATION_REQUIRED = ONLY_IF_REQUIRED_BY_THE_EXACT_AUTHORIZED_PHASE.
A1 requires no unblind/decryption/operational credentials; all remain prohibited or deferred. Later A2 must not acquire real validation access merely to test interfaces.

## 6. Fixture admissibility and provenance policy only

SYNTHETIC_LABEL_ALONE_ESTABLISHES_SAFETY = FALSE  
FIXTURES_CREATED = NONE  
ACTUAL_FIXTURES_INSPECTED = NONE  
ACTUAL_FIXTURES_APPROVED = NONE

|Policy field|Exact proposed rule|
|---|---|
|Allowed construction-input classes|Approved outcome-free DOCUMENTATION_ONLY schema/static-interface rules and independently attested NON_ECONOMIC_SYNTHETIC abstractions; no instance admitted now|
|Prohibited construction-input classes|Real observations or efficacy-revealing metadata/statistics: prevalence, signal, opportunities, market response, rankings, favored city/station/model/source, profitable latency, PnL, performance distributions, indirect summaries/calibrated priors derived from them|
|Provenance requirement|Complete immutable input lineage, author/agent construction history, permission basis, source/version/hash and declared rationale for each construction input; UNKNOWN fails closed|
|Generator/version requirement|Exact existing approved generator/harness identity/version and construction path must be attested before future generation; no invented generator, code or seed now|
|Input disclosure|Declare every material construction input and transformation; masked/randomized/aggregated/anonymized real calibration remains real-informed|
|Reproducibility requirement|Future approved generation must be reproducible from pinned permitted inputs, generator/method/version and declared randomization state where applicable; reproducibility alone does not establish admissibility|
|Logging requirement|Record generation authority, input/generator/content identity, actor/readers, intermediate views and release decisions; no hidden use of prior real efficacy exposure|
|Contamination rule|If real efficacy materially informed construction, classify according to actual provenance/exposure; fixture is not NON_ECONOMIC_SYNTHETIC merely by label|
|Quarantine rule|Deny generation/use/release on ambiguous or prohibited lineage; quarantine affected inputs/derivatives if encountered, append exposure/incident and await exact owner instruction|

Permitted future concepts could include abstract schema type/error boundaries and role-transition cases unrelated to real source behavior. No test vectors, fixtures, distributions, numeric examples, seeds or runnable generator are supplied. A1 cannot approve an actual fixture; prospective admission after a later exact authorization must be checked by appointed roles under the frozen policy.

## 7. Logging specification and documentary access record

LOGGING_CONTROL_IMPLEMENTED_OR_TESTED_BY_A1 = FALSE.

Future access-log specification:
record_id; authority_sha; manifest_version; artifact/input/output_id; immutable content/version reference; actor_role and assigned identity; permitted action; read/view/generation/release class; direct/indirect exposure class; access result; recipient set; supersedes; incident_id; quarantine/release decision and approver; resource-bound check; logging provenance/integrity reference. Where applicable, actual wall-clock logs must be segregated if they could reveal source/request/delivery patterns. Research-readable logs must not include secrets, prohibited values, operational timestamps/counts or their proxies.

Logs must account for denied/aborted acts, administrator/key capabilities and intermediate views, not merely exports. Append-only correction semantics; no silent erasure or backdated claim of access. Storage/retention, actual actors/control implementation and operational effectiveness are unresolved. A1 specifies these controls only.

Actual documentary receipt for this mission:
- three mandatory exact commit objects and three documents in §1 read through governance connector;
- Owner A1 branch identity verified;
- this document's Git identity/content and scope checked for publication;
- harness attestation limited to the cited governance text in §2;
- no source-code/fixture/harness execution or operational data/metadata accessed.

This receipt and Git history are documentary provenance, not proof of a deployed immutable access-log service. No exact per-access time is invented.

## 8. STOP, incident, quarantine and reclassification specification

THE_CONTRACT_REQUIRES_FAIL_CLOSED_BEHAVIOR  
TECHNICAL_CONTROL_IMPLEMENTATION_ESTABLISHED = FALSE  
TECHNICAL_CONTROL_EFFECTIVENESS_VERIFIED = FALSE

A1 must stop the affected activity if further completion requires prohibited data/metadata, fixture generation/inspection, endpoint access, credentials, code/harness execution, Builder or new infrastructure/control implementation. Record unresolved status and return to owner; no substitute route.

Required trigger classes:
UNEXPECTED_OUTCOME_BEARING_INFORMATION; EFFICACY_REVEALING_DATA; UNAUTHORIZED_RAW_DATA; AMBIGUOUS_INPUT_PROVENANCE; FIXTURE_PROVENANCE_VIOLATION; ACCESS_CONTROL_VIOLATION; UNEXPECTED_PRIVILEGED_ACCESS; OUTPUT_CAPABLE_OF_RANKING_FAMILIES; OUTPUT_CAPABLE_OF_RANKING_CITIES; OUTPUT_CAPABLE_OF_RANKING_STATIONS; OUTPUT_CAPABLE_OF_RANKING_MODELS; OUTPUT_CAPABLE_OF_RANKING_SOURCES; TIMING_INFORMATION_REVEALING_EDGE_ADVANTAGE; RESOURCE_BOUNDARY_EXCEEDED; INPUT_MANIFEST_MISMATCH; OUTPUT_MANIFEST_MISMATCH; UNAUTHORIZED_CROSS_SOURCE_COMPARISON; UNAUTHORIZED_LONGITUDINAL_AGGREGATION; REQUIRED_UNAUTHORIZED_IMPLEMENTATION_OR_EXECUTION.

For each trigger, the proposed incident workflow requires:
1. STOP implicated activity; no further reads/requests/generation and no autonomous retry.
2. LOG bounded class, authority/manifest/role/artifact identity and known/unknown scope. Do not quote unsafe values in ordinary logs or notices.
3. QUARANTINE implicated input/output/intermediate/log/derivatives through an already-authorized mechanism; if no permitted mechanism exists, stop and request exact owner direction rather than implementing one.
4. ACCESS_FROZEN and RELEASE_BLOCKED for affected surfaces, rights and cumulative summaries.
5. SURFACE_RECLASSIFIED_IF_APPLICABLE using actual direct/indirect correlated exposure: UNKNOWN when incomplete, DEVELOPMENT_ONLY or DISCOVERY_CONTAMINATED where justified; no new CONFIRMATORY_CLEAN certificate.
6. ESCALATED_TO_OWNER with safe evidence references and unresolved impact; no permission inferred to inspect quarantine.
7. INVESTIGATED_BEFORE_RESUME under exact authority, independently reviewed where required; owner direction needed before any expansion/resumption across the blocked boundary.

Missing provenance/access logs cannot be treated as no exposure. Incident reclassification must consider related hypotheses, dates/stations/systems/releases and derived summaries without opening prohibited data to prove cleanliness. Logical field-presence outputs, their repetitions, counts/order/timing and combined knowledge can disclose efficacy; accumulation must stop at uncertainty, not after a series has already been inspected.

CAPTURED != CLEAN  
SEALED != CONFIRMATORY_CLEAN  
DELETION_OF_LEAKED_INFORMATION_DOES_NOT_RESTORE_BLINDNESS

## 9. Future A2 prerequisite matrix — no activation

Status definitions:
VERIFIED = supported by the exact authorized documentary evidence for the stated claim only.
UNRESOLVED = future specification/decision absent or not ratified.
NOT_ATTESTED = required identity/approval/control evidence not supplied in the authorized corpus.
NOT_APPLICABLE = capability excluded from this A1 scope; not a waiver for a later changed phase.

|Prerequisite|Status|Exact finding / required later evidence|
|---|---|---|
|A1 documentary authorization|VERIFIED|Owner 728cf23e… authorizes A1 only|
|A2 prohibition until separate prerequisites/decision|VERIFIED|Owner §§2, 5; all three A2 authorization flags FALSE|
|Existing harness identity|NOT_ATTESTED|Need explicit immutable harness identity/path without inferring approval from code presence|
|Harness version|NOT_ATTESTED|Need exact approved version/commit/artifact hash|
|Harness approval authority|NOT_ATTESTED|Need exact authority empowered for this scope|
|Harness approval evidence|NOT_ATTESTED|Need explicit approval artifact tied to version and permissible tests; none in reviewed corpus|
|Fixture-generation path|UNRESOLVED|Need approved existing path/toolchain linked to attested harness; no path selected|
|Allowed fixture inputs|UNRESOLVED|Policy proposed in §6; actual pinned admissible generation inputs not approved/inspected|
|Prohibited fixture inputs|VERIFIED|Owner real-efficacy provenance prohibition is binding; enforcement NOT_ATTESTED|
|Output allowlist|UNRESOLVED|A1 documentary entries exist; later A2 exact technical outputs/metrics and granularity require ratification|
|Quarantined outputs|UNRESOLVED|Categories specified; actual quarantine capability/read permissions NOT_ATTESTED|
|Reader roles|UNRESOLVED|Abstract matrix exists; actual A2 assignments/access limits not supplied|
|Release roles|UNRESOLVED|Independent exact approver/recipients/permissions not appointed|
|Logging controls|NOT_ATTESTED|Specification present; no deployed integrity/access logs tested or certified|
|STOP rules|UNRESOLVED|Proposed documentary rules need exact A2 binding; actual enforcement NOT_ATTESTED|
|Incident controls|NOT_ATTESTED|No operational containment/investigation/independent-resume capability established|
|Resource/time bounds|UNRESOLVED|§11 fields have no owner-ratified numerical values|
|Whether Builder work is required|NOT_ATTESTED|Cannot infer a construction need or absence of one without authorized attestation; no Builder assigned|
|Real-data/operational endpoint/credential/capture capability|NOT_APPLICABLE|Excluded from contemplated offline A2; remains prohibited absent a different separate owner decision|
|Validation unblinding/decryption|NOT_APPLICABLE|No need for this offline documentary/fixture scope; remains prohibited|
|Separate exact A2 execution/generation/testing owner authority|UNRESOLVED|Prerequisites alone never activate A2; current flags remain FALSE|

Current outcome: A2_PREREQUISITES_COMPLETE = FALSE. No existing approved harness is resolved. Even later documentary identity attestation would not alone prove control effectiveness. Any required technical verification must itself be covered by a later precise authority; A1 does not execute tests to fill this gap.

Separate Builder need register: harness construction; fixture-generator construction; vault/isolation/access-control implementation; logging/quarantine/control infrastructure; collector/runtime modification — all NOT_ATTESTED_AS_NEEDED, all PROHIBITED_IN_A1. If any is required, STOP = SEPARATE_BUILDER_AUTHORIZATION_REQUIRED. The owner must separately authorize it; do not infer Builder authorization from A1/A2 prerequisites.

## 10. Option B prerequisite map — documentation only

OPTION_B_AUTHORIZED = FALSE  
OPTION_B_DESIGN != OPTION_B_EXECUTION

|Prerequisite|Status|Before later B consideration/execution|
|---|---|---|
|Exact safe technical question and request/response field boundaries|UNRESOLVED|Owner must specify without efficacy leakage; no endpoint/source/model/city/station/request populated now|
|Rights/credential scope and actual actors|UNRESOLVED|Need precise later authority; no credential value requested or used|
|Safe input restriction before any read/processing|NOT_ATTESTED|No raw observations may be fetched merely to redact later; if no safe interface, B unavailable|
|Actual isolation/admin/log/error/dashboard controls|NOT_ATTESTED|Need evidence under separate permitted work; cannot build or test them in A1|
|Input/output/metric allowlists and recipients|UNRESOLVED|Exact approved metadata classes, cumulative disclosure controls and quarantine permissions|
|Timestamp/frequency/delivery boundary|VERIFIED|Current permission excludes actual values/distributions/lead-lag, cadence/gaps/delivery and efficacy-revealing patterns; no measurement authorized|
|Longitudinal and cross-source restrictions|VERIFIED|No outcome-revealing aggregation/comparison; operational enforcement NOT_ATTESTED|
|Stop/incident/resource/time bounds|UNRESOLVED|Exact binding and actor/capability proof required; no values supplied|
|Separate Owner Option B phase-gate|UNRESOLVED|A1, Astra PASS and completed documentation cannot grant B|
|Unblinding / collector / Builder|NOT_APPLICABLE|Excluded from proposed restricted B scope; if implementation required, distinct authority needed|

B may potentially ask logical endpoint/auth/schema/field/document/version questions only after exact safe authorization. This mission answers none. Field existence differs from parseability, actual timestamp, timestamp distribution, relative source latency, relative market latency and market-response comparison. No safe label permits actual efficacy-bearing timing/count/availability/delivery evidence.

## 11. Resource/time decision fields and dependency timing

|Field|Current documentary value|Why later choice matters|
|---|---|---|
|MAX_CALENDAR_DURATION|OWNER_DECISION_REQUIRED|Bounds any future phase and prevents open-ended extension|
|MAX_COMPUTE|OWNER_DECISION_REQUIRED|Prevents unapproved processing/testing commitment|
|MAX_STORAGE|OWNER_DECISION_REQUIRED|Bounds artifacts, intermediates and quarantine footprint|
|MAX_EXTERNAL_CALLS_IF_ANY|A1 calls to operational endpoints prohibited; future B quota OWNER_DECISION_REQUIRED|No polling or probing inferred from technical scope|
|MAX_HUMAN_ACCESS|OWNER_DECISION_REQUIRED|Actual readers and privilege exposure limits|
|MAX_AGENT_ACCESS|OWNER_DECISION_REQUIRED|Agent/session knowledge and cumulative disclosure|
|ALLOWED_CREDENTIAL_SCOPE|A1 operational credentials prohibited; future B scope OWNER_DECISION_REQUIRED|No credential acquisition/use from generic role names|
|MAX_OUTPUT_VOLUME|OWNER_DECISION_REQUIRED|Bounds releases; volume cap alone cannot prove safety|
|MAX_LOG_RETENTION|OWNER_DECISION_REQUIRED|Accountability and secure retention without invented duration|
|MONETARY_BUDGET|OWNER_DECISION_REQUIRED|No spending commitment inferred|
|STOP_ON_RESOURCE_LIMIT|Required boundary rule; applicable limit remains unresolved|No automatic quota increase or retry past the cap|

No duration, money, compute/storage amount, call quota, human/agent limit or retention duration is invented. Producing this authorized documentary deliverable does not allocate operational resources.

Before later A2/B authorization: exact scope/manifests/provenance classes, actual roles/permissions, bounds, incident/stop obligations and required capability/approval evidence must be explicitly addressed. Before execution: all applicable approved identity/version/control prerequisites must be attested and the exact owner execution decision must exist. Neither documentary proposal nor evidence of a prerequisite automatically grants execution.

Can remain unresolved in A1: actual harness approval, generator path, fixture instances, actors/operational control implementation, credentials, endpoints and numerical limits. Their absence is reported, never filled by assumption. Only the already-declared unresolved portions of economic selection/error/block/power/Book/risk/capacity definitions remain for the corresponding later contract; technical documentation neither resolves nor waives them. Ratified economic preferences, primary horizon, persistent Book and structural choices remain unchanged; no ratified choice is reopened.

DECLARED_UNRESOLVED_FIELD_COUNT = 41  
EXHAUSTIVENESS_CERTIFIED = FALSE

No canonical register modification. Stage-1 input/output/metric specifications refine EXACT_NON_ECONOMIC_FEASIBILITY_SCOPE and RELEASE_PERMISSIONS. Further harness/control/role/resource requirements here are OPTION_SPECIFIC_PHASE_DEPENDENCY; not an automatic 42nd field.

## 12. Completion boundary and handoff

A1_DOCUMENTATION = READY_FOR_OWNER_REVIEW means the authorized documentary package is complete for review, including honest NOT_ATTESTED/UNRESOLVED findings. It does not claim A2 readiness, actual harness/control existence or admissibility of any fixture.

A2_EXISTING_APPROVED_HARNESS = NOT_ATTESTED  
A2_PREREQUISITES_COMPLETE = FALSE  
A2_BLOCKER = HARNESS_NOT_ATTESTED_AND_REQUIRED_PREREQUISITES_UNRESOLVED

OPTION_B_EXECUTED = NO  
REAL_DATA_ACCESSED = NONE  
REAL_METADATA_ACCESSED = NONE  
FIXTURES_CREATED = NONE  
HARNESS_EXECUTED = NO  
REPOSITORY_CODE_EXECUTED = NO  
EXTERNAL_ENDPOINTS_QUERIED = NONE  
CREDENTIALS_USED = NONE  
BUILDER_USED = NO  
DATA_T0 = NOT_DECLARED  
EXPERIMENT_T0 = NOT_DECLARED  
t0 = NOT_DECLARED  
ECONOMIC_AUTHORITY = 0  
ECONOMIC_DECISION_WEIGHT = 0  
COMPOSITE_ECONOMIC_AUTHORITY = 0  
CAPTURE_AUTHORIZATION = NONE  
REAL_CAPITAL_AUTHORIZED = FALSE  
LIVE_TRADING_AUTHORIZED = FALSE  
UNBLIND_AUTHORIZED = FALSE  
OPERATIONAL_SOURCE_SELECTED = NONE  
FULL_VALIDATION_CONTRACT_COMPLETE = FALSE  
READY_FOR_FINAL_VALIDATION_CONTRACT_AUDIT = FALSE  
OBSERVATION_AUTHORITY = UNCHANGED

“External endpoints/metadata/credentials NONE” refers to operational/weather/market/technical feasibility; authorized governance connector reads and document publication are recorded in §7 and are not Option B execution. No fixtures, tests, shell/repository programs, technical controls, runtime or operational sources were used to verify these documents.

ASTRA_PASS != PHASE_AUTHORIZATION  
BLUE_DOCUMENTATION != A2_AUTHORIZATION

ECONOMIC_PROGRESS = exact governance-only manifests, access/fixture/incident policy and prerequisite gaps made reviewable without operational exposure.
REMAINING_BLOCKER = absent exact approved harness attestation and incomplete later A2/B prerequisites/authority.
EXIT_CONDITION = owner review of this A1 package; no further execution until separate exact authority.
FILES_MODIFIED_OUTSIDE_SCOPE = NONE.
NEXT_SAFE_ACTION = OWNER REVIEW ONLY; owner may provide exact already-existing approval evidence or decide a separate bounded authority. Do not execute A2/B or assign Builder.


## 13. A2 documentary governance integration configuration — 2026-10-05

### 13.1 Candidate status, authority and chronology

CONFIGURATION_ID = BLUE_A2_DOCUMENTARY_INTEGRATION_CANDIDATE_V1  
A2_INTEGRATION_MODE = DOCUMENTATION_ONLY_NO_FIXTURE  
DOCUMENTARY_REVIEW_ONLY = TRUE  
PROPOSED_CONFIGURATION_OWNER_RATIFIED = FALSE  
A2_OPERATION = DOCUMENTARY_INPUT_READ_THEN_STRUCTURAL_REPORT_RELEASE_CANDIDATE  
DIGEST_STATUS = PENDING_AUTHORIZED_COMPUTATION  
DRAFT_COMPLETE != EXECUTION_READY  
DRAFT_COMPLETE != OWNER_RATIFIED  
ASTRA_PASS != PHASE_AUTHORIZATION

This is one proposed configuration, appended to the existing A1 dossier. Sections 1–12 are preserved verbatim as the historical A1 record. Their then-current harness NOT_ATTESTED findings are not retroactively completed. This section uses later exact evidence and documents outstanding decisions; it does not amend an Owner Decision, implement a control, generate an object or approve execution. No new document, companion, configuration file, fixture, test object or runtime artifact is created.

|Reference|Exact verified identity|Meaning for this draft|
|---|---|---|
|Owner A1 authority|728cf23e7d69a373306f3c1a3fb5d11240210cda; OWNER_V4_PHASE_GATE_A1_DECISION_2026-10-04.md; blob 483907e4f719ec8bcb3851af0f184690cea96279|§§3–4 authorize manifest, schema/interface, role/access, logging, provenance, STOP/incident and prerequisite documentation; proposals do not activate A2. Artifact remains byte-identical at review snapshot|
|Review snapshot / Astra PASS|31215914a7e11daa20ca0189d859bb69827a055c; audit/ASTRA_V4_A2_D5_TYPE_REPAIR_RUNTIME_EVIDENCE_AUDIT_2026-10-05.md; blob 0deae36fba1962fe9249cffbe787f0680b5abfd8|PASS_D5_TYPE_REPAIR_AND_BOUNDED_RUNTIME_EVIDENCE; sole parent is harness reference. Not execution authority, deployed-control certification or fixture approval|
|Harness reference|78d537de681363ed83a6c7787aba4319f3c73c4d|Exact source reference for all schema/interface descriptions below, not an A2 execution permit|
|Original construction authority|37e3b25f17a7c5d3b3bc8d37df730aa988585b6c; owner/OWNER_V4_A2_DEDICATED_HARNESS_BUILDER_DECISION_2026-10-04.md; blob 81d2ad4dac7ed50173442448437c9a23cc1ef51e|Historical dedicated-harness construction authority; verified exact commit/artifact. Distinct from A1 and future execution-policy authority|

Paths in the table are relative to research/weather_forward/v4/ except the exact A1 authority SHA. A1 is an ancestor of the review snapshot (27 commits ahead, zero behind; merge base equals A1). The snapshot directly follows the exact harness reference. A1 authorizes this drafting activity because it is only documentation/specification and consistency inspection of already-authorized governance and interfaces. Its STOP rule is preserved: no harness-resolution search, runtime verification or new construction is performed to fill remaining unknowns. The later Astra evidence resolves the identity of the reviewed dedicated implementation and its bounded test evidence only; suitability/approval for this new integration operation remains an Owner decision.

Authority chain for this section: A1 permission → later exact source and bounded Astra review as evidence → this documentary candidate → Owner review/ratification → any separately authorized technical transition/execution. Neither review evidence nor this candidate is a phase authorization.

### 13.2 Exact schemas and classification discipline

|Source at harness reference SHA|Verified Git blob|Schemas / interfaces read as text only|
|---|---|---|
|a2_harness/contract.py|f6f94a4a472e3f6652a1502f6afb5825721364d0|InputManifest; OutputManifest; AuthorityBinding; RoleDeclaration; ActionAuthorization; TrustedExecutionPolicyRoot; LogRecord; LogAppendAcknowledgement; StructuredAuditLog; DisclosureRecord; CumulativeDisclosureLedger; HarnessDecision; LoggedActionResult; fixture provenance interfaces and enums|
|a2_harness/harness.py|00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4|HarnessPolicy; identity/canonicalization functions; authority/manifest/role checks; A2Harness.evaluate_input_read and evaluate_output_release; acknowledged finalization and resource-state interface|
|a2_harness/trusted_root.py|9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94|Current production constants and resolver are None|
|a2_harness/README.md|b3b74326d2d41f1d88c9e891186a5af9a663f095|Construction versus execution authority; current no-root and no approved recipient state; limits of in-memory logging|

Each requirement row below has exactly one classification:
- SUPPORTED_SCHEMA_FIELD: a real field or existing typed interface value, not a guarantee that its semantic content is enforced.
- DOCUMENTARY_CONSTRAINT: an obligation for the frozen scope, review or procedure outside runtime fields.
- UNSUPPORTED_BY_CURRENT_SCHEMA: a missing representation or enforcement capability; no enforcement claim.
- FUTURE_IMPLEMENTATION_REQUIREMENT: a specifically identified technical change needed for permissive future operation, requiring separate authority.

Related representations and missing enforcement are separate requirements, not double-classification of one row. Enum names here denote documentary candidate values only. No Python constructor, JSON configuration object, manifest instance, policy instance, log record or test object has been created.

### 13.3 One bounded candidate operation

PURPOSE = determine, only in a separately authorized later operation, whether exact documentary manifest/policy/actor bindings can reach the existing guarded decision-and-log interfaces and whether their returned structural linkage matches the frozen configuration. This is an interface/governance integration objective derived from A1 manifest, role, logging and consistency objectives; no new research objective.

Candidate sequence, not executed:
1. An appointed EXECUTOR/input reader calls evaluate_input_read once with the single input manifest in §13.4, its exact AuthorityBinding/HarnessPolicy, matching READ_INPUT authorization, a StructuredAuditLog and a unique read log_record_id.
2. Only if the read result satisfies the approved structural expectations, the independent RELEASE_APPROVER calls evaluate_output_release once with the single output manifest in §13.5, exact recipient declaration, RELEASE_OUTPUT authorization, returned log, unique release log_record_id and an independently assessed disclosure ledger.
3. A documentary verifier checks the returned decisions, exact actor/role/action/authority/manifest/recipient linkage, append acknowledgement and unique matching stored records. No underlying document/payload processing or export is performed by the harness APIs themselves.

|Operation requirement|Classification|Candidate meaning / limit|
|---|---|---|
|Input class|SUPPORTED_SCHEMA_FIELD|InputClassification.DOCUMENTATION_ONLY|
|Output class|SUPPORTED_SCHEMA_FIELD|OutputManifest.output_type = DOCUMENTATION_ONLY_STRUCTURAL_REPORT (a proposed string label, not a new enum)|
|Calls and verification sequence|DOCUMENTARY_CONSTRAINT|One bounded read then one bounded release evaluation; no retries, additional targets, sweeps or extensions without exact approval. Sequence is not enforced by HarnessPolicy|
|Allowed input-reader role|SUPPORTED_SCHEMA_FIELD|Role.EXECUTOR only; exact actor appointment and matching ActionAuthorization still required|
|Recipient role|SUPPORTED_SCHEMA_FIELD|Role.RESEARCH_VIEWER; exact recipient actor mapping in policy required|
|Independent approver|SUPPORTED_SCHEMA_FIELD|Role.RELEASE_APPROVER, actor_id different from recipient.actor_id, exact RELEASE_OUTPUT authorization under future execution-policy authority|
|Structural evidence|DOCUMENTARY_CONSTRAINT|Only returned decision states/reason codes, exact safe governance/manifests/policy references, actor bindings and acknowledged-log linkage; no efficacy or data claim|
|Duration concept|DOCUMENTARY_CONSTRAINT|Single bounded operation under an Owner-ratified maximum calendar duration; no automatic continuation. Numerical value OWNER_DECISION_REQUIRED|
|Resource-boundary concept|DOCUMENTARY_CONSTRAINT|Owner-ratified compute/storage/access/output/log bounds; external accountable check must establish authority before operation|
|Resource-state interface|SUPPORTED_SCHEMA_FIELD|ResourceBoundaryState and validate_resource_boundary; UNRESOLVED/EXCEEDED fail closed. No actual state supplied or evaluated now|
|Numerical enforcement and automatic gating of read/release by resource check|UNSUPPORTED_BY_CURRENT_SCHEMA|No numerical resource fields, counters or automatic resource precondition in these two APIs|
|STOP/incident workflow|DOCUMENTARY_CONSTRAINT|§13.10; current drafting stops if prohibited access/implementation is needed|
|Exclusions|DOCUMENTARY_CONSTRAINT|No fixture admission/generation/testing, payload, real source/metadata, endpoints, operational credentials, measurements, rankings, capture, trading or economic evidence|


|Expected future successful structural check|Classification|Required conjunction, not a current result|
|---|---|---|
|Input-read returned decision|SUPPORTED_SCHEMA_FIELD|validation_state VALID; permit_or_deny_state PERMIT; quarantine_state CLEAR; release_state BLOCKED (read does not authorize release); completion_state COMPLETED; stop_reason None|
|Output-release returned decision|SUPPORTED_SCHEMA_FIELD|validation_state VALID; permit_or_deny_state PERMIT; quarantine_state CLEAR; release_state AUTHORIZED; completion_state COMPLETED; stop_reason None|
|Returned acknowledged linkage|SUPPORTED_SCHEMA_FIELD|log_acknowledged exactly True; log_record present; exactly one identical stored record with approved unique ID; decision permit/quarantine/release equal the logged values; exact expected authority/actor/role/authorization/action/target/manifest/incident/cumulative/recipient context|
|Read log context|SUPPORTED_SCHEMA_FIELD|Action.READ_INPUT; TargetKind.INPUT_MANIFEST; target_id A2-DOC-IN-OWNER-A1-V1; exact computed input identity; input-reader actor/role and READ_INPUT authorization; recipient fields and cumulative_disclosure_state None|
|Release log context|SUPPORTED_SCHEMA_FIELD|Action.RELEASE_OUTPUT; TargetKind.OUTPUT_MANIFEST; target_id A2-DOC-OUT-STRUCTURAL-REPORT-V1; exact computed output identity; independent approver actor/role and RELEASE_OUTPUT authorization; exact recipient actor/role; cumulative_disclosure_state CLEAR only after supported assessment|
|Verification result and halt rule|DOCUMENTARY_CONSTRAINT|Any DENY, BLOCKED, invalid/unresolved state, missing/mismatched acknowledgement or linkage prevents successful integration and halts the sequence. No operational/economic inference, permissive direct construction or private allocation to bypass a failed gate|

If later permitted calls occurred without an independently anchored production root, the source specifies DENY/BLOCKED, not successful authority. No call is performed here and no runtime result is asserted. The objective is not to obtain PERMIT by weakening gates. Any unexpected, mismatched or incomplete result stops the sequence.

### 13.4 Single candidate InputManifest — documentary table only

Proposed input label: A2-DOC-IN-OWNER-A1-V1. It represents only the structural authority reference to the exact Owner A1 document. It does not represent a document payload, real source or a test fixture. The proposed permitted field names are documentary design labels, not instantiated input contents.

All 17 actual InputManifest fields are specified below. These values are proposals except already binding prohibitions and exact historical references; open values remain explicit.

|Actual field|Candidate value|Classification|
|---|---|---|
|input_id|A2-DOC-IN-OWNER-A1-V1|SUPPORTED_SCHEMA_FIELD|
|manifest_version_identity|A2-DOC-INTEGRATION-MANIFEST-V1; proposed shared input/output/binding version token|SUPPORTED_SCHEMA_FIELD|
|input_classification|InputClassification.DOCUMENTATION_ONLY|SUPPORTED_SCHEMA_FIELD|
|source_provenance_class|OWNER_GOVERNANCE_DECISION; commit=728cf23e7d69a373306f3c1a3fb5d11240210cda; path=research/weather_forward/v4/owner/OWNER_V4_PHASE_GATE_A1_DECISION_2026-10-04.md; blob=483907e4f719ec8bcb3851af0f184690cea96279|SUPPORTED_SCHEMA_FIELD|
|exact_permitted_fields|Ordered candidate tuple: document_commit_sha; document_path; document_blob_sha; authorized_documentary_scope_reference|SUPPORTED_SCHEMA_FIELD|
|exact_prohibited_fields|Ordered candidate tuple: document_body; fixture_payload; real_observation; real_technical_metadata; operational_endpoint; operational_credential; actual_timestamp; cadence; latency; availability; delivery_pattern; efficacy; economic_outcome; performance_distribution; pnl; ranking; source_preference; station_preference; city_preference; model_preference|SUPPORTED_SCHEMA_FIELD|
|permitted_reader_roles|Single-element tuple: Role.EXECUTOR|SUPPORTED_SCHEMA_FIELD|
|raw_values_visible|VisibilityState.VISIBLE, scoped exclusively to permitted documentary reference fields|SUPPORTED_SCHEMA_FIELD|
|timestamps_visible|VisibilityState.HIDDEN|SUPPORTED_SCHEMA_FIELD|
|frequency_or_count_information_visible|VisibilityState.HIDDEN|SUPPORTED_SCHEMA_FIELD|
|longitudinal_observation_allowed|PermissionState.DENIED|SUPPORTED_SCHEMA_FIELD|
|aggregation_allowed|PermissionState.DENIED|SUPPORTED_SCHEMA_FIELD|
|cross_source_comparison_allowed|PermissionState.DENIED|SUPPORTED_SCHEMA_FIELD|
|efficacy_leakage_assessment|LeakageAssessment.UNRESOLVED; prospective documented clearance required before any valid execution configuration|SUPPORTED_SCHEMA_FIELD|
|access_logging_requirement|RequirementState.REQUIRED|SUPPORTED_SCHEMA_FIELD|
|quarantine_on_ambiguity|RequirementState.REQUIRED|SUPPORTED_SCHEMA_FIELD|
|owner_approval_required|RequirementState.REQUIRED; declaration is not approval evidence|SUPPORTED_SCHEMA_FIELD|

The provenance string includes exact repository authority references so those textual references would enter canonical identity. It is still only a caller-supplied string: the harness does not retrieve or authenticate source bytes, prove provenance or verify an Owner signature. This draft's repository verification supplies documentary evidence for the stated historical reference, not deployed verification.

|Additional input requirement|Classification|Exact handling|
|---|---|---|
|Canonical structural identity|SUPPORTED_SCHEMA_FIELD|Derived by input_manifest_identity; held in HarnessPolicy.expected_input_manifest_identity, not a nonexistent InputManifest.digest field; pending computation|
|Documentary source/lineage|DOCUMENTARY_CONSTRAINT|Only pinned A1 authority reference above; changes require a revised candidate/version, approval and recomputation; no linked document traversal or payload opening|
|Allowed transformation|DOCUMENTARY_CONSTRAINT|Identity-preserving transcription of those four reference fields into structural verification; no semantic research derivation|
|Forbidden aggregation/longitudinal processing|DOCUMENTARY_CONSTRAINT|No joined histories, repeated observational summaries or cross-source inference; finite control checks are not operational aggregation|
|Enforcement of allowlist, visibility, source bytes and transformation restrictions|UNSUPPORTED_BY_CURRENT_SCHEMA|Manifest digest binds declarations; APIs do not inspect an input payload, redact it, enforce actual visibility or validate documentary lineage|
|Standalone input payload/hash/lineage or transformation fields|UNSUPPORTED_BY_CURRENT_SCHEMA|No such InputManifest fields. Pinned textual provenance is not a new field or payload binding|

No future clearance is assumed: current candidate UNRESOLVED assessment prevents a valid read. Owner may ratify canonical declarations, but factual clearance requires explicit supported review evidence; ratification alone cannot manufacture a factual leakage finding.

### 13.5 Single candidate OutputManifest — documentary table only

Proposed output label: A2-DOC-OUT-STRUCTURAL-REPORT-V1. One logical structural report would have a frozen textual allowlist carried by exact_metric_or_artifact. No actual report payload, result object or output sample is created.

|Actual field|Candidate value|Classification|
|---|---|---|
|output_id|A2-DOC-OUT-STRUCTURAL-REPORT-V1|SUPPORTED_SCHEMA_FIELD|
|manifest_version_identity|A2-DOC-INTEGRATION-MANIFEST-V1|SUPPORTED_SCHEMA_FIELD|
|output_type|DOCUMENTATION_ONLY_STRUCTURAL_REPORT|SUPPORTED_SCHEMA_FIELD|
|exact_metric_or_artifact|STRUCTURAL_REPORT_ONLY: validation_state; permit_or_deny_state; quarantine_state; release_state; completion_state; stop_reason; detail_code; input_manifest_reference; output_manifest_reference; policy_reference; construction_authority_reference; execution_authority_reference; actor_role_bindings; acknowledged_log_record_references; structural_linkage_status|SUPPORTED_SCHEMA_FIELD|
|granularity|ONE_DOCUMENTARY_OPERATION; exact structural identifiers, enum states and fixed reason codes only; no observations, measurements, payload text, operational timing or event counts|SUPPORTED_SCHEMA_FIELD|
|permitted_recipients|Single-element tuple: Role.RESEARCH_VIEWER|SUPPORTED_SCHEMA_FIELD|
|exportability|PermissionState.UNRESOLVED; future ALLOWED needs exact recipient, destination and release permissions ratified; current release blocked|SUPPORTED_SCHEMA_FIELD|
|quarantine_status|QuarantineState.BLOCKED_PENDING_OWNER_REVIEW; no current CLEAR assertion|SUPPORTED_SCHEMA_FIELD|
|cumulative_disclosure_risk|CumulativeDisclosureState.UNRESOLVED; exact recipient/output/history assessment required|SUPPORTED_SCHEMA_FIELD|
|efficacy_leakage_assessment|LeakageAssessment.UNRESOLVED; prospective report-scope clearance required|SUPPORTED_SCHEMA_FIELD|
|release_approval_requirement|RequirementState.REQUIRED|SUPPORTED_SCHEMA_FIELD|
|retention_rule|OWNER_DECISION_REQUIRED: exact report/journal retention and custodian procedure must be ratified before execution; no numerical default|SUPPORTED_SCHEMA_FIELD|
|incident_if_unexpected_information_revealed|STOP; block release; quarantine through separately approved mechanism; record bounded incident/exposure; escalate to appointed incident authority and Owner; no resume without exact direction|SUPPORTED_SCHEMA_FIELD|

|Additional output requirement|Classification|Exact handling|
|---|---|---|
|Canonical output structural identity|SUPPORTED_SCHEMA_FIELD|output_manifest_identity → HarnessPolicy.expected_output_manifest_identity; pending, no invented OutputManifest.digest|
|Report content restrictions|DOCUMENTARY_CONSTRAINT|Allowlisted structural information only; no economic outcomes/performance/PnL/rankings/preferences, real observations, operational availability/cadence/latency, payload-derived findings or combined efficacy disclosure|
|Report field schema/content sanitizer|UNSUPPORTED_BY_CURRENT_SCHEMA|No output_fields dataclass field, structured report validator, payload serializer or output sanitization. exact_metric_or_artifact is a digest-bound string, not an enforced report parser|
|Safe reason/detail disclosure|DOCUMENTARY_CONSTRAINT|Only reviewed fixed structural codes; unsafe error/debug text quarantined, never included merely because detail_code is a string|
|Exact destination/export transport and recipients' downstream use|UNSUPPORTED_BY_CURRENT_SCHEMA|No destination field, transport, actual export or downstream access control. exportability gates a decision only|
|Retention execution / deletion policy|UNSUPPORTED_BY_CURRENT_SCHEMA|retention_rule is text; no storage lifecycle or deletion enforcement|
|Quarantine containment / external incident workflow|UNSUPPORTED_BY_CURRENT_SCHEMA|State declarations and decision denial do not create isolation, freeze storage or appoint an incident investigator|
|Policy identity and read/release report correlation|DOCUMENTARY_CONSTRAINT|Safe report references must identify the exact policy and both acknowledged records; the harness does not automatically assemble this report|
|Log policy digest / cross-action chain field|UNSUPPORTED_BY_CURRENT_SCHEMA|LogRecord has manifest_identity but no policy_identity or preceding_read_record_id field. Both API calls can be independent; exact policy linkage follows root comparison and documentary evidence, not a new log field|

The existing A1 deliverable publication is already permitted by A1; it is not the candidate future harness release. No output recipient/destination for that future operation is silently granted by this publication.

### 13.6 Single candidate HarnessPolicy, AuthorityBinding and declarations

Proposed documentary policy label: A2-DOC-GOVERNANCE-POLICY-V1. HarnessPolicy has no policy_id, policy_version, allowed_actions, denied_actions, actor-declarations, logging-rule, STOP-rule or resource-limit fields. Those labels/rules below are external documentary constraints, not additions to its dataclass.

|Actual HarnessPolicy field|Candidate value / open binding|Classification|
|---|---|---|
|expected_owner_authority_sha|37e3b25f17a7c5d3b3bc8d37df730aa988585b6c — original construction authority, not A1 or future execution permission|SUPPORTED_SCHEMA_FIELD|
|expected_harness_identity|research/weather_forward/v4/a2_harness — proposed component-path identity token; requires ratification, not claimed to be an existing approved policy token|SUPPORTED_SCHEMA_FIELD|
|expected_harness_version_or_commit_identity|78d537de681363ed83a6c7787aba4319f3c73c4d — reviewed implementation reference; future transition/deployment change must be explicitly reconciled, not silently called the same artifact|SUPPORTED_SCHEMA_FIELD|
|expected_manifest_version_identity|A2-DOC-INTEGRATION-MANIFEST-V1|SUPPORTED_SCHEMA_FIELD|
|expected_input_manifest_id|A2-DOC-IN-OWNER-A1-V1|SUPPORTED_SCHEMA_FIELD|
|expected_input_manifest_identity|PENDING_AUTHORIZED_COMPUTATION; derived, not an Owner-selected hash or valid runtime placeholder|SUPPORTED_SCHEMA_FIELD|
|expected_output_manifest_id|A2-DOC-OUT-STRUCTURAL-REPORT-V1|SUPPORTED_SCHEMA_FIELD|
|expected_output_manifest_identity|PENDING_AUTHORIZED_COMPUTATION; derived, not an Owner-selected hash or valid runtime placeholder|SUPPORTED_SCHEMA_FIELD|
|allowed_input_classifications|Single-element tuple: InputClassification.DOCUMENTATION_ONLY|SUPPORTED_SCHEMA_FIELD|
|prohibited_input_classifications|Tuple: InputClassification.NON_ECONOMIC_SYNTHETIC; InputClassification.REAL_TECHNICAL_METADATA; InputClassification.PROHIBITED; InputClassification.UNKNOWN|SUPPORTED_SCHEMA_FIELD|
|fixture_provenance_contract|None; no fixture admission contract for this mode|SUPPORTED_SCHEMA_FIELD|
|permitted_recipient_actor_roles|Exactly one future pair: (recipient actor identity OWNER_DECISION_REQUIRED, Role.RESEARCH_VIEWER); unresolved placeholder is not an approved actor and cannot be used at runtime|SUPPORTED_SCHEMA_FIELD|

None in fixture_provenance_contract is supported without inventing a generator. The fixture-admission method denies absent contract; the input classification policy alone does not serve as a global method-action firewall.

|Additional binding / policy requirement|Classification|Exact meaning|
|---|---|---|
|Policy label/version|DOCUMENTARY_CONSTRAINT|A2-DOC-GOVERNANCE-POLICY-V1, this §13 at its publication commit. Any canonical content change requires revision, digest recomputation and exact root reapproval|
|Allowed actions|DOCUMENTARY_CONSTRAINT|Only the two named future evaluation calls, their internal logging and bounded structural verification; not currently authorized|
|Denied actions|DOCUMENTARY_CONSTRAINT|Fixture admission/generation/testing; data/metadata access; endpoints/credentials; capture; research/economics/trading; repetition or extra targets; all other actions outside exact future grant|
|Global action allow/deny enforcement|UNSUPPORTED_BY_CURRENT_SCHEMA|No global action allowlist in policy; existing method-specific ActionAuthorization checks are not a general executor capability firewall|
|AuthorityBinding.owner_authority_sha|SUPPORTED_SCHEMA_FIELD|37e3b25f17a7c5d3b3bc8d37df730aa988585b6c, matching policy and future root.expected_construction_authority_sha|
|AuthorityBinding.harness_identity|SUPPORTED_SCHEMA_FIELD|Proposed component-path token identical to policy|
|AuthorityBinding.harness_version_or_commit_identity|SUPPORTED_SCHEMA_FIELD|Reviewed reference SHA identical to policy, subject to separately ratified transition identity|
|AuthorityBinding.manifest_version_identity|SUPPORTED_SCHEMA_FIELD|A2-DOC-INTEGRATION-MANIFEST-V1|
|RoleDeclaration fields|SUPPORTED_SCHEMA_FIELD|actor_id = exact appointed identity (currently OWNER_DECISION_REQUIRED); declared_role = EXECUTOR, RELEASE_APPROVER or RESEARCH_VIEWER as applicable|
|READ_INPUT ActionAuthorization|SUPPORTED_SCHEMA_FIELD|authorization_id OWNER_DECISION_REQUIRED; authority_sha future exact execution-policy Owner artifact SHA unresolved; actor_id input-reader identity; declared_role EXECUTOR; action READ_INPUT; state UNRESOLVED until separate explicit grant|
|RELEASE_OUTPUT ActionAuthorization|SUPPORTED_SCHEMA_FIELD|authorization_id OWNER_DECISION_REQUIRED; same future execution-policy authority; actor_id independent approver; declared_role RELEASE_APPROVER; action RELEASE_OUTPUT; state UNRESOLVED until separate explicit grant|
|Declaration is not authorization|DOCUMENTARY_CONSTRAINT|Role identity alone never grants action permission; future AUTHORIZED state must have exact authority evidence|
|Cumulative disclosure evidence|SUPPORTED_SCHEMA_FIELD|DisclosureRecord and CumulativeDisclosureLedger; exact output_id + recipient_actor_id + recipient_role. Current history/assessment unresolved, not populated|
|Disclosure assessment integrity|UNSUPPORTED_BY_CURRENT_SCHEMA|Ledger evaluates supplied labels; no external exposure-history completeness or safety proof. Empty ledger is UNRESOLVED; global BLOCKED precedes any exact-recipient CLEAR|
|Exact logging linkage|SUPPORTED_SCHEMA_FIELD|LogRecord, LogAppendAcknowledgement and LoggedActionResult bind exact record/context and acknowledgement; unique read/release record identities must be approved/fixed before execution, not populated now|
|External immutable journal, access logs and durable custody|UNSUPPORTED_BY_CURRENT_SCHEMA|StructuredAuditLog is an immutable-value in-memory tuple interface; no cryptographic storage, durable service, ACL, dashboard/admin auditing or retention engine|

Record-ID uniqueness is per supplied log. The future operation must pass the read result's returned log into release, then verify both records and exact context. This is a documentary obligation, not enforcement of a persistent journal or an automatic cross-call prerequisite.

### 13.7 Canonical content and digest semantics

No digest has been computed, selected, fabricated or manually assigned. The draft tables are not canonical runtime instances. Pending placeholders and unresolved actor/content choices must not be imported or submitted as working values.

|Binding|Selected content / rule|Expected digest and status|Classification|
|---|---|---|---|
|Input identity|All 17 actual InputManifest fields in §13.4, plus manifest_kind = InputManifest added by input_manifest_identity|Derived sha256 identity; PENDING_AUTHORIZED_COMPUTATION|SUPPORTED_SCHEMA_FIELD|
|Output identity|All 13 actual OutputManifest fields in §13.5, plus manifest_kind = OutputManifest|Derived sha256 identity; PENDING_AUTHORIZED_COMPUTATION|SUPPORTED_SCHEMA_FIELD|
|Policy identity|All 12 actual HarnessPolicy fields, plus contract_kind = HarnessPolicy; includes derived input/output identities, construction authority, harness/version, class sets, None fixture contract and exact recipient map|Derived sha256 identity; PENDING_AUTHORIZED_COMPUTATION; future root.expected_policy_identity|SUPPORTED_SCHEMA_FIELD|
|Canonicalization procedure|Existing _canonical_digest: json.dumps with ensure_ascii=True, separators=(",", ":"), sort_keys=True; UTF-8 bytes; SHA-256 with sha256: prefix|No alternative hash procedure or manual value|DOCUMENTARY_CONSTRAINT|
|Tuple canonicalization|Input allowed/prohibited fields and reader enum values sorted; output recipient enum values sorted; policy class enum values sorted and recipient actor/role pairs sorted by actor ID then role; duplicates retained, not deduplicated; other strings exactly preserved|Must follow existing identity functions|DOCUMENTARY_CONSTRAINT|
|Order of authorized computation|Freeze exact content/actors/values; compute input and output identities; substitute these derived values into policy; compute policy identity; independent byte/rule verification before any root change or execution|Not performed under A1|DOCUMENTARY_CONSTRAINT|
|External content/destination/lineage binding|Only text explicitly included in the actual fields enters these identities. Unrepresented content, report bytes, destination and external journal require separate documentary integrity binding|No automatic content/security binding|UNSUPPORTED_BY_CURRENT_SCHEMA|

Owner chooses and ratifies canonical content, fields, exact actor-role bindings and permissions. Owner does not choose hash output. A pending digest prevents a valid policy; it does not prevent documentary DRAFT_COMPLETE. Any replacement of an UNRESOLVED enum with CLEAR/ALLOWED/AUTHORIZED, change of recipient, retention text or harness version changes canonical content and requires recomputation and root reapproval before use.

### 13.8 Actor assignments and minimum independence

These are proposed functions, not invented people or assigned runtime identities.

|Function / proposed role|Actor identity|Action|Combination permitted?|Owner decision / classification|
|---|---|---|---|---|
|Execution actor / Role.EXECUTOR|OWNER_DECISION_REQUIRED|Bounded orchestration only; no orchestration Action enum invented|May be the same actor as input reader; no contrary requirement for this documentary-only operation. Not a grant of broader access|DOCUMENTARY_CONSTRAINT|
|Input reader / Role.EXECUTOR|OWNER_DECISION_REQUIRED|Action.READ_INPUT with exact declaration/authorization|Proposed same actor as execution actor; must be explicitly appointed|SUPPORTED_SCHEMA_FIELD|
|Report approver / Role.RELEASE_APPROVER|OWNER_DECISION_REQUIRED|Action.RELEASE_OUTPUT with exact authority/action/role/state|Must differ from output recipient; may also be execution/input-reader actor only if Owner ratifies the combination and evidence shows no other contract conflict; not assumed|SUPPORTED_SCHEMA_FIELD|
|Output recipient / Role.RESEARCH_VIEWER|OWNER_DECISION_REQUIRED|Receive only independently approved structural report|Must differ from release approver. May also be executor/input reader if exact role mapping and contract permitted combination are ratified; not assumed|SUPPORTED_SCHEMA_FIELD|
|Owner authority / PHASE_OWNER function|PROJECT_OWNER function already documented; exact runtime actor identity unresolved|Ratify configuration; issue any separate execution/transition authority|Owner may occupy another role only by explicit appointment without violating approver/recipient independence|DOCUMENTARY_CONSTRAINT|
|Incident/quarantine/journal authority functions|OWNER_DECISION_REQUIRED|STOP, contain via authorized mechanism, preserve safe evidence, decide escalation/resume|No blanket separation rule invented; access, authority and conflict review must be explicit|DOCUMENTARY_CONSTRAINT|

RELEASE_APPROVER != OUTPUT_RECIPIENT is mandatory when approval REQUIRED. Same actor in other functions is not forbidden by default. Schema acceptance of multiple declarations is not proof of contractual permission; role combinations remain Owner decisions. Current Blue drafting identity does not appoint Blue as future execution actor, approver or recipient. No real identity, credential or authorization ID is invented.

### 13.9 Current root and narrowly described future transition

PRODUCTION_TRUSTED_ROOT = ABSENT_OR_NOT_AVAILABLE_FOR_A2  
TRUSTED_ROOT_TRANSITION_REQUIRED = TRUE  
FUTURE_ACTION_REQUIRES_SEPARATE_AUTHORIZATION = TRUE  
TEST_ONLY_TRUSTED_ROOT != EXECUTION_POLICY_AUTHORITY

At the exact reference, both production root constants are None and the resolver returns None. The current deny-all state is not completed A2 execution authority. Historical synthetic root injection exercised controls under the bounded test authority only; it cannot supply this operation's root.

|Future requirement|Classification|Scope, authority and evidence|
|---|---|---|
|TrustedExecutionPolicyRoot.execution_policy_authority_sha|SUPPORTED_SCHEMA_FIELD|A new exact Owner artifact authorizing the narrowly frozen documentary integration operation and applicable permissions; currently OWNER_DECISION_REQUIRED. Not A1, construction authority or Astra PASS|
|expected_construction_authority_sha|SUPPORTED_SCHEMA_FIELD|Candidate historical construction authority 37e3b25f17a7c5d3b3bc8d37df730aa988585b6c|
|expected_harness_identity and expected_harness_version_or_commit_identity|SUPPORTED_SCHEMA_FIELD|Exact approved component/version identity matched to policy and AuthorityBinding; reviewed reference is 78d537de…; any future source change must have explicit provenance/version reconciliation|
|expected_policy_identity|SUPPORTED_SCHEMA_FIELD|Derived exact policy digest after freeze and authorized computation; pending|
|Install an independently anchored permissive root|FUTURE_IMPLEMENTATION_REQUIREMENT|Current implementation requires a separately authorized source-level trusted_root.py change; no caller setter and no test monkeypatch substitute. Separate Owner transition scope and separately authorized Builder work required before any implementation|
|Actual loaded-code/deployment integrity verification|UNSUPPORTED_BY_CURRENT_SCHEMA|The root compares supplied identity tokens and policy digest, not loaded-source hashes or authenticated deployment bytes. Must not equate a matching string with proof that exact code ran|
|Future transition version evidence|DOCUMENTARY_CONSTRAINT|A root source change creates a different repository artifact. Owner must specify its exact transition/deployment commit and independently verified source differences while retaining the reviewed logic reference, or ratify a revised binding/version with recomputed policy. No self-referential commit SHA is invented or precomputed|
|Separate infrastructure need|DOCUMENTARY_CONSTRAINT|No additional infrastructure is proven mandatory for the existing in-memory interfaces. Any required durable journal, isolation, storage/ACL or containment mechanism must be separately assessed and authorized; A1 cannot implement it|
|Verification before activation|DOCUMENTARY_CONSTRAINT|Exact future authority artifact, ratified fields/actors/permissions, computed identities, immutable transition/source evidence, independent review and separately authorized mismatch/positive testing as needed. No new test authorization from this draft|
|Mismatch handling|SUPPORTED_SCHEMA_FIELD|Absent root, authority/harness/version/policy digest mismatch and manifest/action/actor/role mismatch produce fail-closed decisions through existing checks; no permissive fallback|
|Transition activation|DOCUMENTARY_CONSTRAINT|A1 does not cover it. Neither completed configuration nor technical construction/test success activates the future operation; separate exact Owner execution grant required|

Exact future action scope: authorized canonical computation and verification of the frozen documentary input/output/policy; a separately authorized root source transition confined to the chosen exact documentary operation; immutable source/version reconciliation and independent evidence review; only then any separately authorized bounded read/release evaluation. None is performed or authorized here. No collector, vault, generator, observation pipeline, economic component, operational credentials or real-data access is part of this proposed mode.

### 13.10 STOP, quarantine, logging and resource procedure

|Requirement|Classification|Exact candidate obligation|
|---|---|---|
|STOP triggers|DOCUMENTARY_CONSTRAINT|Unexpected outcome/efficacy-bearing information; real data/metadata or payload; ambiguous provenance; fixture content/creation; unauthorized actors/privilege/actions; manifest/policy/digest/log mismatch; missing or duplicate record; no acknowledged exact linkage; unresolved/blocked disclosure; ranking/preferences; operational timing/cadence/availability/delivery; unauthorized longitudinal/aggregation/cross-source behavior; exceeded/unresolved resources; required unapproved implementation or execution|
|Quarantine procedure|DOCUMENTARY_CONSTRAINT|Stop implicated access/use/release; withhold affected raw/intermediate/report/log/debug/admin information; use only an already-authorized containment mechanism; no new mechanism or unsafe inspection to investigate|
|Incident procedure|DOCUMENTARY_CONSTRAINT|Record safe class/reference and known/unknown exposure; freeze affected rights/release; reclassify actual direct/indirect correlated exposure where applicable; escalate to appointed incident authority and Owner; investigate under exact additional authority before resume|
|Logging expectations|DOCUMENTARY_CONSTRAINT|Unique read/release IDs; actual actor/role/authorization/authority, exact target/manifest, decisions, incident/recipient/cumulative context; preserve correction/version history and approved retention; only safe structural records visible|
|Input/intermediate/log/admin access|DOCUMENTARY_CONSTRAINT|Same exact permitted reader/recipient limits apply before viewing, including debug/error traces, key/admin interfaces and indirect summaries. Hiding exports does not undo human/agent exposure|
|Automatic external STOP, quarantine and access freeze enforcement|UNSUPPORTED_BY_CURRENT_SCHEMA|Existing decision denials and quarantine states do not stop arbitrary outside processing, contain storage or revoke privileges|
|Required technical construction if Owner demands automated external enforcement|FUTURE_IMPLEMENTATION_REQUIREMENT|Separately specified and authorized Builder work only if selected requirements need such implementation; no construction or actor assignment under A1|

DELETION_OF_LEAKED_INFORMATION_DOES_NOT_RESTORE_BLINDNESS. CAPTURED != CLEAN. SEALED != CONFIRMATORY_CLEAN. No exposure-cleanliness certificate is produced.

|Resource/time field (documentary only)|Value / decision|Classification|
|---|---|---|
|MAX_CALENDAR_DURATION|OWNER_DECISION_REQUIRED; single-operation concept, no duration default|DOCUMENTARY_CONSTRAINT|
|MAX_COMPUTE|OWNER_DECISION_REQUIRED|DOCUMENTARY_CONSTRAINT|
|MAX_STORAGE|OWNER_DECISION_REQUIRED|DOCUMENTARY_CONSTRAINT|
|MAX_EXTERNAL_CALLS_IF_ANY|Operational calls prohibited for this mode; no quota creates permission|DOCUMENTARY_CONSTRAINT|
|MAX_HUMAN_ACCESS|OWNER_DECISION_REQUIRED; exact human readers and access limit|DOCUMENTARY_CONSTRAINT|
|MAX_AGENT_ACCESS|OWNER_DECISION_REQUIRED; exact agent/session readers and access limit|DOCUMENTARY_CONSTRAINT|
|ALLOWED_CREDENTIAL_SCOPE|Operational credential use prohibited; no credentials required/provisioned|DOCUMENTARY_CONSTRAINT|
|MAX_OUTPUT_VOLUME|OWNER_DECISION_REQUIRED|DOCUMENTARY_CONSTRAINT|
|MAX_LOG_RETENTION / journal retention|OWNER_DECISION_REQUIRED|DOCUMENTARY_CONSTRAINT|
|MONETARY_BUDGET|OWNER_DECISION_REQUIRED; no spending commitment|DOCUMENTARY_CONSTRAINT|
|STOP_ON_RESOURCE_LIMIT|Required; unresolved or exceeded boundary blocks operation, never automatically increases quota|DOCUMENTARY_CONSTRAINT|

No convenient numerical defaults. Schema resource-state validation is not evidence of measurement or enforcement of these limits. All economic-contract parameters can remain unresolved for this documentary draft; no economic choice is reopened or implicitly settled.

### 13.11 Open Owner choices and prerequisite timing

Every open choice below is OWNER_DECISION_REQUIRED. Derived digests are not included as discretionary choices. Factual leakage/disclosure/provenance conclusions require evidence; Owner ratification is not a replacement for evidence.

|Open choice|Why needed / action blocked|Contractual?|Owner decision?|Future Builder issue?|Runtime-test requirement?|
|---|---|---|---|---|---|
|Exact operation scope and two-call sequence|Freezes admitted acts and prohibits retries/extra targets; blocks future phase authorization|Yes, A1 future scope|Yes|Only if added enforcement needed|Separately authorized integration coverage|
|Canonical input/output fields, values, IDs/version and provenance reference|Makes exact binding unambiguous; blocks freeze/computation/use|Yes|Yes, ratify proposals|No field additions proposed|Binding mismatch/positive cases under future authority|
|Canonical policy content, class sets, construction/harness/version binding and fixture None|Binds exact policy, denies non-documentary input; blocks digest/root ratification|Yes|Yes|Root implementation separate|Version/authority/digest mismatches|
|Exact actors, role combinations, recipient and independent approver|Prevents role-only inferred permission; blocks action grants and release|Yes|Yes|External identity/access mechanisms only if needed|Actor/role/action/recipient/independence coverage|
|Authorization IDs and exact future execution-policy authority artifact|Supplies legitimate authority distinct from A1/construction/test PASS; blocks calls/root activation|Yes|Yes|Approved root transition|Wrong/absent authority and state|
|Calendar duration and resource limits/access ceilings|Bounds authorized commitment; blocks operational authorization/execution until applicable values resolved|Yes|Yes|Numerical enforcement only if separately required|State interface evidence is not numerical enforcement|
|Report destination, exportability and exact release permissions|Constrains actual disclosure; blocks report export/release|Yes|Yes|Transport/ACL only if separately needed|Schema cannot test real destination without extra authorized mechanism|
|Journal/report retention, custody and safe visibility|Preserves accountable evidence without hidden exposure; blocks durable operation/release as required|Yes|Yes|Durable logging/retention only if required|Separate approved control verification if required|
|Incident and quarantine authority/procedure|Determines safe freeze/investigation/resume; blocks operational phase lacking safe handling|Yes|Yes|Containment only if required|External controls require separate evidence|
|Trusted-root transition authority and version reconciliation|Preserves independent authority and exact deployed version; blocks permissive execution|Yes|Yes|Source-level root change requires separate Builder grant|Independent source review and bounded tests separately authorized|

Additional prerequisite evidence, not new Owner preference: exact authorized computation and independent digest verification; current-source/interface review for changed transition artifact; safe leakage assessment; recipient-specific cumulative history/review; approved logging/control capability evidence; precise resource-accountability procedure. All are unresolved for execution. A current UNRESOLVED input/output clearance or disclosure label must not be converted to CLEAR by assumption. Empty disclosure history is not a safety certificate.

Timing:
- REQUIRED_BEFORE_PHASE_AUTHORIZATION: exact scope, canonical declarations, actors/role combinations, release/destination, bounds, incident/custody duties, and explicit disposition of unsupported requirements.
- REQUIRED_BEFORE_PHASE_EXECUTION: freeze; authorized digest computation; factual clearances; exact action authorizations; safe disclosure history; exact log identities and approved handling; root transition/source/version evidence; separately granted execution permission.
- CAN_REMAIN_UNRESOLVED_DURING_THIS_DRAFT: all listed future decisions, digests, actual actors, technical implementation/effectiveness and transition. Honest unknowns do not prevent DRAFT_COMPLETE.
- CAN_REMAIN_UNRESOLVED_UNTIL_FINAL_ECONOMIC_CONTRACT: unrelated economic selection, information/inference, Book/execution/risk/promotion definitions; zero economic authority preserved.

Unsupported requirements must receive an explicit Owner disposition: accept a bounded documentary/manual obligation where consistent with the contract, narrow the phase, or separately authorize necessary implementation. No waiver, new implementation contract or runtime capability is silently introduced here.

DECLARED_UNRESOLVED_FIELD_COUNT = 41. EXHAUSTIVENESS_CERTIFIED = FALSE.
This operational phase configuration refines EXACT_NON_ECONOMIC_FEASIBILITY_SCOPE and RELEASE_PERMISSIONS. Option-specific phase prerequisites do not mutate the canonical register.

### 13.12 Future research fixture separation — no immediate fixture

FIXTURE_REQUIRED_FOR_IMMEDIATE_MODE = FALSE  
SYNTHETIC_STRUCTURAL_TEST_OBJECT != A2_RESEARCH_FIXTURE  
SYNTHETIC_LABEL_ALONE_ESTABLISHES_SAFETY = FALSE

Earlier synthetic structural test objects were authorized only for controls testing. Their existence, use and bounded PASS neither establish a research fixture's existence/correct construction nor qualify or authorize one. No such object or payload is opened or recreated.

|Future research-fixture prerequisite|Classification|Documentary requirement only|
|---|---|---|
|Exact qualification and separate scope|DOCUMENTARY_CONSTRAINT|A later Owner-defined research operation, exact fixture purpose and independent admissibility/approval evidence; not this no-fixture mode|
|Admissible construction basis|DOCUMENTARY_CONSTRAINT|Only explicitly approved outcome-free documentary/interface inputs and attested non-economic synthetic abstractions; no arbitrary real calibration|
|Prohibited inputs|DOCUMENTARY_CONSTRAINT|Real observations/efficacy metadata, prevalence/signals/opportunities/market response/performance/PnL/rankings/preferences/profitable latency and correlated derivatives|
|Complete provenance/lineage/reproducibility|DOCUMENTARY_CONSTRAINT|Pinned approved construction inputs/method/version, every material lineage reference, reproducibility metadata and exact manifest/policy binding; masking/aggregation does not erase provenance|
|Provenance representations|SUPPORTED_SCHEMA_FIELD|FixtureProvenance and FixtureProvenanceContract can express IDs, generator/version, input classes, lineage, required/allowed reproducibility keys, contamination/admissibility and exact provenance identity|
|Actual provenance truth / payload qualification|UNSUPPORTED_BY_CURRENT_SCHEMA|Metadata checks do not inspect payloads, establish real construction history or certify content safety|
|Approval evidence|DOCUMENTARY_CONSTRAINT|Exact separate Owner authority plus appointed admissibility/release review evidence before generation/admission/testing; none currently supplied for a research fixture|

No generator is proposed or needed for the immediate operation. Future research-fixture prerequisites are not populated, approved or implemented and do not enlarge this configuration.

### 13.13 Completion, publication and safe next action

This one appended section contains one input manifest, one output manifest and one policy candidate, exhaustive actual field rows, separated documentary/unsupported requirements, proposed role assignments, open choices, digest status and a future root transition description. The candidate remains intentionally non-executable: unresolved digest/actors/clearances/export/disclosure/root/authority are not operational defaults.

The published change is this existing dossier only, on a new Blue documentary branch based on review snapshot 31215914a7e11daa20ca0189d859bb69827a055c. No prior Owner artifact, audit, runtime/Builder code, trusted root, canonical registry or separate document is modified. No source execution, import, tests, constructors, hash computation or runtime verification was performed. Governance text/schema inspection and this documentary publication are the only acts.

EXECUTION_PERFORMED = NO  
FIXTURES_CREATED = NONE  
FIXTURES_ACCESSED = NONE  
REAL_DATA_ACCESSED = NONE  
REAL_METADATA_ACCESSED = NONE  
OPERATIONAL_ENDPOINTS_QUERIED = NONE  
OPERATIONAL_CREDENTIALS_USED = NONE  
BUILDER_USED = NO  
A2_RESEARCH_FIXTURE_AUTHORIZED = FALSE  
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE  
A2_FIXTURE_TESTING_AUTHORIZED = FALSE  
A2_EXECUTION_AUTHORIZED = FALSE  
ECONOMIC_AUTHORITY = 0  
ECONOMIC_DECISION_WEIGHT = 0  
COMPOSITE_ECONOMIC_AUTHORITY = 0  
CAPTURE_AUTHORIZATION = NONE  
DATA_T0 = NOT_DECLARED  
EXPERIMENT_T0 = NOT_DECLARED  
t0 = NOT_DECLARED  
REAL_CAPITAL_AUTHORIZED = FALSE  
LIVE_TRADING_AUTHORIZED = FALSE  
UNBLIND_AUTHORIZED = FALSE  
OBSERVATION_AUTHORITY = UNCHANGED  
NEW_DOCUMENTS_REQUIRED = FALSE_FOR_THIS_DRAFT  
THE_CONTRACT_REQUIRES_FAIL_CLOSED_BEHAVIOR  
TECHNICAL_CONTROL_EFFECTIVENESS_VERIFIED_BY_THIS_MISSION = FALSE

A later exact Owner authority artifact is needed for any future action; that does not require another document in this drafting mission. Historical A1 implementation/effectiveness qualifications remain historical, and later bounded source/test evidence is not promoted to deployed-control effectiveness.

TERMINAL_STATE = A2_INTEGRATION_CONFIGURATION_DRAFT_COMPLETE  
NEXT_SAFE_ACTION = OWNER_REVIEW_AND_RATIFICATION_OF_CONCRETE_CONFIGURATION
