# Quant-Trade — Vertical Depth Phase-A manifest

BASE_SHA=01c2e520fa4116645870f96acf6770ea83f1881c
FINAL_SHA=21a16038e4d712adf3c9d9cb0c71f03f79de25cd
CHECKPOINT_LABEL_COUNT=100
REPAIR_BEARING_CHECKPOINT_COUNT=43
INSUFFICIENT_DEPTH_LABEL_COUNT=56
CP100_DEPTH_COMPLETION=FALSE
OWNER_GOAL=SUBSTANTIVE_DEPTH_NOT_FILENAME_QUOTA
MISSION_ACTIVE=TRUE
LAST_REBUILT_SEQUENTIAL_CHECKPOINT=CP043
PHASE_A_COMPLETE=FALSE
BRANCH=codex/vertical-depth-prewave2-20261021
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

**Historical correction at bd86b47 (superseded in part by rebuilding below):**
CP038–CP060 and CP062–CP100 were 62 diagnostic labels,
not accepted vertical-depth checkpoints. They replay existing suites under runtime
variants and do not contain the required new implementation descent/falsification
investigation. Their previous D2-requalification wording is withdrawn. Reaching
the CP100 filename did not fulfill the requested substantive depth campaign.
CP061 contains one reproduced defect, six new cases and a narrow repair. The
39 scoped-unit counts below come from repair-bearing work; the 62 diagnostic
labels add no units or depth. The earlier delivery overstated progress by using
checkpoint numbering as evidence of substantial work. See VERTICAL_DEPTH_CLAIM_CORRECTION_20261023.md.

`FINAL_SHA` is the exact **qualified executable/source revision**. This manifest,
full-SHA checkpoint normalization, coverage table and final transcripts are
committed in a documentation/evidence-only child so the manifest need not claim
its own unknowable Git hash. The delivered branch tip is that child; its source
and test/schema bytes must match the 78 fingerprints in
`research/vertical_depth/20261021/FINAL_qualification.json`.


**Subsequent rebuilding after Owner clarification:** “until CP100” meant sustained
substantive work, not a filename quota. The mission is active; the numbered labels
are not a stopping/completion criterion. CP038–CP041 now replace their old replay
entries with implementation-specific evidence: 116 newly added cases, actual
process-death/restart tests, three grouped frozen-plan weaknesses and two shared
input-snapshot repairs. Before failures are CP038 64/73, CP040 6/10, CP041 11/16;
CP039's 17 new process cases reproduce no defect. Fifteen deliberate guard removals
are detected by the new fixtures. Focused counts overlap the full regression.

There are now 42 substantive scoped checkpoint entries (CP001–CP041 plus the
previous out-of-sequence CP061); 41 contain repair items and CP039 has no reproduced
defect. These are bounded claims, not independent whole-module qualifications.
The remaining CP042–CP060 and CP062–CP100 (58 labels) remain rejected as depth
checkpoints. Earlier correction paragraphs below describe the prior delivery;
they do not retroactively validate the discarded replay work. Next work must
continue implementation-specific descent rather than fill these filenames.

MODULES_TOUCHED=29
SOURCE_FILES_CHANGED=30
SCHEMAS_CHANGED=1
CAPABILITIES_DEEPENED=43

Modules: Book; canonical Research Core; evidence storage; learning; shared state
journals; RISK; local Campaign/Queue; model execution; PIT corporate actions;
closed decay admission; exact-source qualification; DeskJournal; scientific
snapshot ledger; historical memory; Red Team; PricePanel; acquisition firewall;
typed PIT registry; source route qualification; implementability; structural
portfolio diagnostics; Edge Lab store; ForwardRegistryV2; Git state transactions; standalone experiment freeze snapshots; design-only adapter qualification;
documentary plan/execution runner; pre-outcome observability projection; PIT identity assertion contracts.
These are logical module slices, not 29 whole-module deep qualifications. No later
canonical movement was followed, no active rail/Oracle/Site was modified, and no
future Wave-2 module was built.

D1_COUNT=0
D2_COUNT=24
D3_COUNT=12
D4_COUNT=7

Counts describe the 43 newly deepened **scoped capability units** in
`VERTICAL_MODULE_COVERAGE_20261021.md`, counted once at their maximum demonstrated
depth. They are not full-module qualifications. D4 applies to tuple/serializer
outcome-guard composition, optimized-interpreter closed decay admission, and the
Book/DeskJournal mutation-failure/identity-read compositions in CP016, plus the
internal acquisition plan/content/proof-replay composition in CP022. CP032
promotes the existing Forward registry unit for its tested input/authority/save
composition; CP034 adds the documentary execute/PREPARED/COMPLETED/retry unit.

DEFECTS_REPAIRED=109

This is the number of enumerated repair items in 43 repair-bearing checkpoint
groups, not 109 independent root causes or scientific observations. CP039 is
additional no-defect process-recovery evidence. There remain 56 insufficient-depth
runtime replay labels; their numeric presence is not mission completion. Shared roots and related
manifestations remain grouped and explained in each checkpoint:

| Checkpoint | Repair items | Evidence/repair |
| --- | ---: | --- |
| CP001 | 4 | Book failed-write retry; stale overwrite fencing; invalid fill/mark admission; detached write denial |
| CP002 | 2 | Stable reconstruction hashes; tuple-hidden outcome rejection at both existing Core entrypoints |
| CP003 | 4 | Unique evidence staging; serialized index publication; exact typed references; nonfinite record rejection |
| CP004 | 2 | Ticket replay beyond 200 retained lessons; failed-save recovery |
| CP005 | 3 | Torn UTF-8 recovery; consistent newline visibility; no mutation by rejected append |
| CP006 | 1 | Numerical fail-closed RISK through every existing public entrypoint |
| CP007 | 4 | UTC-instant scheduling; failed-add recovery; durable unique staging; schema/duplicate-ID rejection |
| CP008 | 3 | Positive capacity evidence; causal fill clocks; model/numeric admission |
| CP009 | 2 | Finite action consideration; UTC ordering/tie-breaking |
| CP010 | 1 | Explicit closed decay admission surviving normal/-O/-OO execution |
| CP011 | 2 | Qualification-to-actual-HEAD binding; dirty executable rejection |
| CP012 | 6 | Frozen Desk intent/reopening; completion binding; alias isolation; failed-write recovery; stale publication fencing; terminal/recency admission |
| CP013 | 1 | Exact economic payload bound to each durable Book replay token, with explicit legacy proof limits |
| CP014 | 2 | LearningStore stale-writer fencing and whole-mutation thread isolation through publication/recovery |
| CP015 | 3 | Queue stale/terminal fencing; shared-instance isolation; document-preparation and lock-setup recovery |
| CP016 | 6 | Book/Journal shared-writer recovery, lock-setup retry and guarded durable identity reads |
| CP017 | 4 | Detached scientific ledger snapshots; strict chain admission; atomic publication/retry; serialized append |
| CP018 | 3 | Canonical checkpoint replay identity, strict immutable JSON, serialized artifact registry |
| CP019 | 3 | Detached historical truth, explicit conflicting identities, malformed corpus denial |
| CP020 | 3 | Monotonic Red Team denial, frozen input check, unqualified context denial |
| CP021 | 3 | Detached date caches, duplicate evidence preservation/export denial, split admission |
| CP022 | 4 | Nested outcome keys, qualified clocks/values, plan identity/closed flags, exact internal proof binding |
| CP023 | 3 | Typed/manifest verification, alternate-API outcome denial, concurrent registry fencing |
| CP024 | 3 | Route text admission, reconstructed freeze-context proof, serialized qualification registry |
| CP025 | 2 | Nested unknown exact requirements and unqualified complexity |
| CP026 | 2 | Explicit scoped negative identity/reason and context/list shape |
| CP027 | 3 | Conservative partial/conflicted structure, tuple/list membership identity, scalar tag denial |
| CP028 | 2 | JSON overflow denial and exact schema/event integer identity |
| CP029 | 3 | Forward identities, exact zero consumption, concurrent generation uniqueness |
| CP030 | 1 | Canonical Git write path admission before commit acknowledgement |
| CP031 | 2 | Detached frozen protocol/caller identity and explicit nonfinite-protocol freeze denial |
| CP032 | 3 | Detached Forward, typed PIT and source qualification admission inputs; Forward authority race denial |
| CP033 | 3 | Qualified adapter text, reproduced design-only proof and serialized immutable registry |
| CP034 | 1 | Detached documentary execution body matches PREPARED through completion and ACK loss |
| CP035 | 1 | One immutable input bundle across pre-outcome scan and final qualification |
| CP036 | 2 | Forbidden content checked outside raw payload and in complete typed/provenance extensions |
| CP037 | 1 | Nested plan environment and metric identity detached before hash construction |
| CP038 | 3 | Reconstructed frozen admission; duplicate identity agreement; stable checked plan reference |
| CP040 | 1 | Direct export checks and freezes one captured input body |
| CP041 | 1 | Shared Core builder input/identity snapshot defect across five proven entrypoints |
| CP042 | 3 | Campaign stale-writer fencing; failed-save/shared heartbeat recovery; unambiguous finite durable JSON |
| CP043 | 2 | Frozen PIT lineage/action sequence capture; refusal of ambiguous containers found after first repair |
| CP061 | 1 | Observability displays the detached body that passed the pre-outcome scan |

All repairs have concrete pre-repair failures and focused requalification.
Full before/after transcripts and checkpoint source SHAs are durable under
`research/vertical_depth/20261021/`. The new tests add **992 cases**. Existing
canonical Research Core fixture hashes and valid model behavior remain compatible;
CP022's typed/provenance hash extension is explicit below. Stricter rejection and
explicit write conflicts are intentional.

Material compatibility limit: CP013 adds the optional `operation_fingerprints`
Book field and regenerates its schema. Legacy Books remain readable; an already
applied legacy ID without a recoverable payload proof now blocks replay instead
of claiming a match. No fingerprint is fabricated and no active Book is migrated.
Older consumers require coordinated schema adoption before using these artifacts.

Continuation from delivery `9355b4e1351b0a730bf69369c4bf2fdac34f0f2c` retained
the same immutable Phase-A base and branch. CP018–CP031 add **409 cases**, including
45 supplemental survey controls. These 45 controls do not add whole-module depth
labels or inflate the 34 scoped qualification units. The 25 existing CP085 North
Star nodes have a documented routing/reacquisition pass; that is not exhaustive
qualification of every capability/function. See `VERTICAL_SYSTEM_SURVEY_20261021.md`.
Earlier manifests and receipts remain in Git history.

Continuation on 2026-10-23 from delivery
`44bc9206b009c1ba1e3c96f480f820fd4c5ff9e7` keeps the same base and branch.
CP032–CP037 add **72 adversarial/control cases**. Forward input mutation could
import an authorized registry state after checks; the pre-outcome pipeline could
reread injected forbidden content after its initial scan. Both internal bypasses
are repaired without granting Owner authority or consuming an observation.
Typed/source/design admission, documentary durable execution and planning now
validate and retain detached input bodies. Whole-batch atomicity was not assumed
or built: valid prefixes and idempotent resume retain their existing semantics.
At CP037, depth counts covered 38 scoped units; earlier summaries remain in history.


Owner stop continuation from delivery `97d2da61e93ac22b47a6d68be99d72efc574ba4a`:
CP038–CP100 execute 63 existing scoped test surfaces under ordinary Python with
PYTHONHASHSEED=0 and Python -OO with PYTHONHASHSEED=1729. All 126 invocations pass:
714 overlapping existing tests per mode. They are reused tests, not 714 new cases,
63 repairs, or 63 additional capability counts. Paired logs retain their actual
source SHA; their index records exact commands, imports, test names and test-file
fingerprints. Optimized parent tests do not imply every explicit child command
uses -OO. These runtime replays add no new depth qualification. The former D2 wording is withdrawn.

CP061 adds six new deterministic cases. Five failed against the exact previous
observability module: mutation after the content scan could change readiness,
remove blockers, alter support/Validator status, or inject a returns-bearing claim
ceiling into the pre-outcome output. The input tuple is now detached before the
scan, so the displayed body is the scanned body. Focused standard and -OO runs
both pass 37 tests plus 28 subtests. This is one repair and one scoped D2 unit;
the whole remote projection/delivery path is not qualified. The other 62 numbered entries contain no newly constructed adversarial cases
and are insufficient for the requested vertical checkpoint standard.

The CP100 numeric label was reached, but the substantive depth target was not
met. Work remains stopped under the Owner's instruction; no CP101 is opened.
The stop and the filenames must not be presented as depth completion.


An executor restart removed temporary transcripts before delivery. CP018–CP029
pre-repair failures were reproduced by restoring each exact historical module
version in isolation, with the other source files at `ea50f6cf1caa1eba6eb141d9d62aa0107de91300`,
then restoring the repaired bytes. Focused and full suites were rerun. Those
transcripts and their reconstruction scripts/provenance are now durable. No lost
transcript is represented as retained evidence. CP030 uses its original preserved
before/after transcript and real disposable local Git remotes. CP031 separately
replays its exact previous module version; its diagnostics remain distinct from
whole Factory durable freeze qualification.

Material compatibility additions: CP022 binds original `raw_record_hash` into the
typed acquisition body, intentionally changing those typed/provenance hashes;
CP023 rejects old typed bodies lacking that proof. CP024 immutable qualifications
bind the freeze context, so a new context cannot replay an old registry entry.
CP025/CP027 partial or conflicted nested evidence remains unqualified, and CP026
requires the current textual scope/list/context shapes. CP031 invalid declarations
now return NOT_FROZEN_INVALID_PROTOCOL without a frozen hash/payload. No active state was
migrated and no missing historical proof was fabricated.

Final local regression at `FINAL_SHA`:

| Suite | Passed | Additional evidence |
| --- | ---: | --- |
| Root Python | 1800 | 1077 subtests; two existing fork/thread deprecation warnings |
| Broader Research OS | 268 | 165 subtests; pinned Legacy fixture verified |
| Edge Lab platform protocol harness | 11 | Local model/fixture tests |
| Live Lab JavaScript | 57 | No production Site access |

The unchanged base root suite separately passed 808 tests. Aggregate assertions
and suites overlap; they are not independent evidence samples. Ruff F over all
changed Python and `git diff --check` pass. The actual local Core qualification
receipt binds to `FINAL_SHA`, stays pre-outcome and has all four authorities false.
No hosted CI success, VM reboot, deployment or production qualification is claimed.

UNPROVEN_DEPTH=EXPLICITLY_RETAINED

Priority limits: whole multi-file Desk/research transactions; atomic local queue
selection/claim; direct mutation of public objects; coherent reads of all state
fields during mutation; mutating/reentrant callbacks; CampaignState ABA/cooperating-writer limits and direct unsynchronized
public field mutation; changed content under an existing research ticket ID;
legacy Book replay tokens without recoverable exact payload proof;
old ticket identities discarded before migration; hostile/migrating on-disk
schemas; full epoch close/export/crash composition; scoped memory conflicts;
independent scientific-ledger publishers, unreviewed legacy handoff, whole-batch atomicity (not an existing contract),
mutation during initial deepcopy/iterable collection, authenticated chain anchoring and
large-ledger performance; semantic parser/source truth; all extreme finite arithmetic; noncooperating
writers/distributed filesystems; physical power-loss durability; actual transport
isolation/authentication; untracked import substitution/concurrent mutation during
source qualification. Checkpoints and the 25-node coverage table give finer limits.
Green regression is not exhaustive falsification of every capability/function.

HORIZONTAL_FINDINGS=NONE_NEW
LONGITUDINAL_FINDINGS=1_UNREPAIRED_OWNER_LONGITUDINAL

Existing future B/C0/D0/E and Multi-Source absences were not treated as depth
defects. Existing CP085 partial dispositions remain partial. One handoff defect is retained for its owner; no missing capability family was
established by this campaign.

CROSS_AXIS_FINDING
owner=LONGITUDINAL
from_module=LegacyKnowledgeBase
to_module=canonical_spine
property=REVIEW_LEGACY_OVERLAP must remain unresolved at downstream admission
evidence=research/vertical_depth/20261021/LONGITUDINAL_001.json

The synthetic screen correctly retains conflicting history, while the existing
architecture spine only stops exact duplicates and continues to PASS/downstream
stages on REVIEW. No economic experiment or observation occurred. The spine is
unchanged; this is explicitly not repaired or qualified by the vertical rail.

AUTHORITY_BYPASS_FOUND=TRUE
AUTHORITY_BYPASSES_REPAIRED=TRUE

Reproduced bypasses were internal: tuple-hidden outcome content admitted by the
pre-outcome scanner, NaN-based RISK approval, and decay admission erased by Python
optimization. Later counterexamples also exposed Forward authority import after
validation and temporal/outside-payload pre-outcome content bypasses, including
observability content introduced after its guard. None granted
Owner authority, consumed future/economic market
observations or placed orders. Invalid provenance receipts are also rejected now.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE

PHASE_B_REQUIRED=TRUE
PHASE_B_START_CONDITION=WAVE2_INTEGRATED_SHA_PROVIDED_BY_OWNER
SAFE_AS_DIAGNOSTIC_INPUT_TO_WAVE2=TRUE

Phase B requires a new branch from the Owner's final integrated SHA after the
stated Wave-2/convergence/regression conditions. Do not rebase this Phase-A branch
or blindly port these fixes. Re-run the adversarial ideas against the final
implementations and preserve their explicit limits.

## Reproduce locally

Use Python 3.12 with pytest 9.1.1 (the new tests use pytest), Ruff 0.17.1 and
Node 24.19.0, or document equivalent tool versions. No model/API credentials are
needed. The broader Research OS suite requires the repository's existing pinned
historical ledger fixture. It was locally materialized from commit
`183ad65ff260b903a16548ce37948f54d47a9ec8`, with blob identity
`ba9b165aaf96956776672df51233bb9bf1e6cbc9`, following the existing final-gate workflow.
It is not new scientific state and is not included in this branch's changes.

```bash
git fetch --no-tags origin 183ad65ff260b903a16548ce37948f54d47a9ec8
git show 183ad65ff260b903a16548ce37948f54d47a9ec8:LEGACY_RESEARCH_LEDGER.json > research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json
test "$(git hash-object research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json)" = ba9b165aaf96956776672df51233bb9bf1e6cbc9
PYTHONPATH=src:tests:. python -m pytest -q
PYTHONPATH=src:tests:. python -m pytest -q research/research_os/tests
PYTHONPATH=src:tests:. python -m pytest -q research/edge_lab/platform_probes/harness
node --test research/live_lab_ux/tests/*.test.js
```

The live GitHub dry-run script intentionally was not run: its configured mutable
canonical branch would violate this mission's immutable-snapshot boundary.
Native worker concurrency/recovery is exercised with real disposable local Git
remotes instead. All outputs here are engineering/diagnostic evidence.


Latest substantive continuation: CP042 adds 34 new cases and repairs three grouped
CampaignState weaknesses: stale saves could undo pause/stop/completion, failed
publication lacked coherent object recovery, and reads accepted ambiguous/nonfinite
JSON. New unit D3 is bounded to local observed-body publication/recovery and real
process restart. Seven guard-removal mutants are detected. Totals now describe
43 substantive checkpoint entries, 42 repair-bearing groups, and 57 unreconstructed
numeric labels. Mission active; next substantive sequential checkpoint CP043.
Earlier continuation counts in historical paragraphs are superseded by these
current counters, not silently relabelled as new work.


Latest substantive continuation: CP043 adds 47 new cases for immutable PIT
lineage and consideration contracts. Mutable source arrays changed admitted
facts; the first tuple repair then failed 14 deeper container adversaries and was
refined before qualification. Final before: 34 failed/13 passed; focused after:
78 passed; ten guard removals detected. Two scoped D2 units; no identity storage
or whole-PIT D4 claim. Current totals: 44 substantive entries, 43 repair-bearing
groups, 56 old numeric labels rejected. Next substantive sequential checkpoint:
CP044. Mission remains active under the Owner's clarified intent.
