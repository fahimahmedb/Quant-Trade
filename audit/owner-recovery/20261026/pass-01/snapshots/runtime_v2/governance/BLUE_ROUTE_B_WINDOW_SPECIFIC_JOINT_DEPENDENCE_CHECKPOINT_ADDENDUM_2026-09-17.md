# BLUE ROUTE-B CHECKPOINT ADDENDUM — WINDOW-SPECIFIC JOINT DEPENDENCE — 2026-09-17

**Status:** CURRENT CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parents:** `BLUE_ROUTE_B_BETA_MULTIPLICITY_DEPENDENCE_CHECKPOINT_ADDENDUM_2026-09-17.md`, `D05A_D09_WINDOW_SPECIFIC_CALENDAR_SERIAL_DEPENDENCE_CONTRACT_2026-09-17.md`

This addendum controls where more recent/specific than prior liquidity/breach checkpoints.

## 1. New controlling artifact

Add:

`governance/D05A_D09_WINDOW_SPECIFIC_CALENDAR_SERIAL_DEPENDENCE_CONTRACT_2026-09-17.md`.

## 2. Joint-dependence state

Current state is now:

`BREACH_JOINT_DEPENDENCE_CONTRACT = STRUCTURALLY_CLOSED / NUMERICAL_METHOD_NOT_YET_CONSUMABLE`.

The unresolved remainder is no longer whether common-session, serial-overlap and corporate dependence matter. They all matter and must be represented.

Still open are the exact numerical/mathematical implementation of the joint construction and its UCB/capacity consequences.

## 3. Dependence is window-specific

For every frozen candidate `W`, breach uncertainty and capacity must be evaluated under a `W`-specific dependence rule.

Rolling ADV creates a raw-data influence span:

`INFLUENCE_SPAN(W,t) = [t-W+1, ..., t+1]`

with structural minimum horizon:

`H_OVERLAP(W) = W + 1 regular sessions`.

`W+1` is not asserted to be the complete dependence horizon. Common market/regime persistence can extend dependence beyond that span.

Longer windows may not inherit shorter-window precision or block length by convenience.

## 4. Calendar/session dependence is a first-class axis

Common market liquidity shocks can synchronize breaches across otherwise unrelated corporate groups.

Therefore:

- security-date pair count is not authority-bearing capacity;
- row-level independence is forbidden;
- if calendar blocks are used, the full eligible cross-section for each session/block is kept synchronized;
- distinct-date/calendar information is a required capacity dimension.

The protocol does not claim `N_eff = number_of_dates`; it forbids multiplying common-shock information merely by adding more same-date securities.

## 5. Corporate dependence remains the second axis

`CALIBRATION_DEPENDENCE_GROUP_ID` remains active.

The authority-bearing dependence structure is multi-axis:

`CALENDAR_SERIAL_AXIS x CORPORATE_DEPENDENCE_AXIS`.

A calendar-only or corporate-only method is insufficient unless a separate theorem/conditioning argument establishes otherwise.

## 6. Window-specific serial rule

Before results, freeze a deterministic rule:

`H_SERIAL(W)`

for every candidate window.

Required properties:

- respects at least the structural rolling overlap;
- is nondecreasing in `W` absent contrary proof;
- incorporates additional market/regime persistence under a frozen rule;
- cannot be shortened because longer dependence makes calibration underpowered or changes `W*`.

No specific closed form is yet authorized.

If no defensible rule can be frozen:

`BREACH_SERIAL_DEPENDENCE_RULE_UNRESOLVED`.

## 7. Uniform precision must hold for every candidate window

The familywise authority target remains simultaneous over:

`M = 2 * |W_SET|`

for the two lambda endpoints.

But precision/capacity are now window-specific:

`CAPACITY_AUTH(W)`

or `N_EFF_AUTH(W)` only where a scalar effective sample size is mathematically justified.

Selector authority requires all predeclared windows to satisfy the frozen precision design.

If any candidate is underpowered under its own dependence structure:

`LIQUIDITY_BREACH_CALIBRATION_UNDERPOWERED`.

That window cannot be removed after capacity/results are visible.

## 8. UCB rule remains controlling

For each candidate and endpoint:

`UCB_W(x) <= BETA_LIQ_MAX`

is required for pass authority.

`UCB_W(x)` must be computed under the `W`-specific joint-dependence construction.

Point estimates alone remain non-authoritative.

## 9. Current immediate blockers

Still open before any external breach calibration:

- numerical `P_MAX_REF` and `P_TARGET_REF`;
- numerical `BETA_LIQ_MAX`;
- small exact `W_SET` with distinct measurement-scale rationale;
- numerical `TAU_BETA` / `ALPHA_BETA`;
- exact `H_SERIAL(W)` rule;
- exact synchronized-calendar / corporate multi-axis bootstrap or alternative concentration construction;
- exact simultaneous one-sided UCB implementation;
- source/provider / daily-notional route / calibration-domain / date-sampling rules;
- final capacity calculation under the frozen external corpus.

Route-B final-protocol firewall remains unsatisfied.

No D05 ceiling visibility, numerical breach calibration or Form-4 outcome access is authorized.
