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


# --- capital/order eligibility tier (V2 consolidation) -----------------------
#
# ``verdict`` (CONTINUE/NO_TRADE/KILL) is the mechanical result of the chain and
# is deliberately unchanged by any of this: a RECIPE_PROVISIONAL evaluation may
# still mechanically CONTINUE, exactly as Wave 1 designed, so development can
# proceed before calibration. What was missing is a separate, honest answer to
# "does this CONTINUE mean anything a Desk/Book consumer may act on yet?" A
# recipe that is not RECIPE_CONSUMABLE, evidence that is not forward-confirmed,
# or a research/execution cost consistency check that was never run must never
# be silently read as capital or paper/shadow order eligibility.
#
# This is a representation of the current governance state, not an invented
# rule: it does not decide whether a provisional recipe *may* ever produce
# CONTINUE (that question is explicitly left to Blue, per Wave 1 red team
# item 8.1) and it grants nothing beyond "eligible for portfolio
# consideration" even at its highest tier — approval remains SIZE/RISK/BOOK's
# alone, never the economic engine's.

#: The verdict was not CONTINUE, or the eligibility question does not arise.
ORDER_ELIGIBILITY_NOT_ELIGIBLE = "NOT_ELIGIBLE"
#: CONTINUE, but at least one authority/verification gap remains: see the
#: verdict's ``capital_order_eligibility_reasons`` for exactly which.
ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY = "DEVELOPMENT_SIGNAL_ONLY"
#: CONTINUE, on a consumable recipe, forward-confirmed evidence, and a verified
#: research/execution cost consistency check. Eligible for SIZE/RISK/BOOK to
#: consider — never itself an approved order and never real-capital authority.
ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE = "PORTFOLIO_CONSIDERATION_ELIGIBLE"

ORDER_ELIGIBILITY_STATES = (ORDER_ELIGIBILITY_NOT_ELIGIBLE,
                            ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY,
                            ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)


# --- clustering-unit provenance for a scientific effect estimate -------------
#
# D07-O4 (overlap geometry) is the frozen object that defines the true
# clustering unit for inference (``handoff/CLAUDE_WAVE1_PROTOCOL_PROPOSALS_
# 2026-09-19.md`` s2 O4; Wave 1 red team item 3). It is unfrozen. An effect
# estimate that does not declare where its interval's clustering unit came
# from is silently assuming independence, which is exactly the "free
# t-statistic" failure mode the frozen inference module was built to prevent
# one layer down. This package does not own ``quant.science`` (a distinct
# writer domain per the Wave 1 Builder allocation proposal) and does not
# change its behaviour; it only refuses to treat an undeclared or
# O4-unresolved clustering unit as equivalent to a resolved one.

#: No declaration was made at all.
CLUSTERING_UNIT_UNDECLARED = "CLUSTERING_UNIT_PROVENANCE_UNDECLARED"
#: Declared, but the estimate used the naive "each observation its own
#: cluster" default because D07-O4 is not yet frozen — an assumption, not a
#: result.
CLUSTERING_UNIT_O4_UNRESOLVED = "O4_UNRESOLVED_ASSUMED_INDEPENDENT"
#: Declared and traceable to a specific frozen O4 overlap geometry.
CLUSTERING_UNIT_O4_RESOLVED = "O4_RESOLVED_CLUSTERING_UNIT"

CLUSTERING_UNIT_STATES = (CLUSTERING_UNIT_UNDECLARED, CLUSTERING_UNIT_O4_UNRESOLVED,
                          CLUSTERING_UNIT_O4_RESOLVED)
