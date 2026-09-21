# P0 t0 PRECOMMIT TEMPLATE — CANDIDATE — 2026-09-21

## Status

`T0_PRECOMMIT_TEMPLATE = PREPARED_CANDIDATE`

`t0 = NOT_DECLARED`

This template becomes usable only after:
- hybrid amendment promotion;
- exact-candidate Gate-B contract activation;
- Gate B PASS;
- Blue authorization to prepare the next qualifying launch.

## 1. Precommit identity

Fill BEFORE the qualifying launch.

```text
PRECOMMIT_SCHEMA =
PRECOMMIT_CREATED_AT_UTC =

CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
VERIFIED_INPUT_TREE_DIGEST = sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2

GATE_B_ARTIFACT_DIGEST =
TARGET_HOST_OPAQUE_ID =
BOOT_ID =
PERSISTENT_STATE_IDENTITY =
ACTIVE_FINGERPRINT =
MATERIALIZED_FINGERPRINT =
EFFECTIVE_SERVICE_DIGEST =
RUNTIME_IDENTITY_DIGEST =

QUALIFYING_LAUNCH_AUTHORITY_ID =
QUALIFYING_LAUNCH_AUTHORITY_DIGEST =
AUTHORITY_FRESH = TRUE
AUTHORITY_UNCONSUMED = TRUE

T0_BINDING_MODE = PRECOMMITTED_NEXT_AUTHORIZED_QUALIFYING_LAUNCH
```

No secret requester identity or interpretable SEC content belongs here.

## 2. Prospective Gate-C calendar commitment

Before launch, bind the expected event plan from prospective source-calendar
facts only.

```text
SOURCE_CALENDAR_AUTHORITY_VERSION =

ORDINARY_CLOSED_INTERVAL_EXPECTED_START_UTC =
ORDINARY_CLOSED_INTERVAL_EXPECTED_END_UTC =

NEXT_EXPECTED_LIVE_ACQUISITION_WINDOW_UTC =

COMPLETE_WEEKEND_CLOSURE_START_UTC =
COMPLETE_WEEKEND_CLOSURE_END_UTC =

FIRST_REQUIRED_POST_WEEKEND_ACQUISITION_WINDOW_UTC =

DAILY_INDEX_RECONCILIATION_RULE =
DAILY_INDEX_SETTLE_RULE =

RESOURCE_HEALTH_BASELINE_ARTIFACT_DIGEST =
```

Do not populate these fields from observed outcomes after launch.

## 3. Unique-launch statement

The precommit must contain the following semantic commitment:

> The next single qualifying systemd launch that consumes
> `QUALIFYING_LAUNCH_AUTHORITY_ID` while all bound identities match is the
> unique t0 event for this attempt.

No other launch may be selected retrospectively.

## 4. Seal

Before launch compute and store:

```text
PRECOMMIT_CANONICAL_DIGEST =
PRECOMMIT_STORAGE_REFERENCE =
PRECOMMIT_SEALED_AT_UTC =
```

The sealed precommit must be immutable for this attempt.

Any change requires abandoning the attempt and creating a new precommit before
a new qualifying launch.

## 5. Launch-event materialization

After the launch, append/bind in a separate launch-event artifact:

```text
OBSERVED_LAUNCH_UTC =
SYSTEMD_INVOCATION_ID =
SUPERVISOR_ID =
MAIN_PID =
OBSERVED_BOOT_ID =
CONSUMED_AUTHORITY_ID =
OBSERVED_ACTIVE_FINGERPRINT =
OBSERVED_MATERIALIZED_FINGERPRINT =
OBSERVED_EFFECTIVE_SERVICE_DIGEST =
OBSERVED_PERSISTENT_STATE_IDENTITY =
PRECOMMIT_CANONICAL_DIGEST =
```

Then evaluate:

```text
UNIQUE_MATCHING_LAUNCH = TRUE|FALSE
ALL_PRECOMMITTED_IDENTITIES_MATCH = TRUE|FALSE
AUTHORITY_CONSUMED_EXACTLY_ONCE = TRUE|FALSE
PROVENANCE_UNAMBIGUOUS = TRUE|FALSE
```

Only if ALL are TRUE:

`t0 = OBSERVED_LAUNCH_UTC`

Otherwise:

`NO_T0`

## 6. No retrospective repair

Forbidden for the same attempt:
- changing the precommit after outcomes;
- choosing a later good launch;
- choosing a later good timestamp;
- ignoring an earlier invalidating launch;
- replacing a fingerprint/state/service binding after the fact.

A failed attempt is preserved and closed as failed.

## 7. Gate C handoff

A valid launch-event artifact must feed Gate C immediately.

It does not itself prove Gate C.

## 8. Current non-authority

`T0_PRECOMMIT_TEMPLATE = PREPARED_CANDIDATE / NOT_YET_EXECUTABLE`

`REAL_CAPITAL_AUTHORIZED = FALSE`


## 9. Mandatory hardening fields

Any activated successor to this template must additionally bind:

```text
BLUE_ACTIVATION_ARTIFACT_DIGEST =
ACTIVATED_GATE_B_CONTRACT_DIGEST =
ACTIVATED_RUNBOOK_DIGEST =
GATE_B_RUN_ID =
GATE_B_FINAL_ARTIFACT_DIGEST =

TIME_AUTHORITY_SNAPSHOT_DIGEST =
NTP_SYNCHRONIZED =
BOOT_ID_AT_PRECOMMIT =
REALTIME_MONOTONIC_CORRELATION_DIGEST =

NETWORK_RUNTIME_BINDING_DIGEST =
RESOURCE_BASELINE_DIGEST =
EVIDENCE_RETENTION_BINDING_DIGEST =
SOURCE_CALENDAR_PLAN_DIGEST =
```

If any required field is unknown:

`PRECOMMIT_VALID = FALSE`

## 10. One-attempt / one-authority anti-replay rule

A precommit is valid for exactly one Gate-C attempt.

It binds exactly one:
- `GATE_B_RUN_ID`;
- qualifying launch authority;
- target state identity;
- runtime/service/fingerprint set;
- source-calendar plan.

If the authority is consumed by a mismatched launch, or if a launch occurs before
the precommit is sealed, the attempt is terminally invalid.

Do not issue a replacement authority under the same precommit.

Create a new precommit for a new attempt.

## 11. Clock-step invalidation

Between precommit seal and qualifying launch, a detected unexplained wall-clock
step, NTP loss, boot change, or time-authority change invalidates the precommit.

Result:

`NO_T0`

A new time-authority snapshot and new precommit are required.

## 12. Launch timestamp provenance

The launch-event artifact must identify the authoritative timestamp source and
bind:

- systemd InvocationID;
- boot ID;
- externally attributable launch timestamp;
- corresponding monotonic time/reference if available;
- consumed authority ID;
- precommit digest.

The UTC t0 value is accepted only after this provenance is verified.

## 13. Evidence retention

The precommit and launch-event artifact must live in the restricted evidence
domain covered by the Gate-B evidence-retention binding.

Loss of the precommit or launch event before Gate D invalidates the qualifying
attempt.
