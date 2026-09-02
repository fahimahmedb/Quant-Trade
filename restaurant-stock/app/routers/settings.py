from types import SimpleNamespace

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.flash import redirect
from app.forms import InvalidNumberError, parse_float_fr, parse_int_fr
from app.services import settings_service
from app.templating import templates

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def settings_form(request: Request, db: Session = Depends(get_db)):
    settings = settings_service.get_settings(db)
    return templates.TemplateResponse(request, "settings/form.html", {"request": request, "settings": settings})


@router.post("")
def update_settings(
    request: Request,
    safety_days: str = Form(...),
    target_days: str = Form(...),
    rolling_window_days: str = Form(...),
    price_alert_pct: str = Form("15"),
    db: Session = Depends(get_db),
):
    submitted = SimpleNamespace(
        safety_days=safety_days, target_days=target_days,
        rolling_window_days=rolling_window_days, price_alert_pct=price_alert_pct,
    )
    try:
        parsed_safety_days = parse_float_fr(safety_days)
        parsed_target_days = parse_float_fr(target_days)
        parsed_window_days = parse_int_fr(rolling_window_days)
        parsed_price_alert = parse_float_fr(price_alert_pct)
    except InvalidNumberError as exc:
        return templates.TemplateResponse(
            request,
            "settings/form.html",
            {"request": request, "settings": submitted, "error": str(exc)},
            status_code=422,
        )

    settings_service.update_settings(
        db,
        safety_days=parsed_safety_days,
        target_days=parsed_target_days,
        rolling_window_days=parsed_window_days,
        price_alert_pct=parsed_price_alert,
    )
    return redirect("/settings", "Réglages mis à jour.")
