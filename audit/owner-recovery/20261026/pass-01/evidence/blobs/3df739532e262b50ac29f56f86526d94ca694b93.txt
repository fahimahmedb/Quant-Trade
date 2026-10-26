# OWNER OD04–OD12 STRUCTURAL DECISION

Date: 2026-10-04  
Author: PROJECT_OWNER  
Artifact type: OWNER_DECISION  
OWNER_DECISION_SCOPE = OD04_OD12_STRUCTURAL_ARCHITECTURE_ONLY

## Authority chain

OWNER_OD01_OD03_DECISION_BRANCH =  
owner/weather-v4-od01-od03-decision-2026-10-04

OWNER_OD01_OD03_DECISION_SHA =  
377af70116f24f486feac7b4da5d2873107822a2

BLUE_OD04_OD12_DECISION_SUPPORT_BRANCH =  
blue/weather-v4-od04-od12-decision-support-2026-10-04

BLUE_OD04_OD12_DECISION_SUPPORT_SHA =  
ce9ee937d25eac0d44cfa345924c7630726f995f

NO_NEW_OUTCOMES_ACCESSED =  
TRUE

NO_NEW_DATA_ACCESSED =  
TRUE

ECONOMIC_AUTHORITY =  
0

This artifact records owner structural decisions only. It does not rewrite or replace the prior Owner OD01–OD03 Decision or the Blue OD04–OD12 Decision Support artifact.

## OD04 — Dependence and inference

OD04 = STRUCTURALLY_RATIFIED

PRIMARY_INFERENCE_ARCHITECTURE =  
CONSERVATIVE_CALENDAR_SYSTEM_BLOCKING

IF_DEPENDENCE_ASSUMPTIONS_CANNOT_BE_JUSTIFIED =  
PARTIAL_IDENTIFICATION_OR_INCONCLUSIVE

STRUCTURED_JOINT_MODEL_AS_CONFIRMATORY_ESCAPE_HATCH =  
NOT_AUTHORIZED

DEPENDENCE_UNIT =  
UNRESOLVED

BLOCK_DEFINITION =  
UNRESOLVED

WEATHER_SYSTEM_DEFINITION =  
UNRESOLVED

The structured joint-model route may not be introduced merely because the conservative blocking architecture lacks power or precision.

## OD05 — Multiplicity

OD05 = STRUCTURALLY_RATIFIED

CONFIRMATORY_MULTIPLICITY_CONTROL =  
FINITE_BATCH_FWER

CONFIRMATORY_CLAIM_FAMILY =  
UNRESOLVED

BATCH_COMPOSITION =  
UNRESOLVED

ERROR_BUDGET_ALLOCATION =  
UNRESOLVED

FWER_ALPHA =  
UNRESOLVED

EXPLORATORY_FDR =  
ALLOWED_ONLY_WITH_ECONOMIC_AUTHORITY_0

EXPLORATORY_DISCOVERY_REQUIRES_FRESH_CONFIRMATION =  
TRUE

ERROR_BUDGET_RESET_BY_CHILD_ID =  
FALSE

FAILED_TEST_REFUNDS_ERROR_BUDGET =  
FALSE_UNLESS_PREDECLARED_VALID_RULE

Exploratory FDR results cannot directly receive economic authority. A new child identifier does not reset multiplicity history.

## OD06 — Information and duration

OD06 = STRUCTURALLY_RATIFIED

VALIDATION_ARCHITECTURE =  
STAGED_FEASIBILITY_THEN_FRESH_ECONOMIC_EPOCH

STAGE_1 =  
NON_ECONOMIC_OPERATIONAL_FEASIBILITY

STAGE_1_OUTCOME_ACCESS =  
PROHIBITED

STAGE_1_EDGE_EFFICACY_INFERENCE =  
PROHIBITED

STAGE_1_SELECTION_OF_FAVORED_FAMILIES =  
PROHIBITED

STAGE_1_MAY_MEASURE:

- technical coverage;
- timestamp availability;
- missing and gap mechanics;
- schema completeness;
- custody integrity;
- contractual accessibility.

STAGE_1_MUST_NOT_MEASURE:

- edge prevalence;
- profitable opportunity frequency;
- signal magnitude;
- market response;
- profitability-related historical latency advantage;
- PnL;
- candidate ranking;
- outcome labels used to evaluate an edge.

STAGE_2 =  
FRESH_LOCKED_ECONOMIC_VALIDATION_SURFACE

MINIMUM_INFORMATION =  
UNRESOLVED

MAXIMUM_DURATION =  
UNRESOLVED

The feasibility stage may reduce operational uncertainty only. It may not be used to infer edge efficacy, rank families, or tune the later validation duration from economic outcomes.

## OD07 — Stopping and reopening

OD07 = STRUCTURALLY_RATIFIED

PRIMARY_ENDPOINT_POLICY =  
FIXED_PRIMARY_ENDPOINT

ALLOWED_TERMINAL_STATES:

- PASS;
- FAIL;
- INCONCLUSIVE;
- NOT_VALIDATABLE.

ECONOMIC_PEEK_FOR_EXTENSION =  
NOT_AUTHORIZED

ECONOMIC_PEEK_FOR_RESCUE =  
NOT_AUTHORIZED

SAFETY_OR_DATA_INTEGRITY_SUSPENSION =  
ALLOWED_ONLY_WITH_PREDEFINED_RULES

REOPENING_RULE =  
UNRESOLVED

SECONDARY_HORIZONS_MAY_RESCUE_PRIMARY_CONFIRMATION =  
FALSE

SECONDARY_HORIZONS_MAY_CHANGE_PRIMARY_STOPPING_OR_CONTINUATION =  
FALSE

ANY_CHILD_HYPOTHESIS_TRIGGERED_BY_SECONDARY_RESULTS =  
NEW_VALIDATION_REQUIRED

## OD08 — Prospective capture architecture

OD08 = STRUCTURALLY_RATIFIED

PREFERRED_ARCHITECTURE =  
SEPARATE_DISCOVERY_AND_SEALED_VALIDATION_STREAMS

DISCOVERY_STREAM =  
MAY_SUPPORT_DEVELOPMENT_AND_EXPLORATORY_ANALYSIS_ONLY

SEALED_VALIDATION_STREAM =  
INACCESSIBLE_UNTIL_EXACT_LOCK_AND_UNBLIND_CONDITIONS_ARE_SATISFIED

STREAM_SEPARATION =  
MUST_BE_BASED_ON_EXPOSURE_CUSTODY_AND_CORRELATION_RULES_NOT_MERELY_SEPARATE_FILES_FOLDERS_STATIONS_OR_VENDORS

CAPTURE_AUTHORIZATION =  
NONE

No exact station, endpoint, model, polling cadence, market universe or operational source priority is authorized by this decision.

## OD09 — Custody, access and unblinding

OD09 = STRUCTURALLY_RATIFIED

PREFERRED_CUSTODY_ARCHITECTURE =  
TECHNICALLY_ISOLATED_VAULT_WITH_INDEPENDENT_APPROVAL

CAPTURE_IDENTITY != RESEARCH_IDENTITY

RESEARCH_CAN_DECRYPT_VALIDATION =  
FALSE

ACCESS_LOG =  
IMMUTABLE

UNBLIND =  
EXPLICIT_APPROVAL_ONLY

EXCEPTIONAL_ACCESS =  
MUST_RECLASSIFY_THE_AFFECTED_SURFACE_ACCORDING_TO_THE_EXPOSURE_TAXONOMY

HUMAN_INDEPENDENT_CUSTODIAN =  
NOT_REQUIRED_AT_THIS_STAGE

CURRENT_PHASE_AUTHORIZATION =  
NONE

CAPTURED != CLEAN  
SEALED != CONFIRMATORY_CLEAN

## OD10 — Execution

OD10 = STRUCTURALLY_RATIFIED

INITIAL_CONFIRMATORY_EXECUTION =  
CONSERVATIVE_TAKER_ONLY

MAKER_ECONOMIC_AUTHORITY =  
0

MAKER_VALIDATION =  
SEPARATE_FUTURE_CHILD_HYPOTHESIS_REQUIRED

QUOTE_TOUCH != FILL  
FILL != QUEUE_POSITION_PROOF  
MIDPOINT != EXECUTABLE_PRICE

ACTUAL_30D_FORCED_LIQUIDATION =  
NO

BOOK_CONTINUES_AFTER_MEASUREMENT =  
YES

30D_TERMINAL_VALUATION_PRINCIPLE =  
CONSERVATIVE_EXECUTABLE_LIQUIDATION_VALUE

30D_TERMINAL_VALUATION_RULE =  
UNRESOLVED

DOUBLE_COUNTING_OF_COSTS =  
MUST_BE_PREVENTED

The exact terminal valuation rule remains unresolved pending definitions for depth, latency, partial fills, costs, difficult-to-unwind positions, contracts near settlement and non-atomic legs.

## OD11 — Promotion, evidence and complexity

OD11 = STRUCTURALLY_RATIFIED

MINIMUM_EVIDENCE_FOR_SHADOW_AUTHORITY_CONSIDERATION =  
H4_AND_H5

H4_PLUS_H5_AUTOMATICALLY_GRANTS_AUTHORITY =  
FALSE

H6_REQUIRED_FOR =  
STRONGER_TRANSPORTABILITY_OR_COMPOSITE_ROBUSTNESS_CLAIMS

INITIAL_POLICY_COMPLEXITY =  
FIXED_MINIMAL

CONTEXT_ROUTER =  
NOT_AUTHORIZED

LEARNED_INTERACTIONS =  
NOT_AUTHORIZED

COMPOSITE =  
REQUIRES_SEPARATE_VALIDATION

MULTI_MODEL_CONSENSUS != INDEPENDENT_EVIDENCE  
AGREEMENT_BETWEEN_AI_SYSTEMS != ECONOMIC_AUTHORITY

## OD12 — Resources and future phase authorization

OD12 = STRUCTURALLY_RATIFIED

PREFERRED_NEXT_PHASE_ARCHITECTURE =  
STAGED_NON_OUTCOME_OPERATIONAL_FEASIBILITY

CURRENT_PHASE_AUTHORIZATION =  
NONE

FUTURE_PHASE_AUTHORIZATION =  
REQUIRES_SEPARATE_EXPLICIT_OWNER_ARTIFACT_AFTER_STRUCTURAL_PRE_OP_CONTRACT_INTEGRATION_INDEPENDENT_ASTRA_PRE_OP_AUDIT_AND_SUCCESSFUL_RESOLUTION_OF_REQUIRED_DEPENDENCIES

ASTRA_PASS != PHASE_AUTHORIZATION

Astra may return:

PRE_OP_CONTRACT_AUDIT = PASS_FOR_OWNER_PHASE_GATE_CONSIDERATION

or

PRE_OP_CONTRACT_AUDIT = REPAIR_REQUIRED

An Astra PASS means only that the owner may consider authorizing a bounded non-economic feasibility phase. It never activates that phase automatically.

## Parameters and definitions that remain unresolved

The following remain explicitly unresolved and must not be completed by inference during structural integration:

- statistical selection rule;
- confirmatory claim family;
- batch composition;
- error-budget allocation;
- FWER alpha;
- dependence unit;
- block definition;
- weather-system definition;
- minimum information;
- maximum duration;
- start-state distribution;
- terminal valuation rule;
- cost allocation;
- execution envelope parameters;
- delta_min;
- P_MIN_ROLE and p_min if required;
- drawdown limit;
- tail measure;
- tail level;
- tail limit;
- worst-case limit;
- concentration limits;
- capacity minimum;
- execution-cost limit;
- exact custody actors, credentials and release permissions.

## Global status

OD01 =  
RATIFIED

OD02 =  
PARTIALLY_RATIFIED

OD03 =  
PARTIALLY_RATIFIED

OD04_OD12 =  
STRUCTURALLY_RATIFIED

NUMERICAL_PARAMETERS =  
UNRESOLVED

STATISTICAL_SELECTION_RULE =  
UNRESOLVED

FULL_VALIDATION_CONTRACT_COMPLETE =  
FALSE

CURRENT_CONTRACT_CLASS =  
STRUCTURAL_PRE_OPERATIONAL_CONTRACT_PENDING_INTEGRATION

READY_FOR_FINAL_VALIDATION_CONTRACT_AUDIT =  
FALSE

ECONOMIC_AUTHORITY =  
0

ECONOMIC_DECISION_WEIGHT =  
0

COMPOSITE_ECONOMIC_AUTHORITY =  
0

CAPTURE_AUTHORIZATION =  
NONE

REAL_CAPITAL_AUTHORIZED =  
FALSE

LIVE_TRADING_AUTHORIZED =  
FALSE

t0 =  
NOT_DECLARED

DATA_T0 =  
NOT_DECLARED

EXPERIMENT_T0 =  
NOT_DECLARED

BUILDER_AUTHORIZED =  
FALSE

OBSERVATION_AUTHORITY =  
UNCHANGED

## This artifact does not authorize

- data capture;
- operational capture design implementation;
- DATA_T0;
- EXPERIMENT_T0;
- E1–E5;
- Builder work;
- backtests;
- strategy validation;
- PnL measurement;
- edge ranking;
- paper trading;
- live trading;
- capital activity;
- economic weighting;
- composite activation;
- unblinding.

## Next authorized process step

Blue may integrate the ratified OD01–OD12 structural decisions into a new STRUCTURAL_PRE_OPERATIONAL_CONTRACT.

That contract must preserve every unresolved field explicitly and must not present itself as a final validation contract.

The next Astra mission, after that integration, must be limited to a PRE-OPERATIONAL CONTRACT AUDIT answering whether the structural contract is sufficiently controlled for the owner to consider a separately authorized bounded non-economic feasibility phase.

Neither Blue integration nor Astra PASS authorizes that feasibility phase.
