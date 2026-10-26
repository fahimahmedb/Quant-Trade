# D05-A / D09 LIQUIDITY IDENTITY AND LOOKBACK-SELECTION AMENDMENT — 2026-09-17

**Status:** CLOSED / FROZEN STRUCTURAL AMENDMENT — EXACT LOOKBACK LENGTH / PROVIDER / THRESHOLD STILL OPEN  
**Authority:** Blue Team / Mission Control  
**Parents:** `D05A_D09_LIQUIDITY_EDGAR_CUTOFF_SINGLE_EVALUATION_AMENDMENT_2026-09-17.md`, `D05A_LIQUIDITY_GATE_RESOLUTION_AND_D19_ROUTING_AMENDMENT_2026-09-17.md`, `D05A_UNIT_AND_CEILING_CONVERSION_CONTRACT.md`, `D09_ROUTE_B_LIQUIDITY_ELIGIBILITY_AND_FINITE_COST_SCENARIO_AMENDMENT_2026-09-17.md`

This amendment closes two remaining structural ambiguities before the liquidity parameter/source registry is instantiated: which PIT security/listing identity a final crossing uses for liquidity evaluation, and what may justify the ADV/liquidity lookback length.

It does not select a numerical lookback, provider, ADV threshold, cost coefficient, or inspect D05/Form-4 values.

## 1. Crossing liquidity reference fact

For a final crossing under frozen `G*`, let `F_crossing(G*)` be the frozen set of source facts required to establish that crossing.

The liquidity reference date is:

`CROSSING_LIQUIDITY_REFERENCE_DATE(G*) = max_{f in F_crossing(G*)} EDGAR_DATE(f)`.

The crossing remains an issuer-level scientific event keyed by `ISSUER_CIK`; this rule does not change formation identity or qualification semantics.

**Invariant:** `CROSSING_LIQUIDITY_REFERENCE_USES_LATEST_REQUIRED_EDGAR_DATE`.

## 2. Deployment security/listing identity is resolved at the crossing reference date

The security/listing identity used to evaluate the claim-defining liquidity gate must be the PIT identity valid for the frozen issuer/security mapping rule at:

`CROSSING_LIQUIDITY_REFERENCE_DATE(G*)`.

Conceptually:

`DEPLOYMENT_SECURITY_ID(crossing) = PIT_RESOLVE_SECURITY(ISSUER_CIK, CROSSING_LIQUIDITY_REFERENCE_DATE, frozen resolver contract)`.

This rule fixes **when** the downstream identity is resolved. It does not invent or replace the separately governed security resolver.

Consequences:

- an earlier filing's ticker/listing identity does not control merely because it appeared first;
- splits, ticker changes, relistings, share-class/listing transitions or other identity changes must be handled by the PIT resolver/reference lineage at the crossing reference date;
- no retroactive rewriting of issuer formation history occurs;
- if the resolver cannot produce the unique required deployment identity under the frozen rule, use `DEPLOYMENT_ELIGIBILITY_UNRESOLVED` / FM-08 rather than fall back to a stale earlier identity.

**Invariants**

- `DEPLOYMENT_SECURITY_IDENTITY_IS_PIT_AT_CROSSING_REFERENCE_DATE`
- `EARLIER_FILING_SECURITY_ID_DOES_NOT_OVERRIDE_FINAL_PIT_IDENTITY`
- `UNRESOLVED_FINAL_SECURITY_IDENTITY_ROUTES_FM08_NO_STALE_FALLBACK`

## 3. Daily liquidity cutoff follows the resolved deployment identity

Once the crossing deployment identity is resolved at the reference date, the daily liquidity snapshot continues to use:

`LIQUIDITY_CUTOFF_SESSION = last completed regular session strictly before CROSSING_LIQUIDITY_REFERENCE_DATE`.

The lookback is evaluated on the PIT listing/security lineage applicable to the deployment identity under the frozen source contract.

If a corporate action/listing transition prevents a coherent lookback under the source contract, the implementation must emit the frozen unresolved/failure state. It may not splice incompatible histories ad hoc merely to obtain an ADV value.

**Invariant:** `LIQUIDITY_LOOKBACK_REQUIRES_COHERENT_PIT_SECURITY_LINEAGE`.

## 4. Lookback length is claim-defining

The liquidity lookback length affects both:

- measurement stability/noise of the liquidity estimate; and
- which securities possess sufficient history to become deployment-eligible under the frozen policy.

It can therefore alter the support of `A_claim` and belongs in:

`LIQUIDITY_ELIGIBILITY_RULE_HASH`.

Changing the lookback length after confirmatory authority when it changes deployment support is `NEW_POLICY_VERSION` under EC1/D10-C semantics.

**Invariant:** `LIQUIDITY_LOOKBACK_LENGTH_IS_CLAIM_FINGERPRINTED`.

## 5. Allowed justification for lookback selection

The exact lookback length must be selected before D05 ceiling visibility and before inspecting target-population retention/inclusion statistics.

Its justification must target a predeclared measurement property, such as an independently justified stability/smoothing objective for the liquidity metric under the intended execution regime.

Permitted evidence may come only from a separately frozen source rule independent of Form-4 target-population inclusion/outcomes.

The following are not admissible selection criteria:

- number or percentage of Form-4 issuers/events retained by each candidate window;
- number of final crossings retained;
- D05 ceiling values;
- resulting `Q(theta)`;
- resulting BEEE/MEUE;
- final return outcomes.

**Invariants**

- `LOOKBACK_SELECTED_FOR_MEASUREMENT_PROPERTY_NOT_TARGET_INCLUSION`
- `TARGET_RETENTION_CANNOT_SELECT_LIQUIDITY_LOOKBACK`
- `MEUE_CANNOT_SELECT_LIQUIDITY_LOOKBACK`

## 6. Stability-versus-history tradeoff is predeclared, not optimized on target data

A longer lookback may improve smoothing/stability while increasing the chance that newly listed securities lack sufficient history. A shorter lookback may admit more recent listings while producing a noisier estimate.

This tradeoff is recognized ex ante.

It does not authorize optimization against observed Form-4 support.

The frozen rule must therefore separately declare:

1. the target measurement property used to choose the lookback;
2. the exact lookback length once selected;
3. the minimum valid-observation requirement;
4. the deterministic treatment of insufficient history.

If the frozen policy says insufficient history is ineligible, that is `DEPLOYMENT_INELIGIBLE_BY_FROZEN_RULE`.

If the required measurement should be available but cannot be resolved under the frozen source/PIT semantics, that is `DEPLOYMENT_ELIGIBILITY_UNRESOLVED` and routes FM-08 as already governed.

## 7. Source-contract consequence

The future liquidity source-class / provider contract must be able to support all of the following without target-data adaptation:

- PIT security/listing resolution at `CROSSING_LIQUIDITY_REFERENCE_DATE`;
- daily price/volume or other frozen liquidity fields through the last completed regular session strictly before that date;
- coherent historical lineage across authorized corporate-action/listing transitions;
- provenance/version semantics sufficient to reproduce the lookback;
- explicit missing-history and unresolved-identity states.

A broad-market liquidity source is not admissible merely because it contains a ticker on the filing date; applicability must be proven to the frozen deployment identity and liquidity metric semantics.

## 8. D05-A / post-G* placement

D05-A may compute source-unit/security-date liquidity snapshots whose identity and cutoff are D07-independent.

However, final crossing deployment support still follows `G*`, because the crossing composition determines the latest required EDGAR date and therefore the deployment identity/reference snapshot consumed by that crossing.

Thus:

`SOURCE_SNAPSHOT_D07_INDEPENDENT != FINAL_CROSSING_SUPPORT_D07_INDEPENDENT`.

No pre-D07 source snapshot count may be relabeled as a final deployable-crossing count.

## 9. Current state

Closed/frozen:

- crossing liquidity reference = latest required EDGAR date under final `G*`;
- deployment security/listing identity is PIT-resolved at that date;
- stale earlier security identity cannot be used as fallback;
- liquidity lookback length is claim-defining/fingerprinted;
- lookback selection may use measurement-stability justification but not target-population retention, D05 ceilings, `Q`, MEUE or outcomes.

Still open:

- exact liquidity metric;
- exact lookback length;
- exact minimum valid observations;
- exact insufficient-history policy;
- exact source class/provider/version semantics;
- exact numerical eligibility threshold/functional;
- numerical source values.

No numerical source search, D05 ceiling visibility or outcome access is authorized by this artifact.
