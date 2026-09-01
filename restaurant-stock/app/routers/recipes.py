from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.flash import redirect
from app.services import recipes
from app.templating import templates

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("")
def list_recipes(request: Request, db: Session = Depends(get_db)):
    dishes = db.query(models.Dish).order_by(models.Dish.name).all()
    return templates.TemplateResponse(request, "recipes/list.html", {"request": request, "dishes": dishes})


@router.get("/new")
def new_recipe_form(request: Request, db: Session = Depends(get_db)):
    ingredients = db.query(models.Ingredient).order_by(models.Ingredient.name).all()
    return templates.TemplateResponse(request,
        "recipes/form.html",
        {"request": request, "dish": None, "ingredients": ingredients, "lines": []},
    )


async def _read_lines_from_form(request: Request) -> list[recipes.RecipeLineInput]:
    form = await request.form()
    ingredient_ids = form.getlist("ingredient_id")
    quantities = form.getlist("quantity")
    lines = []
    for raw_id, raw_qty in zip(ingredient_ids, quantities):
        if not raw_id or not raw_qty:
            continue
        try:
            lines.append(recipes.RecipeLineInput(ingredient_id=int(raw_id), quantity=float(raw_qty)))
        except ValueError:
            continue
    return lines


@router.post("/new")
async def create_recipe(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    name = (form.get("name") or "").strip()
    is_active = form.get("is_active") is not None
    lines = await _read_lines_from_form(request)
    if not name:
        return redirect("/recipes/new", "Le nom du plat est obligatoire.", error=True)
    try:
        dish = recipes.upsert_dish(db, dish_id=None, name=name, is_active=is_active, lines=lines)
    except recipes.DuplicateNameError as exc:
        return redirect("/recipes/new", str(exc), error=True)
    return redirect("/recipes", f"Fiche technique « {dish.name} » créée.")


@router.get("/{dish_id}/edit")
def edit_recipe_form(dish_id: int, request: Request, db: Session = Depends(get_db)):
    dish = db.get(models.Dish, dish_id)
    if dish is None:
        return redirect("/recipes", "Plat introuvable.", error=True)
    ingredients = db.query(models.Ingredient).order_by(models.Ingredient.name).all()
    return templates.TemplateResponse(request,
        "recipes/form.html",
        {"request": request, "dish": dish, "ingredients": ingredients, "lines": dish.recipe_lines},
    )


@router.post("/{dish_id}/edit")
async def update_recipe(dish_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    name = (form.get("name") or "").strip()
    is_active = form.get("is_active") is not None
    lines = await _read_lines_from_form(request)
    if not name:
        return redirect(f"/recipes/{dish_id}/edit", "Le nom du plat est obligatoire.", error=True)
    try:
        dish = recipes.upsert_dish(db, dish_id=dish_id, name=name, is_active=is_active, lines=lines)
    except recipes.DuplicateNameError as exc:
        return redirect(f"/recipes/{dish_id}/edit", str(exc), error=True)
    return redirect("/recipes", f"Fiche technique « {dish.name} » mise à jour.")


@router.post("/{dish_id}/delete")
def delete_recipe(dish_id: int, db: Session = Depends(get_db)):
    dish = db.get(models.Dish, dish_id)
    if dish is None:
        return redirect("/recipes", "Plat introuvable.", error=True)
    name = dish.name
    recipes.delete_dish(db, dish_id)
    return redirect("/recipes", f"Fiche technique « {name} » supprimée.")
