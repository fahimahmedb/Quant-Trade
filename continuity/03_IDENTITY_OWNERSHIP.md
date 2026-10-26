# Identity / ownership proof

## Mission-selected ownership

For this mission, V3 owns proposal admission semantics. This is a mission design decision, not a historical claim that V3 was always canonical.

The exact engineering base already contains `DurableProposalLedger` in `multi_source_ideation_hardening.py`. The historical V3 rail contains another `ProposalLedger`. Porting that storage object would create a competing Proposal Ledger and violate the mission's absolute non-duplication law. Therefore the V3 rail is reused semantically, while persistence is deliberately rebound to the existing `DurableProposalLedger`.

F is reused only for the missing pure identity laws needed to preserve root / variant / exposure identity across administrative relabeling. The operational F feeder, F registry, source-work lifecycle, scheduler-like behavior and activation surfaces are not ported and are not enabled.

## Active ownership after CP03

| Mutation / truth | Active owner | Decision |
|---|---|---|
| proposal admission | V3 semantics over existing `DurableProposalLedger` | one passive admission truth |
| proposal persistence | existing `DurableProposalLedger` | reused; no second ledger |
| root / variant / exposure identity | pure F-sourced primitives | sidecar identity only |
| Research Intelligence policy | existing Research Intelligence | unchanged |
| producer / Candidate construction | existing Discovery | unchanged; V3 does not create Candidates |
| tasks / leases / scheduling | Control Plane / Oracle | unchanged |
| scientific adjudication | existing C2/C0 surface | unchanged |
| Scientific Memory | existing Scientific Memory | unchanged |

## Cross-owner linkage

The minimum linkage is:

`ROOT -> PROPOSAL -> RI DECISION -> DISCOVERY HANDOFF -> CANDIDATE CONTINUITY SIDECAR`

The admission record carries stable `root_hypothesis_id`, `variant_id`, provenance and cumulative exposure. RI receives a projection of semantic identity plus a continuity reference. Candidate identity is bound only after a downstream Candidate exists. No Candidate ID or experiment identity is legal in the V3 admission payload.

## Anti-reset law

`root_hypothesis_id` deliberately excludes cohort labels, branch/path labels and source-version labels. A cohort rename therefore cannot create a new root. `variant_id` is root plus scientific parameters. A same-root/same-variant proposal already exposed in the ledger is `DUPLICATE_OR_KNOWN`; changing cohort does not reset exposure. A parameter variant keeps the same root and preserves cumulative prior exposure.

This is scientific identity accounting only. It does not claim that a parameter variant is an independent confirmation or that a new source version proves a new mechanism.

## Historical UNKNOWN

The adapter does not complete historical denominators by inference. If mechanism, actor, universe, clock or horizon is `UNKNOWN`, root/variant identity remains `UNKNOWN`, admission is rejected, and Discovery handoff is forbidden. No placeholder identity is invented to obtain eligibility.

## Authority / activation

All admission evidence remains pre-outcome and closed-authority. F operational activation is not performed.

- F_OPERATIONALLY_ENABLED=FALSE
- SCHEDULER_MUTATION=FALSE
- CANDIDATE_CREATED_BY_ADMISSION=FALSE
- ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
- PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
- REAL_CAPITAL_AUTHORIZED=FALSE
- LIVE_TRADING_AUTHORIZED=FALSE
- OUTCOME_ACCESSED=FALSE

## Conflict resolution

The ownership conflict found during audit was: V3's historical `ProposalLedger` versus the already-present base `DurableProposalLedger`. Resolution: reuse the existing ledger and port only V3 admission behavior. This avoids a second authoritative proposal writer/store and preserves the mission-selected V3 admission boundary without rewriting history.
