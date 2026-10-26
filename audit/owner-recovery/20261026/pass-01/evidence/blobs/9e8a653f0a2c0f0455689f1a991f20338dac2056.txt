# Quant-Trade — Legacy Migration Recommendation

Date: 2026-10-15  
Status: conceptual migration recommendation only. This document does not redesign Research OS, authorize Builder, authorize prospective observation, authorize capital, or authorize live trading.

## 1. Migration principle

Future research should consume the reconciled history as an **immutable evidence base**, not as a queue of experiments to rerun.

The conceptual migration unit should be:

```text
RESEARCH_FAMILY
  → HYPOTHESIS
    → GENERATION
      → RESULT / LIMITATION / TRIAL ACCOUNTING / PROVENANCE
```

Do not migrate only the latest verdict. Negative knowledge, blocked data states, spent windows, source failures and amendments are part of the research memory.

## 2. Minimum behaviors for any future Research OS / P0 integration

A future system should, conceptually:

- import `LEGACY_RESEARCH_LEDGER.json` as read-only historical evidence;
- preserve exact historical typed results where recovered;
- preserve `UNKNOWN` rather than synthesize missing facts;
- bind every migrated result to artifact/branch/commit provenance when known;
- distinguish economic generations from non-material parser/reader repairs;
- expose `EVIDENCE_TIMING` so retrospective work cannot masquerade as prospective;
- carry `KNOWN_ATTEMPTS` separately from `EFFECTIVE_TRIALS`;
- retain effective-trial status `KNOWN / ESTIMATED / PARTIALLY_BOUNDED / UNKNOWN`;
- enforce duplicate/rediscovery checks before accepting a “new” hypothesis;
- surface `FALSIFICATION_SCOPE` so expression kills do not become mechanism kills;
- treat access/data/permission blocks as first-class statuses rather than negative returns;
- prevent spent datasets/holdouts from being silently recycled as fresh validation;
- keep operational readiness separate from mechanism/statistical/economic/prospective evidence.

This is a migration contract recommendation, not implementation authority.

## 3. Suggested legacy-status mapping

| Legacy condition | Canonical migration meaning |
|---|---|
| `REJECT_RESEARCH`, family rejection with adequate historical scope | `TESTED_AND_KILLED` for the exact recovered family/scope |
| `KILL_EXPRESSION` | `TESTED_AND_KILLED` at expression level only |
| positive retrospective but weak multiplicity/execution/prospective evidence | `PROMISING_BUT_UNDERPROVED` |
| `PARK_DATA` | `BLOCKED_BY_DATA` unless a later qualification narrows the gap |
| permission/terms restriction | `BLOCKED_BY_PERMISSION` |
| preregistration with no result | `REQUIRES_PROSPECTIVE_VALIDATION` or protocol-only state, not evidence |
| `PROMOTE_EXPRESSION` without independent economic validation | `PROMOTED_EXPRESSION_NOT_EDGE` |
| unrecovered primary result | `UNKNOWN` |
| retrospective result with spent holdout | result retained; future repeat requires `YES_WITH_NEW_GENERATION` if the same question truly needs retesting |

## 4. Final decision matrix

| Research family | Historical status | Evidence strength | Economic status | Prospective status | Trial-accounting status | Remaining blocker | Repeat research needed? | Next legitimate step |
|---|---|---|---|---|---|---|---|---|
| NASDAQ short-horizon reversal | historical `REJECT_RESEARCH` | negative legacy, incomplete protocol recovery | killed for fixed expression | none recovered | unknown | none for same expression | **NO** | Preserve negative; only materially new generation could reopen |
| Broad futures trend+carry | retrospective positive | strong historical statistics, execution/survivorship limitations | promising but underproved | none recovered | campaign partially bounded | prospective/execution evidence | **ONLY_MISSING_COMPONENT** | Validate missing components only if separately authorized |
| B4 small-universe TSMOM | `FAMILY_REJECTED` | explicit 40-trial gate | killed on spent B4 family/window | none | **40 known** | none for same family/window | **NO** | Do not recycle spent validation window |
| B2 sector XRev | negative replication confirmed | explicit 36-expression family | killed as expressed | none | **36 known** | none for same expressions | **NO** | Do not rename/regrid same family |
| Sector shock reversal | `KILL_EXPRESSION` | explicit economic negative | killed expression only | none | exact global M unknown | none for exact expression | **NO** | Preserve scope; do not infer family kill |
| Stock/bond joint-stress rebound | `KILL_EXPRESSION` | explicit economic negative | killed expression only | none | unknown | none for exact expression | **NO** | Preserve negative |
| Month-end pension rebalance | retrospective indicative + later data-gated formal generation | mixed/moderate | promising but underproved; later generation unresolved | none | global M unknown | adequate permitted data / clean generation | **ONLY_MISSING_COMPONENT** | Reuse prior mechanism/protocol rather than rediscover |
| FOMC pre-announcement overnight | retrospective positive inside broad campaign | indicative after multiplicity context | promising but underproved | none | partially bounded by ~60 campaign | prospective validation / authority | **ONLY_MISSING_COMPONENT** | Preserve exact event definition; no generic policy extrapolation |
| Broader policy-announcement repricing | `PARK_UNTIL_AUTHORITY` | exact primary lane incomplete | unknown | none | unknown | Owner authority | **UNKNOWN** | Owner decision only; no test under current mission |
| Prediction-market generic FLB | sign unstable across samples | mixed | no stable generic taker edge | none | campaign-level only | clean venue-specific evidence if ever justified | **NO** for generic rule | Do not reintroduce “buy favorites/longshots” as novel |
| F2 Kalshi FLB | `BLOCKED_DATA_PERMISSION` | protocol/rights evidence strong, economic evidence absent | unresolved | no outcome access | 0 new economic trials | documented rights/allowed route | **ONLY_MISSING_COMPONENT** | Rights decision only; no bypass |
| Prediction negRisk/combinatorial | tested/rejected after fees/basis issues | moderate historical negative | no opportunity in tested implementation | none | partially bounded | structural market change only | **NO** | Do not repeat easy public arb screen absent changed mechanics |
| BTC→prediction-market latency | 1s positive, 3s+ gone | limited one-day retrospective | inaccessible to slow implementation | none | unknown | latency infrastructure + independent sample | **YES_WITH_NEW_GENERATION** only if infrastructure materially differs | Otherwise preserve as mechanism knowledge |
| Sports sharp-price / CLV | mixed; hindsight and causal lines separated | large sample, high multiplicity | promising/underproved for clean executable use | none | partially bounded | legitimate feed + prospective venue mapping | **ONLY_MISSING_COMPONENT** | Never upgrade close-price hindsight checks to causal evidence |
| Historical crypto carry | historical positive but decayed vs hurdle | moderate/strong historical | no current opportunity in recovered regime | none | part of 35-config crypto campaign | materially changed funding-vs-cash regime | **NO** in same regime | Reconsider only under a genuinely changed generation |
| HL/CEX funding spread | strong retrospective modeled result, decay/execution risk | moderate | promising but underproved | none | partially bounded | prospective capture + one-leg/ADL execution model | **ONLY_MISSING_COMPONENT** | Preserve mechanism and old result; validate missing pieces only |
| Binance extreme-funding reversal | `PARK_DATA` HTTP 451 | no economic evidence | unresolved | none | one attempted run; effective M unknown | permitted source access | **YES_WITH_NEW_GENERATION** if rerun ever authorized | Do not substitute source inside historical generation |
| Simple liquidation rebound | negative/unstable | moderate retrospective negative | killed for simple hourly expressions | none | partially bounded | none for same simple rule | **NO** | A different forced-flow microstructure mechanism must be materially distinct |
| Hyperliquid forced-flow paused lane | `PARK_DATA_CONFIRMED` | exact primary provenance incomplete | unresolved | unknown | unknown | qualified data gap | **ONLY_MISSING_COMPONENT** | Bind primary artifact / complete qualified gap only |
| CFE VIX term premium | v0/v1 `PARK_DATA`; reader repair `PROMOTE_EXPRESSION` | technical/data evidence, no independent edge validation | promoted expression, not edge | prospective registration exists, no result | effective M unknown | distinct admissible evidence package | **ONLY_MISSING_COMPONENT** | `NO_NEW_ECONOMIC_ACTION` under current state |
| Treasury 5Y / ZF | `PARK_DATA`; later `L0_DAILY_SOURCE_GATE_PASS` | source qualification improved; canonical economics unresolved | unresolved | none | outcome exposure exists; M unknown | population/source integrity | **ONLY_MISSING_COMPONENT** | Complete data/source gap only if authorized |
| France OAT/Bund | `PARK_DATA`; later `L0_DAILY_SOURCE_GATE_PASS` | data-route evidence only | unresolved | none | unknown | remaining data adequacy | **ONLY_MISSING_COMPONENT** | Do not invent new France thesis; complete route gap only |
| CFTC ES sentiment | `PARK_DATA`, economics never opened | no economic evidence | unresolved | none | unknown | adequate data | **ONLY_MISSING_COMPONENT** | Data completion only |
| SEC Form 4 insider clusters | census recovery + EOD `PARK_DATA`, 0 economic tests | strong infrastructure history, missing durable census | unresolved | none recovered | 66 Actions runs are workflow attempts, not effective economic trials | durable census + defensible price route/rights | **ONLY_MISSING_COMPONENT** | Recover existing artifacts; **no rebuild currently authorized** |
| Crypto book-pressure prospective | invalid prospective capture | strong negative implementation evidence | unresolved mechanism | attempted prospectively but invalid | 0 valid economic trials | valid capture architecture | **YES_WITH_NEW_GENERATION** | Historical attempt stays invalid; no automatic rerun |
| Russell deletion basket | predeclared, not armed | protocol only | unresolved | no outcome access | effective M unknown | route rights/software/authority | **ONLY_MISSING_COMPONENT** if still pristine and authorized | Reuse exact declaration rather than reselect basket |
| Corporate-action prospective protocols | declarations/protocols only | documentary | unresolved | no completed result recovered | 0 completed economic trials | event admission/source/authority per protocol | **ONLY_MISSING_COMPONENT** | Preserve exact experiment IDs; no duplicate hypothesis generation |
| Weather V1/V2 | design lineage; V2 blocked by inference defect | strong design-negative evidence | no economic verdict | none | 0 economic trials | obsolete/repaired design issues | **NO** | Preserve design lessons; do not revive V1/V2 |
| Weather V3 | `V3_NOT_JUSTIFIED` | program-level negative | no demonstrated edge | none | unknown design activity, no economic validation | materially different mechanism | **NO** | Do not rebuild V3 |
| Weather V4 | pre-op audit passed for consideration; phase not granted | strong governance artifact, no economic evidence | unresolved | none | 0 economic trials | Owner phase decision + unresolved controls | **UNKNOWN** | Preserve OD01–OD12; no phase/economic work currently authorized |
| MLB/soccer/weather replication | primary artifact unrecovered | unknown | unknown | unknown | unknown | provenance recovery | **UNKNOWN** | Recover artifact only, never recreate solely to fill history |
| Box Office | primary artifact unrecovered | unknown | unknown | unknown | unknown | provenance recovery | **UNKNOWN** | Recover artifact only |

## 5. Research status map

### TESTED_AND_KILLED / do not repeat as-is
- B2 sector XRev expressions.
- B4 small-universe macro TSMOM family on spent window.
- Exact sector-shock reversal expression.
- Exact stock/bond stress-rebound expression.
- Generic public negRisk/combinatorial implementation.
- Simple hourly liquidation-rebound implementation.
- Legacy NASDAQ reversal expression.

### TESTED_BUT_UNCERTAIN / PROMISING_BUT_UNDERPROVED
- broad futures trend+carry;
- HL/CEX funding spread;
- FOMC overnight;
- month-end pension;
- sports sharp-price/CLV implementation.

### BLOCKED_BY_DATA / ACCESS / PERMISSION
- Treasury/ZF;
- France OAT/Bund;
- CFTC ES;
- Binance reversal;
- SEC Form 4;
- Hyperliquid forced-flow;
- F2 Kalshi permission;
- invalid book-pressure capture requires a new prospective generation, not a silent repair.

### PROMOTED_EXPRESSION_NOT_EDGE
- CFE VIX reader-repaired expression.

### REQUIRES_PROSPECTIVE_VALIDATION
Every retrospectively positive family that might ever be considered again. No recovered family has earned `PROSPECTIVE_VALIDATED` status.

### UNKNOWN
- Box Office primary result.
- MLB/soccer/weather primary replication result.
- exact global effective-trial denominator.
- genuinely unexplored mechanism space.

## 6. Recommended anti-restart policy

Before any future hypothesis enters a queue, require a lookup against:
1. exact IDs in the legacy ledger;
2. the duplication map;
3. economic identity/mechanism tags;
4. spent dataset/window history;
5. negative knowledge and falsification scope;
6. open blockers and existing next legitimate step.

If the same question was already answered, `Repeat research needed? = NO` should be the default. A new generation should be admitted only for a **material** change, not because a new model wants to rerun an old idea.

## 7. What this migration recommendation does not authorize

It does not authorize:
- implementation of a Research OS;
- new agents;
- Builder activity;
- new data acquisition;
- prospective observation;
- any old or new economic test;
- capital or trading.

It only specifies how the historical evidence should conceptually survive into future tooling.
