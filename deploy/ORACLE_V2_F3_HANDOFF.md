# Existing V2 → engineering-only Codex handoff

This extends `deploy.oracle_v2_deploy`; it reuses the existing V2 service/timer,
exact-release receipt, both exact-SHA CI checks, VM identity and local backend.
It does not run the scientific canary or transfer authority back to V1.

The prepared operator entrypoint is
`scripts/resume_oracle_v2_f3.sh TARGET_SHA EXPECTED_CURRENT_SHA TRANSPORT_PR`,
run as `ubuntu` in the existing SSH session. It first requires all four exact
CI gates, stages the candidate with the pinned CP1 installer, reuses or opens
the native GitHub CLI browser login, writes a root-only credential input and
invokes the explicit handoff. It never prints the token. The login is separate
from SSH authentication. A failed gate leaves the active runtime untouched.

Prerequisites: Owner/root SSH on the intended VM; the expected old release
`a67ffec48fff895d5edc42171855e2213e49cf0d`; V2 timer active/enabled and service
between wakes; V1 inactive/disabled; an immutable CP1-installed target with
successful **Oracle V2 Core** and **SEC P0 pre-t0 gate** runs on that exact SHA.
Never use an old run to qualify a newer commit. Installation alone does not
repoint either current symlink or start a scheduler.

Provide a root-owned, mode `0600` JSON file outside Git containing these string
keys (never paste its token or contents into chat/logs):

- `QUANT_REPOSITORY`: `fahimahmedb/Quant-Trade`
- `QUANT_CODEX_ISSUE_NUMBER`: the engineering issue number
- `QUANT_CODEX_TARGET_BRANCH`: `code/canonical`
- `QUANT_CODEX_EXPECTED_HEAD_SHA`: fresh target-branch head for the Codex task
- `QUANT_CODEX_TASK_ID`: a unique bounded engineering task identity
- `QUANT_CODEX_PROMPT`: a single-line bounded engineering instruction
- `QUANT_GITHUB_TOKEN`: durable GitHub user credential with repository
  contents/issues write and Actions read; principal must support `GET /user`
- `QUANT_GITHUB_ACTOR`: the credential's exact login
- `QUANT_GPT_OSS_COMMAND`: `AUTO_LOCAL_BACKEND` to reuse the V2 loopback model
  through the existing launcher; alternatively an explicit absolute command
  accepting one JSON context on stdin and returning one JSON decision

The handoff checks that identity, fresh GitHub subject and local structured model
decision as `quant-research`, without posting a comment. It repeats these checks
with the scheduler stopped. No hosted-model fallback or model download exists.

Run from the exact installed candidate, replacing each uppercase value with
its verified identity:

```sh
cd /opt/quant-research/releases/TARGET_SHA
sudo /usr/bin/python3.12 -B -m deploy.oracle_v2_deploy \
  --action handoff \
  --release /opt/quant-research/releases/TARGET_SHA \
  --expected-current-sha EXPECTED_CURRENT_SHA \
  --v2-ci-run EXACT_V2_RUN --sec-ci-run EXACT_SEC_RUN \
  --orchestration-config /etc/quant-research-v2/f3-input.json
```

Before writes, the transaction stores a root-only durable snapshot under
`/var/backups/quant-v2-handoff-*`, including original bytes/ownership/modes,
symlink, existing units/drop-ins, shared env, wrappers and sudoers. It stops and
disables V2, proves quiescence and takes the shared worker lock. The shared
`/etc/quant-research/worker.env` stays unchanged; F3 uses a dedicated V2 env file
and a V2 drop-in. V1 remains disabled. The target preserves the old V2 config
and model, changing only release/qualification identity and engineering mode.

An ordinary failure restores saved V2 automatically. After process death/reboot,
V2 stays disabled if mutation had begun; recover using the exact candidate:

```sh
sudo /usr/bin/python3.12 -B -m deploy.oracle_v2_deploy \
  --action rollback --backup-directory /var/backups/ACTUAL_TRANSACTION_DIRECTORY
```

Recovery reads the private disk snapshot, refuses concurrent Owner file/mode
edits and restores the old V2 timer. It never starts V1. Keep the old and new
immutable releases plus private backup. New orchestration ledgers and external
engineering results are preserved, not erased by configuration rollback.

`ACTIVE_F3_PROOF_PENDING` is deployment evidence only. Observe natural timer
wakes and bind the actual release, InvocationIDs, dispatch/result identity,
subsequent GPT-OSS decision and durable receipts. Only actual Codex-result
consumption can close F3. Local tests, a canary, CI or timer activity cannot.
No economic, prospective, capital, trading or whole-system finish is claimed.

## Hosted-call budget and PR context

The default issue-context checkout was actually observed to supply the project
branch, without the executable expected commit. The next qualification reuses a
draft PR with `code/canonical` as head and `project/canonical` as base. It must
never be merged; PR #50 is the bounded transport witness. Actual checkout access
and real result consumption remain unproven until the trial runs.

This trial is valuable only because it closes the current F3 transport blocker.
It is read-only: no new code, commit, strategy, branch, audit or architecture is
requested from Codex. Its GitHub response and existing published subject are
the durable result. Routine state inspection, prioritization and waiting stay
with deterministic code/local GPT-OSS.

The generated service environment enforces one builder invocation and at most
one reviewer invocation per task; head adoption/restart cannot bypass the cap.
There are no paid automatic retries; six unchanged observations park the task.
This bounds invocation count, not token count or account-wide monetary usage.
No hosted-model fallback is introduced. Preserve the first failed trial as
negative engineering evidence. An already-managed, byte-identical F3 drop-in
may be upgraded transactionally; an Owner-modified or later drop-in blocks.
