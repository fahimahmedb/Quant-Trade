"""F12 — alerte de marge érodée (docs/feature-plans/ia-f10-f19.md §3),
prouvée sur SYN-L. Éteinte par défaut (`Settings.feature_f12_enabled`).
"""
from datetime import datetime, timedelta

from app import models
from app.services import ai_margin_alert, settings_service
from tests import synthetic_data as syn


def _enable_f12(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f12_enabled = True
    db.commit()


def test_f12_is_inert_by_default(db_session):
    result = syn.build_syn_l(db_session)
    outcome = ai_margin_alert.assess_margin(db_session, result.dish.id)
    assert not outcome.ok
    assert "désactivée" in outcome.message


# ==========================================================================
# SYN-L — hausse progressive, coefficient 3,4 -> 2,8
# ==========================================================================

def test_syn_l_detects_the_coefficient_drop(db_session):
    result = syn.build_syn_l(db_session)
    _enable_f12(db_session)

    outcome = ai_margin_alert.assess_margin(db_session, result.dish.id, as_of=result.now)

    assert outcome.ok, outcome.message
    assert abs(outcome.coefficient_then - 3.4) < 0.05
    assert abs(outcome.coefficient_now - 2.8) < 0.05
    assert outcome.is_alert
    assert outcome.dropped_over_window, "baisse de plus de 10% sur 90 jours"


def test_ac_f12_3_the_increase_is_attributed_to_the_right_ingredient(db_session):
    result = syn.build_syn_l(db_session)
    _enable_f12(db_session)

    outcome = ai_margin_alert.assess_margin(db_session, result.dish.id, as_of=result.now)

    par_id = {i.ingredient_id: i for i in outcome.impacts}
    steak = par_id[result.ingredient_varying.id]
    assert abs(steak.cost_impact - 0.63) < 0.01, "100g x (0,0187 - 0,0124) = 0,63 €"
    for stable in result.ingredients_stable:
        assert abs(par_id[stable.id].cost_impact) < 0.001, "prix stables : aucun impact"
    # La somme des impacts doit reconstituer exactement l'écart total.
    assert abs(sum(i.cost_impact for i in outcome.impacts) - (outcome.food_cost_now - outcome.food_cost_then)) < 0.001


def test_explanation_names_the_dish_and_the_main_ingredient(db_session):
    result = syn.build_syn_l(db_session)
    _enable_f12(db_session)

    outcome = ai_margin_alert.assess_margin(db_session, result.dish.id, as_of=result.now)

    assert result.dish.name in outcome.explanation
    assert result.ingredient_varying.name in outcome.explanation
    assert "3.4" in outcome.explanation
    assert "2.8" in outcome.explanation


# ==========================================================================
# AC-F12-1 — franchissement exact du seuil, pas avant
# ==========================================================================

def _dish_with_coefficient(db, coefficient, *, sale_price=10.0):
    """Un plat à un seul ingrédient, sans historique de hausse (le prix
    "alors" == le prix "maintenant"), au coefficient EXACT demandé —
    isole la frontière du seuil sans y mêler la baisse sur 90 jours."""
    food_cost = sale_price / coefficient
    ing = syn.ingredient(db, f"Ingrédient seuil {coefficient:g}", unit_cost=food_cost, stock_qty=1_000_000.0)
    plat = syn.dish(db, f"Plat seuil {coefficient:g}", {ing.id: 1.0})
    now = datetime.utcnow()
    db.add(models.PriceHistory(ingredient_id=ing.id, unit_price=food_cost, recorded_at=now - timedelta(days=90)))
    db.add(models.PriceHistory(ingredient_id=ing.id, unit_price=food_cost, recorded_at=now))
    db.commit()
    syn.import_sales_rows(db, [(now, plat.name, 1.0, sale_price)], filename=f"seuil_{coefficient:g}.csv")
    return plat, now


def test_ac_f12_1_exactly_at_threshold_is_not_an_alert(db_session):
    _enable_f12(db_session)
    plat, now = _dish_with_coefficient(db_session, 3.0)  # seuil par défaut, pile dessus

    outcome = ai_margin_alert.assess_margin(db_session, plat.id, as_of=now)

    assert outcome.ok, outcome.message
    assert not outcome.below_threshold, "pile au seuil : pas encore franchi"
    assert not outcome.is_alert


def test_ac_f12_1_just_below_threshold_is_an_alert(db_session):
    _enable_f12(db_session)
    plat, now = _dish_with_coefficient(db_session, 2.99)

    outcome = ai_margin_alert.assess_margin(db_session, plat.id, as_of=now)

    assert outcome.below_threshold
    assert outcome.is_alert


# ==========================================================================
# AC-F12-2 — plat sans prix de vente, exclu avec mention
# ==========================================================================

def test_ac_f12_2_dish_without_sale_price_is_excluded_with_a_mention(db_session):
    ing = syn.ingredient(db_session, "Ingrédient sans vente", unit_cost=0.01, stock_qty=1_000_000.0)
    plat = syn.dish(db_session, "Plat jamais vendu", {ing.id: 100.0})
    now = datetime.utcnow()
    _enable_f12(db_session)

    outcome = ai_margin_alert.assess_margin(db_session, plat.id, as_of=now)

    assert not outcome.ok
    assert "prix de vente" in outcome.message.lower()


# ==========================================================================
# Gate — au moins 2 relevés de prix sur au moins un ingrédient du plat
# ==========================================================================

def test_gate_requires_at_least_two_price_records(db_session):
    """Un seul relevé de prix (le prix courant, jamais changé) : aucune
    hausse n'est démontrable, F12 reste inactif — distinct du cas "pas de
    prix de vente" (AC-F12-2), donc testé séparément."""
    ing = syn.ingredient(db_session, "Ingrédient un seul relevé", unit_cost=0.02, stock_qty=1_000_000.0)
    plat = syn.dish(db_session, "Plat un seul relevé", {ing.id: 100.0})
    now = datetime.utcnow()
    db_session.add(models.PriceHistory(ingredient_id=ing.id, unit_price=0.02, recorded_at=now))
    syn.import_sales_rows(db_session, [(now, plat.name, 1.0, 10.0)], filename="un_seul_releve.csv")
    _enable_f12(db_session)

    outcome = ai_margin_alert.assess_margin(db_session, plat.id, as_of=now)

    assert not outcome.ok
    assert "relevé" in outcome.message.lower()


# ==========================================================================
# AC-F12-4 — prix suggéré, restaure le coefficient d'origine au centime
# ==========================================================================

def test_ac_f12_4_suggested_price_restores_the_original_coefficient(db_session):
    result = syn.build_syn_l(db_session)
    _enable_f12(db_session)

    outcome = ai_margin_alert.assess_margin(db_session, result.dish.id, as_of=result.now)

    assert outcome.suggested_price is not None
    coefficient_avec_prix_suggere = outcome.suggested_price / outcome.food_cost_now
    assert abs(coefficient_avec_prix_suggere - outcome.coefficient_then) < 0.005, "au centime près"


# ==========================================================================
# AC-F12-5 — jamais de modification automatique
# ==========================================================================

def test_ac_f12_5_suggested_price_never_touches_the_actual_sale_price(db_session):
    result = syn.build_syn_l(db_session)
    _enable_f12(db_session)

    avant = ai_margin_alert.assess_margin(db_session, result.dish.id, as_of=result.now).sale_price
    ai_margin_alert.assess_margin(db_session, result.dish.id, as_of=result.now)
    apres = ai_margin_alert.assess_margin(db_session, result.dish.id, as_of=result.now).sale_price

    assert avant == apres == result.sale_price


# ==========================================================================
# TC-F12-06 — hausse puis retour au point de départ, alerte levée puis retirée
# ==========================================================================

def test_tc_f12_06_alert_clears_when_price_returns_to_baseline(db_session):
    result = syn.build_syn_l(db_session)
    _enable_f12(db_session)

    avec_hausse = ai_margin_alert.assess_margin(db_session, result.dish.id, as_of=result.now)
    assert avec_hausse.is_alert

    result.ingredient_varying.unit_cost = 0.0124  # retour au prix d'origine
    db_session.add(models.PriceHistory(
        ingredient_id=result.ingredient_varying.id, unit_price=0.0124, recorded_at=result.now + timedelta(days=1),
    ))
    db_session.commit()

    apres_retour = ai_margin_alert.assess_margin(
        db_session, result.dish.id, as_of=result.now + timedelta(days=1),
    )
    assert not apres_retour.is_alert, "le prix est revenu à son niveau d'origine : plus rien à signaler"


# ==========================================================================
# TC-F12-07 — un ingrédient partagé par 5 plats, impact différencié
# ==========================================================================

def test_tc_f12_07_shared_ingredient_lists_all_five_dishes_with_their_own_impact(db_session):
    now = datetime.utcnow()
    window_start = now - timedelta(days=90)
    partage = syn.ingredient(db_session, "Ingrédient partagé", unit_cost=0.02, stock_qty=1_000_000.0)
    db_session.add(models.PriceHistory(ingredient_id=partage.id, unit_price=0.01, recorded_at=window_start))
    db_session.add(models.PriceHistory(ingredient_id=partage.id, unit_price=0.02, recorded_at=now))
    db_session.commit()

    plats = []
    for i, grammage in enumerate([50.0, 100.0, 150.0, 200.0, 250.0]):
        plat = syn.dish(db_session, f"Plat partagé {i}", {partage.id: grammage})
        syn.import_sales_rows(db_session, [(now, plat.name, 1.0, 10.0)], filename=f"partage_{i}.csv")
        plats.append((plat, grammage))
    _enable_f12(db_session)

    for plat, grammage in plats:
        outcome = ai_margin_alert.assess_margin(db_session, plat.id, as_of=now)
        assert outcome.ok, outcome.message
        impact = next(i for i in outcome.impacts if i.ingredient_id == partage.id)
        # (0,02 - 0,01) x grammage = impact attendu, différent pour chaque plat.
        assert abs(impact.cost_impact - 0.01 * grammage) < 0.001


# ==========================================================================
# TC-F12-08 — impact négligeable, pas d'alerte
# ==========================================================================

def test_tc_f12_08_a_forty_percent_rise_on_a_two_percent_ingredient_does_not_alert(db_session):
    now = datetime.utcnow()
    window_start = now - timedelta(days=90)

    # Ingrédient dominant, prix stable : porte 98% du coût.
    dominant = syn.ingredient(db_session, "Ingrédient dominant TC-F12-08", unit_cost=1.0, stock_qty=1_000_000.0)
    db_session.add(models.PriceHistory(ingredient_id=dominant.id, unit_price=1.0, recorded_at=window_start))
    db_session.add(models.PriceHistory(ingredient_id=dominant.id, unit_price=1.0, recorded_at=now))

    # Ingrédient marginal : 2% du coût, +40% de prix.
    marginal = syn.ingredient(db_session, "Ingrédient marginal TC-F12-08", unit_cost=0.02857, stock_qty=1_000_000.0)
    db_session.add(models.PriceHistory(ingredient_id=marginal.id, unit_price=0.02041, recorded_at=window_start))
    db_session.add(models.PriceHistory(ingredient_id=marginal.id, unit_price=0.02857, recorded_at=now))
    db_session.commit()

    plat = syn.dish(db_session, "Plat TC-F12-08", {dominant.id: 1.0, marginal.id: 1.0})
    syn.import_sales_rows(db_session, [(now, plat.name, 1.0, 3.4)], filename="tc_f12_08.csv")  # coefficient confortable
    _enable_f12(db_session)

    outcome = ai_margin_alert.assess_margin(db_session, plat.id, as_of=now)

    assert outcome.ok, outcome.message
    assert not outcome.is_alert, f"coefficient {outcome.coefficient_now:.2f}, impact réel négligeable"


# ==========================================================================
# Vue "impact d'un ingrédient" — la fonction dédiée, pas seulement assess_margin
# ==========================================================================

def test_ingredient_price_impact_lists_every_dish_using_it(db_session):
    result = syn.build_syn_l(db_session)
    _enable_f12(db_session)

    impacts = ai_margin_alert.ingredient_price_impact(db_session, result.ingredient_varying.id, as_of=result.now)

    assert len(impacts) == 1
    assert impacts[0].dish_id == result.dish.id
    assert impacts[0].is_alert
