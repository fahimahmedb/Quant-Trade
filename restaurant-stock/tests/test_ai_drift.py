"""F5 — dérive de grammage et classification des écarts (docs/feature-plans/ia-f5-f9.md
§1.3-1.6), prouvée sur les jeux synthétiques SYN-B/C/D/E. Toute la
fonctionnalité est éteinte par défaut (`Settings.feature_f5_enabled`) —
chaque test l'active explicitement, et un test dédié prouve que l'éteindre
la neutralise vraiment plutôt que de le supposer.
"""
from datetime import datetime, timedelta

from app import models
from app.services import ai_drift, settings_service
from tests import synthetic_data as syn


def _enable_f5(db):
    settings_service.get_settings(db)  # crée la ligne settings si absente
    settings = db.get(models.Settings, 1)
    settings.feature_f5_enabled = True
    db.commit()


# ==========================================================================
# Feature flag — éteint par défaut, doit vraiment neutraliser F5
# ==========================================================================

def test_f5_is_inert_by_default_even_with_rich_drift_data(db_session):
    result = syn.build_syn_b(db_session)
    drift = ai_drift.detect_drift(db_session, result.ingredient.id)
    assert drift.proposal is None
    assert not drift.gate.ok
    assert "désactivée" in drift.explanation

    badge = ai_drift.classify_losses(db_session, result.ingredient.id)
    assert badge is None


def test_f5_produces_output_once_flag_enabled(db_session):
    result = syn.build_syn_b(db_session)
    _enable_f5(db_session)
    drift = ai_drift.detect_drift(db_session, result.ingredient.id)
    assert drift.proposal is not None, "le même jeu de données doit produire un résultat une fois le flag activé"


# ==========================================================================
# SYN-B — dérive détectée et correctement chiffrée
# ==========================================================================

def test_syn_b_drift_is_detected_within_expected_range(db_session):
    result = syn.build_syn_b(db_session)
    _enable_f5(db_session)

    drift = ai_drift.detect_drift(db_session, result.ingredient.id)

    assert drift.gate.ok
    assert drift.proposal is not None, drift.explanation
    assert drift.proposal.dish_id == result.dish_drifted.id
    assert drift.proposal.correlation >= 0.8
    # Attendu du document : correction entre 163 et 181 g (±5% de 172 g réels).
    assert 163.0 <= drift.proposal.proposed_quantity <= 181.0, drift.proposal.proposed_quantity


def test_syn_b_drift_proposal_targets_the_dish_not_the_untouched_one(db_session):
    result = syn.build_syn_b(db_session)
    _enable_f5(db_session)
    drift = ai_drift.detect_drift(db_session, result.ingredient.id)
    assert drift.proposal.dish_id != result.dish_other.id


# ==========================================================================
# SYN-C — contre-exemple : jamais de correction sans plat majoritaire
# ==========================================================================

def test_syn_c_never_proposes_a_correction_without_a_majority_dish(db_session):
    result = syn.build_syn_c(db_session)
    _enable_f5(db_session)

    drift = ai_drift.detect_drift(db_session, result.ingredient.id)

    assert drift.gate.ok, "le gate de données est atteint, l'écran ne doit pas confondre gate et attribution"
    assert drift.proposal is None, "aucun des 3 plats ne dépasse 50% : aucune correction ne doit être proposée"
    assert drift.explanation, "un message explicatif doit être présent"


# ==========================================================================
# SYN-D — perte récurrente / inhabituel / sous-seuil
# ==========================================================================

def test_syn_d_recurrent_ingredient_gets_the_recurring_badge_with_exact_cumulative(db_session):
    result = syn.build_syn_d(db_session)
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, result.ingredient_recurrent.id)

    assert badge is not None
    assert badge.kind == "perte_recurrente"
    assert badge.streak_length == 5
    attendu = sum(
        next(l for l in s.lines if l.ingredient_id == result.ingredient_recurrent.id).variance_value
        for s in result.recurrent_sessions
    )
    assert abs(badge.cumulative_value - attendu) < 0.001, "le cumul en euros doit être exact au centime"


def test_syn_d2_above_the_absolute_threshold_gets_unusual_not_recurring(db_session):
    """SYN-D2 (médiane historique nulle) : écart injecté juste au-dessus du
    seuil absolu réutilisé (`Settings.loss_alert_eur`) -> badge "inhabituel",
    jamais "récurrent" (avancement-lot-ia-0, décision actée — remplace
    l'ancien seuil de 50% du stock, qui ne raisonnait pas en euros)."""
    result = syn.build_syn_d(db_session, anomaly_above_threshold=True)
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, result.ingredient_anomaly.id)

    assert badge is not None
    assert badge.kind == "inhabituel", f"attendu inhabituel, obtenu {badge.kind!r}"


def test_syn_d2_below_the_absolute_threshold_gets_no_badge(db_session):
    """SYN-D2, frontière basse : le même écart isolé, injecté juste EN
    DESSOUS du seuil absolu, ne doit déclencher aucun badge."""
    result = syn.build_syn_d(db_session, anomaly_above_threshold=False)
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, result.ingredient_anomaly.id)

    assert badge is None


def test_syn_d1_at_3_1x_median_triggers_the_badge(db_session):
    """SYN-D1 (médiane historique non nulle) : la frontière exacte de la
    règle nominale (ANOMALY_RATIO = 3.0). Juste au-dessus -> badge."""
    result = syn.build_syn_d1(db_session, ratio=3.1)
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, result.ingredient.id)

    assert badge is not None and badge.kind == "inhabituel"


def test_syn_d1_at_2_9x_median_gives_no_badge(db_session):
    """Même jeu, juste EN DESSOUS de la frontière -> aucun badge. Sans ce
    contre-exemple, le test précédent ne prouverait que l'existence d'un
    seuil, pas sa valeur."""
    result = syn.build_syn_d1(db_session, ratio=2.9)
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, result.ingredient.id)

    assert badge is None


def test_syn_d_below_threshold_ingredient_gets_no_badge(db_session):
    result = syn.build_syn_d(db_session)
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, result.ingredient_below_threshold.id)

    assert badge is None, "seulement 2 comptages : sous le gate de 4, aucun badge ne doit sortir"


# ==========================================================================
# SYN-E — sous le gate : message honnête, aucune sortie F5
# ==========================================================================

def test_syn_e_reports_the_exact_gate_message(db_session):
    result = syn.build_syn_e(db_session)
    _enable_f5(db_session)

    drift = ai_drift.detect_drift(db_session, result.ingredient.id)
    badge = ai_drift.classify_losses(db_session, result.ingredient.id)

    assert not drift.gate.ok
    assert drift.gate.message == "3 comptages sur 4 nécessaires", drift.gate.message
    assert drift.proposal is None
    assert badge is None


# ==========================================================================
# Seuils de specs-v2-ia-plan-test.md §4 (F5) — gate, seuil réglable, motifs
# ==========================================================================

def _serie_ecarts(db, ecarts, nom="Seuils", jours_entre_comptages=7):
    """Un ingrédient, un plat, un comptage par période, avec l'écart voulu
    injecté à chaque fois. Consommation théorique par période : 10 plats
    x 100 g = 1000 g — donc un écart de 50 g vaut exactement le seuil par
    défaut de 5 %."""
    ing = syn.ingredient(db, f"Ingrédient {nom}", unit_cost=0.01, stock_qty=1_000_000.0)
    plat = syn.dish(db, f"Plat {nom}", {ing.id: 100.0})
    base = datetime(2026, 4, 1)
    sessions = []
    for i, ecart in enumerate(ecarts):
        d = base + timedelta(days=i * jours_entre_comptages)
        syn.import_sales_rows(db, [(d, plat.name, 10.0, None)], filename=f"{nom}_{i}.csv")
        sessions.append(syn.run_count_session(
            db, counted_by=nom, counted={ing.id: ing.current_theoretical_stock - ecart},
            ended_at=d + timedelta(hours=2),
        ))
    return ing, sessions


def test_gate_also_requires_four_weeks_of_sales_not_only_four_counts(db_session):
    """specs-v2 §4 (F5) : « >= 4 comptages validés ET >= 4 semaines de
    ventes ». Quatre comptages resserrés sur dix jours franchissent la
    première condition, pas la seconde."""
    ing, _ = _serie_ecarts(db_session, [0.0, 100.0, 100.0, 100.0], nom="Resserré", jours_entre_comptages=3)
    _enable_f5(db_session)

    gate = ai_drift.data_gate(db_session, ing.id)

    assert gate.completed_counts == 4, "la condition des comptages est bien atteinte"
    assert not gate.ok
    assert "semaines de ventes" in gate.message
    assert ai_drift.classify_losses(db_session, ing.id) is None


def test_recurring_badge_respects_the_configurable_threshold(db_session):
    """Le seuil « 5 % de la consommation théorique OU 10 € » est réglable
    (§8 : « valeurs de départ raisonnées, pas des constantes validées ») :
    des écarts de 4 % ne déclenchent rien par défaut, et le même jeu de
    données bascule dès que le réglage descend à 3 %."""
    ing, _ = _serie_ecarts(db_session, [0.0, 0.0, 40.0, 40.0, 40.0], nom="Sous seuil")
    _enable_f5(db_session)

    assert ai_drift.classify_losses(db_session, ing.id) is None, "4 % < 5 % et 0,40 € < 10 €"

    settings = db_session.get(models.Settings, 1)
    settings.loss_alert_pct = 3.0
    db_session.commit()

    badge = ai_drift.classify_losses(db_session, ing.id)
    assert badge is not None and badge.kind == "perte_recurrente"
    assert badge.streak_length == 3


def test_ac_f5_05_a_variance_with_a_reason_leaves_the_unexplained_cumulative(db_session):
    """AC-F5-5 : « écart avec motif "casse" saisi → exclu du cumul
    "inexpliqué", inclus dans le cumul total »."""
    ing, sessions = _serie_ecarts(db_session, [0.0, 0.0, 100.0, 100.0, 100.0], nom="Motif")
    _enable_f5(db_session)

    avant = ai_drift.classify_losses(db_session, ing.id)
    assert avant.kind == "perte_recurrente"
    assert avant.cumulative_value == avant.cumulative_value_total

    ligne = next(l for l in sessions[-1].lines if l.ingredient_id == ing.id)
    ligne.variance_reason = models.VarianceReason.CASSE
    db_session.commit()

    apres = ai_drift.classify_losses(db_session, ing.id)
    assert apres.streak_length == 3, "le motif ne casse pas la série : le document la conditionne au seul seuil"
    assert apres.cumulative_value_total == avant.cumulative_value_total
    assert apres.cumulative_value < apres.cumulative_value_total
    assert abs(apres.cumulative_value_total - apres.cumulative_value - ligne.variance_value) < 0.001


def test_unusual_badge_compares_to_the_median_not_the_mean(db_session):
    """specs-v2 §4 (F5) : « écart supérieur à 3 fois la MÉDIANE des écarts
    historiques ». Jeu choisi pour que médiane et moyenne ne disent pas la
    même chose : écarts antérieurs 20/20/20/20 (médiane 20), dernier écart
    70 — au-delà de 3 x 20, mais en deçà de 5 x la moyenne."""
    ing, _ = _serie_ecarts(db_session, [20.0, 20.0, 20.0, 20.0, 70.0], nom="Médiane")
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, ing.id)

    assert badge is not None and badge.kind == "inhabituel"
    assert "médiane" in badge.explanation
    assert "3.5 fois" in badge.explanation


def test_explanations_carry_their_numbers(db_session):
    """IA-03 : « phrase pourquoi présente, chiffres cohérents avec les
    données ». Le document donne le format attendu : « écart de 8 % sur 3
    comptages consécutifs, soit 64 € cumulés »."""
    ing, _ = _serie_ecarts(db_session, [0.0, 0.0, 100.0, 100.0, 100.0], nom="Explication")
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, ing.id)

    assert "10 % sur 3 comptages consécutifs" in badge.explanation
    assert "3.00 € cumulés" in badge.explanation  # 3 x 100 g x 0,01 €/g
