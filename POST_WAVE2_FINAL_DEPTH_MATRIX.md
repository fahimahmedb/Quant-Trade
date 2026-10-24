# GIGA Q depth matrix

Depths describe demonstrated slices, not whole-module labels. D0 happy path;
D1 validation; D2 replay/restart; D3 concurrency/crash/partial persistence;
D4 hostile payload/fencing/fail-closed. A D4 input guard does not prove D3 storage.

| Critical slice | Demonstrated depth | Evidence / attack | Remaining limit |
| --- | --- | --- | --- |
| Scientific ledger append/publication | D3 | Retained V tests re-proved: alias isolation, malformed chain, concurrent sequence/hash, replace failure, file/directory fsync loss | Independent-process stale publication and all power-loss boundaries not qualified. |
| Canonical Git write admission | D4 | Q retained fixture: ignored normalized paths rejected before Git acknowledgement; stale blob refusal | This is a path/CAS slice, not every remote transport failure. |
| Epoch/trial/export/negative identity rebuild | D2 | Reordered JSON, repeated construction, detached caller data, material mutation changes hash | Concurrent snapshots in other builders remain open. |
| Negative-memory admission | D4 | Empty/UNKNOWN/non-text scope/reason denied; explicit unknown context retained | Complete legacy corpus view immutability and conflicting IDs remain open. |
| Canonical Factory outcome membrane | D4 | Nested list/tuple/JSON, normalized semantic role, conflicting key order, opaque object refusal, safe provenance control | Other domain ingestion firewalls still have retained failures. |
| V2 export / pipeline tuple membrane | D4 | Tuple and JSON-equivalent array contamination both block | Full pipeline snapshot isolation remains open. |
| Passive Proposal Ledger | D4 admission / D2 snapshot | Canonical firewall plus passive operational guard; duplicates and immutable collision tests | No claim of process-durable disk storage or independent-process serialization. |
| Multi-Source barrier / source claims | D2 | Existing source crash/concurrency/replay fixtures | In-memory passive claims are not worker leases. |
| RI-to-Discovery admission | D1/D4 bounded gate | Capability mismatch, unsupported route, non-executable action, source/family laws | No production proposal lineage binding proved. |
| Candidate / frozen Factory | D2 on existing W1 slice | Registry, plan, receipt, replay and declaration binding tests | Historical frozen replay and shared-input attack failures remain; no D3/D4 module claim. |
| Auxiliary schema handoff | D1/D4 representation slice | Actual producer PASS/PARK/BLOCK/UNKNOWN and frozen/null JSON bodies validate; authority/mutation extensions reject | Wire acceptance does not prove scientific validity or grant authority. |
| Frozen declaration-to-economic view | D4 continuity guard | Q aligned positive control and conflicting horizon refusal; Candidate hash retained | Native/shared wire binding and full documentary breadth remain open. |
| C0 / scientific disposition | D1/D2 | Canonical adjudication and cross-lane tests | Supplied independent refs do not prove unlimited semantic independence. |
| Scientific-to-economic handoff | D4 | Self-rehashed copied field drift, BLOCK recast as PROMOTE, nested outcomes rejected | All upstream reference producers still need complete hostile qualification. |
| Economic/portfolio reference admission | D4 closed-state slice | Missing explicit FALSE/consumption evidence rejected | Ref hashes are integrity evidence, not signatures proving external issuer authority. |
| D0 lifecycle | D2 contract slice | Existing lifecycle/ref/review/replacement tests | Active observations and remote lifecycle operation forbidden. |
| Legacy refusal-to-spine | D4 refusal slice | Scoped-negative, protocol-repair, blocker, validation, review and future-state refusals survive handoff | Legacy source conflict/alias defects remain. |
| Queue refill accounting | D4 state slice | FAILED is terminal; unknown/missing/future task state cannot prove an empty queue | Local Campaign/Queue concurrency failures remain distinct from Git worker proof. |
| Oracle task/lease/retry | D3 bounded disposable tests | Existing worker tests inject stale generations, conflicts, restart and receipts | No actual VM reboot/dependency-outage campaign. |
| Observation receipt reconciliation | D2/D4 slice | Existing restart/duplicate/conflict fixtures; Q terminal generation/sequence/provenance tests | Host-local ACK evidence is not independently reauthenticated against a remote service here. |
| Live Lab reducer | D2/D4 bounded local slice | Native tests cover old generations, duplicate/reordered/stale events and reconnect mocks | Real remote reconnect, missing-event snapshot rebuild and outage evidence absent. |
| Data/source/PIT/evidence registry | D1/D2 bounded W1 slice | W1 tests pass on retained canonical behavior | V typed/route/acquisition/snapshot attacks remain; do not assign whole-module D4. |
| Red Team / implementability / portfolio | D1/D2 bounded slice | Existing canonical tests | Retained adversarial failures prevent deeper qualification. |
| Book / Desk / Learning | D0/D1 with selected replay checks | Existing V1 root regressions and source review | Retained concurrency, failed-save, numeric, identity replay failures block D3/D4 qualification. |

The baseline V replay is 994 cases: 230 passed, 764 failed. These are case counts,
not independent defect counts. Some fixtures assert historical interfaces; each
requires triage against current ownership before a semantic repair. Q reuses only
selected, re-proved tests and does not merge the old repairs. The final replay and
per-case index are produced on the exact final HEAD by `scripts/qualify_giga_q.py`.
Any remaining failures keep qualification closed even if ordinary suites pass.
