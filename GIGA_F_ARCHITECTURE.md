# GIGA F architecture

Immutable base: `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.
Branch: `builder/giga-f-idea-federation-autonomous-feed-20261023`.

```
pinned source observation / origin engine
 -> SeedRegistry enrolment + exposure + complete bounded variant family
 -> canonical Git transaction (before any policy selection)
 -> shared context -> existing Multi-Source policies A / B / C
 -> existing DurableProposalLedger, persisted in the append-only journal
 -> ELIGIBLE_FOR_DISCOVERY (synthesis eligibility only)
 -> separately qualified Research Intelligence RUN_PRODUCER
 -> existing discovery_chain.run_discovery_chain
 -> existing producer / Candidate / Factory admission law
```

The feedback path is `FrontierHealth -> Oracle admission -> one SOURCE_QUALIFICATION
task -> evidence_data lane -> source_ingestion -> policy_intake`. There is no new
process, timer, queue, lease implementation, producer or Candidate constructor.
The feeder runs before ordinary task selection when explicitly enabled; it does
not require an empty downstream queue. Existing task selection executes source
work on subsequent wakes. Downstream work continues under backpressure.

## Code owners and boundaries

- `research/research_os/idea_feed/contracts.py`: seed schema, identity axes,
  outcome/authority/operational field firewall, novelty comparison.
- `research/research_os/idea_feed/sources.py`: seven origins; connector to existing
  `expansion/engine_dossiers_v1.py::qualify_document_packet`; local model abstraction.
- `research/research_os/idea_feed/registry.py`: append-only seed, exposure, policy
  and technical Discovery lineage journal; cohort projections.
- `research/research_os/idea_feed/intake.py`: calls existing Multi-Source policies,
  barrier/receipts, Proposal Ledger and Discovery membrane. No scheduler imports.
- `research/research_os/idea_feed/feeder.py`: pure health/derivation plus canonical
  transaction adapter and the two source task stages.
- `research/research_os/oracle_worker.py`: existing admission, selection, leases,
  retry ceilings, expired-claim recovery, receipts/events and atomic publication.
- `research/research_os/worker_stages.py`: dispatch and explicit stage authorization.
- `research/research_os/github_state.py`: existing global HEAD CAS, with an added
  append-prefix check for the journal. Only that journal can grow between stages;
  all ordinary stage artifacts remain create-only.
- `research/research_os/runtime/WORKFLOW_LANES.json`: adds two stages to the
  existing evidence lane. Existing source_qualification capability and task route
  are reused without adding a registry, scheduler or worker authority.

Existing Multi-Source core, hardening, bindings, cycle and Policy C wrapper are
unchanged. Existing Discovery/Research Intelligence/producer files are unchanged.
Eligibility is deliberately insufficient to invoke a producer. Scientific KILL
or PROMOTE can only be projected from a validated C0 adjudication bound to the
exact Candidate previously recorded by Discovery. The feed cannot decide them.

## Deployment and scientific limits

`runtime/IDEA_FEED_POLICY.json` is disabled by default and contains explicitly
labeled fixtures. The executable demonstration enables it only in a disposable
local Git remote. No live runtime is activated. For deployment, configure pinned,
admissible source descriptors and budgets on the canonical state branch, then
use the existing qualified release/deployment process.

No external model runtime or provider is configured. `GPT_OSS_LIVE=FALSE`.
F3 enumerates bounded predeclared empirical question plans; it does not inspect
prices, optimize a statistic or run an economic experiment. All tested-variant
and outcome counters stay zero/UNKNOWN until their existing authority owners
legitimately supply future evidence. Exposure history cannot prove complete
researcher/model independence.

Qualification paths: `tests/test_giga_f_idea_feed.py`,
`scripts/demo_giga_f_idea_feed.py`, `scripts/qualify_giga_f.py`.
