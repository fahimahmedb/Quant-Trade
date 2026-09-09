"""F14 — risque de péremption (docs/feature-plans/ia-f10-f19.md §5),
prouvée sur SYN-M. Éteinte par défaut (`Settings.feature_f14_enabled`).
"""
from datetime import datetime, timedelta

from app import models
from app.services import ai_expiry_risk, deliveries, settings_service
from tests import synthetic_data as syn


def _enable_f14(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f14_enabled = True
    db.commit()


def test_f14_is_inert_by_default(db_session):
    result = syn.build_syn_m(db_session)
    outcome = ai_expiry_risk.assess_expiry_risk(db_session, result.ingredient.id)
    assert not outcome.ok
    assert "désactivée" in outcome.message


# ==========================================================================
# AC-F14-1 — sans conservation renseignée, silencieux
# ==========================================================================

def test_ac_f14_1_no_shelf_life_is_silent(db_session):
    ing = syn.ingredient(db_session, "Ingrédient sans conservation", stock_qty=100.0)
    _enable_f14(db_session)

    outcome = ai_expiry_risk.assess_expiry_risk(db_session, ing.id)

    assert not outcome.ok
    assert "conservation" in outcome.message.lower()
    assert not outcome.at_risk


# ==========================================================================
# AC-F14-2 / AC-F14-3 — SYN-M, frontière exacte et montant en euros exact
# ==========================================================================

def test_syn_m_stock_above_threshold_is_at_risk_with_exact_value(db_session):
    result = syn.build_syn_m(db_session)
    result.ingredient.current_theoretical_stock = result.stock_at_risk
    result.ingredient.shelf_life_days = result.shelf_life_days
    db_session.commit()
    _enable_f14(db_session)

    outcome = ai_expiry_risk.assess_expiry_risk(db_session, result.ingredient.id)

    assert outcome.ok, outcome.message
    assert outcome.at_risk
    assert abs(outcome.daily_consumption - result.daily_consumption_g) / result.daily_consumption_g < 0.05
    # 12000 - 5*2000 = 2000 g en trop, x 0,003 €/g = 6,00 €.
    assert abs(outcome.remaining_at_shelf_life_end - 2000.0) < 100.0
    assert abs(outcome.value_at_risk - 6.0) < 0.5
    assert f"{outcome.value_at_risk:.2f}" in outcome.explanation


def test_syn_m_stock_below_threshold_is_never_at_risk(db_session):
    """Non-vacuité par contre-exemple : sans lui, un code qui répond
    toujours at_risk=True passerait quand même le test précédent."""
    result = syn.build_syn_m(db_session)
    result.ingredient.current_theoretical_stock = result.stock_safe
    result.ingredient.shelf_life_days = result.shelf_life_days
    db_session.commit()
    _enable_f14(db_session)

    outcome = ai_expiry_risk.assess_expiry_risk(db_session, result.ingredient.id)

    assert outcome.ok, outcome.message
    assert not outcome.at_risk
    assert outcome.value_at_risk == 0.0


# ==========================================================================
# TC-F14-04 — consommation nulle, alerte immédiate, jamais de division par zéro
# ==========================================================================

def test_tc_f14_04_zero_consumption_flags_immediately_without_crashing(db_session):
    ing = syn.ingredient(db_session, "Ingrédient jamais vendu", stock_qty=500.0)
    ing.shelf_life_days = 3
    db_session.commit()
    _enable_f14(db_session)

    outcome = ai_expiry_risk.assess_expiry_risk(db_session, ing.id)

    assert outcome.ok, outcome.message
    assert outcome.at_risk
    assert outcome.daily_consumption == 0.0
    assert outcome.remaining_at_shelf_life_end == 500.0
    assert outcome.value_at_risk == 500.0 * ing.unit_cost


# ==========================================================================
# TC-F14-05 — une réception entre-temps force un recalcul
# ==========================================================================

def test_tc_f14_05_a_delivery_in_between_changes_the_result(db_session):
    result = syn.build_syn_m(db_session)
    result.ingredient.current_theoretical_stock = result.stock_safe  # pas à risque au départ
    result.ingredient.shelf_life_days = result.shelf_life_days
    db_session.commit()
    _enable_f14(db_session)

    avant = ai_expiry_risk.assess_expiry_risk(db_session, result.ingredient.id)
    assert not avant.at_risk

    deliveries.record_delivery(
        db_session, received_on=datetime.utcnow(), supplier="Fournisseur SYN-M",
        lines=[deliveries.DeliveryLineInput(
            ingredient_id=result.ingredient.id, quantity=10_000.0, unit_price=result.ingredient.unit_cost,
        )],
    )

    apres = ai_expiry_risk.assess_expiry_risk(db_session, result.ingredient.id)
    assert apres.at_risk, "le stock a bondi de 10 000 g, largement au-dessus du seuil maintenant"
    assert apres.remaining_at_shelf_life_end != avant.remaining_at_shelf_life_end
