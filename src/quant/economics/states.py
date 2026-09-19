"""Every state string the economic engine is allowed to emit.

One module holds them so that a state cannot be invented at a call site.  The
governance artifacts name these states; code that returns a string not listed
here is returning something no decision authority recognises.

Sources:

* ``governance/D09_ECONOMIC_CORE_EC1_ALLOCATION_WEIGHTED_EFFECT.md`` (frozen)
* ``governance/D09_ROUTE_B_COMMON_CORE_REMAINDER_2026-09-17.md``
* ``governance/D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md`` (frozen role split)
* ``governance/D09_ROUTE_B_M_ECONOMIC_UNCERTAINTY_ENVELOPE_2026-09-17.md``
* ``governance/D09_ROUTE_B_COST_PARAMETER_SOURCE_AND_JOINT_SCENARIO_CONTRACT_2026-09-17.md``
"""

from __future__ import annotations


# --- delta coordinate compatibility gate (remainder contract, object A) -------

DELTA_COORDINATE_COMPATIBLE = "DELTA_COORDINATE_COMPATIBLE"
DELTA_COORDINATE_MISMATCH = "DELTA_COORDINATE_MISMATCH"
DELTA_COORDINATE_UNRESOLVED = "DELTA_COORDINATE_UNRESOLVED"

DELTA_COORDINATE_STATES = (DELTA_COORDINATE_COMPATIBLE, DELTA_COORDINATE_MISMATCH,
                           DELTA_COORDINATE_UNRESOLVED)


# --- BEEE root semantics (EC1 section 8) -------------------------------------

BEEE_UNIQUE_ROOT = "BEEE_UNIQUE_ROOT"
BEEE_NO_ECONOMIC_ROOT = "BEEE_NO_ECONOMIC_ROOT"
BEEE_NONUNIQUE_ROOT = "BEEE_NONUNIQUE_ROOT"
BEEE_NONMONOTONE_MAPPING = "BEEE_NONMONOTONE_MAPPING"

BEEE_STATES = (BEEE_UNIQUE_ROOT, BEEE_NO_ECONOMIC_ROOT, BEEE_NONUNIQUE_ROOT,
               BEEE_NONMONOTONE_MAPPING)


# --- expected-cost and margin failure states ---------------------------------

K_FORWARD_PARAMETER_UNRESOLVED = "K_FORWARD_PARAMETER_UNRESOLVED"
M_ECONOMIC_ENVELOPE_UNRESOLVED = "M_ECONOMIC_ENVELOPE_UNRESOLVED"
M_ECONOMIC_MAPPING_UNRESOLVED = "M_ECONOMIC_MAPPING_UNRESOLVED"
JOINT_COST_SCENARIO_UNRESOLVED = "JOINT_COST_SCENARIO_UNRESOLVED"
PARAMETER_UNRESOLVED = "PARAMETER_UNRESOLVED"
SOURCE_SET_NONCOMMENSURABLE = "SOURCE_SET_NONCOMMENSURABLE"
INVALID_MEUE_RECIPE = "INVALID_MEUE_RECIPE"
FRICTION_MARGIN_DOUBLE_COUNT = "FRICTION_MARGIN_DOUBLE_COUNT"
THETA_UNRESOLVED = "THETA_UNRESOLVED"


# --- recipe consumability ----------------------------------------------------

#: The recipe is structurally complete *and* every parameter it needs carries
#: authority. Only this state may produce a consumable numerical MEUE.
RECIPE_CONSUMABLE = "RECIPE_CONSUMABLE"
#: Structurally complete but at least one input is provisional or the margin
#: functional is still a freeze candidate. Numbers may be produced but are
#: explicitly non-authoritative.
RECIPE_PROVISIONAL = "RECIPE_PROVISIONAL"
#: Structurally incomplete or self-contradictory. No numbers at all.
RECIPE_INVALID = "RECIPE_INVALID"

RECIPE_STATES = (RECIPE_CONSUMABLE, RECIPE_PROVISIONAL, RECIPE_INVALID)


# --- economic verdicts (mission section 7 chain) -----------------------------

CONTINUE = "CONTINUE"
NO_TRADE = "NO_TRADE"
KILL = "KILL"

VERDICTS = (CONTINUE, NO_TRADE, KILL)


# --- provenance of an economic parameter -------------------------------------

#: Estimated from evidence admitted by that parameter's own frozen source
#: contract. The only class that can make a recipe consumable.
PROVENANCE_CALIBRATED = "CALIBRATED_UNDER_PARAMETER_SOURCE_CONTRACT"
#: A number that exists in V1 production/shadow code. The friction partition
#: section 9 is explicit that this is *not* calibration authority.
PROVENANCE_V1_ASSUMED = "ASSUMED_V1_EXECUTION_PARAMETER"
#: An engineering plausibility value with explicit governance status, admitted
#: by the envelope contract section 3 only when stronger evidence is absent.
PROVENANCE_ENGINEERING_BOUND = "ENGINEERING_PLAUSIBILITY_BOUND"
#: No admissible source passed.
PROVENANCE_UNAVAILABLE = "UNAVAILABLE"

PROVENANCE_CLASSES = (PROVENANCE_CALIBRATED, PROVENANCE_V1_ASSUMED,
                      PROVENANCE_ENGINEERING_BOUND, PROVENANCE_UNAVAILABLE)

#: Provenance classes that do not by themselves carry calibration authority and
#: therefore *must* appear in the joint model-risk scenario set.
PROVENANCE_REQUIRING_MODEL_RISK = (PROVENANCE_V1_ASSUMED, PROVENANCE_ENGINEERING_BOUND)


# --- estimator kind for an expected-cost component ---------------------------

#: The only estimator kind K_forward may use: a central expectation.
ESTIMATOR_CENTRAL_EXPECTATION = "CENTRAL_EXPECTATION"
#: Forbidden inside K_forward by NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD.
ESTIMATOR_UPPER_QUANTILE = "UPPER_QUANTILE"
ESTIMATOR_WORST_CASE = "WORST_CASE"

ESTIMATOR_KINDS = (ESTIMATOR_CENTRAL_EXPECTATION, ESTIMATOR_UPPER_QUANTILE,
                   ESTIMATOR_WORST_CASE)


# --- economic home of a named risk class (anti double count) -----------------

HOME_K_FORWARD = "K_FORWARD"
HOME_M_ECONOMIC = "M_ECONOMIC"

ECONOMIC_HOMES = (HOME_K_FORWARD, HOME_M_ECONOMIC)
