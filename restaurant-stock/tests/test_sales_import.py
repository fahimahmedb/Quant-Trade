from app import models
from app.services import recipes, sales_import


def _make_dish_with_recipe(db_session, dish_name="Burger", ingredient_name="Steak haché"):
    ingredient = models.Ingredient(
        name=ingredient_name,
        unit=models.Unit.GRAMME,
        unit_cost=0.01,
        current_theoretical_stock=5000,
    )
    db_session.add(ingredient)
    db_session.commit()
    dish = recipes.upsert_dish(
        db_session,
        dish_id=None,
        name=dish_name,
        is_active=True,
        lines=[recipes.RecipeLineInput(ingredient_id=ingredient.id, quantity=150)],
    )
    return dish, ingredient


def test_parse_csv_happy_path():
    content = "date,plat,quantite,prix_unitaire\n2026-08-01,Burger,3,12.5\n2026-08-01,Salade,2,\n"
    result = sales_import.parse_csv(content)
    assert result.errors == []
    assert len(result.rows) == 2
    assert result.rows[0].raw_dish_name == "Burger"
    assert result.rows[0].quantity_sold == 3
    assert result.rows[0].unit_price == 12.5
    assert result.rows[1].unit_price is None


def test_parse_csv_accepts_french_dates_and_comma_decimals():
    content = "date;plat;quantite;prix_unitaire\n01/08/2026;Burger;3,5;12,5\n"
    result = sales_import.parse_csv(content)
    assert result.errors == []
    assert result.rows[0].quantity_sold == 3.5
    assert result.rows[0].unit_price == 12.5


def test_parse_csv_reports_missing_columns():
    content = "jour,article\n2026-08-01,Burger\n"
    result = sales_import.parse_csv(content)
    assert result.rows == []
    assert "quantité" in result.errors[0]


def test_parse_csv_skips_invalid_rows_but_keeps_valid_ones():
    content = (
        "date,plat,quantite\n"
        "2026-08-01,Burger,3\n"
        "not-a-date,Burger,2\n"
        "2026-08-01,Burger,not-a-number\n"
    )
    result = sales_import.parse_csv(content)
    assert len(result.rows) == 1
    assert len(result.errors) == 2


def test_import_sales_matches_dish_and_decrements_stock(db_session):
    dish, ingredient = _make_dish_with_recipe(db_session)
    content = "date,plat,quantite\n2026-08-01,Burger,3\n"

    sales_import_row, parsed = sales_import.import_sales(db_session, "export.csv", content)

    assert sales_import_row.row_count == 1
    assert sales_import_row.unmatched_count == 0
    db_session.refresh(ingredient)
    # 5000g - (150g * 3) = 4550g
    assert ingredient.current_theoretical_stock == 4550
    movements = db_session.query(models.StockMovement).all()
    assert len(movements) == 1
    assert movements[0].movement_type == models.MovementType.VENTE
    assert movements[0].quantity_delta == -450


def test_import_sales_flags_unmatched_dish(db_session):
    content = "date,plat,quantite\n2026-08-01,Plat inconnu,1\n"
    sales_import_row, _ = sales_import.import_sales(db_session, "export.csv", content)

    assert sales_import_row.unmatched_count == 1
    line = db_session.query(models.SaleLine).one()
    assert line.dish_id is None
    assert sales_import.unmatched_raw_names(db_session, sales_import_row.id) == [
        "Plat inconnu"
    ]


def test_map_raw_name_to_dish_applies_stock_and_remembers_alias(db_session):
    dish, ingredient = _make_dish_with_recipe(db_session, dish_name="Burger maison")
    content = "date,plat,quantite\n2026-08-01,BURGER (maison),2\n"
    sales_import_row, _ = sales_import.import_sales(db_session, "export.csv", content)
    assert sales_import_row.unmatched_count == 1

    updated = sales_import.map_raw_name_to_dish(
        db_session, "BURGER (maison)", dish.id, remember_alias=True
    )
    assert updated == 1

    db_session.refresh(ingredient)
    assert ingredient.current_theoretical_stock == 5000 - 150 * 2
    db_session.refresh(sales_import_row)
    assert sales_import_row.unmatched_count == 0

    # Un second import avec le même intitulé brut doit désormais se résoudre seul.
    content_2 = "date,plat,quantite\n2026-08-02,BURGER (maison),1\n"
    sales_import_row_2, _ = sales_import.import_sales(db_session, "export2.csv", content_2)
    assert sales_import_row_2.unmatched_count == 0
    db_session.refresh(ingredient)
    assert ingredient.current_theoretical_stock == 5000 - 150 * 2 - 150 * 1
