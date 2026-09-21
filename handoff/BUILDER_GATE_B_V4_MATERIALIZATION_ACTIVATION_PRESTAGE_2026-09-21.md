# BUILDER — Gate-B V4 materialization / activation prestage — FINAL — 2026-09-21

## 0. Final disposition

MISSION_TYPE = READ_ONLY_ANALYSIS + HANDOFF_ONLY

GATE_B_ACTIVATION_PRESTAGE = READY_FOR_BLUE_REVIEW

This handoff completes the previously incomplete checkpoint. It is a sealed
prestage plan only. Nothing in this document authorizes execution.

Current mission branch before this final replacement:
builder/gate-b-v4-materialization-activation-prestage-2026-09-21

Durable checkpoint consumed by this continuation:
9500256c1bed1b93ca593994d5e186c6ec303b5e

Verified checkpoint ancestry:
09dcf60e754a9d0d4e733b7582bb81350567fc5b..9500256c1bed1b93ca593994d5e186c6ec303b5e
contains exactly one prior delta, this handoff checkpoint.

This plan does NOT declare:

    GATE_B = PASS
    TARGET_HOST_READY = TRUE
    t0 = DECLARED

and does not authorize real capital.

## 1. Authorities read and applied

The plan is derived from:

1. QUANT_NORTH_STAR.md
2. governance/BLUE_GATE_B_PARALLEL_PREPARATION_DISPATCH_2026-09-21.md
3. governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md
4. governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md
5. governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md
6. governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md
7. governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md
8. governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md
9. operator/gate-b-read-only-preflight-2026-09-21
   @44285788fce3d5d048b037dd8d1089e1f08f43e9
10. frozen V4 runtime files at
    4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072.

The operator preflight is preserved as evidence, not reinterpreted as current
host truth. Every host-dependent field below is rechecked at activation.

## 2. Frozen object and known immutable bindings

Exact candidate:

    CANDIDATE_SHA=4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
    GIT_TREE=4d15ef6f471213ee6ab56337b555d2906ef9bf16
    VERIFIED_INPUT_TREE_DIGEST=sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2

Selected exact-head CI:

    35536353538 = COMPLETED / SUCCESS

Exact-head CI verification artifact:

    artifact id = 10612758620
    archive digest = sha256:06c690203d589e389847cd345809480da2b99254fe7fd7f38b82c6bf5d54659a

Frozen repository unit:

    deploy/quant-sec-capture.service

Expected repository/loaded unit byte digest from the read-only preflight:

    sha256:cfeeb12ac670b5e8f46932db113ba71ed153f389e28da0c3eb41f1c0581b15a9

Expected final release path:

    /opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

Fixed service root:

    /opt/quant

Durable P0 state root:

    /var/lib/quant-p0

Writable service state view:

    /opt/quant/var

Rejected V3 currently reported by preflight as the fixed service view:

    2da079d8ad75c69eb3fc2990c512735cb4bdc02b

The preflight reported the V4 release path absent. That fact MUST be rechecked
before mutation; an unexpected newly existing V4 path is not silently reused.

## 3. Preserved preflight facts and drift hints

Operator public preflight:

    TARGET_HOST_OPAQUE_ID =
    sha256:8880e5f6d980ae94454b13dcdb0b8bb85db989b0b17a36a70b1829243d989ad5

    RESTRICTED_SNAPSHOT_CANONICAL_SHA256 =
    sha256:77bfe820fa981ca3dfa70ba74d11bdb03aad6595b5752c72cd6510817e487d6b

    resolver digest =
    sha256:70cdb37efe507d7b6e575b27172140323116146cbbb99c687680482117b203da

    durable-state metadata-only drift digest =
    sha256:fecf62f341995c41e18cd57b18aefca534afa0e9631dbb4fb039679f0b8088ec

Those values are activation-time comparison anchors only. The state metadata
digest is NOT a semantic state-validity proof.

The preflight also reported:
- unit loaded with no drop-ins;
- service failed and disabled;
- V3 service view read-only;
- durable-state source visible;
- no bound restricted evidence root;
- no live-process baseline because the service was stopped;
- no target-host mutation.

## 4. Blue activation seal required before any mutation

Blue must seal one machine-checkable activation for one unique GATE_B_RUN_ID.

At minimum the activation must bind:

    ACTIVATION_SCHEMA_VERSION
    BLUE_DECISION_TIMESTAMP_UTC

    CANDIDATE_SHA
    GIT_TREE
    VERIFIED_INPUT_TREE_DIGEST

    AUTHORITATIVE_HYBRID_AMENDMENT_REF
    AUTHORITATIVE_HYBRID_AMENDMENT_DIGEST

    ACTIVATED_GATE_B_CONTRACT_REF
    ACTIVATED_GATE_B_CONTRACT_DIGEST

    ACTIVATED_GATE_B_RUNBOOK_REF
    ACTIVATED_GATE_B_RUNBOOK_DIGEST

    ACTIVATED_RELEASE_MATERIALIZATION_REF
    ACTIVATED_RELEASE_MATERIALIZATION_DIGEST

    ACTIVATED_GATE_B_EVIDENCE_SCHEMA_REF
    ACTIVATED_GATE_B_EVIDENCE_SCHEMA_DIGEST

    TARGET_HOST_OPAQUE_ID
    EXPECTED_SERVICE_UNIT=quant-sec-capture.service

    GATE_B_RUN_ID
    GATE_B_ATTEMPT_NUMBER
    OPERATOR_IDENTITY_REFERENCE

    V4_SOURCE_GIT_DIR
    V4_SOURCE_OBJECT_EVIDENCE_DIGEST

    EXPECTED_V3_SERVICE_VIEW_SOURCE
    EXPECTED_STATE_SOURCE_MOUNT_IDENTITY
    EXPECTED_STATE_SOURCE_MOUNT_IDENTITY_DIGEST

    EVIDENCE_ROOT
    EVIDENCE_ROOT_PARENT_IDENTITY

    PERSISTENT_MOUNT_AUTHORITY_REFERENCE
    PERSISTENT_MOUNT_AUTHORITY_DIGEST

    ACTIVATION_CANONICAL_DIGEST
    ACTIVATION_STORAGE_REFERENCE
    ACTIVATION_SEALED_AT_UTC

    GATE_B_MUTATION_AUTHORIZED=TRUE

The activated evidence schema MUST be the Blue-promoted schema at activation
time. Do not hard-code this prestage branch's schema as future authority.

A missing/mismatched field is STOP, before mutation.

## 5. Mutation capability matrix — default deny

Every omitted capability is FALSE.

For the V4 materialization + service-view transition itself, the minimum
capabilities are:

| Capability | Required for this prestage execution | Rule |
| --- | --- | --- |
| ALLOW_EVIDENCE_ROOT_SETUP | TRUE | Create only the run-scoped restricted evidence directory. |
| ALLOW_RELEASE_MATERIALIZATION | TRUE while V4 path is absent | No overwrite; no linked worktree; no alternate object store. |
| ALLOW_MOUNT_RECONFIGURATION | TRUE | Only fixed service-view and its state child view. |
| ALLOW_PERSISTENT_MOUNT_AUTHORITY_UPDATE | TRUE only if Blue binds the exact authority | No second competing mount authority may be invented. |
| ALLOW_SYSTEMD_DAEMON_RELOAD_FOR_MOUNTS | TRUE only if persistent mount units/files are changed | Frozen service fragment itself is not edited. |
| ALLOW_SYSTEMD_START_STOP | FALSE for blocker-remediation phase | If service is unexpectedly active, STOP rather than silently stop it under this subphase. |
| ALLOW_SYNTHETIC_STATE_SETUP | FALSE for blocker-remediation phase | Separate Gate-B destructive scope. |
| ALLOW_CHILD_FAULT_INJECTION | FALSE for blocker-remediation phase | Separate Gate-B destructive scope. |
| ALLOW_SUPERVISOR_SIGKILL | FALSE for blocker-remediation phase | Separate Gate-B destructive scope. |
| ALLOW_CONTROLLED_REBOOT | FALSE for blocker-remediation phase | Separate Gate-B destructive scope. |
| ALLOW_MISSING_MOUNT_TEST | FALSE for blocker-remediation phase | Later destructive B8 only. |
| ALLOW_WRITER_LOCK_CONTENTION_TEST | FALSE for blocker-remediation phase | Later destructive B2/B8 only. |
| ALLOW_DEPLOYMENT_AUTHORITY_WRITE | FALSE for blocker-remediation phase | This mutates durable P0 state and is later-only. |
| ALLOW_FINGERPRINT_MATERIALIZATION | FALSE for blocker-remediation phase | This mutates durable P0 state and is later-only. |
| ALLOW_REAL_SEC_NETWORK | FALSE | Mandatory for synthetic/destructive Gate B unless separately superseded by Blue. |
| ALLOW_ROLLBACK_TO_REJECTED_V3_VIEW | FALSE by default | May be TRUE only for stopped-host recovery; never qualifying continuation. |

Blue may seal broader destructive Gate-B capabilities only after parallel-lane
convergence. No operator may infer permission from this table.

## 6. Evidence-root proposal and first authorized mutation

Proposed restricted run root:

    /var/lib/quant-p0-qualification/gate-b/$GATE_B_RUN_ID

Requirements:
- outside the immutable release;
- outside /var/lib/quant-p0;
- persistent across the planned Gate-B lifecycle/reboot campaign;
- root-owned, mode 0700;
- sufficient bytes/inodes;
- filesystem/mount identity recorded;
- no public requester identity, raw filing content, per-event sensitive data or
  secret environment values.

Before the first mutation, all activation fields and digests are verified
read-only and the service is confirmed inactive.

The FIRST command in this plan that requires
GATE_B_MUTATION_AUTHORIZED=TRUE is exactly:

    sudo install -d -m 0700 -o root -g root "$EVIDENCE_ROOT"

Preconditions immediately before that command:

    test "$GATE_B_MUTATION_AUTHORIZED" = "TRUE"
    test "$ALLOW_EVIDENCE_ROOT_SETUP" = "TRUE"
    test -n "$GATE_B_RUN_ID"
    test ! -e "$EVIDENCE_ROOT"

If Blue pre-provisions the exact run-scoped evidence root under a separately
sealed authority, this creation is skipped and the first Gate-B mutation becomes
the staging-directory creation in section 8. Blue must record which boundary
applied.

## 7. Activation-time read-only rebind

Before any mutation, collect and hash a fresh activation snapshot.

Mandatory rechecks:

1. host/time
   - UTC wall clock;
   - timezone;
   - NTP synchronized state;
   - boot ID;
   - realtime/monotonic correlation;
   - target host opaque identity.

2. service
   - ActiveState/SubState/Result;
   - enablement;
   - FragmentPath;
   - DropInPaths;
   - ExecStart;
   - WorkingDirectory;
   - Restart;
   - RestartUSec;
   - StartLimitIntervalUSec;
   - StartLimitBurst;
   - KillMode;
   - KillSignal;
   - TimeoutStopUSec;
   - EnvironmentFiles;
   - repository unit SHA-256;
   - loaded fragment SHA-256.

3. mounts
   - exact findmnt source/target/fstype/options for:
     /opt/quant-releases,
     /opt/quant,
     /opt/quant/var,
     /var/lib/quant-p0;
   - persistent mount authority actually responsible for those paths;
   - source filesystem identity for /var/lib/quant-p0.

4. runtime/network
   - OS/kernel;
   - Python real path/version/implementation;
   - OpenSSL;
   - resolver digest;
   - proxy-variable NAMES and opaque effective binding only;
   - /etc/quant/sec-capture.env digest/metadata without printing secret values.

5. state
   - metadata inventory;
   - acquisition-critical authority/provenance file digests;
   - lock holders;
   - integrity latch;
   - unexplained lifecycle/scheduler/attempt pre-seeding;
   - raw-object referential integrity.

Any unexplained drift from the read-only preflight or activation is STOP.

If the service is active, this blocker-remediation subphase does not stop it:
return to Blue unless ALLOW_SYSTEMD_START_STOP was explicitly authorized for the
same run.

## 8. Exact V4 source and materialization procedure

### 8.1 Source authority

The source is not a branch name and not the CI archive.

The source authority is the exact Git commit object:

    4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

whose tree MUST resolve to:

    4d15ef6f471213ee6ab56337b555d2906ef9bf16

V4_SOURCE_GIT_DIR must be a Blue-bound local Git repository/object source on the
target host. The admin/development clone is admissible only as an object source;
the final release must have no dependency on it.

Read-only source checks:

    git -C "$V4_SOURCE_GIT_DIR" cat-file -e "$EXPECTED_SHA^{commit}"
    test "$(git -C "$V4_SOURCE_GIT_DIR" rev-parse "$EXPECTED_SHA^{tree}")" = "$EXPECTED_TREE"
    git -C "$V4_SOURCE_GIT_DIR" fsck --full --strict

A moving ref, source archive, linked worktree, shared worktree or source whose
expected object cannot be independently resolved is FAIL.

### 8.2 Existing-final-path decision

Recheck:

    test ! -e "$QUANT_RELEASE"

If the final V4 path now exists, DO NOT overwrite it and DO NOT enter the
creation path below. Verify it completely under the activated release contract.
Any mismatch is integrity failure and FAILED_TERMINAL for the run.

### 8.3 Fresh staging

Use a unique same-parent staging path:

    STAGE="/opt/quant-releases/.stage-$EXPECTED_SHA-$GATE_B_RUN_ID"

Require:

    test ! -e "$STAGE"

First release-materialization mutation:

    sudo install -d -m 0755 -o root -g root "$STAGE"

Populate a self-contained Git database without alternates or linked worktree:

    sudo git -C "$STAGE" init
    sudo git -C "$STAGE" fetch --no-tags "$V4_SOURCE_GIT_DIR" "$EXPECTED_SHA"
    sudo git -C "$STAGE" checkout --detach "$EXPECTED_SHA"

No remote is required in the release. Do not use git clone --shared,
git worktree add, object alternates, or a .git indirection file.

### 8.4 Git/object verification in staging

Require all of:

    test -d "$STAGE/.git"
    test ! -f "$STAGE/.git"
    test ! -e "$STAGE/.git/objects/info/alternates"
    test "$(sudo git -C "$STAGE" rev-parse HEAD)" = "$EXPECTED_SHA"
    test "$(sudo git -C "$STAGE" rev-parse 'HEAD^{tree}')" = "$EXPECTED_TREE"
    test "$(sudo git -C "$STAGE" rev-parse --is-shallow-repository)" = "false"
    test -z "$(sudo git -C "$STAGE" status --porcelain=v1 --untracked-files=all)"
    sudo git -C "$STAGE" fsck --full --strict

The worktree inventory must contain exactly this release worktree and no linked
worktree dependency. A .git file or alternates file is immediate FAIL.

Required frozen paths must exist at minimum:

    deploy/quant-sec-capture.service
    deploy/quant_sec_supervisor.py
    scripts/quant.py
    scripts/verify_p0.py
    src/quant/dataplane/sec/fingerprint.py

Repository unit SHA-256 must equal:

    sha256:cfeeb12ac670b5e8f46932db113ba71ed153f389e28da0c3eb41f1c0581b15a9

### 8.5 Independent verified-input-tree regeneration

Regenerate the exact algorithm from frozen scripts/verify_p0.py without writing
handoff/SEC_FORM4_P0_VERIFICATION.json:

    python3 - "$STAGE" <<'PY'
    import hashlib
    import sys
    from pathlib import Path

    root = Path(sys.argv[1])
    digest = hashlib.sha256()
    for tree in ("src", "tests", "scripts", "deploy"):
        for path in sorted((root / tree).rglob("*")):
            if (not path.is_file()
                    or "__pycache__" in path.parts
                    or path.suffix in {".pyc", ".pyo"}):
                continue
            digest.update(str(path.relative_to(root)).encode("utf-8"))
            digest.update(path.read_bytes())
    print("sha256:" + digest.hexdigest())
    PY

Require exact equality with:

    sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2

Do not treat the stale committed verification placeholder as the exact-head CI
artifact.

### 8.6 Create the empty state mountpoint before immutability

The frozen Git tree intentionally contains no tracked var/ directory.

Create exactly one operational mountpoint in staging:

    sudo install -d -m 0755 -o root -g root "$STAGE/var"

Require it to be empty:

    test -z "$(find "$STAGE/var" -mindepth 1 -print -quit)"

An empty directory does not alter the Git tree/status. No state content is copied
into the release.

### 8.7 Protect backing release bytes

Before promotion:

    sudo chown -R root:root "$STAGE"
    sudo chmod -R a-w "$STAGE"

Recheck HEAD/tree/status/unit/input-tree after permission hardening.

### 8.8 Promote without overwrite

Immediately before promotion:

    test ! -e "$QUANT_RELEASE"

Promote within /opt/quant-releases:

    sudo mv -n -T "$STAGE" "$QUANT_RELEASE"

Then require:

    test -d "$QUANT_RELEASE"
    test ! -e "$STAGE"
    test "$(sudo git -C "$QUANT_RELEASE" rev-parse HEAD)" = "$EXPECTED_SHA"
    test "$(sudo git -C "$QUANT_RELEASE" rev-parse 'HEAD^{tree}')" = "$EXPECTED_TREE"
    test -z "$(sudo git -C "$QUANT_RELEASE" status --porcelain=v1 --untracked-files=all)"

If mv -n leaves STAGE present, treat that as final-path collision; do not repair
in place.

The release is now immutable but the service is still NOT started.

## 9. Release-materialization artifact

Seal, without secret content:

    TARGET_HOST_V4_RELEASE_MATERIALIZATION_<UTC>.json

It must bind at least:

- GATE_B_RUN_ID;
- activation reference/digest;
- target host opaque ID;
- V4_SOURCE_GIT_DIR opaque/reference binding;
- source object-evidence digest;
- expected/observed SHA;
- expected/observed tree;
- expected/observed verified-input-tree digest;
- exact CI run/artifact/archive digest;
- clean-status verdict;
- self-contained .git verdict;
- alternates verdict;
- linked-worktree verdict;
- fsck verdict;
- repository unit digest;
- final release path;
- final release filesystem/mount identity;
- ownership/permission evidence;
- empty var mountpoint verdict;
- overall PASS/FAIL/UNKNOWN;
- service_started=false;
- t0_declared=false.

On any materialization FAIL, preserve this red artifact and stop.

## 10. Durable-state preservation invariants

Release creation and service-view transition MUST NOT:

- delete /var/lib/quant-p0;
- copy P0 state into the release;
- create a replacement qualifying reservoir;
- truncate journals;
- remove unexplained rows;
- rewrite the acquisition fingerprint;
- create/consume deployment authority;
- clear an integrity latch;
- start the collector.

Before mount transition, record:
- source mount identity;
- filesystem device identity;
- ownership/permissions;
- metadata inventory digest;
- acquisition-critical authority/provenance digests.

After transition, require the same durable source identity and same pre-existing
state bytes, except for evidence generated outside the state root.

No rsync/cp/rm command against /var/lib/quant-p0 is part of this plan.

## 11. Exact fixed service-view transition V3 -> V4

### 11.1 Preconditions

Require:
- service inactive;
- exact V4 release verified;
- /opt/quant currently resolves to the activation-bound rejected V3 source;
- /opt/quant is read-only;
- /opt/quant/var is a mountpoint;
- /var/lib/quant-p0 is the exact activation-bound durable source mount;
- no P0 writer/lock holder exists;
- mutation authority includes ALLOW_MOUNT_RECONFIGURATION=TRUE.

If any condition differs, STOP. Do not adapt locally.

### 11.2 Snapshot current topology

Capture restricted findmnt/stat data and SHA-256 it before changing any mount.

Preserve the old V3 service-view source only as rollback metadata. V3 is not an
eligible qualifying runtime.

### 11.3 Detach only the writable child view

    sudo umount /opt/quant/var

Immediately verify:
- /var/lib/quant-p0 remains mounted and unchanged;
- /opt/quant remains the old V3 read-only service view;
- service remains inactive.

Failure is terminal; do not force/lazy-unmount.

### 11.4 Detach the old fixed code view

    sudo umount /opt/quant

Do not use umount -l or umount -f.

Inspect the underlying /opt/quant mountpoint. It must not contain an unexpected
stale runnable tree. Do not delete unexpected content to make the test pass.

Unexpected underlying content is MISSING_OPERATIONAL_PROOF/FAIL and the run
becomes FAILED_TERMINAL.

### 11.5 Attach the exact V4 release as fixed service view

    sudo mount --bind "$QUANT_RELEASE" /opt/quant
    sudo mount -o remount,bind,ro /opt/quant

Require:
- mount source resolves to the exact V4 release;
- target is /opt/quant;
- read-only is effective;
- HEAD/tree/unit digest still match V4;
- no writable source-code path is exposed through the service view.

### 11.6 Attach the preserved durable state as the only writable child

    sudo mount --bind /var/lib/quant-p0 /opt/quant/var
    sudo mount -o remount,bind,rw /opt/quant/var

Require:
- /opt/quant/var is a mountpoint;
- it resolves to the exact activation-bound /var/lib/quant-p0 identity;
- code outside var remains read-only;
- state inventory/provenance digests still match the pre-transition snapshot.

No service start occurs in this transition.

## 12. Persistent mount ordering

The read-only preflight did not publish the host's persistent mount authority.
Therefore this prestage does NOT guess whether the existing V3 view is owned by
fstab, native .mount units or another already-audited mechanism.

Blue activation must bind:

    PERSISTENT_MOUNT_AUTHORITY_REFERENCE
    PERSISTENT_MOUNT_AUTHORITY_DIGEST

Rule:

1. If an auditable existing authority owns /opt/quant and /opt/quant/var, update
   that exact authority from V3 to V4 under
   ALLOW_PERSISTENT_MOUNT_AUTHORITY_UPDATE=TRUE.
2. Do not create a second competing authority.
3. If the current authority cannot be identified unambiguously, STOP.
4. Any persistent authority must enforce:
   - code view before state child view;
   - state source must itself already be a real mount;
   - both mount views before quant-sec-capture.service;
   - service start fails when either mandatory mount cannot be established.

If Blue elects to normalize onto native systemd mount units, the only acceptable
new units are exact, separately hashed units equivalent to:

    /etc/systemd/system/opt-quant.mount

        [Unit]
        Description=Quant fixed V4 service view
        Before=quant-sec-capture.service

        [Mount]
        What=/opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
        Where=/opt/quant
        Type=none
        Options=bind,ro

        [Install]
        RequiredBy=quant-sec-capture.service

and:

    /etc/systemd/system/opt-quant-var.mount

        [Unit]
        Description=Quant durable P0 state view
        Requires=opt-quant.mount
        After=opt-quant.mount
        Before=quant-sec-capture.service
        AssertPathIsMountPoint=/var/lib/quant-p0

        [Mount]
        What=/var/lib/quant-p0
        Where=/opt/quant/var
        Type=none
        Options=bind,rw

        [Install]
        RequiredBy=quant-sec-capture.service

This normalization is optional and requires explicit Blue authorization because
the existing persistence mechanism is not public evidence.

After any persistent-authority update:
- daemon-reload only if required by that authority;
- repository service fragment bytes remain unchanged;
- DropInPaths remains empty;
- loaded service-unit digest remains the frozen V4 unit digest;
- mount-authority files receive their own SHA-256 digests.

## 13. Missing-mount fail-closed boundary

Two independent fail-closed mechanisms are required.

### 13.1 Persistent dependency boundary

The persistent mount authority must refuse the state child bind unless
/var/lib/quant-p0 is itself the expected mounted durable source. It must order
both views before the collector service.

### 13.2 Runtime/content boundary

The V4 release contains only an EMPTY var mountpoint. No fingerprint or state is
stored there.

If /opt/quant/var is absent:
- the qualifying supervisor cannot find the required materialized fingerprint;
- any attempted state creation is against the read-only V4 service view;
- startup therefore must fail rather than create a fresh qualifying state tree.

The later controlled missing-mount B8 test must prove:
- service does not become active;
- no new local state appears beneath the unmounted release var directory;
- /var/lib/quant-p0 remains preserved;
- failure evidence is externally attributable.

That test requires ALLOW_MISSING_MOUNT_TEST=TRUE and
ALLOW_SYSTEMD_START_STOP=TRUE and is NOT performed by this prestage.

## 14. Activation-time fingerprint / service bindings

Before later fingerprint materialization or deployment-authority creation, bind:

- loaded fragment digest == frozen repository unit digest;
- DropInPaths empty;
- WorkingDirectory=/opt/quant;
- ExecStart launches /usr/bin/python3 -I
  /opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --qualifying;
- Restart=on-failure;
- RestartSec=15s;
- StartLimitIntervalSec=600s;
- StartLimitBurst=5;
- KillMode=control-group;
- KillSignal=SIGTERM;
- TimeoutStopSec=30s;
- EnvironmentFiles includes /etc/quant/sec-capture.env;
- effective-unit digest emitted by the frozen supervisor;
- Python/OpenSSL/runtime identity;
- private requester identity availability;
- global requester budget/single-writer authority.

The frozen supervisor validates existing materialization before launching a child.
It does not create a missing fingerprint on qualifying start.

Fingerprint materialization, when later explicitly authorized, uses the frozen
sec-fingerprint primitive and must be executed in the exact effective service
environment. It writes:

    /opt/quant/var/sec/acquisition_fingerprint.json

schema:

    p0_materialized_fingerprint/v2

and binds:
- active acquisition-critical fingerprint;
- host identity digest;
- materialized time;
- collector version;
- Git commit;
- canonical manifest including effective service invocation.

Existing materialization is validated and never silently overwritten.

Fingerprint materialization is a durable-state mutation and is therefore outside
the blocker-remediation mutation allowlist above.

Deployment-authority creation is likewise later-only. The frozen command path is:

    /usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py \
      --root /opt/quant --authorize-deployment

It performs explicit pre-t0 ledger migration when required and creates a
fresh one-use deployment authority. It MUST NOT be run unless Blue separately
sets ALLOW_DEPLOYMENT_AUTHORITY_WRITE=TRUE after state-authority review.

## 15. Rollback rules

Rollback never converts a failed attempt into PASS.

### Before final release promotion
- do not populate the final SHA path;
- preserve the failed staging path and red evidence;
- do not reuse the same staging path or run ID.

### After final release promotion but before service-view switch
- leave the immutable V4 release in place for audit;
- service remains stopped;
- do not delete or patch the release.

### During/after service-view switch
If a mandatory transition check fails:
- service remains stopped;
- preserve mount/evidence snapshots;
- never modify durable-state contents to recover;
- mark the run FAILED_TERMINAL.

Rebinding the rejected V3 view is permitted only when the sealed activation
explicitly contains:

    ALLOW_ROLLBACK_TO_REJECTED_V3_VIEW=TRUE

and only as stopped-host operational recovery. It MUST NOT:
- start the service;
- continue the same Gate-B run;
- count as qualifying runtime;
- erase the failed V4 evidence.

A new attempt requires a new GATE_B_RUN_ID and a new Blue activation.

## 16. FAILED_TERMINAL semantics

For one activated run, the first mandatory FAIL sets:

    GATE_B_RUN_STATUS=FAILED_TERMINAL
    ACTIVATION_CONSUMED=TRUE

Mandatory terminal failures include at least:
- host/activation mismatch;
- unexpected active writer/service at blocker-remediation entrance;
- source commit/tree mismatch;
- verified-input-tree mismatch;
- dirty release;
- linked worktree;
- Git alternates;
- failed git fsck;
- repository unit digest mismatch;
- final release path collision or foreign contents;
- state source mount identity drift;
- unexplained state inventory/provenance drift;
- V3 service-view source mismatch before transition;
- failure to preserve state during child/root mount switch;
- V4 service view not exact/read-only;
- state child not exact/writable-only-at-var;
- ambiguous or competing persistent mount authority;
- evidence-root loss/truncation;
- any mandatory schema/evidence binding UNKNOWN;
- any unexpected real SEC request during synthetic/destructive Gate B.

After FAILED_TERMINAL:
1. preserve the red artifact;
2. perform only evidence-safe shutdown/recovery explicitly allowed by activation;
3. do not overwrite/rewrite the failed artifact;
4. do not continue destructive/qualifying progression;
5. do not reuse the run ID;
6. return to Blue.

## 17. Complete restricted artifact / digest inventory

Every artifact is canonicalized and SHA-256 hashed. The final manifest binds all
sub-artifact digests.

### Governance / authority
- Blue activation artifact + ACTIVATION_CANONICAL_DIGEST.
- activated hybrid amendment digest.
- activated Gate-B entrance contract digest.
- activated Gate-B runbook digest.
- activated release-materialization contract digest.
- activated evidence-schema digest.
- operator identity reference.
- GATE_B_RUN_ID / attempt number.

### Frozen repository identity
- candidate SHA.
- Git tree.
- verified-input-tree digest.
- exact-head CI run 35536353538.
- CI artifact id 10612758620.
- CI archive digest
  sha256:06c690203d589e389847cd345809480da2b99254fe7fd7f38b82c6bf5d54659a.
- independent Astra V4 review HEAD/run references required by the Gate-B contract.

### Pre-activation / authority snapshot
- activation-time host/time-authority artifact + digest.
- target-host opaque identity.
- boot/time correlation artifact + digest.
- preflight snapshot reference/digest.
- source-Git object-authority artifact + digest.

### Release
- TARGET_HOST_V4_RELEASE_MATERIALIZATION_<UTC>.json + digest.
- Git fsck output digest.
- self-contained Git/worktree/alternates verdict digest.
- regenerated input-tree evidence digest.
- repository unit digest.
- release filesystem/permission identity digest.

### Mount / state transition
- pre-transition mount topology artifact + digest.
- persistent mount-authority artifact + digest.
- any persistent mount-unit/file byte digests.
- post-transition mount topology artifact + digest.
- missing-mount fail-closed artifact + digest when later executed.
- pre-state inventory digest.
- acquisition-critical authority/provenance inventory digest.
- post-state inventory digest.

### Runtime/systemd/network
- systemd identity artifact + digest.
- loaded fragment digest.
- effective-unit digest.
- runtime/interpreter/OpenSSL artifact + digest.
- network/proxy/resolver/TLS opaque binding artifact + digest.
- environment-file opaque digest/metadata artifact.
- single-writer/global-requester-budget artifact + digest.

### Materialization/readiness
- fingerprint materialization artifact + digest.
- active/materialized equality evidence digest.
- readiness output digest.
- deployment-authority test artifact(s) + digest(s).

### Filesystem / lifecycle / resources
- filesystem semantics B2 artifact + digest.
- resource baseline artifact + digest.
- evidence-retention artifact + digest.
- each lifecycle subtest B8 artifact + digest:
  start, stop, fresh authorized start, abnormal child failure, child SIGKILL,
  supervisor SIGKILL, restart delay/burst, replacement-supervisor forgery
  rejection, controlled reboot, missing mount, writer-lock contention.
- synthetic-campaign network-activity artifact proving real_sec_requests_made=0.

### Sanitization / closure
- safe-state-separation artifact + digest.
- post-destructive sanitization artifact + digest.
- final SHA/tree/input-tree rebind digest.
- final systemd/runtime/mount rebind digest.
- final active/materialized fingerprint digest.
- schema-validation output + digest.
- final TARGET_HOST_GATE_B_ENTRANCE_<UTC>.json + digest.
- final Gate-B artifact manifest + ARTIFACT_MANIFEST_DIGEST.

The public repository receives only non-sensitive binding metadata. Restricted
host/runtime/acquisition evidence remains in the approved restricted root.

## 18. Gate-B evidence acceptance boundary

Before Blue reception, the final Gate-B JSON must validate against the activated
Blue evidence schema.

Human prose cannot override schema failure.

A schema validation failure is:

    GATE_B = BLOCKED

and if it occurs within an activated run after mutation, the run's evidence is
preserved and returned to Blue under the terminal-failure rules applicable to
that run.

Even a fully green Gate-B artifact does not create t0. Blue separately decides
Gate-B reception, then a separate prospective t0 precommit and exactly one
qualifying launch are required.

## 19. Execution sequence summary

The future authorized operator sequence is:

1. verify sealed activation and exact run ID;
2. rebind host/time/service/mount/runtime/network/state evidence read-only;
3. create the restricted run evidence root;
4. materialize V4 from the exact Git object into fresh staging;
5. verify SHA/tree/input-tree/Git self-containment/unit digest;
6. create empty var mountpoint, harden bytes, promote without overwrite;
7. seal release-materialization evidence;
8. verify durable state again;
9. transition /opt/quant/var off V3;
10. transition /opt/quant from V3 to exact V4 read-only bind;
11. reattach the exact durable state as /opt/quant/var;
12. update/verify the ONE Blue-bound persistent mount authority;
13. re-run full mount/state/service identity verification;
14. stop and return to Blue if any mandatory mismatch exists;
15. only under separately allowed Gate-B capabilities continue B2-B10,
    fingerprint/materialization, lifecycle campaign and sanitization;
16. seal and schema-validate the final Gate-B evidence chain;
17. return to Blue for reception.

No autonomous continuation to t0 is allowed.

## 20. Final attestation

This Builder continuation performed repository analysis and updated only this
handoff document.

    TARGET_HOST_INSPECTION_PERFORMED_THIS_CONTINUATION=FALSE
    TARGET_HOST_MUTATION_PERFORMED=FALSE
    SYSTEMD_MUTATION_PERFORMED=FALSE
    MOUNT_MUTATION_PERFORMED=FALSE
    P0_STATE_MUTATION_PERFORMED=FALSE
    RELEASE_MATERIALIZATION_PERFORMED=FALSE
    REAL_SEC_NETWORK_REQUESTS_MADE=0
    GATE_B_MUTATION_AUTHORIZED=FALSE
    GATE_B=NOT_STARTED
    t0=NOT_DECLARED

GATE_B_ACTIVATION_PRESTAGE = READY_FOR_BLUE_REVIEW

Control returns to Blue.
