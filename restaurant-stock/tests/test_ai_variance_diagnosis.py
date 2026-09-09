"""F17 — diagnostic de cause d'écart (docs/feature-plans/ia-f10-f19.md §8,
cible SYN-N). Chaque scénario ci-dessous a été vérifié empiriquement
(script autonome, base en mémoire) avant d'écrire l'assertion dessus : les
seuils de concentration ne sont pas devinés, le comportement exact du jeu
de données l'est.

Convention commune à la plupart des fixtures locales (pas de jeu SYN dédié
au-delà de SYN-N, comme F12/F16/F18 dans ce même lot) : un ingrédient dont
les écarts NON expliqués (sans motif) sont scindés en deux catégories -
celle qui porte le signal testé (concentrée un jour, une zone, une date),
et 2-3 comptages MOTIVÉS (motif "casse") ajoutés uniquement pour satisfaire
le gate (§8 : « >= 3 écarts avec motif saisi ») sans polluer la série non
expliquée qu'analysent les règles.
"""
import random
from datetime import datetime, timedelta

from app import models
from app.services import ai_variance_diagnosis as diag, settings_service
from tests import synthetic_data as syn


def _enable(db, *, f17=True, f5=False):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    if f17:
        settings.feature_f17_enabled = True
    if f5:
        settings.feature_f5_enabled = True
    db.commit()


DAY_FACTORS_FLAT = {1: 1.0, 2: 1.1, 3: 1.2, 4: 1.15, 5: 1.2, 6: 0.9}  # affluence quasi plate
CLOSED_DAYS = {0}
START = datetime(2026, 1, 5)  # un lundi


def _at(week: int, weekday_offset: int) -> datetime:
    return START + timedelta(weeks=week, days=weekday_offset) + timedelta(hours=20)


def _build_ingredient_with_sales(db, name: str, *, seed: int, zone=models.StorageZone.SEC, day_factors=None):
    rng = random.Random(seed)
    ing = syn.ingredient(db, name, zone=zone, stock_qty=10_000_000.0)
    plat = syn.dish(db, f"Plat {name}", {ing.id: 1.0})
    rows = syn.generate_weekly_quantities(
        rng, start=START, weeks=10, base_qty=20.0,
        day_factors=day_factors or DAY_FACTORS_FLAT, closed_days=CLOSED_DAYS, noise_pct=0.10,
    )
    syn.import_sales_rows(db, [(d, plat.name, q, None) for d, q in rows], filename=f"{name}.csv")
    return ing


def _run_sessions(db, ing, *, unexplained: list[tuple[int, int]], motivated: list[tuple[int, int]]):
    for week, offset in unexplained:
        syn.run_count_session(
            db, counted_by="test", counted={ing.id: ing.current_theoretical_stock - 15.0},
            ended_at=_at(week, offset),
        )
    for week, offset in motivated:
        syn.run_count_session(
            db, counted_by="test", counted={ing.id: ing.current_theoretical_stock - 5.0},
            motifs={ing.id: models.VarianceReason.CASSE}, ended_at=_at(week, offset),
        )


def test_f17_is_inert_by_default(db_session):
    result = syn.build_syn_n(db_session)
    _enable(db_session, f17=False)

    out = diag.diagnose(db_session, result.ingredient.id)

    assert not out.gate.ok and "désactivée" in out.gate.message
    assert out.hypotheses == []


# ==========================================================================
# AC-F17-1 — jours de forte affluence (SYN-N)
# ==========================================================================

def test_ac_f17_1_weekend_concentrated_variances_on_syn_n(db_session):
    result = syn.build_syn_n(db_session)
    _enable(db_session)

    out = diag.diagnose(db_session, result.ingredient.id)

    assert out.gate.ok, out.gate.message
    kinds = [h.kind for h in out.hypotheses]
    assert kinds == ["affluence"], kinds
    assert "vendredi" in out.hypotheses[0].question and "samedi" in out.hypotheses[0].question


# ==========================================================================
# AC-F17-2 — aucun motif jamais saisi -> silencieux
# ==========================================================================

def test_ac_f17_2_no_motif_ever_entered_stays_silent(db_session):
    """EXACTEMENT la répartition non expliquée de SYN-N (5 comptages,
    100% vendredi/samedi — AC-F17-1 prouve juste au-dessus qu'elle
    déclenche bien "affluence" une fois le gate franchi), mais sans AUCUN
    motif saisi nulle part : sans ce fixture précis, la fermeture du gate
    serait indissociable d'une simple insuffisance de concentration."""
    ing = _build_ingredient_with_sales(db_session, "AC-F17-2 sans motif", seed=20)
    _run_sessions(
        db_session, ing,
        unexplained=[(2, 4), (3, 5), (5, 4), (7, 5), (9, 4)],
        motivated=[],
    )
    # Un 6e comptage, conforme et sans motif : franchit le seuil "6
    # comptages" du gate en isolant précisément ce que ce test vérifie
    # (aucun motif nulle part), plutôt que de rester bloqué sur l'autre
    # clause du même gate.
    syn.run_count_session(
        db_session, counted_by="test", counted={ing.id: ing.current_theoretical_stock},
        ended_at=_at(1, 2),
    )
    _enable(db_session)

    out = diag.diagnose(db_session, ing.id)

    assert not out.gate.ok
    assert out.gate.completed_counts >= diag.MIN_COMPLETED_COUNTS
    assert "motif" in out.gate.message
    assert out.hypotheses == []


# ==========================================================================
# AC-F17-3 — formulation systématiquement interrogative
# ==========================================================================

def test_ac_f17_3_every_hypothesis_is_phrased_as_a_question(db_session):
    result = syn.build_syn_n(db_session)
    _enable(db_session)

    out = diag.diagnose(db_session, result.ingredient.id)

    assert out.hypotheses
    for h in out.hypotheses:
        assert h.question.strip().endswith("?"), h.question


def test_no_affluence_hypothesis_when_the_concentrated_day_is_not_high_traffic(db_session):
    """Non-vacuité du croisement avec les ventes réelles (docstring du
    module) : les écarts non expliqués sont concentrés à 100% sur UN seul
    jour (dimanche), mais c'est le jour le PLUS CREUX en volume de vente,
    pas un jour de forte affluence. Sans le croisement, la seule
    concentration suffirait à déclencher l'hypothèse — ni ce test ni
    TC-F17-04 (dispersé, jamais concentré) ne le prouveraient alors."""
    day_factors = {1: 1.2, 2: 1.2, 3: 1.2, 4: 1.2, 5: 1.2, 6: 0.3}
    ing = _build_ingredient_with_sales(db_session, "Jour creux concentré", seed=35, day_factors=day_factors)
    for week in [1, 2, 3, 4, 5]:
        syn.run_count_session(
            db_session, counted_by="test", counted={ing.id: ing.current_theoretical_stock - 15.0},
            ended_at=_at(week, 6),
        )
    _run_sessions(db_session, ing, unexplained=[], motivated=[(6, 1), (7, 2), (8, 3)])
    _enable(db_session)

    out = diag.diagnose(db_session, ing.id)

    assert out.gate.ok, out.gate.message
    assert "affluence" not in [h.kind for h in out.hypotheses]


# ==========================================================================
# TC-F17-04 — écarts aléatoires sans structure -> aucune hypothèse
# ==========================================================================

def test_tc_f17_04_no_structure_no_hypothesis_invented(db_session):
    """Non-vacuité par construction : les mêmes 6 écarts non expliqués que
    SYN-N (en nombre), mais répartis sur 6 jours de semaine DIFFÉRENTS —
    si le code inventait une corrélation, ce test le prouverait."""
    ing = _build_ingredient_with_sales(db_session, "TC-F17-04 sans structure", seed=21)
    _run_sessions(
        db_session, ing,
        unexplained=[(1, 1), (2, 2), (4, 3), (5, 4), (7, 5), (8, 6)],
        motivated=[(3, 1), (6, 3), (9, 2)],
    )
    _enable(db_session)

    out = diag.diagnose(db_session, ing.id)

    assert out.gate.ok, out.gate.message
    assert out.hypotheses == [], [h.kind for h in out.hypotheses]


# ==========================================================================
# TC-F17-05 — deux causes plausibles simultanées -> les deux proposées
# ==========================================================================

def test_tc_f17_05_two_simultaneous_causes_both_proposed(db_session):
    """SYN-N (affluence) + l'ingrédient placé dans une zone où 2 autres
    ingrédients montrent eux aussi des écarts non expliqués (zone) : les
    deux hypothèses doivent sortir, pas un choix arbitraire entre elles."""
    result = syn.build_syn_n(db_session)
    result.ingredient.storage_zone = models.StorageZone.FRIGO_NEGATIF
    db_session.commit()

    peer1 = _build_ingredient_with_sales(db_session, "TC-F17-05 peer 1", seed=22, zone=models.StorageZone.FRIGO_NEGATIF)
    _run_sessions(db_session, peer1, unexplained=[(2, 3)], motivated=[])
    peer2 = _build_ingredient_with_sales(db_session, "TC-F17-05 peer 2", seed=23, zone=models.StorageZone.FRIGO_NEGATIF)
    _run_sessions(db_session, peer2, unexplained=[(3, 2)], motivated=[])
    _build_ingredient_with_sales(db_session, "TC-F17-05 peer clean", seed=24, zone=models.StorageZone.FRIGO_NEGATIF)

    _enable(db_session)

    out = diag.diagnose(db_session, result.ingredient.id)

    kinds = {h.kind for h in out.hypotheses}
    assert kinds == {"affluence", "zone"}, kinds


# ==========================================================================
# Règle "zone" — isolée, avec contre-exemple
# ==========================================================================

def test_zone_hypothesis_when_peers_share_the_pattern(db_session):
    ing = _build_ingredient_with_sales(db_session, "Zone cible", seed=25, zone=models.StorageZone.FRIGO_NEGATIF)
    _run_sessions(
        db_session, ing,
        unexplained=[(1, 1), (2, 2), (4, 3), (5, 4)],  # jours variés : n'active pas "affluence"
        motivated=[(3, 1), (6, 3), (9, 2)],
    )
    peer1 = _build_ingredient_with_sales(db_session, "Zone peer 1", seed=26, zone=models.StorageZone.FRIGO_NEGATIF)
    _run_sessions(db_session, peer1, unexplained=[(2, 3)], motivated=[])
    peer2 = _build_ingredient_with_sales(db_session, "Zone peer 2", seed=27, zone=models.StorageZone.FRIGO_NEGATIF)
    _run_sessions(db_session, peer2, unexplained=[(3, 2)], motivated=[])
    _build_ingredient_with_sales(db_session, "Zone peer clean", seed=28, zone=models.StorageZone.FRIGO_NEGATIF)
    _enable(db_session)

    out = diag.diagnose(db_session, ing.id)

    kinds = [h.kind for h in out.hypotheses]
    assert kinds == ["zone"], kinds
    assert "Frigo négatif" in out.hypotheses[0].question


def test_no_zone_hypothesis_when_peers_stay_clean(db_session):
    """Non-vacuité par contre-exemple : mêmes écarts sur l'ingrédient
    cible, mais AUCUN pair de la zone n'est touché."""
    ing = _build_ingredient_with_sales(db_session, "Zone cible propre", seed=29, zone=models.StorageZone.FRIGO_NEGATIF)
    _run_sessions(
        db_session, ing,
        unexplained=[(1, 1), (2, 2), (4, 3), (5, 4)],
        motivated=[(3, 1), (6, 3), (9, 2)],
    )
    _build_ingredient_with_sales(db_session, "Zone peer propre 1", seed=30, zone=models.StorageZone.FRIGO_NEGATIF)
    _build_ingredient_with_sales(db_session, "Zone peer propre 2", seed=31, zone=models.StorageZone.FRIGO_NEGATIF)
    _build_ingredient_with_sales(db_session, "Zone peer propre 3", seed=32, zone=models.StorageZone.FRIGO_NEGATIF)
    _enable(db_session)

    out = diag.diagnose(db_session, ing.id)

    assert "zone" not in [h.kind for h in out.hypotheses]


# ==========================================================================
# Règle "date" — isolée, avec contre-exemple
# ==========================================================================

def test_date_hypothesis_on_a_clean_break(db_session):
    ing = _build_ingredient_with_sales(db_session, "Cassure de date", seed=33)
    _run_sessions(
        db_session, ing,
        unexplained=[(5, 1), (6, 2), (7, 3), (8, 4), (9, 5)],
        motivated=[(1, 1), (3, 3), (9, 6)],
    )
    # conforme, avant la cassure : complète le "avant" propre
    syn.run_count_session(
        db_session, counted_by="test", counted={ing.id: ing.current_theoretical_stock},
        ended_at=_at(2, 2),
    )
    syn.run_count_session(
        db_session, counted_by="test", counted={ing.id: ing.current_theoretical_stock},
        ended_at=_at(4, 4),
    )
    _enable(db_session)

    out = diag.diagnose(db_session, ing.id)

    kinds = [h.kind for h in out.hypotheses]
    assert kinds == ["date"], kinds


def test_no_date_hypothesis_when_variances_are_spread_out(db_session):
    """Non-vacuité par contre-exemple : le fixture TC-F17-04 (déjà
    dispersé sur des jours différents) est aussi dispersé dans le temps
    (pas de série "propre avant / sale après") — aucune hypothèse date."""
    ing = _build_ingredient_with_sales(db_session, "Pas de cassure", seed=34)
    _run_sessions(
        db_session, ing,
        unexplained=[(1, 1), (2, 2), (4, 3), (5, 4), (7, 5), (8, 6)],
        motivated=[(3, 1), (6, 3), (9, 2)],
    )
    _enable(db_session)

    out = diag.diagnose(db_session, ing.id)

    assert "date" not in [h.kind for h in out.hypotheses]


# ==========================================================================
# Règle "fiche technique" (renvoi F5) — isolée, avec contre-exemple
# ==========================================================================

def _build_f5_drift_and_f17_gate(db):
    """Même relation linéaire que SYN-B (F5), étendue à 9 comptages sur
    des jours de semaine variés (pour ne pas aussi déclencher "affluence")
    et 3 d'entre eux motivés (pour satisfaire le gate F17) — la
    corrélation ne porte que sur les quantités par période, jamais sur le
    jour de semaine ni le motif, donc ni l'un ni l'autre ne l'affaiblit."""
    rng = random.Random(2)
    declared_g, actual_g = 150.0, 172.0
    drift_g = actual_g - declared_g
    autre_g = 60.0
    autre_n = 32

    steak = syn.ingredient(db, "Steak renvoi F5", unit_cost=0.012, stock_qty=500_000.0)
    burger = syn.dish(db, "Burger renvoi F5", {steak.id: declared_g})
    autre = syn.dish(db, "Assiette renvoi F5", {steak.id: autre_g})

    burger_counts = [40, 65, 30, 75, 45, 55, 50, 60, 35]
    weekday_shifts = [0, 2, 4, 1, 3, 5, 6, 2, 4]
    motif_indices = {1, 4, 7}

    start = datetime(2026, 2, 2)
    for i, burger_n in enumerate(burger_counts):
        period_start = start + timedelta(days=i * 7 + weekday_shifts[i])
        rows = [
            (period_start, burger.name, float(burger_n), None),
            (period_start, autre.name, float(autre_n), None),
        ]
        syn.import_sales_rows(db, rows, filename=f"renvoi_{i}.csv")
        vrai_manque = syn.noisy(rng, drift_g * burger_n, 0.10)
        motifs = {steak.id: models.VarianceReason.CASSE} if i in motif_indices else None
        syn.run_count_session(
            db, counted_by="test", counted={steak.id: steak.current_theoretical_stock - vrai_manque},
            motifs=motifs, ended_at=period_start + timedelta(hours=2),
        )
    return steak, burger


def test_fiche_technique_renvoi_when_f5_has_a_proposal(db_session):
    steak, burger = _build_f5_drift_and_f17_gate(db_session)
    _enable(db_session, f5=True)

    out = diag.diagnose(db_session, steak.id)

    kinds = [h.kind for h in out.hypotheses]
    assert kinds == ["fiche_technique"], kinds
    assert burger.name in out.hypotheses[0].question


def test_no_fiche_technique_renvoi_when_f5_is_disabled(db_session):
    """Non-vacuité par contre-exemple : même jeu, F5 éteint -> F17 ne doit
    pas se rabattre sur sa propre hypothèse de dérive."""
    steak, _burger = _build_f5_drift_and_f17_gate(db_session)
    _enable(db_session, f5=False)

    out = diag.diagnose(db_session, steak.id)

    assert "fiche_technique" not in [h.kind for h in out.hypotheses]
