# BLUE ROUTE-B CHECKPOINT AMENDMENT — NOTIONAL ADV CAPACITY GATE — 2026-09-17

**Status:** CURRENT CHECKPOINT AMENDMENT  
**Authority:** Blue Team / Mission Control  
**Parent:** `BLUE_D05_D09_ROUTE_B_LIQUIDITY_SUPPORT_CHECKPOINT_AMENDMENT_2026-09-17.md`

This amendment controls where more recent/specific than its parent.

## 1. New controlling artifact

Add:

`governance/D05A_D09_LIQUIDITY_METRIC_AND_LOOKBACK_STABILITY_CONTRACT_2026-09-17.md`.

## 2. Gate purpose

The claim-defining liquidity gate is now frozen as a **capacity eligibility** gate only.

Opening spread/depth/auction/slippage/impact quality is not a second support dimension. Those effects remain in the separately governed `K_forward` / `M_economic` economic-cost path.

Therefore a capacity-eligible but expensive-to-execute event remains in scientific support and carries its governed cost rather than being retroactively excluded.

Current state:

`LIQUIDITY_GATE_PURPOSE = CLOSED / CAPACITY_ELIGIBILITY_ONLY`.

## 3. Metric coordinate

The claim-defining liquidity metric family is:

`ADV_NOTIONAL = average daily notional traded value`.

Participation is expressed in the same capital coordinate:

`PARTICIPATION(theta) = INTENDED_ORDER_NOTIONAL(theta) / ADV_NOTIONAL(theta)`.

Raw share-volume ADV is not the current-lineage claim-defining capacity coordinate.

The exact daily traded-notional construction remains open and must bind a PIT source-provided field or a frozen PIT price × share-volume construction with adjustment/corporate-action semantics.

Current state:

`LIQUIDITY_METRIC_FAMILY = CLOSED / NOTIONAL_ADV`

`DAILY_TRADED_NOTIONAL_CONVENTION = OPEN / NOT_YET_CONSUMABLE`.

## 4. Lookback-selection form

The earlier measurement-property rule is narrowed to a relative estimator-stability / precision target.

The current-lineage selection form is:

`W* = shortest predeclared candidate window W such that RELATIVE_ADV_ERROR(W) <= epsilon_ADV`.

The candidate-window set, exact external stability functional and numerical `epsilon_ADV` must be frozen before inspecting their numerical calibration results.

Calibration must be independent of Form-4 target retention, D05 values, crossing counts, `Q(theta)`, BEEE/MEUE and outcomes.

This rule intentionally avoids choosing an indefinitely long window merely to minimize variance; the shortest passing window preserves recency subject to the required measurement stability.

Current state:

`LOOKBACK_SELECTION_FORM = CLOSED / SHORTEST_WINDOW_MEETING_PREDECLARED_RELATIVE_STABILITY`

while the numerical candidates, functional, threshold and final window remain open.

## 5. Firewall / remaining blockers

`ROUTE_B_FINAL_PROTOCOL_FIREWALL_SATISFIED = FALSE` remains unchanged.

Liquidity-side blockers now reduce to:

- exact daily traded-notional PIT convention;
- predeclared candidate-window set;
- exact external relative-stability functional;
- numerical `epsilon_ADV`;
- final lookback length selected mechanically from that rule;
- minimum valid observations / insufficient-history treatment;
- missing/non-trading session and corporate-action semantics;
- source/provider/version/PIT semantics;
- numerical ADV eligibility threshold / permitted participation functional;
- concrete `A_CONSTRUCTOR` binding the resulting rule;
- D19 mechanics for unresolved final deployment support where required.

No numerical source search, D05 ceiling visibility or outcome access is authorized by this amendment.
