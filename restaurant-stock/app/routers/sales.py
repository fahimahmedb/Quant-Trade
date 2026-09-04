from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.flash import redirect
from app.services import sales_import
from app.templating import pluriel, templates

router = APIRouter(prefix="/sales", tags=["sales"])


def _decode(raw_bytes: bytes) -> str:
    """Les exports Excel français sont souvent en Windows-1252, pas en UTF-8."""
    try:
        return raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw_bytes.decode("cp1252")


@router.get("/import")
def import_form(request: Request, db: Session = Depends(get_db)):
    recent_imports = (
        db.query(models.SalesImport).order_by(models.SalesImport.imported_at.desc()).limit(20).all()
    )
    return templates.TemplateResponse(request,
        "sales/import.html", {"request": request, "recent_imports": recent_imports}
    )


@router.post("/import")
async def handle_import(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw_bytes = await file.read()
    if not raw_bytes:
        return redirect("/sales/import", "Fichier vide.", error=True)
    content = _decode(raw_bytes)
    sales_import_row, parsed = sales_import.import_sales(db, file.filename or "export.csv", content)

    n = sales_import_row.row_count
    message = f"{n} ligne{pluriel(n)} importée{pluriel(n)}."
    error_summary = None
    if parsed.errors:
        n_err = len(parsed.errors)
        message += f" {n_err} ligne{pluriel(n_err)} ignorée{pluriel(n_err)} (voir détail ci-dessous)."
        error_summary = "; ".join(parsed.errors[:5])
        reste = n_err - 5
        if reste > 0:
            error_summary += f"; et {reste} autre{pluriel(reste)}"
    return redirect(
        f"/sales/imports/{sales_import_row.id}",
        message,
        error=bool(parsed.errors),
        errors=error_summary,
    )


@router.get("/imports/{import_id}")
def import_detail(import_id: int, request: Request, db: Session = Depends(get_db)):
    sales_import_row = db.get(models.SalesImport, import_id)
    if sales_import_row is None:
        return redirect("/sales/import", "Import introuvable.", error=True)
    unmatched = sales_import.unmatched_raw_names(db, import_id)
    dishes = db.query(models.Dish).order_by(models.Dish.name).all()
    return templates.TemplateResponse(request,
        "sales/detail.html",
        {
            "request": request,
            "sales_import": sales_import_row,
            "unmatched": unmatched,
            "dishes": dishes,
        },
    )


@router.post("/imports/{import_id}/map")
async def map_dish(import_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    raw_name = (form.get("raw_name") or "").strip()
    dish_id_raw = form.get("dish_id") or ""
    new_dish_name = (form.get("new_dish_name") or "").strip()

    if new_dish_name:
        existing = (
            db.query(models.Dish)
            .filter(models.Dish.name.ilike(new_dish_name))
            .one_or_none()
        )
        if existing is not None:
            dish_id = existing.id
        else:
            dish = models.Dish(name=new_dish_name)
            db.add(dish)
            db.commit()
            db.refresh(dish)
            dish_id = dish.id
    elif dish_id_raw:
        dish_id = int(dish_id_raw)
    else:
        return redirect(f"/sales/imports/{import_id}", "Choisissez un plat existant ou nommez-en un nouveau.", error=True)

    count = sales_import.map_raw_name_to_dish(db, raw_name, dish_id)
    return redirect(
        f"/sales/imports/{import_id}",
        f"« {raw_name} » rattaché ({count} ligne{pluriel(count)} mise{pluriel(count)} à jour). "
        "Le mappage sera réutilisé automatiquement.",
    )
