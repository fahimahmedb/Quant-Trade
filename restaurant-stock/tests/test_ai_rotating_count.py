"""F11 — comptage tournant intelligent (docs/feature-plans/ia-f10-f19.md
§2), prouvée sur SYN-K. Éteinte par défaut (`Settings.feature_f11_enabled`),
et nécessite F10 activé (elle en dépend explicitement).
"""
from datetime import datetime, timedelta

from app import models
from app.services import ai_drift, ai_rotating_count, settings_service
from tests import synthetic_data as syn

AS_OF = datetime(2026, 11, 24).date()  # juste après la dernière session SYN-K


def _enable_f10_f11(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f10_enabled = True
    settings.feature_f11_enabled = True
    db.commit()


def test_f11_is_inert_by_default(db_session):
    syn.build_syn_k(db_session)
    result = ai_rotating_count.daily_session(db_session, as_of=AS_OF)
    assert not result.ok
    assert "désactivée" in result.message
    assert result.items == []


def test_f11_requires_f10_even_when_its_own_flag_is_on(db_session):
    syn.build_syn_k(db_session)
    settings_service.get_settings(db_session)
    settings = db_session.get(models.Settings, 1)
    settings.feature_f11_enabled = True  # F10 reste éteint
    db_session.commit()

    result = ai_rotating_count.daily_session(db_session, as_of=AS_OF)
    assert not result.ok
    assert "F10" in result.message


# ==========================================================================
# Grille fréquence x criticité — les quatre coins couverts par SYN-K
# ==========================================================================

def test_syn_k_stable_critical_ingredient_is_weekly(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)

    suggestion = ai_rotating_count.suggest_frequency(db_session, result.stable_ingredient.id, as_of=AS_OF)

    assert suggestion.criticality_class == "A"
    assert suggestion.conforming_streak >= 6
    assert suggestion.frequency == "hebdomadaire", "critique, jamais mensuel même stable"


def test_syn_k_unstable_critical_ingredient_is_daily(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)

    suggestion = ai_rotating_count.suggest_frequency(db_session, result.unstable_ingredient.id, as_of=AS_OF)

    assert suggestion.criticality_class == "A"
    assert suggestion.conforming_streak < 3
    assert suggestion.frequency == "quotidien"


def test_syn_k_stable_low_value_ingredient_is_monthly(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)

    suggestion = ai_rotating_count.suggest_frequency(db_session, result.stable_low_value.id, as_of=AS_OF)

    assert suggestion.criticality_class == "C"
    assert suggestion.conforming_streak >= 6
    assert suggestion.frequency == "mensuel"


def test_tc_f11_06_new_ingredient_without_history_is_daily(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)

    suggestion = ai_rotating_count.suggest_frequency(db_session, result.new_ingredient.id, as_of=AS_OF)

    assert suggestion.criticality_class is None
    assert suggestion.frequency == "quotidien"


def test_explanation_carries_the_streak_and_the_frequency(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)

    suggestion = ai_rotating_count.suggest_frequency(db_session, result.stable_low_value.id, as_of=AS_OF)

    assert "mensuel" in suggestion.explanation
    assert str(suggestion.conforming_streak) in suggestion.explanation


# ==========================================================================
# AC-F11-4 / TC-F11-07 — badge F5 prioritaire sur tout, y compris le retrait manuel
# ==========================================================================

def test_ac_f11_4_f5_badge_forces_inclusion_even_when_classed_monthly(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)
    settings = db_session.get(models.Settings, 1)
    settings.feature_f5_enabled = True
    db_session.commit()

    # Un écart de perte récurrente sur stable_low_value (classé mensuel) :
    # 3 comptages consécutifs significatifs, construits ici plutôt que
    # dans SYN-K pour ne pas casser son streak "toujours conforme" utilisé
    # par un autre test.
    ing = result.stable_low_value
    base = datetime(2026, 12, 1)
    for i in range(3):
        d = base + timedelta(days=i * 7)
        syn.run_count_session(
            db_session, counted_by="Badge F5",
            counted={ing.id: ing.current_theoretical_stock - 50.0},
            ended_at=d,
        )
    # Le badge F5 lui-même doit être actif pour ce test : vérifié directement
    badge = ai_drift.classify_losses(db_session, ing.id)
    assert badge is not None, "le jeu doit produire un badge F5 réel pour que ce test prouve quelque chose"

    daily = ai_rotating_count.daily_session(db_session, as_of=(base + timedelta(days=20)).date())
    assert daily.ok, daily.message
    item = next(it for it in daily.items if it.ingredient_id == ing.id)
    assert item.included
    assert item.reason == "badge_f5"


def test_tc_f11_07_manual_removal_is_overridden_by_a_later_f5_badge(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)
    settings = db_session.get(models.Settings, 1)
    settings.feature_f5_enabled = True
    db_session.commit()

    ing = result.stable_ingredient  # hebdomadaire, pas dû tous les jours
    ai_rotating_count.set_manual_override(db_session, ing.id, include=False)

    sans_badge = ai_rotating_count.daily_session(db_session, as_of=AS_OF)
    item = next(it for it in sans_badge.items if it.ingredient_id == ing.id)
    assert not item.included
    assert item.reason == "manuel"

    base = datetime(2026, 12, 1)
    for i in range(3):
        d = base + timedelta(days=i * 7)
        syn.run_count_session(
            db_session, counted_by="Badge tardif",
            counted={ing.id: ing.current_theoretical_stock - 50.0},
            ended_at=d,
        )
    badge = ai_drift.classify_losses(db_session, ing.id)
    assert badge is not None

    avec_badge = ai_rotating_count.daily_session(db_session, as_of=(base + timedelta(days=20)).date())
    item2 = next(it for it in avec_badge.items if it.ingredient_id == ing.id)
    assert item2.included, "le badge F5 doit réintégrer l'ingrédient malgré le retrait manuel"
    assert item2.reason == "badge_f5"


def test_manual_override_can_be_cleared(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)

    ai_rotating_count.set_manual_override(db_session, result.stable_ingredient.id, include=False)
    ai_rotating_count.set_manual_override(db_session, result.stable_ingredient.id, include=None)

    daily = ai_rotating_count.daily_session(db_session, as_of=AS_OF)
    item = next(it for it in daily.items if it.ingredient_id == result.stable_ingredient.id)
    assert item.reason == "frequence"


# ==========================================================================
# AC-F11-3 — comptage complet obligatoire, prioritaire sur toute session ciblée
# ==========================================================================

def test_ac_f11_3_overdue_full_count_forces_every_active_ingredient(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)

    trop_tard = (result.sessions[-1].ended_at + timedelta(days=29)).date()  # > 28 j par défaut
    daily = ai_rotating_count.daily_session(db_session, as_of=trop_tard)

    assert daily.ok, daily.message
    assert daily.full_count_required
    assert all(it.included for it in daily.items)
    assert all(it.reason == "comptage_complet_du" for it in daily.items)


def test_full_count_not_yet_required_leaves_room_for_a_targeted_session(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)

    daily = ai_rotating_count.daily_session(db_session, as_of=AS_OF)  # 1 jour après la dernière session

    assert daily.ok
    assert not daily.full_count_required
    assert not all(it.included for it in daily.items), "au moins un ingrédient mensuel/hebdo ne doit pas être dû"


def test_full_count_interval_is_configurable(db_session):
    result = syn.build_syn_k(db_session)
    _enable_f10_f11(db_session)
    settings = db_session.get(models.Settings, 1)
    settings.full_count_interval_days = 5.0
    db_session.commit()

    six_jours_apres = (result.sessions[-1].ended_at + timedelta(days=6)).date()
    daily = ai_rotating_count.daily_session(db_session, as_of=six_jours_apres)

    assert daily.full_count_required


# ==========================================================================
# Gate — global, indépendant du gate par-ingrédient de F10
# ==========================================================================

def test_gate_requires_at_least_three_global_completed_counts(db_session):
    ing = syn.ingredient(db_session, "Ingrédient seul", stock_qty=10_000_000.0)
    plat = syn.dish(db_session, "Plat seul", {ing.id: 1.0})
    start = datetime(2026, 1, 5)
    rows = [(start + timedelta(days=d), plat.name, 5.0, None) for d in range(56)]
    syn.import_sales_rows(db_session, rows, filename="seul.csv")
    _enable_f10_f11(db_session)

    # Un seul comptage complet (sous le gate de 3) : aucune session du jour.
    syn.run_count_session(db_session, counted_by="Un seul", counted={}, ended_at=start + timedelta(days=60))

    result = ai_rotating_count.daily_session(db_session, as_of=(start + timedelta(days=61)).date())
    assert not result.ok
    assert "sur 3 nécessaires" in result.message
