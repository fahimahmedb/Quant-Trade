from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services import counting
from app.templating import templates

router = APIRouter(tags=["dashboard"])


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    latest_session = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.isnot(None))
        .order_by(models.CountSession.ended_at.desc())
        .first()
    )
    top_variances = []
    variance_total = 0.0
    variance_count = 0
    counted_lines = 0
    conform_lines = 0
    if latest_session:
        report = counting.variance_report(db, latest_session.id)
        # Le total porte sur toute la session, pas sur les cinq lignes
        # affichées : c'est le chiffre qui justifie l'outil, il serait faux
        # de le calculer sur un extrait.
        variance_total = sum(abs(line.variance_value or 0) for line in report)
        variance_count = sum(1 for line in report if (line.variance or 0) != 0)
        # Le héros de l'accueil met en avant l'indicateur favorable, pas la
        # perte : c'est le nombre de lignes conformes qui y figure en grand.
        counted_lines = len(report)
        conform_lines = counted_lines - variance_count
        top_variances = report[:5]

    pending_suggestions = (
        db.query(models.OrderSuggestionLine)
        .filter(models.OrderSuggestionLine.decision == models.SuggestionDecision.EN_ATTENTE)
        .count()
    )
    open_session = (
        db.query(models.CountSession).filter(models.CountSession.ended_at.is_(None)).first()
    )
    open_session_counted = 0
    open_session_total = 0
    if open_session:
        open_session_total = len(open_session.lines)
        open_session_counted = sum(
            1 for line in open_session.lines if line.counted_quantity is not None
        )
    dish_count = db.query(models.Dish).filter(models.Dish.is_active.is_(True)).count()
    ingredient_count = db.query(models.Ingredient).filter(models.Ingredient.is_active.is_(True)).count()

    return templates.TemplateResponse(request,
        "dashboard.html",
        {
            "request": request,
            "latest_session": latest_session,
            "top_variances": top_variances,
            "variance_total": variance_total,
            "variance_count": variance_count,
            "counted_lines": counted_lines,
            "conform_lines": conform_lines,
            "pending_suggestions": pending_suggestions,
            "open_session": open_session,
            "open_session_counted": open_session_counted,
            "open_session_total": open_session_total,
            "dish_count": dish_count,
            "ingredient_count": ingredient_count,
        },
    )
