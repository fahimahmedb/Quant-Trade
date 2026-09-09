"""F18 — indicateur de confiance et retour automatique à v1 (docs/
feature-plans/ia-f10-f19.md §9). Aucun jeu SYN dédié dans le document ;
fixtures locales, comme F12/F16 dans ce même lot.

Deux profils réutilisés dans tout ce fichier :
- une TENDANCE sans saisonnalité hebdomadaire (F6 perd face à la v1 sur
  CHAQUE semaine rejouée — vérifié empiriquement avant d'écrire ces
  tests, pas supposé) ;
- SYN-A (Lot IA-0), où F6 gagne largement (vérifié dans
  tests/test_ai_forecast.py, gain 82,8 %).
"""
import random
from datetime import datetime, timedelta

from app import models
from app.services import ai_forecast, ai_forecast_confidence, settings_service
from tests import synthetic_data as syn


def _enable(db, *, f18=True):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f6_enabled = True
    if f18:
        settings.feature_f18_enabled = True
    db.commit()


def _trending_ingredient(db, *, weeks=16):
    """Tendance haussière pure, aucune saisonnalité hebdomadaire : F6 (qui
    ne voit que des moyennes par jour de semaine) perd face à la v1 (qui
    réagit vite à la tendance) sur chaque semaine rejouée."""
    ing = syn.ingredient(db, "Ingrédient tendance F18", stock_qty=10_000_000.0)
    plat = syn.dish(db, "Plat tendance F18", {ing.id: 1.0})
    start = datetime(2026, 1, 5)
    rows = [
        (start + timedelta(days=d), plat.name, 10.0 + d * 0.5, None)
        for d in range(weeks * 7)
    ]
    syn.import_sales_rows(db, rows, filename="tendance_f18.csv")
    return ing


def _mixed_two_bad_weeks(db):
    """Historique majoritairement saisonnier (F6 gagne), sauf les 3
    dernières semaines de VENTES injectées sans saisonnalité — ce qui, une
    fois rejoué, dégrade les 2 DERNIÈRES semaines évaluables seulement (la
    3e depuis la fin reste gagnante pour F6, la fenêtre de F6 lui laissant
    encore assez d'historique propre) : configuration vérifiée
    empiriquement pour donner exactement 2 semaines dégradées à la suite,
    jamais 3, avant d'écrire TC-F18-04 dessus."""
    rng = random.Random(1)
    ing = syn.ingredient(db, "Ingrédient 2 semaines F18", stock_qty=10_000_000.0)
    plat = syn.dish(db, "Plat 2 semaines F18", {ing.id: 1.0})
    start = datetime(2026, 1, 5)
    day_factors = {1: 1.0, 2: 1.1, 3: 1.2, 4: 2.0, 5: 2.2, 6: 0.8}
    closed_days = {0}
    total_weeks = 16
    disrupt_last_n_weeks = 3
    rows = []
    for d in range(total_weeks * 7):
        date = start + timedelta(days=d)
        wd = date.weekday()
        week_index = d // 7
        if wd in closed_days:
            continue
        if week_index >= total_weeks - disrupt_last_n_weeks:
            qty = syn.noisy(rng, 40.0, 0.05)
        else:
            qty = syn.noisy(rng, 20.0 * day_factors.get(wd, 1.0), 0.10)
        rows.append((date, plat.name, qty, None))
    syn.import_sales_rows(db, rows, filename="mixte_f18.csv")
    return ing


def test_f18_is_inert_by_default(db_session):
    ing = _trending_ingredient(db_session)
    _enable(db_session, f18=False)

    confidence = ai_forecast_confidence.assess_confidence(db_session, ing.id)
    reversion = ai_forecast_confidence.check_and_apply_reversion(db_session, ing.id)

    assert not confidence.ok and "désactivée" in confidence.message
    assert not reversion.ok and "désactivée" in reversion.message


# ==========================================================================
# AC-F18-1 / AC-F18-2 — dégradation sur 3 semaines, retour journalisé
# ==========================================================================

def test_ac_f18_1_three_degraded_weeks_trigger_the_revert(db_session):
    ing = _trending_ingredient(db_session)
    _enable(db_session)

    outcome = ai_forecast_confidence.check_and_apply_reversion(db_session, ing.id)

    assert outcome.ok, outcome.message
    assert outcome.action == "reverted_to_v1"
    db_session.refresh(ing)
    assert ing.f6_reverted_to_v1


def test_ac_f18_2_the_revert_is_logged(db_session):
    ing = _trending_ingredient(db_session)
    _enable(db_session)

    ai_forecast_confidence.check_and_apply_reversion(db_session, ing.id)

    entree = (
        db_session.query(models.ModelDecisionLog)
        .filter_by(feature="F18", ingredient_id=ing.id, event="revert_to_v1")
        .one_or_none()
    )
    assert entree is not None
    assert "3" in entree.detail


def test_reverted_ingredient_falls_back_to_v1_in_weekday_forecast(db_session):
    """La bascule doit réellement désactiver F6 pour cet ingrédient — pas
    seulement journaliser l'événement à côté d'un comportement inchangé."""
    ing = _trending_ingredient(db_session)
    _enable(db_session)

    avant = ai_forecast.weekday_forecast(db_session, ing.id)
    assert avant.gate_ok, "F6 doit fonctionner normalement avant la bascule"

    ai_forecast_confidence.check_and_apply_reversion(db_session, ing.id)

    apres = ai_forecast.weekday_forecast(db_session, ing.id)
    assert not apres.gate_ok
    assert "F18" in apres.gate_message


def test_no_alert_ingredient_never_flagged(db_session):
    """Non-vacuité par contre-exemple : sans lui, un code qui bascule
    TOUJOURS passerait quand même les tests précédents."""
    result = syn.build_syn_a(db_session, seed=1, weeks=16)
    _enable(db_session)

    outcome = ai_forecast_confidence.check_and_apply_reversion(db_session, result.ingredient.id)

    assert outcome.action == "none"
    db_session.refresh(result.ingredient)
    assert not result.ingredient.f6_reverted_to_v1


# ==========================================================================
# TC-F18-04 — dégradation sur 2 semaines seulement, pas de retour
# ==========================================================================

def test_tc_f18_04_two_degraded_weeks_do_not_trigger_the_revert(db_session):
    ing = _mixed_two_bad_weeks(db_session)
    _enable(db_session)

    backtest = ai_forecast.backtest_vs_v1(db_session, ing.id)
    deux_dernieres = backtest.weekly_results[-2:]
    troisieme = backtest.weekly_results[-3]
    assert not any(w.f6_better for w in deux_dernieres), "le jeu doit dégrader les 2 dernières semaines"
    assert troisieme.f6_better, "la 3e depuis la fin doit rester gagnante pour F6, sinon ce test ne prouve rien"

    outcome = ai_forecast_confidence.check_and_apply_reversion(db_session, ing.id)

    assert outcome.action == "none"
    db_session.refresh(ing)
    assert not ing.f6_reverted_to_v1


# ==========================================================================
# TC-F18-05 — hystérésis : réactivation seulement sur backtest complet
# ==========================================================================

def test_tc_f18_05_reactivation_requires_a_favorable_full_backtest(db_session):
    result = syn.build_syn_a(db_session, seed=1, weeks=16)
    _enable(db_session)
    result.ingredient.f6_reverted_to_v1 = True  # état de départ : déjà revenu à la v1
    db_session.commit()

    backtest = ai_forecast.backtest_vs_v1(db_session, result.ingredient.id)
    assert backtest.should_activate, "le jeu doit être franchement favorable, sinon ce test ne prouve rien"

    outcome = ai_forecast_confidence.check_and_apply_reversion(db_session, result.ingredient.id)

    assert outcome.action == "reactivated"
    db_session.refresh(result.ingredient)
    assert not result.ingredient.f6_reverted_to_v1

    entree = (
        db_session.query(models.ModelDecisionLog)
        .filter_by(feature="F18", ingredient_id=result.ingredient.id, event="reactivated")
        .one_or_none()
    )
    assert entree is not None


def test_tc_f18_05_no_flip_flopping_while_still_degraded(db_session):
    """« Pas de bascule en boucle » : un ingrédient déjà revenu à la v1,
    sur des données qui restent défavorables à F6, ne doit pas se
    réactiver au contrôle suivant."""
    ing = _trending_ingredient(db_session)
    _enable(db_session)

    ai_forecast_confidence.check_and_apply_reversion(db_session, ing.id)  # 1er appel : bascule
    db_session.refresh(ing)
    assert ing.f6_reverted_to_v1

    outcome = ai_forecast_confidence.check_and_apply_reversion(db_session, ing.id)  # 2e appel

    assert outcome.ok, outcome.message  # le backtest doit réellement s'exécuter, pas échouer par défaut
    assert outcome.action == "none", "les données restent défavorables : aucune réactivation"
    db_session.refresh(ing)
    assert ing.f6_reverted_to_v1, "toujours revenu à la v1"


# ==========================================================================
# AC-F18-3 — aucun terme statistique visible côté restaurateur
# ==========================================================================

def test_ac_f18_3_no_jargon_in_the_restaurant_facing_explanation(db_session):
    result = syn.build_syn_a(db_session, seed=1, weeks=16)
    _enable(db_session)

    outcome = ai_forecast_confidence.assess_confidence(db_session, result.ingredient.id)

    assert outcome.ok, outcome.message
    for terme_interdit in ["MAPE", "RMSE", "mape", "rmse"]:
        assert terme_interdit not in outcome.explanation
    assert "%" in outcome.explanation
    assert outcome.average_error_pct is not None
