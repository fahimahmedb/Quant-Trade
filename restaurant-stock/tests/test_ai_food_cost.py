"""F9 — food cost théorique vs réel (docs/IA scope.md §1.9), prouvée sur
SYN-H, à ±0,1 point comme l'exige le document. Éteinte par défaut
(`Settings.feature_f9_enabled`).
"""
from datetime import timedelta

from app import models
from app.services import ai_food_cost, settings_service
from tests import synthetic_data as syn


def _enable_f9(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f9_enabled = True
    db.commit()


def test_f9_is_inert_by_default(db_session):
    result = syn.build_syn_h(db_session)
    outcome = ai_food_cost.compute_food_cost(
        db_session, result.opening_count.ended_at, result.closing_count.ended_at,
    )
    assert not outcome.ok
    assert "désactivée" in outcome.message
    assert outcome.theoretical_pct is None


def test_syn_h_theoretical_and_real_food_cost_within_point_one(db_session):
    result = syn.build_syn_h(db_session, weeks=8)
    _enable_f9(db_session)

    outcome = ai_food_cost.compute_food_cost(
        db_session, result.opening_count.ended_at, result.closing_count.ended_at,
    )

    assert outcome.ok, outcome.message
    assert abs(outcome.theoretical_pct - result.theoretical_food_cost_pct) < 0.1, outcome.theoretical_pct
    assert abs(outcome.real_pct - result.real_food_cost_pct) < 0.1, outcome.real_pct
    # L'écart doit être positif et proche de 2,5 points (32,5 - 30,0) : le
    # réel coûte plus cher que ce que la recette laisse penser.
    assert 2.0 < (outcome.real_pct - outcome.theoretical_pct) < 3.0


def test_missing_bracketing_count_is_reported_honestly(db_session):
    result = syn.build_syn_h(db_session, weeks=8)
    _enable_f9(db_session)

    # Une fenêtre qui déborde largement après le dernier comptage de clôture :
    # aucun comptage n'encadre la fin de cette période.
    outcome = ai_food_cost.compute_food_cost(
        db_session, result.opening_count.ended_at, result.closing_count.ended_at + timedelta(days=365),
    )

    assert not outcome.ok
    assert "comptage" in outcome.message.lower()
    # Le théorique reste calculable indépendamment (aucun comptage requis) :
    # seul le réel est bloqué par l'absence de clôture.
    assert outcome.theoretical_pct is not None


def test_no_revenue_in_period_is_reported_not_divided_by_zero(db_session):
    result = syn.build_syn_h(db_session, weeks=8)
    _enable_f9(db_session)

    avant_tout = result.opening_count.ended_at - timedelta(days=365)
    outcome = ai_food_cost.compute_food_cost(db_session, avant_tout, avant_tout + timedelta(days=1))

    assert not outcome.ok
    assert "chiffre d'affaires" in outcome.message.lower()
