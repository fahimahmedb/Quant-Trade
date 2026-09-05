"""F7 — cycle de commande conscient de la livraison (docs/IA scope.md
§1.8), prouvée sur les trois variantes de SYN-G. `plan_order_cycle` est une
fonction pure (aucun accès DB) : les tests G1/G2/G3 vérifient directement
son arithmétique, sans passer par la base ni par un feature flag — c'est
`plan_order_cycle_for_ingredient` (la version branchée sur la base) qui est
gatée, testée séparément plus bas.
"""
from datetime import datetime, timedelta

from app import models
from app.services import ai_forecast, ai_ordering, settings_service
from tests import synthetic_data as syn


def _enable_f7(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f7_enabled = True
    db.commit()


def _plan(g):
    return ai_ordering.plan_order_cycle(
        today=g.today, delivery_weekdays=g.delivery_weekdays, shelf_life_days=g.shelf_life_days,
        daily_consumption=g.daily_consumption, current_stock=g.current_stock,
        pack_size=g.pack_size, order_cutoff_passed=g.order_cutoff_passed,
    )


# ==========================================================================
# G1 — nominal : couvre jusqu'à la livraison suivante, arrondi au conditionnement
# ==========================================================================

def test_g1_targets_next_delivery_and_covers_until_the_one_after(db_session):
    g1 = syn.build_syn_g(db_session, variant="G1")
    result = _plan(g1)

    assert result.ok
    assert result.target_delivery.weekday() == 4, "mercredi -> la prochaine livraison est vendredi"
    assert result.covers_until.weekday() == 1, "doit couvrir jusqu'au mardi suivant"
    # 4 jours (ven->mar) x 2 kg/jour = 8 kg, stock épuisé d'ici la livraison -> arrondi à 10 kg (2x5kg).
    assert result.suggested_quantity == 10_000.0
    assert not result.warnings


# ==========================================================================
# G2 — heure limite dépassée : bascule sur la livraison suivante
# ==========================================================================

def test_g2_skips_to_the_delivery_after_when_cutoff_has_passed(db_session):
    g2 = syn.build_syn_g(db_session, variant="G2")
    result = _plan(g2)

    assert result.ok
    assert result.target_delivery.weekday() == 1, "cutoff dépassé pour vendredi -> bascule sur mardi suivant"
    assert "heure limite" in result.message.lower()
    # 3 jours (mar->ven) x 2 kg/jour = 6 kg -> arrondi à 10 kg (2x5kg).
    assert result.suggested_quantity == 10_000.0


def test_g1_and_g2_target_different_deliveries_for_the_same_starting_point(db_session):
    g1 = syn.build_syn_g(db_session, variant="G1")
    g2 = syn.build_syn_g(db_session, variant="G2")
    assert _plan(g1).target_delivery != _plan(g2).target_delivery


# ==========================================================================
# G3 — conservation courte, livraison trop rare : plafond + avertissement
# ==========================================================================

def test_g3_caps_at_shelf_life_and_warns_about_delivery_frequency(db_session):
    g3 = syn.build_syn_g(db_session, variant="G3")
    result = _plan(g3)

    assert result.ok
    assert result.warnings, "le plafond péremption doit produire un avertissement explicite"
    # Plafond : 2 jours de conservation x 2 kg/jour = 4 kg, mais le
    # conditionnement minimal (5 kg) dépasse déjà cette limite.
    assert "insuffisante" in result.warnings[0].lower()
    assert result.suggested_quantity <= g3.shelf_life_days * g3.daily_consumption + g3.pack_size


def test_g3_suggested_quantity_is_lower_than_the_uncapped_g1_equivalent(db_session):
    """Le plafond doit vraiment réduire la quantité, pas juste ajouter un
    message à côté d'un calcul inchangé."""
    g1 = syn.build_syn_g(db_session, variant="G1")
    g3 = syn.build_syn_g(db_session, variant="G3")
    assert _plan(g3).suggested_quantity < _plan(g1).suggested_quantity


# ==========================================================================
# Version branchée sur la base — feature flag et repli sur la v1
# ==========================================================================

def test_f7_is_inert_by_default(db_session):
    ing = syn.ingredient(db_session, "Tomate F7", stock_qty=1000.0)
    ing.shelf_life_days = 5
    ing.delivery_weekdays = "1,4"
    ing.pack_size = 5000.0
    db_session.commit()

    result = ai_ordering.plan_order_cycle_for_ingredient(db_session, ing.id)
    assert not result.ok
    assert "désactivée" in result.message


def test_f7_falls_back_to_v1_rolling_average_without_optional_fields(db_session):
    """Zéro saisie obligatoire (principe des specs V2) : un ingrédient sans
    conservation/livraison/conditionnement renseignés ne doit jamais planter,
    juste rester sur la règle v1."""
    ing = syn.ingredient(db_session, "Sel F7", stock_qty=1000.0)
    _enable_f7(db_session)

    result = ai_ordering.plan_order_cycle_for_ingredient(db_session, ing.id)

    assert not result.ok
    assert "v1" in result.message.lower()


def test_f7_uses_f6_forecast_when_its_own_gate_is_met(db_session):
    a = syn.build_syn_a(db_session, seed=1, weeks=12)
    a.ingredient.shelf_life_days = 30
    a.ingredient.delivery_weekdays = "1,4"
    a.ingredient.pack_size = 1.0
    # SYN-A part d'un stock volontairement énorme (pour ne jamais aller au
    # négatif sous les ventes) : sans un stock bas ici, "needed" retombe à 0
    # quel que soit le rythme de consommation utilisé, et le test ne
    # prouverait rien.
    a.ingredient.current_theoretical_stock = 10.0
    db_session.commit()
    settings_service.get_settings(db_session)
    settings = db_session.get(models.Settings, 1)
    settings.feature_f6_enabled = True
    settings.feature_f7_enabled = True
    db_session.commit()

    # Un vendredi (facteur 2,0, le plus haut de la semaine, dans la fenêtre
    # de 12 semaines de SYN-A).
    un_vendredi = datetime(2026, 1, 9)

    outcome = ai_forecast.weekday_forecast(db_session, a.ingredient.id)
    assert outcome.gate_ok
    prevision_vendredi = outcome.forecast.expected_daily_qty[un_vendredi.weekday()]

    # Preuve directe que le rythme utilisé est celui de F6 : brancher
    # manuellement la même prévision dans la fonction pure doit reproduire
    # exactement ce que la version branchée sur la base a calculé — pas une
    # comparaison indirecte à une moyenne v1, faussée ici par un détail sans
    # rapport (StockMovement.created_at est horodaté à l'exécution réelle du
    # test, pas à la date synthétique des ventes : la fenêtre glissante v1
    # ne mesure donc pas ce qu'elle croit mesurer sur des données de test
    # antidatées, un artefact de la génération, pas de F7 lui-même).
    attendu = ai_ordering.plan_order_cycle(
        today=un_vendredi, delivery_weekdays={1, 4}, shelf_life_days=30,
        daily_consumption=prevision_vendredi, current_stock=10.0, pack_size=1.0,
    )

    resultat = ai_ordering.plan_order_cycle_for_ingredient(db_session, a.ingredient.id, today=un_vendredi)

    assert resultat.ok
    assert resultat.suggested_quantity == attendu.suggested_quantity
    assert resultat.suggested_quantity > 0
