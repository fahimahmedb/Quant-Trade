# CODEX HANDOFF — V4.2 WIRE-UP

Repo: `fahimahmedb/Quant-Trade`
Branch: `research/edge-lab-continuous`
Goal: resume from current HEAD; do **not** restart research or rebuild architecture.

## Read only these first
1. `research/edge_lab/V4_2_SYNTHESIS_AFTER_CLAUDE_AUDIT.md`
2. `research/edge_lab/discovery/v4_2_pilot/README.md`
3. `research/edge_lab/discovery/v4_2_pilot/disc-cfe-vix-term-premium-l1-v0.md`
4. `research/edge_lab/discovery/v4_2_pilot/disc-sec-form4-eod-l1-v0.md`
5. `research/edge_lab/discovery/v4_2_pilot/disc-france-oat-bund-l1-v0.md`
Then inspect existing live V4 files only as needed: `DISCOVERY_FIRST_V4.md`, `discovery/POLICY.json`, `discovery/REQUIREMENTS.md`, `discovery/STATE.json`, scheduler/worker code.

## What changed while you were away
- V3 stays the **strict validation lane**; its WAIT / RECOVERY must never block discovery.
- V4 introduced **Discovery First**: cheap proxies, unit economics first, architecture tax, PARK instead of global blocking.
- Claude challenge -> V4.2 refinement: each cheap test gets **asymmetric inferential rights** declared before result:
  - `TEST_CAN_KILL`
  - `TEST_CAN_SUPPORT`
  - `TEST_CANNOT_SAY`
  - `BIAS_DIRECTION` by dimension
- Verdicts are typed: `KILL_EXPRESSION`, `KILL_MECHANISM`, `PARK_DATA`, `PARK_ECONOMICS`, `PROMOTE_EXPRESSION`, `PROMOTE_MECHANISM`, `PROMOTE_HIGH`; plus `INCONCLUSIVE` only when a predeclared data-adequacy condition fails.
- Post-result changes to signal/horizon/universe/proxy/benchmark/cost/delay/inclusion = **new linked experiment**, never silent reinterpretation.
- Unit economics and `BREAK_EVEN_FRICTION` come before expensive data engineering.
- Positive L1 gets **one** predeclared cheap adversarial test before strict validation.
- Timeboxes are defaults; extension requires `NEW_INFORMATION_EXPECTED`, `WHY_THIS_CHANGES_DECISION`, `ADDITIONAL_COST`, `STOP_IF_NOT_OBTAINED_BY`.
- Queue selection should favor decision leverage + discriminating power + low data friction / fast verdict; no weighted pseudo-score.
- Multiplicity remains lightweight but explicit: experiment count + mechanism-cluster count.
- No new orchestration framework / Bayesian engine / dashboard architecture / agent roles.

## Pilot status
Three V4.2 contracts already exist and are intentionally **not wired into the live worker yet**:
- VIX/CFE term-premium L1
- SEC Form 4 EOD L1 using public filing availability, not transaction date
- France OAT/Bund L1 relative repricing

These are the crash-test for the method. Preserve them; improve only if you can show a concrete ambiguity or false inference path.

## Your task
Please **wire V4.2 into the existing system with the smallest possible change surface** and optimize it before enabling it.

Acceptance target:
1. keep V3 validation intact;
2. migrate live Discovery contract/state to V4.2 semantics without a parallel framework;
3. preserve all old exposures / CLOSED families / multiplicity history;
4. make a blocked validation task non-blocking for Discovery;
5. make experiment pre-declaration immutable before outcome access;
6. enforce typed verdicts + inference rights + data-adequacy rule;
7. enforce unit-economics-before-heavy-data and one-cheap-red-team logic;
8. keep architecture work <=10% and refuse refactors that do not unlock >=2 experiments or protect result integrity;
9. update telemetry/site state only as needed to expose Discovery vs Validation truthfully;
10. after tests pass, execute the **cheapest admissible pilot** instead of doing more architecture.

## Optimization mandate
You are allowed to simplify or remove V4/V4.2 machinery if it improves expected time-to-decision without weakening the three hard invariants:
- no real/live capital;
- no hidden retune/replay after outcome exposure;
- Discovery never claims a validated edge.

Prefer deletion / reuse over new abstractions. Reuse V3 CAS/receipts where useful, but do not force L3 ceremony onto L1.

Before coding, return a short plan with:
`KEEP / CHANGE / DELETE / FIRST_EXPERIMENT`.
Then implement, test, persist, and move to economic research.