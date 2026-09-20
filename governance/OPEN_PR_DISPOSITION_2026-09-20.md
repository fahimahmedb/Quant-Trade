# Open PR Disposition — 2026-09-20

Snapshot authority: live GitHub state reconstructed by Blue V2. PR mergeability is not authority.

The active Gate A v3 Builder branch has **no PR** in this snapshot. None of the PRs below is the active Builder workflow.

| PR | TITLE | HEAD | BASE | HEAD_SHA | CURRENT_AUTHORITY_RELATION | UNIQUE_VALUE | DISPOSITION |
|---:|---|---|---|---|---|---|---|
| #7 | Build the first autonomous research vertical slice | `codex/add-task-acknowledgment-and-tracking` | `autonomous-quant-rebuild` | `5d80132d...` | pure historical ancestor of current lineage | early vertical-slice history | **CLOSED_THIS_PASS / SUPERSEDED** |
| #8 | Define persistent research runtime above the first vertical slice | `runtime/persistent-research-v1` | `codex/add-task-acknowledgment-and-tracking` | `8bc25a9c...` | historical ancestor | persistent-runtime history | **CANDIDATE_FOR_CLOSURE** |
| #9 | Add persistent research campaign orchestrator | `codex/build-persistent-research-campaign-orchestrator` | `runtime/persistent-research-v1` | `dc65d491...` | historical ancestor | orchestration history | **CANDIDATE_FOR_CLOSURE** |
| #10 | Re-center Quant on the full persistent system architecture | `quant-system-v1` | `runtime/persistent-research-v1` | `8fea5581...` | historical ancestor; same tip as stale default branch | architecture history | **CANDIDATE_FOR_CLOSURE** |
| #11 | Build a restart-safe persistent research runtime | `codex/optimiser-recherche-persistente-avec-intelligence++` | `runtime/persistent-research-v1` | `eb69d66f...` | stale/diverged one-commit line | unique historical attempt retained by branch | **CANDIDATE_FOR_CLOSURE** |
| #12 | Quant System V1 + corrective integrity pass | `claude/quant-code-mandate-q0l644` | `quant-system-v1` | `dba6a951...` | pure historical ancestor | integrity-pass history | **CANDIDATE_FOR_CLOSURE** |
| #13 | Complete Quant System V1 integrity repair | `codex/complete-v1-integrity-pass-for-codex` | `claude/quant-code-mandate-q0l644` | `a5b8e5fc...` | pure historical ancestor | repair history | **CANDIDATE_FOR_CLOSURE** |
| #14 | Quant System V1: connect all North-Star planes in persistent paper/shadow mode | `builder/sec-form4-census-v2a` | stale default branch | `08dcfc39...` | diverged / superseded by later P0 and current product leaves | old census/product implementation history | **CANDIDATE_FOR_CLOSURE / DO_NOT_MERGE** |
| #15 | Builder C: Evidence Store + PIT Security Identity | `builder/evidence-store-identity-v2` | `reviewer/v1-final-red-team` | `b8f7dffb...` | diverged / superseded by later P0 hardening | evidence-store identity history | **CANDIDATE_FOR_CLOSURE / DO_NOT_MERGE** |
| #17 | P0 pre-t0: close both capture-integrity blockers, materialize fingerprint V1 | `builder/p0-integrity-blockers-fingerprint-v1` | `blue/frontier-p0-integrity-blockers-2026-09-18` | `8d5dbb41...` | head is an ancestor of current P0/Blue lineage and remains an Astra baseline | important historical audit baseline, retained as branch | **CANDIDATE_FOR_CLOSURE / AUDIT_EVIDENCE_RETAINED** |

## Actions taken

- PR #7: closure comment posted and PR closed. Head branch retained.
- PR #8: closure comment posted, but the subsequent close mutation was rejected by the connector safety guard. It remains open and is therefore explicitly classified as CANDIDATE_FOR_CLOSURE rather than silently assumed closed.
- PRs #9-#17 above: left open in this pass. Their dispositions are unambiguous, but no need exists to force additional mutations while Gate A v3 Builder is active.
- No PR was merged.
- No PR base was changed.
- No Builder PR was created or touched.

## Closure policy for next cleanup window

After Builder reception, Blue may close the remaining candidates one by one with a concise comment naming `blue/master-v2-2026-09-20` and the relevant canonical successor. Closing a PR must never be coupled to deleting its evidence branch unless reachability is independently proven.
