"""Suite de non-régression — boucle cœur v1 (Specs V2, section 6.2).

Un test nommé par invariant NR-xx. Règle des specs : aucune fonctionnalité
n'est déployée sans toute cette suite verte. NR-12 (débordements mobiles)
est dans test_nr_mobile.py car il a besoin d'un vrai navigateur.
"""
import re
from pathlib import Path

from app import models
from app.services import counting, ordering, recipes, sales_import, settings_service

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_CSV = BASE_DIR / "sample_data" / "exemple_export_ventes.csv"


def _ingredient(db, name, **kw):
    ing = models.Ingredient(name=name, unit=kw.pop("unit", models.Unit.GRAMME), **kw)
    db.add(ing)
    db.commit()
    return ing


def _visible_text(html: str) -> str:
    """Texte affiché : sans scripts, sans balises (donc sans attributs value=…).

    Les espaces fines et insécables de la typographie française (U+202F,
    U+00A0) sont ramenées à une espace ordinaire : ces tests portent sur ce
    qui est écrit, pas sur la finesse de l'espace qui précède « € ».
    """
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html).replace("\u202f", " ").replace("\u00a0", " ")


def _import_sample(client):
    return client.post(
        "/sales/import",
        files={"file": (SAMPLE_CSV.name, SAMPLE_CSV.read_bytes(), "text/csv")},
    )


# NR-01 --------------------------------------------------------------------
def test_nr01_food_cost_equals_sum_of_grammage_times_current_price(db_session):
    farine = _ingredient(db_session, "Farine", unit_cost=0.0012)
    beurre = _ingredient(db_session, "Beurre", unit_cost=0.0098)
    dish = recipes.upsert_dish(
        db_session, dish_id=None, name="Brioche", is_active=True,
        lines=[
            recipes.RecipeLineInput(ingredient_id=farine.id, quantity=333),
            recipes.RecipeLineInput(ingredient_id=beurre.id, quantity=77),
        ],
    )
    expected = 333 * 0.0012 + 77 * 0.0098
    assert abs(dish.food_cost - expected) < 0.01


# NR-02 --------------------------------------------------------------------
def test_nr02_sample_csv_import_creates_exact_movement_count(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    parsed = sales_import.parse_csv(SAMPLE_CSV.read_text())
    assert parsed.errors == []

    with sessions() as db:
        recipe_sizes = {d.name.casefold(): len(d.recipe_lines) for d in db.query(models.Dish)}
    expected = sum(recipe_sizes.get(r.raw_dish_name.casefold(), 0) for r in parsed.rows)
    assert expected == 28  # garde-fou : jeu de démo + CSV d'exemple figés

    r = _import_sample(client)
    assert r.status_code == 200
    with sessions() as db:
        assert db.query(models.StockMovement).count() == expected


# NR-03 --------------------------------------------------------------------
def test_nr03_unrecognized_burger_line_goes_to_mapping_screen_without_movement(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    r = _import_sample(client)
    assert "non reconnus" in r.text and "Burger" in r.text
    with sessions() as db:
        line = db.query(models.SaleLine).filter_by(raw_dish_name="Burger").one()
        assert line.dish_id is None and line.stock_applied is False
        assert db.query(models.SalesImport).one().unmatched_count == 1


# NR-04 --------------------------------------------------------------------
def test_nr04_remembered_alias_makes_second_import_need_no_mapping(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    r = _import_sample(client)
    import_path = r.url.path
    with sessions() as db:
        burger_id = db.query(models.Dish).filter_by(name="Burger maison").one().id
    client.post(f"{import_path}/map", data={"raw_name": "Burger", "dish_id": str(burger_id), "new_dish_name": ""})

    r2 = client.post("/sales/import", files={
        "file": ("j2.csv", "date,plat,quantite\n2026-08-31,Burger,2\n", "text/csv"),
    })
    assert "non reconnus" not in r2.text
    with sessions() as db:
        assert db.query(models.SalesImport).order_by(models.SalesImport.id.desc()).first().unmatched_count == 0


# NR-05 --------------------------------------------------------------------
def test_nr05_theoretical_stock_decremented_by_sales_times_grammage(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    _import_sample(client)
    parsed = sales_import.parse_csv(SAMPLE_CSV.read_text())
    burgers_sold = sum(r.quantity_sold for r in parsed.rows if r.raw_dish_name == "Burger maison")
    with sessions() as db:
        steak = db.query(models.Ingredient).filter_by(name="Steak haché").one()
        assert steak.current_theoretical_stock == 8000 - 150 * burgers_sold


# NR-06 --------------------------------------------------------------------
def test_nr06_completed_count_recalibrates_stock_and_traces_movement(db_session):
    ing = _ingredient(db_session, "Riz", unit_cost=0.002, current_theoretical_stock=5000)
    session = counting.start_count_session(db_session)
    counting.confirm_count_line(db_session, session.lines[0].id, counted_quantity=4200)
    counting.complete_count_session(db_session, session.id)

    db_session.refresh(ing)
    assert ing.current_theoretical_stock == 4200
    movement = db_session.query(models.StockMovement).filter_by(
        movement_type=models.MovementType.COMPTAGE
    ).one()
    assert movement.quantity_delta == -800 and movement.resulting_stock == 4200


# NR-07 --------------------------------------------------------------------
def test_nr07_variances_sorted_by_absolute_value_desc(db_session):
    small = _ingredient(db_session, "Poivre", unit_cost=0.05, current_theoretical_stock=100)
    big = _ingredient(db_session, "Boeuf", unit_cost=0.03, current_theoretical_stock=5000)
    surplus = _ingredient(db_session, "Sel", unit_cost=0.01, current_theoretical_stock=1000)
    session = counting.start_count_session(db_session)
    by_ing = {l.ingredient_id: l for l in session.lines}
    counting.confirm_count_line(db_session, by_ing[small.id].id, 95)      # 0,25 €
    counting.confirm_count_line(db_session, by_ing[big.id].id, 4500)     # 15 €
    counting.confirm_count_line(db_session, by_ing[surplus.id].id, 1500)  # -5 € (surplus)
    report = counting.variance_report(db_session, session.id)
    assert [l.ingredient_id for l in report] == [big.id, surplus.id, small.id]


# NR-08 --------------------------------------------------------------------
def test_nr08_negative_theoretical_stock_is_flagged_on_variance_screen(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    with sessions() as db:
        basil = models.Ingredient(name="Basilic", unit=models.Unit.GRAMME, unit_cost=0.02,
                                  storage_zone=models.StorageZone.FRIGO_POSITIF,
                                  current_theoretical_stock=-100)
        db.add(basil)
        db.commit()
    r = client.post("/counting/start", data={"counted_by": "NR"})
    session_id = int(r.url.path.rstrip("/").split("/")[-1])
    with sessions() as db:
        line = (db.query(models.CountLine).join(models.Ingredient)
                .filter(models.CountLine.count_session_id == session_id,
                        models.Ingredient.name == "Basilic").one())
        line_id = line.id
    page = client.get(f"/counting/{session_id}").text
    assert "Stock théorique négatif avant comptage" in page
    client.post(f"/counting/{session_id}/zone/frigo_positif", data={f"count_{line_id}": "5"})
    client.post(f"/counting/{session_id}/complete")
    variance_page = client.get("/variance").text
    assert "Basilic" in variance_page
    assert "déjà négatif avant ce comptage" in variance_page
    assert "+105" not in variance_page  # le % n'est plus affiché (non significatif)


# NR-09 --------------------------------------------------------------------
def test_nr09_suggestion_present_below_threshold_absent_above(db_session):
    settings_service.update_settings(db_session, safety_days=2, target_days=5, rolling_window_days=7)
    low = _ingredient(db_session, "Tomate", current_theoretical_stock=5, alert_threshold=10)
    high = _ingredient(db_session, "Sel", current_theoretical_stock=500, alert_threshold=10)
    batch = ordering.generate_suggestions(db_session)
    suggested = {l.ingredient_id for l in batch.lines}
    assert low.id in suggested and high.id not in suggested


# NR-10 --------------------------------------------------------------------
def test_nr10_no_code_path_sends_an_order():
    forbidden = re.compile(r"smtp|sendmail|requests\.(post|put)|httpx\.(post|put|Client|AsyncClient)|webhook|urlopen", re.I)
    offenders = []
    for path in (BASE_DIR / "app").rglob("*.py"):
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if forbidden.search(line):
                offenders.append(f"{path.relative_to(BASE_DIR)}:{n}: {line.strip()}")
    assert offenders == [], offenders


# NR-11 --------------------------------------------------------------------
def test_nr11_three_indicators_logged_after_events(seeded_client):
    from app.services import metrics

    client, sessions = seeded_client.client, seeded_client.session_factory
    _import_sample(client)
    r = client.post("/counting/start", data={})
    session_id = int(r.url.path.rstrip("/").split("/")[-1])
    with sessions() as db:
        line = db.query(models.CountLine).filter_by(count_session_id=session_id).first()
        zone = line.ingredient.storage_zone.value
        client.post(f"/counting/{session_id}/zone/{zone}", data={f"count_{line.id}": str(line.theoretical_quantity - 10)})
    client.post(f"/counting/{session_id}/complete")

    with sessions() as db:
        ing = db.query(models.Ingredient).filter_by(name="Farine").one()
        ing.alert_threshold = ing.current_theoretical_stock + 1000
        db.commit()
    client.post("/orders/generate")
    with sessions() as db:
        sline = db.query(models.OrderSuggestionLine).first()
        assert sline is not None
        client.post(f"/orders/lines/{sline.id}/decide", data={"final_quantity": str(sline.suggested_quantity)})

    with sessions() as db:
        assert len(metrics.variance_trend(db)) == 1
        assert metrics.suggestion_adoption_stats(db).decided == 1
        assert metrics.counting_duration_stats(db).average_seconds is not None


# NR-13 --------------------------------------------------------------------
def test_nr13_french_decimal_comma_accepted_everywhere(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    # ingrédient
    r = client.post("/ingredients/new", data={
        "name": "Huile", "unit": "mL", "unit_cost": "0,0075", "storage_zone": "sec",
        "current_theoretical_stock": "12,5", "alert_threshold": "1,5",
    })
    assert r.status_code < 400
    # fiche technique
    with sessions() as db:
        huile_id = db.query(models.Ingredient).filter_by(name="Huile").one().id
    r = client.post("/recipes/new", data={"name": "Vinaigrette", "is_active": "true",
                                          "ingredient_id": [str(huile_id)], "quantity": ["7,5"]})
    assert r.status_code < 400
    # réglages
    r = client.post("/settings", data={"safety_days": "2,5", "target_days": "6", "rolling_window_days": "7"})
    assert r.status_code < 400
    # comptage
    r = client.post("/counting/start", data={})
    session_id = int(r.url.path.rstrip("/").split("/")[-1])
    with sessions() as db:
        line = (db.query(models.CountLine).join(models.Ingredient)
                .filter(models.CountLine.count_session_id == session_id, models.Ingredient.name == "Huile").one())
        line_id = line.id
    r = client.post(f"/counting/{session_id}/zone/sec", data={f"count_{line_id}": "3,5"})
    assert r.status_code < 400
    # suggestion de commande
    with sessions() as db:
        assert db.get(models.CountLine, line_id).counted_quantity == 3.5
        huile = db.get(models.Ingredient, huile_id)
        huile.current_theoretical_stock = 0
        huile.alert_threshold = 10
        db.commit()
    client.post("/orders/generate")
    with sessions() as db:
        sline = db.query(models.OrderSuggestionLine).filter_by(ingredient_id=huile_id).one()
        sline_id = sline.id
    r = client.post(f"/orders/lines/{sline_id}/decide", data={"final_quantity": "10,5"})
    assert r.status_code < 400
    with sessions() as db:
        assert db.get(models.OrderSuggestionLine, sline_id).final_quantity == 10.5
        assert db.get(models.Ingredient, huile_id).unit_cost == 0.0075
        assert db.query(models.Settings).one().safety_days == 2.5


# NR-14 --------------------------------------------------------------------
def test_nr14_deleting_ingredient_used_in_recipe_is_refused_with_message(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    with sessions() as db:
        steak_id = db.query(models.Ingredient).filter_by(name="Steak haché").one().id
    r = client.post(f"/ingredients/{steak_id}/delete")
    assert r.status_code < 400
    assert "utilisé dans au moins une fiche technique" in r.text
    with sessions() as db:
        assert db.get(models.Ingredient, steak_id) is not None


# NR-15 --------------------------------------------------------------------
def test_nr15_duplicate_ingredient_name_gives_clear_message(seeded_client):
    client = seeded_client.client
    r = client.post("/ingredients/new", data={
        "name": "farine", "unit": "g", "unit_cost": "0.001", "storage_zone": "sec",
        "current_theoretical_stock": "1", "alert_threshold": "",
    })
    assert r.status_code == 409
    assert "existe déjà" in r.text


# NR-16 (OBS-1) ------------------------------------------------------------
def test_nr16_count_equal_to_theoretical_gives_strictly_zero_variance_on_demo_set(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    r = client.post("/counting/start", data={"counted_by": "OBS-1"})
    session_id = int(r.url.path.rstrip("/").split("/")[-1])
    with sessions() as db:
        lines = db.query(models.CountLine).filter_by(count_session_id=session_id).all()
        assert len(lines) == 9
        by_zone: dict[str, dict] = {}
        for line in lines:
            by_zone.setdefault(line.ingredient.storage_zone.value, {})[f"count_{line.id}"] = str(line.theoretical_quantity)
    for zone, data in by_zone.items():
        assert client.post(f"/counting/{session_id}/zone/{zone}", data=data).status_code < 400
    client.post(f"/counting/{session_id}/complete")
    with sessions() as db:
        report = counting.variance_report(db, session_id)
        assert len(report) == 9
        assert all(l.variance == 0 and l.variance_value == 0 for l in report)


# NR-17 (OBS-2) ------------------------------------------------------------
def test_nr17_no_price_displayed_as_zero_for_nonzero_priced_ingredient(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    text = _visible_text(client.get("/ingredients").text)
    assert "0,00 €" not in text
    assert "1,20 €/kg" in text     # Farine 0,0012 €/g
    assert "2,50 €/kg" in text     # Frites surgelées 0,0025 €/g
    assert "0,35 €/unité" in text  # Pain burger
    with sessions() as db:
        farine_id = db.query(models.Ingredient).filter_by(name="Farine").one().id
    assert "1,20 €/kg" in _visible_text(client.get(f"/ingredients/{farine_id}/edit").text)


# NR-18 (OBS-3) ------------------------------------------------------------
def test_nr18_all_displayed_quantities_use_decimal_comma(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    _import_sample(client)
    # Cas exact d'OBS-3 : 40 bouteilles − 0,2 × 17 verres = 36,6 (et non « 36.60 »).
    assert "36,60 unité" in _visible_text(client.get("/ingredients").text)

    r = client.post("/counting/start", data={})
    session_id = int(r.url.path.rstrip("/").split("/")[-1])
    with sessions() as db:
        line = db.query(models.CountLine).filter_by(count_session_id=session_id).first()
        client.post(f"/counting/{session_id}/zone/{line.ingredient.storage_zone.value}",
                    data={f"count_{line.id}": str(line.theoretical_quantity - 12.5)})
    client.post(f"/counting/{session_id}/complete")
    client.post("/orders/generate")

    period_decimal = re.compile(r"\d\.\d")
    for path in ["/", "/ingredients", "/recipes", "/variance", "/orders", "/metrics", f"/counting/{session_id}/summary"]:
        text = _visible_text(client.get(path).text)
        assert not period_decimal.search(text), f"point décimal affiché sur {path}: {period_decimal.search(text).group()}"
