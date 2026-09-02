"""Jeu de données de démonstration pour un restaurant fictif (bistrot).

Usage : python -m app.seed
Ne fait rien si des ingrédients existent déjà (évite d'écraser des données réelles).
`seed_demo(db)` est aussi utilisé par la suite de non-régression (NR-02, NR-16…).
"""
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal, init_db
from app.services import recipes

INGREDIENTS = [
    # (nom, unité, coût unitaire €, zone, stock théorique de départ)
    ("Steak haché", models.Unit.GRAMME, 0.012, models.StorageZone.FRIGO_POSITIF, 8000),
    ("Pain burger", models.Unit.UNITE, 0.35, models.StorageZone.SEC, 60),
    ("Salade", models.Unit.GRAMME, 0.004, models.StorageZone.FRIGO_POSITIF, 3000),
    ("Tomate", models.Unit.GRAMME, 0.003, models.StorageZone.FRIGO_POSITIF, 5000),
    ("Frites surgelées", models.Unit.GRAMME, 0.0025, models.StorageZone.FRIGO_NEGATIF, 15000),
    ("Farine", models.Unit.GRAMME, 0.0012, models.StorageZone.SEC, 20000),
    ("Mozzarella", models.Unit.GRAMME, 0.009, models.StorageZone.FRIGO_POSITIF, 4000),
    ("Sauce tomate", models.Unit.GRAMME, 0.004, models.StorageZone.FRIGO_POSITIF, 6000),
    ("Vin rouge (bouteille)", models.Unit.UNITE, 4.5, models.StorageZone.CAVE, 40),
]

DISHES = [
    ("Burger maison", {
        "Steak haché": 150, "Pain burger": 1, "Salade": 20, "Tomate": 30,
    }),
    ("Salade composée", {
        "Salade": 150, "Tomate": 100, "Mozzarella": 50,
    }),
    ("Pizza Margherita", {
        "Farine": 200, "Sauce tomate": 100, "Mozzarella": 100,
    }),
    ("Frites", {
        "Frites surgelées": 200,
    }),
    ("Verre de vin rouge", {
        "Vin rouge (bouteille)": 0.2,
    }),
]


def seed_demo(db: Session) -> tuple[int, int]:
    """Crée le jeu de démo dans `db`. Renvoie (ingrédients créés, fiches créées) ;
    (0, 0) si des ingrédients existaient déjà."""
    if db.query(models.Ingredient).count() > 0:
        return (0, 0)

    ingredients_by_name = {}
    for name, unit, unit_cost, zone, stock in INGREDIENTS:
        ingredient = models.Ingredient(
            name=name, unit=unit, unit_cost=unit_cost,
            storage_zone=zone, current_theoretical_stock=stock,
        )
        db.add(ingredient)
        ingredients_by_name[name] = ingredient
    db.commit()

    for dish_name, lines in DISHES:
        recipes.upsert_dish(
            db,
            dish_id=None,
            name=dish_name,
            is_active=True,
            lines=[
                recipes.RecipeLineInput(
                    ingredient_id=ingredients_by_name[ing_name].id, quantity=qty
                )
                for ing_name, qty in lines.items()
            ],
        )
    return (len(INGREDIENTS), len(DISHES))


def run() -> None:
    init_db()
    db = SessionLocal()
    try:
        created_ingredients, created_dishes = seed_demo(db)
        if (created_ingredients, created_dishes) == (0, 0):
            print("Des ingrédients existent déjà — le seed ne fait rien (pas d'écrasement).")
        else:
            print(f"Créé {created_ingredients} ingrédient(s) et {created_dishes} fiche(s) technique(s).")
    finally:
        db.close()


if __name__ == "__main__":
    run()
