"""Réception de livraison et historique des prix (Specs V2, F1).

Seule entrée de stock de l'application : sans elle, le stock théorique
dérive à chaque livraison jusqu'au comptage suivant et les prix restent
figés à la saisie initiale.
"""
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.services import settings_service, stock


class DeliveryError(ValueError):
    """Erreur métier de saisie de réception, à afficher telle quelle au gérant."""


@dataclass
class DeliveryLineInput:
    ingredient_id: int
    quantity: float
    unit_price: float  # € par unité de référence de l'ingrédient


@dataclass
class DeliveryResult:
    receipt: models.DeliveryReceipt
    price_alerts: list[str] = field(default_factory=list)
    backdated_warning: str | None = None


def last_known_price(db: Session, ingredient: models.Ingredient) -> float:
    """Prix à pré-remplir : le dernier prix d'achat connu, sinon le prix courant."""
    latest = (
        db.query(models.PriceHistory)
        .filter(models.PriceHistory.ingredient_id == ingredient.id)
        .order_by(models.PriceHistory.recorded_at.desc(), models.PriceHistory.id.desc())
        .first()
    )
    return latest.unit_price if latest else ingredient.unit_cost


def supplier_suggestions(db: Session, limit: int = 20) -> list[str]:
    """Fournisseurs déjà saisis, du plus récent au plus ancien (mémorisation F1)."""
    rows = (
        db.query(models.DeliveryReceipt.supplier, func.max(models.DeliveryReceipt.id).label("last_id"))
        .filter(models.DeliveryReceipt.supplier.isnot(None))
        .filter(models.DeliveryReceipt.supplier != "")
        .group_by(models.DeliveryReceipt.supplier)
        .order_by(func.max(models.DeliveryReceipt.id).desc())
        .limit(limit)
        .all()
    )
    return [row[0] for row in rows]


def _last_completed_count(db: Session) -> models.CountSession | None:
    return (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.isnot(None))
        .order_by(models.CountSession.ended_at.desc())
        .first()
    )


def record_delivery(
    db: Session,
    *,
    received_on: datetime,
    supplier: str | None,
    lines: list[DeliveryLineInput],
    note: str | None = None,
    photo_path: str | None = None,
) -> DeliveryResult:
    """Enregistre une réception : stock +=, prix courant mis à jour, ancien archivé.

    Rien n'est écrit si une ligne est invalide (quantité ou prix ≤ 0,
    ingrédient disparu entre la saisie et la validation — TC-F1-03, TC-F1-05).
    """
    if not lines:
        raise DeliveryError("Ajoutez au moins une ligne à la réception.")

    settings = settings_service.get_settings(db)
    alert_pct = settings.price_alert_pct

    # Validation complète avant toute écriture.
    prepared: list[tuple[models.Ingredient, DeliveryLineInput]] = []
    for line in lines:
        ingredient = db.get(models.Ingredient, line.ingredient_id)
        if ingredient is None:
            raise DeliveryError(
                "Un ingrédient de la réception n'existe plus (supprimé entre la saisie "
                "et la validation). Rechargez la page et ressaisissez la ligne concernée."
            )
        if line.quantity <= 0:
            raise DeliveryError(f"Quantité invalide pour « {ingredient.name} » : elle doit être supérieure à 0.")
        if line.unit_price <= 0:
            raise DeliveryError(f"Prix invalide pour « {ingredient.name} » : il doit être supérieur à 0.")
        prepared.append((ingredient, line))

    receipt = models.DeliveryReceipt(
        received_on=received_on,
        supplier=(supplier or "").strip() or None,
        note=(note or "").strip() or None,
        photo_path=photo_path,
    )
    db.add(receipt)
    db.flush()

    result = DeliveryResult(receipt=receipt)
    for ingredient, line in prepared:
        previous_price = ingredient.unit_cost

        stock.record_movement(
            db, ingredient, models.MovementType.RECEPTION, line.quantity,
            reference=f"réception#{receipt.id}",
        )

        db.add(models.DeliveryLine(
            receipt_id=receipt.id,
            ingredient_id=ingredient.id,
            quantity=line.quantity,
            unit_price=line.unit_price,
            previous_unit_price=previous_price or None,
        ))

        # Le prix courant devient le prix d'achat ; l'ancien est archivé avec sa date.
        # Le prix initial (saisi à la création de l'ingrédient) était forcément en
        # vigueur avant cette réception : on l'horodate au plus tard à sa date,
        # sinon une réception antidatée le ferait passer après dans l'historique.
        if previous_price and not _has_history(db, ingredient.id):
            db.add(models.PriceHistory(
                ingredient_id=ingredient.id, unit_price=previous_price,
                recorded_at=min(ingredient.created_at, received_on), supplier=None,
            ))
        ingredient.unit_cost = line.unit_price
        db.add(models.PriceHistory(
            ingredient_id=ingredient.id, unit_price=line.unit_price,
            recorded_at=received_on, supplier=receipt.supplier, receipt_id=receipt.id,
        ))

        if previous_price:
            change_pct = (line.unit_price - previous_price) / previous_price * 100
            if abs(change_pct) > alert_pct:
                result.price_alerts.append(
                    f"Prix {ingredient.name} {change_pct:+.0f} % vs dernière livraison"
                    .replace(".", ",")
                )

    last_count = _last_completed_count(db)
    if last_count is not None and received_on < last_count.ended_at:
        result.backdated_warning = (
            f"Réception antérieure au comptage du {last_count.ended_at:%d/%m/%Y} : "
            "le stock théorique de ce comptage ne sera pas recalculé rétroactivement."
        )

    db.commit()
    db.refresh(receipt)
    return result


def _has_history(db: Session, ingredient_id: int) -> bool:
    return (
        db.query(models.PriceHistory)
        .filter(models.PriceHistory.ingredient_id == ingredient_id)
        .first()
        is not None
    )
