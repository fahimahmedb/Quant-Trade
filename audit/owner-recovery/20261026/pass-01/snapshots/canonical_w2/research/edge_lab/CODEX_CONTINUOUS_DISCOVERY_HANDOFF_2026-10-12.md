# Codex continuous discovery handoff — 2026-10-12

REPOSITORY = fahimahmedb/Quant-Trade
SOURCE_BRANCH = research/edge-lab-continuous
MODE = PRODUCTIVE_RESEARCH_UNTIL_CONTEXT_OR_TOKEN_EXHAUSTION
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Mission

Maximize economic information gained per token and per minute. Keep taking small, causally distinct, low-cost research actions until context/tokens are nearly exhausted or a true external blocker requires future data. Do not wait for the Owner between routine steps.

The hourly ChatGPT fallback worker remains enabled on the same source branch. Therefore every write is race-sensitive: never force-push and never overwrite a newer remote state.

## Read once at start

1. `research/edge_lab/CONTROL.json`
2. `research/edge_lab/EDGE_DISCOVERY_METHOD.md`
3. `research/edge_lab/discovery/STATE.json` — inspect only current status/next/unfinished/claims/exposure fields; do not repeatedly dump the whole file.
4. This handoff.

Then operate from fresh remote state. Re-read CONTROL only at material boundaries and before any economic look.

## Existing valid prospective protocols

Treat these as immutable unless a purely documentary clock/source correction is required BEFORE any event/outcome exposure:

- `discovery/experiments/disc-us-issuer-oddlot-priority-prospective-l1-v1.md`
- `discovery/experiments/disc-us-reverse-split-cash-in-lieu-prospective-l1-v2.md`
- `discovery/experiments/disc-us-reverse-split-round-up-prospective-l1-v2.md`
- `discovery/experiments/disc-us-spac-redemption-floor-prospective-l1-v1.md`
- `discovery/experiments/disc-us-etf-liquidation-nav-convergence-prospective-l1-v1.md`

INVALID for prospective admission: reverse-split cash-in-lieu v1 and round-up v1 because their creating commits were after their stated T0.

The first qualifying fresh event under a frozen protocol must be persisted/claimed BEFORE any selected-event price, NAV, payout, completion or economic payload. Never skip an unattractive event.

## Known parked / closed areas

Do not restart from zero or consume tokens re-proving these unless a genuinely new access fact appears:

- WTI producer-hedging-pressure: `PARK_DATA`; do not re-probe CME/DataMine without a new zero-cost historical CL retrieval fact.
- Treasury daily 5Y auction expression: parked, no replay.
- VIX completed promoted exploratory expression: no replay/nearby tuning; L2 data dependency parked unless genuinely new distinct access.
- SEC Form-4 census: existing history; do not rebuild default crawl.
- France TEC10 route: rights/access blocked; do not substitute proxy silently.
- closed families include F1 crypto carry, daily ETF B2/B4, prediction negative-risk, fixed SMARD expression.
- Binance extreme-funding one-shot was `PARK_DATA` after frozen endpoint HTTP 451; no source substitution/replay.

## Token-efficient action loop

Repeat this loop continuously. Each iteration should normally consume only a few shell/web/API actions and produce one durable research state transition.

### 0. Refresh cheaply

`git fetch origin research/edge-lab-continuous`

If local HEAD is behind, fast-forward/rebase before doing work. Read fresh `CONTROL.json`. If `paused=true`, stop. Never force-push.

### 1. Resolve the highest-value currently-open item

Priority:

A. If an already-frozen prospective protocol has a qualifying post-T0 event, persist the exact event identity/clock/eligibility receipt BEFORE economic payload access.
B. If an economic look is already claimed/unresolved, do NOT open another; perform documentary/source qualification or L0 breadth instead.
C. If no active event/look, take one small causally distinct L0 mechanism from public sources.
D. If an L0 has `L1_NOW`, qualify the minimum data route and freeze one cheap discriminating L1 BEFORE outcomes.
E. If a frozen, legitimately claimed L1 is executable and there is no other unresolved economic look, execute it exactly once and classify KILL / PARK / PROMOTE within its declared inference rights.

### 2. Prefer micro-actions, not essays

Useful micro-actions include:

- one bounded SEC/EDGAR prospective metadata scan;
- one issuer/exchange/regulator primary-document qualification;
- one data-route HEAD/schema/licensing check without payload;
- one L0 mechanism qualification;
- one prospective L1 predeclaration with future T0;
- one exact claim/selection receipt;
- one one-shot frozen computation;
- one adversarial check only if predeclared and primary criteria allow it;
- one clean PARK_DATA / PARK_ECONOMICS / KILL_EXPRESSION decision.

Avoid generic literature reviews, architecture work, dashboards, governance rewrites, broad code refactors, or long narrative reports.

### 3. L0 filter

For a new mechanism answer only:

- MECHANISM
- WHO_PAYS
- WHY_PERSIST
- CHEAP_DATA_NOW
- CHEAP_EXPRESSION
- FATAL_PROBLEM

Then choose only one: `L1_NOW`, `PARK_DATA`, `PARK_ECONOMICS`, `DUPLICATE`.

L0 MUST NOT inspect signal -> future return/PnL.

Prefer small-actor niches: discrete corporate-action rules, odd lots/fractions, tiny fund closures, redemption/settlement mechanics, irregular public events, fragmented public data, nuisance operations, capacity-limited effects. Mechanism breadth beats parameter variants.

### 4. Before any economic look

Freeze in a file/commit BEFORE outcome access:

- exact universe/event-selection rule;
- exact public-time clock;
- exact entry/exit/payoff;
- fixed quantity if needed;
- central + stress frictions;
- adequacy requirement;
- KILL/PARK/PROMOTE rule;
- one adversarial check at most;
- explicit inference limits;
- exposure/independence status.

No tuning after outcome access. Material changes become a new linked variant with full exposure history.

### 5. One economic look at a time

Before claiming an economic look, refresh remote HEAD + `CONTROL.json` + current unfinished claims. Commit/push the claim first. If push loses a race, fetch/re-read and do not continue until state is reconciled.

The hourly fallback worker may write concurrently. A newer remote claim wins. Never overwrite it.

### 6. Persist compactly

Important work must never live only in chat/stdout.

For each meaningful action, persist the smallest useful artifact and commit it immediately. Prefer <=1 focused file plus required state update. Commit messages should start `research:`.

A result receipt should be compact and contain at least:

- RESULT
- EFFECT_SIZE or `NOT_COMPUTED`
- UNCERTAINTY
- POWER_LIMITATION
- ECONOMIC_SIGNIFICANCE
- FAILED_CRITERIA
- LESSON
- FAMILY_STATUS
- NEXT_DECISION

Do not duplicate source text. Link primary sources and record exact timestamps/accessions/hashes where cheap.

### 7. Conserve tokens aggressively

- Use `rg`, `jq`, `git diff`, targeted line reads; do not repeatedly print giant STATE files.
- Reuse already-qualified sources and cached artifacts.
- Prefer scripts/CLI over verbal reasoning when deterministic.
- Batch independent metadata checks in one shell invocation when safe.
- Max ~3-5 primary-source requests for a normal L0 micro-action; if unresolved, PARK and move on.
- Do not explain routine steps to the user while working.
- Do not create a new framework/version because a capability is missing.
- Never spend paid USD.

### 8. Candidate-generation territories

When breadth is needed, choose a territory not already exhausted. Examples, not requirements:

- corporate actions beyond existing tender/reverse-split rails;
- ETF/fund mechanics beyond the already-frozen liquidation rail;
- index/reconstitution implementation frictions where public timing is exact;
- exchange/regulatory fee or settlement asymmetries accessible to tiny capital;
- primary-market allocation/proration quirks;
- public-data release mechanics with true tradable timing and free executable proxy;
- futures/options mechanics only if complete zero-cost tradable data exists now;
- cross-market operational constraints where small capacity is an advantage.

Reject quickly when WHO_PAYS or CHEAP_DATA_NOW is weak.

## Git race protocol

Work directly on `research/edge-lab-continuous` so the fallback worker can see progress.

Before each commit:

1. `git fetch origin research/edge-lab-continuous`
2. if remote moved, rebase/reconcile narrowly;
3. re-read any file you will replace;
4. commit focused changes;
5. `git push origin HEAD:research/edge-lab-continuous` WITHOUT force.

If push is rejected, fetch and reconcile. Do not retry by force.

## Stop conditions

Do NOT stop merely because no READY task exists. Generate another causally distinct L0 or qualify data.

Stop only when one of these is true:

- CONTROL.paused=true;
- context/tokens are nearly exhausted;
- a true external blocker means no useful documentary/L0 work remains in this session;
- a future-time prospective event/outcome is required and all other cheap breadth work is temporarily exhausted.

Before token/context exhaustion, persist a final compact checkpoint on GitHub containing: fresh HEAD, unresolved claim if any, last useful result, exact NEXT action, and invariants. Then push.

## Hard invariants

`REAL_CAPITAL_AUTHORIZED = FALSE`
`LIVE_TRADING_AUTHORIZED = FALSE`
`PAID_USD_AUTHORIZED = 0`

No broker orders, no live trading, no real-capital authorization, no fabricated PASS/edge claim, no replay or hidden retuning, no deletion of exposure history.

The terminal objective is not activity. It is to reduce expected time to a real, capturable, still-live edge.