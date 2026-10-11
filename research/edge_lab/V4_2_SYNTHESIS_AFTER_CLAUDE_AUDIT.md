# Quant-Trade — V4.2 synthesis after adversarial audit

## Status

This document is a design synthesis only. It does **not** silently change the live Discovery worker contract. The purpose is to turn the V4 challenge + adversarial audit into a sharper target before modifying POLICY / REQUIREMENTS / STATE / scheduler behavior.

Reference doctrine remains `DISCOVERY_FIRST_V4.md` until an explicit V4.2 application commit.

---

## 1. Verdict on the audit

The audit is directionally correct: `REWORK_V4`, not `REPLACE_V4`.

Keep:
- Discovery / Validation split.
- No global blocking by WAIT / RECOVERY_NEEDED.
- Cheap imperfect proxies allowed in Discovery.
- Heavy PIT / execution / rights / capacity work deferred until justified.
- Discovery can never declare a validated edge.

Rework:
- throughput KPIs;
- proxy semantics;
- promotion logic;
- mechanism signatures;
- queue ranking;
- timeboxes;
- research-stop rules;
- unit-economics timing.

The audit is also too conservative in one place: it treats the next refinement mostly as better documentation around each experiment. The core opportunity is stronger than that: every Discovery test should be designed as an **asymmetric decision instrument** with a precise claim it can kill and a precise claim it can support.

---

## 2. Primary objective

Do not optimize tests/week.

Do not optimize commits, gates, completed cards, or even a synthetic DI-Y score.

Optimize:

> expected reduction in decision regret per unit research cost, subject to preserving scientific traceability.

This is not a directly maximized scalar KPI. It is implemented through a small set of ordinal fields and explicit decision contracts.

The operational question before any test is:

> What exact belief or action can this test change, in which direction, and what is the cheapest observation that can cause that change?

---

## 3. Replace proxy taxonomy with inference geometry

`UPPER_BOUND / LOWER_BOUND / DIRECTIONAL / REPRESENTATIVE` are useful descriptions, but they are insufficient because a single proxy can be favorable for amplitude, neutral for sign, and invalid for capturability.

Each experiment should instead declare four inference fields:

### TEST_CAN_KILL
Exact claim that a negative result can falsify.

### TEST_CAN_SUPPORT
Exact claim that a positive result can support.

### TEST_CANNOT_SAY
Conclusions explicitly forbidden from this proxy.

### BIAS_DIRECTION
For each important target dimension, state whether the proxy is expected to bias the test upward, downward, unknown, or approximately neutral.

Example dimensions:
- signal amplitude;
- timing;
- costs;
- survivorship;
- execution quality;
- capacity.

A cheap test may therefore be:
- `ONE_SIDED_KILL`;
- `ONE_SIDED_SUPPORT`;
- `BIDIRECTIONAL`;
- `DESCRIPTIVE_ONLY`.

This is more precise than assigning one global proxy label.

---

## 4. Typed verdicts: stop conflating mechanism, expression and data failure

The current `KILL / PROMOTE / PARK` states are too coarse for learning.

A Discovery result should distinguish at least:

- `KILL_EXPRESSION` — this exact implementation / horizon / proxy expression is not worth pursuing.
- `KILL_MECHANISM` — evidence contradicts the causal mechanism strongly enough to close the family.
- `PARK_DATA` — test could be valuable but data path is currently inefficient.
- `PARK_ECONOMICS` — mechanism may exist but economics are too small / infrequent / capacity-limited for the objective.
- `PROMOTE_EXPRESSION` — exact expression deserves a cleaner L2/L3 test.
- `PROMOTE_MECHANISM` — mechanism is supported, but the best executable expression is not yet known.
- `PROMOTE_HIGH` — unusually strong evidence + economic headroom; priority validation.

This prevents a weak proxy from killing a valid mechanism, and prevents a positive correlation from promoting an entire family.

---

## 5. Mechanism contract before return contract

Every candidate must define before data access:

- `MECHANISM` — causal story in one sentence.
- `WHO_PAYS` — structural payer / constrained participant.
- `WHY_PERSIST` — why competition does not fully arbitrage it.
- `PRIMARY_SIGNATURE` — the most discriminating prediction beyond mean return.
- `ALTERNATIVE_EXPLANATION` — strongest competing explanation.
- `NEGATIVE_CONTROL` or `PLACEBO` — cheap way to separate the two if practical.

A positive mean return with no mechanism signature is at most `PROMOTE_EXPRESSION`, never `PROMOTE_MECHANISM`.

A signature is valid only if predeclared and if it distinguishes the mechanism from at least one plausible alternative.

---

## 6. Unit economics moves before data engineering

Before any test requiring meaningful data work, run a 5–15 minute economic envelope.

Required fields:
- plausible gross effect scale;
- event / trade frequency;
- capital required;
- turnover;
- rough transaction cost band;
- delay sensitivity;
- capacity relevant to small capital;
- expected decay / crowding risk.

The purpose is not precision. It is to establish whether a plausible world exists in which the edge matters.

### Economic headroom

Do not use arbitrary `2x` or `3x` cost stress globally.

Instead define:

`BREAK_EVEN_FRICTION = gross effect size at which all modeled costs consume the edge`

and compare it with a defensible friction interval for the target venue / size / execution style.

Promote only if there is meaningful distance between the discovery estimate and a plausible break-even frontier.

---

## 7. Timeboxes become defaults + extension contract

Keep speed pressure, remove ritual stopping.

Defaults:
- L0 mechanism + unit economics: 15 min.
- L1: 45–60 min.
- L2: 90–120 min.

A test may exceed the default only if **before extension** the worker writes:
- `NEW_INFORMATION_EXPECTED`;
- `WHY_THIS_CHANGES_DECISION`;
- `ADDITIONAL_COST`;
- `STOP_IF_NOT_OBTAINED_BY`.

No extension solely to improve cleanliness, documentation, architecture, or statistical appearance.

Two non-information cycles still imply PARK, unless a predeclared extension contract is active.

---

## 8. Research frontier instead of static priority queue

Do not rank with a precise weighted score; that creates pseudo-science and gaming.

Each candidate gets ordinal fields:
- `DECISION_LEVERAGE = HIGH | MEDIUM | LOW`
- `MECHANISM_PRIOR = HIGH | MEDIUM | LOW`
- `DISCRIMINATING_POWER = HIGH | MEDIUM | LOW`
- `CAPTURABILITY_PLAUSIBILITY = HIGH | MEDIUM | LOW`
- `TIME_TO_VERDICT = SHORT | MEDIUM | LONG`
- `DATA_FRICTION = LOW | MEDIUM | HIGH`
- `CONTAMINATION_RISK = LOW | MEDIUM | HIGH`

Selection is lexicographic:
1. exclude candidates without a plausible path to small-capital economics unless they can falsify a broad family very cheaply;
2. prefer HIGH decision leverage;
3. among those, prefer HIGH discriminating power;
4. then lower data friction / shorter time-to-verdict;
5. use mechanism prior and capturability as tie-breakers;
6. use diversification as a concentration cap, not a quota.

No category must receive work merely to satisfy a target allocation.

---

## 9. Positive results get one cheap adversarial test before strict validation

A positive L1 does not automatically enter V3.

Before promotion, select **one** predeclared highest-value falsifier, for example:
- realistic execution delay;
- conservative cost band;
- naive risk-factor benchmark;
- placebo dates;
- negative-control population;
- sign / monotonicity signature;
- one natural subperiod split fixed in advance.

Do not run a battery of red-team tests. One cheap test should target the largest known failure mode.

If it survives:
- promote.

If it fails:
- type the failure (`KILL_EXPRESSION`, `PARK_DATA`, etc.).

---

## 10. Multiplicity accounting must exist in Discovery, but be lightweight

The audit is correct that selection across many ideas is itself a source of optimism.

Do not impose V3 statistical gates at L1.

Do preserve:
- every experiment ID;
- every tested expression;
- every result, including negative / null;
- every post-result change;
- family / mechanism clustering.

Important distinction:

> 20 tests of one underlying mechanism are not 20 independent discoveries.

Track both:
- `EXPERIMENT_COUNT`;
- `MECHANISM_CLUSTER_COUNT`.

Promotion confidence should be lower when a positive emerged after many sibling expressions.

---

## 11. Kill rules should be asymmetric and explicit

A cheap test should kill a mechanism only when one of these is true:
- the proxy is an explicit favorable bound and the mechanism still fails;
- the primary mechanism signature is contradicted;
- a conservative upper bound on gross economics is below plausible friction;
- the same mechanism has failed across multiple materially distinct expressions without a credible data explanation.

Otherwise, a negative cheap proxy usually means `KILL_EXPRESSION` or `PARK_DATA`, not `KILL_MECHANISM`.

This is the main protection against false KILL.

---

## 12. Discovery should search for edges with structural asymmetry

Prioritize candidates where at least one is true:
- forced / inelastic counterparty;
- mandate or regulatory constraint;
- low-capacity opportunity beneath institutional attention;
- recurring calendar / mechanical flow;
- fragmented market with costly arbitrage;
- settlement / operational convention;
- information that is public but operationally awkward;
- temporary balance-sheet or inventory pressure;
- explicit subsidy / fee / rebate / tax asymmetry;
- payoff asymmetry where small players have an advantage.

Penalize pure pattern mining with no payer, no friction and no persistence story.

---

## 13. Discovery throughput target becomes a diagnostic, not an objective

Keep `tests/week` only as an alarm for stagnation.

Suggested diagnostics:
- discriminating tests completed;
- mechanism clusters touched;
- median time to a typed verdict;
- hours spent with no decision change;
- number of promotions surviving cheap red-team;
- architecture hours;
- number of PARKs reopened due to a genuinely changed fact.

No minimum promotion quota.

A week with 3 high-leverage falsifications can be better than 12 trivial tests.

---

## 14. Immediate consequence for current queue

### CFE / VIX

Do not ask only whether a positive premium exists.

First define whether the candidate is:
- unconditional short-vol risk premium;
- term-structure / roll compensation;
- hedging-pressure conditional premium;
- another expression.

The L1 test must state its benchmark and mechanism signature. A generic positive average can be explained by crash-risk compensation and is not sufficient evidence of an exploitable anomaly.

### SEC / Form 4

Before price mapping work, separate transaction classes (e.g. purchases vs grants / routine sales) based on an economically defensible predeclared rule. Main signature should involve stronger response for transactions with higher information content, not only average post-filing drift.

### France OAT/Bund

Do not choose famous historical fiscal events from model memory. Prefer either a predeclared official event source / rule or a prospective capture. The key test is relative repricing beyond broad European duration / risk factors, not merely a raw spread move.

### Crypto book pressure

The first useful prospective test must predeclare:
- signal construction;
- sampling clock;
- reaction lag;
- horizon;
- crossing / fee assumption;
- naive benchmark;
- one robustness / placebo tied to the mechanism.

No historical archive engineering until this prospective L1 produces a typed positive verdict.

### Policy announcements

Keep prospective. Define before each event what constitutes receipt time, target asset, horizon and benchmark. Do not backfill famous news retrospectively.

---

## 15. What NOT to add

Do not build:
- a generalized experiment orchestration framework;
- a complex Bayesian numerical prior engine;
- a universal weighted DI-Y score;
- extra agent roles;
- a new dashboard architecture;
- more approval gates;
- per-market execution simulators before promotion;
- automated hyperparameter search.

V4.2 should be mostly a **better decision contract**, not a bigger software system.

---

## 16. Minimal V4.2 experiment card

```yaml
id:
family:
mechanism_cluster:
status:
level: L0|L1|L2

mechanism:
who_pays:
why_persist:
primary_signature:
alternative_explanation:
negative_control:

research_decision:
decision_if_positive:
decision_if_negative:

test_can_kill:
test_can_support:
test_cannot_say:
bias_direction:

proxy:
fixed_rule:
benchmark:
cost_band:
break_even_friction:
known_biases:
prior_exposures:

max_time_minutes:
extension_contract: null

result: null
typed_verdict: null
next: null
```

This is intentionally compact. Any field that does not change inference or the next action should not be added.

---

## 17. Acceptance criteria before applying V4.2

A V4.2 application is acceptable only if it makes all of the following true without adding a new architecture layer:

1. every test states exactly what it can kill / support / not say;
2. mechanism and expression verdicts are separated;
3. unit economics is checked before expensive data work;
4. positive results receive one cheap adversarial test before V3;
5. timeboxes can extend only through an explicit information contract;
6. queue choice is based on decision leverage / discriminating power / cost, not age or static priority alone;
7. multiplicity across experiments is preserved without imposing L3 statistics at L1;
8. V3 WAIT / RECOVERY still cannot block Discovery;
9. no new general framework is built;
10. the first three current TEST_NOW cards can be rewritten into this contract and executed without further architecture work.

---

## 18. Final design position

`REWORK_V4`, with a narrow change surface.

The biggest improvement is not another layer, another KPI or another agent.

It is this:

> **Every cheap experiment must have asymmetric inferential rights. Before seeing the result, state exactly what a positive can justify, what a negative can kill, and what neither result is allowed to claim.**

That rule turns Discovery from a high-throughput test factory into a decision-learning system while keeping the speed advantage that V4 was created to recover.
