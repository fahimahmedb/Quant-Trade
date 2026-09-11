"""F27 — apprentissage statistique réel (docs/feature-plans, cible SYN-V).
Chaque seuil ci-dessous a été vérifié empiriquement (scripts autonomes
probe_f27_hw.py puis probe_f27_real.py, scratchpad) avant d'être écrit en
assertion — en particulier le contraste F27/F6 sur données à tendance,
qui est le cœur de ce que ce ticket doit prouver, pas seulement affirmer.
"""
from datetime import date, datetime, timedelta

from app import models
from app.services import ai_forecast, ai_forecast_learned as fl, settings_service
from tests import synthetic_data as syn


def _enable(db, *, f27=True, f6=True):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    if f6:
        settings.feature_f6_enabled = True
    if f27:
        settings.feature_f27_enabled = True
    db.commit()


def test_f27_is_inert_by_default(db_session):
    result = syn.build_syn_v(db_session)
    _enable(db_session, f27=False)

    out = fl.learned_forecast(db_session, result.ingredient.id, as_of=result.start + timedelta(weeks=result.weeks))

    assert not out.ok and "désactivée" in out.message


def test_gate_matches_f6_threshold(db_session):
    """Même gate que F6 (6 semaines) — une comparaison n'a de sens que si
    les deux modèles se déclenchent au même moment."""
    result = syn.build_syn_v(db_session, weeks=5)  # sous le seuil
    _enable(db_session)

    out = fl.learned_forecast(db_session, result.ingredient.id, as_of=result.start + timedelta(weeks=5))

    assert not out.ok and "6 nécessaires" in out.message


def test_learned_forecast_beats_naive_weighted_average_on_trending_data(db_session):
    """Le cœur du ticket : sur une activité en croissance régulière (SYN-V),
    F6 (moyenne pondérée du passé récent, aucun terme de tendance) reste
    structurellement en retard sur la réalité — vérifié empiriquement à
    ~18 % d'erreur moyenne contre ~10 % pour F27, qui extrapole la
    tendance apprise."""
    result = syn.build_syn_v(db_session)
    _enable(db_session)
    as_of = result.start + timedelta(weeks=result.weeks)

    f27_out = fl.learned_forecast(db_session, result.ingredient.id, as_of=as_of)
    f6_out = ai_forecast.weekday_forecast(db_session, result.ingredient.id, as_of=as_of)

    assert f27_out.ok, f27_out.message
    assert f6_out.gate_ok, f6_out.gate_message

    expected_level = result.base_start + result.growth_per_week * result.weeks
    expected = {wd: expected_level * result.day_factors[wd] for wd in range(7)}

    f27_errors = [abs(f27_out.expected_daily_qty[wd] - expected[wd]) / expected[wd] for wd in range(7)]
    f6_errors = [abs(f6_out.forecast.expected_daily_qty[wd] - expected[wd]) / expected[wd] for wd in range(7)]
    f27_mape = sum(f27_errors) / len(f27_errors)
    f6_mape = sum(f6_errors) / len(f6_errors)

    assert f27_mape < 0.15, f"F27 attendu sous 15% d'erreur, obtenu {f27_mape:.1%}"
    assert f6_mape > 0.15, f"F6 attendu structurellement au-dessus de 15% sur cette tendance, obtenu {f6_mape:.1%}"
    assert f27_mape < f6_mape


def test_learned_forecast_reports_a_positive_trend(db_session):
    result = syn.build_syn_v(db_session)
    _enable(db_session)

    out = fl.learned_forecast(db_session, result.ingredient.id, as_of=result.start + timedelta(weeks=result.weeks))

    assert out.ok, out.message
    assert out.trend_per_day > 0.5  # croissance connue de 1.5/semaine ~= 0.21/jour de tendance de fond, mesuré ~1.08
    assert "hausse" in out.explanation


def test_closed_day_is_learned_without_a_dedicated_rule(db_session):
    """Contrairement à F6 (règle explicite « >= 4 occurrences à zéro »),
    F27 ne code AUCUNE notion de jour fermé. Fermeture introduite
    seulement à partir de la semaine 5 (sur 12) — jamais dès le premier
    jour — pour que la preuve porte sur une vraie ADAPTATION en cours de
    route (l'indice saisonnier initial, dérivé de la toute première
    semaine, montrerait encore un dimanche ouvert) et non sur ce que
    l'initialisation aurait de toute façon déjà capturé correctement
    (vérifié empiriquement : une fermeture dès le premier jour ne
    dépend PAS de γ, l'initialisation seule suffit — un test qui n'aurait
    rien prouvé sur l'apprentissage lui-même)."""
    ing = syn.ingredient(db_session, "Fermeture récente", stock_qty=10_000_000.0)
    plat = syn.dish(db_session, "Plat fermeture récente", {ing.id: 1.0})
    import random
    rng = random.Random(55)
    start = date(2026, 1, 5)  # lundi
    closure_start_week = 5
    total_weeks = 12
    rows = []
    for week in range(total_weeks):
        for wd in range(7):
            d = start + timedelta(days=week * 7 + wd)
            if wd == 6 and week >= closure_start_week:
                continue  # fermé le dimanche seulement à partir de la semaine 5
            rows.append((datetime(d.year, d.month, d.day), plat.name, syn.noisy(rng, 20.0, 0.10), None))
    syn.import_sales_rows(db_session, rows, filename="fermeture_recente.csv")
    _enable(db_session)

    out = fl.learned_forecast(db_session, ing.id, as_of=start + timedelta(weeks=total_weeks))

    assert out.ok, out.message
    assert out.expected_daily_qty[6] < 3.0  # dimanche : la fermeture récente a été apprise
    for wd in range(6):
        assert out.expected_daily_qty[wd] > 10.0  # les autres jours restent au niveau réel (~20)


def test_different_ingredients_learn_different_parameters(db_session):
    """La preuve la plus directe que ce ne sont pas des règles : deux
    ingrédients aux profils différents (l'un en tendance forte et
    saisonnier, SYN-V ; l'autre plat et quasi sans bruit) doivent obtenir
    des (α, β, γ) DIFFÉRENTS — jamais une constante unique appliquée à
    tout le monde, contrairement à `cold_start_smoothing_days` (F23) ou
    `MIN_PAST_OCCURRENCES` (F20)."""
    result = syn.build_syn_v(db_session)

    ing_flat = syn.ingredient(db_session, "Plat stable", stock_qty=10_000_000.0)
    plat_flat = syn.dish(db_session, "Plat sans tendance", {ing_flat.id: 1.0})
    import random
    rng = random.Random(99)
    start_flat = date(2026, 1, 5)
    rows = []
    for day_offset in range(12 * 7):
        d = start_flat + timedelta(days=day_offset)
        rows.append((datetime(d.year, d.month, d.day), plat_flat.name, syn.noisy(rng, 20.0, 0.02), None))
    syn.import_sales_rows(db_session, rows, filename="flat.csv")
    _enable(db_session)

    out_v = fl.learned_forecast(db_session, result.ingredient.id, as_of=result.start + timedelta(weeks=result.weeks))
    out_flat = fl.learned_forecast(db_session, ing_flat.id, as_of=start_flat + timedelta(weeks=12))

    assert out_v.ok and out_flat.ok
    params_v = (out_v.params.alpha, out_v.params.beta, out_v.params.gamma)
    params_flat = (out_flat.params.alpha, out_flat.params.beta, out_flat.params.gamma)
    assert params_v != params_flat


def test_compare_models_prefers_f27_on_trending_data(db_session):
    """Étend backtest_vs_v1 (F18) à 3 candidats : sur SYN-V, le vainqueur
    empirique doit être F27, jamais supposé."""
    result = syn.build_syn_v(db_session)
    _enable(db_session)

    out = fl.compare_models(db_session, result.ingredient.id)

    assert out.ok, out.message
    assert out.weeks_evaluated >= 4
    assert out.mape_f27 is not None and out.mape_f6 is not None
    assert out.mape_f27 < out.mape_f6
    assert out.mape_f27 < out.mape_v1
    assert out.best_model == "F27"


def test_compare_models_can_prefer_v1_when_there_is_no_trend_to_learn(db_session):
    """La comparaison n'est pas truquée en faveur de F27 : sur une
    activité déjà plate et stable (SYN-W, sans tendance), rien ne
    justifie la variance supplémentaire d'un modèle à 3 paramètres jugés
    sur une seule semaine de validation — la simple moyenne glissante
    (v1) gagne, F27 doit explicitement faire MOINS bien qu'elle ET que F6
    (vérifié empiriquement avant d'écrire ce test : v1 ≈5,5 %, F6 ≈5,8 %,
    F27 ≈8,5 % d'erreur — le modèle le plus simple gagne quand il n'y a
    rien à extrapoler, exactement ce qu'on attend d'une vraie comparaison)."""
    result = syn.build_syn_w(db_session)
    _enable(db_session)

    out = fl.compare_models(db_session, result.ingredient.id)

    assert out.ok, out.message
    assert out.mape_f6 is not None and out.mape_f27 is not None
    assert out.mape_f27 > out.mape_f6 > out.mape_v1
    assert out.best_model == "v1"


def test_learned_forecast_handles_declining_trend_symmetrically(db_session):
    """SYN-V prouve l'extrapolation à la hausse ; SYN-X (même construction,
    signe opposé) prouve qu'elle fonctionne aussi à la baisse — pas un
    artefact d'une seule direction testée."""
    result = syn.build_syn_x(db_session)
    _enable(db_session)
    as_of = result.start + timedelta(weeks=result.weeks)

    out = fl.learned_forecast(db_session, result.ingredient.id, as_of=as_of)

    assert out.ok, out.message
    assert out.trend_per_day < -0.1

    expected_level = max(1.0, result.base_start - result.decline_per_week * result.weeks)
    expected = {wd: expected_level * result.day_factors[wd] for wd in range(7)}
    errors = [abs(out.expected_daily_qty[wd] - expected[wd]) / expected[wd] for wd in range(7)]
    assert sum(errors) / len(errors) < 0.15


def test_compare_models_prefers_f27_on_declining_trend_too(db_session):
    result = syn.build_syn_x(db_session)
    _enable(db_session)

    out = fl.compare_models(db_session, result.ingredient.id)

    assert out.ok, out.message
    assert out.mape_f27 is not None and out.mape_f6 is not None
    assert out.mape_f27 < out.mape_f6
    assert out.mape_f27 < out.mape_v1
    assert out.best_model == "F27"
