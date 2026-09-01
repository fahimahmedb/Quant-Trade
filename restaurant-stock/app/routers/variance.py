from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services import counting
from app.templating import templates

router = APIRouter(prefix="/variance", tags=["variance"])


@router.get("")
def variance_dashboard(request: Request, session_id: int | None = None, db: Session = Depends(get_db)):
    sessions = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.isnot(None))
        .order_by(models.CountSession.ended_at.desc())
        .all()
    )
    selected = None
    report = []
    if sessions:
        selected = next((s for s in sessions if s.id == session_id), sessions[0])
        report = counting.variance_report(db, selected.id)

    return templates.TemplateResponse(request,
        "variance/list.html",
        {"request": request, "sessions": sessions, "selected": selected, "report": report},
    )
