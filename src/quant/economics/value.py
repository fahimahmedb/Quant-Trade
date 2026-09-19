"""``Phi``, and the break-even effect ``BEEE`` as the root of ``Phi``.

EC1 section 7-8 fixes the shape:

    GROSS_VALUE(delta, theta) = Q(theta) * delta
    Phi(delta, theta)         = GROSS_VALUE(delta, theta) - K_forward(delta, theta)
    R_BEEE(theta)             = {delta : Phi(delta, theta) = 0}

and refuses to assume ``Phi`` is affine in ``delta``.  The quotient
``BEEE = K_forward / Q`` is available only in the independently established
affine case, guarded here by ``BEEE_QUOTIENT_REQUIRES_AFFINE_COST_INDEPENDENCE``.

The root finder is deterministic: the effect domain and its node count are part
of the recipe, so two runs of the same frozen recipe return the same state and
the same number.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Callable, Mapping

from .fingerprint import recipe_hash
from .frictions import CostInputUnavailable, KForwardRecipe
from .states import (BEEE_NO_ECONOMIC_ROOT, BEEE_NONMONOTONE_MAPPING,
                     BEEE_NONUNIQUE_ROOT, BEEE_UNIQUE_ROOT,
                     K_FORWARD_PARAMETER_UNRESOLVED)
from .theta import ThetaState


@dataclass(frozen=True)
class EffectDomain:
    """The admissible effect domain on which root existence is evaluated.

    Part of the frozen recipe: the remainder contract section 4 requires the
    effect domain and the deterministic root-selection rule to be declared, not
    chosen at the moment a number is wanted.
    """

    lower: float
    upper: float
    nodes: int = 401
    #: Absolute tolerance on ``Phi`` at the returned root.
    root_tolerance: float = 1e-12
    #: Bisection iterations. Fixed so the result is reproducible.
    max_iterations: int = 200

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not self.upper > self.lower:
            problems.append("EFFECT_DOMAIN_NOT_ORDERED")
        if self.nodes < 3:
            problems.append("EFFECT_DOMAIN_GRID_TOO_COARSE")
        if self.root_tolerance <= 0:
            problems.append("ROOT_TOLERANCE_MUST_BE_POSITIVE")
        if self.max_iterations < 10:
            problems.append("ROOT_ITERATIONS_TOO_FEW")
        return problems

    def grid(self) -> list[float]:
        step = (self.upper - self.lower) / (self.nodes - 1)
        return [self.lower + step * index for index in range(self.nodes)]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BEEEResult:
    """The break-even effect, or the reason there isn't one."""

    state: str
    value: float | None
    #: ``Phi`` at each grid node, for the audit trail.
    root_count: int
    strictly_increasing: bool
    phi_at_lower: float | None = None
    phi_at_upper: float | None = None
    detail: str = ""

    @property
    def resolved(self) -> bool:
        return self.state == BEEE_UNIQUE_ROOT and self.value is not None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AffineShortcutUnavailable(RuntimeError):
    """``BEEE = K_forward / Q`` was requested where it does not apply."""


@dataclass(frozen=True)
class PhiInstance:
    """A consumable ``Phi`` for one ``theta`` and one parameter vector."""

    theta: ThetaState
    k_forward: KForwardRecipe
    params: Mapping[str, float]
    domain: EffectDomain

    @property
    def q(self) -> float:
        return float(self.theta.expected_deployed_exposure)

    def gross_value(self, delta: float) -> float:
        return self.q * delta

    def cost(self, delta: float) -> float:
        return self.k_forward.expected_cost(delta, self.theta, self.params)

    def phi(self, delta: float) -> float:
        return self.gross_value(delta) - self.cost(delta)

    def rule_document(self) -> dict[str, Any]:
        return {"k_forward": self.k_forward.rule_document(),
                "effect_domain": self.domain.to_dict(),
                "theta_id": self.theta.theta_id,
                "q_provenance": self.theta.q_provenance}

    def fingerprint(self) -> str:
        return recipe_hash(self.rule_document())


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def solve_beee(phi: Callable[[float], float], domain: EffectDomain) -> BEEEResult:
    """Deterministically resolve the economically meaningful root of ``Phi``.

    Ordering of the failure states is deliberate. More than one root is reported
    as ``BEEE_NONUNIQUE_ROOT`` even if the mapping also fails monotonicity,
    because non-uniqueness is the sharper statement about what an authority would
    be asked to consume. A single root reached by a mapping that is not strictly
    increasing is ``BEEE_NONMONOTONE_MAPPING``: a crossing where more effect
    makes the economics worse is not a break-even point.
    """
    problems = domain.violations()
    if problems:
        raise ValueError("invalid effect domain: " + "; ".join(problems))

    grid = domain.grid()
    values = [phi(node) for node in grid]
    if any(not math.isfinite(value) for value in values):
        return BEEEResult(BEEE_NONMONOTONE_MAPPING, None, 0, False,
                          detail="PHI_NOT_FINITE_ON_EFFECT_DOMAIN")

    zero_nodes = sum(1 for value in values if value == 0.0)
    crossings = sum(1 for index in range(len(values) - 1)
                    if _sign(values[index]) * _sign(values[index + 1]) < 0)
    root_count = zero_nodes + crossings
    strictly_increasing = all(values[index + 1] > values[index]
                              for index in range(len(values) - 1))

    if root_count > 1:
        return BEEEResult(BEEE_NONUNIQUE_ROOT, None, root_count, strictly_increasing,
                          values[0], values[-1],
                          detail=f"{root_count} roots on the declared effect domain")
    if root_count == 0:
        detail = ("PHI_POSITIVE_ON_WHOLE_DOMAIN" if values[0] > 0
                  else "PHI_NEGATIVE_ON_WHOLE_DOMAIN")
        return BEEEResult(BEEE_NO_ECONOMIC_ROOT, None, 0, strictly_increasing,
                          values[0], values[-1], detail=detail)
    if not strictly_increasing:
        return BEEEResult(BEEE_NONMONOTONE_MAPPING, None, root_count, False,
                          values[0], values[-1],
                          detail="PHI_NOT_STRICTLY_INCREASING_ON_EFFECT_DOMAIN")

    # Exactly one root and strictly increasing: bracket it and bisect.
    for index, value in enumerate(values):
        if value == 0.0:
            return BEEEResult(BEEE_UNIQUE_ROOT, grid[index], 1, True,
                              values[0], values[-1], detail="ROOT_AT_GRID_NODE")
    low = next(index for index in range(len(values) - 1)
               if _sign(values[index]) * _sign(values[index + 1]) < 0)
    left, right = grid[low], grid[low + 1]
    left_value = values[low]
    for _ in range(domain.max_iterations):
        middle = 0.5 * (left + right)
        middle_value = phi(middle)
        if abs(middle_value) <= domain.root_tolerance:
            return BEEEResult(BEEE_UNIQUE_ROOT, middle, 1, True,
                              values[0], values[-1], detail="ROOT_BY_BISECTION")
        if _sign(middle_value) == _sign(left_value):
            left, left_value = middle, middle_value
        else:
            right = middle
    return BEEEResult(BEEE_UNIQUE_ROOT, 0.5 * (left + right), 1, True,
                      values[0], values[-1], detail="ROOT_BY_BISECTION_ITERATION_LIMIT")


def beee(instance: PhiInstance) -> BEEEResult:
    """Resolve BEEE for one ``Phi`` instance, mapping input failure to a state."""
    try:
        return solve_beee(instance.phi, instance.domain)
    except CostInputUnavailable as error:
        return BEEEResult(K_FORWARD_PARAMETER_UNRESOLVED, None, 0, False,
                          detail=f"{error.component}:{error.parameter_id}")


def beee_affine(instance: PhiInstance) -> float:
    """``BEEE = K_forward / Q`` under the affine special case only.

    Raises unless all three conditions EC1 section 8 names actually hold:
    ``Q > 0``, ``Q`` independent of ``delta``, and ``K_forward`` independent of
    ``delta``. ``Q`` is a scalar property of ``theta`` here, so its independence
    from ``delta`` is structural; the cost independence is checked against the
    declarations *and* probed numerically, because a declaration that is wrong
    would silently produce a number for a non-affine mapping.
    """
    if instance.q <= 0:
        raise AffineShortcutUnavailable(
            "BEEE_QUOTIENT_REQUIRES_AFFINE_COST_INDEPENDENCE: Q(theta) is not positive")
    if instance.k_forward.depends_on_delta:
        raise AffineShortcutUnavailable(
            "BEEE_QUOTIENT_REQUIRES_AFFINE_COST_INDEPENDENCE: a cost component declares "
            "dependence on delta")
    probes = (instance.domain.lower, 0.5 * (instance.domain.lower + instance.domain.upper),
              instance.domain.upper)
    costs = [instance.cost(delta) for delta in probes]
    if max(costs) - min(costs) > 1e-12:
        raise AffineShortcutUnavailable(
            "BEEE_QUOTIENT_REQUIRES_AFFINE_COST_INDEPENDENCE: K_forward varies with delta "
            "although no component declared it")
    return costs[0] / instance.q
