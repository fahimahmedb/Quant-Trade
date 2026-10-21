# Horizontal C1 CP003 — auxiliary contract surface gap

BASE_SHA=97165db2faa3300cef1f23de0045ed93d25eb9cb
HEAD_SHA=bb854852283b13afe7821e3183ab5ba912e09c7f
BRANCH=codex/horizontal-completeness-convergence1-20261021
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

Owner asked to continue on the existing intermediate branch. No newer architecture
was merged, no base changed and L001 remains owned by Longitudinal.

Modules reviewed: early implementability and experiment envelope durable contracts.
Expected surface: every legitimate current producer disposition and its current
durable fields is representable in the existing auxiliary JSON Schema. Basis:
North Star §§5, 12, 15; registered ImplementabilityAssessment/ExperimentEnvelope;
the actual existing assess_implementability_depth and freeze_experiment_envelope.

Found H003, CURRENT_REQUIRED_CAPABILITY / HORIZONTAL: auxiliary assessment schema
omits BLOCK_IMPLEMENTABILITY, disallows UNKNOWN on four feasibility fields and
does not declare current detail/provenance/authority fields while forbidding
additional properties. Actual PASS/PARK/BLOCK/unknown producer outputs all fail
Draft 2020-12 validation. This is an absent legitimate output-state/field surface,
not malformed-parser stress or a semantic field lost across module boundaries.

Found H004, CURRENT_REQUIRED_CAPABILITY / HORIZONTAL: ExperimentEnvelope schema
forbids the protocol_payload field emitted by the current producer, for both a
frozen object and the explicit nonfrozen null state. The protocol body already
exists, is persisted and is consumed; its durable schema representation is absent.

The old registry test only checked required-key subset inclusion. It therefore
passed while the actual closed schema rejected the produced records. New tests
use the installed full jsonschema 4.26.0 Draft202012Validator against actual
producer outputs and JSON round trips. The explicit test dependency and existing
canonical CI gate will make this validation reproducible, without adding a runtime
dependency or changing common shared contracts.

Planned repair: expand the two existing auxiliary definitions to represent current
outputs; preserve legacy minimal records, additionalProperties=false, and closed
authority/mutation fields. No new producer, store, scheduler, memory or economic
capability. Schema acceptance is representation, never readiness/authority grant;
existing hash, provenance and execution gates retain those responsibilities.

Future Wave-2 surfaces: unchanged. No Vertical finding established. L001 remains
open with no handoff repair on this rail.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
SAFE_TO_CONTINUE=TRUE
