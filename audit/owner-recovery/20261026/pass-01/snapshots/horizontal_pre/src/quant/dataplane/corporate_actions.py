"""Vendor-neutral point-in-time corporate-action contracts.

Events are expressed in stable issuer/security ids, never ticker text. A caller
must distinguish when an event became knowable (``knowledge_at``) from when it
took economic/legal effect (``effective_at``), which prevents a historical
replay from silently importing future corporate-action knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .identity import IdentityBook, parse_pit_instant, validate_evidence_hash


ACTION_TYPES = ("NAME_CHANGE", "MERGER", "SPLIT", "SPIN_OFF", "DELISTING")
LEG_KINDS = ("CASH", "STOCK", "SPIN")


@dataclass(frozen=True)
class CorporateActionLeg:
    """One consideration/distribution leg per source share."""

    kind: str
    target_security_id: str | None = None
    units_per_source_share: float | None = None
    cash_per_source_share: float | None = None
    currency: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in LEG_KINDS:
            raise ValueError(f"unknown corporate-action leg kind: {self.kind}")
        if self.kind == "CASH":
            if self.cash_per_source_share is None or self.cash_per_source_share <= 0:
                raise ValueError("CASH leg requires positive cash_per_source_share")
            if not self.currency:
                raise ValueError("CASH leg requires currency")
            if self.units_per_source_share is not None:
                raise ValueError("CASH leg cannot declare units_per_source_share")
        else:
            if not self.target_security_id:
                raise ValueError(f"{self.kind} leg requires target_security_id")
            if self.units_per_source_share is None or self.units_per_source_share <= 0:
                raise ValueError(f"{self.kind} leg requires positive units_per_source_share")
            if self.cash_per_source_share is not None:
                raise ValueError(f"{self.kind} leg cannot declare cash_per_source_share")


@dataclass(frozen=True)
class CorporateActionEvent:
    """Point-in-time corporate-action assertion with explicit evidence lineage."""

    event_id: str
    action_type: str
    knowledge_at: str
    effective_at: str
    evidence_hashes: tuple[str, ...]
    source_security_id: str | None = None
    issuer_id: str | None = None
    legs: tuple[CorporateActionLeg, ...] = ()
    split_ratio: float | None = None
    new_name: str | None = None
    delisting_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id is required")
        if self.action_type not in ACTION_TYPES:
            raise ValueError(f"unknown corporate-action type: {self.action_type}")
        parse_pit_instant(self.knowledge_at)
        parse_pit_instant(self.effective_at)
        if not self.evidence_hashes:
            raise ValueError("corporate actions require evidence lineage")
        for value in self.evidence_hashes:
            validate_evidence_hash(value)

        if self.action_type == "NAME_CHANGE":
            if not self.issuer_id or not self.new_name:
                raise ValueError("NAME_CHANGE requires issuer_id and new_name")
            if self.legs or self.split_ratio is not None:
                raise ValueError("NAME_CHANGE cannot carry consideration or split terms")
        elif self.action_type == "SPLIT":
            if not self.source_security_id:
                raise ValueError("SPLIT requires source_security_id")
            if self.split_ratio is None or self.split_ratio <= 0:
                raise ValueError("SPLIT requires positive split_ratio")
            if self.legs:
                raise ValueError("SPLIT uses split_ratio, not consideration legs")
        elif self.action_type == "MERGER":
            if not self.source_security_id or not self.legs:
                raise ValueError("MERGER requires source_security_id and consideration legs")
            if any(leg.kind == "SPIN" for leg in self.legs):
                raise ValueError("MERGER consideration may contain CASH/STOCK legs, not SPIN")
            if self.split_ratio is not None:
                raise ValueError("MERGER cannot declare split_ratio")
        elif self.action_type == "SPIN_OFF":
            if not self.source_security_id:
                raise ValueError("SPIN_OFF requires source_security_id")
            if not self.legs or any(leg.kind != "SPIN" for leg in self.legs):
                raise ValueError("SPIN_OFF requires one or more SPIN distribution legs")
            if self.split_ratio is not None:
                raise ValueError("SPIN_OFF cannot declare split_ratio")
        elif self.action_type == "DELISTING":
            if not self.source_security_id:
                raise ValueError("DELISTING requires source_security_id")
            if self.legs or self.split_ratio is not None:
                raise ValueError("DELISTING cannot carry consideration or split terms")

    def known_as_of(self, as_of: str) -> bool:
        return parse_pit_instant(self.knowledge_at) <= parse_pit_instant(as_of)

    def effective_as_of(self, as_of: str) -> bool:
        point = parse_pit_instant(as_of)
        return (parse_pit_instant(self.knowledge_at) <= point
                and parse_pit_instant(self.effective_at) <= point)


class CorporateActionBook:
    """PIT event queries over stable identities, with no ticker-based mapping."""

    def __init__(self, events: Iterable[CorporateActionEvent]):
        self.events = tuple(events)
        ids = [event.event_id for event in self.events]
        if len(ids) != len(set(ids)):
            raise ValueError("event_id must be unique")

    def known_as_of(self, as_of: str) -> tuple[CorporateActionEvent, ...]:
        parse_pit_instant(as_of)
        return tuple(sorted(
            (event for event in self.events if event.known_as_of(as_of)),
            key=lambda event: (event.knowledge_at, event.effective_at, event.event_id),
        ))

    def effective_as_of(self, as_of: str) -> tuple[CorporateActionEvent, ...]:
        parse_pit_instant(as_of)
        return tuple(sorted(
            (event for event in self.events if event.effective_as_of(as_of)),
            key=lambda event: (event.effective_at, event.event_id),
        ))

    def events_for_security(
        self,
        security_id: str,
        *,
        known_as_of: str,
    ) -> tuple[CorporateActionEvent, ...]:
        """Return only events knowable by ``known_as_of`` touching this stable id."""
        candidates = []
        for event in self.known_as_of(known_as_of):
            targets = {leg.target_security_id for leg in event.legs if leg.target_security_id}
            if event.source_security_id == security_id or security_id in targets:
                candidates.append(event)
        return tuple(candidates)

    def validate_identity_links(self, identities: IdentityBook) -> None:
        """Fail loudly when an event references an undeclared stable identity."""
        for event in self.events:
            if event.issuer_id and not identities.has_issuer_id(event.issuer_id):
                raise ValueError(
                    f"event {event.event_id} references unknown issuer {event.issuer_id}")
            if (event.source_security_id
                    and not identities.has_security_id(event.source_security_id)):
                raise ValueError(
                    f"event {event.event_id} references unknown security "
                    f"{event.source_security_id}")
            for leg in event.legs:
                if (leg.target_security_id
                        and not identities.has_security_id(leg.target_security_id)):
                    raise ValueError(
                        f"event {event.event_id} references unknown target security "
                        f"{leg.target_security_id}")

    def lineage_hashes(self) -> tuple[str, ...]:
        return tuple(sorted({value for event in self.events for value in event.evidence_hashes}))
