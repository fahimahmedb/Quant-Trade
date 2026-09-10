"""F24 — comparaison de prix multi-fournisseurs (docs/feature-plans/
backlog-lot-ia-2.md §5, point bloquant 2, débloqué a posteriori — cible
SYN-U). Voir le docstring du module pour le raisonnement complet :
`PriceHistory.supplier` (F1) porte déjà l'information, aucun nouveau
champ ni table n'était nécessaire.
"""
from datetime import datetime

from app import models
from app.services import ai_supplier_price_comparison as cmp, deliveries, settings_service
from tests import synthetic_data as syn


def _enable(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f24_enabled = True
    db.commit()


def test_f24_is_inert_by_default(db_session):
    syn.build_syn_u(db_session)

    out = cmp.compare_suppliers(db_session)

    assert not out.ok and "désactivée" in out.message


def test_single_supplier_produces_no_comparison(db_session):
    ing = syn.ingredient(db_session, "Un seul fournisseur", stock_qty=100.0)
    deliveries.record_delivery(
        db_session, received_on=datetime(2026, 1, 1), supplier="Fournisseur unique",
        lines=[deliveries.DeliveryLineInput(ingredient_id=ing.id, quantity=5.0, unit_price=4.0)],
    )
    _enable(db_session)

    out = cmp.compare_suppliers(db_session)

    assert out.ok, out.message
    assert out.comparisons == []


def test_two_suppliers_is_the_minimum_that_produces_a_comparison(db_session):
    """Non-vacuité de la frontière : exactement 2 fournisseurs distincts
    doivent suffire à déclencher la comparaison — le seuil est « < 2 :
    rien », pas « <= 2 »."""
    ing = syn.ingredient(db_session, "Deux fournisseurs", stock_qty=100.0)
    deliveries.record_delivery(
        db_session, received_on=datetime(2026, 1, 1), supplier="Fournisseur X",
        lines=[deliveries.DeliveryLineInput(ingredient_id=ing.id, quantity=5.0, unit_price=4.0)],
    )
    deliveries.record_delivery(
        db_session, received_on=datetime(2026, 1, 2), supplier="Fournisseur Y",
        lines=[deliveries.DeliveryLineInput(ingredient_id=ing.id, quantity=5.0, unit_price=3.0)],
    )
    _enable(db_session)

    out = cmp.compare_suppliers(db_session)

    assert out.ok, out.message
    assert len(out.comparisons) == 1
    assert out.comparisons[0].ingredient_id == ing.id


def test_most_recent_price_per_supplier_is_used_not_the_lowest_ever(db_session):
    """Non-vacuité : Fournisseur B a eu 10€ puis 8€ — F24 doit retenir 8€
    (le plus récent), jamais 10€ (dépassé) ni le plus bas jamais vu."""
    result = syn.build_syn_u(db_session)
    _enable(db_session)

    out = cmp.compare_suppliers(db_session)

    assert out.ok, out.message
    comparison = out.comparisons[0]
    b_price = next(p for p in comparison.prices if p.supplier == "Fournisseur B")
    assert b_price.unit_price == 8.0


def test_best_supplier_and_potential_saving_are_computed_correctly(db_session):
    result = syn.build_syn_u(db_session)
    _enable(db_session)

    out = cmp.compare_suppliers(db_session)

    comparison = out.comparisons[0]
    assert comparison.best_supplier == result.cheaper_supplier  # Fournisseur A
    assert comparison.best_price == result.cheaper_price  # 6.0
    assert comparison.current_price == result.current_price  # 8.0 (dernière réception, Fournisseur B)
    assert comparison.potential_saving_pct == 25.0  # (8 - 6) / 8 * 100
    # Trié du moins cher au plus cher.
    assert [p.supplier for p in comparison.prices] == ["Fournisseur A", "Fournisseur B"]


def test_current_supplier_flag_matches_designated_supplier_even_when_not_cheapest(db_session):
    result = syn.build_syn_u(db_session)
    _enable(db_session)

    out = cmp.compare_suppliers(db_session)

    comparison = out.comparisons[0]
    by_name = {p.supplier: p for p in comparison.prices}
    assert by_name["Fournisseur B"].is_current is True  # désigné, même si pas le moins cher
    assert by_name["Fournisseur A"].is_current is False


def test_no_saving_when_current_price_is_already_the_best(db_session):
    """Non-vacuité : quand le fournisseur désigné est déjà le moins cher,
    rien à gagner — `potential_saving_pct` doit rester None, jamais 0.0
    présenté comme s'il y avait une économie mesurée nulle."""
    ing = syn.ingredient(db_session, "Déjà au meilleur prix", stock_qty=100.0)
    deliveries.record_delivery(
        db_session, received_on=datetime(2026, 1, 1), supplier="Fournisseur cher",
        lines=[deliveries.DeliveryLineInput(ingredient_id=ing.id, quantity=5.0, unit_price=9.0)],
    )
    deliveries.record_delivery(
        db_session, received_on=datetime(2026, 1, 2), supplier="Fournisseur pas cher",
        lines=[deliveries.DeliveryLineInput(ingredient_id=ing.id, quantity=5.0, unit_price=4.0)],
    )
    ing.supplier_name = "Fournisseur pas cher"
    db_session.commit()
    _enable(db_session)

    out = cmp.compare_suppliers(db_session)

    comparison = out.comparisons[0]
    assert comparison.best_supplier == "Fournisseur pas cher"
    assert comparison.current_price == 4.0  # dernière réception
    assert comparison.potential_saving_pct is None
