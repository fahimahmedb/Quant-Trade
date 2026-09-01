from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.flash import redirect
from app.forms import InvalidNumberError, parse_float_fr
from app.services import counting
from app.templating import templates

router = APIRouter(prefix="/counting", tags=["counting"])


@router.get("")
def counting_home(request: Request, db: Session = Depends(get_db)):
    open_session = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.is_(None))
        .order_by(models.CountSession.started_at.desc())
        .first()
    )
    history = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.isnot(None))
        .order_by(models.CountSession.ended_at.desc())
        .limit(10)
        .all()
    )
    return templates.TemplateResponse(request,
        "counting/home.html",
        {"request": request, "open_session": open_session, "history": history},
    )


@router.post("/start")
def start_session(counted_by: str = "", db: Session = Depends(get_db)):
    session = counting.start_count_session(db, counted_by=counted_by.strip() or None)
    if not session.lines:
        return redirect(
            "/counting",
            "Aucun ingrédient actif à compter — ajoutez d'abord vos ingrédients.",
            error=True,
        )
    return redirect(f"/counting/{session.id}", "Comptage démarré.")


@router.get("/{session_id}")
def counting_session_view(session_id: int, request: Request, db: Session = Depends(get_db)):
    session = db.get(models.CountSession, session_id)
    if session is None:
        return redirect("/counting", "Session de comptage introuvable.", error=True)
    if session.is_completed:
        return redirect(f"/counting/{session_id}/summary")

    zones = list(models.StorageZone)
    lines_by_zone = {zone: [] for zone in zones}
    for line in session.lines:
        lines_by_zone[line.ingredient.storage_zone].append(line)
    for zone_lines in lines_by_zone.values():
        zone_lines.sort(key=lambda line: line.ingredient.name)

    counted = sum(1 for line in session.lines if line.counted_quantity is not None)
    return templates.TemplateResponse(request,
        "counting/session.html",
        {
            "request": request,
            "session": session,
            "zones": zones,
            "lines_by_zone": lines_by_zone,
            "reasons": list(models.VarianceReason),
            "counted": counted,
            "total": len(session.lines),
        },
    )


@router.post("/{session_id}/zone/{zone}")
async def save_zone(
    session_id: int, zone: models.StorageZone, request: Request, db: Session = Depends(get_db)
):
    session = db.get(models.CountSession, session_id)
    if session is None or session.is_completed:
        return redirect("/counting", "Session de comptage introuvable ou déjà close.", error=True)

    form = await request.form()
    saved = 0
    for line in session.lines:
        if line.ingredient.storage_zone != zone:
            continue
        raw_value = form.get(f"count_{line.id}")
        if raw_value is None or raw_value.strip() == "":
            continue
        try:
            counted_quantity = parse_float_fr(raw_value)
        except InvalidNumberError:
            continue
        raw_reason = form.get(f"reason_{line.id}") or ""
        try:
            reason = models.VarianceReason(raw_reason) if raw_reason else None
        except ValueError:
            reason = None
        counting.confirm_count_line(db, line.id, counted_quantity, reason)
        saved += 1

    return redirect(f"/counting/{session_id}#zone-{zone.value}", f"{saved} ligne(s) enregistrée(s) — {zone.label}.")


@router.post("/{session_id}/complete")
def complete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(models.CountSession, session_id)
    if session is None:
        return redirect("/counting", "Session de comptage introuvable.", error=True)
    counting.complete_count_session(db, session_id)
    return redirect(f"/counting/{session_id}/summary", "Comptage terminé, stock théorique recalé.")


@router.get("/{session_id}/summary")
def session_summary(session_id: int, request: Request, db: Session = Depends(get_db)):
    session = db.get(models.CountSession, session_id)
    if session is None:
        return redirect("/counting", "Session de comptage introuvable.", error=True)
    report = counting.variance_report(db, session_id)
    total_value = sum(line.variance_value or 0 for line in report)
    return templates.TemplateResponse(request,
        "counting/summary.html",
        {"request": request, "session": session, "report": report, "total_value": total_value},
    )
