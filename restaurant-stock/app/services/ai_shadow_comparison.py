"""Écran de comparaison en mode ombre (avancement-lot-ia-0-trois-decisions
§1 / backlog-lot-ia-1.md §1 : « à construire, après F6 déjà en place »,
et §6, critère de sortie du Lot IA-1). Expose `ai_forecast.backtest_vs_v1`
(Lot IA-0, IA-01) par ingrédient actif — l'écran l'expose, il n'invente
rien de nouveau, aucun second calcul qui pourrait diverger du gate réel
d'activation de F6.

Réservé à l'équipe projet, jamais au restaurateur (backlog §6) : voir
`app/routers/admin.py` pour la protection par jeton, distincte de la
session établissement.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app import models
from app.services import ai_forecast


@dataclass
class IngredientComparison:
    ingredient_id: int
    ingredient_name: str
    result: ai_forecast.BacktestResult
    currently_reverted_to_v1: bool  # F18 : bascule runtime déjà appliquée pour cet ingrédient


def shadow_mode_comparison(db: Session) -> list[IngredientComparison]:
    """Un `backtest_vs_v1` par ingrédient actif, triés par nom — la vue
    d'ensemble que l'équipe projet utilise pour juger, ingrédient par
    ingrédient, si F6 est prêt à être activé pour de vrai (IA-01/IA-05)."""
    ingredients = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.is_active.is_(True))
        .order_by(models.Ingredient.name)
        .all()
    )
    return [
        IngredientComparison(
            ingredient_id=ing.id, ingredient_name=ing.name,
            result=ai_forecast.backtest_vs_v1(db, ing.id),
            currently_reverted_to_v1=ing.f6_reverted_to_v1,
        )
        for ing in ingredients
    ]
