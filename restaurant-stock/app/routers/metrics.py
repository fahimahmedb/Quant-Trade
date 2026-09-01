from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import metrics
from app.templating import templates

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
def metrics_dashboard(request: Request, db: Session = Depends(get_db)):
    adoption = metrics.suggestion_adoption_stats(db)
    duration = metrics.counting_duration_stats(db)
    trend = metrics.variance_trend(db)
    return templates.TemplateResponse(request,
        "metrics/dashboard.html",
        {"request": request, "adoption": adoption, "duration": duration, "trend": trend},
    )
