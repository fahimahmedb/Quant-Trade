# GIGA Q second-truth audit

Method: inspect definitions, persistence and actual callers; replay copies of
truth with self-consistent hashes; identify which upstream object owns semantics.
No store, scheduler, Candidate registry, Book or lifecycle engine was introduced.

| Surfaces expressing related truth | Canonical ownership and relationship | Result |
| --- | --- | --- |
| Historical H/V repair branches vs Wave2 | Exact supplied Wave2 commit owns this mission's code. Historical SHA-pinned tests are attack inputs only. | No merge/rebase/cherry-pick; source identity recorded in repair manifest. |
| ScientificMemory vs LegacyKnowledgeBase | ScientificMemory is normalized scoped scientific authority; legacy imported ledger/CP069 review owns historical provenance. Legacy is a compatibility read view. | Source-view conflict/alias tests remain open; do not call historical labels universal negative knowledge. |
| Proposal Ledger vs ResearchTask queue | Ledger owns passive proposals; Control Plane owns READY work and leases. | Existing operational-key rejection retained; Q consumes canonical pre-outcome membrane. |
| Source claims vs worker leases | Passive context/source claims have no runtime ownership/expiry; task generations are canonical worker fencing. | Different scopes; no conversion to lease authority. |
| RI decision vs scheduler state | RI recommends qualified actions; canonical refill/worker materializes bounded tasks. | Q stops unknown task state from masquerading as an empty queue. |
| Task schema vs queue terminal accounting | ResearchTask schema owns allowed task states; queue classifies them for existing scheduling semantics. | Q re-proves FAILED is terminal and unsupported states are explicit UNKNOWN. Historical KILLED remains compatibility-only. |
| Canonical V2 Candidate vs producer Candidate | Existing distinct native contracts have explicit boundaries and hashes. | Not unified by inventing a third Candidate. Broader native/wire conformance remains partial. |
| Candidate vs frozen execution declaration | Candidate owns hypothesis/generation; bound frozen protocol owns execution expression at freeze. | Q derives economic view from protocol; preserves Candidate snapshot/hash; disagreement blocks. |
| Factory registry vs scientific store | Registry is a pure hash binding; frozen envelope/scientific objects remain upstream owners. | No persistent duplicate experiment registry. |
| Auxiliary schema vs actual implementability/envelope producer | Producer owns current emitted semantics; existing auxiliary schema owns their wire representation. | Q repairs omitted fields/states and protocol body/null, without creating another schema or loosening authority. |
| Canonical C0 vs preserved C0 kernel | `scientific_adjudication.py` is canonical adapter; `_scientific_adjudication_c0.py` is preserved implementation, not independent authority. | No new verdict enum or scientific store. |
| Economic native identity vs shared CandidateEconomicIdentity schema | Native W1 structural law owns current diagnostics; stable shared schema is a different declared interface. | Native-to-shared adapter/conformance UNKNOWN. This blocks whole-system wire qualification; no arbitrary adapter invented. |
| Scientific/economic handoff copied ceiling/statuses | C0 owns verdict/ceiling; W1 owns structural/readiness status. Handoff must consume those exact values. | Q rejects self-rehashed drift and non-promotable upstream adjudication. |
| D0 canonical adapter vs preserved D0 kernel | Adapter rebinds campaign identity and validates canonical refs; preserved kernel remains the lifecycle implementation. | Q strengthens public ref admission through existing adapter, leaving historical source blob intact. |
| D0 shadow contract vs persistent Book | D0 explicitly owns identity/lifecycle only and contains no positions. `quant.book.Ledger` owns V1 bankroll/positions. | Different truth domains. No allocation/execution authority inferred. |
| Canonical outcome guard vs lane guards | Factory owns shared pre-outcome semantic checks; lanes retain stricter context-specific checks (e.g. passive operational fields). | Q ledger consumes canonical guard; tuple law synchronized in existing V2 scanners. Other ingestion guard gaps remain, not declared resolved. |
| Oracle events/receipts vs local outbox | Canonical Git commit owns task/output/event/receipt fact; local PENDING/ACK files describe delivery only. | Q canonical-path and terminal-lineage checks prevent specified drift. Local ACK shape is not a new scientific verdict. |
| Live Lab vs canonical task/research state | Mapper/reducer projects canonical facts. It cannot manufacture success, negative evidence, profitability or execution authority. | Local projection tests pass; remote/snapshot proof remains partial. |
| V1 local queue vs canonical Git worker | Git task/ref/lease law is current Oracle authority; local Campaign/Queue is retained V1 compatibility/runtime code. | Historical local-queue failures remain real retained-surface risk; no replacement scheduler built. |
| Book vs evaluation ledger | Same Ledger implementation with distinct explicit CAPITAL/EVALUATION domains; evaluation cannot change authoritative bankroll. | Retained cross-ledger identity/isolation attacks remain; no third ledger introduced. |
| Book outcomes vs LearningStore vs scientific feedback | Book owns accounting; LearningStore owns V1 lessons; scientific memory owns scoped research facts and V2 epoch release policy. | End-to-end convergence unqualified; lessons are not silently promoted to evidence. |
| Generated status inventory vs test suite | Fresh package-aware discovery owns the count. STATE/CHIEF_BRIEF are generated projections. | Regenerated after added tests; final exact-head check repeats freshness. |

SECOND_TRUTH_BLOCKERS is not asserted zero. Native/shared identity wiring, retained
historical-view integrity, incomplete guard convergence and unqualified cross-loop
transport remain explicit blockers or interface questions. Reusing a hash field
does not prove two owners mean the same thing.
