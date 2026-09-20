# Branch Authority Registry — 2026-09-20

Authority: Quant North Star > durable current Blue governance > frozen candidate/audit evidence > historical refs.

This registry is descriptive governance. A branch existing does **not** make it current. Green CI does **not** imply Gate PASS. No branch deletion was performed in this pass while Gate A v3 Builder is active.

## Critical authority facts

- CURRENT_BLUE_OWNER = `blue/master-v2-2026-09-20`
- CURRENT_BLUE_HEAD_RESOLVER = `git log -1 --format=%H origin/blue/master-v2-2026-09-20 -- handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`
- FROZEN_GATE_A_V2 = `blue/p0-gate-a-v2-final-2026-09-20@db166fd04c681e67a2c6d4440828af14ef58c48c` — REJECTED.
- CANONICAL_GATE_A_V2_AUDIT = `astra/p0-gate-a-v2-independent-audit-2026-09-20@64b105f5a2cc1d798d1cf1e41e715b967c845a85` — BLOCKED, B1/B3 open, B2 closed.
- ACTIVE_GATE_A_V3_BUILDER = `builder/p0-gate-a-v3-2026-09-20`; at reconstruction time its HEAD was still exactly the frozen v2 SHA.
- Builder dependencies that MUST remain reachable: `c81fa1cdf93d5b08265c5f06ed0f4424bdda917f` and `345e18d94963b4fcc7063d73d1c23aff5244ca28`.
- Canonical product leaves remain immutable and paused: Forward `83521dbf...`; Economic `35dff27b...`; both currently have zero GitHub Actions runs.
- Default branch remains `claude/nasdaq-trading-model-design-h3mp4n@8fea5581...`, 277 commits behind the Blue V2 base lineage. Do not change it during active Builder work.

## Full branch registry

| BRANCH | HEAD | STATUS | ROLE / RATIONALE | SUPERSEDED_BY / DEPENDENCY | OPEN_PR | SAFE_TO_DELETE |
|---|---|---|---|---|---|---|
| `blue/master-v2-2026-09-20` | `69884d50a01dc0c0490059ac5c7f76e886e88458` | **ACTIVE_OWNER** | Blue V2 governance/orchestration | — | — | NO |
| `claude/quant-blue-master-2026-09-20-mogpvh` | `69884d50a01dc0c0490059ac5c7f76e886e88458` | **SUPERSEDED** | Previous Blue Master authority | blue/master-v2-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `astra/p0-gate-a-v2-independent-audit-2026-09-20` | `64b105f5a2cc1d798d1cf1e41e715b967c845a85` | **CANONICAL** | Final independent Gate A v2 audit; BLOCKED | — | — | NO |
| `astra/checkpoint-gate-a-v2-independent-audit-2026-09-20` | `357b0e58bcf29832ee72976f757bc12d481c5d45` | **AUDIT_EVIDENCE** | Superseded audit checkpoint; stale CLOSED claim is evidence | astra/p0-gate-a-v2-independent-audit-2026-09-20 | — | NO |
| `astra/p0-deep-adversarial-pre-t0` | `643deacdf5bbbdb1d2410c762eb20f72aff16bbf` | **AUDIT_EVIDENCE** | P0 pre-t0 hardening/deployment isolation authority | — | — | NO |
| `astra/p0-deep-adversarial-2026-09-19` | `816b999832d3ebf8d5d535981f232147a2a257f9` | **AUDIT_EVIDENCE** | Earlier adversarial trail | astra/p0-deep-adversarial-pre-t0 | — | NO |
| `blue/checkpoint-gate-a-v2-audit-2026-09-20` | `4678c29eb8cd22aa7ef143075c6d4b68739026a3` | **AUDIT_EVIDENCE** | Originates R1-R5 before formal Astra branch | astra/p0-gate-a-v2-independent-audit-2026-09-20 | — | NO |
| `blue/p0-gate-a-v2-final-2026-09-20` | `db166fd04c681e67a2c6d4440828af14ef58c48c` | **REJECTED** | Frozen Gate A v2 input; exact-head CI green but audit BLOCKED | builder/p0-gate-a-v3-2026-09-20 | — | NO |
| `builder/p0-gate-a-v3-2026-09-20` | `db166fd04c681e67a2c6d4440828af14ef58c48c` | **BUILDER_IN_PROGRESS** | Active Gate A v3 Builder branch; currently no commit beyond frozen base | — | — | NO |
| `blue/p0-calendar-direct-reconcile-red-2026-09-20` | `c81fa1cdf93d5b08265c5f06ed0f4424bdda917f` | **AUDIT_EVIDENCE** | Original unredirected B1 reconcile() discriminant; Builder dependency | — | — | NO |
| `blue/p0-manual-probe-red-2026-09-20` | `efbf72484e5e6873aba2446d53a728798b3f453f` | **AUDIT_EVIDENCE** | Tip weakened, but parent 345e18d9 contains original collector.poll() discriminant; Builder dependency | — | — | NO |
| `blue/p0-direct-reconcile-fix-2026-09-20` | `dc9769b2790e724aaa281af209d822449d0bedfb` | **REJECTED** | Known insufficient B1 fix and test-redirection example | — | — | NO |
| `blue/p0-audit-authority-red-2026-09-20` | `ca0f6b00c3e88e2a6e6d541ad538a529bfb57aee` | **AUDIT_EVIDENCE** | B2 red evidence now closed in v2 | blue/p0-gate-a-v2-final-2026-09-20 | — | NO |
| `blue/p0-audit-authority-fix-2026-09-20` | `a98bc8aef3a397c054a3df495f14a781b1b939de` | **SUPERSEDED** | B2 fix content absorbed into v2 | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-manual-operator-provenance-fix-2026-09-20` | `927f496a58fe71ffbaa6cce4df5297fe9638d0bb` | **SUPERSEDED** | Alternative B3 fix; not canonical | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-manual-probe-fix-2026-09-20` | `a6924958e88c8f3f4ad38caa2c45bf8db9309116` | **SUPERSEDED** | Partial B3 fix; still incomplete | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-calendar-dst-proof-2026-09-20` | `99a64981b7f3c5e8755782d68d52cb7c7408e764` | **REFERENCE_ONLY** | DST edge proof; not a current blocker | — | — | REVIEW_AFTER_BUILDER |
| `blue/p0-calendar-holiday-red-2026-09-20` | `c1ff38596a6679d4d7e1fc3437c4e0dd22c7e2fd` | **SUPERSEDED** | Holiday correction absorbed into v2 lineage | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-continuity-qualification-2026-09-20` | `3dfc54a4219f1b31374ff4a007f1d9a2dfc0ec4c` | **STALE** | Historical fork/common ancestor; no current authority | — | — | REVIEW_AFTER_BUILDER |
| `blue/p0-gate-a-v2-2026-09-20` | `d652d6dc9bda0c920b6ceb00437c14b904666497` | **SUPERSEDED** | Partial/flawed v2 predecessor | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-gate-a-v2-staging-2026-09-20` | `fd2e0f3b546fa8ad8e67a8368eb6a9a2543c81dc` | **SUPERSEDED** | Rival staging consolidation; not selected | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-gate-a-consolidated-2026-09-20` | `7b7529407753d9a4f2717abfd0bcebfd0861a8f4` | **SUPERSEDED** | Misleadingly named pre-audit ancestor | blue/p0-gate-a-v2-final-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/p0-gate-a-final-2026-09-20` | `19b6069e485c2e619698e235d24a6110556b1865` | **REJECTED** | Rejected Gate A v1 exact historical candidate | blue/p0-gate-a-v2-final-2026-09-20 | — | NO |
| `blue/p0-gate-a-long-history-2026-09-20` | `d79387f06821e2c0c4d345d7d42d05200ac384d3` | **REFERENCE_ONLY** | Long-history/stress proof; not one of current Gate blockers | — | — | REVIEW_AFTER_BUILDER |
| `parallel/claude-forward-data-2026-09-20` | `83521dbfdd90027c90d04adfb7d814593c2355c5` | **CANONICAL** | Canonical Forward leaf input; frozen pending later CI qualification | — | — | NO |
| `parallel/claude-economic-v2-2026-09-20` | `35dff27b8fac53618da434ee6d31febbddcc0e69` | **CANONICAL** | Canonical Economic leaf input; frozen pending later CI qualification | — | — | NO |
| `blue/forward-finalization-2026-09-20` | `d209348159c44ba4eac9c0a1999e04f0e96e7108` | **DIVERGED** | 2 ahead / 2 behind canonical Forward; smoke-workflow concept only | parallel/claude-forward-data-2026-09-20 | — | ONLY_AFTER_BUILDER_AND_INDEX |
| `blue/integration-readiness-2026-09-20` | `37e9f95f3e24be78b1cb61ab35244b2880988b12` | **FROZEN_INPUT** | Future product-integration topology reference; execution paused | — | — | NO |
| `blue/long-horizon-research-2026-09-20` | `7e0fae86834db7f46ecea5755faf0ac544245399` | **REFERENCE_ONLY** | P14D-adjacent research; out of current scope | — | — | REVIEW_AFTER_BUILDER |
| `checkpoint/blue-master-consolidated-2026-09-20` | `4db2614e419bbbaaa185dc49e12538355d33a0d2` | **SUPERSEDED** | Prior master consolidation checkpoint | blue/master-v2-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `checkpoint/blue-master-project-2026-09-20` | `9b55e5276a03907257a867e61ab45c26356c0d36` | **SUPERSEDED** | Earlier project recovery checkpoint | blue/master-v2-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/d05-d07-governance-2026-09-15` | `1700611ad56104a2e4fde6ff72ce886d43a55958` | **SUPERSEDED** | Historical governance ancestor | blue/master-v2-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `blue/frontier-p0-continuity-rule-2026-09-18` | `36febf41bec20c1ac83ff1070b2813b29717b431` | **SUPERSEDED** | Historical P0 frontier ancestor | astra/p0-deep-adversarial-pre-t0 | — | REVIEW_AFTER_BUILDER |
| `blue/frontier-p0-fingerprint-v1-2026-09-18` | `fab2318a5323c7ea55c35e245973e4fe5924f6e9` | **SUPERSEDED** | Historical P0 fingerprint ancestor | astra/p0-deep-adversarial-pre-t0 | — | REVIEW_AFTER_BUILDER |
| `blue/frontier-p0-integrity-blockers-2026-09-18` | `c1a955316055aaf6c1b28853e21ed07e36e55f6a` | **SUPERSEDED** | Historical P0 integrity ancestor | astra/p0-deep-adversarial-pre-t0 | — | REVIEW_AFTER_BUILDER |
| `blue/frontier-p0-operational-2026-09-18` | `ef4e1fe30b8f96f6dd70fa26add67d224b5edc8d` | **SUPERSEDED** | Historical P0 operational ancestor | astra/p0-deep-adversarial-pre-t0 | — | REVIEW_AFTER_BUILDER |
| `blue/handoff-memory-2026-09-15` | `c1a955316055aaf6c1b28853e21ed07e36e55f6a` | **SUPERSEDED** | Historical handoff ancestor | blue/master-v2-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `builder/p0-integrity-blockers-fingerprint-v1` | `8d5dbb41559c4716e94d5290b6ae979a8b96143c` | **AUDIT_EVIDENCE** | Initial P0 audit baseline; historical PR #17 | astra/p0-deep-adversarial-pre-t0 | #17 OPEN / CANDIDATE_FOR_CLOSURE | NO |
| `builder/evidence-store-identity-v2` | `b8f7dffbe040753cb1e47b7f38f3ab4485e1e7ba` | **SUPERSEDED** | Old Builder C line; historical PR #15 | later P0 hardening | #15 OPEN / CANDIDATE_FOR_CLOSURE | REVIEW_AFTER_BUILDER |
| `builder/forward-market-recorder-v2` | `87bd049574ec41fe9d22b2ffcfdfc06ec7b7166a` | **SUPERSEDED** | Old Forward recorder Builder branch | parallel/claude-forward-data-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `builder/research-factory-core-v2-proof-scratch` | `9097eab6e8bde2fd5307a55416e0fb0f0e9dd807` | **STALE** | Research proof scratch | — | — | REVIEW_AFTER_BUILDER |
| `builder/research-factory-core-v2` | `ca8ffe439953b063fb9d049773ce0b6245958c7d` | **SUPERSEDED** | Old research-factory Builder line | later main lineage | — | REVIEW_AFTER_BUILDER |
| `builder/sec-form4-census-v2a` | `08dcfc39b4b22e0b25e54edde7b6accbb2bc4502` | **SUPERSEDED** | Old census/product-era branch; historical PR #14 | later P0 raw-capture/hardening | #14 OPEN / CANDIDATE_FOR_CLOSURE | REVIEW_AFTER_BUILDER |
| `builder/sec-form4-p0-raw-capture` | `348c4e42bf4efb29d6e4135cc39b2e5ae31bf5ef` | **SUPERSEDED** | Raw capture v1 | builder/sec-form4-p0-raw-capture-v2 | — | REVIEW_AFTER_BUILDER |
| `builder/sec-form4-p0-raw-capture-v2` | `859ffafd2f31aa16e26c120def79aa8726517ed0` | **SUPERSEDED** | Merged historical PR #16; absorbed into later P0 lineage | astra/p0-deep-adversarial-pre-t0 | — | REVIEW_AFTER_BUILDER |
| `reviewer/v1-final-red-team` | `37f298423ca4a100c1c633da2c3c6c2641d8dd8e` | **AUDIT_EVIDENCE** | Historical whole-system red-team baseline | — | — | NO |
| `autonomous-quant-rebuild` | `4af5b1dea0e1785acdf697d411153bfbf3113ad6` | **SUPERSEDED** | Early autonomous-research ancestor | later main lineage | — | REVIEW_AFTER_BUILDER |
| `runtime/persistent-research-v1` | `8bc25a9ce576617a68ccd1131ed914461acccb61` | **SUPERSEDED** | Early persistent-research runtime | later main lineage | #8 OPEN / CANDIDATE_FOR_CLOSURE | REVIEW_AFTER_BUILDER |
| `quant-system-v1` | `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce` | **SUPERSEDED** | Early whole-system branch; same tip as stale default | later main lineage | #10 OPEN / CANDIDATE_FOR_CLOSURE | REVIEW_AFTER_BUILDER |
| `parallel/claude-wave1-economic-system-2026-09-19` | `b17b381a8fa1f6a24e6cd6f92a090b40627bfe78` | **SUPERSEDED** | Literal ancestor/base of Economic v2 | parallel/claude-economic-v2-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `parallel/codex-wave1-economic-system-2026-09-19` | `738a5879ef8634d3e08c717a2d439632fe64e1ff` | **REFERENCE_ONLY** | Historical alternate Economic comparison line | parallel/claude-economic-v2-2026-09-20 | — | REVIEW_AFTER_BUILDER |
| `recovery/claude-sec-local-20260914` | `ac37339ed31b59f2c16caed6a5e914e647006671` | **REFERENCE_ONLY** | Preserved recovery snapshot | — | — | REVIEW_AFTER_BUILDER |
| `claude/nasdaq-trading-model-design-h3mp4n` | `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce` | **STALE** | Repository default branch; 277 commits behind Blue V2 base | future explicit default-branch migration | — | REVIEW_AFTER_BUILDER |
| `claude/quant-code-mandate-q0l644` | `dba6a95153006a395ea7bc739f552a9c21b9ca35` | **SUPERSEDED** | Historical implementation mandate; PR #12 | later main lineage | #12 OPEN / CANDIDATE_FOR_CLOSURE | REVIEW_AFTER_BUILDER |
| `claude-config-bootstrap` | `002b9b04a2a62e26229b4fc17a39d64c109f53c6` | **SUPERSEDED** | Historical config bootstrap | later main lineage | — | REVIEW_AFTER_BUILDER |
| `codex/add-task-acknowledgment-and-tracking` | `5d80132da2de3d3a3525c49d09234700017dc994` | **SUPERSEDED** | Early vertical slice; PR #7 closed this pass | later main lineage | #7 CLOSED_THIS_PASS | REVIEW_AFTER_BUILDER |
| `codex/alignment-bootstrap` | `73e30782aab39fe19261c1edead9c86ea916e69c` | **STALE** | Unmerged stale Codex branch | — | — | REVIEW_AFTER_BUILDER |
| `codex/build-persistent-research-campaign-orchestrator` | `dc65d4918b5253949122dead09e02a4c4f60833d` | **SUPERSEDED** | Historical PR #9 | later main lineage | #9 OPEN / CANDIDATE_FOR_CLOSURE | REVIEW_AFTER_BUILDER |
| `codex/complete-v1-integrity-pass-for-codex` | `a5b8e5fc3a1b6aba1b43337a66e0db08822d87f0` | **SUPERSEDED** | Historical PR #13 | later main lineage | #13 OPEN / CANDIDATE_FOR_CLOSURE | REVIEW_AFTER_BUILDER |
| `codex/optimiser-recherche-persistente-avec-intelligence++` | `eb69d66f93081a8252bfcbfd0bc779923e9d6467` | **STALE** | Diverged one-commit historical PR #11 | — | #11 OPEN / CANDIDATE_FOR_CLOSURE | REVIEW_AFTER_BUILDER |
| `codex/reprendre-mission-astra-p0-pre-t0` | `a321bfd9d77d42bb43a4fcd8b774a6eb38789179` | **SUPERSEDED** | PR #18 head merged into P0 hardening | astra/p0-deep-adversarial-pre-t0 | — | REVIEW_AFTER_BUILDER |
| `codex/test` | `723a778e302b6bc96e72030ded91440f75769aba` | **STALE** | Scratch/test branch | — | — | REVIEW_AFTER_BUILDER |
| `research/design-v1` | `2da2d1b6786e9a7b1d34f94f5066dca79abf8e07` | **STALE** | Old research design branch | — | — | REVIEW_AFTER_BUILDER |
| `tmp-ignore` | `002b9b04a2a62e26229b4fc17a39d64c109f53c6` | **STALE** | Temporary branch | — | — | REVIEW_AFTER_BUILDER |
| `claude/memoire-finance-presentation-9p2q5g` | `57a966f8239ef1e044ed6eab790ea030445a8037` | **REFERENCE_ONLY** | Unrelated historical content; no current Quant authority | — | — | REVIEW_AFTER_BUILDER |
| `claude/nasdaq-quant-trading-model-emdbg5` | `dda7395c6b29b663434331ba4f6faf77818b23e5` | **REFERENCE_ONLY** | Unrelated/legacy NASDAQ work | — | — | REVIEW_AFTER_BUILDER |
| `claude/political-prediction-token-optimization-di47f2` | `7a0872efa595984c366dd0ed042f7cc97961aac0` | **REFERENCE_ONLY** | Unrelated historical content | — | — | REVIEW_AFTER_BUILDER |
| `claude/price-prediction-model-ykhog1` | `79572ad060120cb978c865ae5a5993cc6f3c616f` | **REFERENCE_ONLY** | Unrelated historical content | — | — | REVIEW_AFTER_BUILDER |
| `claude/restaurant-stock-management-mvp-6oq43e` | `e083cc70e3f4c2ce31ea04f4fc43be35e9549ab0` | **REFERENCE_ONLY** | Unrelated historical content | — | — | REVIEW_AFTER_BUILDER |

## Deletion rule

No row above is authorization to delete a branch. During BUILDER_IN_PROGRESS, all deletion remains deferred. After Builder reception, Blue must re-check exact reachability, cited SHAs, unique red/CI evidence, open-PR state, and whether the v3 regression suite durably absorbed the evidence before deleting any ref.

## Default-branch governance smell

CURRENT_DEFAULT_BRANCH = `claude/nasdaq-trading-model-design-h3mp4n`
CURRENT_DEFAULT_HEAD = `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce`
CANONICAL_PROGRAM_LINE = `blue/master-v2-2026-09-20` for governance, with frozen/audit/product refs explicitly listed above.
RISK_OF_DEFAULT_BRANCH_CHANGE = HIGH during active Builder work because PR bases, workflows, external tooling and future agents may depend on it.
RECOMMENDED_FUTURE_ACTION = after Gate A v3 reception/Astra disposition, perform an explicit default-branch migration review; never change it as incidental cleanup.
