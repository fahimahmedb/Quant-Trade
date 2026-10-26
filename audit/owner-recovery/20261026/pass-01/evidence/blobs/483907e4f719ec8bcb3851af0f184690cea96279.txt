# OWNER — WEATHER V4 PHASE-GATE A1 DECISION — 2026-10-04

Date: 2026-10-04  
Author: PROJECT_OWNER  
Artifact type: OWNER_PHASE_GATE_DECISION

## 1. Authority

BLUE_PHASE_GATE_DECISION_SUPPORT_SHA =  
d669e603b87ac95c85c80861646de859df1b8819

ASTRA_PRE_OP_AUDIT_SHA =  
926741e7a67cb80bccde0ff428f2837bb200cf19

AUDITED_STRUCTURAL_PRE_OP_CONTRACT_SHA =  
de74c887b5dec9e4bd6f851c3571e69191015f43

OWNER_OD04_OD12_STRUCTURAL_DECISION_SHA =  
9391ce7a3f66cfc5bff2c745ca2dbb1072bba954

OWNER_OD01_OD03_DECISION_SHA =  
377af70116f24f486feac7b4da5d2873107822a2

This decision ratifies only the exact bounded phase-gate scope below. It does not amend prior economic decisions, the structural pre-operational contract, or Astra's audit qualifications.

## 2. Owner selection

OPTION_A =  
DOCUMENTATION / SYNTHETIC-FIXTURE-ONLY FEASIBILITY

OPTION_B =  
NOT_AUTHORIZED_YET

OPTION_C =  
DECLINED_AS_CURRENT_PATH

The selected Option A is split into two distinct scopes.

A1_DOCUMENTATION_SCOPE =  
AUTHORIZED

A2_SYNTHETIC_FIXTURE_TESTING_SCOPE =  
CONDITIONALLY_AUTHORIZABLE_ONLY_AFTER_PREREQUISITES_ARE_VERIFIED

PHASE_AUTHORIZATION =  
A1_ONLY_AT_INITIAL_GATE

A2_EXECUTION =  
BLOCKED_PENDING_PREREQUISITE_ATTESTATION

## 3. A1 — exact authorized scope

A1 may perform only documentation and specification work needed to prepare a safe later feasibility phase.

A1_ALLOWED_ACTS:

- manifest definition;
- role and access specification;
- schema/interface documentation;
- fixture admissibility policy;
- logging specification;
- incident and STOP rule specification;
- provenance specification;
- resource/time-bound specification;
- documentation of prerequisites for any later A2 or B decision;
- documentation-only consistency checks against already-authorized governance artifacts.

A1_PROHIBITED_ACTS:

- access real observational data;
- access real market data;
- access real weather data;
- access efficacy-revealing technical metadata;
- query real operational endpoints;
- use operational credentials;
- create economic evidence;
- rank edges, families, cities, stations, models or sources;
- measure availability, cadence, timing, latency, gaps or delivery behavior;
- compare source or market responses;
- create or inspect actual synthetic fixtures;
- implement collectors;
- deploy collectors;
- implement a new harness;
- implement a new vault;
- implement a new isolation layer;
- implement new access-control mechanisms;
- modify runtime infrastructure;
- use Builder;
- declare DATA_T0;
- declare EXPERIMENT_T0;
- unblind validation data;
- backtest;
- measure PnL;
- paper trade;
- live trade;
- use real capital.

A1_REAL_DATA_ACCESS =  
NONE

A1_REAL_METADATA_ACCESS =  
NONE

A1_EXTERNAL_ENDPOINT_ACCESS =  
NONE

A1_CREDENTIAL_USE =  
NONE

A1_FIXTURES_CREATED =  
NONE

A1_BUILDER_USE =  
PROHIBITED

A1_OPERATIONAL_SOURCE_SELECTION =  
NONE

A1 may propose exact future manifests, roles, limits and control requirements. Such proposals do not themselves activate A2, Option B, Builder, capture, data access, or economic validation.

## 4. A1 output requirements

A1 must produce documentation sufficient for owner review of later prerequisites, including:

- proposed exact PHASE_INPUT_MANIFEST schema and candidate populated documentary entries only where the source is already-authorized governance/documentation material;
- proposed exact PHASE_OUTPUT_MANIFEST schema;
- abstract role/capability matrix;
- fixture-admissibility and provenance policy;
- explicit documentation of whether an already-existing approved offline harness can be resolved from current authorized repository/governance evidence without operational probing;
- if such a harness cannot be resolved exactly, record UNKNOWN / NOT_ATTESTED and STOP;
- prerequisites that would have to be satisfied before A2 could be considered;
- prerequisites that would have to be satisfied before Option B could be considered;
- resource/time-bound fields requiring later owner choice;
- logging requirements;
- STOP rules;
- incident and quarantine rules;
- explicit list of any need for separate Builder authorization.

A1 must not convert UNKNOWN into an inferred YES.

A1 must not invent:
- a harness;
- actors;
- credentials;
- endpoint availability;
- source availability;
- resource ceilings;
- durations;
- budgets;
- storage/compute quotas;
- operational permissions.

Where exact owner values are absent:

OWNER_DECISION_REQUIRED

## 5. A2 — condition suspensive only

A2 is NOT authorized by this artifact.

A2 may be considered only after a separate prerequisite attestation establishes, from authorized evidence, that an already-existing explicitly approved offline test harness and required controls exist and satisfy the exact owner scope.

A2_PREREQUISITES_INCLUDE:

- harness identity and version resolved exactly;
- harness approval authority resolved exactly;
- permitted fixture-generation path specified;
- fixture provenance firewall specified;
- allowed inputs and prohibited inputs frozen;
- allowed outputs and quarantined outputs frozen;
- reader roles and release roles frozen;
- logging requirements frozen;
- incident/STOP rules frozen;
- resource/time bounds ratified as required;
- no hidden requirement for new Builder work.

If any required harness, vault, isolation layer, access-control mechanism, collector, runtime component or other control must be constructed:

STOP =  
SEPARATE_BUILDER_AUTHORIZATION_REQUIRED

No assumption may be made that an approved harness currently exists.

A2_EXECUTION_AUTHORIZED =  
FALSE

A2_FIXTURE_GENERATION_AUTHORIZED =  
FALSE

A2_FIXTURE_TESTING_AUTHORIZED =  
FALSE

## 6. Option B

OPTION_B_AUTHORIZED =  
FALSE

OPTION_B_DESIGN_MAY_REMAIN_DOCUMENTED =  
TRUE

OPTION_B_DESIGN != OPTION_B_EXECUTION

No real technical-access feasibility is authorized.

No endpoint, source, station, model, city, cadence, market universe, credential or technical request is selected by this decision.

Any future Option B requires a separate explicit owner phase-gate decision after applicable controls and prerequisites are resolved.

## 7. Option C

OPTION_C =  
DECLINED_AS_CURRENT_PATH

This does not erase Option C from future governance. It means only that the owner currently chooses bounded A1 documentation work rather than deliberate full deferral.

## 8. Synthetic fixture qualification

SYNTHETIC_LABEL_ALONE_ESTABLISHES_SAFETY =  
FALSE

A1 may define fixture policy only.

A1 may not generate, inspect, approve or test an actual fixture.

Any future fixture may be treated as NON_ECONOMIC_SYNTHETIC only if its construction does not encode, calibrate from or disclose real efficacy-revealing information, including:

- edge prevalence;
- signal magnitude;
- profitable-opportunity frequency;
- market response;
- candidate/family ranking;
- favored city/station/model/source;
- profitability-related latency;
- PnL;
- performance distributions.

Unknown fixture provenance fails closed.

## 9. Fail-closed interpretation

THE_CONTRACT_REQUIRES_FAIL_CLOSED_BEHAVIOR

TECHNICAL_CONTROL_IMPLEMENTATION_ESTABLISHED =  
FALSE

TECHNICAL_CONTROL_EFFECTIVENESS_VERIFIED =  
FALSE

A1 is authorized to specify controls, not to claim they are implemented or effective.

If A1 discovers that its own documentary task cannot continue without prohibited access, fixture generation, operational endpoint calls, credentials, Builder work or new control implementation:

A1_STOP =  
REQUIRED

NEXT_REQUIRED_AUTHORITY =  
SEPARATE_OWNER_DECISION

## 10. Unresolved register and resource discipline

DECLARED_UNRESOLVED_FIELD_COUNT =  
41

EXHAUSTIVENESS_CERTIFIED =  
FALSE

No automatic 42nd canonical unresolved field is created.

Stage-1 input/output/metric manifest work is treated as an operational phase-gate specification linked primarily to:

EXACT_NON_ECONOMIC_FEASIBILITY_SCOPE

RELEASE_PERMISSIONS

Numerical resource and time ceilings remain owner decisions where needed. A1 may specify the fields and decision requirements but must not invent values.

A1_DOCUMENTATION_WORK_DOES_NOT_AUTHORIZE_OPERATIONAL_RESOURCE_USE =  
TRUE

## 11. Hard governance state

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

UNBLIND_AUTHORIZED =  
FALSE

ASTRA_PASS != PHASE_AUTHORIZATION

BLUE_DECISION_SUPPORT != PHASE_AUTHORIZATION

THIS_OWNER_ARTIFACT_AUTHORIZES =  
A1_DOCUMENTATION_SCOPE_ONLY

## 12. Next safe action

NEXT_SAFE_ACTION =  
BLUE_A1_DOCUMENTATION_EXECUTION_ONLY

Blue may execute the authorized A1 documentation scope and produce the exact documentary outputs required above.

Blue must STOP rather than cross into A2, Option B, Builder, fixture creation, real-data access, operational endpoint access, capture, experimentation or economic validation.

After A1 completion, the owner must review the resulting artifact before any further authority transition.
