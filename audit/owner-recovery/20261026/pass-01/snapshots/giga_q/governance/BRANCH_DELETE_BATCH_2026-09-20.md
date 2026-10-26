# BRANCH DELETE BATCH — 2026-09-20

Authority: Blue / Mission Control.

Purpose: exact, non-executable deletion batch for branch refs already classified `DELETE_NOW_SAFE` in `governance/BRANCH_CLEANUP_PLAN_2026-09-20.md`.

This file does **not** authorize force-moving refs and does not change repository history by itself.

Preconditions verified at generation time:
- open PR count = 0;
- all 18 refs below are unprotected;
- none is the current repository default;
- none is current Blue authority;
- none is the frozen Gate A v3 candidate;
- none is active Astra Gate A v3 audit;
- none is canonical Forward/Economic;
- none is an active Gate A/P0 evidence ref required during Astra.

Before actual deletion, re-fetch each branch and require that its HEAD still equals the expected SHA below. If any HEAD changed, remove that branch from the batch and re-review it.

| Branch | Expected HEAD |
|---|---|
| `autonomous-quant-rebuild` | `4af5b1dea0e1785acdf697d411153bfbf3113ad6` |
| `claude/quant-code-mandate-q0l644` | `dba6a95153006a395ea7bc739f552a9c21b9ca35` |
| `claude-config-bootstrap` | `002b9b04a2a62e26229b4fc17a39d64c109f53c6` |
| `codex/add-task-acknowledgment-and-tracking` | `5d80132da2de3d3a3525c49d09234700017dc994` |
| `codex/build-persistent-research-campaign-orchestrator` | `dc65d4918b5253949122dead09e02a4c4f60833d` |
| `codex/complete-v1-integrity-pass-for-codex` | `a5b8e5fc3a1b6aba1b43337a66e0db08822d87f0` |
| `quant-system-v1` | `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce` |
| `runtime/persistent-research-v1` | `8bc25a9ce576617a68ccd1131ed914461acccb61` |
| `tmp-ignore` | `002b9b04a2a62e26229b4fc17a39d64c109f53c6` |
| `codex/alignment-bootstrap` | `73e30782aab39fe19261c1edead9c86ea916e69c` |
| `codex/optimiser-recherche-persistente-avec-intelligence++` | `eb69d66f93081a8252bfcbfd0bc779923e9d6467` |
| `builder/research-factory-core-v2-proof-scratch` | `9097eab6e8bde2fd5307a55416e0fb0f0e9dd807` |
| `parallel/claude-wave1-economic-system-2026-09-19` | `b17b381a8fa1f6a24e6cd6f92a090b40627bfe78` |
| `claude/memoire-finance-presentation-9p2q5g` | `57a966f8239ef1e044ed6eab790ea030445a8037` |
| `claude/political-prediction-token-optimization-di47f2` | `7a0872efa595984c366dd0ed042f7cc97961aac0` |
| `claude/price-prediction-model-ykhog1` | `79572ad060120cb978c865ae5a5993cc6f3c616f` |
| `claude/restaurant-stock-management-mvp-6oq43e` | `e083cc70e3f4c2ce31ea04f4fc43be35e9549ab0` |
| `claude/nasdaq-quant-trading-model-emdbg5` | `dda7395c6b29b663434331ba4f6faf77818b23e5` |

BATCH_SIZE = 18

## Actual deletion procedure when a proper delete-ref capability is available

For every ref, independently:

1. fetch the current branch HEAD;
2. compare it with the expected SHA above;
3. verify the branch is still unprotected;
4. verify it has no newly opened PR;
5. verify it has not been promoted to current authority/evidence;
6. delete only the branch ref;
7. re-list branches and record the deletion result.

Do not delete all refs blindly if any precondition changes.

If using a human Git client, the equivalent operation is branch-ref deletion only (for example `git push origin --delete <branch>`), after the checks above.

Do not delete tags, commits, frozen candidate refs, audit branches, or canonical product leaves as part of this batch.
