"""Which hypothesis to work on next, on declared grounds.

Research capacity is the scarcest resource this system has, so the ordering of
hypotheses is an economic decision and should be made the same way as any other:
against declared inputs, before results are known.

The ranking is deliberately crude and explicit — expected information value and
capital potential over Builder cost and time to falsification — because a
sophisticated score would invite tuning. What matters more than the formula is
what the formula may not read:

    P0_RESERVOIR_IS_NEVER_A_PRIORITY_SIGNAL

A candidate whose priority inputs include any prospective P0 signal is refused.
Prioritising research by what the reservoir seems to contain is the same leak as
reading it directly, only slower.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from ..economics.fingerprint import recipe_hash


#: Input classes a priority score may legitimately read.
ADMISSIBLE_PRIORITY_INPUTS = (
    "PUBLISHED_MECHANISM_LITERATURE",
    "SYSTEM_CAPABILITY_GAP",
    "BUILDER_EFFORT_ESTIMATE",
    "TIME_TO_FALSIFICATION_ESTIMATE",
    "CAPACITY_HEADROOM_ESTIMATE",
    "EXISTING_EXPLORATORY_RESULT_LABELLED_DEVELOPMENT",
    "GOVERNANCE_DEPENDENCY_STATE",
)

#: Input classes that would turn prioritisation into a reservoir side-channel.
FORBIDDEN_PRIORITY_INPUTS = {
    "P0_PROSPECTIVE_FILING_COUNT": "P0_RESERVOIR_IS_NEVER_A_PRIORITY_SIGNAL",
    "P0_PROSPECTIVE_OUTCOMES": "P0_RESERVOIR_IS_NEVER_A_PRIORITY_SIGNAL",
    "P0_CAPTURE_VOLUME": "P0_RESERVOIR_IS_NEVER_A_PRIORITY_SIGNAL",
    "P0_IDENTITIES_OR_ACCESSIONS": "P0_RESERVOIR_IS_NEVER_A_PRIORITY_SIGNAL",
    "D05_CEILING_VALUES": "RECIPE_PRECEDES_CEILING_NUMERICAL_FINAL_MEUE_MAY_FOLLOW_GEOMETRY",
    "RESULTING_MEUE_MAGNITUDE": "MEUE_RESULT_CANNOT_TUNE_ITS_OWN_MARGIN",
}


@dataclass(frozen=True)
class HypothesisCandidate:
    """One candidate research lane with its declared priority inputs."""

    hypothesis_id: str
    family: str
    #: What the system learns whether the answer is yes or no, in [0, 1].
    information_value: float
    #: Builder effort, in Builder-days.
    builder_days: float
    #: Sessions of forward data before the hypothesis could be falsified.
    sessions_to_falsification: int
    #: Deployable capital this lane could plausibly support, account currency.
    capital_potential: float
    priority_inputs: tuple[str, ...] = ()
    #: Governance states that must hold before work may start.
    prerequisites: tuple[str, ...] = ()
    note: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not 0.0 <= self.information_value <= 1.0:
            problems.append(f"{self.hypothesis_id}: INFORMATION_VALUE_OUT_OF_RANGE")
        if self.builder_days <= 0:
            problems.append(f"{self.hypothesis_id}: BUILDER_DAYS_MUST_BE_POSITIVE")
        if self.sessions_to_falsification <= 0:
            problems.append(f"{self.hypothesis_id}: TIME_TO_FALSIFICATION_MUST_BE_POSITIVE")
        if self.capital_potential < 0:
            problems.append(f"{self.hypothesis_id}: CAPITAL_POTENTIAL_NEGATIVE")
        if not self.priority_inputs:
            problems.append(f"{self.hypothesis_id}: PRIORITY_INPUTS_UNDECLARED")
        for source in self.priority_inputs:
            if source in FORBIDDEN_PRIORITY_INPUTS:
                problems.append(
                    f"{self.hypothesis_id}: {FORBIDDEN_PRIORITY_INPUTS[source]}:{source}")
            elif source not in ADMISSIBLE_PRIORITY_INPUTS:
                problems.append(f"{self.hypothesis_id}: PRIORITY_INPUT_NOT_ADMITTED:{source}")
        return problems

    @property
    def score(self) -> float | None:
        """``information_value * capital_potential / (days * sessions)``.

        Returns ``None`` when the candidate is inadmissible: an inadmissible
        candidate has no priority, not a low one.
        """
        if self.violations():
            return None
        return (self.information_value * self.capital_potential
                / (self.builder_days * self.sessions_to_falsification))

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["score"] = self.score
        document["violations"] = self.violations()
        return document


@dataclass(frozen=True)
class PriorityRanking:
    ranking_id: str
    ranked: tuple[HypothesisCandidate, ...]
    refused: tuple[HypothesisCandidate, ...]
    violations: tuple[str, ...] = ()

    def order(self) -> list[str]:
        return [candidate.hypothesis_id for candidate in self.ranked]

    def to_dict(self) -> dict[str, Any]:
        return {"ranking_id": self.ranking_id,
                "ranked": [candidate.to_dict() for candidate in self.ranked],
                "refused": [candidate.to_dict() for candidate in self.refused],
                "violations": list(self.violations),
                "rule_hash": recipe_hash({
                    "admissible_inputs": list(ADMISSIBLE_PRIORITY_INPUTS),
                    "forbidden_inputs": sorted(FORBIDDEN_PRIORITY_INPUTS),
                    "score": "information_value * capital_potential / "
                             "(builder_days * sessions_to_falsification)"})}


def rank(ranking_id: str, candidates: Iterable[HypothesisCandidate],
         satisfied_prerequisites: Iterable[str] = ()) -> PriorityRanking:
    """Rank admissible candidates; refuse the rest with their reasons.

    A candidate whose prerequisites are not satisfied is refused rather than
    ranked low: working on it now would produce evidence nothing can consume.
    """
    available = set(satisfied_prerequisites)
    ranked: list[HypothesisCandidate] = []
    refused: list[HypothesisCandidate] = []
    problems: list[str] = []
    for candidate in candidates:
        candidate_problems = candidate.violations()
        missing = [state for state in candidate.prerequisites if state not in available]
        if missing:
            candidate_problems.append(
                f"{candidate.hypothesis_id}: PREREQUISITES_UNSATISFIED:{','.join(missing)}")
        if candidate_problems:
            refused.append(candidate)
            problems.extend(candidate_problems)
            continue
        ranked.append(candidate)
    ranked.sort(key=lambda item: (-(item.score or 0.0), item.hypothesis_id))
    return PriorityRanking(ranking_id, tuple(ranked), tuple(refused),
                           tuple(sorted(set(problems))))
