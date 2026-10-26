# BLUE — GATE A V4 FINAL INDEPENDENT RECEPTION — 2026-09-21

## 0. Blue disposition

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

`TARGET_HOST_READY = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT DECLARED`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

This is Blue's reception of the completed independent Astra audit.
It closes the repository-correction review for the exact frozen v4 candidate only.

It does not transfer repository proof into target-host proof.

## 1. Exact candidate

Frozen candidate:

`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Selected candidate CI already known:

`35536353538 = COMPLETED / SUCCESS`

## 2. Independent auditor

Astra branch:

`astra/p0-gate-a-v4-independent-audit-2026-09-20`

Final Astra HEAD:

`afe25984b0ddd261fda143d858106c3c71e45149`

Ancestry independently rechecked by Blue reception:

- merge-base(candidate, Astra) =
  `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- Astra final HEAD is four commits ahead of the frozen candidate;
- changed paths are audit-only:
  - `.github/workflows/astra-gate-a-v4-independent-audit.yml`
  - `audit/astra_gate_a_v4_independent_probe.py`
  - `handoff/ASTRA_GATE_A_V4_MISSION_2026-09-20.md`
  - `handoff/ASTRA_GATE_A_V4_CHECKPOINT_2026-09-21.md`
  - `handoff/ASTRA_GATE_A_V4_INDEPENDENT_AUDIT_2026-09-20.md`
- no frozen production file was modified by Astra.

## 3. Final exact-head CI

At exact final Astra HEAD
`afe25984b0ddd261fda143d858106c3c71e45149`:

- `Astra Gate A v4 independent audit`
  - run `35545297473`
  - `COMPLETED / SUCCESS`

- `SEC P0 pre-t0 gate`
  - run `35545297451`
  - `COMPLETED / SUCCESS`

This closes the handoff's explicit final-self-reference gap.
No CI evidence is transferred from the prior evidence HEAD.

## 4. Independent findings received

Astra independently reproduced the historical v3 instability mechanism without
using the corrected canonicalizer as its oracle.

On frozen v4 Astra found:

- transient ExecStart observations
  `start_time / stop_time / pid / code / status`
  do not move the effective-unit digest;
- tested real command/configuration drift is rejected or changes the digest;
- current systemd semantic checks remain fail-closed;
- qualifying lookalikes do not pass by substring accident;
- materialization / one-use deployment authority / child-launch boundaries remain intact;
- no second-order repository bypass was found.

Independent verdict received:

`AUDIT_GATE_A_V4 = PASS_REPOSITORY_CORRECTION`

## 5. TEST_DEFECT received

Astra identified one Builder test whose name overstates its lifecycle scope:

`test_materialize_authorize_then_qualifying_start_is_not_invalidated_by_metadata_change`

FACT:
the test itself proves digest stability, not the full authority/materialization/child
lifecycle implied by its name.

Classification received:

`TEST_DEFECT / NON_BLOCKING`

Blue accepts this classification for the current Gate A v4 repository disposition
because Astra independently exercised the missing authority boundary through A8
and the existing Phase5 campaign.

The misleading test name/coverage statement should not be reused as independent
end-to-end lifecycle proof in future governance.

## 6. Parser limitations received

Astra surfaced five parser limitations:

1. duplicate stable keys are last-write-wins;
2. literal semicolon inside argv is not round-trippable by the simple split parser;
3. internal argv whitespace can move the digest;
4. duration parsing accepts trailing noncanonical text;
5. equivalent duration textual representations can move the digest.

For the exact frozen current service Astra classified these:

`NON_ISSUE / HYPOTHETICAL_FUTURE_UNIT_LIMITATION`

Blue accepts that current-candidate classification because no reachable current-unit
false equality/fail-open was reproduced and the frozen service does not use the
affected representations.

These limitations remain design debt for any future service shape that introduces
such representations. They are not silently generalized away.

## 7. Remaining proof domain

Repository correction is closed.

Still `TARGET_HOST_ONLY`:

- actual v4 execution on the real systemd host;
- real post-invocation ExecStart serialization under v4;
- runtime-image identity;
- mount semantics;
- durable-state-root authority;
- single-writer/global requester-budget topology;
- reboot/lifecycle/filesystem semantics required by Gate B.

Therefore:

`TARGET_HOST_READY = FALSE`

until Gate B is executed and accepted.

## 8. Relationship to hybrid P14D work

This reception closes the independent-v4-review blocker in the hybrid promotion
checklist.

It does NOT close the separate Gate-A hybrid fault-matrix blocker.

Current remaining method blocker:

`FINAL_GATE_A_FAULT_MATRIX = OPEN`

The hybrid amendment must not be promoted until that evidence is durably delivered
and Blue-inspected with no repository-side blocker.

## 9. Blue final repository decision

FACT:
Builder correction + discriminating tests + independent Astra A1-A10 + final
exact-head CI all support the same repository-level conclusion.

BLUE DECISION:

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

Scope:
exact frozen candidate
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`.

No stronger state is implied.

Next:
receive the bounded Gate-A hybrid fault-matrix evidence; if clean, complete exact
lineage binding and decide whether the hybrid P14D amendment may be promoted before
target-host Gate B.
