"""Journalisation des mouvements de stock théorique.

Un seul point d'entrée pour modifier `Ingredient.current_theoretical_stock`
afin que chaque variation soit tracée dans StockMovement (indicateur 8 du
brief : écart théorique/réel dans le temps).
"""
from sqlalchemy.orm import Session

from app import models


def record_movement(
    db: Session,
    ingredient: models.Ingredient,
    movement_type: models.MovementType,
    quantity_delta: float,
    reference: str | None = None,
) -> models.StockMovement:
    ingredient.current_theoretical_stock += quantity_delta
    movement = models.StockMovement(
        ingredient_id=ingredient.id,
        movement_type=movement_type,
        quantity_delta=quantity_delta,
        resulting_stock=ingredient.current_theoretical_stock,
        reference=reference,
    )
    db.add(movement)
    return movement
