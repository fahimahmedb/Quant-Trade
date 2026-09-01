from app import models
from app.services import recipes


def test_food_cost_computed_from_ingredient_lines(db_session):
    farine = models.Ingredient(name="Farine", unit=models.Unit.GRAMME, unit_cost=0.002)
    beurre = models.Ingredient(name="Beurre", unit=models.Unit.GRAMME, unit_cost=0.01)
    db_session.add_all([farine, beurre])
    db_session.commit()

    dish = recipes.upsert_dish(
        db_session,
        dish_id=None,
        name="Croissant",
        is_active=True,
        lines=[
            recipes.RecipeLineInput(ingredient_id=farine.id, quantity=100),
            recipes.RecipeLineInput(ingredient_id=beurre.id, quantity=50),
        ],
    )

    # 100g farine * 0.002 + 50g beurre * 0.01 = 0.2 + 0.5 = 0.7
    assert dish.food_cost == 0.7


def test_upsert_dish_replaces_lines_on_edit(db_session):
    farine = models.Ingredient(name="Farine", unit=models.Unit.GRAMME, unit_cost=0.002)
    sucre = models.Ingredient(name="Sucre", unit=models.Unit.GRAMME, unit_cost=0.003)
    db_session.add_all([farine, sucre])
    db_session.commit()

    dish = recipes.upsert_dish(
        db_session,
        dish_id=None,
        name="Gâteau",
        is_active=True,
        lines=[recipes.RecipeLineInput(ingredient_id=farine.id, quantity=200)],
    )
    assert len(dish.recipe_lines) == 1

    updated = recipes.upsert_dish(
        db_session,
        dish_id=dish.id,
        name="Gâteau au sucre",
        is_active=True,
        lines=[recipes.RecipeLineInput(ingredient_id=sucre.id, quantity=80)],
    )

    assert updated.id == dish.id
    assert updated.name == "Gâteau au sucre"
    assert len(updated.recipe_lines) == 1
    assert updated.recipe_lines[0].ingredient_id == sucre.id


def test_duplicate_ingredient_lines_are_merged_by_summing(db_session):
    farine = models.Ingredient(name="Farine", unit=models.Unit.GRAMME, unit_cost=0.002)
    db_session.add(farine)
    db_session.commit()

    # Même ingrédient sélectionné deux fois par erreur dans le formulaire.
    dish = recipes.upsert_dish(
        db_session,
        dish_id=None,
        name="Pain",
        is_active=True,
        lines=[
            recipes.RecipeLineInput(ingredient_id=farine.id, quantity=100),
            recipes.RecipeLineInput(ingredient_id=farine.id, quantity=50),
        ],
    )

    assert len(dish.recipe_lines) == 1
    assert dish.recipe_lines[0].quantity == 150


def test_zero_or_negative_quantity_lines_are_skipped(db_session):
    farine = models.Ingredient(name="Farine", unit=models.Unit.GRAMME, unit_cost=0.002)
    db_session.add(farine)
    db_session.commit()

    dish = recipes.upsert_dish(
        db_session,
        dish_id=None,
        name="Test",
        is_active=True,
        lines=[recipes.RecipeLineInput(ingredient_id=farine.id, quantity=0)],
    )
    assert dish.recipe_lines == []
