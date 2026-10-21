# CP098 — JSON-equivalent containers disagree at the outcome membrane

Before-code executable e0959488d774e422986ce434a9053c1ba7eb448b; clean Builder
head ecbe74279c09a9bfb95f5b1d6d586d1c81e0a87b matches remote. Owner North Star
blob a328b4e remains controlling; CP085 remains the breadth baseline. Oracle
1d55c50d3e241f32bd10b09b3af424d5e6de21a5 differs from integrated d2e58a7 only
by worker wake receipts. Blue 9026e4d and Site source d14b96c are unchanged.
Normal Git accesses succeed; current environment observations available.

## Search and actual consumer reproduction

Searched all-branch history for tuple/serialization/outcome membrane and relevant
V2 tests plus Builder receipts. Existing CP042/044 export guards and reverse-ACK
allowlists remain useful; no tuple/container-equivalence admission test found.
Both v2_pipeline._reject_outcome_payload and v2_core._scan_forbidden_outcome_keys
traverse Mapping and list only. canonical_hash uses standard json.dumps, which
serializes tuples as JSON arrays, just like lists.

Using the actual JSON qualification fixture, add only:
export.review_context = ({"outcome": "SYNTHETIC_MEMBRANE_MARKER"},)
The actual run_pre_outcome_pipeline returns READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY
with outcome_accessed FALSE. Direct build_frozen_export_intent accepts the same
field and returns FROZEN_EXPORT_INTENT. JSON round-tripping that bundle turns the
tuple into a list; both consumers then block, respectively with
OUTCOME_DATA_VISIBLE_TO_RESEARCH and OUTCOME_DATA_IN_RESEARCH_EXPORT.
canonical_hash(tuple_bundle) == canonical_hash(round_tripped_list_bundle).
Thus a canonical JSON-equivalent payload receives contradictory membrane
admission, and an outcome-labeled synthetic field reaches the frozen export.
No actual economic value or outcome store was read. This establishes a Python
callable surface gap, not a bypass of the JSON-only CLI ingestion path.

## Reuse / build / no-build

Extend the two existing recursive guards to include tuples, the additional array
container already supported by the canonical serializer. Preserve each consumer's
existing forbidden vocabulary and diagnostics. Do not broaden to arbitrary
iterables, add another serializer, change hashes, consume generators, or scan
strings heuristically. Regression tests should exercise both real consumers,
nested/mixed containers, canonical-equivalence denial and benign replay stability.

Do not alter epoch updates merely because an isolated helper could be stricter:
no active epoch-update writer/consumer mismatch was demonstrated in this audit.
No new component is justified. Four authority flags remain literally FALSE; no
canonical Oracle mutation, experiment, prospective capture, active/sealed outcome
access, Site/API probe, deployment or cloud configuration change.
