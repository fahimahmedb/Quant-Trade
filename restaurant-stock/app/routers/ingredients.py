from types import SimpleNamespace

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.flash import redirect
from app.forms import InvalidNumberError, parse_float_fr, parse_optional_float_fr
from app.templating import templates

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


def _name_taken(db: Session, name: str, exclude_id: int | None = None) -> bool:
    query = db.query(models.Ingredient).filter(models.Ingredient.name.ilike(name))
    if exclude_id is not None:
        query = query.filter(models.Ingredient.id != exclude_id)
    return query.first() is not None


def _recent_movements(db: Session, ingredient_id: int, limit: int = 20) -> list[models.StockMovement]:
    return (
        db.query(models.StockMovement)
        .filter(models.StockMovement.ingredient_id == ingredient_id)
        .order_by(models.StockMovement.created_at.desc())
        .limit(limit)
        .all()
    )


def _render_form(request, *, ingredient, movements=None, error=None, status_code=200):
    return templates.TemplateResponse(
        request,
        "ingredients/form.html",
        {
            "request": request,
            "ingredient": ingredient,
            "movements": movements or [],
            "units": list(models.Unit),
            "zones": list(models.StorageZone),
            "error": error,
        },
        status_code=status_code,
    )


@router.get("")
def list_ingredients(request: Request, db: Session = Depends(get_db)):
    ingredients = db.query(models.Ingredient).order_by(
        models.Ingredient.storage_zone, models.Ingredient.name
    ).all()
    return templates.TemplateResponse(request,
        "ingredients/list.html",
        {"request": request, "ingredients": ingredients, "zones": list(models.StorageZone)},
    )


@router.get("/new")
def new_ingredient_form(request: Request):
    return _render_form(request, ingredient=None)


@router.post("/new")
def create_ingredient(
    request: Request,
    name: str = Form(...),
    unit: models.Unit = Form(...),
    unit_cost: str = Form("0"),
    storage_zone: models.StorageZone = Form(...),
    current_theoretical_stock: str = Form("0"),
    alert_threshold: str = Form(""),
    db: Session = Depends(get_db),
):
    name = name.strip()
    # Objet de secours pour ré-afficher exactement ce que l'utilisateur a
    # saisi si la validation échoue, plutôt que de vider le formulaire.
    submitted = SimpleNamespace(
        id=None, name=name, unit=unit, unit_cost=unit_cost, storage_zone=storage_zone,
        current_theoretical_stock=current_theoretical_stock, alert_threshold=alert_threshold,
        is_active=True,
    )
    if _name_taken(db, name):
        return _render_form(request, ingredient=submitted, error=f"Un ingrédient « {name} » existe déjà.", status_code=409)
    try:
        parsed_unit_cost = parse_float_fr(unit_cost)
        parsed_stock = parse_float_fr(current_theoretical_stock)
        parsed_threshold = parse_optional_float_fr(alert_threshold)
    except InvalidNumberError as exc:
        return _render_form(request, ingredient=submitted, error=str(exc), status_code=422)

    ingredient = models.Ingredient(
        name=name,
        unit=unit,
        unit_cost=parsed_unit_cost,
        storage_zone=storage_zone,
        current_theoretical_stock=parsed_stock,
        alert_threshold=parsed_threshold,
    )
    db.add(ingredient)
    db.commit()
    return redirect("/ingredients", f"Ingrédient « {ingredient.name} » créé.")


@router.get("/{ingredient_id}/edit")
def edit_ingredient_form(ingredient_id: int, request: Request, db: Session = Depends(get_db)):
    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return redirect("/ingredients", "Ingrédient introuvable.", error=True)
    return _render_form(request, ingredient=ingredient, movements=_recent_movements(db, ingredient_id))


@router.post("/{ingredient_id}/edit")
def update_ingredient(
    ingredient_id: int,
    request: Request,
    name: str = Form(...),
    unit: models.Unit = Form(...),
    unit_cost: str = Form("0"),
    storage_zone: models.StorageZone = Form(...),
    current_theoretical_stock: str = Form("0"),
    alert_threshold: str = Form(""),
    is_active: bool = Form(False),
    db: Session = Depends(get_db),
):
    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return redirect("/ingredients", "Ingrédient introuvable.", error=True)
    name = name.strip()
    submitted = SimpleNamespace(
        id=ingredient_id, name=name, unit=unit, unit_cost=unit_cost, storage_zone=storage_zone,
        current_theoretical_stock=current_theoretical_stock, alert_threshold=alert_threshold,
        is_active=is_active,
    )
    if _name_taken(db, name, exclude_id=ingredient_id):
        return _render_form(
            request, ingredient=submitted, movements=_recent_movements(db, ingredient_id),
            error=f"Un ingrédient « {name} » existe déjà.", status_code=409,
        )
    try:
        parsed_unit_cost = parse_float_fr(unit_cost)
        parsed_stock = parse_float_fr(current_theoretical_stock)
        parsed_threshold = parse_optional_float_fr(alert_threshold)
    except InvalidNumberError as exc:
        return _render_form(
            request, ingredient=submitted, movements=_recent_movements(db, ingredient_id),
            error=str(exc), status_code=422,
        )

    ingredient.name = name
    ingredient.unit = unit
    ingredient.unit_cost = parsed_unit_cost
    ingredient.storage_zone = storage_zone
    ingredient.current_theoretical_stock = parsed_stock
    ingredient.alert_threshold = parsed_threshold
    ingredient.is_active = is_active
    db.commit()
    return redirect("/ingredients", f"Ingrédient « {ingredient.name} » mis à jour.")


@router.post("/{ingredient_id}/delete")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return redirect("/ingredients", "Ingrédient introuvable.", error=True)
    if ingredient.recipe_lines:
        return redirect(
            "/ingredients",
            f"Impossible de supprimer « {ingredient.name} » : utilisé dans au moins une fiche technique.",
            error=True,
        )
    if ingredient.movements:
        return redirect(
            "/ingredients",
            f"Impossible de supprimer « {ingredient.name} » : historique de mouvements de stock existant "
            "(traçabilité). Désactivez-le plutôt (case « actif ») pour le retirer sans perdre l'historique.",
            error=True,
        )
    db.delete(ingredient)
    db.commit()
    return redirect("/ingredients", f"Ingrédient « {ingredient.name} » supprimé.")
