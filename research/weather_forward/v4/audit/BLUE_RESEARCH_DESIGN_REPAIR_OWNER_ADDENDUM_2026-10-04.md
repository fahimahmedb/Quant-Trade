# Blue handoff — mandatory Research Design Repair addendum — 2026-10-04

Owner-provided instructions for integration into the Research Design Repair Plan.
This is a requirements handoff, not an approved research contract or experiment start.

## Exact starting authority

- Audit: `042002f06dd1d146e7a0b9a3e433891bc7352f94`
- Canonical registry: `research/weather_forward/v4/audit/ASTRA_V4_EDGE_MAP_OVERFIT_AUDIT_2026-10-04.json` at that audit commit.
- Preserve all 33 EDGE_ID values and lineage. No silent deletion, merge, split, rename or redefinition.
- Material extensions receive a child hypothesis ID and recorded reason.
- Maintain REAL_CAPITAL_AUTHORIZED = FALSE; LIVE_TRADING_AUTHORIZED = FALSE; t0 = NOT_DECLARED; BUILDER_AUTHORIZED = FALSE; ECONOMIC_DECISION_WEIGHT = 0; COMPOSITE_ECONOMIC_AUTHORITY = 0.
- Distinguish HYPOTHESIS_SPACE, OBSERVATION_AUTHORITY, INFERENTIAL_AUTHORITY and ECONOMIC_AUTHORITY.
- No new edge-discovery pass, E1–E5 outcome study, economic backtest or weight optimization during repair.

## Owner's exact final block

```text
============================================================
HYPOTHESIS-SPECIFIC CLEANLINESS
============================================================

Cleanliness is hypothesis-specific.

Prospective capture, immutable storage and sealed custody are necessary but not
sufficient for confirmatory validity.

For every hypothesis and every candidate validation surface, record possible
direct and indirect exposure to:

- the same dates;
- the same city;
- the same station;
- nearby or upstream stations;
- the same weather system;
- correlated markets;
- overlapping forecast windows;
- related wallets;
- published summaries;
- derived datasets;
- external analyses;
- model releases;
- source incidents;
- any result or statistic that could influence specification or selection.

A surface may be sealed and still fail to be confirmatory for a particular
hypothesis if that hypothesis, its selection, its specification or its
promotion depended on:

- outcomes from the same surface;
- materially correlated observations;
- nearby periods or markets;
- published summaries of the same information;
- a related hypothesis that used overlapping outcomes.

For each hypothesis, classify each candidate surface as:

- CONFIRMATORY_CLEAN
- DEVELOPMENT_ONLY
- DISCOVERY_CONTAMINATED
- UNKNOWN

Do not assign CONFIRMATORY_CLEAN merely because data were captured before the
hypothesis was activated or because the files remained technically sealed.

A dormant hypothesis may use previously captured sealed data for confirmation
only if all of the following are demonstrated:

1. the hypothesis specification was frozen before access;
2. the selection rule was not influenced by outcomes from that surface;
3. no materially correlated outcome or summary influenced the selection;
4. the data provenance and custody are complete;
5. the validation estimand and stopping rules were pre-registered;
6. the surface was not used to choose the hypothesis, threshold, horizon,
   context, metric or economic objective.

If any condition is not demonstrated, classify the surface as:

DEVELOPMENT_ONLY

or

UNKNOWN

and require fresh post-lock validation.

============================================================
NO IMPLICIT EXPERIMENT AUTHORIZATION
============================================================

This mission may design:

- broad prospective capture;
- immutable storage;
- custody procedures;
- access controls;
- exposure ledgers;
- unblind procedures;
- future validation protocols.

This mission does not authorize:

- collector implementation;
- collector deployment;
- live data activation;
- DATA_T0;
- EXPERIMENT_T0;
- research freeze;
- unblinding;
- capital activity;
- paper-trading claims of validation;
- live trading;
- Builder activity.

Do not infer DATA_T0 or EXPERIMENT_T0 from the date of this repair plan.

Those timestamps remain:

t0 = NOT_DECLARED

until the owner explicitly decides otherwise through the approved governance
process.

Designing a prospective protocol is not the same as starting the protocol.
Describing a collector is not authorizing its deployment.
Creating a sealed-storage plan is not creating confirmatory evidence.
```

## Required terminal state of Blue's plan

Return exactly one:

```text
RESEARCH_DESIGN_REPAIR = READY_FOR_INDEPENDENT_CONTRACT_AUDIT
RESEARCH_DESIGN_REPAIR = OWNER_DECISIONS_REQUIRED
RESEARCH_DESIGN_REPAIR = BLOCKED_BY_UNRESOLVED_AUTHORITY
```

No implicit owner decision: economic primary/secondary estimands, horizons, independent units, success/failure/continuation/stopping/reopening rules, minimum information and optional-stopping controls must be proposed explicitly where unresolved. Missing exposure records default to UNKNOWN; capture/access/viewing/outcome-viewing/design-use are separate fields. Custody must identify CAPTURE_OWNER, CUSTODY_OWNER, RESEARCH_ACCESS, OUTCOME_ACCESS, UNBLIND_DATE and PRE_REGISTERED_SHA.

The previously mentioned V3 terminal SHA `fff9f5ed6604cf6cbf5bb3bf90141f033cd0c170` is not verified by this addendum. Blue must independently resolve its remote object and exact deliverables before using it; otherwise mark CLAIMED_BUT_NOT_REPOSITORY_VERIFIED. This does not retroactively alter the original Astra audit anchor or conclusions.

## Source basis

The exact block above was supplied by the owner in this conversation. Scientific rationale and prior audit limitations are recorded in the Astra Markdown/JSON at the audit commit above. No new external source, market outcome or sealed dataset was inspected for this handoff.
