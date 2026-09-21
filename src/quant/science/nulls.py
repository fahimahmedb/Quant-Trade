"""Null models that preserve the structure they are supposed to test against.

A null distribution built by shuffling everything answers the wrong question. The
nulls here keep the parts of the design that are not under test — the allocation
weights, the issuer clustering, the calendar — and move only the thing whose
predictive content is being questioned.

The placebo null refuses an offset that lands inside the true exposure window,
because a placebo overlapping the real holding period shares its returns and
would understate the null spread. That refusal is the difference between a
placebo test and a formality.

Empirical p-values use the ``(1 + hits) / (1 + draws)`` convention, so they are
never zero: a finite null sample cannot prove an effect is impossible under the
null.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Sequence

from .formation import HOLD_SESSIONS, SessionCalendar
from .inference import ratio_estimate


PLACEBO_OFFSET_OVERLAPS = "PLACEBO_OFFSET_OVERLAPS_TRUE_EXPOSURE"
PLACEBO_OFFSET_OFF_CALENDAR = "PLACEBO_OFFSET_OFF_CALENDAR"


@dataclass(frozen=True)
class NullDraws:
    model: str
    draws: tuple[float, ...]
    refused: tuple[str, ...] = ()
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def empirical_p_value(observed: float, draws: Sequence[float],
                      two_sided: bool = True) -> float | None:
    """``(1 + hits) / (1 + draws)``; ``None`` when there are no draws."""
    if not draws:
        return None
    if two_sided:
        hits = sum(1 for value in draws if abs(value) >= abs(observed))
    else:
        hits = sum(1 for value in draws if value >= observed)
    return (1.0 + hits) / (1.0 + len(draws))


def placebo_offsets(calendar: SessionCalendar, entry_sessions: Sequence[str],
                    offsets: Sequence[int],
                    hold_sessions: int = HOLD_SESSIONS) -> tuple[list[int], list[str]]:
    """Keep only offsets that are on-calendar for every event and non-overlapping."""
    admissible: list[int] = []
    refused: list[str] = []
    for offset in offsets:
        if offset == 0:
            refused.append(f"{offset}:OFFSET_ZERO_IS_THE_TRUE_SAMPLE")
            continue
        if abs(offset) <= hold_sessions:
            refused.append(f"{offset}:{PLACEBO_OFFSET_OVERLAPS}")
            continue
        off_calendar = False
        for session in entry_sessions:
            position = calendar.index_of(session)
            if position is None or calendar.at(position + offset) is None:
                off_calendar = True
                break
        if off_calendar:
            refused.append(f"{offset}:{PLACEBO_OFFSET_OFF_CALENDAR}")
            continue
        admissible.append(offset)
    return admissible, refused


def placebo_null(weights: Sequence[float], entry_sessions: Sequence[str],
                 measure: Callable[[str], float | None], calendar: SessionCalendar,
                 offsets: Sequence[int], clusters: Sequence[Any] | None = None,
                 hold_sessions: int = HOLD_SESSIONS) -> NullDraws:
    """Shift every event's entry by the same offset and re-measure.

    A common offset for all events preserves the cross-sectional and clustering
    structure; only the alignment to the signal is destroyed, which is exactly
    the content under test.
    """
    admissible, refused = placebo_offsets(calendar, entry_sessions, offsets, hold_sessions)
    draws: list[float] = []
    for offset in admissible:
        shifted: list[float] = []
        shifted_weights: list[float] = []
        shifted_clusters: list[Any] = []
        for index, session in enumerate(entry_sessions):
            position = calendar.index_of(session)
            if position is None:
                continue
            moved = calendar.at(position + offset)
            if moved is None:
                continue
            outcome = measure(moved)
            if outcome is None:
                continue
            shifted.append(outcome)
            shifted_weights.append(weights[index])
            if clusters is not None:
                shifted_clusters.append(clusters[index])
        if not shifted:
            refused.append(f"{offset}:NO_MEASURABLE_PLACEBO_OUTCOMES")
            continue
        estimate = ratio_estimate(shifted_weights, shifted,
                                  shifted_clusters if clusters is not None else None)
        if estimate.point is not None:
            draws.append(estimate.point)
    return NullDraws("PLACEBO_COMMON_SESSION_SHIFT", tuple(draws), tuple(refused),
                     f"admissible_offsets={admissible}")


def cluster_sign_flip_null(weights: Sequence[float], outcomes: Sequence[float],
                           clusters: Sequence[Any] | None = None,
                           draws: int = 2000, seed: int = 20260919) -> NullDraws:
    """Flip whole clusters' demeaned contributions, preserving within-cluster shape.

    Flipping individual observations inside a cluster would destroy the
    dependence the cluster represents and produce a null that is too tight.
    """
    import random

    denominator = float(sum(weights))
    if denominator <= 0:
        return NullDraws("CLUSTER_SIGN_FLIP", (), ("NO_DEPLOYED_EXPOSURE",))
    point = sum(weight * outcome
                for weight, outcome in zip(weights, outcomes)) / denominator
    keys = clusters if clusters is not None else list(range(len(weights)))
    groups: dict[Any, list[int]] = {}
    for index, key in enumerate(keys):
        groups.setdefault(key, []).append(index)
    order = sorted(groups, key=repr)
    if len(order) < 2:
        return NullDraws("CLUSTER_SIGN_FLIP", (),
                         ("VARIANCE_UNIDENTIFIED_FROM_ONE_CLUSTER",))
    generator = random.Random(seed)
    samples: list[float] = []
    for _ in range(draws):
        total = 0.0
        for key in order:
            sign = 1.0 if generator.random() < 0.5 else -1.0
            total += sign * sum(weights[index] * (outcomes[index] - point)
                                for index in groups[key])
        samples.append(total / denominator)
    return NullDraws("CLUSTER_SIGN_FLIP", tuple(samples), (), f"seed={seed}")
