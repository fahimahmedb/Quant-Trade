"""Fiches techniques (section 4.1 du brief)."""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app import models


@dataclass
class RecipeLineInput:
    ingredient_id: int
    quantity: float


class DuplicateNameError(ValueError):
    pass


def food_cost(dish: models.Dish) -> float:
    """Coût matière du plat = somme(grammage * coût unitaire de l'ingrédient)."""
    return sum(line.quantity * line.ingredient.unit_cost for line in dish.recipe_lines)


def upsert_dish(
    db: Session,
    *,
    dish_id: int | None,
    name: str,
    is_active: bool,
    lines: list[RecipeLineInput],
) -> models.Dish:
    name_query = db.query(models.Dish).filter(models.Dish.name.ilike(name))
    if dish_id is not None:
        name_query = name_query.filter(models.Dish.id != dish_id)
    if name_query.first() is not None:
        raise DuplicateNameError(f"Un plat « {name} » existe déjà.")

    if dish_id is not None:
        dish = db.get(models.Dish, dish_id)
        if dish is None:
            raise ValueError(f"Plat introuvable : {dish_id}")
        dish.name = name
        dish.is_active = is_active
        dish.recipe_lines.clear()
        db.flush()
    else:
        dish = models.Dish(name=name, is_active=is_active)
        db.add(dish)
        db.flush()

    # Un ingrédient sélectionné deux fois par erreur dans le formulaire (lignes
    # dynamiques) ne doit pas planter : on additionne les grammages plutôt que
    # de violer la contrainte d'unicité (dish_id, ingredient_id).
    merged_quantities: dict[int, float] = {}
    for line in lines:
        if line.quantity <= 0:
            continue
        merged_quantities[line.ingredient_id] = (
            merged_quantities.get(line.ingredient_id, 0.0) + line.quantity
        )

    for ingredient_id, quantity in merged_quantities.items():
        db.add(
            models.RecipeIngredient(
                dish_id=dish.id,
                ingredient_id=ingredient_id,
                quantity=quantity,
            )
        )

    db.commit()
    db.refresh(dish)
    return dish


def delete_dish(db: Session, dish_id: int) -> None:
    dish = db.get(models.Dish, dish_id)
    if dish is not None:
        db.delete(dish)
        db.commit()
