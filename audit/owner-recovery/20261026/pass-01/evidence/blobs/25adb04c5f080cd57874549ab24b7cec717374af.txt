# GIGA F final manifest

BASE_SHA=`ebc72b9fd14f91420c37e0b7607f9bfb584a289a`
BRANCH=`builder/giga-f-idea-federation-autonomous-feed-20261023`
MISSION=`POST_WAVE2_AUTONOMOUS_RESEARCH_INPUT_BUILD`
QUALIFICATION_BINDING=`EXACT_COMMIT_CONTAINING_THIS_MANIFEST_AND_PASSING_QUALIFY_GIGA_F`

This file cannot embed its own commit SHA. The external receipt from
`scripts/qualify_giga_f.py --remote-check --output /tmp/giga-f-exact-head.json`
binds every check to the exact committed HEAD, requires a clean tree and compares
the remote branch head. `.github/workflows/giga-f-qualification.yml` publishes the
same receipt/logs as an exact-head Actions artifact. No final seal is valid until
that qualification completes successfully on this exact commit.

| Acceptance | Evidence |
|---|---|
| SOURCE_FEDERATION_PRESENT | Seven origins in idea_feed/sources.py; captured-source connector + labeled fixtures |
| DURABLE_SEED_REGISTRY_PRESENT | idea_feed/registry.py on canonical Git state |
| DENOMINATOR_PRESERVED | Immutable birth roots, append prefix/storage checks, blocked/pending states retained |
| VARIANT_ACCOUNTING_PRESENT | Stable shared roots, variant identities, all finite search plans enrolled |
| RESEARCH_EXPOSURE_TRACKING_PRESENT | Root exposure events, published-claim knowledge, model/prompt provenance, sticky contamination |
| MULTISOURCE_REUSED_NOT_REPLACED | Original A/B/C, cycle, hardening and bindings unchanged; canonical proposal validation reused |
| DISCOVERY_BINDING_PROVEN | Existing RI gate blocks eligibility-only input; qualified fixture reaches existing Discovery |
| AUTONOMOUS_REPLENISHMENT_PROVEN | Existing Oracle derives bounded canonical source task and executes separate stages |
| BACKPRESSURE_PROVEN | Configurable backlog/duplicate/capacity/compute checks return explicit no-op |
| CRASH_REPLAY_PROVEN | Real local Git CAS, injected crash, lease recovery, restart count equality |
| NO_SECOND_SCHEDULER | Existing task routes/capability/leases/retries/CAS; no timer or worker creation |
| NO_SECOND_DISCOVERY_ENGINE | Original discovery_chain/discovery_engine/producer admission unchanged |
| NO_SYNTHETIC_OUTCOME_EVIDENCE | Fixture questions and technical Candidate plumbing only; no outcome observations |

Code:
`research/research_os/idea_feed/{contracts,registry,sources,intake,feeder}.py`.
Canonical seam changes: `research/research_os/{oracle_worker,worker_stages,github_state}.py`
and `research/research_os/runtime/WORKFLOW_LANES.json`.
Config: `research/research_os/runtime/IDEA_FEED_POLICY.json`.
Fixtures: `research/research_os/sources/giga_f_fixture_f1.json` through `f7.json`.
Tests: `tests/test_giga_f_idea_feed.py` and existing suites listed in GIGA_F_TEST_MATRIX.md.
Executable demonstration: `scripts/demo_giga_f_idea_feed.py`.
Durable demonstration receipt:
`research/research_os/idea_feed/evidence/deterministic_demo.json`.

The demonstration registers seven origin families, 13 seed records including a
duplicate, seven roots, five parametric variants, zero tested variants and three
shared-context policy proposals. Source adapters create zero Candidates. Only
existing Discovery creates a fixture Candidate after a separate qualified RI test
fixture. Restart preserves the entire journal/denominator. Outcomes stay UNKNOWN.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
GPT_OSS_LIVE=FALSE

Real blocker: no external local model runtime configured or qualified. Missing
external data is represented by pinned fixtures/UNKNOWN, not fake feeds. Default
configuration remains disabled so fixtures cannot become live scientific input.
F3 enrolls empirical question plans and does not execute economic tests.

FULL_REGRESSION / EXACT_HEAD_QUALIFICATION / WORKTREE_CLEAN / REMOTE_HEAD_MATCH
are assertions of the external exact-head receipt, not assumed from this document.
The seal emitter must withhold the final SHA and convergence assertion if any fails.
