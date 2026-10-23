# CP038–CP100 evidence and Owner stop

These are 63 bounded audit checkpoints of test surfaces that exist on immutable
base 01c2e520fa4116645870f96acf6770ea83f1881c. They are not 63 repairs. Each
checkpoint records the exact existing adversaries and two runtime invocations;
CP038_100_INDEX.json preserves the original HEAD and test file hashes. All 126
invocations passed (714 overlapping existing tests per mode). Parent Python was
ordinary with PYTHONHASHSEED=0, then -OO with PYTHONHASHSEED=1729. Explicit child
interpreter flags in fixtures are not silently upgraded to -OO. Each optimized
invocation emits the expected pytest warning about non-test assertions.

The paired runs occurred at 97d2da61e93ac22b47a6d68be99d72efc574ba4a. CP061 then
added six deterministic input-isolation cases: five failed, one passed against
the exact previous observability module. The module was restored in a try/finally
diagnostic and repaired bytes restored immediately. CP061_before.txt names that
source; CP061_after.txt and CP061_optimized_after.txt show the post-repair focused
37-test/28-subtest runs. The repair is committed at
18beb0fb823199074a3d563e2daa1d33d25f600e. Final suites and the exact Core receipt
bind to that repaired source, not the earlier pair-run HEAD. The rest of the
source/test/schema fingerprints must match that exact qualified revision.

CP038_100_RUNNER.txt is the original execution script, retained as evidence.
Its local /workspace paths must be adapted to a new clone/output directory for
reuse, and its file catalog is CP038_100_FILES.json. A portable equivalent for
each path P in that catalog is:

```bash
PYTHONPATH=src:tests:. PYTHONHASHSEED=0 python -m pytest -q tests/P
PYTHONPATH=src:tests:. PYTHONHASHSEED=1729 python -OO -m pytest -q tests/P
```

P is a filename from the JSON list. The pinned historical ledger is materialized
exactly as described in the root final manifest before running fixtures that
need it. Do not fetch later canonical state. Before-proof reproduction must use
the prior module bytes with the new test retained; the paired suite tests do not
include the six newly added tests.

CP037_FINAL_qualification_snapshot.json preserves the prior delivery's manifest;
its earlier FINAL_* references belong to that delivery's Git tree, where their
original bytes remain available. It is not a claim those historical hashes match
the newly replaced final transcripts. The current FINAL_qualification.json is
the authoritative current evidence index.

STATIC_initial_tooling_error.txt records a failed attempt to invoke a nonexistent
export_schemas.py. FINAL_static_checks.txt records the corrected repository
script generate_schemas.py, plus successful Ruff F and whitespace checks. The
initial command error is not a product defect or a successful schema check.

CP100 is the Owner-requested stop. No CP101 is opened. No economic/observation/
capital/live-trading permission was granted, and no deployment was performed.
Unproven depth and the existing LONGITUDINAL_001 remain in the final manifest.
