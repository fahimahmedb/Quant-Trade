# Astra independent Gate-B V4 transition preactivation review

`ASTRA_GATE_B_PREACTIVATION_REVIEW = BLOCKED_SCHEMA_FALSE_PASS_AND_UNSEALED_OPERATIONAL_PROOF`

Return owner: **Blue / Mission Control**. This is an independent review of the
preactivation pack, not a Gate-B execution result. No findings were fixed.

## Scope and provenance

FACT: authorized branch is
`astra/gate-b-v4-transition-independent-preactivation-review-2026-09-21`.
Starting HEAD verified after `git fetch origin --prune`:
`6937732ce55c18a7674d2929864e8405af4fef75`.
User-specified Blue baseline: `ba510bd5e3077c7e29b35aef9cf45c98a5fd128c`.
The start differs from that baseline only by the Astra mission document. The
mission's older expected-start wording is therefore not a candidate substitution.
The dispatch records its own earlier Blue baseline `4c855dca...`; this review
uses the user's explicit starting HEAD and exact document bytes below.

North Star, dispatch and mission were read first, followed by all six primary
authorities. Builder materialization-prestage conclusions were never read or
used. No other lane's acceptance matrix was used. Supporting deployment contract
and t0 template were inspected independently.

Primary authorities at starting HEAD (SHA-256 of file bytes):

| governance file, all dated 2026-09-21 | SHA-256 |
| --- | --- |
| P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT.md | e3dddcc4936b626fac3f6fad3a1d0bbd821ef4af24806c6532d94d638b4a7a73 |
| TARGET_HOST_GATE_B_ENTRANCE_CONTRACT.md | e3f805a6d3e6f72e3dc0cd79670a1134569a0c6a8bc0f7e6229ed725468b5477 |
| TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK.md | 7db5a567a60b1be325d0719341ab2a997a6c9f33f371fe53e11a3aa11f4a9ad2 |
| BLUE_GATE_B_ACTIVATION_TEMPLATE.md | 93cdce6b73506850296173f2cf09c616f7fa59b5557379be05d6dfdac406c52d |
| TARGET_HOST_GATE_B_EVIDENCE_SCHEMA.json | 145293a685ca412141b78889eb25eed60cf1e33a850e41a2bd10456faf7c5fde |
| TARGET_HOST_V4_RELEASE_MATERIALIZATION.md | 78ecbbb79a2c38468681be94680a88d0b8de183df6cbb8bf2785a589beea4adf |

FACT: the public Operator handoff was read from exact commit
`44285788fce3d5d048b037dd8d1089e1f08f43e9`, path
`handoff/OPERATOR_GATE_B_READ_ONLY_PREFLIGHT_2026-09-21.md`, verified Git blob
`48dfd849095362b924412f474a641010addd3406`.
CLAIM (Operator's host observations, not newly executed by Astra): V4 absent;
service view on rejected V3; service failed/disabled; loaded unit matches V4;
state views share filesystem identity; evidence root unbound; no mutation.
FACT: these statements and their explicit limitations appear in that handoff.
UNKNOWN: current host state and retrievability of its session-only raw snapshot.

Environment incident: no checkout existed under /home/ubuntu. An isolated clone
was made in /tmp and verified. An external process subsequently switched that
clone to a Builder branch and staged an unrelated mission file. Astra did not
perform that checkout or alter its staged work. A fresh clone under
/home/ubuntu/astra-independent-6937732-review was created on the SAME authorized
Astra branch. Exact primary input bytes and every schema result were reverified
there before writing this handoff. No new branch was created by Astra.

FACT: the governance branch's supervisor bytes differ from frozen V4. Supporting
runtime conclusions below were checked using `git show` of frozen
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`, whose tree is
`4d15ef6f471213ee6ab56337b555d2906ef9bf16`. The governance checkout is not a
release source merely because it carries V4 governance.

## Findings

### F1 — contradictory and incomplete evidence can validate as PASS

Classification: **REAL_DEFECT**. Domain: evidence schema, not production runtime.
Blocking for activation/reception as presently specified.

FACT: schema `properties.independent_review` requires only review_head and a
nonempty verdict; ci_runs is optional. `sub_artifacts` requires only one generic
entry, permits REAL_DEFECT/MISSING_PROOF/UNKNOWN classifications, and does not
require a retrievable reference. The PASS conditional constrains domain verdicts
and defect classifications, but not independent_review or sub_artifacts.

FACT: an independently constructed artifact validates with overall PASS,
independent review verdict FAIL, CI run 1, all-zero syntactic hashes and an
UNKNOWN/REAL_DEFECT sub-artifact. No independent CI runs, boot ID, actual runtime
identity, loaded properties, state inventory, active/materialized fingerprint
values, B9 authority test, individual B1-B10 records, or release-materialization
artifact is supplied. All mandatory domain envelopes exist, but contain only a
verdict, digest and classifications. Setting a domain classification to UNKNOWN
also validates. Appendix A reproduces this with format checking enabled.

INFERENCE: a consumer equating machine validation with evidentiary completeness
can present a misleading PASS. The contract's human review still prohibits it;
this is not proof that Blue would accept it. Hash syntax cannot prove referenced
bytes, and JSON Schema alone cannot authenticate external evidence.

RECOMMENDATION: Blue must require a complete, explicit semantic acceptance
procedure and resolve the schema's internal contradictions/mandatory proof
coverage before activation. This review does not implement that change.

### F2 — cross-run laundering, collision and terminal-run reuse lack a bound check

Classification: **MISSING_PROOF**. Blocking operational acceptance proof.

FACT: contract 17.2/17.8 requires unique run IDs, immutable failed evidence and
run-bound sub-artifacts. Activation sections 4/6 invalidate reused or failed IDs.
But the schema only requires an eight-character run ID and positive attempt
number. Sub-artifacts carry neither run ID nor activation digest; manifest
membership, digest resolution and authority history are not checked by schema.
Changing only the top-level run ID while reusing all hashes validates, as do
duplicate artifact entries. No immutable run allocation/consumption registry or
serialized reservation/check procedure is bound by the activation template.

INFERENCE: concurrent allocation, recycled FAILED_TERMINAL evidence or a relabeled
old run can pass structural validation. This is not a reproduced runtime replay;
B9's qualifying-launch nonce is a different authority from a Gate-B run ID.

RECOMMENDATION: require positive evidence of unique reservation, current Blue
activation status, durable consumption/terminal history, immutable red retention,
and resolved per-artifact run/activation/host binding. Any permitted prior PASS
reuse needs the explicit Blue disposition required by the contract.

### F3 — activation does not seal the whole executable authority surface

Classification: **MISSING_PROOF**. Blocking until a concrete activation closes it.

FACT: activation section 1 seals hybrid amendment, contract and runbook but has
no explicit required schema digest, release-materialization procedure digest,
exact transition command-plan digest, synthetic reservoir binding, evidence-root
binding, or permitted mount source/destination matrix. Section 2 grants broad
mutation classes. Runbook 0A requires resolving the activated schema and 0B the
activated materialization procedure, without a matching explicit template field.

INFERENCE: a valid-looking seal can leave the operator choosing consequential
mount/state operations or a changed schema after authorization. The template's
expiry section supplies invalidation events, not a fixed expiry or mandatory
current revocation check. An old unconsumed activation can therefore remain
apparently usable after unbound environmental drift. No universal time-to-live
is assumed to be required; the missing item is an unambiguous freshness policy.

RECOMMENDATION: Blue's concrete seal must bind these choices, allowed effects,
preconditions, freshness/revocation evidence and evidence-safe stop behavior.
Booleans alone are insufficient review evidence for this transition.

### F4 — exact V3-to-V4 and state/mount sequence remains unproven

Classification: **MISSING_PROOF**. Blocking before transition authorization.

FACT: materialization sections 3/5/6/7 prohibit overwrite, mutable backing,
state deletion and service start during materialization. The deployment contract
requires stopping the old writer, preserving the same state volume, external
mount ordering and no live bind replacement. Runbook 0B creates/verifies the
release but does not supply the concrete nested-mount transition procedure.
Operator R3 establishes the starting mismatch, not its safe resolution.

FACT: frozen V4 unit orders after network-online, not the state mount. The
supporting deployment contract explicitly admits mount enforcement is external.
Frozen V4 supervisor main creates var/sec and a lock file after environment
validation; it is not independent proof of durable mount identity.

INFERENCE: parent-view replacement can obscure the nested state view; an
underlying writable directory could be mistaken for preserved state; a reboot
could start before the required mounts. Equal filesystem identity alone does
not establish equal state directory/content. These are attack hypotheses, not
claims that such loss occurred.

RECOMMENDATION: require a sealed sequence with observed stopped/no-writer
preconditions, exact source/root identity, preserved pre/post inventory, nested
mount handling, external ordering and missing-mount denial, including reboot.
Do not roll back by restarting rejected V3. Preserve evidence and stop on failure.

### F5 — offline destructive campaign and sanitization lack a proven mechanism

Classification: **MISSING_PROOF**. Blocking under contract 17.7 and runbook 7A.

FACT: B8 and runbook 6 demand real-systemd lifecycle tests on synthetic/offline
state; B10 demands separation from the preserved future qualifying reservoir.
Frozen service ExecStart is the qualifying supervisor at /opt/quant. There is no
concrete supported reservoir/transport isolation procedure in these authorities.
A synthetic directory for filesystem tests alone does not make the actual
service's SEC transport synthetic.

INFERENCE: starting the exact service with its private requester configuration
could contact SEC; substituting its root/environment/unit could test a different
binding; reusing destructive journals could contaminate future state. Simply
removing credentials may prove refusal, not a full successful lifecycle campaign.

RECOMMENDATION: require the exact supported isolation mechanism, negative real
network test and observation, equivalence limits, preserved-state protection,
and pre/post sanitization proof before any such start. Unsupported path swaps,
manual journal cleanup and hand-edited authority are already prohibited. STOP
is the correct present behavior, not improvised execution.

### F6 — evidence retention and preflight reproducibility remain open

Classification: **MISSING_PROOF**. Blocking before relying on final evidence.

FACT: Operator handoff section 0 says raw snapshot existed only in its session;
R5 says evidence root NOT_YET_BOUND. Contract 17.4 requires persistent restricted
storage, journal retention and a hash-addressable manifest. Public hash alone
cannot retrieve the snapshot. R8 explicitly says metadata digest is not state
validity proof. R6 has no live RSS/FD baseline.

UNKNOWN: whether a retrievable restricted copy exists elsewhere. Do not call it
lost as a fact. Journald usage is not proof of persistence across reboot, freedom
from destructive rotation, or sufficient retention through Gate D.

RECOMMENDATION: require retrievable restricted artifacts, manifest closure,
permissions, persistent journal/boot evidence and reviewed headroom; repeat
activation-time observations where needed. Do not publish raw state to repair
this proof gap. A stopped-service baseline must not be represented as measured
running-process health.

### F7 — read-only label on git status is not an enforced no-write guarantee

Classification: **TEST_DEFECT**. Non-blocking to this independent review; must be
resolved in any strictly read-only executable preflight.

FACT: runbook phase 1 labels its commands read-only but invokes plain
`git status --porcelain=v1` without suppressing optional index writes. Git status
can refresh index metadata; clean output is not a byte-for-byte tree verifier.
No target release command was executed by Astra to demonstrate a target write.
INFERENCE: the label overstates command behavior if Git metadata is writable.
This is not a demonstrated preauthorization bypass: phase -1 and phase 0A still
explicitly forbid mutation before a valid seal, and phase 1 says when authorized.
RECOMMENDATION: make no-write behavior explicit in the eventual command plan and
prove deployed bytes independently of cached status/index flags and ignored files.

## Attack coverage and negative results

Each row below has one exact classification. These do not waive F1-F6.

| Attack | Classification | Evidence type and disposition |
| --- | --- | --- |
| SHA-named wrong release / stale committed verification JSON | NON_ISSUE | FACT: materialization 1-4 requires exact SHA/tree, self-contained Git and correct CI input digest; path name and stale committed JSON expressly insufficient. Actual deployed byte proof remains required. |
| Mutable backing tree / hidden writable production alias | TARGET_HOST_ONLY | FACT: materialization 5 and contract B1 explicitly forbid it, including backing path. UNKNOWN: actual ownership, aliases, effective write access, ignored/untracked code and mount protection. Read-only service view alone fails the stated requirement. |
| Linked worktree, .git indirection, alternates, mutable object dependency | NON_ISSUE | FACT: materialization 2-3 prohibits dependent final forms and requires self-containment. No prose loophole found; inspect actual object completeness and environment-based dependencies before acceptance. |
| Unsafe transition, state loss and mount ordering | MISSING_PROOF | F4; never infer root identity from shared filesystem alone. |
| Real SEC request during destructive tests | MISSING_PROOF | F5; prohibition exists, isolation proof does not. Schema correctly rejects a PASS with request count 1. |
| Overbroad capabilities / stale activation | MISSING_PROOF | F3; missing fields default FALSE, but TRUE needs concretely bounded effects. |
| Commands before authorization | NON_ISSUE | FACT: activation seal and phase -1/0A prohibit them, including evidence-root creation. No authority from branch/chat/CI. F7 identifies a command-label weakness, not permission to run it. |
| Missing mandatory fields / contradictory schema PASS | REAL_DEFECT | F1 and Appendix A. |
| Cross-run laundering / terminal run reuse / run-ID collision | MISSING_PROOF | F2; textual prohibition is present, registry and resolved chain proof absent. |
| Sanitization / synthetic qualifying-state contamination | MISSING_PROOF | F5; B10 and 17.7 fail closed on ambiguity. |
| Journal loss or rotation / restricted evidence loss | MISSING_PROOF | F6; no admissible inference from absence of observed errors. |
| Time/NTP ambiguity | TARGET_HOST_ONLY | FACT: contract 17.3, runbook 2A/9A, t0 template 11 require synchronization, clock correlation and rechecks. Operator R1 is a snapshot CLAIM, not proof through later reboot/precommit. |
| Reboot evidence ambiguity | TARGET_HOST_ONLY | FACT: B2/B8 require acknowledged-state survival and attributable transitions. UNKNOWN: paired boot IDs, journal persistence, monotonic clock epochs and mount-before-service ordering. A changed boot ID alone is insufficient. |
| t0 precommit bypass / retrospective selection | NON_ISSUE | FACT: amendment C0, runbook 8-10A and precommit template 3-6/10-13 require prior seal, unique consumed authority and external launch timestamp; mismatch or prior launch invalidates. Gate-B green cannot declare t0. No textual retrospective-selection loophole found. |
| Contract/runbook/schema/template mismatch | REAL_DEFECT | F1 mandatory proof coverage mismatch; F3 separately identifies unsealed authority choices. |
| Authorized real-network exception versus schema | TEST_DEFECT | FACT: contract 17.5 and activation 2 permit separately authorized test-specific traffic, while schema PASS requires exactly zero. This fails safe but cannot represent that exception without explicit supersession. Default zero-network campaign remains the required current path. |
| Governance checkout mistaken for frozen runtime | NON_ISSUE | FACT: exact V4 is pinned independently; governance supervisor differs. Never execute this audit branch as V4. No claim of a new frozen-V4 regression follows. |

## Appendix A — independent executable schema falsifier

FACT: executed locally with Python 3 and jsonschema 4.10.3,
Draft202012Validator with FormatChecker, against the exact schema hash above.
No Quant imports, service start, SEC calls, mount commands or state access.
All digests/identities below are deliberately fabricated. This is not host evidence.
Run from the pinned repository checkout; script writes nothing.

```python
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

s = json.loads(Path(
    'governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json'
).read_text())
Draft202012Validator.check_schema(s)
v = Draft202012Validator(s, format_checker=FormatChecker())
h = 'sha256:' + '0' * 64
p = {}
for key in s['required']:
    spec = s['properties'][key]
    if 'const' in spec:
        p[key] = spec['const']
    elif spec.get('$ref') == '#/$defs/sha256':
        p[key] = h
    elif spec.get('$ref') == '#/$defs/verdict_object':
        p[key] = dict(verdict='PASS', evidence_digest=h,
                      classification='FACT', defect_classification='NON_ISSUE')
    else:
        p[key] = 'placeholder'
p.update(
    created_at_utc='2026-09-21T12:00:00Z', gate_b_run_id='audit-run-0001',
    gate_b_attempt_number=1, repository_ci_runs=[1],
    independent_review=dict(review_head='0'*40, verdict='FAIL'),
    synthetic_campaign_network_activity=dict(
        real_sec_requests_made=0, verdict='PASS', evidence_digest=h),
    sub_artifacts=[dict(name='placeholder', digest=h,
                        classification='UNKNOWN', defect_classification='REAL_DEFECT')],
    overall_verdict='PASS')
cases = {'minimal_missing_proofs_and_failed_review': p}
q = copy.deepcopy(p); q['runtime_identity']['classification'] = 'UNKNOWN'
cases['unknown_classification_with_pass'] = q
q = copy.deepcopy(p); q['gate_b_run_id'] = 'audit-run-0002'
cases['relabel_run_without_rebinding_evidence'] = q
q = copy.deepcopy(p); q['sub_artifacts'] *= 2
cases['duplicate_artifacts'] = q
q = copy.deepcopy(p); q['time_authority']['verdict'] = 'FAIL'
cases['control_domain_fail'] = q
q = copy.deepcopy(p); del q['time_authority']
cases['control_missing_domain'] = q
q = copy.deepcopy(p); q['synthetic_campaign_network_activity']['real_sec_requests_made'] = 1
cases['control_real_sec_request'] = q
q = copy.deepcopy(p); q['t0_declared'] = True
cases['control_t0_true'] = q
q = copy.deepcopy(p); q['candidate_sha'] = '0'*40
cases['control_wrong_candidate'] = q
q = copy.deepcopy(p); q['runtime_identity']['defect_classification'] = 'MISSING_PROOF'
cases['control_domain_missing_proof'] = q
for name, payload in cases.items():
    print(name, 'ACCEPTED' if v.is_valid(payload) else 'REJECTED')
```

Observed output:

```text
minimal_missing_proofs_and_failed_review ACCEPTED
unknown_classification_with_pass ACCEPTED
relabel_run_without_rebinding_evidence ACCEPTED
duplicate_artifacts ACCEPTED
control_domain_fail REJECTED
control_missing_domain REJECTED
control_real_sec_request REJECTED
control_t0_true REJECTED
control_wrong_candidate REJECTED
control_domain_missing_proof REJECTED
```

The controls establish sensitivity to existing restrictions. The four accepted
cases establish structural acceptance only, not successful external evidence
verification or an actual accepted Gate-B run.

## Blue reception and boundaries

RECOMMENDATION: withhold activation until F1's acceptance defect and F2-F6's
operational proof gaps are resolved in an exact sealed successor/concrete plan
and independently reviewed. Actual host-only checks must still occur within
Blue's single authorized run. A later Builder prestage may supply missing proof;
this report neither assumes nor assesses that outcome.

No production code, schema, governance contract or target runtime was changed.
Only this audit handoff is delivered. No target service/state/mount/release,
requester, reboot or lifecycle operation was performed. Repository clones,
fetches and local fabricated-data validation are audit preparation only.

```text
TARGET_HOST_MUTATION_PERFORMED = FALSE
PRODUCTION_CODE_MODIFIED = FALSE
FINDINGS_FIXED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE = 0
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
RETURN_CONTROL_TO = BLUE
ASTRA_GATE_B_PREACTIVATION_REVIEW = BLOCKED_SCHEMA_FALSE_PASS_AND_UNSEALED_OPERATIONAL_PROOF
```
