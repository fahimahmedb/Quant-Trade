# Quant-Trade — DELTA Research Pack V1 — Final Decision Matrix

Date: 2026-10-15
Status: OWNER REVIEW REQUIRED
Branch: `research/delta-research-pack-v1-20261015`
Base: `93534d9c365b52f2aa80c4277da1cac4e7338d31`

## Authority status

This file consolidates the four ratified DELTA research missions. It is a recommendation package only.

```text
BUILDER_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```

No recommendation below changes those flags.

## Reference verification

Verified repository anchors:

- `377af70116f24f486feac7b4da5d2873107822a2` — Owner OD01–OD03 decision; exact Owner North Star: `Long-run net real wealth growth after all real frictions.`
- `9391ce7a3f66cfc5bff2c745ca2dbb1072bba954` — Owner OD04–OD12 structural decision.
- `de74c887b5dec9e4bd6f851c3571e69191015f43` — structural pre-operational contract repair separating audit state from allowed dispositions.

Original OD branches remain pinned to the declared OD commits. Targeted branch/commit search did not locate a direct artifact explicitly superseding the canonical OD01–OD12 decisions. This is a targeted verification, not a claim that every later branch was semantically audited line by line.

## Decision matrix

| Question | Result | Evidence strength | Quant-Trade relevance | Decision |
|---|---|---:|---:|---|
| Preferred architecture | T2 | MODERATE | VERY HIGH | RECOMMEND FOR OWNER CONSIDERATION, NOT SELECTED |
| T1 Full Research OS | insufficient marginal evidence now | LOW/MODERATE | HIGH later | DEFER |
| T3 Event/Fundamental-first standalone | Event strong, Fundamental less proven | MODERATE | HIGH | DEFER AS STANDALONE |
| T4 Other/hybrid | no superior concrete challenger emerged | LOW | OPEN | UNKNOWN_WITH_REASON |
| P0 discovery engine | none required | STRONG LOGICAL / MODERATE EMPIRICAL | VERY HIGH | RETAIN NONE |
| First post-P0 discovery family | mechanism-first forced flows / institutional constraints | MODERATE/HIGH | HIGH | RETAIN RECOMMENDATION |
| Second post-P0 discovery family | Event/Document intelligence | MODERATE/HIGH | HIGH | RETAIN RECOMMENDATION |
| Edge archaeology | useful feeder/control, not proven standalone winner | MODERATE | HIGH | RETAIN AS FEEDER/CONTROL |
| Literature mining | useful feeder/control | MODERATE/HIGH | HIGH | RETAIN AS FEEDER/CONTROL |
| Open-ended LLM discovery | promising but experimental/adaptive-risk | LOW/MODERATE | HIGH later | DEFER STANDALONE |
| Microstructure/HFT | mechanisms real, access/latency costly | HIGH | LOW now | DEFER / HFT REJECT NEAR-TERM |
| Small-capital search spaces | flow/event/regulatory/capacity-limited niches | MODERATE | VERY HIGH | RETAIN |
| Evidence model | multidimensional vector + separate readiness | HIGH CONCEPTUAL | VERY HIGH | RETAIN P0 |
| E0–E7 | navigation summary only | MODERATE | MEDIUM | RETAIN INTERFACE ONLY |
| Generation model | immutable material generations + amendment log + DAG | HIGH | VERY HIGH | RETAIN P0 |
| Trial accounting | observed attempts exact; effective trials separate with unknown allowed | HIGH | VERY HIGH | RETAIN P0 |
| Prospective proof | frozen full contract; timing/integrity/authorization separated | HIGH | VERY HIGH | RETAIN P0 CAPABILITY |
| Real prospective collection | not authorized | CANONICAL | VERY HIGH | REJECT CURRENT PHASE |
| Learning telemetry | record from day one | MODERATE/HIGH | HIGH | RETAIN P0 |
| Meta-Research engine | premature | MODERATE | MEDIUM later | DEFER |
| Economic Reality Stub | early implementability without auto-KILL | HIGH | VERY HIGH | RETAIN P0 |
| Full portfolio engine | unnecessary for scientific P0 | HIGH | LATER | DEFER |
| Full Shadow Book | unnecessary for scientific P0 | HIGH | LATER | DEFER |
| Full execution optimizer | unnecessary for scientific P0 | HIGH | LATER | DEFER |
| CIO AI | no live evidence sufficient for authority | HIGH | LOW now | REJECT P0 |
| Autonomous capital | outside authority | CANONICAL | NONE current | REJECT P0 |

## Why T2 is recommended, but not selected

The DELTAs provide three converging observations:

1. A common evidence/trial core adds value to every discovery method and directly addresses Quant-Trade's observed `effective_trials = UNKNOWN` / evidence-chain weakness.
2. The best accessible discovery evidence is concentrated in a **small number** of materially different families, not enough to justify an immediate full autonomous federation.
3. Event/Document evidence is meaningful, but not strong enough to show that Event/Fundamental should replace quant/mechanism-first discovery as the entire system.

Therefore the current evidence best matches the preregistered T2 rule:

```text
common evidence core has value across methods
+
one/small number of specialized engines capture most accessible discovery value
+
additional engines have uncertain marginal contribution
```

This is a recommendation to the Owner, not an architectural selection.

## TRAJECTORY_RECOMMENDATION

```text
TRAJECTORY = T2_RECOMMENDED_FOR_OWNER_CONSIDERATION
DECISION_AUTHORITY = OWNER_ONLY
T1 = DEFER
T3 = DEFER_AS_STANDALONE
T4 = OPEN_IF_OWNER_IDENTIFIES_A_SUPERIOR_HYBRID
NO_DECISION = NOT_REQUIRED_BY_CURRENT_EVIDENCE_BUT_REMAINS_VALID_OWNER_OUTCOME
```

## P0_BOUNDARY_RECOMMENDATION

```text
P0 = MINIMUM_SCIENTIFIC_KERNEL

RETAIN:
- hypothesis identity
- immutable material generations
- amendment log
- ancestry DAG
- preregistration/freeze
- minimal PIT/provenance
- experiment/result immutability + reproducibility package
- evidence vector
- separate operational readiness
- research decision model
- observed-trial ledger
- effective-trial uncertainty model
- falsification scope
- decision map / decision divergence
- prospective contract ledger capability
- prospective integrity checks
- authorization field separated from integrity
- Economic Reality Stub
- learning telemetry

P0_DISCOVERY = NONE
```

## DISCOVERY_RECOMMENDATION — post-P0 only

```text
DISCOVERY_1 = MECHANISM_FIRST_FORCED_FLOW_INSTITUTIONAL_CONSTRAINTS
DISCOVERY_2 = EVENT_DOCUMENT_INTELLIGENCE
SUPPORT = EDGE_ARCHAEOLOGY + LITERATURE_MINING
```

No discovery module is authorized by this matrix.

## Small-capital map

### RETAINED_SEARCH_SPACES

```text
FORCED / PREDICTABLE INSTITUTIONAL FLOWS
EVENT / DOCUMENT / EARNINGS / GUIDANCE
REGULATORY / SETTLEMENT / MARKET-STRUCTURE CHANGES
CAPACITY-LIMITED EVENT-DRIVEN / RELATIVE-VALUE CASES
PUBLIC-DATA COMPLEXITY NICHES
```

### DEFERRED

```text
FUNDAMENTAL_LONG_SHORT_AUTOMATION
GENERIC_CROSS_MARKET
VOL_RISK_PREMIUM_AS_PRIMARY_ENGINE
HIGH_TURNOVER_STAT_ARB
FULL_ORDER_BOOK_MICROSTRUCTURE
GENERIC_CROSS_SECTIONAL_ML
EXPENSIVE_ALTERNATIVE_DATA
```

### REJECT NEAR-TERM

```text
ULTRA_LOW_LATENCY_HFT
COLOCATION/QUEUE-EDGE MARKET MAKING
GENERIC_MICROCAP_SHORT-ANOMALY MINING WITHOUT BORROW PROOF
```

## OPEN_UNKNOWNS

1. Exact effective-trial estimator by family/search process.
2. Exact numerical statistical/economic gates still reserved/unresolved under OD governance.
3. Whether the recommended post-P0 pair will outperform alternatives after identical prospective trial accounting.
4. Whether accessible forced-flow proxies preserve enough timing advantage after realistic implementation.
5. Whether Event/Document advantages survive after competition, timing, spread and capacity costs in Quant-Trade's actual universe.
6. Exact capital/data/access scenario for later economic optimization.
7. Exact implementation technology for P0; belongs in ADR/Build Spec after Owner trajectory decision.
8. Whether later Meta-Research demonstrably improves prequential research efficiency without becoming another overfit layer.

## OWNER_DECISIONS_REQUIRED

```text
ODR-DELTA-01
Accept / reject / return NO_DECISION on T2 recommendation.

ODR-DELTA-02
If trajectory is accepted, authorize ADR + Canonical Research Contract + P0 Build Specification drafting only.

ODR-DELTA-03
Do not authorize Builder by implication; Builder remains a separate later gate after Red Team/spec freeze.

ODR-DELTA-04
Any future historical data reacquisition, economic cohort run or prospective observation requires exact-scope authority under canonical governance.
```

## Governance compatibility

```text
GOVERNANCE_COMPATIBILITY = PASS
OD01_OD12 = PASS
STRUCTURAL_PRE_OP = PASS
EXISTING_INVARIANTS = PASS
```

No direct conflict was found between DELTA recommendations and the canonical governance anchors. Recommendations preserve unresolved fields as unresolved.

## DELTA mission termination

```text
DELTA_A_DECISION = COMPLETE
DELTA_B_DECISION = COMPLETE
DELTA_C_DECISION = COMPLETE
DELTA_D_DECISION = COMPLETE
FINAL_DECISION_MATRIX = COMPLETE

RATIFIED_DELTA_RESEARCH_MANDATE = TERMINATED
NEXT_SAFE_ACTION = OWNER_REVIEW_OF_DELTA_DECISION_MATRIX
```

The DELTA mandate may not self-extend into new research missions, ADR drafting, Builder work, prospective observation or economic experimentation.
