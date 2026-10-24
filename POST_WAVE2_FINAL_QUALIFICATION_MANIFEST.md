# GIGA Q qualification manifest

Mission disposition: **NOT_QUALIFIED / BLOCKERS_REMAIN**.

Base: `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.
Branch: `builder/giga-q-final-whole-system-hardening-20261023`.
North Star blob: `a328b4e6d7d71dafd532938888ebf9818b1b610f`.

The six root matrices/manifests describe presence, bounded depth, handoffs,
canonical owners, demonstrated repairs and limits separately. They are not a
scientific verdict or evidence of profitable edge. No final release SHA is emitted.

## Exact-head procedure

`scripts/qualify_giga_q.py --output-dir /tmp/giga-q-final --verify-remote` records
the exact HEAD/tree, supplied base ancestry, North Star identity, clean worktree,
remote branch match, command results and remaining attack failures. It runs:

- focused Q repaired-surface tests;
- complete root unittest and pytest suites in separate processes;
- complete Research OS unittest and pytest suites (includes Wave1, Wave2,
  cross-lane, runtime and crash/replay cases);
- Live Lab JavaScript tests;
- generated schemas/status freshness and V1 deterministic demo;
- closed authority/Control Plane policy proof;
- the full retained V corpus against that same HEAD in a disposable checkout;
- final exact HEAD, clean tree and optional remote equality checks.

The ordinary and attack suites have separate results. Full mission regression
cannot PASS while mandatory retained attacks are unresolved. The final receipt
contains the actual failure counts and case index; no result is inherited from
Wave2 or a parent commit. A nonzero exit is an intentional truthful qualification
failure when attacks or invariant checks fail, not an approval request.

Git cannot embed its own final commit SHA. The exact-head receipt and GitHub
Actions run/artifacts are the non-circular binding for the commit containing this
manifest. `.github/workflows/giga-q-final-qualification.yml` executes the same
procedure on this branch and uploads evidence even when qualification fails.

## Qualification limits and blockers

Tracked unresolved blockers: B01 production proposal-to-Discovery lineage is not
established; B02 native/shared economic wire binding is unresolved; B03 the full
retained hostile corpus needs semantic triage and further repairs. These are
qualification findings, not runtime state. The qualification receipt carries the
same explicit blocker IDs. Deployed/live or Capital work being deferred does not
by itself turn an expected authority boundary into a new implementation defect.

| Gate | Current disposition |
| --- | --- |
| Repaired-surface falsifications | Focused and neighboring checks pass; exact final rerun remains authoritative. |
| Horizontal completeness | Partial capabilities and unqualified production/wire handoffs remain; zero blockers not proved. |
| Vertical depth | Full retained attack corpus does not pass; whole-module D3/D4 not proved. |
| Longitudinal continuity | Specific seams repaired; complete source-to-memory cycle and Research-to-Capital transport not qualified. |
| Second truth | Owners identified; native/shared binding and retained view/guard gaps remain. |
| Full regression | Determined from exact-head receipt; passing ordinary tests cannot conceal attack failures. |
| Host / remote Site / reboot | UNEXECUTED; no deployment or economic action performed. |
| Safe for post-Wave2 convergence | FALSE while these blockers remain. |

No zero-violation whole-system assertion is emitted. Engineering tests inject
synthetic prohibited payloads to prove rejection; they do not access market outcomes.
The canonical economic/prospective/capital/live flags remain FALSE, outcome access
remains closed, and no runtime/economic operation is authorized by this work.
