from sqlalchemy.orm import Session

from app import models


def get_settings(db: Session) -> models.Settings:
    settings = db.get(models.Settings, 1)
    if settings is None:
        settings = models.Settings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(
    db: Session,
    *,
    safety_days: float,
    target_days: float,
    rolling_window_days: int,
    price_alert_pct: float | None = None,
) -> models.Settings:
    settings = get_settings(db)
    settings.safety_days = safety_days
    settings.target_days = target_days
    settings.rolling_window_days = rolling_window_days
    if price_alert_pct is not None:
        settings.price_alert_pct = price_alert_pct
    db.commit()
    db.refresh(settings)
    return settings
