from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.flash import redirect
from app.forms import InvalidNumberError, parse_float_fr
from app.services import ordering
from app.templating import pluriel, templates

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def orders_home(request: Request, db: Session = Depends(get_db)):
    latest_batch = (
        db.query(models.OrderSuggestionBatch)
        .order_by(models.OrderSuggestionBatch.generated_at.desc())
        .first()
    )
    if latest_batch is None:
        return templates.TemplateResponse(request, "orders/empty.html", {"request": request})
    return redirect(f"/orders/{latest_batch.id}")


@router.post("/generate")
def generate(db: Session = Depends(get_db)):
    batch = ordering.generate_suggestions(db)
    n = len(batch.lines)
    message = (
        f"{n} suggestion{pluriel(n)} générée{pluriel(n)}."
        if batch.lines
        else "Aucun ingrédient sous son seuil actuellement : rien à suggérer."
    )
    return redirect(f"/orders/{batch.id}", message)


@router.get("/{batch_id}")
def batch_detail(batch_id: int, request: Request, db: Session = Depends(get_db)):
    batch = db.get(models.OrderSuggestionBatch, batch_id)
    if batch is None:
        return redirect("/orders", "Lot de suggestions introuvable.", error=True)
    history = (
        db.query(models.OrderSuggestionBatch)
        .filter(models.OrderSuggestionBatch.id != batch_id)
        .order_by(models.OrderSuggestionBatch.generated_at.desc())
        .limit(10)
        .all()
    )
    # Une ligne en attente reflète le stock du moment de la GÉNÉRATION du
    # lot, pas forcément le stock actuel : un comptage recale le stock
    # théorique sans jamais toucher les lignes déjà générées (section 3.4).
    # On la resynchronise donc à chaque affichage, avant que quelqu'un ne
    # valide une quantité calculée sur un chiffre devenu faux.
    for line in batch.lines:
        ordering.refresh_pending_line(db, line)

    lines = sorted(batch.lines, key=lambda line: line.ingredient.name)
    return templates.TemplateResponse(request,
        "orders/detail.html",
        {"request": request, "batch": batch, "lines": lines, "history": history},
    )


@router.post("/lines/{line_id}/decide")
async def decide_line(line_id: int, request: Request, db: Session = Depends(get_db)):
    line = db.get(models.OrderSuggestionLine, line_id)
    if line is None:
        return redirect("/orders", "Ligne de suggestion introuvable.", error=True)

    form = await request.form()
    action = form.get("action")
    batch_id = line.batch_id

    if action == "reject":
        ordering.decide_suggestion_line(
            db, line_id, final_quantity=0, decision=models.SuggestionDecision.REJETEE
        )
        return redirect(f"/orders/{batch_id}", "Suggestion rejetée.")

    raw_qty = (form.get("final_quantity") or "").strip()
    try:
        final_qty = parse_float_fr(raw_qty)
    except InvalidNumberError:
        return redirect(f"/orders/{batch_id}", "Quantité invalide.", error=True)

    decision = (
        models.SuggestionDecision.ACCEPTEE
        if abs(final_qty - line.suggested_quantity) < 1e-9
        else models.SuggestionDecision.MODIFIEE
    )
    ordering.decide_suggestion_line(db, line_id, final_quantity=final_qty, decision=decision)
    return redirect(f"/orders/{batch_id}", "Quantité de commande validée.")
