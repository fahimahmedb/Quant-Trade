from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.flash import redirect
from app.templating import templates

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


def _name_taken(db: Session, name: str, exclude_id: int | None = None) -> bool:
    query = db.query(models.Ingredient).filter(models.Ingredient.name.ilike(name))
    if exclude_id is not None:
        query = query.filter(models.Ingredient.id != exclude_id)
    return query.first() is not None


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
    return templates.TemplateResponse(request,
        "ingredients/form.html",
        {
            "request": request,
            "ingredient": None,
            "units": list(models.Unit),
            "zones": list(models.StorageZone),
        },
    )


@router.post("/new")
def create_ingredient(
    request: Request,
    name: str = Form(...),
    unit: models.Unit = Form(...),
    unit_cost: float = Form(0.0),
    storage_zone: models.StorageZone = Form(...),
    current_theoretical_stock: float = Form(0.0),
    alert_threshold: str = Form(""),
    db: Session = Depends(get_db),
):
    name = name.strip()
    if _name_taken(db, name):
        return redirect("/ingredients/new", f"Un ingrédient « {name} » existe déjà.", error=True)
    ingredient = models.Ingredient(
        name=name,
        unit=unit,
        unit_cost=unit_cost,
        storage_zone=storage_zone,
        current_theoretical_stock=current_theoretical_stock,
        alert_threshold=float(alert_threshold) if alert_threshold.strip() else None,
    )
    db.add(ingredient)
    db.commit()
    return redirect("/ingredients", f"Ingrédient « {ingredient.name} » créé.")


@router.get("/{ingredient_id}/edit")
def edit_ingredient_form(ingredient_id: int, request: Request, db: Session = Depends(get_db)):
    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return redirect("/ingredients", "Ingrédient introuvable.", error=True)
    return templates.TemplateResponse(request,
        "ingredients/form.html",
        {
            "request": request,
            "ingredient": ingredient,
            "units": list(models.Unit),
            "zones": list(models.StorageZone),
        },
    )


@router.post("/{ingredient_id}/edit")
def update_ingredient(
    ingredient_id: int,
    name: str = Form(...),
    unit: models.Unit = Form(...),
    unit_cost: float = Form(0.0),
    storage_zone: models.StorageZone = Form(...),
    current_theoretical_stock: float = Form(0.0),
    alert_threshold: str = Form(""),
    is_active: bool = Form(False),
    db: Session = Depends(get_db),
):
    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return redirect("/ingredients", "Ingrédient introuvable.", error=True)
    name = name.strip()
    if _name_taken(db, name, exclude_id=ingredient_id):
        return redirect(
            f"/ingredients/{ingredient_id}/edit", f"Un ingrédient « {name} » existe déjà.", error=True
        )
    ingredient.name = name
    ingredient.unit = unit
    ingredient.unit_cost = unit_cost
    ingredient.storage_zone = storage_zone
    ingredient.current_theoretical_stock = current_theoretical_stock
    ingredient.alert_threshold = float(alert_threshold) if alert_threshold.strip() else None
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
    db.delete(ingredient)
    db.commit()
    return redirect("/ingredients", f"Ingrédient « {ingredient.name} » supprimé.")
