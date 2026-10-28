# WP1 book-pressure pre-exposure result — 2026-10-28

WP1_RESULT=BLOCK. Builder self-challenge only; no independent scientific validation.

Objective: determine whether ONE prospective successor is admissible without a
historical rerun or new outcome access. No experiment or historical calculation
was executed. No market-source request was made. Network work was Git repository
metadata/fetch only. No runtime, economic ledger or authority state was changed.

## Primary evidence and reconstruction

Repository default ref was remotely resolved to blue/master-v2-2026-09-20 at
42affc56635b9dc7de411b544f657f98967f2371; this was the clean local base.
AGENTS, North Star and the current router were read there. CP12, workstream and
scientific-memory indexes were inspected on audit/forensic-checkpoint-20261019
at 67543ff286ff7a81a6705a197b7e557442d62ac2 as navigation, not qualification.

FACT: frozen declaration commit is 6b9daadaf6a5bf10b3b7356c2740080961add095.
The declaration's embedded head 8e820f454f018a5c7bc7b61bf8002797b4a813d8 is
its predecessor, not the declaration commit. The original pending declaration
was read at its actual commit. Post-capture evidence was read at
68bbab8ec990c813310224bc8737c41480853108, research/edge-lab-continuous.
Exact paths, blob identities and SHA256s are in primary_evidence.json.
The original result's raw bytes were hashed directly and match quality.json's
8845cf3ab3ce20efd3d20acb87b9176b1411fc56ee5552d4bdbd0de5f879ab65.
No historical payoff recomputation was performed.

FACT from declaration and original code:

| Dependency | Historical semantics / implementation |
| --- | --- |
| Venue/instrument/source | BitMEX public REST /api/v1/quote?symbol=XBTUSD&count=1&reverse=true; no source substitution |
| Variables | timestamp, bidPrice, askPrice, bidSize, askSize; positive finite numbers; bid <= ask; exact units/precision source specification not recovered |
| Timing | 21 slots at 5 seconds, one window after publication, UTC plus local send/receive monotonic times; no retries; 3s/request; 120s process alarm; 2MiB protocol ceiling |
| Body/HTTP | protocol <=16384 bytes; implementation rejects >=16384 (boundary discrepancy); no redirects; JSON singleton list; stop on malformed/non200/oversize intended |
| Recorder | explicit prerequisite SHA and unpaused GitAuthority; exclusive intent creation; raw bytes and SHA256 per receipt; metadata headers saved; stop uses error truthiness |
| Admission | calculator hashes raw against receipt, converts required numeric fields to float, parses ISO timestamp; age [-1,10] seconds relative to receipt; interval source gaps [1,12] seconds |
| Signal/lag | sign((bidSize-askSize)/(bidSize+askSize)) at i-1; zero abstains; entry i and exit i+1; 19 possible intervals |
| Trades/costs | long ask-to-bid, short bid-to-ask, divide by entry mid; approximate inverse payoff linearly; crossing plus 11bp central / 21bp stress |
| Funding | protocol says PARK window crossing 00/08/16 UTC; implementation invalidates individual entry/exit crossing intervals, not entire window |
| Adequacy | >=12 valid nonzero trades and >=60 seconds source span |
| Evaluator | adequate and oracle maximum <=0 OR central mean <=0 => KILL; otherwise central mean >=5bp, stress mean >0, both chronological valid-trade half means >0 => PROMOTE; else PARK |
| Bound | absolute next mid move ignoring spreads, perfect hindsight direction minus 11bp; registered nontradable comparator |
| Uncertainty | dependent roughly100s sample, descriptive statistics only; no significance/Sharpe or general mechanism verdict |
| Sink | original calculator exclusive-create result JSON beside declaration; private raw cache and calculation intent; no qualified successor sink/receipt binding |

FACT (artifact content): historical result reports 21 responses, zero valid trades,
adequacy false, economic_test_completed false, statistics null. Quality artifact
reports identical 77-byte bodies with timestamp/symbol/pool but missing BBO,
and empty AssertionError text defeating early stop. Raw bodies are private and
were not recovered here: their exact content remains REPORTED by the quality
artifact, rather than newly verified byte-for-byte. Historical disposition remains
PARK_DATA / CAPTURE_INVALID, never mechanism rejection or negative science.
HISTORICAL_TRIAL_RERUN_ALLOWED=FALSE.

FACT: discovery/STATE.json preserves one execution attempt for this experiment
and bitmex-book-pressure cluster, one expression, one bound, two cost scenarios,
private history UNKNOWN and no independence claim. The contemporaneous pass
also attempted VX and France; SEC was metadata only. Effective multiplicity is
UNKNOWN. Legacy ledger at 183ad65ff260b903a16548ce37948f54d47a9ec8 maps this
to crypto-orderbook-pressure / G1-PROSPECTIVE-CAPTURE, known attempts=1,
valid effective trials=0. Zero valid trials does not erase the exposed attempt.
Prior literature, closed carry, catalogue/metadata and failed-source knowledge
remain disclosed. No clean-history or complete exposure census is claimed.

Current reusable capabilities inspected: historical capture/parser/calculation
and raw-hash/intent guards; imported memory and exact quality-integrity receipt
on convergence-wave2-canonical at ebc72b9fd14f91420c37e0b7607f9bfb584a289a;
same historical scripts on oracle-v2-core at
9dc03a49008882415f2d5d53e0040b51a388492b. These inspected trees yielded no
qualified book-pressure successor implementation. This is bounded discovery,
not a claim about every repository branch. General V2 capability/CI claims do
not qualify this source or evaluator. C1–C4 remain parked.

## Initial conclusion, challenge, revision and verification

INITIAL CONCLUSION (hypothesis): repairing empty-message stop handling might
make the historical acquisition reusable with frozen science.

TEST_EXECUTED: python qualification/wp1_book_pressure/challenge.py. Only AST
fragments from the pinned historical scripts run on synthetic in-memory payloads;
no transport, scheduled capture, historical calculation or payoff loop executes.
The receipt enumerates valid/malformed cases, stale/future, missing fields,
wrong schema, nonpositive prices, units/precision, provenance, duplicate and
out-of-order checks. Timeout/HTTP full transport checks are explicitly unexecuted,
not PASS. Valid fixture acceptance is syntactic test evidence only.

TEST_PASSED: assertions reproduce the empty-message non-stop defect, acceptance
of wrong instrument and declared wrong units, and duplicate/out-of-order interval
rejection. The full receipt records other outcomes. Wrong venue/provenance fields
are ignored by these extracted checks; this does not claim an attacker can
replace an authenticated HTTPS peer. The original evaluator does not inspect
receipt.error or receipt.status. Hash consistency alone does not bind scientific
identity or units. Precision changes are accepted without a recovered precision
contract; acceptance alone is not proof that a particular precision is invalid.

COUNTEREXAMPLE SURVIVES: changing only symbol/units metadata leaves numeric
scientific values unchanged and is accepted. Fixing error truthiness cannot
establish that declared scientific variables are actually admitted.

REVISION: BLOCK. Do not build a speculative source adapter, substitute endpoint,
or declare an admissible successor. No product repair was made because source
semantics remain unestablished; a recorder-only repair cannot remove this block.
Any later repair must use exception type plus message, explicit error-is-not-None,
explicit required-field checks and synthetic early-stop tests before source use.
That is an IMPLEMENTATION_REPAIR against intended stop semantics, but changes
the actual admitted sample/request continuation and requires requalification.
Symbol, units, timing and provenance enforcement also affect admission, PIT,
signal inputs and evaluation eligibility; they are not scientifically minor by
being parser changes. Endpoint/units/market substitution cannot be called
equivalent without primary source evidence and an explicit semantic comparison.

## Smallest blockers and bounded next action

BLOCKER: no established offline source contract producing the declared BitMEX
XBTUSD BBO variables with evidenced units/precision/timestamps/provenance,
coupled with an unqualified admission path. The inspected source metadata stores
a Swagger download receipt/hash, not the schema bytes. The historical actual
capture failed to provide those variables. Synthetic invention cannot resolve
that mismatch or authenticate the intended source semantics.

Minimum missing evidence: preserved authoritative schema/documentation bytes
and provenance for the exact route and fields, plus an explanation of the
timestamp/symbol/pool-only responses using preserved evidence. This need not
prove present endpoint health. If unavailable without a live schema probe, the
current mission remains BLOCK; separate explicit Owner exposure authority would
be needed before such a probe and its information must enter scientific history.
No probe is requested or authorized here. Unknown private exposures stay UNKNOWN.

PIT/source/runner/evaluator baselines are NOT_QUALIFIED. Source-to-receipt timing,
funding-window versus interval behavior and body-limit equality need explicit
resolution before any freeze. No protocol, threshold, selection or denominator
was silently changed. Config/environment of a future runner and scientific sink
receipt are NOT_BOUND. Offline challenge environment and script hash are bound
in challenge_receipt.json; this is not a prospective environment qualification.

Required requalification once source evidence resolves the block: acquisition,
admission, early stop and HTTP/timeout/body handling, PIT/order/provenance/raw
hashes, deterministic runner and evaluator including funding/threshold gates,
config/environment and exclusive result receipt. None transfers automatically.
No successor delta has been implemented or requalified in this mission.

Owner execution authority remains closed. Separate scientific review of any
later completed package remains outstanding; this self-challenge cannot supply
it. The WP2 compatibility join was not performed. No new identifier/window is
assigned before reusable machinery is qualified.

## Join interface — blocked values, no join result

SCIENCE_LINEAGE_ID=crypto-orderbook-pressure
HISTORICAL_PARENT_ID=disc-crypto-book-pressure-prospective-l1-v0
SUCCESSOR_ID=NOT_DECLARED_BLOCKED
PROTOCOL_ID=HISTORICAL_DECLARATION@6b9daadaf6a5bf10b3b7356c2740080961add095;SUCCESSOR_NOT_FROZEN
PROSPECTIVE_WINDOW_ID=NOT_DECLARED_BLOCKED
RAW_SOURCE_CONTRACT_ID=NOT_ESTABLISHED
ADMISSION_RULES_ID=NOT_QUALIFIED
RUNNER_IDENTITY=HISTORICAL_ONLY;see primary_evidence.json
EVALUATOR_IDENTITY=HISTORICAL_ONLY;see primary_evidence.json
SCIENTIFIC_SINK_CONTRACT=HISTORICAL_EXCLUSIVE_RESULT_JSON;SUCCESSOR_NOT_BOUND
CONFIG_IDENTITY=NOT_BOUND
ENVIRONMENT_REQUIREMENTS=NOT_QUALIFIED_FOR_SUCCESSOR
DENOMINATOR_FAMILY=crypto-orderbook-pressure;historical_cluster=bitmex-book-pressure;known_attempts=1;M_effective=UNKNOWN
WP1_QUALIFICATION_RECEIPT=qualification/wp1_book_pressure/challenge_receipt.json;BLOCK

Parked: generic data infrastructure, other families, runtime/security governance,
full exposure census and platform consolidation. Reopen only on concrete WP1
dependency evidence. This bounded BLOCK requires no further audit.

Claim ceiling: valid experiment != confirmed mechanism; same-data replay !=
independent confirmation; positive result != economic edge; technical baseline
!= Owner authorization; Owner authorization != scientific validation.
