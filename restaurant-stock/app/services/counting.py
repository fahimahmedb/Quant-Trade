"""Comptage physique et écart théorique/réel (sections 4.4, 4.5, 5)."""
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import stock


def start_count_session(db: Session, counted_by: str | None = None) -> models.CountSession:
    """Crée une session et pré-remplit une ligne par ingrédient actif avec le
    stock théorique courant — le cuisinier confirme ou corrige, il ne ressaisit
    pas depuis zéro (section 5)."""
    session = models.CountSession(counted_by=counted_by)
    db.add(session)
    db.flush()

    ingredients = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.is_active.is_(True))
        .order_by(models.Ingredient.storage_zone, models.Ingredient.name)
        .all()
    )
    for ingredient in ingredients:
        db.add(
            models.CountLine(
                count_session_id=session.id,
                ingredient_id=ingredient.id,
                theoretical_quantity=ingredient.current_theoretical_stock,
            )
        )
    db.commit()
    db.refresh(session)
    return session


def confirm_count_line(
    db: Session,
    line_id: int,
    counted_quantity: float,
    variance_reason: models.VarianceReason | None = None,
) -> models.CountLine:
    line = db.get(models.CountLine, line_id)
    if line is None:
        raise ValueError(f"Ligne de comptage introuvable : {line_id}")
    line.counted_quantity = counted_quantity
    line.variance_reason = variance_reason
    line.confirmed_at = datetime.utcnow()
    db.commit()
    db.refresh(line)
    return line


def complete_count_session(db: Session, session_id: int) -> models.CountSession:
    """Clôture la session : le stock réel confirmé devient le nouveau stock
    théorique de référence pour chaque ingrédient compté."""
    session = db.get(models.CountSession, session_id)
    if session is None:
        raise ValueError(f"Session de comptage introuvable : {session_id}")

    for line in session.lines:
        if line.counted_quantity is None:
            continue
        delta = line.counted_quantity - line.ingredient.current_theoretical_stock
        if delta != 0:
            stock.record_movement(
                db,
                line.ingredient,
                models.MovementType.COMPTAGE,
                delta,
                reference=f"comptage#{session.id}",
            )

    session.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def variance_report(db: Session, session_id: int) -> list[models.CountLine]:
    """Lignes comptées de la session, triées par écart en valeur (€) décroissant."""
    session = db.get(models.CountSession, session_id)
    if session is None:
        raise ValueError(f"Session de comptage introuvable : {session_id}")
    counted = [line for line in session.lines if line.counted_quantity is not None]
    counted.sort(key=lambda line: abs(line.variance_value or 0), reverse=True)
    return counted
