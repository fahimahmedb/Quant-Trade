# NO-IMPORT DELETE-READY CANDIDATES — 2026-10-20

Authority: CP12 deep organizational audit.

Status:

`SEMANTIC_IMPORT_REQUIRED = FALSE` for the refs listed below, based on strict ancestry or exact duplicate-ref proof.

`PHYSICAL_DELETION_AUTHORIZED = FALSE`.

This file does not grant destructive Git authority. It identifies the first branch refs whose removal should not require a capability/scientific-memory/Owner-decision migration step before an eventual Owner-executed cleanup.

## Acceptance rule

A ref may enter this list only when one of these has been independently observed:

1. its exact tip is a strict ancestor of a retained descendant and no unique semantic role remains at the branch-ref level; or
2. another retained/reviewed branch ref points to the exact same commit SHA.

Every ref must be rechecked immediately before eventual deletion because concurrent work can move branches.

---

## A. Verified absorbed Research OS refs

These were previously verified as strict ancestors of the retained modern Oracle lineage:

| Branch | Disposition | Witness |
|---|---|---|
| `builder/research-os-autonomous-loop-20261015` | `ABSORBED_REF_DELETE_READY` | modern Oracle lineage |
| `builder/research-os-autonomous-econ-readiness-port-20261016` | `ABSORBED_REF_DELETE_READY` | modern Oracle lineage |
| `builder/research-os-econ-readiness-activation-20261017` | `ABSORBED_REF_DELETE_READY` | modern Oracle lineage |
| `builder/econ-test-flow-ust-auction-20261019` | `ABSORBED_REF_DELETE_READY` | modern Oracle lineage |

Their material commits remain reachable through the retained descendant lineage. They do not require a new semantic import step solely for branch-ref retirement.

---

## B. Verified Claude WIP strict ancestors

GitHub compare results on 2026-10-20:

### `claude/new-session-3ujgeu-wip-h002`

- witness: `claude/new-session-3ujgeu`
- compare status: descendant ahead by 12, behind by 0
- merge base equals WIP tip `1903aed7212cda271948b42f5b446a1b1bb11ac8`
- disposition: `ABSORBED_REF_DELETE_READY`

### `claude/new-session-3ujgeu-wip-h004`

- witness: `claude/new-session-3ujgeu`
- compare status: descendant ahead by 5, behind by 0
- merge base equals WIP tip `fd1d2e1e09d6acc82667ac2bb163d3ccd089dc89`
- disposition: `ABSORBED_REF_DELETE_READY`

### `claude/new-session-3ujgeu-wip-h006`

- witness: `claude/new-session-3ujgeu`
- compare status: descendant ahead by 12, behind by 0
- merge base equals WIP tip `bc9974d36eb1d90c11ca632cba0646114ec3c9b3`
- disposition: `ABSORBED_REF_DELETE_READY`

Important caveat: `claude/new-session-3ujgeu` itself contains material fast-rail/data/research history and is NOT classified here as delete-ready. This file only classifies the three WIP ancestor refs.

---

## C. Verified exact duplicate Live Lab refs

The following refs point to exactly the same commit:

`6076774f52ca2e619caaab57fb6a278f47608349`

- `builder/live-lab-3d-full-build-20261015`
- `builder/live-lab-owner-ux-rebuild-20261015-checkpoint`
- `builder/live-lab-owner-ux-rebuild-20261015-checkpoint-2`

The 3D branch is still retained for Live Lab capability reconciliation. Therefore the two checkpoint aliases add no unique commit reachability.

| Branch | Disposition | Exact witness |
|---|---|---|
| `builder/live-lab-owner-ux-rebuild-20261015-checkpoint` | `REDUNDANT_REF_DELETE_READY` | `builder/live-lab-3d-full-build-20261015@6076774f...` |
| `builder/live-lab-owner-ux-rebuild-20261015-checkpoint-2` | `REDUNDANT_REF_DELETE_READY` | `builder/live-lab-3d-full-build-20261015@6076774f...` |

This does NOT declare the 3D capability obsolete. Only the two duplicate names are redundant.

---

## D. Current first safe retirement batch

`NO_IMPORT_DELETE_READY_COUNT = 9`

Refs:

1. `builder/research-os-autonomous-loop-20261015`
2. `builder/research-os-autonomous-econ-readiness-port-20261016`
3. `builder/research-os-econ-readiness-activation-20261017`
4. `builder/econ-test-flow-ust-auction-20261019`
5. `claude/new-session-3ujgeu-wip-h002`
6. `claude/new-session-3ujgeu-wip-h004`
7. `claude/new-session-3ujgeu-wip-h006`
8. `builder/live-lab-owner-ux-rebuild-20261015-checkpoint`
9. `builder/live-lab-owner-ux-rebuild-20261015-checkpoint-2`

## E. Required pre-delete recheck

Before Owner eventually removes any ref in this batch:

- fetch/prune current remote refs;
- bind exact current branch tip;
- for `ABSORBED_REF_DELETE_READY`, re-prove `merge-base --is-ancestor` against the named retained witness/descendant;
- for `REDUNDANT_REF_DELETE_READY`, re-prove exact SHA equality and ensure at least one intended witness ref remains;
- refuse deletion if the candidate moved since this audit.

No archive tag is scientifically necessary for these nine refs solely to preserve reachability, because the exact commits are already reachable from retained refs. An Owner may still choose archive tags for operational convenience.