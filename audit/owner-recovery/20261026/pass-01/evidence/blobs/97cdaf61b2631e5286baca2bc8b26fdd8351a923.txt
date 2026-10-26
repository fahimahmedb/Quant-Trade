# GIGA Q repair manifest

Immutable base `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.
Only reproduced defects were repaired. All tests use metadata, fakes or disposable
state/Git repositories; no economic experiment or live action was authorized.

| ID / axes | Minimal pre-repair witness | Canonical truth | Small semantic repair / regression |
| --- | --- | --- | --- |
| Q01 L/V | Self-rehashed handoff changes claim ceiling/readiness, recasts a valid BLOCK as promotable, or adds future returns | Upstream C0 adjudication and W1 references | Existing bridge validates promotability, copied upstream values, cross-owner Candidate identity and canonical outcome law. `test_giga_q_truth_continuity.py`. |
| Q02 V/L | Removing explicit FALSE/consumption evidence from EconomicIdentityRef or PortfolioReadinessRef still validates after rehash | Canonical reference producer emits explicit closed evidence | Existing D0 adapter requires that evidence rather than inferring FALSE from absence. Historical kernel source remains unchanged. |
| Q03 V/L | Case-alternate semantic role, opaque nested object, or tuple-held future-return/authority payload passes a pre-outcome boundary | Canonical Factory outcome membrane | Normalize semantic field inspection without key-order masking; refuse uninspectable objects; passive ledger consumes canonical membrane; existing V2 export/pipeline scans tuples. Safe provenance and UNKNOWN positive controls retained. |
| Q04 L/V | Canonical memory screen returns review/protocol/blocker/scoped-negative/validation refusal but spine executes downstream | Canonical memory screen disposition | Existing spine admits only its explicit clear state; keeps refusal reason and BLOCKED receipt. Based on V LONGITUDINAL_001 attack class. |
| Q05 H/V | Unknown/missing/future task status is treated as empty; legitimate FAILED is uncounted | ResearchTask status contract, existing refill owner | Unknown bucket and fail-closed refusal; FAILED included in terminal accounting. No task identity/store/lease added. H001/H002 re-proved on Wave2. |
| Q06 V | Scientific ledger exports caller aliases, accepts malformed chains, races append sequence/hash, and truncates on publication failure | Existing AppendOnlyHashLedger | Detached inputs/returns, strict ledger-local validation, serialized append/verify/publication, atomic durable JSONL staging and cleanup. Shared historical hash compatibility preserved. 20 red cases before repair; 22 focused cases pass afterward. |
| Q07 V/L | Four noncanonical Git path spellings can return commit acknowledgement without the intended exact file | Existing Git transaction path/ref CAS law | Reject noncanonical spelling/trailing directory before Git mutation; valid write and stale-blob controls retained. Four red cases then six pass. |
| Q08 V/L | Negative scope/identity/reason accepts absent/UNKNOWN/non-text values; malformed scope containers accepted; epoch/trial/negative/export hashes drift when rebuilt from serialized output | Existing V2 builders and explicit negative scope | Validate scoped values/container types; exclude each builder's own derived hash during reconstruction. No new identity scheme. `test_giga_q_negative_memory.py`, `test_giga_q_core_identity.py`. |
| Q09 V/L | Terminal observation receipt accepts a different canonical generation, a non-forward sequence, or truncated provenance | Canonical source event/session/generation and source commit | Existing receipt validator requires complete terminal provenance and same generation with forward sequence. No stale start replay or remote ACK invention. |
| Q10 L | Metadata-only frozen instrument/universe/entry-clock declarations disappear; conflicting horizon can return READY | Bound frozen execution protocol and unchanged Candidate identity | Existing synthetic readiness path derives planned execution fields from verified protocol; preserves Candidate hash and adds frozen protocol provenance; conflicts block. Positive fixture aligned with its own declaration; separate mismatch test retained. Historical H-C1 L001 re-proved. Documentary identities retain exact dossier reconstruction and their original claim ceiling; that declaration handoff remains partial. |
| Q11 V/qualification | Exact-base Mega E CI fails three module imports with `ModuleNotFoundError: pytest` | Existing test dependency and qualification workflow | Add missing dependency installation to that existing workflow. Baseline run `39882531036`, job `120183033112`; no product authority changed. |
| Q12 H/L | Actual PASS/PARK/BLOCK/UNKNOWN implementability records and frozen/null protocol bodies fail their published auxiliary JSON Schema | Existing producer outputs and auxiliary wire contract | Extend the existing schema to represent actual bounded fields/states, retaining closed authority/mutation constraints and no undeclared fields. Ten red cases then eleven focused cases pass; full Draft 2020-12 validation. Re-proves H-C1 H003/H004, without copying old repairs. |
| Q13 V/qualification | Legacy verifier replaces PATH and silently runs a different system Python, losing the installed test dependencies | The interpreter running the qualification owns its dependency environment | Existing verifier resolves its Python subprocess commands to `sys.executable`; an actual subprocess identity assertion is red before and green after. The separate SEC run on the prior code head exposed this at verification-artifact generation after its ordinary suites passed. |

Focused suite and neighboring seam results are recorded under
`governance/giga_q/evidence/`. Final cumulative results bind to exact HEAD through
the qualification script/CI receipt, not a parent's PASS.

## Historical evidence pins

- H convergence1: `6d9dc40b5833442c597f7e7ab8aa631b3d481e83`.
- H prewave2: `7aaeea99d51d3ab53c4d7cc2b73b67a7cee2c76f`.
- V prewave2: `92c4ee0a5e2d9387167f6deec24e7edec1c15b6d`.
- No separately named longitudinal branch was advertised during remote preflight.
  Longitudinal evidence was reacquired from H-C1's frozen-identity probe and V's
  `research/vertical_depth/20261021/LONGITUDINAL_001.json`; no nonexistent L branch
  or independent review is claimed.

Four retained V test files were copied as attack corpora, not implementation:
`test_vertical_scientific_ledger_depth.py`, `test_vertical_git_state_depth.py`,
`test_vertical_negative_memory_depth.py`, `test_vertical_core_depth.py` become
the corresponding `tests/test_giga_q_*.py` suites. Their semantics were re-proved
against the supplied base before repairs. Full unmodified V replay runs separately
on a disposable checkout of the exact final HEAD. None of the old repairs was merged.

Qualification-only dependencies are declared in `tests/requirements-giga-q.txt`.
The GIGA Q and ordinary SEC CI gates install them. Auxiliary schema tests import
the full JSON Schema validator only when executed; runtime code gains no dependency.

## Unresolved work

The complete retained V corpus has failures beyond these repaired slices, including
current source/PIT registries, frozen replay/snapshot isolation, implementability,
Red Team, portfolio, historical views, and retained Book/Desk/Learning/queue code.
Historical expectations are not automatically current law: the per-case replay
index distinguishes evidence from a root-cause verdict, and further semantic
triage/repairs are required. Do not characterize these failures as 764 independent
findings or as all being out of scope. They prevent whole-system qualification.

Research-to-Capital convergence remains explicitly deferred. Q does not implement
it to make a test green. Deployed host, Site, remote reconnect and reboot evidence
are absent, not fabricated. No GIGA F code was merged, rebased or cherry-picked.
