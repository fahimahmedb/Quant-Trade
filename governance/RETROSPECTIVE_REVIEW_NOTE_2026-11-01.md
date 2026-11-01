# Review note — rewritten cumulative retrospective

DATE=`2026-11-01`
REVIEW_SUBJECT=`governance/RETROSPECTIVE_AND_TWO_BRANCH_METHOD_2026-11-01.md@7c11cbf68ca56bee9fc29ed2412a4a6e6abbe6ab`
NON_AUTHORITY_REVIEW_NOTE=`TRUE`

## Verdict

The rewritten retrospective is materially stronger than the earlier framing. Its central causal diagnosis is useful: the dominant recurring failure was not simply branch count or insufficient reasoning, but failure to convert produced work into shared, recoverable, integrated and reusable state.

## What should be retained

- Exact bytes / exact SHA / remotely recoverable publication before claiming durable completion.
- Resumable acquisition and transferable evidence rather than session-local state.
- Access-ready review: reviewer must have the exact candidate/evidence before review starts.
- Same-lineage repair before replacement architecture.
- Decision-changing challenge only; repeated review without a new falsifier should stop.
- Statistical history must be preserved without applying one indiscriminate universal multiplicity penalty to every future family.
- Local WP2 repair may remain part of history, but must not be promoted to remotely durable/independently qualified status without proof.
- `project/canonical` + `code/canonical` remain the correct authority pair.

## Challenge / correction

The report still contains one prioritization ambiguity: documentation-entry alignment is useful cleanup, but it must not displace the current operational critical path already recorded in `CURRENT_PROJECT_STATE.md`.

Current execution priority remains:
`VM_MULTI_WAKE_PROOF_ON_AUTHENTICATED_EXISTING_HOST`

The incomplete exhaustive semantic pass (`308/423` documented union in the retrospective) is a coverage limitation, not automatically a reason to continue historical reading. Reopen only if an unread object can plausibly change a current decision, contradict a conclusion, or recover currently useful semantics.

Branch retirement is also not the current critical path. New work should use the two canonical branches; destructive cleanup remains deferred until dependencies and evidence-retention requirements are proven.

## Decision

RETROSPECTIVE_AS_DIAGNOSTIC=`ACCEPT_WITH_BOUNDED_CORRECTION`
RETROSPECTIVE_AS_EXECUTION_ROUTER=`NO`
EXECUTION_ROUTER=`governance/CURRENT_PROJECT_STATE.md`
NEXT_ACTION=`VM_MULTI_WAKE_PROOF_ON_AUTHENTICATED_EXISTING_HOST`

The main process lesson to operationalize is:
`PRODUCE -> PERSIST EXACTLY -> VERIFY RECOVERABILITY -> INTEGRATE -> CONTINUE`

Do not add more governance unless it changes a decision or prevents a demonstrated false PASS / state-loss failure.
