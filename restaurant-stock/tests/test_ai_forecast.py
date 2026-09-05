"""F6 — prévision par jour de semaine, en mode ombre (docs/IA scope.md
§1.2/1.7/1.10), prouvée sur SYN-A/E/F/I. Éteinte par défaut
(`Settings.feature_f6_enabled`) : un test dédié le prouve plutôt que de le
supposer.
"""
from app import models
from app.services import ai_forecast, settings_service
from tests import synthetic_data as syn


def _enable_f6(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f6_enabled = True
    db.commit()


def test_f6_is_inert_by_default(db_session):
    result = syn.build_syn_a(db_session, seed=1, weeks=12)
    forecast = ai_forecast.weekday_forecast(db_session, result.ingredient.id)
    assert not forecast.gate_ok
    assert "désactivée" in forecast.gate_message
    assert forecast.forecast is None


# ==========================================================================
# SYN-A — saisonnalité hebdomadaire retrouvée à ±10%, lundi exclu
# ==========================================================================

def test_syn_a_forecast_matches_injected_factors_within_tolerance(db_session):
    result = syn.build_syn_a(db_session, seed=1, weeks=12)
    _enable_f6(db_session)

    outcome = ai_forecast.weekday_forecast(db_session, result.ingredient.id)

    assert outcome.gate_ok, outcome.gate_message
    forecast = outcome.forecast
    assert forecast.closed_days == result.closed_days, "le lundi (fermé) doit être détecté et exclu"
    assert 0 not in forecast.expected_daily_qty, "aucune prévision ne doit être produite pour un jour fermé"

    for wd, facteur in result.day_factors.items():
        attendu = result.base_daily_qty * facteur
        obtenu = forecast.expected_daily_qty[wd]
        assert abs(obtenu - attendu) / attendu < 0.10, (
            f"jour {wd} : prévision {obtenu:.2f} hors de ±10% de l'attendu {attendu:.2f}"
        )


def test_syn_e_forecast_is_gated_under_six_weeks(db_session):
    result = syn.build_syn_e(db_session)
    _enable_f6(db_session)

    outcome = ai_forecast.weekday_forecast(db_session, result.ingredient.id)

    assert not outcome.gate_ok
    assert "6" in outcome.gate_message
    assert outcome.forecast is None


# ==========================================================================
# SYN-F — robustesse : un pic ×100 ne doit pas déplacer la prévision de plus de ±10%
# ==========================================================================

def test_syn_f_outlier_sale_does_not_move_forecast_more_than_ten_percent(db_session):
    result = syn.build_syn_f(db_session, seed=6, weeks=12)
    _enable_f6(db_session)

    propre = ai_forecast.weekday_forecast(db_session, result.clean.ingredient.id)
    avec_aberration = ai_forecast.weekday_forecast(db_session, result.ingredient.id)

    assert propre.gate_ok and avec_aberration.gate_ok
    jour_touche = result.outlier_sale_date.weekday()
    valeur_propre = propre.forecast.expected_daily_qty[jour_touche]
    valeur_bruitee = avec_aberration.forecast.expected_daily_qty[jour_touche]
    ecart = abs(valeur_bruitee - valeur_propre) / valeur_propre
    assert ecart < 0.10, f"la vente x100 a déplacé la prévision de {ecart:.0%}, au-delà de ±10%"


def test_syn_f_outlier_is_an_extreme_multiple_of_the_normal_day(db_session):
    """Vérifie que le test ci-dessus prouve bien quelque chose : l'aberration
    injectée doit être un pic massif brut, sinon "ne pas bouger de ±10%"
    serait trivialement vrai même sans médiane robuste."""
    result = syn.build_syn_f(db_session, seed=6, weeks=12)
    lignes = (
        db_session.query(models.SaleLine)
        .filter(models.SaleLine.dish_id == result.dish.id, models.SaleLine.sale_date == result.outlier_sale_date)
        .all()
    )
    assert len(lignes) == 1
    normal_estime = result.clean.base_daily_qty * result.day_factors[result.outlier_sale_date.weekday()]
    assert lignes[0].quantity_sold > normal_estime * 50


# ==========================================================================
# SYN-I — cold start : historique partiel signalé, jamais extrapolé
# ==========================================================================

def test_syn_i_forecast_keeps_working_at_ingredient_level(db_session):
    result = syn.build_syn_i(db_session)
    _enable_f6(db_session)

    outcome = ai_forecast.weekday_forecast(db_session, result.ingredient.id)

    assert outcome.gate_ok, outcome.gate_message
    assert outcome.forecast.expected_daily_qty, "la prévision doit fonctionner malgré le nouveau plat"


def test_syn_i_new_dish_is_flagged_as_partial_history_not_extrapolated(db_session):
    result = syn.build_syn_i(db_session)
    _enable_f6(db_session)

    outcome = ai_forecast.weekday_forecast(db_session, result.ingredient.id)

    partiels = {p.dish_id: p for p in outcome.forecast.partial_dishes}
    assert result.dish_new.id in partiels, "le nouveau plat doit être signalé comme historique partiel"
    assert result.dish_existing.id not in partiels, "le plat ancien couvre toute la fenêtre, pas partiel"

    premiere_vente_reelle = (
        db_session.query(models.SaleLine)
        .filter_by(dish_id=result.dish_new.id)
        .order_by(models.SaleLine.sale_date)
        .first()
    )
    assert partiels[result.dish_new.id].first_sale_on == premiere_vente_reelle.sale_date.date()

    # Aucune extrapolation silencieuse : les ventes du nouveau plat ne
    # doivent exister que depuis sa semaine d'introduction, pas avant.
    ventes_avant_introduction = (
        db_session.query(models.SaleLine)
        .filter(
            models.SaleLine.dish_id == result.dish_new.id,
            models.SaleLine.sale_date < premiere_vente_reelle.sale_date,
        )
        .count()
    )
    assert ventes_avant_introduction == 0
