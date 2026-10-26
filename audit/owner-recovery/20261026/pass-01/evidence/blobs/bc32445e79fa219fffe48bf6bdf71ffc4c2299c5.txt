# BUILDER — GATE B OFFLINE LIFECYCLE / SANITIZATION PRESTAGE — 2026-09-21

## 0. Final disposition

`GATE_B_OFFLINE_LIFECYCLE_PRESTAGE = BLOCKED_MISSING_MECHANISM`

Conclusion:

`EXISTING_SAFE_MECHANISM_NOT_PROVEN`

Return owner:

`BLUE / MISSION CONTROL`

This is a read-only prestage for Astra finding F5 only. It is not a Gate-B execution result, does not authorize target-host mutation, does not declare Gate B PASS, and does not declare t0.

```text
TARGET_HOST_MUTATION_PERFORMED = FALSE
PRODUCTION_CODE_MODIFIED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE_BY_THIS_MISSION = 0
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
RETURN_CONTROL_TO = BLUE
```

## 1. Scope and authority

Architectural authority:
- `QUANT_NORTH_STAR.md`

Gate-B preparation authority read:
- `handoff/BLUE_GATE_B_PARALLEL_PREPARATION_CONVERGENCE_2026-09-21.md`
- `handoff/BUILDER_GATE_B_OFFLINE_LIFECYCLE_SANITIZATION_PRESTAGE_MISSION_2026-09-21.md`
- `governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md`
- `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`
- `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`
- Astra independent preactivation review:
  `astra/gate-b-v4-transition-independent-preactivation-review-2026-09-21@aff6b7a2ca6355f518578c0ddbcac72fb49a356c`
  handoff blob `5f13ecbd2278a07730d6da04536afda102f453c6`

Frozen implementation inspected exactly at:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Git tree authority from governance:

`4d15ef6f471213ee6ab56337b555d2906ef9bf16`

### Branch / starting-head provenance

FACT: the authorized working branch is
`builder/gate-b-offline-lifecycle-sanitization-prestage-2026-09-21`.

FACT: at mission start, the remote branch compared identical to the user-specified starting HEAD:

`b790dd574a48963ea981645ffdb18650f45d76b3`.

FACT: the mission document itself still contains the older expected starting HEAD
`2ee9e1d2d84b7c0ded400a56f64ad7d9e2a60651`.

FACT: Git comparison shows `b790dd5...` is exactly one commit ahead of
`2ee9e1d...`, and that single commit adds only the mission document
`handoff/BUILDER_GATE_B_OFFLINE_LIFECYCLE_SANITIZATION_PRESTAGE_MISSION_2026-09-21.md`.

INFERENCE: this is mission-document evolution, not a frozen-candidate substitution.

## 2. Frozen V4 objects inspected

The following frozen-V4 blobs were inspected:

| Path | Frozen V4 blob |
| --- | --- |
| `deploy/quant-sec-capture.service` | `94671297254ecbc4c77ebd6e72fbfa066604e79e` |
| `deploy/quant_sec_supervisor.py` | `c8a27e32e1d18d0ca147b29fabfb3419e66a93c3` |
| `scripts/quant.py` | `cfb784c3efed28317fc7a2af4eeb395d127bc109` |
| `src/quant/clock.py` | `2e4a5483e5659dcadc704cb7fa4aedef01f576a8` |
| `src/quant/paths.py` | `0777140e9b031863526372d9badc7427c6b8b3ef` |
| `src/quant/dataplane/sec/collector.py` | `dd301dab4de08719293ef35df02164e9d663248a` |
| `src/quant/dataplane/sec/transport.py` | `59b20b85f395b9970dbe4acb88a1b50f6e5b323b` |
| `src/quant/dataplane/sec/policy.py` | `779801e5371968121749807bd7c4127d9cb8b53c` |
| `src/quant/dataplane/sec/fingerprint.py` | `b3ea2aa9379e7354bf7d51590eebf5e66e2503f0` |
| `src/quant/dataplane/sec/supervisor.py` | `e36096db655817d3669913ce795a0350732cc174` |
| `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md` | `3ffe40107b7710c58de3b5a01b2e1574d611c5cb` |

No non-frozen implementation was used to infer V4 runtime behavior.

## 3. Finding

### FACT — the exact qualifying systemd path is fixed

The frozen unit launches:

```text
/usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --qualifying
```

with:
- `WorkingDirectory=/opt/quant`;
- `EnvironmentFile=/etc/quant/sec-capture.env`;
- `QUANT_SEC_SERVICE_MANAGER=systemd`;
- `Restart=on-failure`;
- `RestartSec=15`;
- `StartLimitBurst=5`;
- `KillMode=control-group`.

FACT: frozen supervisor validation requires the actually loaded fragment bytes to match the repository unit, rejects any loaded drop-in, requires the exact working directory, requires the environment file, and requires an exact `--qualifying` token.

INFERENCE: a Gate-B campaign that changes ExecStart, WorkingDirectory, or adds a drop-in is no longer exercising the exact frozen service binding whose semantics Gate B is supposed to prove.

### FACT — arbitrary environment redirection is intentionally stripped

The external supervisor builds a child environment from a whitelist. It retains only:
- PATH / HOME / fixed locale;
- `QUANT_SEC_USER_AGENT`;
- service-manager / InvocationID provenance;
- supervisor-derived timing, qualifying-mode and effective-unit fields.

FACT: proxy, PYTHONPATH, sitecustomize, Git, arbitrary operator environment and other ambient variables are not passed to the child.

INFERENCE: a synthetic campaign cannot legitimately redirect the production requester through an operator-supplied proxy or arbitrary environment variable while still claiming the frozen service path is unchanged.

### FACT — the production service path has no offline transport selector

`SecForm4Collector.__init__` accepts an optional injected `transport`.

FACT: the transport module itself explicitly states that tests substitute the transport wholesale and that the production path has no test-only branch.

FACT: `QuantSystem.__init__` constructs `SecForm4Collector` without supplying a transport.

FACT: when a policy is configured and no transport is injected, the collector constructs:

`SecHttpTransport(policy, ...)`.

FACT: `SecHttpTransport` defaults to:

`SEC_HOST = "www.sec.gov"`.

FACT: no frozen V4 service/systemd/config path inspected exposes an offline transport mode or a transport-factory selector to the actual `sec-serve` process.

INFERENCE: the fake transport used by repository tests is not reachable through the exact production systemd launch path without changing code or substituting the executable path.

### FACT — removing requester identity prevents network but also prevents the required successful service path

The policy has no default requester identity.

FACT: if `QUANT_SEC_USER_AGENT` is absent or invalid, `policy_from_environment` fails closed.

FACT: the operator CLI checks `collector.configured` before entering `sec-fingerprint` or `sec-serve`; an unconfigured collector exits BLOCKED rather than running an acquisition service.

FACT: the qualifying supervisor computes the active fingerprint from the configured policy and later validates an already-materialized fingerprint before creating the child.

INFERENCE: removing requester identity can prove fail-closed refusal and no SEC request, but it cannot exercise the full successful child lifecycle campaign required by B8: live child, child failure/SIGKILL, same-supervisor automatic restart witness, supervisor SIGKILL, restart delay/burst behavior, reboot path and post-run provenance.

### FACT — with a configured production requester, a newly enabled service can issue a real request immediately

FACT: `sec-serve` boots the system, enables the collector when disabled, then enters `serve_sec()`.

FACT: `CollectorState.last_poll_started_at_utc` defaults to null and `poll_due()` returns true when configured+enabled and no prior poll exists.

FACT: the dedicated service loop runs due capture before sleeping.

FACT: `collector.poll()` enters the single request path, reserves the global budget, mints a one-use permit, then calls:

`self.transport.fetch(path, permit)`.

FACT: the production transport sends an HTTPS GET through `http.client.HTTPSConnection` to its configured host, defaulting to `www.sec.gov`.

INFERENCE: an exact successful systemd start with valid requester configuration does not contain an internal “offline but otherwise normal” barrier. Absent a separately proven external egress-denial mechanism, real SEC traffic is possible.

### FACT — state selection is root selection; there is no independent service state-root selector

`QuantPaths` defines all operational state under:

`<root>/var`.

The accepted target topology is:
- exact release under `/opt/quant-releases/<sha>`;
- fixed service view at `/opt/quant`;
- durable state at `/var/lib/quant-p0`;
- writable state view at `/opt/quant/var`.

FACT: the systemd unit fixes `--root /opt/quant`.

FACT: the real service has no separate `--state-root` option and no state-root environment variable.

FACT: changing `--root` changes both code/content root and state root.

INFERENCE: direct execution against another root may isolate state, but it is not the exact systemd service path. Editing ExecStart to another root changes the frozen service authority and effective-unit digest.

### FACT — lifecycle provenance and synthetic contamination live in the same state reservoir

Under `root/var/sec`, frozen V4 stores, among other files:
- `supervisor_state.json`;
- `supervisor_events.jsonl`;
- `deployment_authority.json`;
- `deployment_authorities.jsonl`;
- `lifecycle.jsonl`;
- `scheduler.jsonl`;
- `attempts.jsonl`;
- `request_intents.jsonl`;
- collector state and commit ledger;
- traffic-budget state and commit ledger;
- acquisition fingerprint materialization;
- raw/restricted capture evidence.

FACT: collector load logic fails closed if historical journals/evidence exist while collector state is missing.

FACT: the qualifying deployment contract says to preserve history and never discard journals merely to obtain a clean-looking start.

INFERENCE: running destructive Gate-B lifecycle exercises in the future qualifying reservoir and later deleting or editing the resulting rows is not sanitization; it destroys the provenance the design intentionally makes durable.

### FACT — one-use deployment authority is root-local and durable

The frozen supervisor:
- creates one authority file with `O_EXCL`;
- binds it to the current acquisition fingerprint and host boot ID;
- rejects stale, malformed, mismatched or replayed authority;
- appends the consumed nonce to `deployment_authorities.jsonl`;
- deletes the one-use authority file only after durable consumption.

FACT: those authority files live under the same `root/var/sec` reservoir as the other lifecycle evidence.

INFERENCE: a destructive campaign needs its own non-qualifying/synthetic reservoir and its own authority lineage if its authority history must not pollute future Gate-C state.

### FACT — fingerprint/materialization binds the real service semantics

The acquisition fingerprint includes:
- acquisition-critical source bytes;
- policy including a digest binding of requester identity;
- runtime version strings;
- request shape including `www.sec.gov`;
- service definition/launcher digests;
- effective service invocation including qualifying mode and effective loaded-unit digest.

FACT: qualifying service validation requires an existing materialized fingerprint and fails closed on missing, foreign, stale or mismatched materialization.

INFERENCE: an ad hoc offline flag, alternate requester host, changed unit, drop-in or changed ExecStart would be acquisition-semantic drift unless it is explicitly implemented and fingerprinted. Frozen V4 contains no such supported offline semantic.

## 4. Why the obvious substitutes do not close F5

### Alternate `--root`

FACT: possible for hand-run Python.

FACT: not the frozen systemd ExecStart.

INFERENCE: it proves behavior of a different launch binding and does not prove the exact target service manager path.

### Injected fake transport

FACT: supported by `SecForm4Collector` for programmatic/tests.

FACT: not wired through `QuantSystem` / `sec-serve` / the frozen systemd service.

INFERENCE: using it would substitute a materially different executable construction path.

### Remove `QUANT_SEC_USER_AGENT`

FACT: prevents configured SEC access.

FACT: also blocks `sec-serve` before a successful qualifying collector lifecycle exists.

INFERENCE: suitable for a negative fail-closed check only, not the required destructive lifecycle campaign.

### Proxy or arbitrary environment redirect

FACT: arbitrary proxy/operator environment is stripped by the supervisor child whitelist.

INFERENCE: not a supported current-V4 offline mechanism.

### systemd drop-in / changed unit

FACT: the supervisor rejects loaded drop-ins and fragment mismatch.

FACT: the effective unit is part of the acquisition-critical binding.

INFERENCE: invalidates proof of the exact frozen service.

### Hidden/ad hoc bind-mount swap

CLAIM: a separately provisioned synthetic filesystem could theoretically isolate all `root/var` state while leaving code bytes and ExecStart unchanged.

FACT: current governance explicitly says the unit does not itself enforce mounts and that mount ordering is external.

FACT: Gate-B hardening 17.7 and runbook 7A prohibit improvised path substitution, hidden bind swaps and hand-edited authority state.

UNKNOWN: whether the target host can support a fully sealed, reviewable synthetic `/opt/quant/var` reservoir swap plus externally enforced zero-egress boundary without altering the effective frozen service semantics.

INFERENCE: this possibility is an infrastructure design option for Blue, not an existing proven V4 mechanism.

### Manual journal deletion after test

FACT: prohibited by the qualifying deployment contract and inconsistent with durable provenance.

INFERENCE: it would erase exactly the evidence needed to prove what happened and therefore cannot be accepted as sanitization.

## 5. Exact missing primitive

The missing primitive is one **supported, auditable Gate-B synthetic execution binding** for the exact frozen service.

That binding must provide both of these properties together:

1. **Network impossibility**
   - the exact systemd service may run far enough to exercise child/supervisor lifecycle semantics;
   - no real SEC request can leave the host;
   - the guarantee is externally testable and bound into Gate-B evidence;
   - it cannot rely on test-only constructor injection, requester-identity removal, arbitrary proxy environment or an unbound unit/drop-in change.

2. **State-reservoir separation**
   - all writable `/opt/quant/var` / `root/var` effects for the destructive campaign go to a dedicated synthetic reservoir;
   - the preserved future qualifying reservoir is not writable by the campaign;
   - synthetic supervisor/lifecycle/scheduler/attempt/budget/materialization/authority rows remain intact as restricted Gate-B evidence;
   - after service stop, the synthetic reservoir can be detached/separated and the exact future Gate-C reservoir selected and re-bound without deleting history or changing the frozen executable/service semantics.

Frozen V4 does not expose such a combined binding as a supported runtime primitive.

## 6. Is implementation/config/testability work required?

`MINIMAL_WORK_REQUIRED = YES`

FACT: current frozen V4 has no production-service offline transport selector and no independent state-root selector.

RECOMMENDATION: Blue should specify one of two explicit routes rather than let the operator improvise.

### Route 1 — sealed infrastructure mechanism, if it can be proven without changing V4

Blue may specify a target-host mechanism that keeps:
- the exact frozen repository unit;
- no drop-ins;
- identical ExecStart/WorkingDirectory;
- identical code and interpreter binding;

while additionally sealing:
- exact synthetic reservoir mount source/destination identity;
- exact precondition that preserved qualifying state is not mounted writable into the service;
- exact egress-denial mechanism proving no SEC packet/request can leave;
- before/after mount identities;
- network-denial evidence;
- synthetic materialization and one-use authority lineage;
- stop-before-reservoir-switch rule;
- post-campaign rebind of the future qualifying reservoir;
- immutable retention of synthetic lifecycle evidence;
- post-sanitization inventory and final no-stale-authority/no-integrity-latch checks.

UNKNOWN: whether this route is feasible on the actual host while satisfying every existing service/fingerprint constraint. This mission did not mutate the host and therefore cannot prove it.

### Route 2 — minimal production-supported offline/testability primitive

If Route 1 cannot be sealed without semantic substitution, a code/config change is required.

RECOMMENDATION: Blue should then issue a new Builder mission for a production-reachable offline transport mode and explicit state-reservoir semantics that:
- are reached through the same supervisor/`sec-serve` executable path;
- are impossible to confuse with live SEC mode;
- are acquisition-fingerprint-bound;
- fail closed on ambiguous mode;
- preserve the same service-manager lifecycle behavior;
- provide a negative proof that `SecHttpTransport` / real socket send cannot occur;
- preserve all lifecycle/authority journals;
- have repository tests proving live mode cannot accidentally select offline mode and offline mode cannot emit network.

INFERENCE: because those bytes/config semantics would differ from frozen V4, Blue would need to decide the required refreeze/requalification scope before such a changed candidate could stand in for V4.

## 7. What Blue should specify next

RECOMMENDATION: Blue should issue a bounded successor specification named conceptually:

`GATE_B_SYNTHETIC_EXECUTION_BINDING_V1`

It should bind, before any mutation:
- exact candidate SHA/tree;
- exact repository and loaded unit digests;
- exact synthetic state reservoir identity;
- exact preserved future-qualifying reservoir identity;
- exact evidence-root identity;
- exact zero-egress mechanism and its pre/post verification;
- allowed mount operations and ordering;
- allowed lifecycle operations;
- unique Gate-B run ID and activation digest;
- non-qualifying/synthetic deployment authority lineage;
- exact materialization expected for the synthetic reservoir;
- exact evidence retained from each destructive subtest;
- exact transition from synthetic reservoir to preserved qualifying reservoir;
- exact sanitization assertions;
- prohibition on deleting/redacting synthetic lifecycle rows to manufacture a clean state;
- fresh future t0 authority requirement.

If Blue instead chooses a code change, the successor spec must additionally define the offline-mode semantics and its fingerprint membership before Builder implementation begins.

## 8. Sanitization boundary that can be asserted today

FACT: V4's durable journals are designed not to be silently rewritten away.

Therefore the only safe sanitization model visible from current evidence is **separation, not cleanup**:

- keep the destructive campaign's reservoir immutable/restricted as Gate-B evidence;
- stop the service before changing reservoir binding;
- never delete or edit synthetic lifecycle/authority rows to make the future reservoir look clean;
- bind a distinct future qualifying reservoir;
- inventory that future reservoir independently;
- require no stale one-use authority, no unexplained lifecycle rows and no integrity latch in that future reservoir;
- re-bind SHA/tree/input-tree/fingerprint/service/runtime/mount identity before Blue reception.

CLAIM: this separation model is consistent with Gate-B B10 and runbook Phase 7.

UNKNOWN: the exact currently supported host operation that safely performs the reservoir separation while preserving all frozen service semantics.

That UNKNOWN is the blocking F5 gap.

## 9. Final classification

```text
ASTRA_FINDING = F5
CLASSIFICATION = MISSING_PROOF
BUILDER_CONCLUSION = EXISTING_SAFE_MECHANISM_NOT_PROVEN
MINIMAL_WORK_REQUIRED = YES
TARGET_HOST_MUTATION_PERFORMED = FALSE
PRODUCTION_CODE_MODIFIED = FALSE
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
GATE_B_OFFLINE_LIFECYCLE_PRESTAGE = BLOCKED_MISSING_MECHANISM
RETURN_CONTROL_TO = BLUE
```
