# BUILDER CHECKPOINT 006 — EVIDENCE-BACKED SOURCE CONSUMPTION SEMANTICS

CHECKPOINT_ID: BUILDER_CP_006_SOURCE_CONSUMPTION_SEMANTICS_20261020
TASK_CAPABILITY: Correct historical source-consumption inference and prioritize binding documentary authority
BUILDER_ROLE: V2 Forward Builder / Quant Engineer
WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: e8aa1d79e897eab83271dc833cb03aed92c6eda7
CURRENT_BUILDER_HEAD_DESCRIBED: 44caecf6b54b9a5c6ad795d1f3daa3beff24b8fe
FRESH_ORACLE_V2_HEAD_REACQUIRED: e817e6c3d8782b04e09231910375948670b9eb7d
UPSTREAM_RELATED_BRANCHES:
- builder/oracle-v2-core-20261020
- audit/forensic-checkpoint-20261019

## Objective

Adversarially challenge CP005's conservative assumption that any historical pre-planner frontier task proves consumption of the later deterministic family fallback. Correct the planner if durable execution evidence does not support that inference.

## CP005 assumption falsified

CP005 treated every old frontier task without an explicit source binding as having consumed the current hard-coded fallback source for that family.

That assumption is too broad.

Historical/manual frontier tasks predate the current deterministic producer path, and V2 tasks can terminate before producer execution. Administrative task issuance is not proof that a source was scientifically consumed.

## Durable task evidence

### Institutional Flow

`FRONTIER-INSTITUTIONAL-FLOW-DISTINCT-MECHANISM-001`
- historical COMPLETE task;
- produced `FLOW-RUSSELL-RECON-CLOSE-001`;
- predates current deterministic V2 producer-stage accounting;
- has no durable `execution.completed_stages.mechanism_research` proof tying it to the current SEC T+1 fallback.

Therefore this old successful task does NOT prove that `sec_t1_operative_rule.json` was consumed.

`FRONTIER-INSTITUTIONAL-FLOW-DISTINCT-MECHANISM-007`
- BLOCKED;
- durable completed stage only: `legacy_duplicate_check`;
- no `mechanism_research` completion.

`FRONTIER-INSTITUTIONAL-FLOW-DISTINCT-MECHANISM-008`
- BLOCKED;
- completion receipt references the attempted mechanism stage, but durable `execution.completed_stages` contains only `legacy_duplicate_check`;
- the mechanism artifact is the pre-execution authorization blocker, not an engine-output/source-consumption proof.

`FRONTIER-INSTITUTIONAL-FLOW-DISTINCT-MECHANISM-009`
- likewise blocked before producer execution by `STAGE_NOT_EXPLICITLY_AUTHORIZED:mechanism_research`.

Conclusion: the current CFR T+1 packet remains scientifically unused by those blocked V2 tasks.

### Event Document

`FRONTIER-EVENT-DOCUMENT-DISTINCT-MECHANISM-004`
- COMPLETE;
- durable completed stages include `document_or_fundamental_research`, disconfirmation, freeze and validation handoff.

This DOES prove use of the then-current deterministic Event Document fallback. The Apple dividend packet is therefore conservatively treated as consumed for that frontier.

### Fundamental

`FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003`
- COMPLETE;
- durable completed stages include `document_or_fundamental_research`, disconfirmation, freeze and validation handoff.

This DOES prove use of the then-current deterministic Fundamental fallback. The Apple statement-cells packet is therefore conservatively treated as consumed for that frontier.

## Implementation correction

Commit:

`10a90a335ea72c8f9b8a5cc6f04707eb83079355` — `Count historical source use only after producer execution`

Updated `research/research_os/frontier_source_planner_v2.py`:
- introduced explicit producer-stage mapping by task type;
- a pre-planner task without source binding marks the known deterministic fallback consumed only when the exact producer stage exists in `execution.completed_stages`;
- pre-producer BLOCK, migration, administrative issuance or mere task existence no longer counts as source consumption;
- new planner-derived tasks with an explicit immutable source binding still reserve that exact source identity once issued, preventing duplicate reissue under a new sequence.

## Documentary-authority ordering correction

A second adversarial check found that chronology-only source sorting was scientifically weak for the two qualified Institutional Flow packets:

- `sec_t1_staff_faq.json`
  - available/captured: `2026-10-15T18:28:08.251479+00:00`
  - `rule_kind = STANDARD_SETTLEMENT_CONSTRAINT_EXPLANATION`
  - document kind explicitly states staff FAQ / nonbinding;
  - captured text states `no legal force or effect`.

- `sec_t1_operative_rule.json`
  - available/captured: `2026-10-15T20:43:05.673234+00:00`
  - `rule_kind = STANDARD_SETTLEMENT_OPERATIVE_RULE`
  - official CFR 17 CFR 240.15c6-1 text.

Selecting the FAQ merely because its capture timestamp is earlier would invert evidentiary authority.

Commit:

`d45ec7f4480a8044d46265552316782f1af74463` — `Prefer binding source authority before capture chronology`

Planner ordering now prefers:
1. binding operative rule;
2. explanatory staff material;
3. capture chronology/path/hash as deterministic tie-breakers.

For Institutional Flow:
- operative rule authority rank = 0;
- staff FAQ explanation authority rank = 10.

The output carries `evidence_authority_rank` and `evidence_kind` for transparent selection provenance.

## Test correction and expansion

Commit:

`44caecf6b54b9a5c6ad795d1f3daa3beff24b8fe` — `Test evidence-backed historical source consumption`

Updated focused tests now prove:
- a pre-producer Institutional BLOCK does not consume the CFR default;
- CFR operative rule is selected first on such state;
- FAQ is selected only after durable producer-stage completion proves the CFR default was actually consumed;
- Event/Fundamental defaults become exhausted only after durable producer-stage completion;
- QUANT with no qualified source remains a no-op;
- strongest unused Institutional evidence is bound into the refill task;
- capture-support JSON remains rejected;
- source mutation remains fail-closed;
- Institutional `mechanism_research` authorization still passes explicitly.

## Independent exact-head CI proof

GitHub Actions:
- Workflow: `Oracle V2 Core`
- Run ID: `39445273191`
- Exact head SHA: `44caecf6b54b9a5c6ad795d1f3daa3beff24b8fe`
- Job: `v2-core`
- Conclusion: `success`

Successful steps:
1. checkout/setup;
2. compile V2 Core and Builder extensions;
3. V2 contract/bridge/pipeline/worker/whole-loop tests plus edge-observability/source-planner tests;
4. policy fail-closed verification;
5. claim-ceiling verification;
6. exact-head V2 qualification receipt;
7. real V2 entrypoint against fresh GitHub state with remote writes disabled;
8. qualification artifact upload.

The broader `SEC P0 pre-t0 gate` for this SHA was still in progress when this checkpoint was written; no success claim is made for that gate here.

## Structural-overlap safeguard reconfirmed

A new documentary source does not automatically become a new economic edge.

Current preflight behavior remains unchanged:
- exact current hypothesis => `BLOCK_EXACT_CURRENT_DUPLICATE`;
- high structural/current-exposure overlap => review/block path;
- planner source novelty cannot bypass current-corpus distinctness screening.

Thus the source planner expands admissible evidence input capacity, not the number of edges by fiat.

## Authority / safety

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE
OUTCOME_ACCESS_STATUS: NOT_ACCESSED
ACTIVE_EPOCH_MUTATION_BY_BUILDER: NONE

## What is now proven

- Administrative task issuance is not evidence of scientific source consumption.
- Historical implicit-source consumption can be inferred conservatively from durable producer-stage completion where the deterministic fallback is known.
- Current blocked Institutional 007/008/009 tasks did not consume the CFR T+1 packet.
- Event/Fundamental current default packets do have durable producer-stage consumption evidence.
- Binding primary authority must outrank weaker explanatory material before chronological tie-breaking.
- Exact-head Oracle V2 CI remains green after the correction.

## What is not proven

- No new edge, alpha, economic result or profitability.
- No claim that the CFR T+1 candidate will survive current-overlap screening.
- No claim that the staff FAQ is economically distinct from the CFR rule; it is only a second qualified documentary packet.
- No source-network activation or acquisition expansion.
- No runtime deployment/reboot/Site closure.

## Next coherent Builder investigation

Do not add another generic missing-data architecture. Current repository already has:
- family-specific dossier requirements and `data_requirements`;
- implementability diagnostics;
- design-only adapter registry;
- acquisition firewall;
- typed PIT normalization/provenance.

The next potential residual gap to prove or falsify is narrower: whether there is a deterministic bridge from actual dossier/readiness gaps into typed, prioritized, non-network acquisition intents. Build it only if repository/historical inspection confirms that no existing capability already supplies this bridge.

EXACT_RESUME_ACTION: reacquire fresh Oracle HEAD; inspect existing acquisition/evidence-demand surfaces and historical branches for an existing dossier-gap -> acquisition-intent bridge. If absent, design the smallest pure fail-closed bridge; if present, do not duplicate it.
SAFE_TO_CONTINUE: TRUE
