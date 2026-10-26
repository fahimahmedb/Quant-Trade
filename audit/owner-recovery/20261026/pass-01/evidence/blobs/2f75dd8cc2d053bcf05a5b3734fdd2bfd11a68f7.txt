# Wave-1 CLAUDE — protocol decisions still owed, and what is now mechanical

**Status:** BUILDER PROPOSAL — REQUIRES BLUE / MISSION CONTROL AUTHORITY
**Branch:** `parallel/claude-wave1-economic-system-2026-09-19`
**Base:** `8d5dbb41559c4716e94d5290b6ae979a8b96143c`

This artifact decides nothing. It separates the protocol work that Wave 1 made
*mechanical* from the protocol work that is still a scientific decision, and for
each remaining decision it states the admissible options and what each one costs.

Nothing here reads the P0 prospective reservoir, quotes a D05 ceiling, or uses a
Form 4 outcome. Every option below is stated from the frozen governance record and
from public source structure only.

---

## 1. What became mechanical in this wave

| Object | Before | Now |
|---|---|---|
| D07 closed signal semantics | prose in `D07_OPEN_SPACE_BOUNDARY.md` | `quant.science.formation`, with `WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS` enforced and a discriminating test |
| D07 closed population | prose section 2.1 | `quant.science.eligibility`, including the code-`A`-versus-indicator-`A` trap |
| D05-A design-invariance test (D07 §5) | a rule to be applied by hand | `quant.science.invariance.design_invariance`, classifying any quantity over the full admissible `O1 × O2 × O3 × O4` space |
| Allocation-weighted estimator and its variance | EC1 warned the naive variance is wrong | `quant.science.inference.ratio_estimate`, cluster-robust with the random denominator respected |
| `Φ / BEEE / M_economic / MEUE` | four open D09 objects | `quant.economics`, mechanical and outcome-blind, reporting `RECIPE_PROVISIONAL` rather than claiming authority it lacks |
| Terminal/absent observation | undefined, easy to paper over | routed to `D19_TERMINAL_TREATMENT_REQUIRED`, never to a payoff substitute |

The consequence for the decisions below is that Blue can now classify each
candidate metric *before* choosing a geometry, instead of choosing a geometry and
arguing about invariance afterwards.

---

## 2. D07 final geometry (workstream 12) — four choices, none taken

The boundary is frozen and exhaustive where D07 says it is. I implemented every
admissible option and refused to select among them.

### O1 — projection of an EDGAR date with no regular session

Admissible set is closed and exhaustive: `{PREVIOUS_REGULAR_SESSION,
NEXT_REGULAR_SESSION}`. `NEAREST_REGULAR_SESSION` is refused by name in code.

What the choice moves: only filings whose EDGAR date falls on a non-session day,
and only by shifting which 10-session formation window they join. A worked test on
the branch shows a case where one convention forms a signal and the other does
not, so the formation event count is **claim-design-sensitive** and belongs to
D05-B, not D05-A.

Cost of each option: `PREVIOUS` attaches a weekend filing to a window that closed
before the market could act on it, which is defensible for *formation* geometry
(the insider's second purchase existed) and is not an entry rule. `NEXT` keeps
formation and entry on the same side of the weekend. Neither is dominated. This is
a convention choice, and the honest reason to prefer one is interpretive, not
empirical — which is exactly why it must be frozen before values are seen.

**Decision owed:** one of the two. **Refused here.**

### O2 — intra-session application order and the crossing instant

D07 requires a deterministic order, a logical instant for `<2 → ≥2`, and a tie
rule where the source gives no strict order. D07 does **not** enumerate the
admissible set, so I did not invent one: the engine consumes a declared ordering
key and refuses to run without it.

What the choice moves: which filing/owner is designated as the triggering
observation, and the logical trigger position inside the session. The branch has a
test showing two declared orderings naming different triggering owners on the same
data. It cannot move the threshold, the window membership, the expiry timing, or
the entry date.

**Decision owed:** the admissible O2 set, plus the selection within it. **Refused
here** — enumerating the admissible set is itself a boundary decision.

### O3 — interval identification for the closed 20-session hold

The holding length is closed. Only indexing is open: where the interval starts,
how sessions are numbered, where the twentieth ends, and how an expected session is
represented when the security is not normally observable.

Implemented as a declared convention carrying an exit index offset, with offsets
that would change the closed twenty-session hold refused. Two offsets are
arithmetically compatible with a twenty-session hold depending on whether the exit
is at the open of session `E+20` or the close of session `E+19`; the branch treats
both as admissible *candidates* for the invariance test and selects neither.

**Decision owed:** the convention, and whether the two candidates above are in
fact both admissible. **Refused here.**

### O4 — overlap geometry

Still legitimately open, and the only dimension that can change the meaning and
cardinality of an *observation*. Until it is declared, the engine returns
`D05_B_UNTIL_O4_FROZEN` for any observation count, matching D07's own statement
that `observation_count_per_issuer` is D05-B until O4 is frozen.

**Decision owed:** whether two distinct signals remain two observations when
exposure windows overlap; treatment of a new same-issuer signal after re-arm while
a prior exposure is live; cross-issuer overlap representation; and the statistical
unit when one issuer contributes several partially overlapping windows. **Refused
here.** This one materially changes the statistical unit, and therefore the
variance object the D08 inference consumes.

---

## 3. D05 discharge conditions (workstream 13)

Dischargeable **without any empirical value**, now that the invariance test is
executable: for each candidate D05-A metric, run `design_invariance` over the full
admissible space and record the classification. A metric that comes back
`DESIGN_INVARIANT_D05A_ELIGIBLE` is discharged as D07-independent; anything
`CLAIM_DESIGN_SENSITIVE_D05B` is routed to D05-B; anything `AMBIGUOUS_EMBARGO`
must be resolved before execution and without inspecting values.

What this wave did **not** discharge: the metric list itself, the strata, and the
stopping rule. Those are D05-A freeze objects with their own artifacts, and
proposing them from this branch would amount to choosing what gets measured.

**Recommended sequence, requiring no new authority:** classify every already-named
candidate metric with the executable test, publish the classification table, and
only then open the metric/strata/stopping freeze. The classification is
reproducible and outcome-blind, so doing it first costs nothing and removes the
usual argument.

---

## 4. D05-B / D08 preparation (workstream 14)

What the branch now supplies, ready to be frozen rather than invented later:

* the estimator: the allocation-weighted ratio, on the EC1 coordinate;
* its variance: cluster-robust with the random denominator respected, plus a
  seed-declared cluster bootstrap for when the linearisation is not trusted;
* the multiplicity budget: widenable with disclosure, never narrowable;
* null models that preserve structure, with placebo offsets overlapping the true
  exposure window refused;
* the separation of statistical distinguishability from economic sufficiency, so
  neither can stand in for the other.

What remains a decision, and is **refused here**:

1. **Clustering unit.** The variance depends on it and O4 defines it. This cannot
   be frozen before O4.
2. **α, power target, and the one-sided versus two-sided form.** A one-sided test
   is defensible for a directional economic claim and changes the threshold
   materially. Not a Builder choice.
3. **Sequential / stopping rule for forward confirmation.** How many forward
   windows, what may end the test early, and what an early stop does to the
   threshold.
4. **Futility and equivalence boundaries.** The economic engine already kills a
   lane whose whole interval sits below MEUE; the statistical futility boundary is
   separate and unfrozen.
5. **Which variance method is authoritative** when delta-method and bootstrap
   intervals disagree. Choosing after seeing both is result-driven selection; the
   rule must precede the numbers.

---

## 5. D19 specification (workstream 15)

`D07-O3` explicitly defines no payoff substitute, and the branch honours that: a
session inside the exposure interval that is not observable returns
`D19_TERMINAL_TREATMENT_REQUIRED` and no number.

What D19 must define, with the options I can see and no selection among them:

| Case | Options visible from the frozen record | Consequence |
|---|---|---|
| Delisting mid-interval | proceeds at last authorized price; hold to a defined terminal instant; treat as an adverse terminal outcome | favourable truncation would bias the effect upward; exclusion would create survivorship |
| Cash acquisition completing mid-interval | consideration as the terminal value; truncate at announcement | announcement truncation discards a real economic outcome |
| Halt spanning the exit session | roll to the first session with a price; treat as terminal | rolling changes the closed interval length and interacts with O3 |
| Missing price mid-interval, security still listed | interpolate (refused by the branch), carry forward, or mark the interval incomplete | interpolation invents an observation |
| Exchange/listing change | continuity of identity by issuer CIK, or a new instrument | affects whether the interval survives at all |

Also owed by D19: the **adverse perturbation set** and the thresholds at which a
perturbation is considered to have changed the conclusion, and how final inference
consumes them. The branch supplies the robustness machinery (the same invariance
harness works for perturbation sets) but not the set or the thresholds.

**Refused here.** Every option above changes the sign or magnitude of a realised
outcome, and choosing one is a scientific decision.

---

## 6. Builder allocation proposal (workstream 29)

One writer per domain, because the failures this system suffers from are
concurrent writes to shared economic state, not a shortage of parallelism.

| Domain | Files | Writer |
|---|---|---|
| P0 SEC capture, pre-`t0` | `src/quant/dataplane/sec/**`, `deploy/**` | Astra — exclusive, unchanged |
| Control plane / clock | `src/quant/clock.py`, `scripts/quant.py` | frozen while fingerprint-critical; no writer |
| Economic engine | `src/quant/economics/**` | one Builder |
| Scientific protocol | `src/quant/science/**` | one Builder, distinct from the economic writer so the economic engine cannot quietly relax a protocol object to make a threshold reachable |
| Data plane, non-SEC | `src/quant/dataplane/*.py` | one Builder |
| Desk / book / factory (V1) | `src/quant/desk/**`, `book/**`, `factory/**` | one Builder |
| Operations | `src/quant/operations/**` | may share the desk writer |
| Governance artifacts | `governance/**` | Blue only; Builders write proposals to `handoff/` |

The separation that matters most is economic engine versus scientific protocol.
They are the two objects that can be traded off against each other, and one writer
holding both is how a threshold gets negotiated down.

---

## 7. Decisions refused in this wave

Stated plainly, because the value of a refusal is lost if it is not recorded:

1. O1, O2, O3 and O4 selections (workstream 12).
2. The admissible O2 and O3 *sets*, where D07 leaves them unenumerated.
3. The D05-A metric list, strata and stopping rule (workstream 13).
4. α, power, one- versus two-sided form, sequential stopping, futility and
   equivalence boundaries, and the authoritative variance method (workstream 14).
5. Every D19 terminal-treatment option and the adverse perturbation set
   (workstream 15).
6. Numerical Form 4 cost coefficients, uncertainty envelopes, and the joint
   adverse scenario values (workstream 1). The recipe is built; the numbers are
   Blue's, and `src/quant/economics` asserts none.
7. Promotion of the `M_economic` functional from freeze candidate to authority
   (cost/scenario contract §9 offers it as a candidate; only Blue can freeze it).
8. Whether `RESEARCH_ONE_WAY_COST_BPS` rises or the desk's `max_participation`
   falls, to close defect ECON-001. Raising the research cost re-rates already
   recorded lane evidence; lowering desk participation does not. That trade-off
   belongs to the project owner.
9. Reopening Route A or Workstream 16. Untouched.
10. Anything that would move `t0`, alter P0 governance, or authorise real capital.
