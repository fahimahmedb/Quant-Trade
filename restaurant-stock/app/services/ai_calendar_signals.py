"""F20 — signaux calendaires (Lot IA-2, docs/feature-plans/
backlog-lot-ia-2.md ticket 4, phase 1). F6 ne connaît que la
saisonnalité du jour de semaine ; ce module ajoute trois signaux
supplémentaires, chacun sans aucune dépendance externe :
jours fériés + vacances scolaires (`french_calendar.py`, calendrier
déterministe) et jours exceptionnels marqués manuellement
(`ExceptionalDay`) — ce dernier referme l'écran « marquage journée
exceptionnelle » resté non construit depuis le Lot IA-0
(docs/bilan-ia-0.md, item F6).

Un signal actif est un FACTEUR MULTIPLICATIF sur l'estimation F6 du jour
de semaine, mesuré EMPIRIQUEMENT sur les occurrences passées de ce MÊME
signal — jamais un effet fixe deviné (« -20 % un jour férié » n'a de
sens pour aucun restaurant en particulier). Moins de 3 occurrences
passées : aucun facteur appliqué, l'estimation F6 seule reste la sortie
(dégradation silencieuse, même principe que partout ailleurs dans le
projet).

Priorité entre signaux quand plusieurs sont actifs le même jour (le
document ne tranche pas ce cas — décision purement technique actée ici,
backlog §1 règle 4) : EXCEPTIONNEL (signal le plus spécifique, saisi par
le restaurateur pour CE restaurant précis) > FÉRIÉ (un jour précis,
récurrent chaque année) > VACANCES scolaires (la catégorie la plus
large, plusieurs semaines). Un seul facteur appliqué à la fois, jamais
un cumul multiplicatif de plusieurs signaux sur un aussi petit
échantillon — cumuler amplifierait le bruit statistique plus que le
signal réel.

Réutilise `ai_forecast.weekday_forecast` et `ai_forecast.
ingredient_daily_consumption` (F6) tels quels — aucun second calcul de
prévision de base, cette fonction ne fait qu'ajuster sa sortie.
"""
from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from app import models
from app.services import ai_forecast, french_calendar, settings_service
from app.templating import pluriel

MIN_PAST_OCCURRENCES = 3  # backlog ticket 4 : « moins de 3 occurrences : aucun facteur appliqué »


@dataclass
class CalendarAdjustment:
    signal: str | None  # "exceptionnel" | "ferie" | "vacances" | None
    factor: float | None
    occurrences_used: int = 0


@dataclass
class AdjustedForecastResult:
    ok: bool
    message: str | None
    base_expected_qty: float | None = None
    adjustment: CalendarAdjustment | None = None
    adjusted_expected_qty: float | None = None
    explanation: str = ""


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f20_enabled


def mark_exceptional_day(db: Session, on_date: date, note: str | None = None) -> models.ExceptionalDay:
    """Indépendant du feature flag F20 (backlog ticket 4 : « le marquage
    manuel reste disponible même sans F20 actif ») : une saisie, jamais
    gatée par le calcul qui l'exploite ensuite."""
    existing = db.query(models.ExceptionalDay).filter_by(on_date=on_date).one_or_none()
    if existing is not None:
        existing.note = note
        db.commit()
        db.refresh(existing)
        return existing
    entry = models.ExceptionalDay(on_date=on_date, note=note)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def unmark_exceptional_day(db: Session, on_date: date) -> None:
    db.query(models.ExceptionalDay).filter_by(on_date=on_date).delete()
    db.commit()


def _signal_for_date(d: date, exceptional_dates: set[date], vacation_zone: str | None) -> str | None:
    """Priorité documentée dans le docstring du module : exceptionnel >
    férié > vacances. Un seul signal retenu, jamais un cumul."""
    if d in exceptional_dates:
        return "exceptionnel"
    if french_calendar.is_public_holiday(d):
        return "ferie"
    if french_calendar.is_school_vacation(d, vacation_zone):
        return "vacances"
    return None


def adjusted_forecast(db: Session, ingredient_id: int, target_date: date) -> AdjustedForecastResult:
    """backlog-lot-ia-2.md ticket 4."""
    if not _feature_enabled(db):
        return AdjustedForecastResult(ok=False, message="Fonctionnalité F20 désactivée (feature flag éteint).")

    outcome = ai_forecast.weekday_forecast(db, ingredient_id)
    if not outcome.gate_ok:
        return AdjustedForecastResult(ok=False, message=outcome.gate_message)

    base = outcome.forecast.expected_daily_qty.get(target_date.weekday())
    if base is None:
        return AdjustedForecastResult(
            ok=False, message="Jour de fermeture habituel pour cet ingrédient : aucune estimation de base.",
        )

    settings = settings_service.get_settings(db)
    exceptional_dates = {row.on_date for row in db.query(models.ExceptionalDay).all()}
    signal = _signal_for_date(target_date, exceptional_dates, settings.school_vacation_zone)

    if signal is None:
        return AdjustedForecastResult(
            ok=True, message=None, base_expected_qty=base,
            adjustment=CalendarAdjustment(signal=None, factor=None),
            adjusted_expected_qty=base,
            explanation=f"{base:g} attendus (jour ordinaire, aucun signal calendaire).",
        )

    daily = ai_forecast.ingredient_daily_consumption(db, ingredient_id)
    ratios: list[float] = []
    for past_date, actual in daily.items():
        if past_date >= target_date:
            continue
        if _signal_for_date(past_date, exceptional_dates, settings.school_vacation_zone) != signal:
            continue
        past_weekday_expected = outcome.forecast.expected_daily_qty.get(past_date.weekday())
        if not past_weekday_expected:
            continue
        ratios.append(actual / past_weekday_expected)

    if len(ratios) < MIN_PAST_OCCURRENCES:
        n = len(ratios)
        return AdjustedForecastResult(
            ok=True, message=None, base_expected_qty=base,
            adjustment=CalendarAdjustment(signal=signal, factor=None, occurrences_used=n),
            adjusted_expected_qty=base,
            explanation=(
                f"{base:g} attendus — signal « {signal} » détecté mais seulement {n} occurrence{pluriel(n)} "
                f"passée{pluriel(n)} connue{pluriel(n)} ({MIN_PAST_OCCURRENCES} nécessaires) : "
                "estimation habituelle conservée."
            ),
        )

    factor = sum(ratios) / len(ratios)
    adjusted = base * factor
    n = len(ratios)
    explanation = (
        f"{adjusted:g} attendus — {base:g} habituellement, ajusté ×{factor:.2f} pour un jour "
        f"« {signal} » ({n} occurrence{pluriel(n)} passée{pluriel(n)} mesurée{pluriel(n)})."
    )
    return AdjustedForecastResult(
        ok=True, message=None, base_expected_qty=base,
        adjustment=CalendarAdjustment(signal=signal, factor=factor, occurrences_used=n),
        adjusted_expected_qty=adjusted,
        explanation=explanation,
    )
