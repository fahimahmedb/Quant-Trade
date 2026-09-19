"""The D05-A design-invariance test, executable.

``governance/D07_OPEN_SPACE_BOUNDARY.md`` section 5 states the rule plainly: a
quantity may enter D05-A only if its definition, observation unit, population,
denominator, mapping and calculation are identical for **every admissible
combination** of ``D07-O1 x O2 x O3 x O4``.  The test runs against the full frozen
open space, never the likely or preferred geometry, and a quantity that moves
under any admissible convention is ``CLAIM-DESIGN-SENSITIVE -> D05-B``.

If invariance cannot be established before values are observed, the state is
``AMBIGUOUS -> EMBARGO``. That is not terminal, but it is also not a pass: this
module never resolves an ambiguity by picking a geometry.

The O1 candidate set is supplied by the frozen exhaustive admissible set. The O2,
O3 and O4 candidate sets have to be supplied by the caller, because D07 leaves
them open without enumerating them — and a test run over a space the caller
narrowed is honest only if the narrowing is visible, so the space used is
returned with the verdict.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Sequence

from .formation import (FORMATION_UNRESOLVED, GeometryChoice, O1_ADMISSIBLE,
                        OBSERVATION_COUNT_UNRESOLVED, O3Convention)


DESIGN_INVARIANT = "DESIGN_INVARIANT_D05A_ELIGIBLE"
CLAIM_DESIGN_SENSITIVE = "CLAIM_DESIGN_SENSITIVE_D05B"
AMBIGUOUS_EMBARGO = "AMBIGUOUS_EMBARGO"

#: Values that mean "no answer under this geometry" rather than an answer.
UNRESOLVED_MARKERS = (FORMATION_UNRESOLVED, OBSERVATION_COUNT_UNRESOLVED, None)


def admissible_geometries(o2_orderings: Sequence[str],
                          o3_conventions: Sequence[O3Convention],
                          o4_overlaps: Sequence[str],
                          o1_set: Sequence[str] = O1_ADMISSIBLE
                          ) -> tuple[GeometryChoice, ...]:
    """Every combination of the supplied candidate sets."""
    return tuple(GeometryChoice(o1=o1, o2_ordering=o2, o3=o3, o4_overlap=o4)
                 for o1 in o1_set for o2 in o2_orderings
                 for o3 in o3_conventions for o4 in o4_overlaps)


@dataclass(frozen=True)
class InvarianceVerdict:
    classification: str
    #: Geometry description -> value produced under it.
    values: dict[str, Any]
    #: The space the test actually ran over, so a narrowed space is visible.
    space: dict[str, Any]
    reasons: tuple[str, ...] = ()

    @property
    def d05a_eligible(self) -> bool:
        return self.classification == DESIGN_INVARIANT

    def to_dict(self) -> dict[str, Any]:
        return {"classification": self.classification, "values": dict(self.values),
                "space": dict(self.space), "reasons": list(self.reasons)}


def _describe(geometry: GeometryChoice) -> str:
    o3 = geometry.o3.name if geometry.o3 else None
    return f"o1={geometry.o1}|o2={geometry.o2_ordering}|o3={o3}|o4={geometry.o4_overlap}"


def _space(geometries: Sequence[GeometryChoice]) -> dict[str, Any]:
    return {
        "combinations": len(geometries),
        "o1": sorted({geometry.o1 for geometry in geometries if geometry.o1}),
        "o2": sorted({geometry.o2_ordering for geometry in geometries
                      if geometry.o2_ordering}),
        "o3": sorted({geometry.o3.name for geometry in geometries if geometry.o3}),
        "o4": sorted({geometry.o4_overlap for geometry in geometries
                      if geometry.o4_overlap}),
    }


def design_invariance(quantity: Callable[[GeometryChoice], Any],
                      geometries: Sequence[GeometryChoice],
                      quantity_name: str = "") -> InvarianceVerdict:
    """Classify one quantity against the supplied admissible geometry space.

    A quantity that raises under some geometry is ambiguous, not sensitive: an
    exception is the absence of a definition, and reporting it as a value
    difference would claim we measured something.
    """
    label = quantity_name or "quantity"
    if not geometries:
        return InvarianceVerdict(AMBIGUOUS_EMBARGO, {}, {"combinations": 0},
                                 (f"{label}: NO_ADMISSIBLE_GEOMETRY_SUPPLIED",))
    values: dict[str, Any] = {}
    reasons: list[str] = []
    for geometry in geometries:
        description = _describe(geometry)
        problems = geometry.violations()
        if problems:
            reasons.append(f"{label}: INADMISSIBLE_GEOMETRY_IN_SPACE:{description}")
            continue
        try:
            value = quantity(geometry)
        except Exception as error:  # noqa: BLE001 - absence of a definition
            reasons.append(f"{label}: QUANTITY_UNDEFINED_UNDER:{description}:{error}")
            continue
        values[description] = value
    if reasons:
        return InvarianceVerdict(AMBIGUOUS_EMBARGO, values, _space(geometries),
                                 tuple(reasons))
    unresolved = [description for description, value in values.items()
                  if value in UNRESOLVED_MARKERS]
    if unresolved:
        return InvarianceVerdict(
            AMBIGUOUS_EMBARGO, values, _space(geometries),
            tuple(f"{label}: UNRESOLVED_UNDER:{description}"
                  for description in sorted(unresolved)))
    distinct = {repr(value) for value in values.values()}
    if len(distinct) == 1:
        return InvarianceVerdict(DESIGN_INVARIANT, values, _space(geometries))
    return InvarianceVerdict(
        CLAIM_DESIGN_SENSITIVE, values, _space(geometries),
        (f"{label}: value varies across {len(distinct)} admissible geometries",))
