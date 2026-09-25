# Open PR Disposition — 2026-09-20

Snapshot authority: live GitHub state reconstructed by Blue V2. PR mergeability is not authority.

The active Gate A v3 Builder branch has **no PR** in this snapshot. None of the PRs below is the active Builder workflow.

| PR | TITLE | HEAD | BASE | HEAD_SHA | CURRENT_AUTHORITY_RELATION | UNIQUE_VALUE | DISPOSITION |
|---:|---|---|---|---|---|---|---|
| #7 | Build the first autonomous research vertical slice | `codex/add-task-acknowledgment-and-tracking` | `autonomous-quant-rebuild` | `5d80132d...` | pure historical ancestor of current lineage | early vertical-slice history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #8 | Define persistent research runtime above the first vertical slice | `runtime/persistent-research-v1` | `codex/add-task-acknowledgment-and-tracking` | `8bc25a9c...` | historical ancestor | persistent-runtime history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #9 | Add persistent research campaign orchestrator | `codex/build-persistent-research-campaign-orchestrator` | `runtime/persistent-research-v1` | `dc65d491...` | historical ancestor | orchestration history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #10 | Re-center Quant on the full persistent system architecture | `quant-system-v1` | `runtime/persistent-research-v1` | `8fea5581...` | historical ancestor; same tip as stale default branch | architecture history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #11 | Build a restart-safe persistent research runtime | `codex/optimiser-recherche-persistente-avec-intelligence++` | `runtime/persistent-research-v1` | `eb69d66f...` | stale/diverged one-commit line | unique historical attempt retained by branch | **CLOSED_THIS_PASS / SUPERSEDED** |
| #12 | Quant System V1 + corrective integrity pass | `claude/quant-code-mandate-q0l644` | `quant-system-v1` | `dba6a951...` | pure historical ancestor | integrity-pass history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #13 | Complete Quant System V1 integrity repair | `codex/complete-v1-integrity-pass-for-codex` | `claude/quant-code-mandate-q0l644` | `a5b8e5fc...` | pure historical ancestor | repair history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #14 | Quant System V1: connect all North-Star planes in persistent paper/shadow mode | `builder/sec-form4-census-v2a` | stale default branch | `08dcfc39...` | diverged / superseded by later P0 and current product leaves | old census/product implementation history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #15 | Builder C: Evidence Store + PIT Security Identity | `builder/evidence-store-identity-v2` | `reviewer/v1-final-red-team` | `b8f7dffb...` | diverged / superseded by later P0 hardening | evidence-store identity history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #17 | P0 pre-t0: close both capture-integrity blockers, materialize fingerprint V1 | `builder/p0-integrity-blockers-fingerprint-v1` | `blue/frontier-p0-integrity-blockers-2026-09-18` | `8d5dbb41...` | head is an ancestor of current P0/Blue lineage and remains an Astra baseline | important historical audit baseline, retained as branch | **CLOSED_THIS_PASS / SUPERSEDED** |

## Actions taken

- PR #7 was already closed in the first cleanup pass.
- PRs #8, #9, #10, #11, #12, #13, #14, #15 and #17 were closed in the second cleanup pass after live head/base verification.
- Every closure received a governance comment explaining that the PR was historical/superseded.
- PR #17 was closed **without deleting its branch**; its P0 history remains retained as audit evidence during Gate A v3 Astra review.
- No PR was merged.
- No PR base was changed.
- No branch was deleted as part of PR cleanup.
- Live GitHub verification after the pass reports **0 open PRs**.

## Closure policy for next cleanup window

All historical PR containers are now closed. Future cleanup is branch-level only.

Branch deletion remains a separate, more conservative decision. During independent Gate A v3 Astra review, do not delete Gate A evidence refs, frozen candidates, audit refs, Blue authority, Builder delivery, canonical Forward/Economic leaves, or any branch carrying unique evidence. Re-check reachability and citations before every deletion.
