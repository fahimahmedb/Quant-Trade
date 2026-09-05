"""Validation du générateur synthétique lui-même (docs/IA scope.md §1-2),
avant de s'en servir pour prouver F5/F6/F7/F9. Si un jeu SYN a un défaut de
construction, un test qui l'utilise pourrait sembler passer pour une
mauvaise raison — ces tests vérifient la vérité terrain déclarée par
chaque builder, indépendamment de toute fonctionnalité IA.
"""
import random
from datetime import datetime

from app import models
from tests import synthetic_data as syn


def test_determinism_same_seed_produces_identical_output():
    """IA-04 (déterminisme, cité section 1.1) : même graine -> même sortie.
    Testé sur la primitive de génération directement, qui porte tout l'aléa
    des builders — plus rapide et plus précis qu'un aller-retour par la DB,
    et ça évite la collision de nom d'ingrédient qu'appeler un même builder
    deux fois dans la même base provoquerait (unicité de Ingredient.name)."""
    kwargs = dict(
        start=datetime(2026, 1, 5), weeks=12, base_qty=20.0,
        day_factors={1: 1.0, 2: 1.1, 3: 1.2, 4: 2.0, 5: 2.2, 6: 0.8},
        closed_days={0}, noise_pct=0.10,
    )
    out1 = syn.generate_weekly_quantities(random.Random(42), **kwargs)
    out2 = syn.generate_weekly_quantities(random.Random(42), **kwargs)
    assert out1 == out2, "la même graine doit reproduire exactement les mêmes quantités"


def test_different_seeds_produce_different_noise():
    kwargs = dict(
        start=datetime(2026, 1, 5), weeks=2, base_qty=20.0,
        day_factors={1: 1.0}, closed_days=set(), noise_pct=0.10,
    )
    out1 = syn.generate_weekly_quantities(random.Random(1), **kwargs)
    out2 = syn.generate_weekly_quantities(random.Random(2), **kwargs)
    assert out1 != out2, "deux graines différentes ne doivent pas produire le même bruit"


def test_syn_a_closes_monday_and_injects_expected_weekday_pattern(db_session):
    result = syn.build_syn_a(db_session, seed=1, weeks=12)
    lines = (
        db_session.query(models.SaleLine)
        .filter(models.SaleLine.dish_id == result.dish.id)
        .all()
    )
    weekdays_present = {line.sale_date.weekday() for line in lines}
    assert 0 not in weekdays_present, "aucune vente ne doit tomber un lundi (fermeture)"
    assert weekdays_present == set(result.day_factors), "tous les autres jours doivent être représentés"

    # La moyenne par jour doit refléter le facteur injecté à ±15% (marge de
    # sécurité au-delà du bruit ±10% déclaré, pour éviter un test fragile).
    par_jour: dict[int, list[float]] = {}
    for line in lines:
        par_jour.setdefault(line.sale_date.weekday(), []).append(line.quantity_sold)
    for wd, facteur in result.day_factors.items():
        moyenne = sum(par_jour[wd]) / len(par_jour[wd])
        attendu = result.base_daily_qty * facteur
        assert abs(moyenne - attendu) / attendu < 0.15, (
            f"jour {wd} : moyenne {moyenne:.2f} trop loin de l'attendu {attendu:.2f}"
        )


def test_syn_b_declared_quantity_drives_theoretical_stock_not_the_drift(db_session):
    """Le stock théorique de l'app ne doit jamais connaître les 172 g réels
    — seul le comptage physique révèle l'écart, comme en production."""
    result = syn.build_syn_b(db_session)
    total_burger = sum(result.burger_counts_per_period)

    theoretical_consumed_if_declared_used = total_burger * result.declared_g
    autre_lines = (
        db_session.query(models.SaleLine)
        .filter(models.SaleLine.dish_id == result.dish_other.id)
        .all()
    )
    autre_consumed = sum(line.quantity_sold * 60.0 for line in autre_lines)

    stock_final_attendu = 500_000.0 - theoretical_consumed_if_declared_used - autre_consumed
    # Le stock théorique après les ventes MAIS avant tout recalage de
    # comptage doit correspondre au grammage déclaré, jamais au réel.
    premiere_session = result.counts[0]
    ligne_avant_recalage = next(
        l for l in premiere_session.lines if l.ingredient_id == result.ingredient.id
    )
    # theoretical_quantity de la 1re session = stock juste après la 1re
    # période de ventes (avant recalage) : doit correspondre au déclaré.
    conso_periode_1 = (
        result.burger_counts_per_period[0] * result.declared_g + 32 * 60.0
    )
    assert ligne_avant_recalage.theoretical_quantity == 500_000.0 - conso_periode_1

    assert result.burger_share >= 0.5, "condition F5 : le plat testé doit peser au moins 50%"
    db_session.refresh(result.ingredient)


def test_syn_b_variance_correlates_with_drifted_dish_sales_volume(db_session):
    """Vérité terrain que F5 devra retrouver : l'écart par période est
    proportionnel au volume de burgers vendus (corrélation >= 0.8, exigée
    par le document) — jamais au volume de l'autre plat, constant."""
    result = syn.build_syn_b(db_session)
    # variance = theoretical - counted ; on a compté en dessous du théorique
    # (perte), donc variance > 0 pour chaque période.
    variances = [
        next(l for l in s.lines if l.ingredient_id == result.ingredient.id).variance
        for s in result.counts
    ]
    n = len(variances)
    burgers = result.burger_counts_per_period
    moy_b, moy_v = sum(burgers) / n, sum(variances) / n
    cov = sum((b - moy_b) * (v - moy_v) for b, v in zip(burgers, variances)) / n
    std_b = (sum((b - moy_b) ** 2 for b in burgers) / n) ** 0.5
    std_v = (sum((v - moy_v) ** 2 for v in variances) / n) ** 0.5
    correlation = cov / (std_b * std_v)
    assert correlation >= 0.8, f"corrélation trop faible pour que F5 l'attribue au burger : {correlation:.2f}"


def test_syn_c_three_dishes_share_consumption_equally(db_session):
    result = syn.build_syn_c(db_session)
    for p in result.dishes:
        lines = db_session.query(models.SaleLine).filter_by(dish_id=p.id).all()
        total = sum(l.quantity_sold for l in lines)
        assert total == 30.0 * 4, "chaque plat doit peser exactement le même volume"


def test_syn_d_recurrent_ingredient_has_five_consistent_variances(db_session):
    result = syn.build_syn_d(db_session)
    assert len(result.recurrent_sessions) == 5
    for session in result.recurrent_sessions:
        line = next(l for l in session.lines if l.ingredient_id == result.ingredient_recurrent.id)
        pct = abs(line.variance_pct)
        assert 5.0 < pct < 11.0, f"écart hors de la fourchette ~8% attendue : {pct:.1f}%"


def test_syn_d_anomaly_ingredient_is_conform_then_spikes_once(db_session):
    result = syn.build_syn_d(db_session)
    *conformes, dernier = result.anomaly_sessions
    for session in conformes:
        line = next(l for l in session.lines if l.ingredient_id == result.ingredient_anomaly.id)
        assert line.variance == 0.0
    ligne_finale = next(l for l in dernier.lines if l.ingredient_id == result.ingredient_anomaly.id)
    assert ligne_finale.variance > 0, "le dernier comptage doit montrer une perte massive isolée"


def test_syn_d_below_threshold_ingredient_has_only_two_sessions(db_session):
    result = syn.build_syn_d(db_session)
    assert len(result.below_threshold_sessions) == 2, "sous le seuil de 3 comptages exigé par F5"


def test_syn_e_is_under_both_gates(db_session):
    result = syn.build_syn_e(db_session)
    assert len(result.count_sessions) == 3, "sous le seuil de 4 comptages de F5"
    assert result.weeks == 4, "sous le seuil de 6 semaines de F6"


def test_syn_f_injects_a_100x_sale_and_a_zero_count(db_session):
    result = syn.build_syn_f(db_session)
    outlier = (
        db_session.query(models.SaleLine)
        .filter(models.SaleLine.dish_id == result.dish.id, models.SaleLine.sale_date == result.outlier_sale_date)
        .one()
    )
    normal_avg = result.clean.base_daily_qty * result.day_factors[result.outlier_sale_date.weekday()]
    assert outlier.quantity_sold > normal_avg * 50, "la vente aberrante doit être un ordre de grandeur x100"

    ligne = next(
        l for l in result.zero_count_session.lines if l.ingredient_id == result.ingredient.id
    )
    assert ligne.counted_quantity == 0.0


def test_syn_g_variants_have_distinct_shelf_life_and_delivery_pattern(db_session):
    g1 = syn.build_syn_g(db_session, variant="G1")
    g2 = syn.build_syn_g(db_session, variant="G2")
    g3 = syn.build_syn_g(db_session, variant="G3")
    assert g1.shelf_life_days == 5 and g1.delivery_weekdays == {1, 4}
    assert g2.order_cutoff_passed and not g1.order_cutoff_passed
    assert g3.shelf_life_days == 2 and g3.delivery_weekdays == {1}, (
        "G3 : conservation courte et une seule livraison/semaine -> fréquence insuffisante"
    )


def test_syn_h_theoretical_and_real_food_cost_hit_targets_within_tolerance(db_session):
    result = syn.build_syn_h(db_session)
    assert abs(result.theoretical_food_cost_pct - 30.0) < 0.05
    assert abs(result.real_food_cost_pct - 32.5) < 0.05

    receipts = (
        db_session.query(models.DeliveryLine)
        .filter(models.DeliveryLine.ingredient_id == result.ingredient.id)
        .all()
    )
    receipt_value = sum(r.quantity * r.unit_price for r in receipts)
    closing_line = next(
        l for l in result.closing_count.lines if l.ingredient_id == result.ingredient.id
    )
    opening_line = next(
        l for l in result.opening_count.lines if l.ingredient_id == result.ingredient.id
    )
    real_cost = (
        opening_line.counted_quantity * result.ingredient.unit_cost
        + receipt_value
        - closing_line.counted_quantity * result.ingredient.unit_cost
    )
    real_pct = real_cost / result.revenue * 100.0
    assert abs(real_pct - 32.5) < 0.1, "critère du document : ±0,1 point"


def test_syn_i_new_dish_has_partial_history_not_extrapolated(db_session):
    result = syn.build_syn_i(db_session)
    lignes_nouveau = (
        db_session.query(models.SaleLine).filter_by(dish_id=result.dish_new.id).all()
    )
    assert len(lignes_nouveau) == (result.weeks - result.new_dish_start_week) * 7
    lignes_ancien = (
        db_session.query(models.SaleLine).filter_by(dish_id=result.dish_existing.id).all()
    )
    assert len(lignes_ancien) == result.weeks * 7, "le plat ancien doit couvrir tout l'historique"
