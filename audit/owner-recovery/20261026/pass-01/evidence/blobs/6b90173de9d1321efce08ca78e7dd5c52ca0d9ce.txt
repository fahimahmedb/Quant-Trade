# BUILDER P0 EFFECTIVE UNIT DIGEST STABILITY V4 — FINAL HANDOFF — 2026-09-20

## 0. Role and non-claims

This is the Builder handoff for the P0 Effective Unit Digest Stability v4 corrective mission. It reports implementation and reproducible evidence only.

Builder does **not** declare:
- Gate A v4 PASS;
- target-host readiness;
- t0;
- P14D continuity;
- real-capital authorization;
- Gate B readiness;
- independent correctness of its own fix.

Blue / Mission Control remains the decision authority. Independent Astra/Red Team review is still required after Blue reception, per `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` §1.

## 1. Authority chain

- North Star: `QUANT_NORTH_STAR.md`
- Mission specification: `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_MISSION_2026-09-20.md`
- Blue defect finding: `blue/master-v2-2026-09-20:handoff/BLUE_TARGET_HOST_REAL_DEFECT_EFFECTIVE_UNIT_DIGEST_2026-09-20.md`
- Governance index: `blue/master-v2-2026-09-20:governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
- Frozen candidate under corrective review: `blue/p0-gate-a-v3-frozen-2026-09-20@2da079d8ad75c69eb3fc2990c512735cb4bdc02b`
- Restricted defect artifact binding: `sha256:cb402bb3151a59708c6e3b6406323fe8671680b0e2785c9bb92ff47064639442`
- Builder branch: `builder/p0-effective-unit-digest-stability-v4-2026-09-20`
- Exact implementation baseline (verified by `git merge-base`): `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`
- Code-fix delivery SHA (the corrective code change itself): `0bdd397d7409b01529c1f958c68781499679a95e`
- **Final delivery HEAD (code fix + this handoff/checkpoint): `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`**

The Builder branch is a linear descendant of the frozen baseline SHA and does not modify Blue master or any frozen/checkpoint branch. Three commits sit ahead of the baseline: `b3fc705f` (pre-existing mission doc, not authored in this session), `0bdd397d` (this correction), and `4d06bdbf` (this handoff + checkpoint document). Both `0bdd397d` and `4d06bdbf` independently received exact-head CI SUCCESS (§7) — a commit cannot truthfully embed its own SHA, so Blue should still resolve the branch HEAD before reception rather than trusting this document's SHA in isolation.

## 2. Changed paths

Relative to `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`, the code-fix commit (`0bdd397d`) changes exactly:

- `deploy/quant_sec_supervisor.py` — the corrective fix
- `tests/test_astra_pre_t0.py` — mandatory discriminating regression tests
- `STATE.md` — regenerated proof-inventory count (`python3 scripts/status_artifacts.py --write`), a mechanical consequence of the 12 added tests, no other field changed

No Blue governance file, frozen/checkpoint branch, Forward/Economic/Product integration code, Gate B, P14D governance, or real-capital execution code was touched.

## 3. The defect and the fix

### 3.1 Mechanism

`deploy/quant_sec_supervisor.py::_effective_systemd_definition` requested `ExecStart` via `systemctl show` and hashed the **raw** returned property string into `QUANT_SEC_EFFECTIVE_UNIT_DIGEST`. On real systemd, that string embeds both static command configuration (`path`, `argv[]`, `ignore_errors`) and transient execution observations (`start_time`, `stop_time`, `pid`, `code`, `status`). The latter change every time the qualifying service actually executes, even with zero semantic change to the unit — so the acquisition-critical digest moved as a side effect of the service running, which could make a valid pre-start materialization fail fingerprint validation.

### 3.2 Fix

Added `_canonicalize_exec_start()`, which parses the brace-delimited `ExecStart` struct(s) into field maps and drops the five transient keys (`start_time`, `stop_time`, `pid`, `code`, `status`), keeping `path`, `argv[]`, `ignore_errors` and any other configuration fields. `_effective_systemd_definition` now:

1. Fails closed (`SYSTEMD_EFFECTIVE_EXECSTART_UNPARSEABLE`) if no `{...}` struct can be parsed out of `ExecStart` at all.
2. Validates `path`/`argv[]` still reference `quant_sec_supervisor.py` (`SYSTEMD_EFFECTIVE_EXECSTART_MISMATCH` otherwise).
3. Validates `--qualifying` is present as an **exact argv token** (tightened from a substring check — see §3.3).
4. Binds the canonicalized entry list, not the raw string, into the JSON structure that gets hashed into the final digest.

All pre-existing checks (fragment byte equality, no-drop-ins, WorkingDirectory, Restart/RestartUSec/StartLimitIntervalUSec/StartLimitBurst/KillMode/KillSignal/TimeoutStopUSec, EnvironmentFiles, fail-closed on unavailable/unparseable duration) are unchanged and still run before the digest is computed.

### 3.3 Incidental tightening (in-scope)

While implementing the mandatory "removal/change of `--qualifying` => rejected" discriminant, the original substring check (`"--qualifying" not in exec_start`) was found not to reject an altered flag like `--qualifying-disabled`, because that string still contains `--qualifying` as a substring. This was tightened to an exact-token match (`"--qualifying" not in exec_start_argv.split()`). This is the same function/line already being corrected for the digest-stability defect and directly required by the mission's own mandatory-test list (§4 item 5); it is not scope expansion beyond `_effective_systemd_definition`.

## 4. Independent reproduction (old defect)

Per mission §5, the fix was not used as the sole proof the defect existed. Before implementing any change, an independent reproduction script was run against the **unmodified baseline** (`git status` confirmed a clean tree at `2da079d8`/`b3fc705f` before any edits):

- Fixture: realistic target-host `ExecStart` form, matching the mission's literal regression fixture, once with placeholder/no-run transient fields and once with populated `start_time`/`stop_time`/`pid=48213`/`code=exited`/`status=0/SUCCESS` (i.e., "before a run" vs "after one qualifying invocation"), same path/argv/ignore_errors in both.
- Result on unmodified baseline:
  - `digest_before = sha256:3a1dadfc11f1d0bb35f52a8a9ca002c860a5925a03c171ebb8351621d9c5eb58`
  - `digest_after  = sha256:d5295f5e814711c651afaff093b761ab54c3700940f1145248c66f3d0c181d9c`
  - `STABLE: False` — **defect reproduced independently**, matching Blue's target-host finding qualitatively (digest changes solely from transient execution metadata, no semantic drift).
- Same script re-run after the fix on the identical fixtures: `digest_before == digest_after`, both `sha256:0afa1ec62709e3ee0197e0f97f6aeed52e14211a0417caf7047e769771ce7955` — digest now stable.

## 5. New discriminant results

Added `Phase8EffectiveUnitDigestStabilityCampaign` (12 tests) to `tests/test_astra_pre_t0.py`, covering every discriminant the mission requires (§4) plus the literal target-host regression fixture (§4 mandatory fixture):

| Test | Discriminant |
| --- | --- |
| `test_target_host_execstart_fixture_is_accepted` | mission's literal target-host `ExecStart` fixture is accepted |
| `test_pid_timestamp_code_status_drift_leaves_digest_identical` | identical executable/argv, different PID/timestamps/exit code/status ⇒ identical digest |
| `test_same_semantic_unit_before_and_after_prior_invocation_is_stable` | same semantic unit before vs. after a prior invocation ⇒ identical digest |
| `test_executable_path_drift_is_rejected_or_changes_accepted_digest` | executable-path drift ⇒ rejected or digest changes |
| `test_argv_drift_is_rejected_or_changes_accepted_digest` | argv drift ⇒ rejected or digest changes |
| `test_qualifying_flag_removed_or_altered_is_rejected` | removal AND alteration (`--qualifying-disabled`) of `--qualifying` ⇒ rejected |
| `test_non_empty_dropinpaths_is_rejected` | non-empty `DropInPaths` ⇒ rejected |
| `test_loaded_fragment_byte_mismatch_is_rejected` | loaded fragment byte mismatch vs. repository unit ⇒ rejected |
| `test_workdir_semantic_drift_is_rejected` | `WorkingDirectory` drift ⇒ rejected |
| `test_environment_file_semantic_drift_is_rejected` | `EnvironmentFiles` drift ⇒ rejected |
| `test_unparseable_structured_execstart_fails_closed` | unparseable structured `ExecStart` ⇒ fail closed |
| `test_materialize_authorize_then_qualifying_start_is_not_invalidated_by_metadata_change` | end-to-end: `_effective_environment()`'s `QUANT_SEC_EFFECTIVE_UNIT_DIGEST` is identical before/after a simulated qualifying invocation, i.e. a materialize→authorize→start sequence is not invalidated solely by systemd execution-metadata change |

Restart/timing/kill-policy drift discriminants were already covered by the pre-existing `Phase7EffectiveSystemdContractCampaign` (unchanged, still green — see §6).

**Discriminating-power check (not merely "new tests pass"):** before restoring the fix, the source file was reverted to the committed baseline (`git stash push --keep-index -- deploy/quant_sec_supervisor.py`) with the new tests left in place, and the Phase8 suite was re-run:

```
FAILED test_materialize_authorize_then_qualifying_start_is_not_invalidated_by_metadata_change
FAILED test_pid_timestamp_code_status_drift_leaves_digest_identical
SUBFAILED(variant='altered') test_qualifying_flag_removed_or_altered_is_rejected
FAILED test_same_semantic_unit_before_and_after_prior_invocation_is_stable
4 failed, 9 passed
```

The fix was then restored (`git stash pop`) and the full Phase8 suite passed 12/12, confirming these four are genuinely discriminating tests rather than tautologies.

## 6. Exact local test commands / results

All commands run from repository root, `PYTHONPATH=src` where required, on final delivery HEAD `0bdd397d7409b01529c1f958c68781499679a95e`:

| Command | Result |
| --- | --- |
| `python3 scripts/generate_schemas.py --check` | `schemas checked` — PASS |
| `python3 scripts/status_artifacts.py --check` | `fresh: CHIEF_BRIEF.md` / `fresh: STATE.md` — PASS |
| `PYTHONPATH=src python3 -m unittest discover -s tests` | **423 tests, OK** (195.2s) |
| `PYTHONPATH=src python3 -m unittest tests.test_sec_form4_capture tests.test_p0_adversarial tests.test_astra_pre_t0` | **287 tests, OK** (15.8s) |
| `python3 scripts/demo_quant_system.py` | **35/35 checks passed** |
| `pytest tests/test_astra_pre_t0.py -k "Phase7EffectiveSystemdContractCampaign or Phase5AuthorityBindingCampaign or Phase8EffectiveUnitDigestStabilityCampaign"` | **22 passed, 5 subtests passed** |

Proof inventory at this candidate: **423 unit tests discovered** (411 baseline + 12 added by this mission); **35 end-to-end demo assertions**, matching `STATE.md`'s regenerated canonical block.

`handoff/SEC_FORM4_P0_VERIFICATION.json` was left untouched locally: `verify_p0.py --write/--check` binds to `github.sha`, which is only known once pushed, so — consistent with how the prior Gate A v3 delivery handled this same step — it is exercised by CI itself ("Generate exact-head verification artifact" / "Upload exact-head verification artifact" steps below), not pre-committed against a guessed SHA.

## 7. GitHub Actions — exact-head CI

Workflow: `SEC P0 pre-t0 gate` (`.github/workflows/sec-p0-pre-t0-gate.yml`)

Exact-head run on the code-fix commit `0bdd397d7409b01529c1f958c68781499679a95e`:

- **Run ID: `35535347844`**
- **Result: `COMPLETED / SUCCESS`**
- URL: `https://github.com/fahimahmedb/Quant-Trade/actions/runs/35535347844`

Exact-head run on the final delivery HEAD `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072` (code fix + this handoff/checkpoint):

- **Run ID: `35536353538`**
- **Result: `COMPLETED / SUCCESS`**
- URL: `https://github.com/fahimahmedb/Quant-Trade/actions/runs/35536353538`

Both runs are green on all steps:
- Fail-closed check (no SEC identity configured)
- Generated schema drift
- Status artifact freshness
- Full unit suite
- SEC P0 lane suite
- V1 end-to-end regression
- Generate exact-head verification artifact
- Upload exact-head verification artifact
- Restore committed verification placeholder
- Clean working tree

## 8. Residual risks / UNKNOWNs

- **Not independently verified by Builder.** This correction has not been reviewed by Astra/Red Team. Per governance, Builder does not certify its own correction as independent evidence.
- **`_canonicalize_exec_start` parsing scope.** The parser handles the single-`ExecStart=`-directive struct form actually used by `deploy/quant-sec-capture.service` (`{ path=... ; argv[]=... ; ... }`). It has not been exercised against a unit with multiple `ExecStart=` directives (systemd's repeated-struct form for that case) since the frozen unit only declares one; this is out of scope for the current unit file but worth flagging if the unit is ever changed.
- **Token-splitting of `argv[]` on whitespace.** `exec_start_argv.split()` assumes space-separated arguments with no embedded spaces (true for the current fixed argv). An argument containing a literal space would not be handled correctly, but the qualifying supervisor's argv is fixed and does not take operator-supplied arguments.
- **This correction has not been exercised against a real systemd target host.** All evidence here is repository-level (mocked `subprocess.run`) reproduction and regression, consistent with mission §0/§5 (`Only an operator/agent with real target-host access may claim target-host execution evidence`). It has not been re-run against the actual target host that produced the original defect artifact.
- **`--qualifying` exact-token tightening (§3.3)** is a behavior change beyond the literal "canonicalize ExecStart" instruction, done because it was required to pass the mission's own mandatory test (§4 item 5) and is confined to the same function already in scope. Blue/Astra should confirm this is within the intended correction boundary.
- Builder does not claim: Gate A v4 PASS, target-host readiness, t0, P14D proof, Gate B, Product integration, or real-capital authorization. None of those follow from this handoff.

## 9. Statement

Builder does not certify its own correction independently. This handoff reports implementation and reproducible repository-level evidence only.

## 10. Next step

Builder stops here and hands control back to Blue for reception and independent Astra/Red Team review, per the general governance flow: `finding → Blue decision → specification → Builder → independent review → Blue decision`.
