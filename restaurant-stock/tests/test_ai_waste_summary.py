"""F22 — gaspillage consolidé et valorisé (docs/feature-plans/
backlog-lot-ia-2.md ticket 1, cible SYN-Q). Chaque scénario a été vérifié
empiriquement (script autonome, base en mémoire) avant d'écrire
l'assertion dessus.

Le renvoi F17 est testé sur un fixture DÉDIÉ reproduisant EXACTEMENT la
répartition « 3 vendredis + 2 samedis » déjà prouvée déclenchante par
SYN-N (Lot IA-1) — la règle « affluence » de F17 prend la plus PETITE
série de jours qui atteint son seuil de concentration ; un premier essai
avec une répartition différente (4 vendredis + 1 samedi) s'est révélé ne
prendre en compte QUE le vendredi, qui n'était alors pas individuellement
le jour le plus vendeur de ce jeu précis (le samedi l'était de peu) — un
comportement réel et déjà couvert par les tests F17 du Lot IA-1, pas un
bug de F22. Réutiliser la répartition déjà prouvée évite de re-tester
F17 lui-même ici, ce qui n'est pas l'objet de ce fichier.
"""
import random
from datetime import datetime, timedelta

from app import models
from app.services import ai_waste_summary as waste, settings_service
from tests import synthetic_data as syn

DAY_FACTORS = {1: 1.0, 2: 1.1, 3: 1.2, 4: 2.0, 5: 2.2, 6: 0.8}
CLOSED_DAYS = {0}


def _enable(db, *, f22=True, f17=False, f14=False):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    if f22:
        settings.feature_f22_enabled = True
    if f17:
        settings.feature_f17_enabled = True
    if f14:
        settings.feature_f14_enabled = True
    db.commit()


def test_f22_is_inert_by_default(db_session):
    result = syn.build_syn_q(db_session)
    settings_service.get_settings(db_session)

    out = waste.waste_summary(db_session)

    assert not out.ok and "désactivée" in out.message
    assert out.entries == []


def test_no_loss_at_all_reports_zero(db_session):
    syn.ingredient(db_session, "Ingrédient propre", unit_cost=1.0)
    _enable(db_session)

    out = waste.waste_summary(db_session)

    assert out.ok, out.message
    assert out.total == 0.0
    assert out.entries == []
    assert "Aucune perte" in out.explanation


# ==========================================================================
# Agrégation — SYN-Q, montants connus
# ==========================================================================

def test_syn_q_totals_match_known_amounts(db_session):
    result = syn.build_syn_q(db_session)
    _enable(db_session)

    out = waste.waste_summary(db_session)

    assert out.ok, out.message
    assert out.explained_total == result.explained_total
    assert out.unexplained_total == result.unexplained_total
    assert out.total == result.explained_total + result.unexplained_total
    assert out.revenue == result.revenue
    assert abs(out.pct_of_revenue - 9.0) < 0.01


def test_syn_q_decoy_session_outside_the_window_is_excluded(db_session):
    """Non-vacuité par contre-exemple intégré à SYN-Q : une perte de 100 €
    existe hors fenêtre (150 jours). Si le filtre de fenêtre disparaissait,
    le total constaté sauterait de 18 € à 118 €."""
    result = syn.build_syn_q(db_session)
    _enable(db_session)

    out = waste.waste_summary(db_session)

    assert out.total == 18.0
    assert out.total != 18.0 + 100.0


def test_window_is_configurable(db_session):
    """Une fenêtre réduite à 10 jours ne doit plus voir QUE la perte la
    plus récente de SYN-Q (5 jours, motivée, 2 €) — pas les 4 comptages
    plus anciens."""
    syn.build_syn_q(db_session)
    _enable(db_session)
    settings = db_session.get(models.Settings, 1)
    settings.waste_summary_window_days = 10.0
    db_session.commit()

    out = waste.waste_summary(db_session)

    assert out.total == 2.0
    assert out.explained_total == 2.0
    assert out.unexplained_total == 0.0


# ==========================================================================
# Renvoi F17 — fixture dédié (répartition SYN-N, valeur au-dessus du seuil)
# ==========================================================================

def _ingredient_with_weekend_pattern(db, *, unit_cost: float, shortage: float, name: str):
    now = datetime.utcnow()
    rng = random.Random(5)
    ing = syn.ingredient(db, name, unit_cost=unit_cost, stock_qty=100_000.0)
    plat = syn.dish(db, f"Plat {name}", {ing.id: 1.0})
    start = now - timedelta(weeks=10)
    rows = syn.generate_weekly_quantities(
        rng, start=start, weeks=10, base_qty=20.0,
        day_factors=DAY_FACTORS, closed_days=CLOSED_DAYS, noise_pct=0.10,
    )
    syn.import_sales_rows(db, [(d, plat.name, q, None) for d, q in rows], filename=f"{name}.csv")

    def _at(weeks_ago: int, weekday_target: int) -> datetime:
        d = now - timedelta(weeks=weeks_ago)
        while d.weekday() != weekday_target:
            d -= timedelta(days=1)
        return d

    for weeks_ago, weekday_target in [(8, 4), (6, 4), (4, 4), (2, 5), (1, 5)]:  # 3 ven + 2 sam
        syn.run_count_session(
            db, counted_by="X", counted={ing.id: ing.current_theoretical_stock - shortage},
            ended_at=_at(weeks_ago, weekday_target),
        )
    for weeks_ago in [7, 5, 3]:
        syn.run_count_session(
            db, counted_by="X", counted={ing.id: ing.current_theoretical_stock - 5.0},
            motifs={ing.id: models.VarianceReason.CASSE}, ended_at=_at(weeks_ago, 1),
        )
    return ing


def test_f17_hypothesis_attached_above_threshold_with_f17_enabled(db_session):
    ing = _ingredient_with_weekend_pattern(
        db_session, unit_cost=1.0, shortage=15.0, name="Renvoi au-dessus du seuil",
    )
    _enable(db_session, f17=True)
    settings = db_session.get(models.Settings, 1)
    assert 5 * 15.0 >= settings.loss_alert_eur, "le jeu doit dépasser le seuil, sinon ce test ne prouve rien"

    out = waste.waste_summary(db_session)

    assert len(out.entries) == 1
    assert len(out.entries[0].hypotheses) == 1
    assert out.entries[0].hypotheses[0].kind == "affluence"


def test_no_f17_hypothesis_when_f17_is_disabled(db_session):
    """Non-vacuité par contre-exemple : même jeu, F17 éteint."""
    _ingredient_with_weekend_pattern(
        db_session, unit_cost=1.0, shortage=15.0, name="Renvoi F17 éteint",
    )
    _enable(db_session, f17=False)

    out = waste.waste_summary(db_session)

    assert len(out.entries) == 1
    assert out.entries[0].hypotheses == []


def test_no_f17_hypothesis_when_unexplained_value_is_below_the_threshold(db_session):
    """Non-vacuité par contre-exemple : F17 activé, gate F17 largement
    atteint (mêmes 5+3 comptages), mais la valeur unexpliquée (5 x 1 € =
    5 €) reste sous Settings.loss_alert_eur (10 € par défaut) — isole la
    clause de seuil de F22 de la clause de gate de F17."""
    _ingredient_with_weekend_pattern(
        db_session, unit_cost=1.0, shortage=1.0, name="Renvoi sous le seuil",
    )
    _enable(db_session, f17=True)

    out = waste.waste_summary(db_session)

    assert out.entries[0].unexplained_value == 5.0
    assert out.entries[0].hypotheses == []


# ==========================================================================
# F14 — risque à venir, jamais additionné
# ==========================================================================

def test_f14_at_risk_total_reported_separately(db_session):
    ing = syn.ingredient(db_session, "Ingrédient à risque", unit_cost=2.0, stock_qty=100.0)
    ing.shelf_life_days = 5.0
    db_session.commit()  # aucune vente : consommation nulle, tout le stock est "à risque"
    _enable(db_session, f14=True)

    out = waste.waste_summary(db_session)

    assert out.at_risk_total == 200.0  # 100 unités x 2,00 €
    assert out.total == 0.0
    assert "péremption" in out.explanation


def test_no_at_risk_total_when_f14_is_disabled(db_session):
    """Non-vacuité par contre-exemple : même stock à risque, F14 éteint."""
    ing = syn.ingredient(db_session, "Ingrédient à risque F14 éteint", unit_cost=2.0, stock_qty=100.0)
    ing.shelf_life_days = 5.0
    db_session.commit()
    _enable(db_session, f14=False)

    out = waste.waste_summary(db_session)

    assert out.at_risk_total == 0.0
