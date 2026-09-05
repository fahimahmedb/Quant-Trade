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


# ==========================================================================
# Signalé sur les captures du second correctif V1.2 : une ligne « en
# attente » gardait le stock du moment de la GÉNÉRATION du lot, jamais
# resynchronisé avec un comptage terminé depuis (qui recale le stock
# théorique sans jamais toucher les lignes déjà générées). Une suggestion
# affichée pouvait donc sous-estimer un manque réel — l'inverse de ce que
# l'outil doit éviter.
# ==========================================================================
def test_refresh_pending_line_updates_stale_current_stock_and_suggested_quantity(db_session):
    ing = _ingredient(db_session, "Beurre", current_stock=728)
    _record_sale_history(db_session, ing, 3290, days_ago=3)  # 470 g/jour sur 7 jours
    settings_service.update_settings(
        db_session, safety_days=2, target_days=5, rolling_window_days=7
    )
    batch = ordering.generate_suggestions(db_session)
    line = batch.lines[0]
    assert line.current_stock == 728
    ancienne_suggestion = line.suggested_quantity

    # Un comptage termine après la génération : le stock théorique est
    # recalé à la baisse (perte constatée), la ligne en attente ne le sait
    # pas encore tant qu'elle n'a pas été rafraîchie.
    ing.current_theoretical_stock = 677.04
    db_session.commit()

    refreshed = ordering.refresh_pending_line(db_session, line)

    assert refreshed.current_stock == 677.04, "le stock affiché doit être celui d'après recalage"
    assert refreshed.suggested_quantity > ancienne_suggestion, (
        "un manque plus important après recalage doit augmenter la quantité suggérée, "
        "pas la laisser sous-estimée"
    )


def test_refresh_pending_line_zeroes_out_a_shortage_resolved_since_generation(db_session):
    ing = _ingredient(db_session, "Vin rouge", current_stock=8, alert_threshold=10)
    batch = ordering.generate_suggestions(db_session)
    line = batch.lines[0]
    assert line.suggested_quantity == 2

    # Le comptage trouve finalement plus de stock que prévu : le manque a disparu.
    ing.current_theoretical_stock = 15
    db_session.commit()

    refreshed = ordering.refresh_pending_line(db_session, line)

    assert refreshed.suggested_quantity == 0, (
        "un manque résolu par le recalage ne doit plus suggérer de commander"
    )


def test_refresh_pending_line_never_touches_an_already_decided_line(db_session):
    ing = _ingredient(db_session, "Vin rouge", current_stock=8, alert_threshold=10)
    batch = ordering.generate_suggestions(db_session)
    line = batch.lines[0]
    ordering.decide_suggestion_line(
        db_session, line.id, final_quantity=2, decision=models.SuggestionDecision.ACCEPTEE
    )

    ing.current_theoretical_stock = 100  # le manque a disparu depuis la décision
    db_session.commit()

    unchanged = ordering.refresh_pending_line(db_session, line)

    assert unchanged.current_stock == 8, (
        "une décision déjà validée est un fait historique, pas une suggestion à corriger après coup"
    )
    assert unchanged.suggested_quantity == 2
    assert unchanged.final_quantity == 2


def test_orders_screen_shows_post_count_stock_not_the_stale_generation_time_value(seeded_client):
    """Reproduction bout en bout du scénario signalé : un lot de suggestions
    généré, puis un comptage qui recale le stock à la baisse — l'écran
    /orders/{id} doit refléter le nouveau stock au prochain affichage, pas
    celui d'avant le comptage."""
    from app.services import counting

    client, sessions = seeded_client.client, seeded_client.session_factory
    with sessions() as db:
        settings_service.update_settings(
            db, safety_days=2, target_days=5, rolling_window_days=7
        )
        beurre = _ingredient(db, "Beurre", current_stock=728)
        _record_sale_history(db, beurre, 3290, days_ago=3)
        batch = ordering.generate_suggestions(db)
        batch_id = batch.id

        session = counting.start_count_session(db, counted_by="Test")
        ligne_beurre = next(l for l in session.lines if l.ingredient.name == "Beurre")
        counting.confirm_count_line(db, ligne_beurre.id, counted_quantity=677.04)
        for l in session.lines:
            if l.id != ligne_beurre.id:
                counting.confirm_count_line(db, l.id, counted_quantity=l.theoretical_quantity)
        counting.complete_count_session(db, session.id)

    page = client.get(f"/orders/{batch_id}").text
    assert "il reste 677,04 g" in page, "l'écran affiche encore le stock d'avant comptage"
    assert "il reste 728 g" not in page, "l'ancien stock, périmé depuis le comptage, ne doit plus apparaître"
