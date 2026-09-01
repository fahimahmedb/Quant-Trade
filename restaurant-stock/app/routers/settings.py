from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.flash import redirect
from app.services import settings_service
from app.templating import templates

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def settings_form(request: Request, db: Session = Depends(get_db)):
    settings = settings_service.get_settings(db)
    return templates.TemplateResponse(request, "settings/form.html", {"request": request, "settings": settings})


@router.post("")
def update_settings(
    safety_days: float = Form(...),
    target_days: float = Form(...),
    rolling_window_days: int = Form(...),
    db: Session = Depends(get_db),
):
    settings_service.update_settings(
        db,
        safety_days=safety_days,
        target_days=target_days,
        rolling_window_days=rolling_window_days,
    )
    return redirect("/settings", "Réglages mis à jour.")
