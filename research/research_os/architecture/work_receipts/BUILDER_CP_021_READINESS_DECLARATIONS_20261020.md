# Builder CP021 — experiment package / independent Validator semantic gates

STATUS=IMPLEMENTED_FOCUSED_TESTS_PASS_FULL_QUALIFICATION_PENDING
BASE=a92ea663f6933e0e714b4c9943ed85c06bd97bdb
HEAD=commit containing this checkpoint
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)
ORACLE_HEAD=49bc8077b55a7fdc3f0f432e692b319b59f22021

DONE: existing readiness composition requires actual non-placeholder text for
cost/capacity model IDs and capacity evidence reference. Independently, the
existing Validator requires textual model IDs, rejects boolean/empty/unknown
declarations and non-finite scalar presence. Structured rules remain supported;
declared numeric costs can still be zero. Raw input text and hashes are not
normalized or rewritten. These checks do not establish economic feasibility.

Additional falsification in this same scientific-contract package reproduced
effective_trials=Infinity → READY. The Validator now rejects non-finite KNOWN
trial estimates; UNKNOWN remains UNKNOWN. No effective-trial estimate is invented.

EVIDENCE: five new adversarial/integration tests; 28 focused tests PASS including
the existing composition and independent-validation suites. Cases cover wrong
types, whitespace, placeholder variants, direct Validator entry, correctly
hashed invalid expression declarations, non-finite trial accounting, valid
structured rules and zero costs. Input immutability and closed authority checked.
The initial new direct tests incorrectly treated structured block reasons as
strings; assertions were corrected to check existing reason.code, without
altering product output or weakening expectations. Pyflakes/whitespace PASS.

CI coverage: added these tests plus original economic-readiness integration and
Validator suites to V2 workflow, so these critical upstream contracts are no
longer merely tested by an optional standalone Research OS suite.

ARCHITECTURE_IMPACT: early implementability → exact frozen package → independent
Validator now agrees on invalid declaration semantics. All scientific meaning
remains pre-outcome; READY still requires separate Owner authorization.
No runner execution, acquisition, runtime/Site deployment, epoch/policy or
Capital Desk/Book changes. Four source/contract packages delivered since CP016.

NEXT_BEST_WORK: full configured + broader Research OS + V2 workflow qualification
on this exact code, hosted receipts, then compact architecture/resume checkpoint.
Direct V2 negative-sidecar→search use and complete evidence acquisition remain
open investigations; no claim that the entire North Star is implemented.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
