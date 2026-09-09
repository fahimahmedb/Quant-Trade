"""F23 — cold start d'un plat sans historique (docs/feature-plans/
backlog-lot-ia-2.md ticket 5, cible SYN-S). La constante de lissage
(`cold_start_smoothing_days`, défaut 14 jours) a été vérifiée par script
autonome avant d'être fixée (scratchpad probe_f23.py) : à K=14, le poids du
réel est exactement 0,5 à 14 jours (par construction de la formule), et
atteint ~74,5 % à 41 jours (juste avant le gate F6 à 6 semaines) — une
bascule complète mais non brutale à J+42, vérifiée empiriquement plutôt que
supposée.
"""
from datetime import date, datetime, timedelta

from app import models
from app.services import ai_cold_start as cs, ai_forecast, settings_service
from tests import synthetic_data as syn


def _enable(db, *, f23=True, f6=True):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    if f6:
        settings.feature_f6_enabled = True
    if f23:
        settings.feature_f23_enabled = True
    db.commit()


def test_f23_is_inert_by_default(db_session):
    result = syn.build_syn_s(db_session)
    _enable(db_session, f23=False)

    out = cs.blended_daily_consumption(db_session, result.ingredient.id, as_of=result.start)

    assert not out.ok and "désactivée" in out.message


def test_no_chef_estimate_means_no_effect(db_session):
    """Gate du ticket : absent, le plat garde le comportement actuel."""
    ing = syn.ingredient(db_session, "Sans estimation", stock_qty=1000.0)
    syn.dish(db_session, "Plat sans estimation", {ing.id: 1.0})  # initial_daily_estimate reste None
    _enable(db_session)

    out = cs.blended_daily_consumption(db_session, ing.id, as_of=date(2026, 1, 5))

    assert not out.ok and "Aucun plat" in out.message


def test_pure_chef_estimate_on_day_zero(db_session):
    """Aucune vente réelle encore : l'estimation du chef seule fait foi."""
    result = syn.build_syn_s(db_session, chef_estimate=15.0)
    _enable(db_session)

    out = cs.blended_daily_consumption(db_session, result.ingredient.id, as_of=result.start)

    assert out.ok, out.message
    assert out.days_observed == 0
    assert out.real_weight == 0.0
    assert out.blended_daily_qty == 15.0


def test_real_weight_is_exactly_half_at_the_smoothing_constant(db_session):
    """Non-vacuité de la formule (poids_réel = jours/(jours+K)) : à
    exactement K=14 jours observés, le poids doit être exactement 0,5 —
    pas approximativement, la formule le garantit par construction."""
    result = syn.build_syn_s(db_session, days=30)
    _enable(db_session)

    out = cs.blended_daily_consumption(db_session, result.ingredient.id, as_of=result.start + timedelta(days=14))

    assert out.ok, out.message
    assert out.days_observed == 14
    assert out.real_weight == 0.5
    assert out.blended_daily_qty == 0.5 * result.chef_estimate + 0.5 * out.real_component


def test_blend_shifts_toward_real_average_as_days_accumulate(db_session):
    result = syn.build_syn_s(db_session, chef_estimate=15.0, real_qty_per_day=10.0, days=30)
    _enable(db_session)

    early = cs.blended_daily_consumption(db_session, result.ingredient.id, as_of=result.start + timedelta(days=2))
    late = cs.blended_daily_consumption(db_session, result.ingredient.id, as_of=result.start + timedelta(days=28))

    assert early.ok and late.ok
    # Le réel (~10) est BAS SOUS l'estimation du chef (15) : plus on
    # observe, plus l'estimation mélangée doit se rapprocher de 10, donc
    # DIMINUER — un jeu où réel > chef vérifierait la même propriété par
    # une hausse, ce test choisit délibérément la direction inverse.
    assert late.blended_daily_qty < early.blended_daily_qty
    assert late.real_weight > early.real_weight
    assert 9.0 < late.real_component < 11.0  # bruit ±10% autour de 10, vérifié empiriquement


def test_f23_defers_entirely_once_f6_gate_is_reached(db_session):
    """Non-vacuité de la bascule complète (règle métier du ticket) :
    exactement à la frontière du gate F6 (6 semaines = 42 jours de span
    calendaire), F23 doit s'effacer PRÉCISÉMENT quand F6 devient
    disponible — jamais un jour avant (F23 encore seul), jamais un jour
    après (les deux inactifs, ce qui laisserait un trou)."""
    result = syn.build_syn_s(db_session, days=45)
    _enable(db_session)

    just_before = cs.blended_daily_consumption(db_session, result.ingredient.id, as_of=result.start + timedelta(days=41))
    gate_before = ai_forecast.weekday_forecast(db_session, result.ingredient.id, as_of=result.start + timedelta(days=41))
    at_boundary = cs.blended_daily_consumption(db_session, result.ingredient.id, as_of=result.start + timedelta(days=42))
    gate_at_boundary = ai_forecast.weekday_forecast(db_session, result.ingredient.id, as_of=result.start + timedelta(days=42))

    assert gate_before.gate_ok is False
    assert just_before.ok is True

    assert gate_at_boundary.gate_ok is True
    assert at_boundary.ok is False
    assert "déjà disponible" in at_boundary.message


def test_multiple_new_dishes_sharing_an_ingredient_sum_their_estimates(db_session):
    ing = syn.ingredient(db_session, "Ingrédient partagé neuf", stock_qty=10_000_000.0)
    plat_a = syn.dish(db_session, "Plat neuf A", {ing.id: 1.0})
    plat_b = syn.dish(db_session, "Plat neuf B", {ing.id: 2.0})  # grammage différent
    plat_a.initial_daily_estimate = 5.0
    plat_b.initial_daily_estimate = 3.0  # contribution : 3.0 * 2.0 = 6.0
    db_session.commit()
    _enable(db_session)

    out = cs.blended_daily_consumption(db_session, ing.id, as_of=date(2026, 1, 5))

    assert out.ok, out.message
    assert out.chef_component == 5.0 * 1.0 + 3.0 * 2.0  # 11.0
    assert out.blended_daily_qty == 11.0  # jour zéro : aucune vente encore


def test_established_dish_sharing_ingredient_defers_entirely_to_f6(db_session):
    """Non-vacuité de l'absence de double comptage (docstring du module) :
    un ingrédient déjà consommé depuis 90 jours par un plat établi a déjà
    franchi le gate F6 tout seul — l'ajout d'un plat neuf avec sa propre
    estimation ne doit PAS raviver un mélange chef/réel partiel qui
    ignorerait la consommation déjà bien mesurée du plat établi."""
    ing = syn.ingredient(db_session, "Ingrédient avec plat établi", stock_qty=10_000_000.0)
    ancien = syn.dish(db_session, "Plat ancien établi", {ing.id: 1.0})
    nouveau = syn.dish(db_session, "Plat neuf ajouté", {ing.id: 1.0})
    nouveau.initial_daily_estimate = 15.0
    db_session.commit()
    _enable(db_session)

    start = date(2025, 10, 1)
    rows = []
    for day_offset in range(90):
        d = start + timedelta(days=day_offset)
        rows.append((datetime(d.year, d.month, d.day), ancien.name, 8.0, None))
    syn.import_sales_rows(db_session, rows, filename="etabli.csv")

    as_of = start + timedelta(days=90)
    gate = ai_forecast.weekday_forecast(db_session, ing.id, as_of=as_of)
    out = cs.blended_daily_consumption(db_session, ing.id, as_of=as_of)

    assert gate.gate_ok is True
    assert out.ok is False
    assert "déjà disponible" in out.message
