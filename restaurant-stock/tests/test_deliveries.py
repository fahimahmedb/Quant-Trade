"""F1 — réception de livraison et historique des prix.

Couvre AC-F1-1 à AC-F1-5 et TC-F1-01 à TC-F1-07 (Specs V2, section 3).
Les prix sont saisis en unité d'achat (€/kg) et stockés par unité de
référence (€/g) : les tests vérifient les deux bouts de la conversion.
"""
import pytest

from app import models
from app.services import deliveries, pricing


def _ingredient(db, name="Farine", unit=models.Unit.GRAMME, unit_cost=0.0012, stock=1000.0):
    ing = models.Ingredient(name=name, unit=unit, unit_cost=unit_cost,
                            current_theoretical_stock=stock)
    db.add(ing)
    db.commit()
    return ing


def _line(ingredient, quantity, price_per_purchase_unit):
    return deliveries.DeliveryLineInput(
        ingredient_id=ingredient.id,
        quantity=quantity,
        unit_price=pricing.to_storage_price(price_per_purchase_unit, ingredient.unit),
    )


def _delivery_form(client, sessions, *, received_on, supplier="Metro", rows, photo=None):
    """rows = [(nom ingrédient, quantité, prix en unité d'achat)] tels que saisis."""
    with sessions() as db:
        ids = {i.name: i.id for i in db.query(models.Ingredient)}
    data = {
        "received_on": received_on, "supplier": supplier, "note": "",
        "ingredient_id": [str(ids[name]) for name, _, _ in rows],
        "quantity": [str(q) for _, q, _ in rows],
        "unit_price": [str(p) for _, _, p in rows],
    }
    files = {"photo": photo} if photo else None
    return client.post("/deliveries/new", data=data, files=files)


# TC-F1-01 / AC-F1-2 / AC-F1-3 --------------------------------------------
def test_tc_f1_01_nominal_delivery_updates_stock_and_prices(db_session):
    farine = _ingredient(db_session, "Farine", unit_cost=0.0012, stock=1000)
    beurre = _ingredient(db_session, "Beurre", unit_cost=0.0080, stock=500)
    tomate = _ingredient(db_session, "Tomate", unit_cost=0.0030, stock=2000)

    result = deliveries.record_delivery(
        db_session,
        received_on=models.utcnow(),
        supplier="Metro",
        lines=[_line(farine, 25000, 1.40), _line(beurre, 2000, 9.00), _line(tomate, 5000, 3.20)],
    )

    assert len(result.receipt.lines) == 3
    db_session.refresh(farine); db_session.refresh(beurre); db_session.refresh(tomate)
    # AC-F1-2 : stock augmenté de la quantité exacte
    assert farine.current_theoretical_stock == 1000 + 25000
    assert beurre.current_theoretical_stock == 500 + 2000
    assert tomate.current_theoretical_stock == 2000 + 5000
    # AC-F1-3 : prix courant = prix d'achat (converti en €/g)
    assert farine.unit_cost == pytest.approx(0.0014)
    assert pricing.to_display_price(farine.unit_cost, farine.unit) == pytest.approx(1.40)
    # mouvements de réception tracés
    movements = db_session.query(models.StockMovement).filter_by(
        movement_type=models.MovementType.RECEPTION).all()
    assert len(movements) == 3
    assert all(m.quantity_delta > 0 for m in movements)


def test_ac_f1_3_recipe_food_cost_reflects_new_price_immediately(db_session):
    from app.services import recipes

    farine = _ingredient(db_session, "Farine", unit_cost=0.0012)
    dish = recipes.upsert_dish(db_session, dish_id=None, name="Pizza", is_active=True,
                               lines=[recipes.RecipeLineInput(ingredient_id=farine.id, quantity=200)])
    assert dish.food_cost == pytest.approx(200 * 0.0012)

    deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="Metro",
                               lines=[_line(farine, 25000, 2.00)])

    db_session.refresh(dish)
    assert dish.food_cost == pytest.approx(200 * 0.002)


# TC-F1-07 ----------------------------------------------------------------
def test_tc_f1_07_only_the_delivered_ingredient_changes_the_recipe_cost(db_session):
    from app.services import recipes

    ings = [_ingredient(db_session, n, unit_cost=c) for n, c in
            [("Farine", 0.0012), ("Sauce", 0.0040), ("Mozza", 0.0090), ("Basilic", 0.0200)]]
    dish = recipes.upsert_dish(
        db_session, dish_id=None, name="Margherita", is_active=True,
        lines=[recipes.RecipeLineInput(ingredient_id=i.id, quantity=100) for i in ings],
    )
    before = dish.food_cost
    other_costs_before = [i.unit_cost for i in ings[1:]]

    deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="Metro",
                               lines=[_line(ings[0], 10000, 2.40)])  # 1,20 -> 2,40 €/kg

    db_session.refresh(dish)
    assert [i.unit_cost for i in ings[1:]] == other_costs_before
    assert dish.food_cost == pytest.approx(before + 100 * (0.0024 - 0.0012))


# AC-F1-5 / TC-F1-01 ------------------------------------------------------
def test_ac_f1_5_price_alert_above_threshold_only(db_session):
    from app.services import settings_service

    settings_service.update_settings(db_session, safety_days=2, target_days=5,
                                     rolling_window_days=7, price_alert_pct=15)
    ing = _ingredient(db_session, "Tomate", unit_cost=0.0030)

    # +10 % : pas d'alerte
    result = deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="Metro",
                                        lines=[_line(ing, 1000, 3.30)])
    assert result.price_alerts == []

    # +20 % : alerte
    result = deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="Metro",
                                        lines=[_line(ing, 1000, 3.96)])
    assert len(result.price_alerts) == 1
    assert "Tomate" in result.price_alerts[0] and "+20" in result.price_alerts[0]


def test_price_alert_threshold_is_configurable(db_session):
    from app.services import settings_service

    settings_service.update_settings(db_session, safety_days=2, target_days=5,
                                     rolling_window_days=7, price_alert_pct=30)
    ing = _ingredient(db_session, "Tomate", unit_cost=0.0030)
    result = deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="Metro",
                                        lines=[_line(ing, 1000, 3.60)])  # +20 %, sous le seuil 30 %
    assert result.price_alerts == []


# AC-F1-4 ------------------------------------------------------------------
def test_ac_f1_4_price_history_is_recorded_with_date_and_supplier(db_session):
    from datetime import datetime

    ing = _ingredient(db_session, "Farine", unit_cost=0.0012)
    deliveries.record_delivery(db_session, received_on=datetime(2026, 3, 1), supplier="Metro",
                               lines=[_line(ing, 1000, 1.40)])
    deliveries.record_delivery(db_session, received_on=datetime(2026, 4, 1), supplier="Transgourmet",
                               lines=[_line(ing, 1000, 1.60)])

    history = (db_session.query(models.PriceHistory)
               .filter_by(ingredient_id=ing.id)
               .order_by(models.PriceHistory.recorded_at).all())
    # prix initial archivé + les deux réceptions
    assert [round(pricing.to_display_price(h.unit_price, ing.unit), 2) for h in history] == [1.20, 1.40, 1.60]
    assert [h.supplier for h in history] == [None, "Metro", "Transgourmet"]
    assert history[-1].recorded_at == datetime(2026, 4, 1)


# TC-F1-06 ----------------------------------------------------------------
def test_tc_f1_06_two_deliveries_same_day_same_ingredient_give_two_entries(db_session):
    from datetime import datetime

    ing = _ingredient(db_session, "Farine", unit_cost=0.0012, stock=0)
    day = datetime(2026, 5, 12)
    deliveries.record_delivery(db_session, received_on=day, supplier="Metro", lines=[_line(ing, 1000, 1.40)])
    deliveries.record_delivery(db_session, received_on=day, supplier="Metro", lines=[_line(ing, 500, 1.50)])

    assert db_session.query(models.DeliveryReceipt).count() == 2
    entries = db_session.query(models.PriceHistory).filter_by(ingredient_id=ing.id).all()
    assert len([e for e in entries if e.receipt_id is not None]) == 2
    db_session.refresh(ing)
    assert ing.current_theoretical_stock == 1500


# TC-F1-03 ----------------------------------------------------------------
def test_tc_f1_03_zero_price_is_refused_and_nothing_is_written(db_session):
    ing = _ingredient(db_session, "Farine", unit_cost=0.0012, stock=1000)

    with pytest.raises(deliveries.DeliveryError, match="Prix invalide"):
        deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="Metro",
                                   lines=[_line(ing, 1000, 0)])

    db_session.rollback()
    db_session.refresh(ing)
    assert ing.current_theoretical_stock == 1000
    assert db_session.query(models.DeliveryReceipt).count() == 0
    assert db_session.query(models.StockMovement).count() == 0


def test_zero_quantity_is_refused(db_session):
    ing = _ingredient(db_session, "Farine")
    with pytest.raises(deliveries.DeliveryError, match="Quantité invalide"):
        deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="",
                                   lines=[_line(ing, 0, 1.40)])


# TC-F1-05 ----------------------------------------------------------------
def test_tc_f1_05_ingredient_deleted_between_entry_and_validation_gives_clear_message(db_session):
    ing = _ingredient(db_session, "Éphémère")
    ghost = deliveries.DeliveryLineInput(ingredient_id=ing.id + 999, quantity=10, unit_price=0.001)

    with pytest.raises(deliveries.DeliveryError, match="n'existe plus"):
        deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="",
                                   lines=[_line(ing, 100, 1.0), ghost])

    db_session.rollback()
    assert db_session.query(models.DeliveryReceipt).count() == 0


# TC-F1-04 ----------------------------------------------------------------
def test_tc_f1_04_backdated_delivery_is_accepted_with_a_warning(db_session):
    from datetime import datetime, timedelta

    from app.services import counting

    ing = _ingredient(db_session, "Farine", stock=1000)
    session = counting.start_count_session(db_session)
    counting.confirm_count_line(db_session, session.lines[0].id, counted_quantity=900)
    counting.complete_count_session(db_session, session.id)

    result = deliveries.record_delivery(
        db_session, received_on=models.utcnow() - timedelta(days=3), supplier="Metro",
        lines=[_line(ing, 500, 1.40)],
    )

    assert result.backdated_warning is not None
    assert "ne sera pas recalculé rétroactivement" in result.backdated_warning
    db_session.refresh(ing)
    assert ing.current_theoretical_stock == 900 + 500  # acceptée malgré tout

    # une réception postérieure au comptage n'avertit pas
    later = deliveries.record_delivery(db_session, received_on=datetime.now() + timedelta(days=1),
                                       supplier="Metro", lines=[_line(ing, 100, 1.40)])
    assert later.backdated_warning is None


# Suggestions de fournisseur ----------------------------------------------
def test_supplier_suggestions_are_remembered_most_recent_first(db_session):
    ing = _ingredient(db_session, "Farine")
    for supplier in ["Metro", "Transgourmet", "Metro"]:
        deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier=supplier,
                                   lines=[_line(ing, 100, 1.40)])
    assert deliveries.supplier_suggestions(db_session) == ["Metro", "Transgourmet"]


def test_last_known_price_prefills_from_history_then_current_cost(db_session):
    ing = _ingredient(db_session, "Farine", unit_cost=0.0012)
    assert deliveries.last_known_price(db_session, ing) == 0.0012
    deliveries.record_delivery(db_session, received_on=models.utcnow(), supplier="Metro",
                               lines=[_line(ing, 100, 1.40)])
    assert deliveries.last_known_price(db_session, ing) == pytest.approx(0.0014)


# Écrans (AC-F1-1) ---------------------------------------------------------
def test_ac_f1_1_three_line_delivery_submits_from_a_single_screen(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory

    form = client.get("/deliveries/new").text
    assert form.count('name="ingredient_id"') >= 3  # 3 lignes saisissables d'emblée
    assert 'data-last-price="1,2"' in form          # prix pré-rempli en €/kg (Farine), virgule française

    r = _delivery_form(client, sessions, received_on="2026-09-01", rows=[
        ("Farine", "25000", "1,40"), ("Tomate", "5000", "3,20"), ("Mozzarella", "2000", "9,00"),
    ])
    assert r.status_code == 200
    with sessions() as db:
        farine = db.query(models.Ingredient).filter_by(name="Farine").one()
        assert farine.current_theoretical_stock == 20000 + 25000
        assert farine.unit_cost == pytest.approx(0.0014)
        assert db.query(models.DeliveryReceipt).one().supplier == "Metro"


# TC-F1-02 ----------------------------------------------------------------
def test_tc_f1_02_french_decimal_comma_quantity_is_accepted(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    r = _delivery_form(client, sessions, received_on="2026-09-01",
                       rows=[("Vin rouge (bouteille)", "2,5", "4,80")])
    assert r.status_code == 200
    with sessions() as db:
        vin = db.query(models.Ingredient).filter_by(name="Vin rouge (bouteille)").one()
        assert vin.current_theoretical_stock == 42.5
        assert vin.unit_cost == pytest.approx(4.80)


def test_delivery_screen_reports_zero_price_without_crashing(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    r = _delivery_form(client, sessions, received_on="2026-09-01", rows=[("Farine", "1000", "0")])
    assert r.status_code == 422
    assert "Prix invalide" in r.text
    with sessions() as db:
        assert db.query(models.DeliveryReceipt).count() == 0
        assert db.query(models.Ingredient).filter_by(name="Farine").one().current_theoretical_stock == 20000


def test_price_history_and_alert_are_visible_on_screen(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    r = _delivery_form(client, sessions, received_on="2026-09-01", rows=[("Farine", "1000", "1,80")])
    assert "Prix Farine +50 % vs dernière livraison" in r.text  # alerte affichée

    with sessions() as db:
        farine_id = db.query(models.Ingredient).filter_by(name="Farine").one().id
    # Espaces fines/insécables ramenées à une espace ordinaire : l'assertion
    # porte sur le prix affiché, pas sur la typographie qui l'entoure.
    page = client.get(f"/ingredients/{farine_id}/edit").text.replace("\u202f", " ")
    assert "Historique des prix d'achat" in page
    assert "1,80 €/kg" in page and "1,20 €/kg" in page
    assert "Réception" in client.get(f"/ingredients/{farine_id}/edit").text  # mouvement tracé


def test_delivery_photo_is_stored_and_served(seeded_client, tmp_path, monkeypatch):
    from app.config import UPLOAD_DIR

    client, sessions = seeded_client.client, seeded_client.session_factory
    png = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a"
        "49444154789c6360000002000100ffff03000006000557bfabd40000000049454e44ae426082"
    )
    r = _delivery_form(client, sessions, received_on="2026-09-01",
                       rows=[("Farine", "1000", "1,40")],
                       photo=("bl.png", png, "image/png"))
    assert r.status_code == 200
    with sessions() as db:
        receipt = db.query(models.DeliveryReceipt).one()
        assert receipt.photo_path is not None
        stored = UPLOAD_DIR / receipt.photo_path
    assert stored.exists()
    stored.unlink()


def test_delivery_photo_rejects_non_image(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    r = _delivery_form(client, sessions, received_on="2026-09-01",
                       rows=[("Farine", "1000", "1,40")],
                       photo=("bl.pdf", b"%PDF-1.4", "application/pdf"))
    assert r.status_code == 422
    assert "JPEG, PNG ou WebP" in r.text
    with sessions() as db:
        assert db.query(models.DeliveryReceipt).count() == 0
