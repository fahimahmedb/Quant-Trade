"""F6 — prévision par jour de semaine, en mode ombre (docs/IA scope.md
§1.2/1.7/1.10), prouvée sur SYN-A/E/F/I. Éteinte par défaut
(`Settings.feature_f6_enabled`) : un test dédié le prouve plutôt que de le
supposer.
"""
import random
from datetime import datetime, timedelta

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


# ==========================================================================
# Règle de calcul de specs-v2-ia-plan-test.md §4 (F6) : « moyenne des 8
# dernières occurrences du même jour de semaine, pondérée par récence (les 4
# plus récentes comptent double) »
# ==========================================================================

def _huit_vendredis(db, anciennes: float, recentes: float, semaines: int = 8):
    """Un ingrédient vendu UNIQUEMENT le vendredi, sur `semaines` semaines :
    les 4 premières occurrences à `anciennes`, les 4 dernières à `recentes`.
    Les autres jours sont sans vente sur >= 4 occurrences, donc détectés
    comme jours de fermeture — ce qui isole exactement le vendredi."""
    ing = syn.ingredient(db, "Ingrédient vendredi", stock_qty=1_000_000.0)
    plat = syn.dish(db, "Plat vendredi", {ing.id: 1.0})
    premier_vendredi = datetime(2026, 1, 2)
    rows = []
    for i in range(semaines):
        qty = anciennes if i < semaines - 4 else recentes
        rows.append((premier_vendredi + timedelta(days=i * 7), plat.name, qty, None))
    syn.import_sales_rows(db, rows, filename="vendredis.csv")
    return ing


def test_recent_occurrences_count_double_in_the_weighted_mean(db_session):
    ing = _huit_vendredis(db_session, anciennes=15.0, recentes=30.0)
    _enable_f6(db_session)

    outcome = ai_forecast.weekday_forecast(db_session, ing.id)

    assert outcome.gate_ok, outcome.gate_message
    obtenu = outcome.forecast.expected_daily_qty[4]  # vendredi
    # (4 x 15 x 1 + 4 x 30 x 2) / (4 x 1 + 4 x 2) = 300 / 12 = 25.
    # Une moyenne simple donnerait 22,5 : l'écart mesure la pondération.
    assert abs(obtenu - 25.0) < 0.001, obtenu


def test_only_the_last_eight_occurrences_are_used(db_session):
    """La fenêtre du document est bornée à 8 occurrences : ce qui s'est
    passé avant ne doit plus déplacer la prévision du tout."""
    ing = _huit_vendredis(db_session, anciennes=15.0, recentes=30.0, semaines=12)
    _enable_f6(db_session)
    avant = ai_forecast.weekday_forecast(db_session, ing.id).forecast.expected_daily_qty[4]

    # Les 4 occurrences les plus ANCIENNES (hors fenêtre) divisées par deux.
    anciennes = (
        db_session.query(models.SaleLine)
        .order_by(models.SaleLine.sale_date)
        .limit(4)
        .all()
    )
    for ligne in anciennes:
        ligne.quantity_sold = ligne.quantity_sold / 2
    db_session.commit()

    apres = ai_forecast.weekday_forecast(db_session, ing.id).forecast.expected_daily_qty[4]
    assert apres == avant, "une occurrence hors des 8 dernières ne doit rien changer"


def test_ac_f6_04_every_forecast_carries_an_interval_and_its_occurrence_count(db_session):
    """AC-F6-4 : « intervalle affiché sur toute prévision, jamais une valeur
    seule »."""
    ing = _huit_vendredis(db_session, anciennes=15.0, recentes=30.0)
    _enable_f6(db_session)

    forecast = ai_forecast.weekday_forecast(db_session, ing.id).forecast

    assert set(forecast.estimates) == set(forecast.expected_daily_qty)
    estimation = forecast.estimates[4]
    assert estimation.low == 15.0 and estimation.high == 30.0
    assert estimation.low <= estimation.expected_qty <= estimation.high
    assert estimation.occurrences == 8


def test_ia_08_outlier_is_reported_as_a_point_anomaly_not_silently_dropped(db_session):
    """IA-08 exige les deux moitiés : « détection comme anomalie ponctuelle »
    ET « pas d'effet sur la prévision ». Écarter en silence ne satisfait que
    la seconde."""
    result = syn.build_syn_f(db_session, seed=6, weeks=12)
    _enable_f6(db_session)

    forecast = ai_forecast.weekday_forecast(db_session, result.ingredient.id).forecast

    jour = result.outlier_sale_date.weekday()
    assert result.outlier_sale_date.date() in forecast.estimates[jour].excluded_outliers
    autres = [wd for wd in forecast.estimates if wd != jour]
    assert all(not forecast.estimates[wd].excluded_outliers for wd in autres), (
        "aucun jour normal ne doit voir d'occurrence écartée"
    )


# ==========================================================================
# IA-01 — backtest F6 contre la règle v1 (specs-v2-ia-plan-test.md §6.3)
# ==========================================================================

def test_ia_01_backtest_beats_v1_on_a_seasonal_ingredient(db_session):
    """SYN-A porte une saisonnalité hebdomadaire franche (vendredi = 2x
    mardi) : c'est exactement ce qu'une moyenne glissante ne peut pas
    voir. Le backtest doit le mesurer, pas le supposer."""
    result = syn.build_syn_a(db_session, seed=1, weeks=16)
    _enable_f6(db_session)

    backtest = ai_forecast.backtest_vs_v1(db_session, result.ingredient.id)

    assert backtest.ok, backtest.message
    assert backtest.weeks_evaluated >= 4, "le document exige >= 4 semaines rejouées"
    assert backtest.mape_f6 < backtest.mape_v1
    assert backtest.improvement >= 0.15
    assert backtest.should_activate


def test_ia_01_backtest_refuses_activation_without_weekday_seasonality(db_session):
    """« Sinon, v1 reste. » Un ingrédient sans saisonnalité hebdomadaire ne
    doit PAS franchir le gate : sans ce contre-exemple, le test précédent
    ne prouverait que l'existence du calcul, pas sa sélectivité."""
    ing = syn.ingredient(db_session, "Ingrédient plat", stock_qty=10_000_000.0)
    plat = syn.dish(db_session, "Plat sans saison", {ing.id: 1.0})
    start = datetime(2026, 1, 5)
    quantites = syn.generate_weekly_quantities(
        random.Random(42), start=start, weeks=16, base_qty=20.0, noise_pct=0.10,
    )
    syn.import_sales_rows(db_session, [(d, plat.name, q, None) for d, q in quantites], filename="plat.csv")
    _enable_f6(db_session)

    backtest = ai_forecast.backtest_vs_v1(db_session, ing.id)

    assert backtest.ok, backtest.message
    assert not backtest.should_activate, (
        f"F6 ne gagne que {backtest.improvement:.1%} : sous les 15 % exigés, la v1 doit rester"
    )


def test_ia_01_backtest_never_reads_the_week_it_predicts(db_session):
    """Le rejeu doit être borné : une prévision calculée pour la semaine N
    ne doit pas changer si l'on modifie les ventes de la semaine N."""
    result = syn.build_syn_a(db_session, seed=1, weeks=16)
    _enable_f6(db_session)
    coupure = datetime(2026, 3, 2).date()  # un lundi, bien après le gate

    avant = ai_forecast.weekday_forecast(db_session, result.ingredient.id, as_of=coupure)

    a_venir = (
        db_session.query(models.SaleLine)
        .filter(models.SaleLine.sale_date >= datetime(2026, 3, 2))
        .all()
    )
    assert a_venir, "le jeu doit bien contenir des ventes après la coupure"
    for ligne in a_venir:
        ligne.quantity_sold = ligne.quantity_sold * 5
    db_session.commit()

    apres = ai_forecast.weekday_forecast(db_session, result.ingredient.id, as_of=coupure)
    assert apres.forecast.expected_daily_qty == avant.forecast.expected_daily_qty


def test_ia_04_forecast_is_deterministic_on_identical_data(db_session):
    """IA-04 : « rejeu sur données identiques -> résultat identique »."""
    result = syn.build_syn_a(db_session, seed=1, weeks=12)
    _enable_f6(db_session)

    premier = ai_forecast.weekday_forecast(db_session, result.ingredient.id).forecast
    second = ai_forecast.weekday_forecast(db_session, result.ingredient.id).forecast

    assert premier.expected_daily_qty == second.expected_daily_qty
    assert premier.closed_days == second.closed_days
