# BLUE — WEATHER V4 PHASE-GATE OWNER DECISION SUPPORT — 2026-10-04

DECISION_SUPPORT_ONLY = TRUE  
OWNER_APPROVAL = FALSE  
PHASE_GATE_DECISION_SUPPORT = READY_FOR_OWNER_REVIEW  
PHASE_AUTHORIZATION = NONE  
OWNER_PHASE_GATE = NOT_GRANTED

Decision question: WHAT EXACT NON-ECONOMIC FEASIBILITY PHASE, IF ANY, SHOULD THE OWNER AUTHORIZE NEXT?

## 1. Exact authority and qualifications

|Mandatory authority|Exact commit|Verified artifact/blob|
|---|---|---|
|Astra pre-op audit; branch astra/weather-v4-pre-op-contract-audit-2026-10-04|926741e7a67cb80bccde0ff428f2837bb200cf19|research/weather_forward/v4/audit/ASTRA_V4_PRE_OP_CONTRACT_AUDIT_2026-10-04.md; 2f285b19dc6a61947ba7be78f48bb35425c71de6|
|Audited structural contract; branch blue/weather-v4-structural-pre-op-contract-2026-10-04|de74c887b5dec9e4bd6f851c3571e69191015f43|research/weather_forward/v4/blue/BLUE_V4_STRUCTURAL_PRE_OPERATIONAL_CONTRACT_2026-10-04.md; 33cb77198d36357d6993fefa82c0a57174544a7d|
|Audited contract companion|de74c887b5dec9e4bd6f851c3571e69191015f43|same basename .json; 91d7c0b64dc9310a4432a3d6a11fd84966f6cfb5|
|Owner structural decision|9391ce7a3f66cfc5bff2c745ca2dbb1072bba954|research/weather_forward/v4/owner/OWNER_OD04_OD12_STRUCTURAL_DECISION_2026-10-04.md; 3df739532e262b50ac29f56f86526d94ca694b93|
|Owner OD01–OD03 decision|377af70116f24f486feac7b4da5d2873107822a2|research/weather_forward/v4/owner/OWNER_OD01_OD03_DECISION_2026-10-04.md; a64a29069d6a3b8a6e4166f27a3d9159b86fd3d7|

All mandatory commits/artifacts independently resolved at exact SHA. Named Astra/Blue branch HEADs matched those SHAs during this mission. Astra commit's sole parent is audited contract de74c887…; that contract's sole parent is df39039b…. The repaired companion has no audit verdict in owner_fields_transcribed; its historical readiness state NOT_PERFORMED and allowed future dispositions are separate. The actual completed audit result is in Astra's later report, not retroactively written into the audited contract.

PRE_OP_CONTRACT_AUDIT = PASS_FOR_OWNER_PHASE_GATE_CONSIDERATION  
ASTRA_PASS != PHASE_AUTHORIZATION  
BLUE_DECISION_SUPPORT != PHASE_AUTHORIZATION  
THE_CONTRACT_REQUIRES_FAIL_CLOSED_BEHAVIOR  
TECHNICAL_CONTROL_IMPLEMENTATION_ESTABLISHED = FALSE  
TECHNICAL_CONTROL_EFFECTIVENESS_VERIFIED = FALSE  
DECLARED_UNRESOLVED_FIELD_COUNT = 41  
EXHAUSTIVENESS_CERTIFIED = FALSE  
UNBLIND_IMPLEMENTATION_REQUIRED = ONLY_IF_REQUIRED_BY_THE_EXACT_AUTHORIZED_PHASE  
SYNTHETIC_LABEL_ALONE_ESTABLISHES_SAFETY = FALSE

PASS is structural permission for the owner to consider an exact bounded phase, not a security/custody/implementation certificate. No fixture is approved or implementation verified here. The Stage-1 input/output/metric allowlist specification links primarily to EXACT_NON_ECONOMIC_FEASIBILITY_SCOPE and RELEASE_PERMISSIONS. No canonical 42nd field is created and no register modified.

Preserve ratified Probability-first preference, 30-calendar-day primary horizon, persistent Book, no resets, blocking/finite-batch FWER/fixed-endpoint architecture, taker-only confirmation, no actual forced 30d liquidation, minimal policy and H4+H5 consideration floor. Full economic definitions, risk limits and selection rule remain unresolved. This document changes none.

## 2. Three materially distinct choices — none selected

|Choice|Distinct purpose and tradeoff|Cannot establish|
|---|---|---|
|A — DOCUMENTATION / SYNTHETIC-FIXTURE-ONLY FEASIBILITY|Offline documentation and, only after explicit future permission, admissible fixtures/mocks using an approved existing technical harness. No real access. May reveal interface/control-design errors without operational observations; preparation, generator provenance and offline review still cost resources|Endpoint/auth availability, actual coverage/delivery/timing, deployed control effectiveness, clean real validation data or economics|
|B — RESTRICTED TECHNICAL-ACCESS FEASIBILITY|A narrowly authorized real technical question through a demonstrably restricted interface. Could resolve existence/authentication/field presence without efficacy information; requires more prior controls, rights, custody and disclosure review|Latency/delivery distributions, real gap/frequency patterns, preferred source/city/station/model, prevalence, rankings, economic feasibility or trading effectiveness|
|C — NO OPERATIONAL PHASE YET|Remain documentation-only; owner retains time/resources to specify missing roles, safe boundaries or controls. C is a valid deliberate choice, not failure|Any new operational feasibility finding or implemented control proof|

A is not automatically preferable. B is not an extension automatically unlocked by A. C is not permission to perform a substitute pilot. Implementation details below are unresolved owner fields within these three choices, not extra alternatives.

All acts described below are candidate future scope only. No part of A, B or C is executed by this mission. OPTION_B_DESIGN != OPTION_B_EXECUTION.

## 3. OPTION A specification

|Required field|Proposed future boundary — unapproved|
|---|---|
|OPTION_ID|A|
|PURPOSE|Assess documentation/schema/manifest consistency and technical interface/control logic on admissible offline material|
|ALLOWED_ACTS|Review approved non-outcome docs/static contracts; specify manifests/roles/logs/incidents; after separate explicit permission generate/use admissible synthetic fixtures, static vectors and mocks in an approved existing offline harness|
|PROHIBITED_ACTS|All real observations/market/trading/efficacy data; operational endpoint calls/auth; raw metadata sampling; new collector/runtime/code deployment; backtest/economic study; production/control implementation under this label; unblind|
|ALLOWED_INPUTS|Pinned approved authority/schema/protocol/static-interface documents with outcome-free provenance; future NON_ECONOMIC_SYNTHETIC fixtures satisfying §6|
|PROHIBITED_INPUTS|Real payloads, telemetry or statistics; selected performance cases, incident efficacy summaries, actual fixtures without approved provenance; documentation examples derived from real efficacy data|
|ALLOWED_OUTPUTS|Approved conceptual schemas/manifests, consistency findings, fixture-provenance/generator specifications, synthetic interface/error/control test findings in exact allowlisted form|
|QUARANTINED_OUTPUTS|Unexpected real values, source preferences, empirical claims, unapproved fixture contents/logs/debug traces, ambiguous construction lineage; all unreleased intermediates|
|WHO_MAY_ACCESS_INPUTS|Assigned EXECUTOR sees approved docs/admissible synthetic material only; other abstract roles see only assigned classes in §7|
|WHO_MAY_SEE_OUTPUTS|Assigned RELEASE_APPROVER reviews bounded quarantined drafts; RESEARCH_VIEWER sees approved outcome-free exports only; no actual recipients appointed|
|ACCESS_LOGGING_REQUIREMENTS|Immutable artifact/generator/input/hash and role-action log; record reading, generation, intermediates and releases; no secret/raw accidental content copied into readable logs|
|FIXTURE_POLICY|Prospective admission only under §6; no actual fixture exists or is inspected/approved in this mission|
|RESOURCE_BOUNDARY|Owner-defined compute/storage/human/agent/output/retention caps; external calls, real credentials/capture forbidden; caps unresolved §8|
|TIME_BOUNDARY|Owner-defined deadline/stop time, no inferred duration; OWNER_DECISION_REQUIRED|
|STOP_RULES|All §9 classes; additionally halt if an approved offline harness or admissible inputs unavailable, rather than implementing a replacement|
|INCIDENT_RULES|All §9 actions; construction-lineage violation quarantines fixture and derivatives and reclassifies exposed surfaces|
|DEPENDENCIES_REQUIRED_BEFORE_AUTHORIZATION|Exact acts and fixture policy, pinned doc/provenance classes, abstract-to-actual role assignment, I/O allowlists, caps, stop/incident/release rules and explicit owner authorization|
|DEPENDENCIES_NOT_REQUIRED_FOR_THIS_PHASE|Real endpoint rights/credentials, actual market/source binding, real vault/unblind, collector/Builder; final economic inference/risk definitions may remain unresolved|
|WHAT_THE_PHASE_CAN_ESTABLISH|Document consistency and offline interface/control behavior for the exact authorized harness/inputs, if executed later; synthetic findings are scope-limited|
|WHAT_THE_PHASE_CANNOT_ESTABLISH|Real operational availability, actual custody/vault enforcement, actual schema payload coverage, market execution, economics, statistical information/tails, H4/H5/H6 or clean historical exposure|
|CONTAMINATION_RISK|Hidden real calibration in “synthetic” inputs, outcome-bearing docs or mocks, copied logs and indirect summaries; no safe label without provenance|
|FAIL_CLOSED_BEHAVIOR_REQUIRED|Reject/quarantine ambiguity before read/use/release; stop on violated boundary; actual mechanism must later be established for exact scope, not presumed implemented|
|UNBLINDING_REQUIRED|NO; PROHIBITED_OR_DEFERRED|
|RAW_REAL_DATA_REQUIRED|NO; PROHIBITED|
|COLLECTOR_REQUIRED|NO; PROHIBITED_OR_DEFERRED|
|BUILDER_REQUIRED|NO for this fixed scope using approved existing offline tools; if code/control/harness implementation is needed, stop for distinct owner scope/Builder decision|
|CREDENTIALS_REQUIRED|NO operational credentials; PROHIBITED_OR_DEFERRED|

Fixture-driven interface checking is technical testing, not strategy validation. Its actual future outputs require an explicit phase decision; the current document supplies no fixtures or runnable code.

## 4. OPTION B specification

|Required field|Proposed future boundary — unapproved|
|---|---|
|OPTION_ID|B|
|PURPOSE|Answer a strictly scoped technical existence/authentication/field/schema/document/version/interface question without observing or deriving efficacy|
|ALLOWED_ACTS|Only exact preapproved technical request and restricted response projection through an already established safe interface, with appointed role and call/disclosure limits; no actual request is specified or made now|
|PROHIBITED_ACTS|Broad/raw payload access; observing weather/market values/outcome labels; probing history; timing/cadence/gap/frequency measurement; relative source/market comparisons; repeated adaptive probes; source/station/model/city/family ranking; capture; implementation; unblind|
|ALLOWED_INPUTS|Only owner-approved REAL_TECHNICAL_METADATA field-existence/type/protocol/document/version material whose values and combined exposure cannot reveal efficacy; approved non-outcome docs; admissible synthetic material only under §6|
|PROHIBITED_INPUTS|Actual timestamp values/distributions, price/weather/trade/outcome content, informative identifiers/counts/delivery patterns, response order or timing revealing advantage, efficacy-bearing debug/admin/raw telemetry|
|ALLOWED_OUTPUTS|Exact approved question result, such as logical field-existence/type/schema result, redacted technical access result or outcome-free document/interface specification; actual value/metric is not supplied here|
|QUARANTINED_OUTPUTS|Raw responses/intermediates/unapproved identifiers and values, timestamps, delivery/error series, counts and provenance ambiguity; any output or cumulative sequence capable of preference/ranking/efficacy inference|
|WHO_MAY_ACCESS_INPUTS|Assigned restricted EXECUTOR/interface can view only approved non-efficacy projection; CUSTODY_ADMIN no research/decrypt privilege; unknown raw observational content must not be knowingly requested under B|
|WHO_MAY_SEE_OUTPUTS|RELEASE_APPROVER sees only safely bounded projections and disclosure ledger; RESEARCH_VIEWER sees approved exports; incident access explicitly separately bounded, not broad retrospective raw review|
|ACCESS_LOGGING_REQUIREMENTS|Immutable request-manifest hash, roles, permit/reject, access/release record and cumulative disclosure state; secret/raw payload and operational timestamp/count series segregated from research-readable logs|
|FIXTURE_POLICY|If needed to demonstrate interface restrictions later, only §6-admissible offline fixtures; never derive mocks or test vectors from real responses/performance; no actual fixture now|
|RESOURCE_BOUNDARY|Owner-defined exact call/access/compute/storage/output/retention limits, narrowly scoped credential rights; no quota values invented; no general operational use|
|TIME_BOUNDARY|Owner-defined request/phase boundary; no availability/timing/cadence estimate now; no automatic polling or extension|
|STOP_RULES|All §9; B unavailable if the interface's input, output, admin, log or cumulative exposure cannot be specified safely|
|INCIDENT_RULES|All §9; freeze affected request/release/credential access, preserve secure evidence and classify actual/indirect exposure; no suppression-as-blindness claim|
|DEPENDENCIES_REQUIRED_BEFORE_AUTHORIZATION|Exact outcome-free request/field allowlists; access feasibility/provenance from permitted docs only; identified safe interface/control requirements, custody actors, credential scope, cumulative-disclosure rule, caps and incident plan|
|DEPENDENCIES_NOT_REQUIRED_FOR_THIS_PHASE|Economic claim/alpha/block/power/risk thresholds, real observational capture, collector, Maker evidence, H4/H5/H6 or unblind; no requirement to finish all economics to frame a safe technical question|
|WHAT_THE_PHASE_CAN_ESTABLISH|Only exact authorized technical existence/authentication/schema/field/document/version/interface finding if later executed; no finding made here|
|WHAT_THE_PHASE_CANNOT_ESTABLISH|Sustained delivery/reliability/coverage, efficacy-relevant gaps or cadence, actual timestamp advantage, source priority, economic opportunity or execution validity, clean real validation evidence|
|CONTAMINATION_RISK|Highest access/cumulative risk of the three options; a safe-looking response/status/version may reveal source relevance; access itself can expose efficacy even without export|
|FAIL_CLOSED_BEHAVIOR_REQUIRED|Safe projection must be justified before any request/access; ambiguous or efficacy-bearing route rejected; do not first inspect real metadata to decide whether B is safe|
|UNBLINDING_REQUIRED|NO; PROHIBITED_OR_DEFERRED; no sealed-validation decryption allowed|
|RAW_REAL_DATA_REQUIRED|NO raw observational/economic data; exact non-efficacy real metadata only conditionally permitted in future B|
|COLLECTOR_REQUIRED|NO; polling/capture/collector PROHIBITED_OR_DEFERRED|
|BUILDER_REQUIRED|NO in this fixed scope; if safe interface/control implementation is missing, B stays unavailable pending a separate exact owner-authorized implementation decision|
|CREDENTIALS_REQUIRED|Potentially YES for the exact future authenticated technical request; rights/scope/identity OWNER_DECISION_REQUIRED; none invented or used here|

If safe response generation depends on a new gateway/control implementation, that is a separate prerequisite—not permission to build it during B. Any machine/admin processing efficacy-bearing content is still access needing its own authority/exposure review; research output suppression does not authorize that raw input access. B cannot import raw weather/market content “just to redact it”. If origin-side restriction or a separately authorized safe interface cannot prevent prohibited access, B is unavailable.

## 5. OPTION C specification

|Required field|Proposed owner choice — unapproved|
|---|---|
|OPTION_ID|C|
|PURPOSE|Decline operational feasibility now and retain documentation-only governance until required safeguards can be safely specified|
|ALLOWED_ACTS|Owner review and, if separately commissioned, further outcome-blind document/role/manifest/provenance/resource/incident specification; no operational findings|
|PROHIBITED_ACTS|Executing A or B, fixture generation/use, harness testing, real data/metadata/endpoints/credentials, collectors/Builder/runtime, unblind/economics|
|ALLOWED_INPUTS|Exact authority/support and approved outcome-free governance/schema documents only|
|PROHIBITED_INPUTS|All real observational/technical metadata samples, efficacy-bearing documentation, fixtures or performance; no evidence-gathering substitute|
|ALLOWED_OUTPUTS|Owner decision to defer, unresolved-boundary inventory and conceptual documentary clarification; no fabricated feasibility result|
|QUARANTINED_OUTPUTS|Unexpected outcomes/metadata/fixture contents, unapproved operational/efficacy material and any attempted permissive workaround|
|WHO_MAY_ACCESS_INPUTS|Assigned document EXECUTOR/PHASE_OWNER roles only approved documents; role assignment for later work remains explicit|
|WHO_MAY_SEE_OUTPUTS|Owner and exact document-release recipients approved through RELEASE_APPROVER; no real actors invented|
|ACCESS_LOGGING_REQUIREMENTS|Document/reference/hash, role and release/incident logs; no operational telemetry created|
|FIXTURE_POLICY|No fixture generation/inspection/approval/use; provenance rules may remain conceptual; §6 applies if accidental fixture content arrives|
|RESOURCE_BOUNDARY|No operational resource commitment; any separately commissioned documentation budget/time/access/retention requires owner bounds|
|TIME_BOUNDARY|No operational start/deadline inferred; owner may specify review date/documentation scope separately without activating feasibility|
|STOP_RULES|All §9 plus attempted transition to testing/access without a new owner decision|
|INCIDENT_RULES|All §9 where applicable; unexpected data quarantined and exposure recorded without creating an operational phase|
|DEPENDENCIES_REQUIRED_BEFORE_AUTHORIZATION|No operational authorization is granted by C; owner records deliberate deferral and any separately permitted document scope|
|DEPENDENCIES_NOT_REQUIRED_FOR_THIS_PHASE|Actual operational actors/credentials, vault/control code, endpoints/manifests for executable access, numerical risk/inference thresholds may remain unresolved|
|WHAT_THE_PHASE_CAN_ESTABLISH|Only documentary status, remaining constraints and owner's choice to defer; C is not an executed operational phase|
|WHAT_THE_PHASE_CANNOT_ESTABLISH|Any endpoint, auth, fixture/harness, capture/control-effectiveness, economic or real data finding|
|CONTAMINATION_RISK|Restricted to documentary/accidental unsolicited exposure; no new access reduces exposure but cannot undo prior contamination|
|FAIL_CLOSED_BEHAVIOR_REQUIRED|Do not initiate an operation to fill a missing field; preserve unresolved status and deny attempted workaround|
|UNBLINDING_REQUIRED|NO; PROHIBITED_OR_DEFERRED|
|RAW_REAL_DATA_REQUIRED|NO; PROHIBITED|
|COLLECTOR_REQUIRED|NO; PROHIBITED_OR_DEFERRED|
|BUILDER_REQUIRED|NO; PROHIBITED_OR_DEFERRED|
|CREDENTIALS_REQUIRED|NO; PROHIBITED_OR_DEFERRED|

C may be chosen when actors, safe manifests, provenance, resources/access or stop/incident rules cannot be specified. It preserves optionality without claiming progress through unauthorized testing.

## 6. Synthetic fixture firewall — specification only

SYNTHETIC_LABEL_ALONE_ESTABLISHES_SAFETY = FALSE.

|Required policy field|A|B|C|
|---|---|---|---|
|FIXTURE_PROVENANCE_REQUIREMENT|Full declared lineage of construction inputs; approved outcome-free docs/schema only|Same if a fixture is later needed; no real-response-derived examples|No fixture use; hypothetical lineage requirement retained|
|FIXTURE_GENERATOR_VERSIONING|Immutable generator specification/version/hash and declared deterministic or random construction method; none instantiated now|Same; generator cannot adapt to real endpoint observations|May document requirement; no generator run|
|FIXTURE_GENERATION_INPUT_CLASS|Approved DOCUMENTATION_ONLY and independently justified NON_ECONOMIC_SYNTHETIC construction inputs only|Same, never REAL_TECHNICAL_METADATA or real observations for fixture calibration|Not applicable to execution; all generation prohibited|
|FIXTURE_INPUT_DISCLOSURE|Complete input classes/provenance and visible construction semantics to restricted approver; no hidden empirical calibration|Same; no copied real response/debug traces|Document requirements only|
|FIXTURE_ACCESS_LOGGING|Who generated/read/tested/exported which immutable input/generator/content hash, including intermediate views|Same; fixture and real-interface logs cannot be used to calibrate one another|Log accidental receipt/exposure as incident, do not inspect further|
|FIXTURE_REPRODUCIBILITY_REQUIREMENT|Later reproducible from pinned outcome-free inputs/method/seed if used; reproducibility does not establish safety|Same; not reproduce real performance behavior|Not tested|
|FIXTURE_CONTAMINATION_RULE|If real efficacy materially informed generation, PROHIBITED_FOR_STAGE_1; quarantine derivatives, record actual exposure|Same; cannot call it synthetic to bypass B access restrictions|Accidental received content triggers stop and exposure classification|

Permitted hypothetical construction: schema type/boundary/error cases and abstract role/access states unrelated to any actual market/source behavior. Artificial constants/seed choices for logical tests have no economic interpretation and may not be presented as operational thresholds. No constants or seed values supplied here.

Prohibited construction: real prevalence/signal/opportunity/response/ranking/source-city-station-model preference/profitable latency/P&L/performance distributions, directly or from summaries/priors selected using those results. Formerly viewed efficacy cannot be smuggled into “expert” calibration. Documentation/mock authors and agents must disclose construction history; unknown lineage fails closed. Randomization, aggregation, masking/anonymization do not erase provenance.

FIXTURES_CREATED = NONE. No actual fixture generated, read, approved, hashed or empirically declared admissible in this mission.

## 7. Abstract actors and access surfaces

All role holders, service identities, actual permissions and credentials are OWNER_DECISION_REQUIRED; none appointed. Role separation is a requirement to specify/prove later, not an established deployment.

|Role|A proposed duty/access|B proposed duty/access|C proposed duty/access|
|---|---|---|---|
|PHASE_OWNER|Accountable exact offline scope/bounds; owner decision holder remains authority|Accountable exact request/access/release boundaries|Records deferral/documentation scope|
|EXECUTOR|Approved docs/fixtures/harness only|Restricted approved metadata interface only, no raw observational/admin/validation access|Documents only|
|CUSTODY_ADMIN|Protect doc/fixture lineage and quarantined logs; no actual validation vault needed|Manage isolated access/log/quarantine controls; no implied raw/key/validation permission|Document retention/quarantine, no operational vault|
|RESEARCH_VIEWER|Approved synthetic/documentary exports only|Approved sanitized technical outputs only|Approved documentary outputs|
|RELEASE_APPROVER|Separate approval of scope-compliant outputs/provenance/cumulative disclosure|Independent approval of exact technical exports and cumulative ledger, without broad raw view|Approve documentary exports only|
|INCIDENT_AUTHORITY|Freeze/reclassify/investigate bounded incident|Freeze requests/rights/release and investigate without widening raw access|Quarantine accidental disclosure and prevent operational workaround|

If roles overlap or admins can view/decrypt prohibited inputs, the exact decision must disclose and constrain that capability; names on a chart do not prove blindness.

|Capability|A|B|C|
|---|---|---|---|
|VAULT_IMPLEMENTATION|Real validation vault not required; PROHIBITED_OR_DEFERRED. Approved offline quarantine/access controls still prerequisite|Established isolation for restricted technical artifacts/access may be needed; no vault implementation authorized within B. Actual validation vault PROHIBITED_OR_DEFERRED|PROHIBITED_OR_DEFERRED|
|DECRYPTION|Sealed validation/real payload decryption PROHIBITED|Sealed validation PROHIBITED; exact technical secret handling, if required, needs separate restricted rights; no permission inferred|PROHIBITED_OR_DEFERRED|
|UNBLINDING|PROHIBITED_OR_DEFERRED|PROHIBITED_OR_DEFERRED|PROHIBITED_OR_DEFERRED|
|RAW_OBSERVATIONAL_ACCESS|PROHIBITED|PROHIBITED|PROHIBITED|
|REAL_METADATA_ACCESS|PROHIBITED|Conditional exact outcome-free scope only, after separate owner authorization|PROHIBITED|
|EXTERNAL_ENDPOINT_ACCESS|PROHIBITED|Conditional exact approved technical request only; no endpoint selected now|PROHIBITED|
|COLLECTOR_IMPLEMENTATION|PROHIBITED_OR_DEFERRED|PROHIBITED_OR_DEFERRED|PROHIBITED_OR_DEFERRED|
|BUILDER|PROHIBITED_OR_DEFERRED|PROHIBITED_OR_DEFERRED; missing controls block B|PROHIBITED_OR_DEFERRED|

UNBLIND_IMPLEMENTATION_REQUIRED = ONLY_IF_REQUIRED_BY_THE_EXACT_PHASE. None of these specified options needs unblinding; it remains prohibited and implementation may be deferred. Choosing B never changes that.

Input access controls apply to raw inputs, intermediates, logs, dashboards, error text, debug traces, admin interfaces, key-management interfaces, indirect summaries and correlated metadata. A future exact manifest must name reader roles for every class, including executor/admin—not merely recipients of exports. No unmanifested surface accessible to research. Approval/incident roles receive only bounded safe evidence; investigation may need a separate explicit permission if raw/efficacy evidence is involved.

## 8. Proposed manifest schemas and owner bounds — no populated records

PHASE_INPUT_MANIFEST and PHASE_OUTPUT_MANIFEST are schemas only. No actual input/output row, endpoint/source/station/model/city/universe, credential or technical response is selected/populated. Field definitions below do not contain executable requests or permissive defaults.

### PHASE_INPUT_MANIFEST schema

|Field|Type / required meaning|
|---|---|
|input_id|Required immutable specification identifier; value to be assigned in exact future owner scope|
|input_classification|Required enum DOCUMENTATION_ONLY / NON_ECONOMIC_SYNTHETIC / REAL_TECHNICAL_METADATA / PROHIBITED; PROHIBITED never admissible|
|source_provenance_class|Declared doc/synthetic/technical lineage class and evidence of non-efficacy provenance, with hash/version references|
|exact_permitted_fields|Explicit finite field/type/view allowlist; no wildcard response access|
|exact_prohibited_fields|Explicit prohibited values/relationships and inherited efficacy exclusions; allowlist absence means no permission|
|permitted_reader_roles|Exact roles/capabilities for each raw/projected input, including admin and service processing|
|raw_values_visible|Required declared visibility and safe justification; does not authorize raw observations|
|timestamps_visible|Required distinguished categories from timestamp ladder below; actual values/distributions not automatically visible|
|frequency_or_count_information_visible|Required scope and leakage proof; no counts/patterns by technical label alone|
|longitudinal_observation_allowed|Explicit exact permission or denial; no automatic repeated probes|
|aggregation_allowed|Explicit aggregation definition/denial and cumulative disclosure review|
|cross-source_comparison_allowed|Explicit scope/denial; no comparative source advantage or preference permitted|
|efficacy_leakage_assessment|Pre-access assessment of direct, correlated and cumulative effects; UNKNOWN fails closed|
|access_logging_requirement|Immutable role/action/artifact/version and quarantine audit requirements; unsafe telemetry segregated|
|quarantine_on_ambiguity|Required fail-closed quarantine/deny workflow before further access/use|
|owner_approval_required|Exact owner decision reference required before access; current approval absent|

Additional conceptual provenance links may reference fixture input/generator versions, abstract request shape and allowed output IDs; they are manifest subfields, not extra canonical unresolved contract fields.

### PHASE_OUTPUT_MANIFEST schema

|Field|Type / required meaning|
|---|---|
|output_id|Required immutable output specification ID, no actual output populated|
|output_type|Declared document/synthetic technical finding/restricted metadata finding class|
|exact_metric_or_artifact|Exact logical metric or document definition and computation inputs; not a named real source or observed result|
|granularity|Permitted detail/redaction and denied combinations; granularity selected explicitly|
|permitted_recipients|Exact role-based recipients, including in-product/internal views|
|exportability|Explicit permitted export destination/scope or denial; export restriction alone is insufficient|
|quarantine_status|Release state and authority; not a declaration that an actual artifact is clean|
|cumulative_disclosure_risk|Assessment of all prior related releases and recipient/agent knowledge; repetition/order/availability/timing assessed|
|efficacy_leakage_assessment|Direct and indirect ranking/preference/advantage/efficacy assessment; UNKNOWN blocks release|
|release_approval_requirement|Independent exact approval with manifest/owner-scope reference; no automatic export|
|retention_rule|Owner-approved storage/access/retention and secure incident evidence policy|
|incident_if_unexpected_information_revealed|Exact mapping to STOP/quarantine/exposure rules §9|

Cumulative disclosure ledger must bind what each human/agent/admin has already seen, not merely files exported. A sequence of harmless-looking statuses/schema versions can reveal latency, event prevalence, delivery/source reliability or preference. Before a further request/read/release, evaluate its combination with previous content and context. If aggregate safety cannot be demonstrated, deny further access/release. Do not collect a series first and then decide whether exporting it is safe.

### Timestamp/delivery safety ladder

|Information class|A/C|Potential B boundary|
|---|---|---|
|FIELD_EXISTS|Documentation/schema statements only|Possible exact authorized logical presence question; not actual availability study|
|FIELD_PARSEABLE|Outcome-free abstract syntax/fixture specification only|Possible type/format compatibility without actual timestamp value; otherwise unavailable|
|ACTUAL_TIMESTAMP_VALUE|Prohibited real access|Prohibited in these proposed B boundaries; no value redacted only after research views it|
|TIMESTAMP_DISTRIBUTION|Prohibited|Prohibited|
|RELATIVE_SOURCE_LATENCY|Prohibited|Prohibited|
|RELATIVE_MARKET_LATENCY|Prohibited|Prohibited|
|MARKET_RESPONSE_COMPARISON|Prohibited|Prohibited|

No current measurement of availability, timing, frequency, cadence, gaps or delivery behavior. Technical response duration, error occurrence or version identity can reveal efficacy cumulatively; it needs the same pre-access firewall. Actual endpoint existence/auth success/field presence questions remain unanswered.

### Resource/time owner fields

|Owner decision field|A|B|C|
|---|---|---|---|
|MAX_CALENDAR_DURATION|OWNER_DECISION_REQUIRED|OWNER_DECISION_REQUIRED|No operational phase; future commissioned doc deadline OWNER_DECISION_REQUIRED|
|MAX_COMPUTE|OWNER_DECISION_REQUIRED|OWNER_DECISION_REQUIRED|Any separately commissioned docs OWNER_DECISION_REQUIRED|
|MAX_STORAGE|OWNER_DECISION_REQUIRED|OWNER_DECISION_REQUIRED|Document/incident retention OWNER_DECISION_REQUIRED|
|MAX_EXTERNAL_CALLS_IF_ANY|Operational calls prohibited, no numeric quota supplied|OWNER_DECISION_REQUIRED; exact question/cumulative safety bound, not general polling|Operational calls prohibited|
|MAX_HUMAN_ACCESS|OWNER_DECISION_REQUIRED, roles/input classes bounded|OWNER_DECISION_REQUIRED, all privileged access included|Document recipients/access OWNER_DECISION_REQUIRED|
|MAX_AGENT_ACCESS|OWNER_DECISION_REQUIRED, role/session context included|OWNER_DECISION_REQUIRED, no hidden agent summarization|Document access OWNER_DECISION_REQUIRED|
|ALLOWED_CREDENTIAL_SCOPE|Operational credentials prohibited|OWNER_DECISION_REQUIRED; no credential value or identity given|Operational credentials prohibited|
|MAX_OUTPUT_VOLUME|OWNER_DECISION_REQUIRED, disclosure review even below cap|OWNER_DECISION_REQUIRED, cap does not prove efficacy safety|Document releases OWNER_DECISION_REQUIRED|
|MAX_LOG_RETENTION|OWNER_DECISION_REQUIRED; safe incident evidence policy|OWNER_DECISION_REQUIRED; protected unsafe telemetry/rights|Document/incident policy OWNER_DECISION_REQUIRED|
|STOP_ON_RESOURCE_LIMIT|Required boundary stop; limit remains unresolved|Required boundary stop; limit remains unresolved|Stop commissioned document work at its exact bound; no operation starts|

No numerical budgets/durations/quotas/access caps invented. Disallowing an act is a scope prohibition, not an invented numeric default. B generally has greater control/access/cumulative-disclosure overhead; A needs provenance/harness review; C defers operational cost. No prices, availability or measured effort/delivery promise is offered.

## 9. Stop and incident matrix — applies to every option

These are required future rules, not proof of enforcement. They also govern boundaries of any subsequently commissioned documentary work.

For EVERY incident class in the matrix, all seven actions apply:
LOGGED = record event/class, affected manifest/role/artifact/hash where safely available, scope and suspected direct/indirect recipients; distinguish known from unknown exposure.
QUARANTINED = affected input/output/fixture/intermediate/logs and derivatives, with no extra reading to characterize efficacy.
ACCESS_FROZEN = suspend implicated reads/requests/generation/release/privileges; no self-resume or workaround.
SURFACE_RECLASSIFIED_IF_APPLICABLE = actual viewing/construction/correlated exposure appended to candidate-specific ledger; UNKNOWN if scope cannot be established, development/discovery-contaminated where known; no blanket clean claim.
ESCALATED_TO_OWNER = bounded incident notice without copying unsafe values; seek exact authority for any otherwise prohibited investigation.
RELEASE_BLOCKED = all implicated outputs and combined summaries pending safe resolution.
INVESTIGATED_BEFORE_RESUME = provenance, access cause, capability/control gap, cumulative disclosure and independent review; explicit owner resume permission where needed. No investigation grants raw/outcome access itself.

|Incident / STOP trigger|Affected scope and specific investigation focus — all seven actions above mandatory|
|---|---|
|UNEXPECTED_OUTCOME_BEARING_INFORMATION|Input/view and all derivatives; determine authorized versus accidental receipt/view without rereading outcomes|
|EFFICACY_REVEALING_DATA|Direct/indirect signals/preferences, recipients and correlated surfaces|
|UNAUTHORIZED_RAW_DATA|Raw payload/access path and admin/service capability; no “read then redact” exception|
|AMBIGUOUS_INPUT_PROVENANCE|Input and derivatives; require documented lineage before any resume|
|FIXTURE_PROVENANCE_VIOLATION|Generator/input/output lineage and exposed construction knowledge; synthetic label not a waiver|
|ACCESS_CONTROL_VIOLATION|Implicated roles/interfaces/key/admin paths and release rights|
|UNEXPECTED_PRIVILEGED_ACCESS|Actual privileged readers/capabilities and validation/key/log exposure|
|OUTPUT_CAPABLE_OF_RANKING_FAMILIES|Output plus combined context and all influenced hypothesis selection|
|OUTPUT_CAPABLE_OF_RANKING_CITIES|Location comparison/selection exposure and correlated markets|
|OUTPUT_CAPABLE_OF_RANKING_STATIONS|Station comparison/upstream/correlated data exposure|
|OUTPUT_CAPABLE_OF_RANKING_MODELS|Model/version priority inferred by technical outputs or summaries|
|OUTPUT_CAPABLE_OF_RANKING_SOURCES|Source preference/reliability/advantage inferred individually or cumulatively|
|TIMING_INFORMATION_REVEALING_EDGE_ADVANTAGE|Timestamp/delivery/error sequence, cross-source or market-relative information|
|RESOURCE_BOUNDARY_EXCEEDED|Resource-consuming acts and all access/releases after the bound; no automatic extra quota|
|INPUT_MANIFEST_MISMATCH|Unexpected fields/versions/classes/readers, inherited prohibited content|
|OUTPUT_MANIFEST_MISMATCH|Unapproved metric/detail/recipient/export/retention or cumulative content|
|UNAUTHORIZED_CROSS_SOURCE_COMPARISON|Linked requests/results/internal views; do not finish comparison to quantify its effect|
|UNAUTHORIZED_LONGITUDINAL_AGGREGATION|Series, counts, joins, dashboards and any hidden reuse/summarization|
|UNAUTHORIZED_TRANSITION_TO_OPERATIONAL_WORK|A/C scope expansion or missing B controls; stop instead of choosing a permissive substitute|

Incident logs/notifications themselves must not disclose the prohibited information. Secure retention is for bounded accountability, not access by research. Where no safe evidence/quarantine/notification mechanism is established, do not start A/B; no mechanism is constructed by this document.

DELETION_OF_LEAKED_INFORMATION_DOES_NOT_RESTORE_BLINDNESS.

## 10. Dependency timing and canonical-register discipline

DECLARED_UNRESOLVED_FIELD_COUNT = 41. EXHAUSTIVENESS_CERTIFIED = FALSE. No automatic mutation. Exact manifests/metric allowlists refine EXACT_NON_ECONOMIC_FEASIBILITY_SCOPE and RELEASE_PERMISSIONS; they do not silently create a 42nd field. Additional requirements here are OPTION_SPECIFIC_PHASE_DEPENDENCY, not new canonical contract fields.

|Dependency class / timing|A|B|C|
|---|---|---|---|
|REQUIRED_BEFORE_PHASE_AUTHORIZATION|Exact docs/fixture admissibility/acts/I/O/recipient manifest; abstract-to-actual roles; independent release and incident rules; resource/time bounds; no implementation scope creep|All A-relevant non-outcome boundaries plus exact technical request/field/provenance/credential/access shape, safe-interface/control prerequisite, cumulative-disclosure limits and stop rules. If not safely specifiable, B unavailable|No operational authorization; explicit owner deferral. Any later documentary commission needs its own bounded scope|
|REQUIRED_BEFORE_PHASE_EXECUTION|Actual approved existing harness/access/log/quarantine/release capability and admitted outcome-free inputs demonstrated within separate explicit authority; no current fixture/control testing|Required safe interface/isolation/access/projection/secret/log controls actually established and verified under separately authorized work BEFORE real access; absent evidence blocks execution|No operational execution. For future docs, approved documents/access/retention only|
|CAN_REMAIN_UNRESOLVED_DURING_THIS_PHASE|Real endpoint/credentials/operational sources, vault/unblind, collector. Generator specifics may be designed during documentation but no fixture use until exact provenance/admission prerequisites met|Future capture/unblind/economic sources; no real observational access. Optional capabilities not in exact B remain denied. Identity/right/bounds for actual request cannot stay unresolved at execution|Operational actors, credentials, safe live manifests, vault/access controls and resource/capture details can remain unresolved because nothing operational starts|
|CAN_REMAIN_UNRESOLVED_UNTIL_FINAL_ECONOMIC_CONTRACT|Statistical selection, claim/batch/alpha, blocking/system, information/duration, full Book/execution valuation, delta/p_min/risk/capacity/economic limits and decay/reopening|Same; a technical finding neither resolves nor waives them|Same|

“Design during phase” never means use unresolved access/generator choices meanwhile. A may produce conceptual design, but approved input/generation/reader/recipient/boundary rules must precede any corresponding act. Controls not implemented/verified today cannot be assumed effective. Where establishing a required capability needs Builder/control implementation, a separate owner decision is necessary; neither A nor B contains such permission.

Owner review may choose A, B or C only, with no automatic ordering. A/B execution requires an exact owner phase-gate artifact binding scope/manifests/actors/resource/stop and incident limits to the applicable audited contract and Astra qualifications. No full economic contract completion is claimed. Unresolved economics do not justify outcome-bearing “feasibility”.

## 11. Current mission actions and next safe action

REAL_DATA_ACCESSED = NONE  
NEW_DATA_ACCESSED = NONE  
NEW_OUTCOMES_ACCESSED = NONE  
FIXTURES_CREATED = NONE  
EXTERNAL_ENDPOINTS_QUERIED = NONE  
CREDENTIALS_USED = NONE  
OPERATIONAL_SOURCE_SELECTED = NONE  
BUILDER_USED = NO

Governance Git reads/writes only: authority documents and commit/ref/tree metadata; publication/content verification of this new document. “External endpoints NONE” means no operational/weather/market/auth endpoint testing; authorized governance connector publication is not Option B execution. No runtime, harness, fixture, collector, source, endpoint, cadence, market universe, credentials or new operational role selected.

ECONOMIC_AUTHORITY = 0  
ECONOMIC_DECISION_WEIGHT = 0  
COMPOSITE_ECONOMIC_AUTHORITY = 0  
CAPTURE_AUTHORIZATION = NONE  
CURRENT_PHASE_AUTHORIZATION = NONE  
REAL_CAPITAL_AUTHORIZED = FALSE  
LIVE_TRADING_AUTHORIZED = FALSE  
t0 = NOT_DECLARED  
DATA_T0 = NOT_DECLARED  
EXPERIMENT_T0 = NOT_DECLARED  
BUILDER_AUTHORIZED = FALSE  
OBSERVATION_AUTHORITY = UNCHANGED  
OWNER_PHASE_GATE = NOT_GRANTED  
FULL_VALIDATION_CONTRACT_COMPLETE = FALSE  
READY_FOR_FINAL_VALIDATION_CONTRACT_AUDIT = FALSE

ECONOMIC_PROGRESS = framed exactly three safe-boundary owner choices without executing access or manufacturing empirical assurance.
REMAINING_BLOCKER = owner choice and exact option-specific scope/roles/manifests/resources/control prerequisites.
EXIT_CONDITION = OWNER REVIEW ONLY; any subsequent act needs its own explicit scope.
FROZEN_SURFACE_TOUCHED = NONE.
FILES_MODIFIED_OUTSIDE_SCOPE = NONE.

NEXT_SAFE_ACTION = OWNER REVIEW ONLY. No option chosen or authorized; do not begin feasibility work.
