"""F5 — dérive de grammage et classification des écarts (docs/IA scope.md
§1.3-1.6), prouvée sur les jeux synthétiques SYN-B/C/D/E. Toute la
fonctionnalité est éteinte par défaut (`Settings.feature_f5_enabled`) —
chaque test l'active explicitement, et un test dédié prouve que l'éteindre
la neutralise vraiment plutôt que de le supposer.
"""
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


def test_syn_d_anomaly_ingredient_gets_unusual_not_recurring(db_session):
    result = syn.build_syn_d(db_session)
    _enable_f5(db_session)

    badge = ai_drift.classify_losses(db_session, result.ingredient_anomaly.id)

    assert badge is not None
    assert badge.kind == "inhabituel", f"attendu inhabituel, obtenu {badge.kind!r}"


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
