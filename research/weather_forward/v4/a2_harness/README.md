# Weather V4 A2 dedicated offline harness

## Authority

This static implementation was constructed under exact Owner authority:

`37e3b25f17a7c5d3b3bc8d37df730aa988585b6c`

Owner artifact:

`research/weather_forward/v4/owner/OWNER_V4_A2_DEDICATED_HARNESS_BUILDER_DECISION_2026-10-04.md`

Design basis:

`9b65151c6840cff9d6cad4b6ba897e329862d292`

The historical Gate-B runner is not part of this implementation and must remain unchanged:

`governance/run_gate_b_evidence_schema_discriminants_2026-09-21.py`

## Construction status

`IMPLEMENTATION_COMPLETE != CONTROL_EFFECTIVENESS_VERIFIED`

`IMPLEMENTATION_COMPLETE != A2_EXECUTION_AUTHORIZED`

`IMPLEMENTATION_COMPLETE != A2_HARNESS_APPROVED`

`A2_FIXTURE_GENERATION_AUTHORIZED = FALSE`

`A2_FIXTURE_TESTING_AUTHORIZED = FALSE`

`A2_EXECUTION_AUTHORIZED = FALSE`

`ECONOMIC_AUTHORITY = 0`

The completion meaning of these sources is only:

`DEDICATED_A2_HARNESS_STATIC_IMPLEMENTATION_COMPLETE`

It is not `A2_VALIDATED`, `A2_EXECUTION_READY`, or an approval of any future fixture, input, output, actor, source, endpoint, station, city, forecast model, market universe, cadence, resource bound, or economic assumption.

## Scope and properties

The harness is an offline, standard-library-only governance contract implementation. It provides source-level representations and deterministic decision logic for:

- exact Owner authority, harness identity/version, manifest-version, and full manifest-content binding;
- explicit input manifests and fail-closed field/class/reader validation;
- explicit output manifests and release restriction;
- future fixture provenance/lineage metadata only;
- declared roles separated from independently supplied action authorization;
- immutable in-memory structured log records with functional append semantics;
- explicit quarantine states;
- explicit STOP reasons and DENY behavior;
- cumulative-disclosure records whose empty, unrelated, unresolved, or recipient-mismatched history is not treated as safe;
- deterministic output decisions from explicit declared objects and state.

The code deliberately has no wall-clock reads, randomness, network access, environment-variable authority, hidden mutable global state, database integration, credential integration, collector logic, source selection, economic scoring, backtesting, PnL calculation, paper-trading logic, or live-trading logic.

## Manifest and authority behavior

`AuthorityBinding` requires an explicit Owner SHA, harness identity, harness version/commit identity interface, and manifest version identity. `HarnessPolicy` separately declares the exact expected authority, harness version, manifest version, manifest IDs, and exact SHA-256 structural identities for the approved input and output manifests. Missing, ambiguous, or mismatched authority fails closed.

`input_manifest_identity()` and `output_manifest_identity()` use deterministic standard-library JSON canonicalization plus SHA-256. The canonical payloads cover every material field of their respective manifest dataclasses. Set-like allowlists and role lists are sorted before serialization; JSON keys are sorted and compact separators are fixed. Any material manifest-content change therefore produces an identity mismatch against the policy unless the expected identity is separately changed under future authority.

`InputManifest` contains the required A2 structural fields:

- `input_id`
- `input_classification`
- `source_provenance_class`
- `exact_permitted_fields`
- `exact_prohibited_fields`
- `permitted_reader_roles`
- `raw_values_visible`
- `timestamps_visible`
- `frequency_or_count_information_visible`
- `longitudinal_observation_allowed`
- `aggregation_allowed`
- `cross_source_comparison_allowed`
- `efficacy_leakage_assessment`
- `access_logging_requirement`
- `quarantine_on_ambiguity`
- `owner_approval_required`

It also carries the manifest-version identity used for exact binding. Wildcard field permissions are rejected. Unknown or explicitly prohibited input classes are denied. A structurally valid input manifest is still denied if its recomputed full structural identity does not equal `HarnessPolicy.expected_input_manifest_identity`.

`OutputManifest` contains the required structural fields:

- `output_id`
- `output_type`
- `exact_metric_or_artifact`
- `granularity`
- `permitted_recipients`
- `exportability`
- `quarantine_status`
- `cumulative_disclosure_risk`
- `efficacy_leakage_assessment`
- `release_approval_requirement`
- `retention_rule`
- `incident_if_unexpected_information_revealed`

It also carries the manifest-version identity used for exact binding. A structurally valid output manifest is still denied if its recomputed full structural identity does not equal `HarnessPolicy.expected_output_manifest_identity`. Release additionally requires an explicitly permitted recipient role, an exact non-ambiguous recipient actor identity, a distinct release actor with an exact action authorization bound to the same Owner SHA, exportability explicitly allowed, quarantine `CLEAR`, leakage assessment `CLEAR`, cumulative-disclosure state `CLEAR` for the exact output/recipient actor/recipient-role context, and a resolved release-approval requirement. If approval is required, the release actor must declare `RELEASE_APPROVER`. A role declaration by itself never grants release capability.

## Fixture provenance interface

`FixtureProvenance` is metadata structure only. It contains:

- `fixture_id`
- `construction_input_classes`
- `generator_identity`
- `generator_version`
- `lineage_references`
- `reproducibility_metadata`
- `contamination_state`
- `admissibility_state`

No fixture payload, sample fixture, generator output, or fixture-derived value is included here. Unknown or ambiguous provenance, missing lineage, unknown contamination, blocked/unresolved admissibility, or non-allowed construction input classes fail closed.

## Roles and authorization

The declared roles include:

- `PHASE_OWNER`
- `EXECUTOR`
- `CUSTODY_ADMIN`
- `RESEARCH_VIEWER`
- `RELEASE_APPROVER`
- `INCIDENT_AUTHORITY`

`RoleDeclaration` is intentionally distinct from `ActionAuthorization`. A declared role is only an identity statement. An action is permitted only when an explicit authorization object matches the actor, role, exact action, exact authority SHA, and `AUTHORIZED` state.

## Logging

`StructuredAuditLog` is an immutable in-memory record sequence. Appending returns a new log value and does not mutate hidden global state. Each `LogRecord` includes:

- `authority_identity`
- `manifest_identity`
- `actor_role`
- `attempted_action`
- `permit_or_deny_state`
- `quarantine_state`
- `release_state`
- `incident_identifier`
- `cumulative_disclosure_state`

This is not cryptographic immutability and does not claim to be a deployed logging service.

## Fail-closed STOP semantics

Explicit STOP reasons include at least:

- `MISSING_AUTHORITY`
- `UNKNOWN_PROVENANCE`
- `PROHIBITED_INPUT_CLASS`
- `INPUT_MANIFEST_MISMATCH`
- `OUTPUT_MANIFEST_MISMATCH`
- `UNAUTHORIZED_READER`
- `UNAUTHORIZED_RECIPIENT`
- `FIXTURE_LINEAGE_AMBIGUITY`
- `UNEXPECTED_EFFICACY_LEAKAGE`
- `CUMULATIVE_DISCLOSURE_AMBIGUITY`
- `RESOURCE_BOUNDARY_UNRESOLVED`
- `RELEASE_NOT_AUTHORIZED`

Additional exact mismatch/declaration STOP reasons may be used for clearer diagnostics. Unknown values are not silently coerced into permission.

## Cumulative disclosure

`DisclosureRecord` binds each prior assessment to `output_id + recipient_actor_id + recipient_role`. `CumulativeDisclosureLedger` evaluates prior declared disclosure records only. An empty ledger evaluates to `UNRESOLVED`, not `CLEAR`. Any blocked record yields `BLOCKED`; any unresolved record or record with missing/ambiguous recipient actor identity yields `UNRESOLVED`; only explicit clear history can reach `CLEAR`. Output release additionally requires at least one explicit clear disclosure assessment for the exact output identifier, exact recipient actor ID, and recipient role, so a CLEAR assessment for another actor sharing the same role cannot authorize release.

## Construction-mission non-actions

During this construction and static-repair mission:

- no harness code was executed or imported;
- no tests, pytest, smoke tests, linters, type checkers, or CI were run;
- no fixture content was opened;
- no fixture was created, generated, or tested;
- no real data was accessed;
- no real operational/efficacy metadata was accessed;
- no endpoint was queried;
- no credential was used;
- no operational source, city, station, model, cadence, or trading universe was selected;
- no economic validation, backtest, PnL calculation, paper trade, or live trade was performed.

Future fixture generation, fixture testing, or harness execution requires separate exact authority. Static implementation does not activate those permissions.
