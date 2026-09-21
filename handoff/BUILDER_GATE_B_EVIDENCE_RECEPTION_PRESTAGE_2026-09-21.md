# Builder — Gate-B evidence reception prestage — 2026-09-21

`GATE_B_RECEPTION_PRESTAGE = READY_FOR_BLUE_REVIEW`

`MISSION_TYPE = READ_ONLY_ANALYSIS + HANDOFF_ONLY`

This is a proposed reception procedure for Blue. It contains no target-host execution evidence, activation, Gate-B decision, or t0 declaration. It advances the Control/Data-plane evidence boundary needed to preserve persistent acquisition state; it establishes no economic edge or capital authority.

## 1. Scope, baseline and primary authorities

Work branch: `builder/gate-b-evidence-reception-prestage-2026-09-21`.
Verified starting HEAD: `71e2b3855179cabb57fb8ead538dd40f034fbada`.
Blue authority supplied for this mission: `ba510bd5e3077c7e29b35aef9cf45c98a5fd128c`.
The starting commit adds this lane's mission and descends from that Blue authority. The mission's older expected-start SHA is the Blue base; the user's exact branch HEAD governs this delivery. The dispatch's `4c855dca152d237d2b8d86419ebc5e3a59acde42` is its historical preflight authority, not a substitute for this branch identity.

Read North Star, repository instructions/routing, dispatch and mission. Primary reception authorities at the starting HEAD are below. Digests here are SHA-256 of exact committed file bytes, including their existing line endings; they are preparation pins, not the digests of a future activated successor.

| Authority | Exact-byte SHA-256 |
| --- | --- |
| [Entrance contract](../governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md) | `sha256:e3f805a6d3e6f72e3dc0cd79670a1134569a0c6a8bc0f7e6229ed725468b5477` |
| [Runbook](../governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md) | `sha256:7db5a567a60b1be325d0719341ab2a997a6c9f33f371fe53e11a3aa11f4a9ad2` |
| [Evidence schema](../governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json) | `sha256:145293a685ca412141b78889eb25eed60cf1e33a850e41a2bd10456faf7c5fde` |
| [Activation template](../governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md) | `sha256:93cdce6b73506850296173f2cf09c616f7fa59b5557379be05d6dfdac406c52d` |
| [Release materialization prerequisite](../governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md) | `sha256:78ecbbb79a2c38468681be94680a88d0b8de183df6cbb8bf2785a589beea4adf` |

Required operator input read in full: `operator/gate-b-read-only-preflight-2026-09-21@44285788fce3d5d048b037dd8d1089e1f08f43e9`, file `handoff/OPERATOR_GATE_B_READ_ONLY_PREFLIGHT_2026-09-21.md`, Git blob `48dfd849095362b924412f474a641010addd3406`.

That preflight reports V4 release absent, fixed service view on rejected V3, service failed/disabled, no bound restricted evidence root, unavailable live process baseline, and a metadata-only state drift hint. Its restricted raw snapshot existed only in the operator session. Its public digest cannot replace accessible mandatory evidence or new run-bound observations. Loaded-unit byte equality alone cannot close B1, B3, B4 or B7. Blue must receive the separately prepared transition plan/review and seal an activation before any remediation. This lane performs none.

## 2. Non-negotiable reception semantics

Every mandatory condition below is conjunctive. A label without attributable, retrievable proof is not a PASS.

| Observation | Blue reception disposition |
| --- | --- |
| Any mandatory UNKNOWN, missing evidence, inaccessible bytes or ambiguous identity | `GATE_B = BLOCKED`, `NO_T0`; record `MISSING_PROOF` and exact missing requirement. |
| Mandatory FAIL before an authorized attempt, invalid activation, or schema validation failure | `GATE_B = BLOCKED`, `NO_T0`; no mutation permission follows. |
| First mandatory FAIL in an activated attempt | `GATE_B_RUN_STATUS = FAILED_TERMINAL`, activation consumed; Gate B remains blocked. Preserve red evidence and stop progression except evidence-safe shutdown. |
| All B1–B10 and additional mandatory domains PASS, exact identities/chain match, schema valid, no unresolved defects | Eligible for a separate Blue `GATE_B = PASS` decision only. Operator green does not decide the gate. |

B3 contract wording treats an unknown mandatory loaded property as FAIL for progression. Preserve the observation as UNKNOWN/MISSING_PROOF, block reception, and apply the contract's failure rule to an active attempt; never coerce it to PASS. A valid negative test (for example replay correctly rejected) is a PASS of its expected fail-closed behavior, not a mandatory FAIL.

Use schema-compatible defect classes: `REAL_DEFECT` for demonstrated system/integrity/control violation; `TEST_DEFECT` for a demonstrably faulty harness/oracle; `MISSING_PROOF` for absent, incomplete or ambiguous mandatory proof; `TARGET_HOST_ONLY` for the host proof domain, not an exemption; `NON_ISSUE` for an evidenced dismissed concern; `NONE` for no defect supported by the evidence. Contract prose `MISSING_OPERATIONAL_PROOF / GATE_B_BLOCKER` maps to `MISSING_PROOF` in JSON, with the original wording in detail. TEST_DEFECT does not buy a PASS or erase a terminal failure.

Classify assertions separately as `FACT`, `CLAIM`, `INFERENCE`, `RECOMMENDATION`, or `UNKNOWN`. Claims, recommendations and unsupported inference cannot supply missing observations. For a PASS artifact, each of the 13 verdict objects must use `NON_ISSUE`, `TARGET_HOST_ONLY`, or `NONE`; inspect all sub-artifacts for unresolved REAL_DEFECT/TEST_DEFECT/MISSING_PROOF even though the schema does not impose that restriction on them.

Global contamination rule R applies to EVERY matrix row: one operator, one activated run ID, one evidence chain, one terminal result; at most one target-host mutating workstream. No local retry/replacement artifact, overwritten failure, selected green subset, or evidence assembled from several runs. A repaired retry requires a new run ID and new Blue activation. Prior PASS reuse requires an explicit durable Blue disposition naming old run, exact artifact digests, permitted scope, unchanged dependencies and new run. Preserve original provenance; record a new-run reuse wrapper referencing the original instead of relabeling it. Dynamic host/state/boot/process observations must be rebound. No reuse can revive a failed run or suppress its red artifacts.

## 3. Exact activation and identity checks, before domain review

1. Retrieve the sealed Blue activation and its storage reference. Verify Blue decision/seal timestamps precede the first mutation, `GATE_B_MUTATION_AUTHORIZED = TRUE`, operator identity, target host, expected `quant-sec-capture.service`, attempt number, unique `GATE_B_RUN_ID`, and every requested mutation permission. Omitted permission means FALSE. Compare the observed action timeline to the permission matrix; require proof the operator verified the digest immediately before first mutation.
2. Resolve activated contract, runbook, schema, hybrid amendment, lineage binder and materialization procedure at immutable references. Recompute their declared digests from preserved bytes using the sealed digest convention. Compare activation to final JSON, manifest and every run-bound artifact. Path names, current branch tips, and this template are not authority. Blank hybrid amendment reference/digest invalidates activation.
3. Verify activation's cited V4 repository PASS, independent V4 PASS, independent fault-matrix PASS, hybrid promotion, exact lineage binder, operator-pack Red Team and available preflight references. Check revocation, supersession and any Blue-declared activation-critical environment/boot change. Missing disposition blocks; do not infer it from CI alone.
4. Resolve run ID and attempt against Blue's immutable activation/attempt history: no earlier consumption, prior terminal FAIL, concurrent mutating attempt, or repeated nonce. Final `gate_b_run_id` (schema minimum length 8) and positive `gate_b_attempt_number` equal activation and manifest; each sub-artifact payload or hashed provenance wrapper binds the run. Schema uniqueness constraints alone do not establish global uniqueness.
5. Require exact candidate bindings everywhere: candidate `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`; Git tree `4d15ef6f471213ee6ab56337b555d2906ef9bf16`; verified input tree `sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`. These are not this handoff's commit. Check release, service view, materialization, final inventory/identity seal and activation against this triple. No transfer to another candidate without a new Blue disposition.
6. Require repository CI run `35536353538`, exact-head artifact ID `10612758620`, archive digest `sha256:06c690203d589e389847cd345809480da2b99254fe7fd7f38b82c6bf5d54659a`; independent V4 review HEAD `afe25984b0ddd261fda143d858106c3c71e45149` and CI `35545297473`, `35545297451`. Verify these against preserved authoritative evidence, including completed/success status and reviewed SHA. Additional CI IDs need a role; promotion CI is not candidate CI. Never substitute the stale committed `SEC_FORM4_P0_VERIFICATION.json` for exact-head CI evidence.
7. Check host opaque ID matches activation and all host observations. Link each boot ID and InvocationID to the externally witnessed lifecycle timeline. A controlled authorized reboot requires attributable old/new boot identities, clock correlation and post-boot authority validation; boot IDs must not be falsely required to stay equal across that test. Unexplained change or change invalidating activation blocks continuation and needs Blue disposition.
8. Require explicit boolean `t0_declared: false` in the final JSON and applicable materialization/launch evidence. No qualifying t0 launch authority may be consumed by this campaign. A future t0 remains a separate prospective precommit and unique externally attributable launch after Blue's decision.

## 4. B1–B10 acceptance matrix

The “fields” column identifies final-schema carriers and mandatory contents of referenced restricted artifacts. Nested operational fields listed here are contract requirements, not invented additions to the closed final schema. Every row requires evidence digest, assertion/defect classification, and the run/activation/candidate/host provenance from section 3. UNKNOWN handling and R from section 2 apply in addition to the specific rules below.

| Domain / schema carrier | Mandatory fields and required sub-artifacts | Exact cross-checks and PASS | FAIL, UNKNOWN, defect classification and contamination |
| --- | --- | --- | --- |
| **B1 immutable release/state isolation** — `mount_identity`, candidate triple | Release-materialization artifact: source object reference, expected/observed SHA/tree, detached/clean status, self-contained `.git`, no alternates/linked worktree, required paths/unit, final release path/filesystem, owner/permissions, `service_started:false`, `t0_declared:false`. Mount inventory for release, `/opt/quant`, `/opt/quant/var`, `/var/lib/quant-p0`; backing-tree protection and writable-path inventory; B8 missing-mount artifact. | Exact triple from section 3; release path `/opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072/`; fixed service view resolves to that release, not symlink/development checkout. State views identify the same durable reservoir, with source/device/filesystem/mount options and ownership bound. Code outside var and backing release protected. Exact clean tree plus authentic CI subset binding (or authoritative equivalent regeneration) proves input bytes. Missing state mount blocks start before any fallback state creation. | Wrong/dirty release, mutable code, foreign Git dependency, in-place overwrite, silent fresh state, or start without mount: FAIL/REAL_DEFECT. Unobserved topology/materialization/missing-mount behavior: UNKNOWN/MISSING_PROOF, BLOCKED. R: old V3/preflight or another mount namespace is not proof; carry exact same-run topology through post-reboot and B10. |
| **B2 filesystem durability semantics** — `filesystem_semantics` | Separate synthetic test records for advisory flock, hard-link publication, same-filesystem device identity, atomic rename where relied upon, regular-file fsync, directory fsync, acknowledged-state restart/reboot persistence, writer-lock conflict. Bind test paths privately, filesystem identity, inputs/expected outcome, return/errno, acknowledgments, pre/post hashes and external lifecycle references. | Synthetic area is on the actual P0 filesystem from B1; each primitive works with the frozen runtime's assumptions. Acknowledged bytes remain equal after controlled restart/reboot. Competing writer is denied before state alteration. | Lost acknowledged bytes, broken publication/locking or writer admitted: FAIL/REAL_DEFECT. Wrong test filesystem/oracle: TEST_DEFECT; absent actual-host result: UNKNOWN/MISSING_PROOF. R: repository tests only support; no successful subtest from a repaired run closes the failed run. |
| **B3 loaded systemd authority** — `systemd_identity` | Actual `systemctl show` and `systemctl cat` snapshots, loaded fragment/drop-in bytes, repository unit bytes, supervisor effective-unit digest, pre/post-invocation comparison and semantic-drift falsifier. Fields: FragmentPath, DropInPaths, ExecStart, WorkingDirectory, Restart, RestartUSec, StartLimitIntervalUSec, StartLimitBurst, KillMode, KillSignal, TimeoutStopUSec, EnvironmentFiles, running InvocationID. | Loaded fragment SHA-256 equals frozen repository unit `sha256:cfeeb12ac670b5e8f46932db113ba71ed153f389e28da0c3eb41f1c0581b15a9`; verify against candidate bytes. No unbound drop-in. ExecStart `/usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --qualifying`; WorkingDirectory `/opt/quant`; Restart on-failure; delay 15s; interval 600s; burst 5; control-group kill; SIGTERM; stop timeout 30s; EnvironmentFile `/etc/quant/sec-capture.env`; all other frozen semantics including environment/hardening match. Supervisor effective digest stable across transient ExecStart metadata, while semantic command drift changes fingerprint or is rejected. Effective digest equals B7/B10 binding; byte digest and effective digest are different domains. | Wrong loaded semantics, hidden drop-in, transient-metadata instability or undetected command drift: FAIL/REAL_DEFECT. Mandatory unknown property blocks and follows contract failure semantics. Bad units/time normalization in harness: TEST_DEFECT, not an exemption. R: no substituting a file on disk or old preflight for loaded authority during this run. |
| **B4 runtime/process identity** — `runtime_identity` | OS/distribution, kernel, boot ID, restricted machine/host identity, Python executable resolved path/version/implementation, OpenSSL/runtime, relevant packages/environment, cgroup/service manager; process/PID/start/InvocationID provenance and runtime/network identity artifacts. | Host equals activation. Actual service process uses the bound interpreter/environment/cgroup; process identity links B3 invocation to B8 timeline. Reboot change explained externally; final runtime binding established for future Gate C. TLS identity consistent with network binding. | Foreign process/interpreter/host or unexplained runtime substitution: FAIL/REAL_DEFECT. Stopped service with no process observation is UNKNOWN/MISSING_PROOF for live proof, not PASS. R: do not mix live process evidence from a different boot/run; record authorized reboot transition and final identity. |
| **B5 durable state authority / anti-preseeding** — `state_authority` | Pre-destructive inventory and final inventory with metadata/content hashes for acquisition-critical authority/provenance, raw-reference integrity, collector-lock holders, deployment lineage, supervisor/lifecycle/scheduler/attempt provenance, integrity-latch status; anti-preseeding falsifier and retrospective-audit result; explicit inventory delta ledger. | Inventory roots/devices match B1 and preserved state; every prior row has explainable lineage, referenced raw objects exist and hash correctly, no integrity latch/unrecognized writer. Unauthorized seeded authority cannot survive validation and still yield accountable audit. Explainable history retained; every pre/post addition/change/removal attributable. | Unauthorized preseed accepted/accountable: REAL_DEFECT, stop and return to Blue (Gate-A reopening concern). Unexplained history/raw loss/latch: FAIL or UNKNOWN according to evidence, never delete to clear. Metadata-only drift hint is MISSING_PROOF for semantics. R: histories from other runs remain distinguishable and preserved; no imported clean inventory or journal reset. |
| **B6 single writer/global requester budget** — `single_writer_budget` | Collector-lock/process/cgroup ownership, Product writable-state exclusion, global budget authority identity and scope, private requester identity presence/validity, absence fail-closed test, competing writer/requester/bypass checks, zero-network artifact. | Exactly one qualifying writer authority; no Product writer; all SEC requester paths within one global authority and no second requester outside it, including other hosts where relevant. Requester secret stays restricted; absence rejects before a request. Lock/budget identities match state and actual runtime. No assumption that a single-host lock coordinates multiple hosts. | Second writer/budget bypass/identity absence allowing requests: FAIL/REAL_DEFECT. Incomplete requester census or unverified budget scope: UNKNOWN/MISSING_PROOF. R: same-run ownership and budget proof, not a prior singleton snapshot; no concurrent mutating lane. |
| **B7 fingerprint/materialization** — `fingerprint_materialization` | Restricted readiness/materialization record, actual materialized manifest and digest, active fingerprint, candidate triple, effective service binding; stale/foreign/missing materialization rejection tests and before/after stale-artifact hashes. | Active fingerprint equals materialized fingerprint; candidate triple matches activation/CI/clean release; effective-unit digest equals B3; runtime/state/mount bindings agree. Supported procedure alone materializes; stale evidence is preserved, not silently rewritten. Reject before child launch on invalid materialization. | Mismatch accepted, stale overwrite, or missing materialization allowing launch: FAIL/REAL_DEFECT. Existence-only proof or unavailable manifest: UNKNOWN/MISSING_PROOF. R: a different run's fingerprint cannot mask local drift; rebind final B10 identity and preserve negative-test manifests. |
| **B8 destructive lifecycle campaign** — `lifecycle_campaign` | Separate artifacts for normal systemd start, stop, fresh authorized start, abnormal child failure, applicable child SIGKILL, supervisor SIGKILL, replacement-supervisor forgery rejection, restart delay/burst, controlled reboot, mount restored before service, missing-mount blocked start, writer contention. Each records expected/observed result, external journal/event source, boot/InvocationID/PID, UTC plus monotonic correlation, synthetic reservoir, authority reference, state hashes and network observation coverage. | Full authorized sequence on actual host; each transition externally attributable. Restart delay 15s and burst ceiling 5 within frozen 600s interval are observed under effective unit; no forged automatic-restart witness. Reboot restores state mount before start; missing mount/contending writer prevents launch/write. Negative tests fail closed as intended. Zero real SEC requests and no unexpected real-network attempt. | Forged provenance, timing/burst violation, launch without state/authority, unexpected real-network attempt or state corruption: FAIL/REAL_DEFECT; first mandatory FAIL terminal. Gaps/uncovered subtest: UNKNOWN/MISSING_PROOF. Invalid injection/oracle: TEST_DEFECT. Applicability omission requires evidence and Blue disposition, not a silent skip. R: no resuming after failure or choosing successful restarts; full chronological failures retained. |
| **B9 one-use deployment authority** — `state_authority` + `lifecycle_campaign` + `fingerprint_materialization`; explicit B9 sub-artifact | Synthetic/nonqualifying authority creation/validation/consumption record, unique nonce/reference, freshness, bound fingerprint/host boot identity, durable consumption observation across lifecycle, replay rejection, pre-materialization/pre-authority child-launch ordering tests, authority ledger and B10 stale-authority sweep. No standalone B9 top-level key exists. | Exact fingerprint B7 and applicable boot B4; fresh unique authority consumed once durably. Replay/missing/foreign/stale authority rejected before child launch. Separate fresh authority for each start where required. Test authority cannot become future t0 authority. | Replay accepted, consumption lost, wrong identity accepted, child before validation, or reuse for t0: FAIL/REAL_DEFECT. No durable proof/ambiguous nonce lineage: UNKNOWN/MISSING_PROOF. R: deployment nonce and Gate-B run ID are distinct; both tracked; neither recycled to sanitize an earlier attempt. |
| **B10 post-destructive sanitization** — `sanitization` | Service-stop witness; supported state-separation procedure reference; synthetic-state archive/isolation/removal ledger; selected future Gate-C persistent state identity; pre/post inventories and delta explanation; stale-authority/lifecycle/latch checks; final SHA/tree/input-tree/fingerprint/service/runtime/mount rebind; sealed final entrance artifact. | Service stopped before separation; synthetic bytes kept out of future reservoir using approved supported mechanism. Explainable real prior state and failure evidence retained. No stale authority, ambiguous lifecycle provenance, integrity latch or raw-object loss. Final identity chain agrees with activation/candidate and attributable reboot/runtime changes. Explicit t0 false. | Invented bind/path trick, silent reset/deletion, residual synthetic authority, identity mismatch: FAIL/REAL_DEFECT. Unprovable separation or any ambiguity: BLOCKED/MISSING_PROOF. R: no importing another run's sanitized root, erasing red tests, or treating Gate-B authority as future t0 authority. |

## 5. Additional mandatory domains and inventory reconciliation

All of these are required even though the matrix labels stop at B10:

| Domain | Evidence and acceptance check |
| --- | --- |
| `time_authority` | UTC, timezone, NTP/synchronization, time-service identity/configuration, boot ID and realtime/monotonic correlation before destructive tests and across reboot. Unsynchronized/ambiguous timestamps block timing claims. Clock steps must be explained; shell/operator timestamps alone cannot prove lifecycle. |
| `evidence_retention` | Restricted persistent evidence root outside immutable release, mount/filesystem, ownership/permissions, journald persistence/retention, disk/inode capacity and manifest seed. Prove referenced bytes survive test/reboot and are accessible to authorized Blue review. Truncation/rotation/loss destroying proof blocks. |
| `resource_baseline` | Before/after free bytes and inode headroom, state/evidence-root sizes, service RSS, open FD count/limits, cgroup/process limits and retention headroom. Capture live baseline during authorized synthetic running phases if stopped preflight cannot provide it. Final stopped state is explained, not substituted for live measurement. Insufficient headroom or unexplained monotonic growth needs classification; no invented numeric PASS thresholds. |
| `network_runtime_binding` | Non-secret effective service proxy/environment, resolver configuration, OpenSSL/TLS trust/runtime, requester network-path identity and relevant EnvironmentFiles; hashes/opaque references only publicly. Operator-shell absence of proxy variables is insufficient for the service. Bind against B3/B4/B6 and final sanitized configuration. |
| `synthetic_campaign_network_activity` | `real_sec_requests_made` is exactly integer 0, verdict PASS, and evidence digest resolves to full-campaign observation. Require effective offline transport/isolation and attributable request/egress observations covering all starts, failures and reboot, including descendants and possible budget bypass paths. A zero self-reported counter alone is insufficient. Uncovered interval is UNKNOWN/MISSING_PROOF. Any unexpected real SEC attempt is FAIL and terminal even if blocked before an actual request; positive count cannot satisfy current schema PASS. A separately authorized real-network exception would need explicit superseding authority/schema disposition, not relabeling or dropping this field. |

For pre/post inventory comparison, receive three clearly labeled snapshots where available: preserved state before destructive work, synthetic state after exercises before separation, and selected future qualifying reservoir after sanitization. At minimum the first and final snapshots and their digests are mandatory. Inventory schema/serialization/order must be declared and stable. Bind restricted relative paths, file type, ownership/mode, size, relevant timestamps, device/inode identity as applicable, authority/provenance content hashes, raw-object references and target hashes, lock and latch status. Do not expose those inventories publicly.

Compare path sets and content/metadata changes; every creation, mutation, removal, reservoir selection or inode change needs an operation/lifecycle reference, authorization, run ID and disposition. Do not require aggregate digest equality when authorized synthetic activity legitimately changes state. Require exact preservation of protected prior evidence, plus an exhaustive explained delta. Metadata equality is not content integrity. A selected different reservoir needs explicit approved identity/lineage and separation proof; it cannot silently erase inconvenient history. Preserve failed-run inventories immutably.

## 6. Schema-required-field map (v2, unchanged)

Schema ID: `quant://governance/target-host-gate-b-evidence-2026-09-21-v2`; dialect JSON Schema draft 2020-12. All 34 root fields below are required; root and nested defined objects reject additional properties. Do not add top-level B1/B9/schema-digest fields to bypass this: carry operational detail in referenced artifacts/manifest and the separate Blue reception record.

| Required fields | Machine constraints / semantic supplement |
| --- | --- |
| `schema_version`, `created_at_utc` | Constant `gate-b-evidence-v2`; date-time string with format checking enabled; verify timestamp is actually UTC and attributable. |
| `gate_b_run_id`, `gate_b_attempt_number` | String length >=8; integer >=1; global uniqueness and activation equality checked outside schema. |
| `candidate_sha`, `git_tree`, `verified_input_tree_digest` | Constants in section 3. |
| `activation_reference`, `activation_digest`, `contract_reference`, `contract_digest`, `runbook_reference`, `runbook_digest` | Nonempty reference strings; digest format `^sha256:[0-9a-f]{64}$`; resolve bytes and authority, not just syntax. |
| `target_host_opaque_id` | Nonempty string; exact activation/host binding. |
| `repository_ci_runs` | Nonempty unique array of positive integers; exact required run and role checks in section 3. |
| `independent_review` | Required `review_head` (40 lowercase hex), `verdict` (nonempty string); optional-in-schema `ci_runs` (unique positive integers), required by this contract's evidence requirements. Verify actual PASS and exact review/CI bindings. |
| `time_authority`, `runtime_identity`, `mount_identity`, `systemd_identity`, `state_authority`, `single_writer_budget`, `fingerprint_materialization`, `filesystem_semantics`, `lifecycle_campaign`, `resource_baseline`, `evidence_retention`, `network_runtime_binding`, `sanitization` | Each requires `verdict`, `evidence_digest`, `classification`, `defect_classification`; optional `detail`. Verdict is PASS/FAIL/UNKNOWN; digest and classification enums as above. |
| `synthetic_campaign_network_activity` | Required integer `real_sec_requests_made` >=0, PASS/FAIL/UNKNOWN `verdict`, SHA-256 `evidence_digest`; optional `detail`. Overall PASS requires verdict PASS and count 0. |
| `sub_artifacts` | Nonempty array; each item requires nonempty `name`, SHA-256 `digest`, `classification`, `defect_classification`; optional `restricted_reference` (string or null), `detail`. Blue requires each item retrievable via the manifest or reference even if the optional reference is absent/null. |
| `artifact_manifest_digest` | SHA-256 of the declared canonical manifest; verify closure/coverage and actual bytes. |
| `overall_verdict`, `t0_declared` | PASS/BLOCKED/FAILED_TERMINAL; literal boolean false. Overall PASS forces all 13 verdict objects PASS with allowed nonblocking defect labels. This conditional does not prove substantive B1–B10 completeness, signature/authority, run binding, retrieval, or hash equality. |

## 7. Sub-artifact hash-chain and sealing procedure

Blue should seal the following reception convention before activation. The current authorities require canonical digests but do not fully specify activation self-digest exclusion or a manifest/validation-report cycle. These are activation-time resolution items, not permission for an operator to choose a convention after seeing results. Missing or conflicting canonical rules => BLOCKED/MISSING_PROOF at reception. This proposal does not amend the authoritative schema.

1. Activation must declare the exact hash algorithm, canonicalization/version, payload boundary, encoding and self-digest exclusion. Proposed convention: detached immutable payload bytes, SHA-256 over those exact bytes; `ACTIVATION_CANONICAL_DIGEST` in an external seal referencing the payload, so no self-hash. If another canonical serialization is approved, record it and its exact hashed bytes. Do not assume the digest of this Markdown template is an activation digest.
2. For contract/runbook/schema/materialization/hybrid documents, preserve exact immutable bytes plus reference/version and algorithm. Proposed convention is raw UTF-8 committed bytes with no newline normalization. Distinguish Git blob IDs, Git tree IDs, verified input-tree digest, unit-byte digest, effective-unit digest and SHA-256 artifact digests.
3. Every sub-artifact carries run ID, host and relevant candidate/activation/boot/invocation/time context in its payload or a hashed wrapper. A wrapper for a raw journal/command result binds that raw blob's digest; the manifest includes both. Resolve references only as data; do not execute submitted commands or follow arbitrary external references. Preserve restricted access.
4. Manifest names every B1–B10 result (including explicit B9), release materialization, per-subtest lifecycle and authority tests, time snapshot, resource before/after, retention, runtime/network and zero-request proof, pre/post state inventories and delta ledger, final sanitization, and validation report. Every verdict `evidence_digest` must resolve to a listed artifact or listed aggregate whose children are listed and hashed. Enforce unambiguous names/references, complete coverage, no conflicting digest mappings, no dangling links, no omitted failures and no cross-run substitution. Hashes of absent bytes are not evidence.
5. Proposed acyclic seal sequence: freeze complete domain artifacts; assemble candidate final JSON E0 with manifest M0; schema-validate exact E0, preserving report V0 with E0/schema/validator digests. Create final manifest M1 including all domain artifacts plus V0, E0 and M0 as explicitly labeled sealing history. Build final JSON E1 referencing M1 and V0. Validate exact E1 and preserve detached report V1 bound to E1's exact-byte digest, M1 and schema. Seal a separate outer reception envelope referencing E1 and V1. Never insert V1 into E1/M1 after hashing. E0 is a sealing-stage artifact, not a second run or replacement for failed tests. Any change to domain evidence requires explicit review and cannot erase a failure.
6. Blue checks V1 against the exact delivered E1; V0 alone is insufficient. This keeps the runbook-required validation output hashed inside the final Gate-B chain, while the final exact-byte validation report closes it externally without a self-referential hash. Blue must explicitly approve this sequencing or specify an equivalent acyclic procedure before use. Neither validator report is Gate-B PASS authority.
7. Independently recompute SHA-256 of every referenced raw/canonical payload per its declared rule, including schema and manifest. Compare the activation canonical digest across operator pre-mutation record, final artifact and manifest; contract/runbook digests likewise. Manifest references and wrappers must bind the same run/candidate/host. Preserve submitted original bytes, including failed JSON/report, rather than normalizing away discrepancies.
8. Seal Blue's own reception record with final E1, M1, V1, activation and schema digests, exact review findings and run status. Publish only opaque digests, classifications and governance disposition; raw state, machine identity, requester secrets, filing content/locators/count proxies remain restricted.

## 8. Machine-validation and semantic review sequence

These are future read-only review steps on restricted evidence copies, not executed host instructions. Do not run the operator's campaign or candidate scripts as part of reception.

1. Verify bytes/authority and run history from sections 3 and 7 before accepting any operator verdict. Preserve receipt timestamp and exact received artifact digest independently of its claimed timestamp.
2. Parse JSON strictly: reject duplicate object keys and non-JSON NaN/Infinity; validate the pinned schema itself with a draft-2020-12 validator. Enable `date-time` format validation and separately require UTC. Record validator implementation/version and schema byte digest. No remote schema resolution or installing software on the qualifying host is needed.
3. Validate each sealing-stage/final artifact against the activated schema, with no mutation/default insertion/coercion. Preserve exit status and all schema errors as a hashed restricted report. A future review workstation with an already available `jsonschema` package can use the read-only core below; the review pipeline supplies the two exact file paths. It does not fill missing evidence.

```python
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('non-JSON constant: ' + value)


def read_json(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


schema = read_json(sys.argv[1])
evidence = read_json(sys.argv[2])
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
errors = sorted(validator.iter_errors(evidence), key=lambda e: str(list(e.path)))
for error in errors:
    print(list(error.path), error.message)  # restricted report only
raise SystemExit(1 if errors else 0)
```

4. Check root required fields and all B1–B10 artifact coverage using sections 4–6. Explicitly inspect B9, actual operational fields behind verdict objects, exact CI IDs/verdicts, nonce/run uniqueness, full campaign coverage, zero-network attempt handling, and sub-artifact defect classes: these are not all enforced by schema.
5. Verify the entire digest graph, external event chronology and pre/post inventory reconciliation. Require all mandatory domain verdicts PASS and no unresolved mandatory anomaly before marking eligibility. A schema-valid BLOCKED or FAILED_TERMINAL artifact is valid failure reporting, not PASS eligibility.
6. On failure preserve original final artifact, all red sub-artifacts, manifest, validator errors, action chronology, activation/consumption record and safe-shutdown evidence. Missing final sanitization after an early terminal stop must remain explicit UNKNOWN/BLOCKED; do not continue destructive tests merely to complete a green matrix. Return to Blue for disposition. A receipt/format correction can be separately documented without authorizing retry or rewriting original evidence; an actual mandatory FAIL cannot be repaired within the run.
7. Blue records PASS or BLOCKED only after full review; track FAILED_TERMINAL separately where applicable. Even future PASS leaves t0 undeclared, Product paused and real capital unauthorized. Runbook phases 9 onward need their own prospective precommit/launch authority; no autonomous continuation from this review.

## 9. Minimal future Blue reception record

This is an unfilled governance template, not an instance of the evidence schema and not evidence. Place sensitive references/results in restricted storage; public projection uses only safe opaque references and disposition.

```text
BLUE_GATE_B_RECEPTION_VERSION = <Blue-approved version>
BLUE_REVIEW_TIMESTAMP_UTC = <attributable UTC>
BLUE_AUTHORITY_REFERENCE = <immutable decision authority>
GATE_B_RUN_ID = <exact sealed run ID>
GATE_B_ATTEMPT_NUMBER = <positive integer>
OPERATOR_IDENTITY_REFERENCE = <restricted ref>
TARGET_HOST_OPAQUE_ID = <activation match>
FINAL_ENTRANCE_REFERENCE / SHA256 = <E1 ref / exact bytes>
ACTIVATION_REFERENCE / CANONICAL_DIGEST / CANONICAL_RULE = <sealed values>
CONTRACT_REFERENCE / DIGEST = <activated values>
RUNBOOK_REFERENCE / DIGEST = <activated values>
SCHEMA_REFERENCE / DIGEST = <activated values>
HYBRID_AMENDMENT_REFERENCE / DIGEST = <activated values>
CANDIDATE_SHA / GIT_TREE / VERIFIED_INPUT_TREE_DIGEST = <exact triple>
REPOSITORY_CI / INDEPENDENT_REVIEW_HEAD_AND_CI = <verified exact bindings>
MANIFEST_REFERENCE / DIGEST = <M1>
FINAL_VALIDATION_REFERENCE / DIGEST / VALIDATED_E1_DIGEST = <V1>
SCHEMA_VALIDATION = <PASS|FAIL|UNKNOWN, report ref>
ACTIVATION_AND_IDENTITY_MATCH = <PASS|FAIL|UNKNOWN, refs>
ARTIFACT_CHAIN_AND_RETENTION = <PASS|FAIL|UNKNOWN, refs>
RUN_HISTORY_AND_REUSE_DISPOSITION = <none or exact Blue ref and scopes>
B1 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B2 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B3 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B4 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B5 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B6 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B7 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B8 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B9 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
B10 = <PASS|FAIL|UNKNOWN; defect class; evidence refs; explanation>
TIME / RESOURCE / NETWORK / RETENTION = <each verdict and refs>
REAL_SEC_REQUESTS_MADE / OBSERVATION_COVERAGE = <observed value / evidence>
UNEXPECTED_REAL_SEC_ATTEMPTS = <observed result / evidence>
PRE_INVENTORY / POST_INVENTORY / DELTA_LEDGER_DIGESTS = <digests>
SANITIZATION_REFERENCE / DIGEST = <exact final state identity seal>
FIRST_MANDATORY_FAILURE / PRESERVED_RED_CHAIN = <none evidenced or refs>
GATE_B_RUN_STATUS / ACTIVATION_CONSUMPTION = <supported status / record>
UNRESOLVED_MANDATORY_ITEMS = <explicit list or evidenced none>
BLUE_GATE_B_DECISION = <PASS|BLOCKED, only after Blue review>
BLUE_REASON_AND_NEXT_AUTHORIZED_ACTION = <explicit scope>
t0_declared = false
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 10. Delivery and return to Blue

Preparation is complete for review. Before activation, Blue must resolve canonical byte/seal rules and acyclic validation-report sequencing, bind a real restricted evidence root, receive the other preparation lanes, and authorize the exact supported transition/synthetic-separation procedure. These are future activation inputs; their absence is not fabricated as a Gate-B failure or PASS in this prestage. If absent at actual reception, they block eligibility.

Delivery scope: this handoff only. No production source, tests, scripts, schemas, workflows, authoritative governance schema, qualifying release/state, systemd or mounts changed. No destructive campaign or real SEC request executed by this lane. The required origin fetch and repository preparation took place in development checkouts; final work is isolated on the same named authorized branch.

Validation of this delivery: required schema-field map checked against the unchanged schema; exact preparation authority hashes checked; all ten matrix domains, mandatory semantics and future template reviewed; Git whitespace/scope checks run. The embedded read-only validation example is syntax-checked only; it has not validated future evidence, which does not yet exist.

`GATE_B_RECEPTION_PRESTAGE = READY_FOR_BLUE_REVIEW`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

Control returns to Blue for reception-criteria review and convergence. This handoff grants no target-host mutation authority.
