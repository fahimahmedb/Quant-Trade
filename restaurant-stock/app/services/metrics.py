"""Indicateurs à instrumenter dès la v1 (section 8 du brief).

Pas de tableau de bord sophistiqué : ces agrégats simples suffisent à
constituer la preuve pour le premier pilote.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app import models


@dataclass
class VariancePoint:
    session_id: int
    ended_at: object
    total_variance_value: float
    total_absolute_variance_value: float
    line_count: int


def variance_trend(db: Session) -> list[VariancePoint]:
    sessions = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.isnot(None))
        .order_by(models.CountSession.ended_at)
        .all()
    )
    points = []
    for session in sessions:
        counted = [line for line in session.lines if line.counted_quantity is not None]
        total = sum(line.variance_value or 0 for line in counted)
        total_abs = sum(abs(line.variance_value or 0) for line in counted)
        points.append(
            VariancePoint(
                session_id=session.id,
                ended_at=session.ended_at,
                total_variance_value=total,
                total_absolute_variance_value=total_abs,
                line_count=len(counted),
            )
        )
    return points


@dataclass
class AdoptionStats:
    total: int
    acceptee: int
    modifiee: int
    rejetee: int
    en_attente: int

    @property
    def decided(self) -> int:
        return self.acceptee + self.modifiee + self.rejetee

    def pct(self, count: int) -> float:
        return (count / self.decided * 100) if self.decided else 0.0


def suggestion_adoption_stats(db: Session) -> AdoptionStats:
    lines = db.query(models.OrderSuggestionLine).all()
    counts = {decision: 0 for decision in models.SuggestionDecision}
    for line in lines:
        counts[line.decision] += 1
    return AdoptionStats(
        total=len(lines),
        acceptee=counts[models.SuggestionDecision.ACCEPTEE],
        modifiee=counts[models.SuggestionDecision.MODIFIEE],
        rejetee=counts[models.SuggestionDecision.REJETEE],
        en_attente=counts[models.SuggestionDecision.EN_ATTENTE],
    )


@dataclass
class CountDurationStats:
    sessions: list[dict]
    average_seconds: float | None


def counting_duration_stats(db: Session) -> CountDurationStats:
    sessions = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.isnot(None))
        .order_by(models.CountSession.ended_at.desc())
        .all()
    )
    rows = [
        {
            "session_id": s.id,
            "started_at": s.started_at,
            "ended_at": s.ended_at,
            "duration_seconds": s.duration_seconds,
            "counted_by": s.counted_by,
        }
        for s in sessions
    ]
    durations = [r["duration_seconds"] for r in rows if r["duration_seconds"] is not None]
    average = sum(durations) / len(durations) if durations else None
    return CountDurationStats(sessions=rows, average_seconds=average)
