# CURRENT PROJECT STATE — 2026-10-31

Status: **ACTIVE CONTROL TOWER ROUTER — evidence-bound navigation, not autonomous runtime authority**.

`QUANT_NORTH_STAR.md` remains the highest-level product specification.

This file supersedes `governance/CURRENT_PROJECT_STATE_2026-10-20.md` **for current mission selection only**. The 2026-10-20 router is retained intact as historical recovery/navigation evidence and must not be silently rewritten.

LAST_VERIFIED_AT: 2026-10-31.
LAST_VERIFIED_REF: default branch `blue/master-v2-2026-09-20` at `42affc56635b9dc7de411b544f657f98967f2371` before this Control Tower reconciliation sequence; each active subject below is separately bound to its exact ref/SHA/run where known.
OBSERVATION_METHOD: GitHub issue/PR comment histories and remote metadata for #36, #38, PR #39, #42, #43, #44 and PR #46; exact commit comparison; PR diffs/file lists; GitHub Actions run metadata/logs; read-only Quant-Trade Lab status. Chat/conversation summaries were treated only as navigation hints, never as primary proof.

## Current mission

**Finish and qualify the system-level autonomous continuity path before opening any new economic hypothesis, economic outcome, prospective scientific exposure or capital/trading authority.**

Target operating loop:

`EXISTING SCHEDULER -> GPT-OSS ON VM -> READ DURABLE STATE -> SELECT BOUNDED ACTION -> DISPATCH CODEX -> OBSERVE CAUSALLY BOUND RESULT + EXACT-HEAD CI + FRESH REVIEW -> GPT-OSS DECIDES NEXT ACTION -> REPEAT`

Required normal-path result:

- `HUMAN_RELAUNCHES = 0`
- `HUMAN_ROUTING_DECISIONS = 0`
- no duplicate workers/PRs/commits for the same lease;
- no stale-head mutation;
- no self-approval presented as independent review;
- restart/retry/recovery is bounded and durable;
- no second scheduler/daemon unless the existing scheduler is proven insufficient.

`READY_FOR_SCIENCE` remains **NO** until the system itself is complete and qualified. This mission is non-economic.

## Reconciled program state

| Subject | Current classification | Primary evidence / limits | Next bounded action |
|---|---|---|---|
| Pass-B / C0 foundation | **VERIFIED base identity; no global promotion inference** | Pass-B post-disclosure ref `c081a05692e81ad0b999bf46d5f8988649aa7d24`; C0 repair/qualification branch head `13721384fe5b94b0136fb4548192e05d5e34e605`. C0 was reclassified as a counting/representation defect, not a scientific-independence failure. | Reuse as immutable basis for later lanes; do not rerun C0 or infer system readiness from it. |
| Bounded autonomous continuity / issue #38 | **HISTORICAL BOUNDED TERMINAL: WP2 CLOSED IN SYNTHETIC ENGINEERING SCOPE; WP1 PARKED; WP3 TECHNICAL CANDIDATE ONLY** | #38 first proved the exact-base narrow gap `NO_EXISTING_SINGLE_LINEAGE_LEASE_EXECUTION_EVALUATOR_SINK_ROUTE`, then drove the narrow synthetic binding rather than building a new control plane. Final #38 state `BAO-20261030-WP2-CLOSED-01` records WP2 closed in synthetic engineering scope, WP1 still parked, WP3 exact hosted technical candidate only, global join inadmissible. Historical critical-path conclusion there was WP1 as sole global-join blocker; that conclusion is preserved as historical program state, but the later Owner decision in #44 supersedes it for **current mission selection** by requiring full system autonomy qualification before science/economics reopen. | Do not reopen #38 WP2 implementation absent contradictory evidence. Use its bounded proof/review lineage as historical evidence while following the newer system-autonomy mission. |
| WP1 real-science witness / issue #36 | **PARK / BLOCK_EVIDENCE_ABSENT_OR_UNRECOVERED** | Historical BitMEX Swagger receipt exists, but exact bytes/source admissibility/PIT contract were not recovered/qualified. Historical trial rerun remains forbidden. No live probe, no successor execution. | Reopen only on exact offline historical source evidence or a legitimate policy/right-resolution path, and only after the current system-autonomy mission permits science to reopen. |
| WP2 autonomy-lineage / #38 + PR #39 + #42 | **SYNTHETIC CAUSALITY PASS; INDEPENDENT IMPLEMENTATION REVIEW PASS AT `d40053…`; HOSTED EXACT-HEAD PASS AT `8f8df47…`; FRESH EXACT-HEAD REVIEW RECEIPT NOT PRESENT** | #38/PR #39 records independent review id `5709575146` on `d40053bd112164826273a866199e2941259919b0`; review found a real mutable-aliasing receipt defect, rejected the first self-PASS, and accepted the V3 narrow repair with no product/runtime code change. Exact Git compare `d40053… -> 8f8df47d184f0f1594280bec7e9e7941962cf1c5` proves one commit only and **only `STATE.md` changed** (3 additions/5 deletions; no WP2 implementation/test code changed). Hosted run `41069767444 = SUCCESS` is bound to exact head `8f8df47…`; artifact id `12984218335`, digest `sha256:54f6dbcd66d63e337370a7dc758f25fdca94326007f7db6a948bd671bc55e5b4`. Fresh-context #42 could not access enough exact candidate/diff/artifact payload to issue a new exact-head semantic PASS, so do not fabricate an `8f8df47…` review receipt. | Preserve the impact-based lineage: implementation semantics reviewed at `d40053…`, exact compare proves only state projection changed to `8f8df47…`, and hosted CI passes at `8f8df47…`. If an exact-head fresh review is required for later integration, perform it explicitly rather than relabeling the older receipt. |
| Autonomous continuity design / issue #43 | **DECISION RECORDED** | Root defect classified as orchestration/liveness gap, not missing Quant control plane. `IMPORTANT_DECISION != OWNER_GATE`. Normal engineering should run inside a pre-authorized envelope. Only four boundary classes are nondelegable: real-capital/live-trading expansion; first irreversible unblinding/prospective outcome access; frozen protocol/denominator/endpoint/lineage redefinition; irreversible external mutation outside signed envelope. | Keep liveness layer thin; use durable GitHub state + bounded workers + machine policy. Do not create a second intelligent control plane by default. |
| GPT-OSS -> Codex bridge / issue #44 + PR #46 | **REMOTE BUILT/HARDENED; FINAL HOSTED QUALIFICATION NOT PASS; NOT DEPLOYED/ACTIVE PROVEN** | PR #46 base `42affc56635b9dc7de411b544f657f98967f2371`, branch `builder/issue44-gpt-oss-codex-phase1-remote-20261030`, authoritative head `4a4af226cd5edb12b65dc72061657105544a8899`, open/draft/not merged. Current candidate reuses the existing scheduler and adds a one-step GPT-OSS orchestration hook, durable separate control-plane state, expected-head fencing, authenticated/idempotent Codex dispatch, causal result binding, policy gates, retry/PARK and adversarial tests. | Repair projection-only `STATE.md` test count `381 -> 380`, then obtain one exact-head hosted PASS before any VM activation claim. |
| PR #46 hosted qualification | **FAIL-FAST ON GENERATED STATE FRESHNESS, NOT A CODE VERDICT** | Earlier run `41158223304` reached full suite and found one environment mismatch: `tests/test_codex_policy.py` imported pytest while hosted unittest lane did not install pytest. Dependency-neutral repair produced head `4a4af226...`. Exact-head run `41181780415` then passed fail-closed SEC + schema drift but failed `Status artifact freshness`: committed `STATE.md` says 381 tests, fresh generator says 380. Full downstream suite/artifact therefore skipped. | Regenerate only the projection, verify no unrelated semantic change, then rerun exact-head gate. |
| Existing VM/lab scheduler | **EXISTS / CONFIGURED; CURRENT AGENT INACTIVE** | Read-only Lab observation 2026-10-31: `scheduler.enabled=true`, `mode=existing_autonomous_research_worker`, lab head `68bbab8ec990c813310224bc8737c41480853108`; `agent.status=RECOVERY_NEEDED`, `agent.active=false`, `current_prompt_run_observed=false`, `unattended_independence_verified=false`; last observed backend run remains 2026-10-11. | After PR #46 exact-head qualification + independent review, install/connect on the actual existing VM path and prove exact deployed identity/config/permissions. Do not build another scheduler. |
| Real GPT-OSS -> Codex -> GPT-OSS loop | **NOT PROVEN** | Repository code and synthetic/adversarial tests are not runtime proof. No fresh receipt demonstrates GPT-OSS on the actual VM waking Codex, reading the returned exact result and independently making the next decision over multiple wakes. | Execute a bounded synthetic multi-wake runtime qualification after deployment; include stale-head, duplicate, retry/recovery and reviewer-fallback cases. |
| Temporary nighttime Chat watcher | **FALLBACK ONLY; NOT TARGET ARCHITECTURE / NOT AUTONOMY PROOF** | Eight hourly ChatGPT recovery wakes helped maintain #44/#46 continuity while the real VM loop was absent. They were human/Chat infrastructure, not GPT-OSS-owned continuation. | Do not count them toward `HUMAN_RELAUNCHES=0`; retire/ignore for final autonomy claim. |
| C1-C4 deeper enforcement program | **PARKED** | Historical defects remain recorded; they are not erased. They should not trigger a new security architecture unless a concrete current seam depends on them. | Reopen only on a decision-changing concrete defect. |
| New economic/scientific work | **FROZEN** | Owner decision during #44: complete/qualify the system first. Existing historical scientific records remain immutable; no new hypothesis selection/execution should be coupled to the autonomy build. | Reopen only after system-level autonomy is qualified, then separately satisfy scientific authority/admissibility. |

## Architectural synthesis — #43 versus #44

A material design tension was recovered from GitHub and must remain explicit:

- #43 concluded that a **new persistent intelligent supervisor / second Quant control plane was not justified**. The preferred architecture was a thin liveness mechanism, durable GitHub state and bounded Codex workers inside a pre-authorized envelope.
- #44 later asked to exploit the **already-existing GPT-OSS worker** as a low-cost reasoning/orchestration layer capable of inspecting state, dispatching Codex, observing results and choosing the next action.

Current reconciliation: **these are compatible only if the existing scheduler remains the wake/liveness source and GPT-OSS performs one bounded reasoning/orchestration step per wake.** PR #46 follows that pattern. It must not silently become a second daemon/scheduler or a new top-level control plane.

## Important durability and evidence lessons recovered from the threads

1. **Codex local SHA != remote durability.** Multiple #44 invocations produced local commits / `make_pr` metadata that disappeared with ephemeral workspaces. A claim is durable only when exact bytes/commit/ref are actually present on GitHub or in another verified durable store.
2. **Transport-first recovery was required.** When Codex had no remote, the only reliable bridge was to persist exact file bytes/hashes in the issue response and materialize them remotely from an authenticated environment.
3. **Environment blockers are scoped.** `Codex container cannot access VM/GitHub` is not a project-global impossibility when another trusted lane can provide evidence or perform the bounded remote action.
4. **PR body prose may be stale.** Resolve the actual PR `head.sha`, remote files and exact-head workflow runs; do not trust a head SHA printed earlier in the PR description.
5. **Independent review must be identity/impact aware.** #38/PR #39 has a real independent implementation review PASS at `d40053…`. Exact Git compare proves `8f8df47…` changes only `STATE.md`, so implementation semantics are unchanged, while the hosted exact-head PASS belongs to `8f8df47…`. This supports impact-based lineage but does **not** manufacture a fresh exact-head review receipt that #42 could not independently establish.
6. **Built != qualified != deployed != active != used.** PR #46 is remotely built; its final exact-head hosted qualification is not PASS; actual VM deployment and unattended use are not proven.
7. **Nighttime Chat relaunches are not GPT-OSS autonomy.** They preserved work but cannot satisfy the desired zero-human-relaunch system claim.
8. **Generated state drift can mask the real code verdict.** PR #46 has repeatedly failed fast on `STATE.md` test-count freshness; record this separately from code/test semantic failures.
9. **Scientific Control Tower state is not program-governance storage.** Do not write program-management reconciliation into `research/edge_lab/STATE.json` or other protected scientific history merely to make the dashboard look current.
10. **Historical critical path can be superseded without being erased.** #38 terminally identified WP1 as the sole global-join blocker under the then-bounded Pass-B program; the later Owner decision in #44 deliberately changed the current mission to full system-autonomy completion before science/economics. Preserve both with dates/scope instead of rewriting history.

## Current critical path

1. **PR #46 projection repair only** — regenerate `STATE.md` from 381 to the current 380-test inventory; prove no unrelated semantic changes.
2. **Exact-head hosted qualification** — require freshness, full unit suite, SEC P0/adversarial gates, V1 E2E regression, exact-head artifact and clean-worktree checks to PASS on the same immutable head.
3. **Fresh independent exact-head review** — reviewer must be distinct from producer; exact code/patch + CI/artifact identities available to the reviewer. Reuse #38/PR39 evidence only where exact impact analysis proves unchanged semantics; do not conflate that with a new PR46 review.
4. **Real VM installation/rebind** — connect the qualified candidate to the existing scheduler/GPT-OSS worker, not a replacement scheduler. Record exact deployed SHA, model/runtime identity, service/config path, GitHub identity/permissions and rollback.
5. **Synthetic unattended runtime proof** — several sequential wakes: GPT-OSS decides -> Codex dispatch -> exact result -> GPT-OSS verifies/decides -> next dispatch; inject duplicate, stale-head, retry/recovery and reviewer-unavailable scenarios. PASS requires `HUMAN_RELAUNCHES=0`, `HUMAN_ROUTING_DECISIONS=0`, no duplicate worker, no stale mutation, no self-approval.
6. **System autonomy verdict** — only after the above may `SYSTEM_AUTONOMY_STATUS=QUALIFIED_END_TO_END` be asserted.
7. **Science/economics remain separate** — system qualification does not itself authorize economic outcomes or prospective exposure; those reopen under their own scientific authority/admissibility rules.

## Permanent authority boundary

Remain CLOSED unless changed by a later explicit Owner artifact:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE` for new experiments during the current autonomy mission;
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`;
- `REAL_CAPITAL_AUTHORIZED = FALSE`;
- `LIVE_TRADING_AUTHORIZED = FALSE`;
- real capital allocation / position sizing / order authority = FALSE.

Normal engineering decisions inside the pre-authorized envelope are not Owner gates. Owner interruption is reserved for the four nondelegable boundary classes recorded above.

## Source map / recovery order

Read in this order after interruption:

1. `QUANT_NORTH_STAR.md`;
2. this file;
3. the exact active subject and its current remote evidence;
4. older router `governance/CURRENT_PROJECT_STATE_2026-10-20.md` only for historical recovery/navigation that this file does not summarize;
5. branch-specific code/tests/evidence.

Current evidence anchors:

- issue #36: https://github.com/fahimahmedb/Quant-Trade/issues/36
- issue #38: https://github.com/fahimahmedb/Quant-Trade/issues/38
- PR #39: https://github.com/fahimahmedb/Quant-Trade/pull/39
- issue #42: https://github.com/fahimahmedb/Quant-Trade/issues/42
- issue #43: https://github.com/fahimahmedb/Quant-Trade/issues/43
- issue #44: https://github.com/fahimahmedb/Quant-Trade/issues/44
- PR #46: https://github.com/fahimahmedb/Quant-Trade/pull/46
- WP2 hosted run: https://github.com/fahimahmedb/Quant-Trade/actions/runs/41069767444
- PR46 full-suite attempt: https://github.com/fahimahmedb/Quant-Trade/actions/runs/41158223304
- PR46 latest exact-head run as of this reconciliation: https://github.com/fahimahmedb/Quant-Trade/actions/runs/41181780415

## Revalidation triggers

Reconcile before acting if any of the following changes:

- PR #46 `head.sha`;
- hosted run/review identity;
- actual VM deployed SHA/config/model/GitHub identity;
- authority envelope or any of the four nondelegable boundary classes;
- scientific exposure/admissibility state.

Remote commit/file/run/runtime receipts outrank summaries. Issue comments are durable coordination evidence but remain claims unless bound to the underlying remote object. Chat history is not project authority.
