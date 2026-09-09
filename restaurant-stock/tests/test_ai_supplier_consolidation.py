"""F16 — consolidation de commande par fournisseur (docs/feature-plans/
ia-f10-f19.md §7). Aucun jeu SYN dédié dans le document (« purement
combinatoire ») : fixtures locales, construites directement sur les
primitives de `tests/synthetic_data.py`, comme F7 le faisait déjà dans le
Lot IA-0 pour ses propres tests DB-intégrés.

Piège connu du v1 (Lot IA-0, `ai_ordering` : « StockMovement.created_at est
horodaté à l'exécution réelle, pas à la date synthétique des ventes ») :
`today` est ici `datetime.utcnow()` (pas une date fixe de 2026), pour que
la fenêtre glissante v1 (qui filtre sur `created_at`) capture réellement
les ventes injectées dans le même test. `delivery_weekdays` couvre les 7
jours pour ne dépendre d'aucun jour de semaine réel précis à l'exécution.
"""
from datetime import datetime, timedelta

from app import models
from app.services import ai_supplier_consolidation, settings_service
from tests import synthetic_data as syn

ALL_WEEKDAYS = "0,1,2,3,4,5,6"


def _enable(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f7_enabled = True
    settings.feature_f16_enabled = True
    db.commit()


def _due_ingredient(db, name, *, unit_cost, supplier=None, threshold=None, daily_qty=10.0):
    """Un ingrédient dont F7 doit immédiatement suggérer une commande :
    stock quasi épuisé, consommation récente établie par une vente réelle
    à l'instant du test."""
    ing = syn.ingredient(db, name, unit_cost=unit_cost, stock_qty=1.0)
    ing.shelf_life_days = 30
    ing.delivery_weekdays = ALL_WEEKDAYS
    ing.pack_size = 1.0
    ing.supplier_name = supplier
    ing.supplier_free_shipping_threshold = threshold
    plat = syn.dish(db, f"Plat {name}", {ing.id: 1.0})
    now = datetime.utcnow()
    syn.import_sales_rows(db, [(now, plat.name, daily_qty, None)], filename=f"{name}.csv")
    db.commit()
    return ing


def _not_due_ingredient(db, name, *, unit_cost, supplier, shelf_life_days, stock_qty, daily_qty=1.0):
    """Un ingrédient du même fournisseur, largement approvisionné : F7 n'a
    rien à en dire aujourd'hui, mais F16 peut proposer d'en ajouter — à
    condition que sa conservation laisse une marge au-dessus du stock déjà
    présent (sinon même l'ajout minimal dépasserait le plafond de
    péremption, ce qui est le scénario recherché par TC-F16-05, pas par
    ce cas-ci)."""
    ing = syn.ingredient(db, name, unit_cost=unit_cost, stock_qty=stock_qty)
    ing.shelf_life_days = shelf_life_days
    ing.delivery_weekdays = ALL_WEEKDAYS
    ing.pack_size = 1.0
    ing.supplier_name = supplier
    plat = syn.dish(db, f"Plat {name}", {ing.id: 1.0})
    now = datetime.utcnow()
    syn.import_sales_rows(db, [(now, plat.name, daily_qty, None)], filename=f"{name}.csv")
    db.commit()
    return ing


def test_f16_is_inert_by_default(db_session):
    _due_ingredient(db_session, "Ingrédient F16 inerte", unit_cost=1.0)
    result = ai_supplier_consolidation.consolidate_orders(db_session, today=datetime.utcnow())
    assert not result.ok
    assert "désactivée" in result.message
    assert result.groups == []


# ==========================================================================
# AC-F16-1 / TC-F16-04 — sans fournisseur, groupe "Non attribué"
# ==========================================================================

def test_ac_f16_1_ingredient_without_supplier_goes_to_unattributed_group(db_session):
    ing = _due_ingredient(db_session, "Ingrédient sans fournisseur", unit_cost=2.0, supplier=None)
    _enable(db_session)

    result = ai_supplier_consolidation.consolidate_orders(db_session, today=datetime.utcnow())

    assert result.ok, result.message
    groupe = next(g for g in result.groups if g.supplier_name == "Non attribué")
    assert any(l.ingredient_id == ing.id for l in groupe.lines)


def test_ingredients_with_a_real_supplier_are_grouped_under_it_not_unattributed(db_session):
    ing = _due_ingredient(db_session, "Ingrédient fournisseur nommé", unit_cost=1.0, supplier="Fournisseur Nommé")
    _enable(db_session)

    result = ai_supplier_consolidation.consolidate_orders(db_session, today=datetime.utcnow())

    assert not any(g.supplier_name == "Non attribué" for g in result.groups)
    groupe = next(g for g in result.groups if g.supplier_name == "Fournisseur Nommé")
    assert any(l.ingredient_id == ing.id for l in groupe.lines)


def test_ac_f16_1_grouped_quantity_matches_f7s_own_suggestion(db_session):
    """« Affichage F7 inchangé » : la quantité groupée doit être EXACTEMENT
    celle que F7 aurait suggérée seul, jamais recalculée différemment."""
    from app.services import ai_ordering
    ing = _due_ingredient(db_session, "Ingrédient comparaison F7", unit_cost=1.5)
    _enable(db_session)
    now = datetime.utcnow()

    attendu = ai_ordering.plan_order_cycle_for_ingredient(db_session, ing.id, today=now)
    result = ai_supplier_consolidation.consolidate_orders(db_session, today=now)

    ligne = next(l for g in result.groups for l in g.lines if l.ingredient_id == ing.id)
    assert ligne.quantity == attendu.suggested_quantity


# ==========================================================================
# AC-F16-2 — sous le franco, proposition d'ajout respectant la péremption
# ==========================================================================

def test_ac_f16_2_under_threshold_proposes_additions_within_shelf_life(db_session):
    a = _due_ingredient(db_session, "Ingrédient A franco", unit_cost=2.0, supplier="Fournisseur A", threshold=5.0, daily_qty=5.0)
    # Conso quotidienne établie plus haute que le stock (200), pour un
    # plafond de conservation (60 j x conso) largement au-dessus du stock
    # déjà présent : de la marge pour "not due" ET pour "addable" à la fois.
    candidat = _not_due_ingredient(
        db_session, "Ingrédient candidat franco", unit_cost=1.0, supplier="Fournisseur A",
        shelf_life_days=60, stock_qty=200.0, daily_qty=50.0,
    )
    _enable(db_session)

    result = ai_supplier_consolidation.consolidate_orders(db_session, today=datetime.utcnow())

    groupe = next(g for g in result.groups if g.supplier_name == "Fournisseur A")
    assert groupe.under_threshold
    assert groupe.shortfall is not None and groupe.shortfall > 0
    assert groupe.can_reach_threshold
    assert any(p.ingredient_id == candidat.id for p in groupe.proposed_additions)
    for p in groupe.proposed_additions:
        assert p.max_addable_quantity > 0
        # Plafond péremption : jamais plus que la conso sur la fenêtre de
        # conservation, moins ce qui est déjà en stock.
        ing = db_session.get(models.Ingredient, p.ingredient_id)
        assert ing.current_theoretical_stock + p.max_addable_quantity <= ing.shelf_life_days * 100  # marge large
    assert "franco" in groupe.message.lower()
    assert f"{groupe.shortfall:.2f}" in groupe.message


def test_ac_f16_2_total_at_or_above_threshold_has_no_addition_proposed(db_session):
    _due_ingredient(db_session, "Ingrédient au-dessus du franco", unit_cost=100.0, supplier="Fournisseur B", threshold=10.0, daily_qty=5.0)
    _enable(db_session)

    result = ai_supplier_consolidation.consolidate_orders(db_session, today=datetime.utcnow())

    groupe = next(g for g in result.groups if g.supplier_name == "Fournisseur B")
    assert not groupe.under_threshold
    assert groupe.proposed_additions == []


# ==========================================================================
# TC-F16-05 — franco inatteignable sans dépasser la péremption
# ==========================================================================

def test_tc_f16_05_unreachable_threshold_without_spoilage_proposes_deferral(db_session):
    a = _due_ingredient(
        db_session, "Ingrédient A inatteignable", unit_cost=1.0, supplier="Fournisseur C",
        threshold=1000.0, daily_qty=2.0,
    )
    # Candidat déjà quasi plein pour sa conservation : rien à ajouter sans gâcher.
    candidat = _not_due_ingredient(
        db_session, "Ingrédient candidat plein", unit_cost=1.0, supplier="Fournisseur C",
        shelf_life_days=1, stock_qty=1_000_000.0,
    )
    _enable(db_session)

    result = ai_supplier_consolidation.consolidate_orders(db_session, today=datetime.utcnow())

    groupe = next(g for g in result.groups if g.supplier_name == "Fournisseur C")
    assert groupe.under_threshold
    assert not groupe.can_reach_threshold
    assert "péremption" in groupe.message.lower() or "impossible" in groupe.message.lower()
    assert "report" in groupe.message.lower()


def test_can_reach_threshold_is_a_real_computation_not_always_true(db_session):
    """Non-vacuité par contre-exemple : sans le test précédent, un code qui
    répond toujours can_reach_threshold=True passerait quand même celui-ci."""
    _due_ingredient(db_session, "Ingrédient seul, aucun candidat", unit_cost=1.0, supplier="Fournisseur D", threshold=1000.0, daily_qty=1.0)
    _enable(db_session)

    result = ai_supplier_consolidation.consolidate_orders(db_session, today=datetime.utcnow())

    groupe = next(g for g in result.groups if g.supplier_name == "Fournisseur D")
    assert not groupe.can_reach_threshold, "aucun autre ingrédient du même fournisseur : rien à proposer"


# ==========================================================================
# AC-F16-3 — jamais d'envoi automatique
# ==========================================================================

def test_export_text_is_a_plain_copyable_string_never_a_send_call(db_session):
    _due_ingredient(db_session, "Ingrédient export", unit_cost=1.0, supplier="Fournisseur E")
    _enable(db_session)

    result = ai_supplier_consolidation.consolidate_orders(db_session, today=datetime.utcnow())

    groupe = next(g for g in result.groups if g.supplier_name == "Fournisseur E")
    assert isinstance(groupe.export_text, str)
    assert "Fournisseur E" in groupe.export_text
    assert "Total" in groupe.export_text
