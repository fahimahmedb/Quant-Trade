"""Suggestion de commande — logique simple à seuil (section 4.6).

Volontairement naïf (pas d'IA prédictive) : une moyenne glissante sur N
jours sert à la fois à détecter qu'un ingrédient passe sous son seuil et à
dimensionner la quantité suggérée. Tout est visible et modifiable par le
gérant avant validation — jamais d'envoi automatique de commande.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service


def rolling_avg_daily_consumption(
    db: Session, ingredient_id: int, window_days: int, as_of: datetime | None = None
) -> float:
    if window_days <= 0:
        return 0.0
    as_of = as_of or datetime.utcnow()
    since = as_of - timedelta(days=window_days)
    movements = (
        db.query(models.StockMovement)
        .filter(
            models.StockMovement.ingredient_id == ingredient_id,
            models.StockMovement.movement_type == models.MovementType.VENTE,
            models.StockMovement.created_at >= since,
        )
        .all()
    )
    total_consumed = sum(-m.quantity_delta for m in movements)  # delta négatif = consommation
    return max(total_consumed, 0.0) / window_days


def _suggestion_values(
    db: Session, ingredient: models.Ingredient, settings: models.Settings
) -> tuple[float, float, float]:
    """(conso. moyenne/jour, seuil, quantité suggérée) pour CET ingrédient,
    à l'instant présent. Suggested_quantity vaut 0 si le stock actuel est
    déjà au-dessus du seuil — factorisé pour rester identique entre la
    génération d'un lot et le rafraîchissement d'une ligne isolée."""
    avg_daily = rolling_avg_daily_consumption(db, ingredient.id, settings.rolling_window_days)
    threshold = (
        ingredient.alert_threshold
        if ingredient.alert_threshold is not None
        else avg_daily * settings.safety_days
    )
    if ingredient.current_theoretical_stock >= threshold:
        return avg_daily, threshold, 0.0
    # Cible = au moins le seuil lui-même, davantage si la conso récente le justifie.
    target_stock = max(avg_daily * settings.target_days, threshold)
    suggested_quantity = max(target_stock - ingredient.current_theoretical_stock, 0.0)
    return avg_daily, threshold, suggested_quantity


def generate_suggestions(db: Session) -> models.OrderSuggestionBatch:
    settings = settings_service.get_settings(db)
    batch = models.OrderSuggestionBatch()
    db.add(batch)
    db.flush()

    ingredients = (
        db.query(models.Ingredient).filter(models.Ingredient.is_active.is_(True)).all()
    )
    for ingredient in ingredients:
        avg_daily, threshold, suggested_quantity = _suggestion_values(db, ingredient, settings)
        if suggested_quantity <= 0:
            continue

        db.add(
            models.OrderSuggestionLine(
                batch_id=batch.id,
                ingredient_id=ingredient.id,
                current_stock=ingredient.current_theoretical_stock,
                avg_daily_consumption=avg_daily,
                threshold_used=threshold,
                suggested_quantity=suggested_quantity,
            )
        )

    db.commit()
    db.refresh(batch)
    return batch


def refresh_pending_line(db: Session, line: models.OrderSuggestionLine) -> models.OrderSuggestionLine:
    """Une ligne encore en attente doit refléter le stock ACTUEL de son
    ingrédient, pas celui du moment où le lot a été généré : un comptage
    terminé depuis (recalage du stock théorique, section 3.4) change la
    conclusion — à la baisse (le manque est pire que suggéré) comme à la
    hausse (le manque a disparu). Rien ne prévenait de cet écart avant que
    quelqu'un pense à cliquer sur « Régénérer avec les données actuelles ».
    N'affecte jamais une ligne déjà décidée : une décision validée est un
    fait historique, pas une suggestion à corriger après coup."""
    if line.decision != models.SuggestionDecision.EN_ATTENTE:
        return line
    settings = settings_service.get_settings(db)
    avg_daily, threshold, suggested_quantity = _suggestion_values(db, line.ingredient, settings)
    line.current_stock = line.ingredient.current_theoretical_stock
    line.avg_daily_consumption = avg_daily
    line.threshold_used = threshold
    line.suggested_quantity = suggested_quantity
    db.commit()
    db.refresh(line)
    return line


def decide_suggestion_line(
    db: Session,
    line_id: int,
    final_quantity: float,
    decision: models.SuggestionDecision,
) -> models.OrderSuggestionLine:
    line = db.get(models.OrderSuggestionLine, line_id)
    if line is None:
        raise ValueError(f"Ligne de suggestion introuvable : {line_id}")
    line.final_quantity = final_quantity
    line.decision = decision
    line.validated_at = datetime.utcnow()
    db.commit()
    db.refresh(line)
    return line
