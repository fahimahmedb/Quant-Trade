# BRANCH DELETE-READY INDEX — 2026-09-20

Authority: Blue / Mission Control.

Status:
`DELETE_READY_INDEX = EXECUTED / CLOSED`

Purpose: single operational authority for branch refs already approved for namespace deletion. This consolidates the earlier safe batch, post-Gate strict-ancestor batch, and post-Gate absorbed-proof review.

Live verification after Gate A v3 PASS:
- total refs: **34**
- exact HEAD matches expected SHA: **34 / 34**
- unprotected branches: **34 / 34**
- missing/moved refs: **0**
- physical deletions executed: **34 / 34**
- delete-ready survivors: **0**
- execution path: authenticated admin clone / true branch deletion

Deletion removes only the branch ref. It must not be interpreted as deletion of Git objects, historical evidence, or a change in Gate/economic authority.

| Tranche | Branch | Pinned SHA |
|---|---|---|
| `FIRST_SAFE` | `autonomous-quant-rebuild` | `4af5b1dea0e1785acdf697d411153bfbf3113ad6` |
| `FIRST_SAFE` | `claude/quant-code-mandate-q0l644` | `dba6a95153006a395ea7bc739f552a9c21b9ca35` |
| `FIRST_SAFE` | `claude-config-bootstrap` | `002b9b04a2a62e26229b4fc17a39d64c109f53c6` |
| `FIRST_SAFE` | `codex/add-task-acknowledgment-and-tracking` | `5d80132da2de3d3a3525c49d09234700017dc994` |
| `FIRST_SAFE` | `codex/build-persistent-research-campaign-orchestrator` | `dc65d4918b5253949122dead09e02a4c4f60833d` |
| `FIRST_SAFE` | `codex/complete-v1-integrity-pass-for-codex` | `a5b8e5fc3a1b6aba1b43337a66e0db08822d87f0` |
| `FIRST_SAFE` | `quant-system-v1` | `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce` |
| `FIRST_SAFE` | `runtime/persistent-research-v1` | `8bc25a9ce576617a68ccd1131ed914461acccb61` |
| `FIRST_SAFE` | `tmp-ignore` | `002b9b04a2a62e26229b4fc17a39d64c109f53c6` |
| `FIRST_SAFE` | `codex/alignment-bootstrap` | `73e30782aab39fe19261c1edead9c86ea916e69c` |
| `FIRST_SAFE` | `codex/optimiser-recherche-persistente-avec-intelligence++` | `eb69d66f93081a8252bfcbfd0bc779923e9d6467` |
| `FIRST_SAFE` | `builder/research-factory-core-v2-proof-scratch` | `9097eab6e8bde2fd5307a55416e0fb0f0e9dd807` |
| `FIRST_SAFE` | `parallel/claude-wave1-economic-system-2026-09-19` | `b17b381a8fa1f6a24e6cd6f92a090b40627bfe78` |
| `FIRST_SAFE` | `claude/memoire-finance-presentation-9p2q5g` | `57a966f8239ef1e044ed6eab790ea030445a8037` |
| `FIRST_SAFE` | `claude/political-prediction-token-optimization-di47f2` | `7a0872efa595984c366dd0ed042f7cc97961aac0` |
| `FIRST_SAFE` | `claude/price-prediction-model-ykhog1` | `79572ad060120cb978c865ae5a5993cc6f3c616f` |
| `FIRST_SAFE` | `claude/nasdaq-quant-trading-model-emdbg5` | `dda7395c6b29b663434331ba4f6faf77818b23e5` |
| `POST_GATE_ANCESTOR` | `blue/d05-d07-governance-2026-09-15` | `1700611ad56104a2e4fde6ff72ce886d43a55958` |
| `POST_GATE_ANCESTOR` | `blue/handoff-memory-2026-09-15` | `c1a955316055aaf6c1b28853e21ed07e36e55f6a` |
| `POST_GATE_ANCESTOR` | `blue/p0-calendar-holiday-red-2026-09-20` | `c1ff38596a6679d4d7e1fc3437c4e0dd22c7e2fd` |
| `POST_GATE_ANCESTOR` | `blue/p0-gate-a-consolidated-2026-09-20` | `7b7529407753d9a4f2717abfd0bcebfd0861a8f4` |
| `POST_GATE_ANCESTOR` | `blue/p0-gate-a-v2-2026-09-20` | `d652d6dc9bda0c920b6ceb00437c14b904666497` |
| `POST_GATE_ANCESTOR` | `claude/quant-blue-master-2026-09-20-mogpvh` | `69884d50a01dc0c0490059ac5c7f76e886e88458` |
| `POST_GATE_ANCESTOR` | `checkpoint/blue-master-consolidated-2026-09-20` | `4db2614e419bbbaaa185dc49e12538355d33a0d2` |
| `POST_GATE_ANCESTOR` | `checkpoint/blue-master-project-2026-09-20` | `9b55e5276a03907257a867e61ab45c26356c0d36` |
| `POST_GATE_ANCESTOR` | `blue/frontier-p0-continuity-rule-2026-09-18` | `36febf41bec20c1ac83ff1070b2813b29717b431` |
| `POST_GATE_ANCESTOR` | `blue/frontier-p0-fingerprint-v1-2026-09-18` | `fab2318a5323c7ea55c35e245973e4fe5924f6e9` |
| `POST_GATE_ANCESTOR` | `blue/frontier-p0-integrity-blockers-2026-09-18` | `c1a955316055aaf6c1b28853e21ed07e36e55f6a` |
| `POST_GATE_ANCESTOR` | `blue/frontier-p0-operational-2026-09-18` | `ef4e1fe30b8f96f6dd70fa26add67d224b5edc8d` |
| `POST_GATE_PROOF_ABSORBED` | `blue/p0-direct-reconcile-fix-2026-09-20` | `dc9769b2790e724aaa281af209d822449d0bedfb` |
| `POST_GATE_PROOF_ABSORBED` | `blue/p0-gate-a-final-2026-09-20` | `19b6069e485c2e619698e235d24a6110556b1865` |
| `POST_GATE_PROOF_ABSORBED` | `builder/p0-integrity-blockers-fingerprint-v1` | `8d5dbb41559c4716e94d5290b6ae979a8b96143c` |
| `POST_GATE_PROOF_ABSORBED` | `builder/sec-form4-p0-raw-capture-v2` | `859ffafd2f31aa16e26c120def79aa8726517ed0` |
| `POST_GATE_PROOF_ABSORBED` | `codex/reprendre-mission-astra-p0-pre-t0` | `a321bfd9d77d42bb43a4fcd8b774a6eb38789179` |

## Execution result

All 34 refs listed below were revalidated after default-branch migration and then physically deleted with fail-fast exact-SHA checks.

- operator start UTC: `2026-09-20T21:22:08Z`
- post-cleanup branch count: `40`
- restricted log SHA-256: `d9500fc9ec90871d7861932e5afb9b7729f59fec87e85bff1265f7655e285070`
- durable handoff: `handoff/BLUE_REPOSITORY_HYGIENE_EXECUTION_2026-09-20.md`

The table below is now a historical execution manifest, not a list of live refs.

## Execution rule

Immediately before any physical deletion:
1. re-fetch the branch;
2. require current HEAD == pinned SHA above;
3. require branch is still unprotected;
4. require it is not the repository default;
5. require no later Blue governance document has re-promoted it;
6. delete using a true delete-ref / branch-delete operation only;
7. record the deletion result durably.

If any branch moved, became protected, became default, or acquired new authority:
`REMOVE_FROM_DELETE_BATCH / RE-REVIEW`.

Do not emulate deletion with `update_ref`, force-moving, or overwriting the branch.

## Explicit exclusions

Not delete-ready through this index:
- `claude/restaurant-stock-management-mvp-6oq43e` — explicit owner retention request on 2026-09-20;
- current Blue authority;
- frozen Gate A v3 candidate;
- final Astra v3 audit;
- canonical deployment-contract authority;
- divergent B1/B2/B3 falsifier/audit evidence;
- canonical Forward/Economic;
- product capability branches retained for later integration;
- recovery/scientific-learning/design evidence;
- current stale default branch until default migration is separately executed and verified.

## Source documents

- `governance/BRANCH_DELETE_BATCH_2026-09-20.md`
- `governance/POST_GATE_A_BRANCH_DELETE_BATCH_2026-09-20.md`
- `governance/POST_GATE_A_PROOF_REF_REVIEW_2026-09-20.md`

This index supersedes those documents only as the **operational delete-ready list**; their reasoning/evidence remains historical support.
