from datetime import datetime, timedelta

from app import models
from app.services import ordering, settings_service


def _ingredient(db_session, name, current_stock, alert_threshold=None):
    ing = models.Ingredient(
        name=name,
        unit=models.Unit.GRAMME,
        unit_cost=0.02,
        current_theoretical_stock=current_stock,
        alert_threshold=alert_threshold,
    )
    db_session.add(ing)
    db_session.commit()
    return ing


def _record_sale_history(db_session, ingredient, quantity, days_ago):
    """Insère un mouvement de vente passé sans toucher au stock courant, pour
    piloter indépendamment le stock actuel et l'historique de consommation."""
    movement = models.StockMovement(
        ingredient_id=ingredient.id,
        movement_type=models.MovementType.VENTE,
        quantity_delta=-quantity,
        resulting_stock=ingredient.current_theoretical_stock,
        created_at=datetime.utcnow() - timedelta(days=days_ago),
    )
    db_session.add(movement)
    db_session.commit()


def test_rolling_average_only_counts_window(db_session):
    ing = _ingredient(db_session, "Tomate", current_stock=10000)
    _record_sale_history(db_session, ing, 700, days_ago=1)
    _record_sale_history(db_session, ing, 700, days_ago=3)
    _record_sale_history(db_session, ing, 700, days_ago=10)  # hors fenêtre de 7 jours

    avg = ordering.rolling_avg_daily_consumption(db_session, ing.id, window_days=7)

    assert avg == (700 + 700) / 7


def test_generate_suggestions_triggers_below_derived_threshold(db_session):
    ing = _ingredient(db_session, "Tomate", current_stock=100)
    for day in range(7):
        _record_sale_history(db_session, ing, 700, days_ago=day)
    # conso moyenne = 700/jour ; seuil dérivé = 700 * safety_days(2) = 1400 > stock(100)
    settings_service.update_settings(
        db_session, safety_days=2, target_days=5, rolling_window_days=7
    )

    batch = ordering.generate_suggestions(db_session)

    assert len(batch.lines) == 1
    line = batch.lines[0]
    assert line.ingredient_id == ing.id
    assert line.avg_daily_consumption == 700
    assert line.threshold_used == 1400
    # cible = 700 * 5 = 3500 ; suggestion = 3500 - 100 = 3400
    assert line.suggested_quantity == 3400


def test_generate_suggestions_skips_ingredient_above_threshold(db_session):
    ing = _ingredient(db_session, "Sel", current_stock=5000)
    _record_sale_history(db_session, ing, 10, days_ago=1)  # conso très faible

    batch = ordering.generate_suggestions(db_session)

    assert batch.lines == []


def test_manual_alert_threshold_overrides_derived_one(db_session):
    ing = _ingredient(db_session, "Vin rouge", current_stock=8, alert_threshold=10)
    # Pas d'historique de vente : la moyenne dérivée serait 0, mais le seuil
    # manuel du gérant doit quand même déclencher la suggestion.
    batch = ordering.generate_suggestions(db_session)

    assert len(batch.lines) == 1
    line = batch.lines[0]
    assert line.threshold_used == 10
    # cible = max(0 * target_days, seuil=10) = 10 ; suggestion = 10 - 8 = 2
    assert line.suggested_quantity == 2


def test_decide_suggestion_line_records_manager_choice(db_session):
    _ingredient(db_session, "Vin rouge", current_stock=8, alert_threshold=10)
    batch = ordering.generate_suggestions(db_session)
    line = batch.lines[0]

    updated = ordering.decide_suggestion_line(
        db_session, line.id, final_quantity=5, decision=models.SuggestionDecision.MODIFIEE
    )

    assert updated.final_quantity == 5
    assert updated.decision == models.SuggestionDecision.MODIFIEE
    assert updated.validated_at is not None
