"""F9 — food cost théorique vs réel (docs/feature-plans/ia-f5-f9.md §1.9), prouvée sur
SYN-H, à ±0,1 point comme l'exige le document. Éteinte par défaut
(`Settings.feature_f9_enabled`).
"""
from datetime import datetime, timedelta

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


# ==========================================================================
# Matrice popularité / marge — specs-v2-ia-plan-test.md §4 (F9)
# ==========================================================================

def _carte(db):
    """Quatre plats occupant chacun un quadrant, plus les deux cas que le
    document exige d'écarter (plat sans prix de vente, plat jamais vendu).
    Les ingrédients portent un coût unitaire de 1 €/unité pour que le coût
    matière d'un plat soit lisible directement dans son grammage."""
    ing = syn.ingredient(db, "Ingrédient matrice", unit_cost=1.0, stock_qty=1_000_000.0)
    plats = {
        # nom            : (grammage = coût matière, prix de vente, quantité vendue)
        "Star":            (3.0, 12.0, 100.0),   # très vendu, grosse marge
        "À retravailler":  (9.0, 12.0, 90.0),    # très vendu, marge faible
        "À pousser":       (3.0, 12.0, 10.0),    # peu vendu, grosse marge
        "À questionner":   (9.0, 12.0, 5.0),     # peu vendu, marge faible
    }
    crees = {nom: syn.dish(db, nom, {ing.id: cout}) for nom, (cout, _, _) in plats.items()}
    sans_prix = syn.dish(db, "Sans prix de vente", {ing.id: 4.0})
    jamais_vendu = syn.dish(db, "Jamais vendu", {ing.id: 4.0})

    debut = datetime(2026, 5, 4)
    rows = [(debut, nom, qty, prix) for nom, (_, prix, qty) in plats.items()]
    rows.append((debut, sans_prix.name, 50.0, None))
    syn.import_sales_rows(db, rows, filename="matrice.csv")
    return debut, crees, sans_prix, jamais_vendu


def test_matrix_is_inert_by_default(db_session):
    debut, *_ = _carte(db_session)
    result = ai_food_cost.popularity_margin_matrix(db_session, debut, debut + timedelta(days=1))
    assert not result.ok
    assert "désactivée" in result.message
    assert result.entries == []


def test_matrix_places_each_dish_in_the_named_quadrant_with_its_numbers(db_session):
    debut, plats, _, _ = _carte(db_session)
    _enable_f9(db_session)

    result = ai_food_cost.popularity_margin_matrix(db_session, debut, debut + timedelta(days=1))

    assert result.ok, result.message
    par_nom = {e.dish_name: e for e in result.entries}
    assert par_nom["Star"].quadrant == "stars"
    assert par_nom["À retravailler"].quadrant == "a_retravailler"
    assert par_nom["À pousser"].quadrant == "a_pousser"
    assert par_nom["À questionner"].quadrant == "a_questionner"
    assert par_nom["À retravailler"].label == "à retravailler"

    # « avec le chiffre derrière chaque position » (IA-03) : la phrase doit
    # porter la part des ventes, la marge unitaire et son détail.
    star = par_nom["Star"]
    assert star.unit_margin == 9.0 and star.unit_cost == 3.0
    assert star.total_margin == 900.0
    assert "% des ventes" in star.explanation
    assert "9.00 €" in star.explanation or "9,00" in star.explanation


def test_ac_f9_03_dish_without_sale_price_is_excluded_with_a_mention(db_session):
    debut, _, sans_prix, _ = _carte(db_session)
    _enable_f9(db_session)

    result = ai_food_cost.popularity_margin_matrix(db_session, debut, debut + timedelta(days=1))

    assert sans_prix.name in result.excluded_without_price
    assert sans_prix.name not in {e.dish_name for e in result.entries}
    assert len(result.entries) == 4, "les autres plats restent affichés"


def test_tc_f9_06_dish_never_sold_is_not_on_the_matrix(db_session):
    debut, _, _, jamais_vendu = _carte(db_session)
    _enable_f9(db_session)

    result = ai_food_cost.popularity_margin_matrix(db_session, debut, debut + timedelta(days=1))

    assert jamais_vendu.name not in {e.dish_name for e in result.entries}
    assert jamais_vendu.name not in result.excluded_without_price, (
        "un plat jamais vendu n'est pas « sans prix de vente » : il n'a simplement pas de position"
    )


def test_tc_f9_07_sum_of_margins_equals_revenue_minus_theoretical_food_cost(db_session):
    """TC-F9-07, cohérence entre deux chemins de calcul indépendants : la
    somme des marges de la matrice doit retomber sur CA − coût matière
    théorique calculé par `compute_food_cost`. Vérifié sur SYN-H, où tous
    les plats vendus ont un prix (condition de l'identité)."""
    result = syn.build_syn_h(db_session, weeks=8)
    _enable_f9(db_session)
    debut, fin = result.opening_count.ended_at, result.closing_count.ended_at

    cout = ai_food_cost.compute_food_cost(db_session, debut, fin)
    matrice = ai_food_cost.popularity_margin_matrix(db_session, debut, fin)

    somme_marges = sum(e.total_margin for e in matrice.entries)
    assert abs(somme_marges - (cout.revenue - cout.theoretical_cost)) < 0.01
