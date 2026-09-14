"""Outcome-blind event geometry metrics."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Mapping, Sequence

from .experiments import EventRecord, ExperimentError


@dataclass(frozen=True)
class OverlapGeometry:
    horizon_sessions: int
    overlapping_pairs: int
    events_with_any_overlap: int
    max_concurrent_windows: int


@dataclass(frozen=True)
class ClusterGeometry:
    window_sessions: int
    cluster_count: int
    multi_event_cluster_count: int
    cluster_size_distribution: dict[int, int]
    max_cluster_size: int


@dataclass(frozen=True)
class GeometryReport:
    n: int
    annual_distribution: dict[int, int]
    events_per_issuer: dict[str, int]
    hhi: float
    effective_issuers: float
    overlap: OverlapGeometry
    clusters: ClusterGeometry


class GeometryEngine:
    """Compute sample structure from events and a price-free session ordinal map."""

    def __init__(self, overlap_sessions: int = 20, cluster_sessions: int = 10) -> None:
        if overlap_sessions <= 0 or cluster_sessions < 0:
            raise ExperimentError("geometry windows must be positive/non-negative")
        self.overlap_sessions = overlap_sessions
        self.cluster_sessions = cluster_sessions

    def analyze(self, events: Sequence[EventRecord], session_ordinals: Mapping[str, int]) -> GeometryReport:
        ids = [event.event_id for event in events]
        if len(ids) != len(set(ids)):
            raise ExperimentError("event_id must be unique")
        missing = sorted({event.formation_date for event in events if event.formation_date not in session_ordinals})
        if missing:
            raise ExperimentError(f"missing session ordinals for {missing[:3]}")
        annual = Counter(int(event.formation_date[:4]) for event in events)
        issuer_counts = Counter(event.issuer_id for event in events)
        n = len(events)
        hhi = 0.0 if n == 0 else sum((count / n) ** 2 for count in issuer_counts.values())
        effective = 0.0 if hhi == 0.0 else 1.0 / hhi
        return GeometryReport(
            n=n,
            annual_distribution=dict(sorted(annual.items())),
            events_per_issuer=dict(sorted(issuer_counts.items())),
            hhi=hhi,
            effective_issuers=effective,
            overlap=self._overlap(events, session_ordinals),
            clusters=self._clusters(events, session_ordinals),
        )

    def _overlap(self, events: Sequence[EventRecord], ordinals: Mapping[str, int]) -> OverlapGeometry:
        ordered = sorted((ordinals[event.formation_date], event.event_id) for event in events)
        active: deque[tuple[int, str]] = deque()
        pairs = 0
        overlapped_ids: set[str] = set()
        max_concurrent = 0
        for session, event_id in ordered:
            while active and session - active[0][0] >= self.overlap_sessions:
                active.popleft()
            if active:
                pairs += len(active)
                overlapped_ids.add(event_id)
                overlapped_ids.update(prior_id for _, prior_id in active)
            active.append((session, event_id))
            max_concurrent = max(max_concurrent, len(active))
        return OverlapGeometry(self.overlap_sessions, pairs, len(overlapped_ids), max_concurrent)

    def _clusters(self, events: Sequence[EventRecord], ordinals: Mapping[str, int]) -> ClusterGeometry:
        by_issuer: dict[str, list[int]] = defaultdict(list)
        for event in events:
            by_issuer[event.issuer_id].append(ordinals[event.formation_date])
        sizes: list[int] = []
        for sessions in by_issuer.values():
            sessions.sort()
            i = 0
            while i < len(sessions):
                anchor = sessions[i]
                j = i + 1
                while j < len(sessions) and sessions[j] - anchor <= self.cluster_sessions:
                    j += 1
                sizes.append(j - i)
                i = j
        distribution = Counter(sizes)
        return ClusterGeometry(
            self.cluster_sessions,
            len(sizes),
            sum(count for size, count in distribution.items() if size >= 2),
            dict(sorted(distribution.items())),
            max(sizes, default=0),
        )