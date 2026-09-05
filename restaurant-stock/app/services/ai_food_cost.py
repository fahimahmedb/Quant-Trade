"""F9 — food cost théorique vs réel sur une période (Lot IA-0,
docs/IA scope.md §1.9, cible SYN-H).

Food cost théorique = coût recette (fiche technique, coût actuel) des
plats effectivement vendus / chiffre d'affaires de la période. Ne dépend
d'aucun comptage : c'est ce que la carte DEVRAIT coûter.

Food cost réel = consommation physiquement constatée / chiffre d'affaires :
(stock d'ouverture + réceptions de la période − stock de clôture), valorisé
au coût unitaire ACTUEL de chaque ingrédient (même convention que
`CountLine.variance_value` ailleurs dans l'app — pas de FIFO/coût
historique, cohérent avec le reste du projet plutôt qu'une précision que
rien d'autre ici n'offre). Exige un comptage encadrant la période de
chaque côté : sans eux, aucun stock réel connu, seule la règle v1
théorique reste disponible.
"""
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service


@dataclass
class FoodCostResult:
    ok: bool
    message: str | None
    theoretical_pct: float | None = None
    real_pct: float | None = None
    revenue: float | None = None
    theoretical_cost: float | None = None
    real_cost: float | None = None


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f9_enabled


def _bracketing_session(db: Session, ended_at: datetime, *, before: bool) -> models.CountSession | None:
    query = db.query(models.CountSession).filter(models.CountSession.ended_at.isnot(None))
    if before:
        query = query.filter(models.CountSession.ended_at <= ended_at).order_by(models.CountSession.ended_at.desc())
    else:
        query = query.filter(models.CountSession.ended_at >= ended_at).order_by(models.CountSession.ended_at.asc())
    return query.first()


def compute_food_cost(db: Session, start: datetime, end: datetime) -> FoodCostResult:
    """docs/IA scope.md §1.9 (SYN-H) : théorique et réel, sur [start, end]."""
    if not _feature_enabled(db):
        return FoodCostResult(ok=False, message="Fonctionnalité F9 désactivée (feature flag éteint).")

    sales = (
        db.query(models.SaleLine)
        .filter(models.SaleLine.sale_date >= start, models.SaleLine.sale_date <= end)
        .all()
    )
    revenue = sum(s.quantity_sold * (s.unit_price or 0.0) for s in sales)
    if revenue <= 0:
        return FoodCostResult(ok=False, message="Aucun chiffre d'affaires sur cette période.")

    theoretical_cost = sum(
        s.quantity_sold * s.dish.food_cost for s in sales if s.dish is not None
    )
    theoretical_pct = theoretical_cost / revenue * 100.0

    opening = _bracketing_session(db, start, before=True)
    closing = _bracketing_session(db, end, before=False)
    if opening is None or closing is None:
        return FoodCostResult(
            ok=False, message="Comptage d'ouverture ou de clôture manquant pour cette période.",
            theoretical_pct=theoretical_pct, revenue=revenue, theoretical_cost=theoretical_cost,
        )

    opening_qty = {l.ingredient_id: l.counted_quantity for l in opening.lines if l.counted_quantity is not None}
    closing_qty = {l.ingredient_id: l.counted_quantity for l in closing.lines if l.counted_quantity is not None}

    receipts_value: dict[int, float] = {}
    receipt_lines = (
        db.query(models.DeliveryLine)
        .join(models.DeliveryReceipt)
        .filter(models.DeliveryReceipt.received_on > start, models.DeliveryReceipt.received_on <= end)
        .all()
    )
    for line in receipt_lines:
        receipts_value[line.ingredient_id] = receipts_value.get(line.ingredient_id, 0.0) + line.quantity * line.unit_price

    real_cost = 0.0
    for ingredient_id in set(opening_qty) & set(closing_qty):
        ingredient = db.get(models.Ingredient, ingredient_id)
        real_cost += (
            opening_qty[ingredient_id] * ingredient.unit_cost
            + receipts_value.get(ingredient_id, 0.0)
            - closing_qty[ingredient_id] * ingredient.unit_cost
        )
    real_pct = real_cost / revenue * 100.0

    return FoodCostResult(
        ok=True, message=None, theoretical_pct=theoretical_pct, real_pct=real_pct,
        revenue=revenue, theoretical_cost=theoretical_cost, real_cost=real_cost,
    )
