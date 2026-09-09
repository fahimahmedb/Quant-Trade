"""F13 — prévision de mise en place (docs/feature-plans/ia-f10-f19.md §4,
cible SYN-A pour AC-F13-2). Aucun jeu SYN dédié : le document pointe
directement SYN-A (Lot IA-0) pour la précision de la prévision.

`as_of` fixe « aujourd'hui » pour chaque test (mardi 3 mars 2026, dans la
fenêtre de ventes de SYN-A) : le lendemain (mercredi) est un jour ouvert
normal pour la plupart des tests, sauf ceux qui testent explicitement un
jour de fermeture.
"""
from datetime import date

from app import models
from app.services import ai_forecast, ai_production_forecast as prod, settings_service
from tests import synthetic_data as syn

TODAY = date(2026, 3, 3)  # mardi -> lendemain mercredi (ouvert)
TODAY_BEFORE_CLOSED_DAY = date(2026, 3, 1)  # dimanche -> lendemain lundi (fermé)


def _enable(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f6_enabled = True
    settings.feature_f13_enabled = True
    db.commit()


def _syn_a_prepared(db_session, *, stock: float = 0.0, shelf_life_days: float | None = None):
    result = syn.build_syn_a(db_session, seed=1, weeks=12)
    result.ingredient.is_prepared_in_house = True
    result.ingredient.current_theoretical_stock = stock
    result.ingredient.shelf_life_days = shelf_life_days
    db_session.commit()
    return result


def test_f13_is_inert_by_default(db_session):
    result = _syn_a_prepared(db_session)
    settings_service.get_settings(db_session)
    settings = db_session.get(models.Settings, 1)
    settings.feature_f6_enabled = True
    db_session.commit()  # F13 lui-même reste éteint

    out = prod.forecast_production(db_session, result.ingredient.id, as_of=TODAY)

    assert not out.ok and "désactivée" in out.message


# ==========================================================================
# AC-F13-1 — aucun ingrédient marqué -> invisible
# ==========================================================================

def test_ac_f13_1_unmarked_ingredient_stays_invisible(db_session):
    result = syn.build_syn_a(db_session, seed=1, weeks=12)  # jamais marqué "préparé en interne"
    _enable(db_session)

    out = prod.forecast_production(db_session, result.ingredient.id, as_of=TODAY)

    assert not out.ok
    assert "préparé en interne" in out.message


def test_gate_reuses_f6_own_gate_not_a_redefined_one(db_session):
    """Non-vacuité : aucun des autres tests (tous sur SYN-A, 12 semaines,
    largement au-dessus du gate F6) ne distinguerait un code qui réutilise
    le gate de weekday_forecast d'un code qui l'ignorerait — seul un
    historique insuffisant le prouve."""
    result = syn.build_syn_a(db_session, seed=1, weeks=2)  # sous les 6 semaines requises par F6
    result.ingredient.is_prepared_in_house = True
    db_session.commit()
    _enable(db_session)

    out = prod.forecast_production(db_session, result.ingredient.id, as_of=TODAY)

    assert not out.ok
    assert "semaine" in out.message


# ==========================================================================
# AC-F13-2 — sur SYN-A, quantité prévue = consommation attendue ±10%
# ==========================================================================

def test_ac_f13_2_forecast_matches_expected_consumption_on_syn_a(db_session):
    """Stock mis à 0 pour isoler la précision de la prévision elle-même
    de la déduction du stock (AC-F13-3, testée séparément) : SYN-A part
    d'un stock de départ énorme (10 000 000, marge pour 12 semaines de
    ventes) qui masquerait toute quantité suggérée si on le laissait tel
    quel — pas réaliste pour un reste de préparation, qui est une petite
    quantité concrète."""
    result = _syn_a_prepared(db_session, stock=0.0)
    _enable(db_session)

    out = prod.forecast_production(db_session, result.ingredient.id, as_of=TODAY)

    assert out.ok, out.message
    reference = ai_forecast.weekday_forecast(db_session, result.ingredient.id)
    attendu_demain = reference.forecast.expected_daily_qty[2]  # mercredi
    assert abs(out.expected_consumption - attendu_demain) <= 0.10 * attendu_demain
    assert abs(out.suggested_quantity - attendu_demain) <= 0.10 * attendu_demain


# ==========================================================================
# AC-F13-3 — stock de préparation existant déduit
# ==========================================================================

def test_ac_f13_3_existing_stock_is_deducted(db_session):
    result = _syn_a_prepared(db_session, stock=10.0)
    _enable(db_session)

    out = prod.forecast_production(db_session, result.ingredient.id, as_of=TODAY)

    assert out.ok, out.message
    assert out.current_stock == 10.0
    assert out.suggested_quantity == out.expected_consumption - 10.0


def test_ac_f13_3_enough_stock_means_no_suggested_production(db_session):
    """Non-vacuité par contre-exemple : un stock largement suffisant doit
    ramener la suggestion à 0, pas juste la réduire."""
    result = _syn_a_prepared(db_session, stock=1000.0)
    _enable(db_session)

    out = prod.forecast_production(db_session, result.ingredient.id, as_of=TODAY)

    assert out.ok, out.message
    assert out.suggested_quantity == 0.0


# ==========================================================================
# TC-F13-04 — jour de fermeture le lendemain -> aucune production
# ==========================================================================

def test_tc_f13_04_no_production_suggested_when_tomorrow_is_closed(db_session):
    result = _syn_a_prepared(db_session, stock=0.0)
    _enable(db_session)

    out = prod.forecast_production(db_session, result.ingredient.id, as_of=TODAY_BEFORE_CLOSED_DAY)

    assert out.ok, out.message
    assert out.expected_consumption == 0.0
    assert out.suggested_quantity == 0.0


# ==========================================================================
# TC-F13-05 — conservation de 3 jours -> production sur 3 jours, pas 1
# ==========================================================================

def test_tc_f13_05_three_day_shelf_life_covers_three_days(db_session):
    result = _syn_a_prepared(db_session, stock=0.0, shelf_life_days=3.0)
    _enable(db_session)

    out = prod.forecast_production(db_session, result.ingredient.id, as_of=TODAY)

    assert out.ok, out.message
    assert out.window_days == 3
    reference = ai_forecast.weekday_forecast(db_session, result.ingredient.id)
    attendu_3_jours = sum(reference.forecast.expected_daily_qty[wd] for wd in (2, 3, 4))  # mer/jeu/ven
    assert abs(out.expected_consumption - attendu_3_jours) < 0.01
    # Non-vacuité : la fenêtre de 3 jours doit vraiment dépasser 1 seul jour.
    un_seul_jour = reference.forecast.expected_daily_qty[2]
    assert out.expected_consumption > un_seul_jour * 2
