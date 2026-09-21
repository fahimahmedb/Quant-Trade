"""``K_forward`` — the expected forward deployment cost, as a recipe.

Frictions are a first-order object here, not a haircut applied to a research
result afterwards.  ``D09_ROUTE_B_FRICTION_MARGIN_PARTITION_2026-09-17.md``
section 3 requires nine declarations per admitted component; each is a field of
:class:`CostComponent`, and :meth:`KForwardRecipe.violations` fails a recipe that
leaves one out.

Two rules do real work here:

* ``NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD`` — a component may only be a
  central expectation. An upper quantile or worst case is refused, because that
  protection belongs to ``M_economic`` and charging it twice invalidates the
  recipe.
* ``OMITTED_COST_IS_NOT_IMPLICIT_ZERO`` — every class F1..F7 must be either
  modelled or explicitly authorised to be zero. A class nobody mentioned is a
  recipe defect, not a free zero.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Mapping, Sequence

from .fingerprint import recipe_hash
from .parameters import COST_CLASSES, Dependence, ParameterInventory
from .states import (ESTIMATOR_CENTRAL_EXPECTATION, ESTIMATOR_KINDS,
                     K_FORWARD_PARAMETER_UNRESOLVED)
from .theta import ThetaState


#: Sign convention: a cost is a positive number that reduces economic value.
SIGN_COST_POSITIVE = "COST_POSITIVE_REDUCES_VALUE"
#: A credit (for example a rebate) is admissible but must say so explicitly.
SIGN_CREDIT_NEGATIVE = "CREDIT_NEGATIVE_INCREASES_VALUE"
SIGN_CONVENTIONS = (SIGN_COST_POSITIVE, SIGN_CREDIT_NEGATIVE)

#: The unit every component must reduce to before entering ``Phi``.
UNIT_ACCOUNT_CURRENCY = "ACCOUNT_CURRENCY_OVER_EVALUATION_REGIME"

#: Input classes a component may consume. Anything outcome-bearing is absent on
#: purpose: the recipe is outcome-blind.
ALLOWED_INPUT_CLASSES = (
    "FROZEN_COST_PARAMETER",
    "THETA_CAPITAL",
    "THETA_GEOMETRY",
    "THETA_ALLOCATION_STATE",
    "PERMITTED_LIQUIDITY_REFERENCE",
    "PARTICIPATION_DERIVED_FROM_THETA",
    "EXPECTED_DEPLOYED_EXPOSURE_Q",
    "EFFECT_COORDINATE_DELTA",
)

FORBIDDEN_INPUT_CLASSES = {
    "FORM4_REALISED_OUTCOME": "K_FORWARD_RECIPE_IS_OUTCOME_BLIND",
    "D05_CEILING": "RECIPE_PRECEDES_CEILING_NUMERICAL_FINAL_MEUE_MAY_FOLLOW_GEOMETRY",
    "PROGRAM_SUNK_COST": "PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
    "BUILDER_COST": "PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
    "RESEARCH_OPPORTUNITY_COST": "PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
}

#: Explicit cost-shape typology (V2 consolidation). Closes the Codex-identified
#: weakness (self red team item 1 / W1-SELF-001): a cost expressed as an
#: already-computed currency amount does not by itself prove *how* it depends
#: on size. A ``functional`` here already forces the component to be
#: recomputed at each ``theta``/``delta`` rather than supplied as a frozen
#: number (frictions.py's pre-existing design), but nothing previously named
#: *which shape* a component claims to have, so a mislabelled shape (a sqrt
#: impact cost that is actually linear, or a "fixed" fee that scales with
#: capital) could not be caught. ``verify_shape_declarations`` below probes
#: the functional numerically and fails the recipe on a contradiction, the
#: same idiom ``verify_dependence_declarations`` already uses for the
#: capital/delta dependence flags.
COST_SHAPE_FIXED = "FIXED"
COST_SHAPE_PER_SHARE = "PER_SHARE"
COST_SHAPE_PER_NOTIONAL = "PER_NOTIONAL"
COST_SHAPE_SPREAD_CROSSING = "SPREAD_CROSSING"
COST_SHAPE_SQRT_IMPACT = "SQRT_IMPACT"
COST_SHAPE_NONLINEAR_IMPACT = "NONLINEAR_IMPACT"
COST_SHAPE_BORROW = "BORROW"
COST_SHAPE_FINANCING = "FINANCING"
COST_SHAPE_TURNOVER_REBALANCE = "TURNOVER_REBALANCE"
COST_SHAPE_LATENCY_SLIPPAGE_REGIME = "LATENCY_SLIPPAGE_REGIME"

COST_SHAPES = (COST_SHAPE_FIXED, COST_SHAPE_PER_SHARE, COST_SHAPE_PER_NOTIONAL,
              COST_SHAPE_SPREAD_CROSSING, COST_SHAPE_SQRT_IMPACT,
              COST_SHAPE_NONLINEAR_IMPACT, COST_SHAPE_BORROW, COST_SHAPE_FINANCING,
              COST_SHAPE_TURNOVER_REBALANCE, COST_SHAPE_LATENCY_SLIPPAGE_REGIME)

#: Shapes whose expected cost-vs-capital ratio is numerically checkable at a
#: fixed probe scale. ``PER_SHARE``, ``SPREAD_CROSSING``, ``BORROW``,
#: ``FINANCING`` and ``TURNOVER_REBALANCE`` are economically linear-in-size
#: shapes too, but this engine's functional signature carries no separate
#: share-count or holding-period input, so at this abstraction they are
#: numerically indistinguishable from ``PER_NOTIONAL``; they are grouped with
#: it honestly rather than pretending a distinction this probe cannot see.
SHAPES_LINEAR_IN_CAPITAL = (COST_SHAPE_PER_SHARE, COST_SHAPE_PER_NOTIONAL,
                            COST_SHAPE_SPREAD_CROSSING, COST_SHAPE_BORROW,
                            COST_SHAPE_FINANCING, COST_SHAPE_TURNOVER_REBALANCE)
SHAPES_SQRT_IN_CAPITAL = (COST_SHAPE_SQRT_IMPACT,)
SHAPES_SCALE_INVARIANT = (COST_SHAPE_FIXED,)
#: Declared nonlinear or regime-dependent; checked only for "does not turn out
#: to be exactly constant", since a genuinely nonlinear or regime-switched cost
#: that never moves under any probe is mislabelled, but no single closed-form
#: ratio is claimed for either shape.
SHAPES_MUST_VARY_SOMEHOW = (COST_SHAPE_NONLINEAR_IMPACT, COST_SHAPE_LATENCY_SLIPPAGE_REGIME)


class CostInputUnavailable(RuntimeError):
    """A component needed a parameter the inventory has not resolved."""

    def __init__(self, component: str, parameter_id: str) -> None:
        super().__init__(f"{component}: {K_FORWARD_PARAMETER_UNRESOLVED}:{parameter_id}")
        self.component = component
        self.parameter_id = parameter_id
        self.state = K_FORWARD_PARAMETER_UNRESOLVED


#: A component functional: (delta, theta, resolved parameter values) -> currency.
CostFunctional = Callable[[float, ThetaState, Mapping[str, float]], float]


@dataclass(frozen=True)
class CostComponent:
    """One admitted expected-cost component with its nine declarations."""

    #: 1. component name.
    name: str
    #: cost class F1..F7 this component belongs to.
    cost_class: str
    #: 2. economic unit and sign convention.
    unit: str = UNIT_ACCOUNT_CURRENCY
    sign_convention: str = SIGN_COST_POSITIVE
    #: 3. execution regime / applicability condition.
    applicability: str = ""
    #: 4. deterministic formula or estimation functional.
    functional: CostFunctional | None = None
    #: human-readable statement of the formula, hashed with the recipe.
    formula_statement: str = ""
    #: 5. allowed input classes.
    input_classes: tuple[str, ...] = ()
    #: 6. provenance requirement: the parameter ids this component consumes.
    consumes: tuple[str, ...] = ()
    #: 7. whether the expected value depends on capital/geometry/liquidity/
    #: allocation state/delta.
    dependence: Dependence = field(default_factory=Dependence)
    #: 8. failure state if a required input is unavailable.
    failure_state: str = K_FORWARD_PARAMETER_UNRESOLVED
    #: 9. estimator kind. Only a central expectation is admissible.
    estimator_kind: str = ESTIMATOR_CENTRAL_EXPECTATION
    #: Any prudential markup. Must stay at zero; protection lives in M_economic.
    conservatism_markup: float = 0.0
    #: Explicit cost-shape typology (one of ``COST_SHAPES``). Required: a cost
    #: class alone (F1..F7) says which economic bucket a charge belongs to,
    #: not how it scales with size, and Codex's own self red team (item 1)
    #: named exactly this gap.
    shape: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.cost_class not in COST_CLASSES:
            problems.append(f"{self.name}: COST_CLASS_NOT_IN_FROZEN_INVENTORY")
        if self.shape not in COST_SHAPES:
            problems.append(f"{self.name}: COST_SHAPE_NOT_DECLARED")
        if self.unit != UNIT_ACCOUNT_CURRENCY:
            problems.append(f"{self.name}: COMPONENT_UNIT_MUST_REDUCE_TO_ACCOUNT_CURRENCY")
        if self.sign_convention not in SIGN_CONVENTIONS:
            problems.append(f"{self.name}: SIGN_CONVENTION_UNDECLARED")
        if not self.applicability:
            problems.append(f"{self.name}: APPLICABILITY_CONDITION_UNDECLARED")
        if self.functional is None:
            problems.append(f"{self.name}: NO_ESTIMATION_FUNCTIONAL")
        if not self.formula_statement:
            problems.append(f"{self.name}: FORMULA_NOT_STATED")
        if not self.input_classes:
            problems.append(f"{self.name}: ALLOWED_INPUT_CLASSES_UNDECLARED")
        for input_class in self.input_classes:
            if input_class in FORBIDDEN_INPUT_CLASSES:
                problems.append(f"{self.name}: {FORBIDDEN_INPUT_CLASSES[input_class]}")
            elif input_class not in ALLOWED_INPUT_CLASSES:
                problems.append(f"{self.name}: INPUT_CLASS_NOT_ADMITTED:{input_class}")
        if self.estimator_kind not in ESTIMATOR_KINDS:
            problems.append(f"{self.name}: ESTIMATOR_KIND_NOT_RECOGNISED")
        elif self.estimator_kind != ESTIMATOR_CENTRAL_EXPECTATION:
            problems.append(f"{self.name}: NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD")
        if self.conservatism_markup != 0.0:
            problems.append(f"{self.name}: NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD")
        if self.failure_state != K_FORWARD_PARAMETER_UNRESOLVED:
            problems.append(f"{self.name}: COMPONENT_FAILURE_STATE_NOT_RECOGNISED")
        if self.dependence.delta and "EFFECT_COORDINATE_DELTA" not in self.input_classes:
            problems.append(f"{self.name}: DELTA_DEPENDENCE_WITHOUT_DELTA_INPUT_CLASS")
        return problems

    def expected_cost(self, delta: float, theta: ThetaState,
                      params: Mapping[str, float]) -> float:
        if self.functional is None:
            raise CostInputUnavailable(self.name, "<no functional>")
        for parameter_id in self.consumes:
            if parameter_id not in params:
                raise CostInputUnavailable(self.name, parameter_id)
        value = float(self.functional(delta, theta, params))
        return value

    def declaration(self) -> dict[str, Any]:
        """Hashable declaration. The callable is represented by its statement."""
        document = {key: value for key, value in asdict(self).items()
                    if key != "functional"}
        document["dependence"] = self.dependence.to_dict()
        return document


@dataclass(frozen=True)
class AuthorisedZero:
    """An explicit authority that a cost class is economically zero."""

    cost_class: str
    authority_reference: str
    justification: str

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.cost_class not in COST_CLASSES:
            problems.append(f"{self.cost_class}: COST_CLASS_NOT_IN_FROZEN_INVENTORY")
        if not self.authority_reference:
            problems.append(f"{self.cost_class}: ZERO_REQUIRES_EXPLICIT_AUTHORITY")
        if not self.justification:
            problems.append(f"{self.cost_class}: ZERO_REQUIRES_JUSTIFICATION")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class KForwardRecipe:
    """The frozen expected-cost recipe.

    ``K_FORWARD_RECIPE_PRECEDES_D05_CEILING_VISIBILITY``: the recipe is complete
    and hashable before any numerical instantiation, and
    :meth:`expected_cost` refuses to run on an inventory whose parameters are
    unresolved rather than substituting a convenient default.
    """

    recipe_id: str
    components: tuple[CostComponent, ...]
    authorised_zeros: tuple[AuthorisedZero, ...] = ()

    # -- structural checks ----------------------------------------------------

    def coverage_violations(self) -> list[str]:
        covered = {component.cost_class for component in self.components}
        covered |= {zero.cost_class for zero in self.authorised_zeros}
        missing = [cost_class for cost_class in COST_CLASSES if cost_class not in covered]
        return [f"OMITTED_COST_IS_NOT_IMPLICIT_ZERO:{cost_class}" for cost_class in missing]

    def violations(self) -> list[str]:
        problems: list[str] = []
        names = [component.name for component in self.components]
        if len(set(names)) != len(names):
            problems.append("DUPLICATE_COST_COMPONENT_NAME")
        for component in self.components:
            problems.extend(component.violations())
        for zero in self.authorised_zeros:
            problems.extend(zero.violations())
        modelled = {component.cost_class for component in self.components}
        for zero in self.authorised_zeros:
            if zero.cost_class in modelled:
                problems.append(
                    f"{zero.cost_class}: CLASS_BOTH_MODELLED_AND_AUTHORISED_ZERO")
        problems.extend(self.coverage_violations())
        return problems

    def parameter_violations(self, inventory: ParameterInventory) -> list[str]:
        """Every consumed parameter must exist in the frozen inventory."""
        problems: list[str] = []
        for component in self.components:
            for parameter_id in component.consumes:
                if parameter_id not in inventory:
                    problems.append(
                        f"{component.name}: PARAMETER_NOT_IN_FROZEN_INVENTORY:{parameter_id}")
                    continue
                parameter = inventory[parameter_id]
                if parameter.cost_component != component.cost_class:
                    problems.append(
                        f"{component.name}: PARAMETER_COST_CLASS_MISMATCH:{parameter_id}")
        return problems

    # -- evaluation -----------------------------------------------------------

    @property
    def depends_on_delta(self) -> bool:
        return any(component.dependence.delta for component in self.components)

    def expected_cost(self, delta: float, theta: ThetaState,
                      params: Mapping[str, float]) -> float:
        total = 0.0
        for component in self.components:
            total += component.expected_cost(delta, theta, params)
        return total

    def component_costs(self, delta: float, theta: ThetaState,
                        params: Mapping[str, float]) -> dict[str, float]:
        return {component.name: component.expected_cost(delta, theta, params)
                for component in self.components}

    # -- addressability -------------------------------------------------------

    def rule_document(self) -> dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "components": sorted((component.declaration() for component in self.components),
                                 key=lambda row: row["name"]),
            "authorised_zeros": sorted((zero.to_dict() for zero in self.authorised_zeros),
                                       key=lambda row: row["cost_class"]),
        }

    def fingerprint(self) -> str:
        return recipe_hash(self.rule_document())


def verify_dependence_declarations(recipe: KForwardRecipe, theta: ThetaState,
                                   params: Mapping[str, float],
                                   probe_deltas: Sequence[float] = (0.0, 0.01, 0.05),
                                   capital_probe: float = 2.0,
                                   tolerance: float = 1e-12) -> list[str]:
    """Check declared dependence against what the functionals actually do.

    A component that declares ``delta=False`` but whose value moves with delta is
    a silent violation of the frozen recipe: the affine BEEE shortcut would then
    be applied to a mapping that is not affine. This probe is the reason the
    declaration is worth anything.
    """
    from dataclasses import replace as _replace

    problems: list[str] = []
    for component in recipe.components:
        try:
            values = [component.expected_cost(delta, theta, params) for delta in probe_deltas]
        except CostInputUnavailable as error:
            problems.append(f"{component.name}: {error.state}:{error.parameter_id}")
            continue
        varies_with_delta = max(values) - min(values) > tolerance
        if varies_with_delta and not component.dependence.delta:
            problems.append(f"{component.name}: DECLARED_DELTA_INDEPENDENT_BUT_VARIES")
        if not varies_with_delta and component.dependence.delta:
            problems.append(f"{component.name}: DECLARED_DELTA_DEPENDENT_BUT_CONSTANT")
        scaled = _replace(theta, capital=theta.capital * capital_probe)
        try:
            moved = component.expected_cost(probe_deltas[0], scaled, params)
        except CostInputUnavailable:
            continue
        varies_with_capital = abs(moved - values[0]) > tolerance
        if varies_with_capital and not component.dependence.capital:
            problems.append(f"{component.name}: DECLARED_CAPITAL_INDEPENDENT_BUT_VARIES")
    return problems


def verify_shape_declarations(recipe: KForwardRecipe, theta: ThetaState,
                              params: Mapping[str, float], probe_delta: float = 0.0,
                              exposure_scale: float = 4.0, participation_scale: float = 4.0,
                              tolerance: float = 1e-9) -> list[str]:
    """Probe each component's functional against its declared ``shape``.

    Two axes are scaled independently because a component's functional takes
    the full ``theta``, not one "size" scalar: ``expected_deployed_exposure``
    (``Q(theta)``, what ``gross_value`` scales with — the axis a per-notional
    or spread-crossing charge should track) and ``participation`` (the axis a
    square-root impact model scales with, per the envelope contract's own
    reference-participation shape). A component whose numeric behaviour
    contradicts its declared shape is a concrete, checkable instance of the
    weakness Codex's own self red team named (item 1 / ``W1-SELF-001``): an
    already-computed currency amount does not by itself prove which size
    variable it tracks, or how.

    Only the shapes with one unambiguous, checkable ratio are held to a
    numeric tolerance (``FIXED``, the linear-in-exposure group, and
    ``SQRT_IMPACT``); ``NONLINEAR_IMPACT`` and ``LATENCY_SLIPPAGE_REGIME`` are
    checked only for not being silently constant, since neither claims one
    closed-form ratio. This does not invent a numerical coefficient: it only
    checks the *shape* of a functional the recipe author already supplied.
    """
    from dataclasses import replace as _replace

    problems: list[str] = []
    for component in recipe.components:
        if component.shape not in COST_SHAPES:
            continue  # already reported by CostComponent.violations()
        try:
            base = component.expected_cost(probe_delta, theta, params)
            exposure_scaled = component.expected_cost(
                probe_delta,
                _replace(theta, expected_deployed_exposure=
                        theta.expected_deployed_exposure * exposure_scale),
                params)
            participation_probe = theta.participation if theta.participation else 0.01
            participation_scaled = component.expected_cost(
                probe_delta,
                _replace(theta, participation=participation_probe * participation_scale),
                params)
        except CostInputUnavailable as error:
            problems.append(f"{component.name}: {error.state}:{error.parameter_id}")
            continue

        exposure_moves = abs(exposure_scaled - base) > tolerance
        participation_moves = abs(participation_scaled - base) > tolerance

        if component.shape in SHAPES_SCALE_INVARIANT:
            if exposure_moves:
                problems.append(f"{component.name}: DECLARED_FIXED_BUT_VARIES_WITH_EXPOSURE")
            if participation_moves:
                problems.append(f"{component.name}: DECLARED_FIXED_BUT_VARIES_WITH_PARTICIPATION")
        elif component.shape in SHAPES_LINEAR_IN_CAPITAL:
            if theta.expected_deployed_exposure > 0 and not exposure_moves:
                problems.append(f"{component.name}: DECLARED_LINEAR_IN_EXPOSURE_BUT_CONSTANT")
            elif abs(base) > tolerance and exposure_moves:
                ratio = exposure_scaled / base
                if abs(ratio - exposure_scale) > max(1e-6, 1e-6 * exposure_scale):
                    problems.append(
                        f"{component.name}: DECLARED_LINEAR_IN_EXPOSURE_BUT_RATIO_"
                        f"{ratio:.6f}_NOT_{exposure_scale:.6f}")
        elif component.shape in SHAPES_SQRT_IN_CAPITAL:
            if participation_probe > 0 and not participation_moves:
                problems.append(
                    f"{component.name}: DECLARED_SQRT_IMPACT_BUT_CONSTANT_IN_PARTICIPATION")
            elif abs(base) > tolerance and participation_moves:
                ratio = participation_scaled / base
                expected = math.sqrt(participation_scale)
                if abs(ratio - expected) > max(1e-6, 1e-3 * expected):
                    problems.append(
                        f"{component.name}: DECLARED_SQRT_IMPACT_BUT_RATIO_{ratio:.6f}_"
                        f"NOT_SQRT_{expected:.6f}")
        elif component.shape in SHAPES_MUST_VARY_SOMEHOW:
            if not exposure_moves and not participation_moves:
                problems.append(
                    f"{component.name}: DECLARED_{component.shape}_BUT_NEVER_VARIES")
    return problems
