# Quant North Star

This document is the highest-level product and architecture specification for Quant.

If a lower-level document, implementation detail, agent prompt, local optimization, checkpoint, historical branch, runtime convenience, or temporary work package conflicts with this document, **this document wins unless it is explicitly revised by the Owner**.

The purpose of this file is not only to state the terminal objective. It also fixes the final system shape so that local work does not gradually redefine Quant into a smaller project.

---

## 1. Terminal objective

Quant exists to increase real capital through repeatable discovery, selection, sizing, execution and replacement of genuine market edge.

The terminal objective is **net economic gain / long-run real wealth growth after real frictions**.

Risk, drawdown, leverage, Sharpe, hit rate, activity, number of trades, number of experiments, model complexity, code elegance and number of agents are instrumental variables or diagnostics. They are not terminal objectives.

A compact abstraction is:

`W(t+1) = W(t) + gross_pnl - fees - spread - slippage - financing - borrow - execution_losses`

The system should prefer the action that improves expected future wealth conditional on current evidence, including `NO_TRADE` when that is economically superior.

---

## 2. Quant is a system, not a research script

Quant must never be reduced to:

- a backtester;
- a strategy notebook;
- a market scanner;
- an LLM wrapper;
- a research queue;
- a collection of strategies;
- a single producer family;
- Oracle V2 alone;
- Research OS alone;
- Live Lab alone;
- a dashboard with no underlying state.

The target is a **persistent autonomous quantitative system** composed of several interacting planes.

The research system is a major component of Quant, but it is not the whole product. Conversely, the Capital Desk, Book, Site, Data Plane or Build Plane must not be treated as independent products detached from the scientific core.

---

## 3. Whole-system target

```text
                           HUMAN / CONTROL SURFACE
                                    |
                                    v
                           ROOT / CONTROL PLANE
                       clock · scheduler · routing
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
    DATA PLANE               RESEARCH FACTORY              BUILD PLANE
  ingest · validate          observe · discover         Codex / engineering
 point-in-time state          test · falsify               improve Quant
        |                           |
        +-------------+-------------+
                      |
                      v
                 OPPORTUNITIES
                      |
                      v
          SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK
                                              |
                                              v
                                      REAL / SHADOW FEEDBACK
                                              |
                          pnl · fills · rejects · decay · errors
                                              |
                                              +------> LEARNING / MEMORY
                                                           |
                                                           +------> SEARCH
```

The current implementation may begin in pre-outcome, paper or shadow mode, but the topology should match the intended final system rather than inventing a temporary architecture that later has to be discarded.

---

## 4. Canonical final research architecture

The Research Factory is not just a set of producer engines followed by a validator. Its final target is a connected scientific operating system with explicit governance, state, provenance, independent challenge, portfolio interpretation, prospective validation and decay monitoring.

The canonical architecture is:

```text
                              OWNER / GOVERNANCE
                                      |
                                      v
+------------------------------------------------------------------+
|                     CANONICAL RESEARCH CORE                       |
|                                                                  |
| hypotheses / generations / ancestry                              |
| preregistration / freeze                                         |
| data provenance / PIT                                            |
| trial accounting                                                 |
| evidence vector                                                  |
| KILL / PARK / EXPLORE / PROMOTE                                  |
| negative knowledge                                               |
+---------------------------------+--------------------------------+
                                  |
                                  v
+------------------------------------------------------------------+
|                         CONTROL PLANE                            |
|                                                                  |
| queue / priorities / leases / permissions / budgets              |
| capability registry / task contracts / blockers                  |
+---------------+----------------+----------------+----------------+
                |                |                |
                v                v                v
        QUANT / MECHANISMS   EVENT / DOCS     FUNDAMENTAL
                |                |                |
                +-----------+----+-------+--------+
                            |            |
                    FLOWS / REGULATION   ARCHAEOLOGY
                            |
                            v
                   EARLY IMPLEMENTABILITY
                            |
                            v
                EXPERIMENT INFRASTRUCTURE
             data / code / reproducibility / costs
                            |
                            v
                  INDEPENDENT VALIDATOR
                            |
                            v
                         RED TEAM
                            |
                            v
                  ECONOMIC IDENTITY
                            |
                            v
                     PORTFOLIO MAP
                            |
                            v
                  SHADOW / PROSPECTIVE
                            |
                            v
                    DECAY MONITORING

             EVERYTHING EMITS REAL EVENTS / RECEIPTS
                            |
                            v
                    LIVE RESEARCH LAB
```

A second view of the same system emphasizes the scientific/economic flow:

```text
                  RESEARCH OS / SCIENTIFIC CORE
                              |
          +-------------------+--------------------+
          |                   |                    |
          v                   v                    v
  QUANT / MECHANISMS   FUNDAMENTAL / DOCS     EVENTS / FLOWS
          |                   |                    |
          |          earnings / filings            |
          |          guidance / revisions          |
          |          balance sheet                 |
          |          valuation                     |
          |          business quality              |
          +-------------------+--------------------+
                              |
                              v
                     CROSS-EXAMINATION
                              |
                              v
                  INDEPENDENT VALIDATION
                              |
                              v
                    ECONOMIC IDENTITY
                              |
                              v
                     PORTFOLIO ENGINE
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
           alpha        diversification       risk
         expected        marginal value      exposure
             |                |                |
             +----------------+----------------+
                              |
                              v
                         SHADOW BOOK
                              |
                              v
                   PROSPECTIVE VALIDATION
```

These diagrams are normative target architecture, not decorative summaries.

A future Builder must not conclude that the research architecture is complete merely because producer engines, validation classes or observability helpers exist individually. The **links between the components** are part of the architecture.

---

## 5. Meaning of the canonical research components

### Owner / Governance

Owns authority, boundaries, budgets, irreversible decisions, phase gates and explicit permission changes.

Repository files, agents, model output and runtime convenience must not silently grant authority that the Owner has not granted.

### Canonical Research Core

This is the scientific source of truth for research state.

It must preserve:

- hypothesis identity;
- generation and ancestry;
- preregistration and freeze;
- source and model point-in-time state;
- trial accounting and multiplicity;
- evidence maturity;
- decision state such as `KILL`, `PARK`, `EXPLORE`, `PROMOTE` where applicable;
- scoped negative knowledge;
- reproducible lineage.

Later knowledge must not rewrite earlier epistemic state.

### Research Control Plane

Owns the mechanics of research execution:

- queueing;
- priorities;
- leases;
- permissions;
- budgets;
- task contracts;
- capability registry;
- blockers;
- recovery;
- explainable scheduling.

There must be one orchestration truth, not multiple competing schedulers that can silently disagree.

### Producer families

The canonical producer families are currently organized around:

- `QUANT / MECHANISMS`;
- `EVENT / DOCUMENTS`;
- `FUNDAMENTAL`;
- `FLOWS / REGULATION`.

These families are not separate products and do not justify parallel top-level architectures merely because one family needs more depth.

They should generate distinct, falsifiable economic research candidates rather than merely stylistically different dossiers.

### Archaeology

Archaeology is a first-class research capability.

Its purpose is to recover and classify prior knowledge before new work is invented again:

- historical experiments;
- negative/KILL results;
- blocked but unexecuted work;
- prior mechanisms;
- old source packets;
- prior implementation attempts;
- governance decisions;
- superseded protocols;
- useful capabilities stranded on historical branches.

Archaeology must preserve provenance and must distinguish:

- negative result;
- blocked data permission;
- unexecuted design;
- protocol invalidation;
- positive but insufficient signal;
- historical result with limitations.

Old does not mean obsolete, and historical work must not be silently converted into current truth.

### Early Implementability

Implementability begins before expensive testing.

Candidates should be challenged early on whether they have a credible path to:

- a defined instrument or economic expression;
- usable data;
- a valid clock;
- source provenance;
- realistic costs;
- realistic capacity;
- reproducible construction;
- a falsifiable decision rule.

This stage should cheaply kill impossible or underspecified ideas before they consume expensive validation capacity.

### Experiment Infrastructure

Experiment infrastructure binds scientific intent to reproducible execution.

It includes, where applicable:

- frozen protocol;
- data identity;
- code identity;
- environment identity;
- source/model PIT;
- universe;
- clock;
- expression;
- costs;
- capacity;
- multiplicity declaration;
- power/MDE or equivalent geometry;
- reproducibility bindings;
- deterministic decision map;
- immutable candidate/protocol hashes.

A READY package is not permission to execute an economic experiment.

### Cross-examination

Producer output should be exposed to adversarial questioning before final scientific acceptance.

Cross-examination is intended to reveal:

- hidden assumptions;
- weak mechanism logic;
- source ambiguity;
- timing contradictions;
- unsupported causal claims;
- implementation gaps;
- overlap with prior failed mechanisms;
- claims that exceed evidence.

Cross-examination is not itself independent validation unless independence requirements are satisfied.

### Independent Validator

The Validator must be meaningfully independent from the producer and independently inspect scientific validity, provenance, PIT, protocol integrity, reproducibility, multiplicity, implementability declarations and authority boundaries.

It must be able to return an explicit PASS/READY ceiling or machine-readable BLOCK reasons.

### Red Team

The Red Team attacks the candidate from a skeptical perspective and searches for ways the apparent research claim could be wrong.

Typical concerns include:

- leakage/look-ahead;
- survivorship;
- stale or revised data;
- causal timing errors;
- multiple-testing luck;
- unrealistic implementation;
- hidden beta/factor exposure;
- concentration;
- fragile regimes;
- unsupported source semantics;
- invalid inference from structural similarity.

### Economic Identity

Economic identity asks what exposure the candidate actually represents, not merely what label or strategy name it uses.

It should capture enough structure to identify when two different-looking candidates are materially the same economic exposure.

Structural overlap is not empirical correlation.

### Portfolio Map / Portfolio Engine

Before and after outcome authority opens, portfolio reasoning must remain explicit about what is known.

Pre-outcome, the system may reason about:

- structural overlap;
- mechanism identity;
- payer/actor distinctions;
- instrument/universe distinctions;
- clock/horizon distinctions;
- cost and capacity declarations;
- diversification hypotheses;
- portfolio relation state.

Without admissible return data, quantities such as empirical correlation or marginal portfolio contribution remain unknown/not estimated.

Once economic outcome authority is legitimately opened, the Portfolio Engine can additionally reason about:

- expected alpha;
- diversification;
- marginal value;
- risk;
- exposure;
- concentration;
- capacity;
- interaction with the persistent Book.

### Shadow / Prospective

Shadow/prospective stages are authority-gated transitions, not automatic consequences of research readiness.

`READY_FOR_AUTHORIZED_ECONOMIC_TEST` means the package is ready for a separately authorized economic test. It does not mean the test has been authorized.

### Shadow Book

The Shadow Book is the portfolio/accounting surface for authorized non-live economic validation.

It must not silently become a second authoritative live Book.

Its role is to preserve state and allow prospective evidence to accumulate under explicit authority and reproducible execution rules.

### Prospective Validation

Prospective validation evaluates frozen hypotheses on admissible future information under predeclared rules.

It must preserve the separation between:

- discovery;
- frozen protocol;
- prospective observation;
- evaluation;
- decision.

### Decay Monitoring

A validated edge is not permanently trusted.

Quant must monitor for:

- signal weakening;
- implementation degradation;
- cost/capacity change;
- market-structure change;
- source drift;
- regime dependence;
- strategy crowding;
- portfolio interaction change.

Decay can trigger review, resizing, parking, retirement or renewed research.

### Real events / receipts

Every important transition should emit durable factual events/receipts rather than exist only in agent prose.

Examples include:

- task start/claim/completion;
- source qualification;
- evidence gap;
- blocker;
- hypothesis freeze;
- validator decision;
- Red Team decision;
- readiness transition;
- authority denial/grant;
- prospective observation;
- evaluation result;
- strategy decay;
- runtime recovery;
- faults.

Receipts are the bridge between autonomous operation, auditability, recovery and the Live Research Lab.

### Live Research Lab

The Live Research Lab is a factual projection of durable system state.

It is not a second source of business truth and must not invent activity to make the interface look alive.

It should ultimately make the whole research lifecycle observable: what is running, blocked, killed, frozen, validated, ready, prospectively observing, decaying or awaiting authority.

---

## 6. Research state transitions and scientific meaning

A useful high-level research flow is:

`OBSERVE -> SCAN -> FILTER -> HYPOTHESIZE -> DISCONFIRM -> FREEZE -> CROSS-EXAMINE -> VALIDATE -> RED TEAM -> ECONOMIC IDENTITY -> PORTFOLIO MAP -> READINESS`

Depending on evidence and authority, the process may transition to states such as:

- `KILL` — scientifically or economically falsified under the relevant protocol;
- `PARK` — not currently worth more resources, but not disproven;
- `EXPLORE` — discovery-stage work with limited claim ceiling;
- `PROMOTE` — scientifically promoted to a stronger stage, never a synonym for profitability;
- `BLOCK` — cannot proceed because a required condition is unmet;
- `READY_FOR_AUTHORIZED_ECONOMIC_TEST` — frozen package ready for a separate Owner authority decision.

Important distinctions:

`BLOCKED != FAILED`

`UNEXECUTED != NEGATIVE`

`READY != PROFITABLE`

`DOCUMENT_CHANGE != EDGE`

`RULE_EXISTS != FORCED_FLOW`

`GOOD_FUNDAMENTALS != MISPRICING`

`STRUCTURAL_OVERLAP != EMPIRICAL_CORRELATION`

`MODEL_COMMENTARY != EVIDENCE`

---

## 7. Core whole-system planes

### Control Plane / Clock

Owns system lifetime, scheduling, event routing, liveness, state transitions, resource budgets, recovery and observability.

`IDLE` means alive with no useful work now. It does not mean finished.

### Data Plane

Owns acquisition, point-in-time semantics, validation, normalization, lineage, versioning and dataset availability.

No research or capital decision may silently assume data that the system cannot trace.

The intended source path is:

`PRIMARY CAPTURE -> PROVENANCE -> PIT/AVAILABILITY -> STRUCTURED PACKET -> RESEARCH ENGINE`

Model browsing or commentary cannot silently substitute for qualified source identity.

### Research Factory

Continuously searches for edge and replacement strategies as alpha decays.

Canonical broad pattern:

`OBSERVE -> SCAN -> FILTER -> HYPOTHESIZE -> TEST -> FALSIFY/VALIDATE -> REGISTER -> LEARN -> CONTINUE`

The detailed scientific architecture in Sections 4-6 defines what this means operationally.

Research failure is normal and should usually be absorbed internally.

### Capital Desk

Transforms validated opportunity evidence into capital decisions.

Canonical functional chain:

`SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`

These are logical functions, not a requirement for six separate LLMs.

- `SCAN`: surfaces actionable opportunity candidates from research/market state.
- `VET`: decides whether the opportunity itself deserves consideration now.
- `SIZE`: maps edge, uncertainty, liquidity, capacity and capital state into exposure.
- `RISK`: evaluates the opportunity in portfolio context, including correlation and concentration.
- `FILLS`: models/records execution quality and expected-versus-realized implementation loss.
- `BOOK`: authoritative ledger for bankroll, positions, cash, exposure and P&L.

The Desk must not be rebuilt merely because current pre-outcome research does not invoke it.

### Persistent Book

The same bankroll carries forward through time.

There is no fresh seed per experiment, day, Codex run or process restart.

Conceptually:

`S_t = (wealth, cash, positions, exposures, history, active_strategies, market_state)`

Future decisions depend on this state.

### Learning / Memory

Quant learns from:

- profitable and losing trades;
- accepted and rejected opportunities;
- false accepts and false rejects;
- failed hypotheses;
- execution shortfall;
- strategy decay;
- data failures;
- scanner/router quality;
- missed opportunity cost;
- blocked experiments;
- invalid protocols;
- duplicated mechanisms;
- historical negative research.

The durable asset is the system's improving ability to find and monetize edge, not one permanent strategy.

Learning must feed future Search. Merely storing old results without changing future search behavior is incomplete architecture.

### Build Plane

Codex is primarily a **Builder / Quant Engineer**, not the runtime itself.

Codex can create or improve scanners, tests, data adapters, source contracts, experiment infrastructure, portfolio logic, execution models, UI and infrastructure.

When a Codex task ends, Quant's persistent state and runtime should remain coherent and resumable.

Builder work must be checkpointed durably enough that another model can continue without reconstructing hidden conversational context.

---

## 8. Two-speed intelligence

The source architecture's most important compute principle is preserved:

`wide / cheap -> narrow / deep`

Broad deterministic or inexpensive monitoring should process many observations. Expensive reasoning should be concentrated on filtered candidates with high information value.

Do not spend frontier-model reasoning uniformly across all markets or observations.

This principle applies to both research generation and independent challenge.

---

## 9. Autonomy

Within configured boundaries, Quant should be able to choose:

- where to search;
- which markets/instruments/data deserve attention;
- which hypotheses to test;
- which strategies to revise or retire;
- which candidates to reject;
- what to research next;
- whether to stay idle;
- how much shadow/paper capital an opportunity deserves once that authority exists.

The human should not be required to invent the next strategy after every ordinary failure.

Autonomy does not override authority. The system may decide what it wants to research while still being unable to observe prospective outcomes, run economic tests, or trade without the corresponding permission.

---

## 10. Alpha discipline

Profit is not automatically alpha.

Quant must distinguish genuine edge from:

- passive beta;
- factor exposure;
- look-ahead or leakage;
- survivorship bias;
- multiple-testing luck;
- unrealistic fills/costs;
- stale information;
- concentration in a few observations;
- subsidized or non-repeatable P&L;
- protocol drift;
- non-causal timing.

Directional exposure is allowed when economically justified, but secular drift must not be relabeled as discovered autonomous skill.

Scientific readiness, portfolio structural identity and real economic validation are separate states.

---

## 11. Authority membranes

Research, prospective observation, economic evaluation, real capital and live trading are distinct authority domains.

A repository file, READY candidate, model output or successful CI run must not silently open a higher authority layer.

Unless explicitly changed by the Owner, authority values remain as declared in the active canonical policy/state.

A typical pre-outcome state may intentionally maintain:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`;
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`;
- `REAL_CAPITAL_AUTHORIZED = FALSE`;
- `LIVE_TRADING_AUTHORIZED = FALSE`.

The architecture should be able to approach the membrane with complete frozen packages without crossing it.

---

## 12. Events, receipts and observability

Everything important should emit real durable events or receipts.

The live interface is an architectural checksum, not the product itself.

A useful final status surface should be able to truthfully display real persistent system state such as:

```text
BANK / NAV
P&L
UPTIME
POSITIONS / SHADOW POSITIONS
ACTIVE STRATEGIES
TICKETS ACCEPTED / REJECTED / BLOCKED

SCAN    RUN|IDLE|BLOCKED
VET     RUN|IDLE|BLOCKED
SIZE    RUN|IDLE|BLOCKED
RISK    RUN|IDLE|BLOCKED
FILLS   RUN|IDLE|BLOCKED
BOOK    RUN|IDLE|BLOCKED

RESEARCH CORE: generations / frozen / killed / parked / promoted
PRODUCERS: quant / events-docs / fundamental / flows-regulation
ARCHAEOLOGY: recovered / unresolved / duplicate-blocked
IMPLEMENTABILITY: complete / incomplete / blocked
VALIDATOR: pass / block
RED TEAM: pass / block
ECONOMIC IDENTITY: mapped / unresolved
PORTFOLIO: structural / shadow / empirical when authorized
PROSPECTIVE: unauthorized / observing / complete
DECAY: healthy / watch / degrading / retired
DATA: healthy / stale / blocked
BUILD: idle / task running
SYSTEM: heartbeat / faults / next event
```

Every displayed value must come from real persistent state or a deterministic projection over durable state.

The Site must not become a second source of truth.

---

## 13. Source hierarchy

Primary architectural references:

1. explicit Owner decisions;
2. the project owner's supplied source PDF/article and screenshots where applicable;
3. this North Star, which translates those references and later Owner architecture decisions into the Quant target system;
4. lower-level specifications, checkpoints, runtime policies and implementation evidence.

When a lower-level artifact conflicts with this North Star, the North Star wins unless the Owner explicitly revises it.

Financial performance, vendor claims, costs, model capability claims and screenshot profits are unverified unless separately evidenced.

---

## 14. Final convergence rule

Canonicalisation is not Git cleanup.

The final canonical system should emerge only after the best validated state from the major workstreams converges:

```text
RUNTIME / CONTROL CLOSURE
          +
HISTORICAL / ARCHAEOLOGICAL RECONCILIATION
          +
V2 BUILDER IMPROVEMENTS
          +
REAL RECEIPT / LIVE LAB INTEGRATION
          |
          v
   FINAL CONVERGENCE
          |
          v
      CANONICAL V2
```

Do not declare the architecture canonical merely because one stream has completed its work package.

Do not perform destructive cleanup before material capabilities, scientific memory, negative evidence and governance history have been dispositioned.

---

## 15. Architectural completeness test

A major component is not considered complete only because a class or file with the right name exists.

For each important node, ask:

1. Does the capability really exist?
2. Is it connected to the preceding and following stages?
3. Is identity/provenance preserved across the connection?
4. Does it fail closed when assumptions are missing?
5. Does it emit durable evidence/receipts?
6. Is its authority ceiling explicit?
7. Can another agent/runtime resume it from durable state?
8. Does it avoid creating a second source of truth?

The edges between components are part of the architecture.

---

## 16. Decision rule for future work

Before any major recommendation, Builder package, Final Integrator action or implementation, ask:

> Does this move Quant closer to the full persistent autonomous system described here: one that can generate hypotheses, recover prior knowledge, test and falsify rigorously, validate independently, understand economic identity and portfolio context, progress through explicit authority membranes, learn from prospective/economic outcomes when authorized, detect decay, preserve capital state, and continuously search for replacement edge?

Then ask a second question:

> Which component or connection in the final architecture does this work improve, and what remains explicitly incomplete after it is done?

If a local optimization improves a subcomponent but moves the overall system away from that target, prefer the global target.

No work package, checkpoint, agent or temporary architecture should silently redefine the final system.