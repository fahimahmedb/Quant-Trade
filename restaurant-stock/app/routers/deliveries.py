"""Écrans de réception de livraison (F1)."""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Request, UploadFile
from sqlalchemy.orm import Session

from app import models
from app.config import UPLOAD_DIR
from app.database import get_db
from app.flash import redirect
from app.forms import InvalidNumberError, parse_float_fr
from app.services import deliveries, pricing
from app.templating import pluriel, templates

router = APIRouter(prefix="/deliveries", tags=["deliveries"])

ALLOWED_PHOTO_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_PHOTO_BYTES = 8 * 1024 * 1024


def _parse_date_fr(raw: str) -> datetime:
    raw = (raw or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise deliveries.DeliveryError(f"Date de réception invalide : {raw!r}.")


def _price_input_value(price: float) -> str:
    """Valeur d'un <input type=number> : point décimal imposé par HTML, mais
    sans zéros inutiles — « 20 » et « 1.2 » plutôt que « 20.0000 »."""
    return f"{price:.4f}".rstrip("0").rstrip(".") or "0"


def _ingredient_rows(db: Session) -> list[dict]:
    """Ingrédients actifs avec leur prix d'achat pré-rempli, en unité d'achat."""
    ingredients = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.is_active.is_(True))
        .order_by(models.Ingredient.name)
        .all()
    )
    return [
        {
            "ingredient": ing,
            "display_unit": pricing.display_unit(ing.unit),
            "last_price": _price_input_value(
                pricing.to_display_price(deliveries.last_known_price(db, ing), ing.unit)
            ),
        }
        for ing in ingredients
    ]


def _render_new(request, db, *, error=None, status_code=200, submitted=None):
    return templates.TemplateResponse(
        request,
        "deliveries/new.html",
        {
            "request": request,
            "rows": _ingredient_rows(db),
            "suppliers": deliveries.supplier_suggestions(db),
            "today": datetime.now().strftime("%Y-%m-%d"),
            "error": error,
            "submitted": submitted or {},
        },
        status_code=status_code,
    )


@router.get("")
def list_deliveries(request: Request, db: Session = Depends(get_db)):
    receipts = (
        db.query(models.DeliveryReceipt)
        .order_by(models.DeliveryReceipt.received_on.desc(), models.DeliveryReceipt.id.desc())
        .limit(50)
        .all()
    )
    return templates.TemplateResponse(
        request, "deliveries/list.html", {"request": request, "receipts": receipts}
    )


@router.get("/new")
def new_delivery_form(request: Request, db: Session = Depends(get_db)):
    return _render_new(request, db)


async def _save_photo(photo: UploadFile | None) -> str | None:
    if photo is None or not photo.filename:
        return None
    if photo.content_type not in ALLOWED_PHOTO_TYPES:
        raise deliveries.DeliveryError("Photo : formats acceptés JPEG, PNG ou WebP.")
    content = await photo.read()
    if not content:
        return None
    if len(content) > MAX_PHOTO_BYTES:
        raise deliveries.DeliveryError("Photo trop lourde (8 Mo maximum).")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ALLOWED_PHOTO_TYPES[photo.content_type]}"
    (UPLOAD_DIR / name).write_bytes(content)
    return name


@router.post("/new")
async def create_delivery(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    supplier = (form.get("supplier") or "").strip()
    note = (form.get("note") or "").strip()
    raw_date = form.get("received_on") or ""
    submitted = {"supplier": supplier, "note": note, "received_on": raw_date}

    ingredient_ids = form.getlist("ingredient_id")
    quantities = form.getlist("quantity")
    prices = form.getlist("unit_price")

    lines: list[deliveries.DeliveryLineInput] = []
    try:
        received_on = _parse_date_fr(raw_date)
        for raw_id, raw_qty, raw_price in zip(ingredient_ids, quantities, prices):
            if not raw_id or not (raw_qty or "").strip():
                continue  # ligne laissée vide : ignorée, pas une erreur
            ingredient = db.get(models.Ingredient, int(raw_id))
            if ingredient is None:
                raise deliveries.DeliveryError(
                    "Un ingrédient de la réception n'existe plus (supprimé entre la saisie "
                    "et la validation). Rechargez la page et ressaisissez la ligne concernée."
                )
            # Le prix est saisi en unité d'achat (€/kg) et stocké par unité de référence.
            display_price = parse_float_fr(raw_price)
            lines.append(deliveries.DeliveryLineInput(
                ingredient_id=ingredient.id,
                quantity=parse_float_fr(raw_qty),
                unit_price=pricing.to_storage_price(display_price, ingredient.unit),
            ))
        photo_path = await _save_photo(form.get("photo"))
        result = deliveries.record_delivery(
            db, received_on=received_on, supplier=supplier, lines=lines,
            note=note, photo_path=photo_path,
        )
    except (deliveries.DeliveryError, InvalidNumberError) as exc:
        return _render_new(request, db, error=str(exc), status_code=422, submitted=submitted)

    n = len(result.receipt.lines)
    message = f"Réception enregistrée : {n} ligne{pluriel(n)}, stock mis à jour."
    warnings = result.price_alerts + ([result.backdated_warning] if result.backdated_warning else [])
    return redirect(
        f"/deliveries/{result.receipt.id}",
        message,
        alerts=" | ".join(warnings) if warnings else None,
    )


@router.get("/{receipt_id}")
def delivery_detail(receipt_id: int, request: Request, db: Session = Depends(get_db)):
    receipt = db.get(models.DeliveryReceipt, receipt_id)
    if receipt is None:
        return redirect("/deliveries", "Réception introuvable.", error=True)
    return templates.TemplateResponse(
        request, "deliveries/detail.html", {"request": request, "receipt": receipt}
    )
