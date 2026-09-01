from datetime import datetime, timedelta

from app import models
from app.services import counting, metrics


def _ingredient(db_session, name, stock, unit_cost=0.02):
    ing = models.Ingredient(
        name=name, unit=models.Unit.GRAMME, unit_cost=unit_cost, current_theoretical_stock=stock
    )
    db_session.add(ing)
    db_session.commit()
    return ing


def test_suggestion_adoption_stats_counts_by_decision(db_session):
    ing = _ingredient(db_session, "Tomate", 100)
    batch = models.OrderSuggestionBatch()
    db_session.add(batch)
    db_session.flush()
    db_session.add_all(
        [
            models.OrderSuggestionLine(
                batch_id=batch.id,
                ingredient_id=ing.id,
                current_stock=1,
                avg_daily_consumption=1,
                threshold_used=1,
                suggested_quantity=1,
                decision=models.SuggestionDecision.ACCEPTEE,
            ),
            models.OrderSuggestionLine(
                batch_id=batch.id,
                ingredient_id=ing.id,
                current_stock=1,
                avg_daily_consumption=1,
                threshold_used=1,
                suggested_quantity=1,
                decision=models.SuggestionDecision.MODIFIEE,
            ),
            models.OrderSuggestionLine(
                batch_id=batch.id,
                ingredient_id=ing.id,
                current_stock=1,
                avg_daily_consumption=1,
                threshold_used=1,
                suggested_quantity=1,
                decision=models.SuggestionDecision.EN_ATTENTE,
            ),
        ]
    )
    db_session.commit()

    stats = metrics.suggestion_adoption_stats(db_session)

    assert stats.total == 3
    assert stats.acceptee == 1
    assert stats.modifiee == 1
    assert stats.en_attente == 1
    assert stats.decided == 2  # en_attente exclu du taux d'adoption
    assert stats.pct(stats.acceptee) == 50.0


def test_counting_duration_stats_averages_completed_sessions(db_session):
    _ingredient(db_session, "Riz", 1000)
    session = counting.start_count_session(db_session)
    counting.confirm_count_line(db_session, session.lines[0].id, counted_quantity=900)
    completed = counting.complete_count_session(db_session, session.id)
    # On force des horodatages connus pour un calcul de durée déterministe.
    completed.started_at = datetime(2026, 1, 1, 8, 0, 0)
    completed.ended_at = datetime(2026, 1, 1, 8, 10, 0)
    db_session.commit()

    stats = metrics.counting_duration_stats(db_session)

    assert stats.average_seconds == 600
    assert stats.sessions[0]["session_id"] == session.id


def test_variance_trend_only_includes_completed_sessions(db_session):
    ing = _ingredient(db_session, "Riz", 1000, unit_cost=0.01)
    open_session = counting.start_count_session(db_session)
    counting.confirm_count_line(db_session, open_session.lines[0].id, counted_quantity=900)
    # Session jamais complétée : ne doit pas apparaître dans le trend.
    assert metrics.variance_trend(db_session) == []

    completed = counting.complete_count_session(db_session, open_session.id)

    trend = metrics.variance_trend(db_session)
    assert len(trend) == 1
    assert trend[0].session_id == completed.id
    # écart 1000-900=100 (déjà recalibré à 900 mais la ligne garde la valeur saisie)
    assert trend[0].total_variance_value == 100 * ing.unit_cost
