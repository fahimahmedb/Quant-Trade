# GIGA Q capability matrix

Base: `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`, supplied explicitly by the Owner.
Branch: `builder/giga-q-final-whole-system-hardening-20261023`.
North Star: `QUANT_NORTH_STAR.md`, Git blob `a328b4e6d7d71dafd532938888ebf9818b1b610f`.
The blob agrees with Wave2's pinned declaration. September routing documents are
historical context; this mission and the supplied immutable base govern this work.

Presence is separate from adversarial depth and continuity. QUALIFIED_PRESENT
below means the named bounded contract exists and has executable evidence, not
that the entire subsystem or a production deployment is qualified. PRESENT_PARTIAL
includes retained implementations with unresolved attack failures. No existence
claim is inferred from a filename alone. Full-system disposition is NOT_QUALIFIED.

Paths without a prefix in this table are under `research/research_os/`.

| Required capability | Classification | Canonical producer / consumer and evidence | Limit or blocker |
| --- | --- | --- | --- |
| Owner / governance | QUALIFIED_PRESENT | North Star; `runtime/CONTROL_PLANE.json`; `control_plane.py` | No engineering result grants Owner economic authority. |
| Authority membrane | PRESENT_PARTIAL | `worker_preflight.py`, V2 policy, canonical Factory firewall | Closed flags checked; historical alternate-entry and scope attacks remain unresolved. |
| Scientific Memory | PRESENT_PARTIAL | `scientific_memory.py`, `legacy.py`, `scientific_memory_feedback.py` | W1 normalization exists; legacy mutable-view/conflicting-identity attacks remain. |
| Negative knowledge | PRESENT_PARTIAL | `expansion/v2_core.py:build_negative_memory`, `research_intelligence.py:memory_relation` | Q repairs explicit scope/types and replay hash; complete corpus immutability not proved. |
| Historical memory recovery | EXTERNAL_DEPENDENCY | `legacy/source_manifest.json`, pinned imported ledger, CP069 reviews | Missing historical primary bytes are not fabricated. |
| Data acquisition | PRESENT_PARTIAL | `expansion/evidence_acquisition_intents_v2.py`, `acquisition_firewall_v1.py` | Existing deterministic route/receipt path; historical malformed/rebinding failures remain. |
| Evidence identity | PRESENT_PARTIAL | `expansion/typed_pit_registry_v1.py`, source manifests | Secondary registry and provenance attacks remain in retained corpus. |
| PIT / availability / revision | PRESENT_PARTIAL | `expansion/source_qualification.py`, `typed_pit_registry_v1.py`; W1 PIT tests | Passing W1 tests do not close all hostile route/clock/alias tests. |
| External licensed datasets | EXTERNAL_DEPENDENCY | Source qualification permission states | Missing permission/data stays BLOCKED, not negative evidence. |
| Research Intelligence | PRESENT_PARTIAL | `research_intelligence.py`, `research_action_planner.py`, `research_refill_policy.py` | Explainable bounded actions exist; not a measured universal allocator. |
| Ideation | QUALIFIED_PRESENT | `multi_source_ideation.py`, `ideation_cycle.py`, source tests | Passive proposal/seed contracts only. |
| Multi-Source intake | PRESENT_PARTIAL | Three policies, context snapshots, passive claims/ledger, `qualify_for_discovery` | Not a task producer; production proposal-to-Discovery continuity is not established. |
| Live divergent model backend | EXTERNAL_DEPENDENCY | Policy C ModelBackend boundary and unavailable receipts | Fake fixtures confer no live GPT-OSS qualification. |
| Discovery | PRESENT_PARTIAL | `discovery_chain.py`, `discovery_engine.py`, registered producer routes | Qualified RI RUN_PRODUCER admission exists; source catalog and end-to-end proposal consumption remain bounded. |
| Candidate identity | PRESENT_PARTIAL | Existing producer Candidate plus V2 Core Candidate binding | Q fixes serialized reconstruction for affected builders; multiple native representations remain. |
| Implementability | PRESENT_PARTIAL | `expansion/implementability_depth.py` -> Factory; Q repairs auxiliary-schema transmission | Recursive UNKNOWN/complexity and snapshot attacks remain. |
| Experiment registry | QUALIFIED_PRESENT | Pure `expansion/experiment_registry.py` -> infrastructure/Validator | Binding contract, not a second persistent scientific store. |
| Preregistration | PRESENT_PARTIAL | `freeze_experiment_envelope`, frozen runner protocol | Exists before execution; retained freeze/snapshot tests disprove blanket qualification. |
| Freeze | PRESENT_PARTIAL | `expansion/experiment_runner.py`, `final_shape.py` | Q preserves frozen economic declarations; other replay/snapshot attacks remain. |
| Trial accounting | PRESENT_PARTIAL | Canonical trial record and Factory accounting checks | UNKNOWN estimates stay unknown; hostile frozen replay coverage incomplete. |
| Outcome firewall | PRESENT_PARTIAL | `expansion/experiment_outcome_firewall.py`, V2 export membrane, ledger adapters | Q repairs tuple, semantic role, opaque object and passive-ledger gaps; other ingestion boundaries remain unqualified. |
| Cross-examination | PRESENT_PARTIAL | Canonical C0 axes and immutable refs | Contract exists; independence claims remain scoped, not universal semantic proof. |
| Validator | PRESENT_PARTIAL | `expansion/validation_readiness.py`, C0 validator refs | Independent structural readiness, never economic outcome certification. |
| Red Team | PRESENT_PARTIAL | `expansion/red_team_v2.py`, C0 refs | Negative-rights path exists; retained red-team mutation/monotonicity attacks remain. |
| Scientific Verdict | PRESENT_PARTIAL | `expansion/scientific_adjudication.py` | PROMOTE/PARK/KILL/BLOCK with claim ceiling; not profitability or runtime authority. |
| Economic Identity | PRESENT_PARTIAL | `expansion/final_shape.py:economic_identity_v1`, `portfolio_v2.py:structural_identity` | Q repairs frozen declaration transmission; shared wire/native conformance remains unresolved. |
| Portfolio readiness | PRESENT_PARTIAL | `portfolio_v2.py`, D0 reference validators | Q requires explicit closed evidence; structural identity/UNKNOWN/order attacks remain. |
| Structural overlap | PRESENT_PARTIAL | `portfolio_v2.py:structural_pair` | Structural overlap is not empirical correlation. |
| Empirical portfolio metrics | AUTHORITY_GATED | Explicit sealed empirical layer | No return-based correlation or marginal contribution was estimated. |
| Shadow lifecycle contracts | PRESENT_PARTIAL | Canonical `expansion/economic_lifecycle.py` adapter -> preserved D0 kernel | Identity/lifecycle only, no positions; scoped D0 tests pass, full hostile lifecycle qualification not established. |
| Observation identity | PRESENT_PARTIAL | D0 immutable core / observation hash / future evaluation binding | Contract creation does not start observation. |
| Prospective observation | AUTHORITY_GATED | D0 closed authority and forward register | Never activated. |
| Decay / review | PRESENT_PARTIAL | D0 review/evidence contracts; legacy inactive guard | Active evidence consumption remains gated; alternate legacy paths need further hardening. |
| Replacement / supersession | PRESENT_PARTIAL | D0 replacement links and scoped negative-transfer contract | Pre-outcome lineage exists; no active replacement execution. |
| Control Plane | PRESENT_PARTIAL | `control_plane.py` plus Owner-governed runtime documents | Canonical task control exists; no second scheduler added. |
| Capabilities | QUALIFIED_PRESENT | `runtime/CAPABILITY_REGISTRY.json` -> preflight / routing | Scope is registered producer/challenge/control capabilities. |
| Blockers | PRESENT_PARTIAL | Control/task/RI refusals and durable idle/wake receipts | Q preserves memory refusals and unknown queue states; every downstream surface not proved. |
| Budgets / bounded work | PRESENT_PARTIAL | Control max stages/lineages; RI budget checks; worker timeouts | Declared budgets are not measured global VOI. |
| Task identity / terminal accounting | PRESENT_PARTIAL | ResearchTask contract -> `queue_replenisher.py` / worker | Q restores FAILED accounting and unsupported-state refusal; legacy local queue attacks remain. |
| Retries / timeout | PRESENT_PARTIAL | `oracle_worker.py` attempts/retry_after and bounded execution | Disposable Git tests exist; all dependency/clock combinations not qualified. |
| Leases / fencing | PRESENT_PARTIAL | Worker generations / fresh preflight / Git ref CAS | Current canonical worker tests pass; retained local queue is a distinct compatibility surface. |
| Oracle runtime | PRESENT_PARTIAL | `oracle_worker.py`, `oracle_worker_v2.py` | Disposable tests only; no service launch or host mutation. |
| Receipts | PRESENT_PARTIAL | Canonical task/output/event/receipt atomic Git commit | Q rejects noncanonical Git paths and mixed terminal generations; exhaustive receipt authenticity/recovery not proved. |
| Outbox / authenticated emitter | PRESENT_PARTIAL | `deploy/oracle_live_projection.py` PENDING/ACK, bounded transport and reconciliation | Pending starts deliberately are not replayed after lease loss; full exactly-once remote delivery is not claimed. |
| Recovery | PRESENT_PARTIAL | Fresh snapshots, terminal task state, durable ACK reconciliation | Process and synthetic fault tests exist; actual remote reboot untested. |
| Live Lab | PRESENT_PARTIAL | Native JS mapper/reducer, observational transport, canonical receipts | 57 JS checks cover projection cases; deployed reconnect/snapshot service qualification absent. |
| Capital Desk | PRESENT_PARTIAL | `src/quant/desk/desk.py`, journal, execution model | Existing V1 fixture desk only; canonical Research-to-Capital convergence deferred. |
| Opportunity | PRESENT_PARTIAL | `src/quant/desk/opportunity.py` | No current V2 scientific-to-opportunity execution adapter qualified. |
| Scan / Vet | PRESENT_PARTIAL | Existing scanners and CapitalDesk selection | Documentary research eligibility cannot authorize current exposure. |
| Size / Risk | PRESENT_PARTIAL | Existing Desk proposal/risk functions | Retained invalid-numeric/accounting attacks remain; no execution authorized. |
| Fills | PRESENT_PARTIAL | Existing Desk ExecutionModel | Model evidence is not real fills; hostile input/snapshot failures remain. |
| Book | PRESENT_PARTIAL | `src/quant/book/ledger.py` is V1 accounting owner | Replay-token, stale-writer and failed-save attacks remain; D0 is not a competing position ledger. |
| Learning | PRESENT_PARTIAL | `src/quant/learning/store.py`, research feedback | Historical replay/concurrency and Book-to-memory transmission remain unqualified. |
| Feedback | PRESENT_PARTIAL | `scientific_memory_feedback.py`, V2 successor feedback | Epoch policy exists; no outcome feedback released. |
| Status surfaces | PRESENT_PARTIAL | Generated STATE/CHIEF_BRIEF plus Live Lab projections | Factual bounded displays exist; generated inventory must be refreshed after tests change. |
| Research-to-Capital convergence | INTENTIONALLY_DEFERRED | Future convergence owns this integration | Explicitly outside this builder; transmission gaps recorded, no adapter invented. |
| Real capital / live trading | AUTHORITY_GATED | Permanent Owner membrane | Both remain FALSE. |

No row is marked MISSING_REQUIRED solely because execution is forbidden. The
missing production handoffs and unresolved native/shared contracts are explicit
partial-capability blockers, not silently counted as qualified coverage.
