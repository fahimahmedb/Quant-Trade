from types import SimpleNamespace

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.flash import redirect
from app.forms import parse_float_fr
from app.services import recipes
from app.templating import templates

router = APIRouter(prefix="/recipes", tags=["recipes"])


def _render_form(request, db, *, dish, lines, error=None, status_code=200):
    ingredients = db.query(models.Ingredient).order_by(models.Ingredient.name).all()
    return templates.TemplateResponse(
        request,
        "recipes/form.html",
        {"request": request, "dish": dish, "ingredients": ingredients, "lines": lines, "error": error},
        status_code=status_code,
    )


@router.get("")
def list_recipes(request: Request, db: Session = Depends(get_db)):
    dishes = db.query(models.Dish).order_by(models.Dish.name).all()
    return templates.TemplateResponse(request, "recipes/list.html", {"request": request, "dishes": dishes})


@router.get("/new")
def new_recipe_form(request: Request, db: Session = Depends(get_db)):
    return _render_form(request, db, dish=None, lines=[])


async def _read_lines_from_form(request: Request) -> list[recipes.RecipeLineInput]:
    form = await request.form()
    ingredient_ids = form.getlist("ingredient_id")
    quantities = form.getlist("quantity")
    lines = []
    for raw_id, raw_qty in zip(ingredient_ids, quantities):
        if not raw_id or not raw_qty:
            continue
        try:
            lines.append(
                recipes.RecipeLineInput(ingredient_id=int(raw_id), quantity=parse_float_fr(raw_qty))
            )
        except ValueError:
            continue
    return lines


@router.post("/new")
async def create_recipe(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    name = (form.get("name") or "").strip()
    is_active = form.get("is_active") is not None
    lines = await _read_lines_from_form(request)
    submitted = SimpleNamespace(id=None, name=name, is_active=is_active)
    if not name:
        return _render_form(request, db, dish=submitted, lines=lines, error="Le nom du plat est obligatoire.", status_code=422)
    try:
        dish = recipes.upsert_dish(db, dish_id=None, name=name, is_active=is_active, lines=lines)
    except recipes.DuplicateNameError as exc:
        return _render_form(request, db, dish=submitted, lines=lines, error=str(exc), status_code=409)
    return redirect("/recipes", f"Fiche technique « {dish.name} » créée.")


@router.get("/{dish_id}/edit")
def edit_recipe_form(dish_id: int, request: Request, db: Session = Depends(get_db)):
    dish = db.get(models.Dish, dish_id)
    if dish is None:
        return redirect("/recipes", "Plat introuvable.", error=True)
    return _render_form(request, db, dish=dish, lines=dish.recipe_lines)


@router.post("/{dish_id}/edit")
async def update_recipe(dish_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    name = (form.get("name") or "").strip()
    is_active = form.get("is_active") is not None
    lines = await _read_lines_from_form(request)
    submitted = SimpleNamespace(id=dish_id, name=name, is_active=is_active)
    if not name:
        return _render_form(request, db, dish=submitted, lines=lines, error="Le nom du plat est obligatoire.", status_code=422)
    try:
        dish = recipes.upsert_dish(db, dish_id=dish_id, name=name, is_active=is_active, lines=lines)
    except recipes.DuplicateNameError as exc:
        return _render_form(request, db, dish=submitted, lines=lines, error=str(exc), status_code=409)
    return redirect("/recipes", f"Fiche technique « {dish.name} » mise à jour.")


@router.post("/{dish_id}/delete")
def delete_recipe(dish_id: int, db: Session = Depends(get_db)):
    dish = db.get(models.Dish, dish_id)
    if dish is None:
        return redirect("/recipes", "Plat introuvable.", error=True)
    name = dish.name
    recipes.delete_dish(db, dish_id)
    return redirect("/recipes", f"Fiche technique « {name} » supprimée.")
