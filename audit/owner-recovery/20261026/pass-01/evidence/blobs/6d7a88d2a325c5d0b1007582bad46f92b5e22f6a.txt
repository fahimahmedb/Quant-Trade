# V4.2 pilot — inference-rights contracts

Status: DESIGN PILOT ONLY. This folder does not modify the live Discovery worker, POLICY.json, REQUIREMENTS.md, STATE.json, or scheduler behavior.

Purpose: test whether the V4.2 contract is precise enough on three existing TEST_NOW cards before implementation.

The three pilot cards are:

- `disc-cfe-vix-term-premium-l1-v0.md`
- `disc-sec-form4-eod-l1-v0.md`
- `disc-france-oat-bund-l1-v0.md`

## Rule of the pilot

Before any data access or calculation, each card must make all possible interpretations explicit enough that a future result cannot be requalified opportunistically.

Each card therefore defines:

1. exact expression under test;
2. mechanism and structural payer;
3. primary mechanism signature;
4. strongest alternative explanation;
5. decision targeted by the test;
6. `TEST_CAN_KILL`;
7. `TEST_CAN_SUPPORT`;
8. `TEST_CANNOT_SAY`;
9. bias direction by inference dimension;
10. conditions under which a negative is actually informative;
11. unit-economics envelope and break-even-friction question;
12. one predeclared adversarial follow-up if L1 is positive;
13. typed verdict mapping.

## Typed verdicts allowed in this pilot

- `KILL_EXPRESSION`
- `KILL_MECHANISM`
- `PARK_DATA`
- `PARK_ECONOMICS`
- `PROMOTE_EXPRESSION`
- `PROMOTE_MECHANISM`
- `PROMOTE_HIGH`
- `INCONCLUSIVE`

`INCONCLUSIVE` is permitted only when the predeclared data-adequacy condition fails. It must never be used to rescue a negative after the fact.

## Anti-requalification rule

If, after observing a result, the worker changes any of the following, that is a new linked experiment rather than a reinterpretation of the old one:

- signal definition;
- event definition;
- universe;
- horizon;
- threshold;
- proxy;
- benchmark;
- cost model;
- execution delay;
- sample inclusion rule.

## Pilot acceptance test

The contract is considered useful only if, before seeing outcomes, a reviewer can answer for each possible result:

- what belief changes;
- what action changes;
- what remains unknown;
- whether the next action is cheaper data, one adversarial falsifier, strict validation, parking, or closure.

If any branch remains ambiguous, revise the card before running the experiment. Do not add worker architecture to compensate for an ambiguous research contract.
