# Frontier renewal: PARTIAL; policy transition missing, machinery mostly exists

## Evidence and exact scope

Inspected primary code at W2 `ebc72b9fd14f91420c37e0b7607f9bfb584a289a` (W), F `79329f15bbf02c25fa61e5d5ef6028e5abfb1493` (F), V3 `0691a4c1c905c8cfa1e68d521b12d66655ec4dd3` (V), and runtime state `16eafd0b3c8d9e0c633ef01dd191cbd32ae50b42` (R). Paths below are repository-relative at these SHAs. The preserved snapshots' `queue_replenisher.py`, F `idea_feed/registry.py` and V3 `ideation_intake.py` were compared with Git objects: blobs respectively `d548587ea8310d3da0873770cb712f815852c7cc`, `fc6a4fb1d11c3d4224a416f9c853b1b21a8f97f8`, `b893de5abed7f92a7bc97bfcd7e833c1e1244323` matched. Review probes imported those snapshots with bytecode disabled and mutated only in-memory objects.

## What exists versus what needs changing

W `research/research_os/queue_replenisher.py:derive_refill_task` already derives one ordinary READY task when the global queue is empty, enforces four closed authorities, uses idempotent derivation keys, forbids producer execution/recursive refill in the same wake, balances by lowest issued count then priority, and binds selected source hashes. Its task count is issuance, not successful independent experiments. W `research_refill_policy.py:evaluate_frontier_mandates` checks capability/route/source without declaring unknown identity novel. W `research_intelligence.py:classify_frontier` explicitly requires search-space AND archaeology completion before declaring scientific exhaustion.

W `frontier_source_planner_v2.py:plan_frontier_source` selects engine-qualified unused packets, ranks binding primary flow rules above explanatory FAQs, preserves path/blob/packet/record hashes, and infers historical source consumption only from actual producer completion. Its consumption accounting is **frontier-scoped**. Renaming a frontier can evade that local consumption history; downstream global semantic/exposure checks must survive a generation transition.

F `idea_feed/feeder.py:health/derive_request/execute_stage` adds bounded source work on the existing Oracle, source/cohort budgets, backpressure, diversity and age thresholds, policy-hash fencing, one request per wake and existing canonical state publication. F `runtime/IDEA_FEED_POLICY.json` is disabled, identifies a deterministic fixture cohort, and names seven fixture origins. F is real reusable implementation, not proof of seven live productive research sources. `sources.py:documentary_origin` connects qualified documents for only rule/constraint and fundamental families; the generator supplies question templates and leaves identity UNKNOWN unless source fields or downstream synthesis resolve it. Replication/bounded-empirical/model alternatives are enrolled before selection; empirical outcomes remain forbidden here.

F `registry.py:enrol` compares all existing seeds, across cohort labels; cohort is immutable attribution, not a fresh scientific root. `registry.py:expose/guard_append` preserves exposure and prior history. A new cohort label can reset the **per-cohort source-work budget** in `derive_request`; no inspected contract explicitly authorizes that reset against a cumulative program budget. Changing labels is therefore a configuration primitive, not a qualified renewal protocol.

## Required capability assessment

| Function | Classification | Existing mechanism / exact limitation |
|---|---|---|
| Create a new frontier cohort | PARTIAL | W accepts configured frontier entries; F accepts a pinned cohort label and budgets. No validated predecessor→successor transaction, policy owner/trigger or cumulative budget authorization found in inspected code. |
| Retire an old frontier | PARTIAL | W supports global ACTIVE and entry enabled flags; historical tasks remain. F can disable feed. No explicit append-only cohort closure/disposition with successor relation found. |
| Refresh mandates | PARTIAL | W objectives/allowed actions and F policy hashes can change through Git; F execution rejects stale policy. No governed renewal decision linking old mandate, evidence, new question distribution and budget was found. |
| Introduce source families | PARTIAL | W qualifier routes four producer families; F defines seven origin families and pinned source descriptors. New adapters/qualification needed where a real packet does not already fit. Adding an enum is not acquiring data. |
| Change question distribution | PARTIAL | W priorities/mandates; F sources/budgets; V3 ordered policy callbacks and per-cycle maximum. No demonstrated automatic policy learning; ordered V3 callbacks can consume the whole cycle budget before later policies. |
| Learn historical source productivity | PARTIAL | F source/cohort metrics exist; `feeder.health` explicitly reports `source_productivity=UNKNOWN`, allocation explicitly uses minimum exploration with no historical performance allocation. Outcome/cost feedback is incomplete. |
| Avoid cross-generation duplicates | PARTIAL | F journal compares all seeds; V3 ledger compares previous proposals and qualified memory; RI/Discovery recheck semantic families. W source reservation remains frontier-scoped; ledger coverage and mapping across F/V3/current history are not converged. |
| Preserve exposure / trial accounting | PARTIAL | F exposure journal and root/variant relations; existing V2 trial/epoch and frozen Factory identities. No proven complete root→proposal→candidate→experiment→outcome denominator for renewed generations. |
| Prevent silent post-outcome adaptation | PARTIAL | Existing outcome field firewalls, immutable seeds, frozen identities and source/policy hashes are strong primitives. No explicit renewal receipt separating policy-learning information from protected candidate outcomes and untouched OOS partitions was found. |

No row is marked ABSENT merely because the operational release does not use a newer component. No row is PROVEN_WORKING end-to-end across generations. Automatic source-productivity allocation is not even a prerequisite for the first safe successor cohort; initially use fixed preregistered allocation.

## Primary challenge to the audit

The audit's issue-cap statement is correct for the four configured families. A pure W probe found 12 tasks for each, plus one historical `QUANT_MECHANISM_DISTINCT_SIGNAL` task outside those four configured labels. Do not convert 48 issues into 48 tested hypotheses, or infer the whole search space has four possible families.

The runtime's saved `NOOP_FRONTIER_EXHAUSTED` is an old operational status, not W2's current scientific semantics. Running W `derive_from_repo` on W's frozen state at `2026-10-26T00:52:12Z` returned:

```text
NOOP_SEARCH_SPACE_INCOMPLETE
state=SEARCH_SPACE_INCOMPLETE; scientifically_exhausted=False
EVENT_DOCUMENT_DISTINCT_MECHANISM: qualified=1 unused=0 NO_UNUSED_ADMISSIBLE_SOURCE
FUNDAMENTAL_DISTINCT_THESIS: qualified=1 unused=0 NO_UNUSED_ADMISSIBLE_SOURCE
INSTITUTIONAL_FLOW_DISTINCT_MECHANISM: qualified=2 unused=2 SOURCE_SELECTED
QUANT_MECHANISM_DISTINCT: qualified=0 unused=0 NO_ADMISSIBLE_DOCUMENTARY_SOURCE
```

Thus some unused qualified source capacity already exists behind issuance caps and flow task contracts. That does **not** prove an economically novel mechanism can be extracted from the rule/FAQ, nor does the FAQ provide independent confirmation of the rule. Raising all four caps would reproduce event/fundamental duplicates and quant source blocks. New source access and a repaired route must accompany any useful renewal.

A second pure F probe enrolled the same fixture F2 once under `review-a`, then under `review-b`: classification changed from `ECONOMICALLY_DISTINCT` to `TEXTUAL_DUPLICATE`, with `same_root=True`. Cross-cohort suppression primitives are real; this is one deterministic case, not global semantic novelty qualification.

## Is frontier renewal the real missing function?

**Yes, as one precise policy seam; no, as a sole explanation for the stopping behavior.** The missing function is an authorized, immutable successor-policy decision that can reopen a bounded search program while preserving its scientific history. Existing W/F can execute bounded work; V3 can admit proposals; RI can decide useful actions. Creating another generator or scheduler would duplicate existing functions. Renewing depleted sources without resolving data, authority, and positive continuation would increase blocked work.

The smallest contract belongs to Research OS research policy, with existing Control Plane as the only mutation/scheduling owner. Call it a versioned renewal receipt, not a new subsystem:

1. `program_id`, `cohort_id`, predecessor/closure receipt, frozen policy hash, effective clock and idempotency key; old records never edited or deleted.
2. A reason-coded eligibility decision: issuance cap vs duplicate-only vs source/capability/access/authority/budget block vs true scientific exhaustion. A cap is not permission to reset accounting.
3. Exact qualified source versions/hashes, producer routes and capability versions; unresolved access produces a source task or PARK, not an invented candidate.
4. Predeclared question/source-family distribution, root/variant/search budget, cumulative program exposure/budget, stopping rule, exploration floor and validation-capacity bound. Start with fixed allocation; productive-policy learning comes only after the denominator is trustworthy.
5. Existing global root/proposal/memory references and explicit replication/transfer/reopen reasons. New source, prompt, name or cohort is not new mechanism or independent trial.
6. Information-availability cutoff, protected outcome/OOS references and declared policy-learning inputs; a changed search domain after outcomes starts a charged new epoch and never rewrites the earlier frozen protocol.
7. Typed stage/action scope; all four authority flags remain false unless a separate explicit applicable grant exists. Existing Oracle emits at most one admissible task and produces a receipt or bounded NOOP.

Qualification must show replay/duplicate renewals are idempotent; process restart preserves cumulative counts; cohort rename cannot erase exposure; stale policies/source clocks fail closed; an exhausted source does not loop; an unused flow packet can produce one correctly authorized pre-outcome task; all denied authorities remain denied. Stop on any lineage, identity, exposure, outcome-firewall or authority regression. No new live network acquisition or research outcome was attempted in this review.
