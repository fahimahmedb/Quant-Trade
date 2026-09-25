# Branch Authority Registry — 2026-09-20

## 0. LATEST BLUE ROUTING DELTA — authoritative over stale rows below

Context-recovery checkpoint:
`handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md`

Live branch count after repository hygiene execution:
`40`

Current P0 routing:
- historical Gate A v3 repository PASS remains exact-SHA evidence at `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`;
- v3 target-host eligibility is `REJECTED_BY_NEW_REAL_DEFECT`;
- corrective branch `builder/p0-effective-unit-digest-stability-v4-2026-09-20` is ACTIVE Builder work;
- implementation commit: `0bdd397d7409b01529c1f958c68781499679a95e`;
- selected/frozen delivery candidate: `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- Builder branch later moved docs-only to `b10cde0dd193714346abdfe87afb841482e9b7c8`;
- implementation-head workflow `35535347844 = SUCCESS`;
- selected-delivery workflow `35536353538 = SUCCESS`;
- Blue reception = `PASS_FOR_INDEPENDENT_ASTRA_REVIEW`;
- frozen v4 = `blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf...`;
- independent Astra v4 branch dispatched.

Current P14D routing:
- `P0_CONTINUOUS_OBSERVATION_MIN = P14D` remains authoritative until explicit amendment;
- `blue/long-horizon-research-2026-09-20@7e0fae86834db7f46ecea5755faf0ac544245399` is ACTIVE GOVERNANCE-METHOD EVIDENCE for the P14D challenge, not out-of-scope;
- its exact-head workflow `35480999341 = SUCCESS`;
- the technical recommendation is hybrid evidence-based qualification, but the amendment remains draft/non-authoritative;
- final Red Team + explicit Blue amendment are required before t0.

The table below contains historical classifications written before the target-host defect and v4 dispatch. Where a row conflicts with this Section 0, Section 0 wins.


Authority: Quant North Star > durable current Blue governance > frozen candidate/audit evidence > historical refs.

This registry is descriptive governance. A branch existing does **not** make it current. Green CI does **not** imply Gate PASS. Gate A v3 repository proof is now PASS/CLOSED; target-host qualification is the active mission. Physical repository cleanup completed through the authenticated admin clone: 34/34 authorized refs deleted, 0 survivors. Execution handoff: `handoff/BLUE_REPOSITORY_HYGIENE_EXECUTION_2026-09-20.md`.

## Critical authority facts

- CURRENT_BLUE_OWNER = `blue/master-v2-2026-09-20`
- CURRENT_BLUE_HEAD_RESOLVER = `git log -1 --format=%H origin/blue/master-v2-2026-09-20 -- handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`
- FROZEN_GATE_A_V2 = `blue/p0-gate-a-v2-final-2026-09-20@db166fd04c681e67a2c6d4440828af14ef58c48c` — REJECTED.
- CANONICAL_GATE_A_V2_AUDIT = `astra/p0-gate-a-v2-independent-audit-2026-09-20@64b105f5a2cc1d798d1cf1e41e715b967c845a85` — BLOCKED, B1/B3 open, B2 closed.
- DELIVERED_GATE_A_V3_BUILDER = `builder/p0-gate-a-v3-2026-09-20@2da079d8ad75c69eb3fc2990c512735cb4bdc02b`; Builder STOPPED after final handoff and exact-head CI `35514180655 = SUCCESS`.
- FROZEN_GATE_A_V3 = `blue/p0-gate-a-v3-frozen-2026-09-20@2da079d8ad75c69eb3fc2990c512735cb4bdc02b`; historical repository disposition = PASS, but target-host eligibility is now REJECTED_BY_NEW_REAL_DEFECT.
- FINAL_GATE_A_V3_AUDIT = `astra/p0-gate-a-v3-independent-audit-2026-09-20@33995d03c8632e5c3a7b77a12b87366fb06b4d30`; independent verdict PASS; exact-head CI `35517935710 = SUCCESS`.
- BLUE_GATE_A_V3_FINAL_DISPOSITION = `handoff/BLUE_GATE_A_V3_FINAL_DISPOSITION_2026-09-20.md` => `GATE_A_V3_REPOSITORY_DISPOSITION = PASS`.
- Builder dependencies that MUST remain reachable: `c81fa1cdf93d5b08265c5f06ed0f4424bdda917f` and `345e18d94963b4fcc7063d73d1c23aff5244ca28`.
- Canonical product leaves remain immutable and paused: Forward `83521dbf...`; Economic `35dff27b...`; both currently have zero GitHub Actions runs.
- Repository default is now `blue/master-v2-2026-09-20`; migration executed and verified. Former default `claude/nasdaq-trading-model-design-h3mp4n@8fea5581...` remains preserved as a historical ref.

## Full branch registry

| BRANCH | HEAD | STATUS | ROLE / RATIONALE | SUPERSEDED_BY / DEPENDENCY | OPEN_PR | SAFE_TO_DELETE |
|---|---|---|---|---|---|---|
| `blue/master-v2-2026-09-20` | `RESOLVE_LIVE` | **ACTIVE_OWNER** | Blue V2 governance/orchestration | — | — | NO |
| `astra/p0-gate-a-v2-independent-audit-2026-09-20` | `64b105f5a2cc1d798d1cf1e41e715b967c845a85` | **CANONICAL** | Final independent Gate A v2 audit; BLOCKED | — | — | NO |
| `astra/checkpoint-gate-a-v2-independent-audit-2026-09-20` | `357b0e58bcf29832ee72976f757bc12d481c5d45` | **AUDIT_EVIDENCE** | Superseded audit checkpoint; stale CLOSED claim is evidence | astra/p0-gate-a-v2-independent-audit-2026-09-20 | — | NO |
| `astra/p0-deep-adversarial-pre-t0` | `643deacdf5bbbdb1d2410c762eb20f72aff16bbf` | **AUDIT_EVIDENCE** | P0 pre-t0 hardening/deployment isolation authority | — | — | NO |
| `astra/p0-deep-adversarial-2026-09-19` | `816b999832d3ebf8d5d535981f232147a2a257f9` | **AUDIT_EVIDENCE** | Earlier adversarial trail | astra/p0-deep-adversarial-pre-t0 | — | NO |
| `blue/checkpoint-gate-a-v2-audit-2026-09-20` | `4678c29eb8cd22aa7ef143075c6d4b68739026a3` | **AUDIT_EVIDENCE** | Originates R1-R5 before formal Astra branch | astra/p0-gate-a-v2-independent-audit-2026-09-20 | — | NO |
| `blue/p0-gate-a-v2-final-2026-09-20` | `db166fd04c681e67a2c6d4440828af14ef58c48c` | **REJECTED** | Frozen Gate A v2 input; exact-head CI green but audit BLOCKED | builder/p0-gate-a-v3-2026-09-20 | — | NO |
| `builder/p0-gate-a-v3-2026-09-20` | `2da079d8ad75c69eb3fc2990c512735cb4bdc02b` | **DELIVERED / AUDITED** | Gate A v3 Builder delivery; exact-head CI 35514180655 SUCCESS; independently audited PASS | blue/p0-gate-a-v3-frozen-2026-09-20 | — | NO |
| `builder/p0-effective-unit-digest-stability-v4-2026-09-20` | `b10cde0dd193714346abdfe87afb841482e9b7c8` | **DELIVERED / POST_DELIVERY_DOCS** | Corrective implementation at 0bdd397d; Blue-selected delivery candidate is 4d06bdbf with CI 35536353538 SUCCESS; live Builder ref later moved only to record that CI in handoff docs | blue/p0-gate-a-v4-frozen-2026-09-20 | — | NO |
| `blue/p0-gate-a-v3-frozen-2026-09-20` | `2da079d8ad75c69eb3fc2990c512735cb4bdc02b` | **HISTORICAL_REPOSITORY_PASS / TARGET_HOST_REJECTED** | Preserve exact repository-PASS evidence; new target-host REAL_DEFECT forbids further v3 qualification starts | corrective v4 Builder | — | NO |
| `blue/p0-gate-a-v4-frozen-2026-09-20` | `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072` | **FROZEN_V4_AUDIT_INPUT** | Exact Blue-selected v4 delivery candidate; exact-head CI 35536353538 SUCCESS; immutable input to independent Astra review | Astra v4 independent audit | — | NO |
| `astra/p0-gate-a-v4-independent-audit-2026-09-20` | `RESOLVE_LIVE` | **ACTIVE_INDEPENDENT_AUDIT** | Independent v4 Red Team branch created exactly from frozen 4d06bdbf; mission contract committed at b636a04b | handoff/ASTRA_GATE_A_V4_MISSION_2026-09-20.md | — | NO |
| `astra/p0-gate-a-v3-independent-audit-2026-09-20` | `33995d03c8632e5c3a7b77a12b87366fb06b4d30` | **FINAL_AUDIT_EVIDENCE** | Independent Astra Gate A v3 audit PASS; exact-head CI 35517935710 SUCCESS; audit-only delta over frozen candidate | handoff/ASTRA_GATE_A_V3_INDEPENDENT_AUDIT_2026-09-20.md | — | NO |
| `blue/p0-calendar-direct-reconcile-red-2026-09-20` | `c81fa1cdf93d5b08265c5f06ed0f4424bdda917f` | **AUDIT_EVIDENCE** | Original unredirected B1 reconcile() discriminant; Builder dependency | — | — | NO |
| `blue/p0-manual-probe-red-2026-09-20` | `efbf72484e5e6873aba2446d53a728798b3f453f` | **AUDIT_EVIDENCE** | Tip weakened, but parent 345e18d9 contains original collector.poll() discriminant; Builder dependency | — | — | NO |
| `blue/p0-audit-authority-red-2026-09-20` | `ca0f6b00c3e88e2a6e6d541ad538a529bfb57aee` | **AUDIT_EVIDENCE** | B2 red evidence now closed in v2 | blue/p0-gate-a-v2-final-2026-09-20 | — | NO |
| `blue/p0-audit-authority-fix-2026-09-20` | `a98bc8aef3a397c054a3df495f14a781b1b939de` | **SUPERSEDED** | B2 fix content absorbed into v2 | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-manual-operator-provenance-fix-2026-09-20` | `927f496a58fe71ffbaa6cce4df5297fe9638d0bb` | **SUPERSEDED** | Alternative B3 fix; not canonical | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-manual-probe-fix-2026-09-20` | `a6924958e88c8f3f4ad38caa2c45bf8db9309116` | **SUPERSEDED** | Partial B3 fix; still incomplete | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-calendar-dst-proof-2026-09-20` | `99a64981b7f3c5e8755782d68d52cb7c7408e764` | **REFERENCE_ONLY** | DST edge proof; not a current blocker | — | — | REVIEW_AFTER_BUILDER |
| `blue/p0-continuity-qualification-2026-09-20` | `3dfc54a4219f1b31374ff4a007f1d9a2dfc0ec4c` | **STALE** | Historical fork/common ancestor; no current authority | — | — | REVIEW_AFTER_BUILDER |
| `blue/p0-gate-a-v2-staging-2026-09-20` | `fd2e0f3b546fa8ad8e67a8368eb6a9a2543c81dc` | **SUPERSEDED** | Rival staging consolidation; not selected | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-gate-a-long-history-2026-09-20` | `d79387f06821e2c0c4d345d7d42d05200ac384d3` | **REFERENCE_ONLY** | Long-history/stress proof; not one of current Gate blockers | — | — | REVIEW_AFTER_BUILDER |
| `parallel/claude-forward-data-2026-09-20` | `83521dbfdd90027c90d04adfb7d814593c2355c5` | **CANONICAL** | Canonical Forward leaf input; frozen pending later CI qualification | — | — | NO |
| `parallel/claude-economic-v2-2026-09-20` | `35dff27b8fac53618da434ee6d31febbddcc0e69` | **CANONICAL** | Canonical Economic leaf input; frozen pending later CI qualification | — | — | NO |
| `blue/forward-finalization-2026-09-20` | `d209348159c44ba4eac9c0a1999e04f0e96e7108` | **DIVERGED** | 2 ahead / 2 behind canonical Forward; smoke-workflow concept only | parallel/claude-forward-data-2026-09-20 | — | ONLY_AFTER_BUILDER_AND_INDEX |
| `blue/integration-readiness-2026-09-20` | `37e9f95f3e24be78b1cb61ab35244b2880988b12` | **FROZEN_INPUT** | Future product-integration topology reference; execution paused | — | — | NO |
| `blue/long-horizon-research-2026-09-20` | `7e0fae86834db7f46ecea5755faf0ac544245399` | **ACTIVE_GOVERNANCE_METHOD_EVIDENCE** | P14D challenge/hybrid qualification research; exact-head CI 35480999341 SUCCESS; amendment still draft | explicit Blue P14D amendment after final Red Team | — | NO |
| `builder/evidence-store-identity-v2` | `b8f7dffbe040753cb1e47b7f38f3ab4485e1e7ba` | **SUPERSEDED** | Old Builder C line; historical PR #15 | later P0 hardening | #15 CLOSED | REVIEW_AFTER_BUILDER |
| `builder/forward-market-recorder-v2` | `87bd049574ec41fe9d22b2ffcfdfc06ec7b7166a` | **SUPERSEDED** | Old Forward recorder Builder branch | parallel/claude-forward-data-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `builder/research-factory-core-v2` | `ca8ffe439953b063fb9d049773ce0b6245958c7d` | **SUPERSEDED** | Old research-factory Builder line | later main lineage | — | REVIEW_AFTER_BUILDER |
| `builder/sec-form4-census-v2a` | `08dcfc39b4b22e0b25e54edde7b6accbb2bc4502` | **SUPERSEDED** | Old census/product-era branch; historical PR #14 | later P0 raw-capture/hardening | #14 CLOSED | REVIEW_AFTER_BUILDER |
| `builder/sec-form4-p0-raw-capture` | `348c4e42bf4efb29d6e4135cc39b2e5ae31bf5ef` | **SUPERSEDED** | Raw capture v1 | builder/sec-form4-p0-raw-capture-v2 | — | REVIEW_AFTER_BUILDER |
| `reviewer/v1-final-red-team` | `37f298423ca4a100c1c633da2c3c6c2641d8dd8e` | **AUDIT_EVIDENCE** | Historical whole-system red-team baseline | — | — | NO |
| `parallel/codex-wave1-economic-system-2026-09-19` | `738a5879ef8634d3e08c717a2d439632fe64e1ff` | **REFERENCE_ONLY** | Historical alternate Economic comparison line | parallel/claude-economic-v2-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `recovery/claude-sec-local-20260914` | `ac37339ed31b59f2c16caed6a5e914e647006671` | **REFERENCE_ONLY** | Preserved recovery snapshot | — | — | REVIEW_AFTER_BUILDER |
| `claude/nasdaq-trading-model-design-h3mp4n` | `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce` | **STALE** | Repository default branch; 277 commits behind Blue V2 base | future explicit default-branch migration | — | REVIEW_AFTER_BUILDER |
| `codex/test` | `723a778e302b6bc96e72030ded91440f75769aba` | **STALE** | Scratch/test branch | — | — | REVIEW_AFTER_BUILDER |
| `research/design-v1` | `2da2d1b6786e9a7b1d34f94f5066dca79abf8e07` | **STALE** | Old research design branch | — | — | REVIEW_AFTER_BUILDER |
| `claude/restaurant-stock-management-mvp-6oq43e` | `e083cc70e3f4c2ce31ea04f4fc43be35e9549ab0` | **RETAIN_OWNER_REQUEST** | Explicit owner retention request; excluded from repository cleanup batch | — | — | NO |

## Current cleanup authority

Physical cleanup is governed by the newer, post-Gate documents:

- `governance/BRANCH_DELETE_BATCH_2026-09-20.md` — first 18 safe refs;
- `governance/POST_GATE_A_BRANCH_DELETE_BATCH_2026-09-20.md` — 12 post-Gate strict-ancestor refs, live-rechecked and ready;
- `governance/POST_GATE_A_PROOF_REF_REVIEW_2026-09-20.md` — 5 additional absorbed proof refs delete-ready, while divergent falsifier/audit refs remain preserved.

Executed delete-ready total after owner retention override: **34 refs**. Actual deletions executed: **34**. Survivors: **0**.

## Deletion rule

No row above is authorization to delete a branch. During independent Gate A v3 audit, destructive cleanup of Gate A evidence remains deferred. After Astra disposition, Blue must re-check exact reachability, cited SHAs, unique red/CI evidence, open-PR state, and whether the v3 regression suite durably absorbed the evidence before deleting any ref.

## Default-branch governance smell

CURRENT_DEFAULT_BRANCH = `blue/master-v2-2026-09-20`
CURRENT_DEFAULT_HEAD = `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce`
CANONICAL_PROGRAM_LINE = `blue/master-v2-2026-09-20` for governance, with frozen/audit/product refs explicitly listed above.
RISK_OF_DEFAULT_BRANCH_CHANGE = MODERATE after Gate A repository PASS because workflows, external tooling and historical reproducibility may still depend on stable refs.
DEFAULT_BRANCH_MIGRATION_REVIEW = COMPLETE / EXECUTED / VERIFIED.
INTERIM_DEFAULT = `blue/master-v2-2026-09-20` / ACTIVE.
RECOMMENDED_FUTURE_ACTION = execute migration only through an explicit repository-admin default-branch mutation after one final live recheck; never emulate it by moving refs.
