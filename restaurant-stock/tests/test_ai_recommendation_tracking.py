"""F25 — indicateur de confiance étendu à toutes les recommandations IA
(docs/feature-plans/backlog-lot-ia-2.md ticket 3, cible SYN-T).
"""
from app import models
from app.services import ai_production_forecast, ai_recommendation_tracking as track, settings_service
from tests import synthetic_data as syn


def _enable(db, *, f25=True, f13=True, f6=True):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    if f6:
        settings.feature_f6_enabled = True
    if f13:
        settings.feature_f13_enabled = True
    if f25:
        settings.feature_f25_enabled = True
    db.commit()


def _add_order_suggestion(db, *, decision: models.SuggestionDecision, index: int) -> models.OrderSuggestionLine:
    """Ligne F7 minimale, insérée directement (aucune logique métier à
    exercer ici) : sert uniquement à prouver que les statistiques F7/F13
    restent indépendantes (test de non-régression croisée)."""
    batch = models.OrderSuggestionBatch()
    db.add(batch)
    db.flush()
    ing = syn.ingredient(db, f"Ingrédient F7 {decision.value} {index}", unit_cost=0.1)
    line = models.OrderSuggestionLine(
        batch_id=batch.id, ingredient_id=ing.id, current_stock=10.0,
        avg_daily_consumption=1.0, threshold_used=2.0, suggested_quantity=5.0,
        decision=decision,
    )
    db.add(line)
    db.commit()
    return line


def test_f25_is_inert_by_default(db_session):
    result = syn.build_syn_t(db_session)
    _enable(db_session, f25=False)

    suggestion = track.record_production_suggestion(db_session, result.ingredient.id)
    stats = track.adoption_stats_by_feature(db_session)

    assert suggestion is None
    assert "F13" not in stats
    assert "F7" in stats


def test_no_suggestion_when_f13_itself_is_inactive(db_session):
    """Non-vacuité par contre-exemple : F25 actif, mais F13 (la
    fonctionnalité qu'il journalise) ne l'est pas — isole le gate de F25
    de celui de F13."""
    result = syn.build_syn_t(db_session)
    _enable(db_session, f25=True, f13=False)

    suggestion = track.record_production_suggestion(db_session, result.ingredient.id)

    assert suggestion is None


def test_suggestion_matches_the_actual_f13_forecast(db_session):
    result = syn.build_syn_t(db_session)
    _enable(db_session)
    reference = ai_production_forecast.forecast_production(db_session, result.ingredient.id)
    assert reference.ok, reference.message  # sinon ce test ne prouve rien

    suggestion = track.record_production_suggestion(db_session, result.ingredient.id)

    assert suggestion is not None
    assert suggestion.suggested_quantity == reference.suggested_quantity
    assert suggestion.window_days == reference.window_days
    assert suggestion.decision == models.SuggestionDecision.EN_ATTENTE
    assert suggestion.validated_at is None


def test_record_decision_updates_the_suggestion(db_session):
    result = syn.build_syn_t(db_session)
    _enable(db_session)
    suggestion = track.record_production_suggestion(db_session, result.ingredient.id)

    updated = track.record_decision(
        db_session, suggestion.id, decision=models.SuggestionDecision.MODIFIEE, final_quantity=12.5,
    )

    assert updated.decision == models.SuggestionDecision.MODIFIEE
    assert updated.final_quantity == 12.5
    assert updated.validated_at is not None


def test_adoption_stats_by_feature_counts_correctly(db_session):
    result = syn.build_syn_t(db_session)
    _enable(db_session)

    suggestions = [track.record_production_suggestion(db_session, result.ingredient.id) for _ in range(5)]
    track.record_decision(db_session, suggestions[0].id, decision=models.SuggestionDecision.ACCEPTEE, final_quantity=suggestions[0].suggested_quantity)
    track.record_decision(db_session, suggestions[1].id, decision=models.SuggestionDecision.ACCEPTEE, final_quantity=suggestions[1].suggested_quantity)
    track.record_decision(db_session, suggestions[2].id, decision=models.SuggestionDecision.MODIFIEE, final_quantity=suggestions[2].suggested_quantity + 5)
    track.record_decision(db_session, suggestions[3].id, decision=models.SuggestionDecision.MODIFIEE, final_quantity=suggestions[3].suggested_quantity - 2)
    track.record_decision(db_session, suggestions[4].id, decision=models.SuggestionDecision.REJETEE)

    stats = track.adoption_stats_by_feature(db_session)["F13"]

    assert stats.total == 5
    assert stats.acceptee == 2
    assert stats.modifiee == 2
    assert stats.rejetee == 1
    assert stats.en_attente == 0


def test_f7_and_f13_stats_stay_independent(db_session):
    """Non-vacuité par contre-exemple : des décisions F7 ET F13
    simultanées, en proportions DIFFÉRENTES, ne doivent jamais se
    mélanger dans les totaux de l'autre fonctionnalité."""
    result = syn.build_syn_t(db_session)
    _enable(db_session)

    for i in range(3):
        _add_order_suggestion(db_session, decision=models.SuggestionDecision.REJETEE, index=i)
    suggestion = track.record_production_suggestion(db_session, result.ingredient.id)
    track.record_decision(db_session, suggestion.id, decision=models.SuggestionDecision.ACCEPTEE, final_quantity=suggestion.suggested_quantity)

    stats = track.adoption_stats_by_feature(db_session)

    assert stats["F7"].total == 3 and stats["F7"].rejetee == 3 and stats["F7"].acceptee == 0
    assert stats["F13"].total == 1 and stats["F13"].acceptee == 1 and stats["F13"].rejetee == 0
