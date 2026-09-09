"""F12 — alerte de marge érodée ⭐ (Lot IA-1, docs/feature-plans/
ia-f10-f19.md §3, cible SYN-L). Détecte qu'un plat a perdu en rentabilité
parce que ses ingrédients ont augmenté, avant que la marge ne soit
mangée en silence — l'écart le plus silencieux et le plus coûteux du
métier, dit le document.

Prérequis signalé par le document comme non levé : « prix de vente saisi
sur la fiche plat (U7 du plan UX, non encore fait) ». Décision actée
(backlog-lot-ia-1 §4 ticket 3) : construire la logique quand même, en
amont de l'écran — la fonctionnalité reste inerte tant qu'aucun prix
n'est disponible (principe §2 règle 2). Faute d'un champ dédié sur
`Dish`, le « prix de vente » est lu sur une donnée déjà disponible :
le `unit_price` le plus récent parmi les ventes importées de ce plat
(`SaleLine.unit_price`, alimenté par tout CSV qui porte la colonne prix)
— pas un nouveau champ qui dupliquerait une donnée déjà présente dans le
flux existant. Un plat sans aucune vente valorisée est exclu, avec
mention (AC-F12-2).

Gate : >= 2 relevés de prix (`PriceHistory`) sur AU MOINS UN ingrédient
du plat — sans historique de prix, aucune hausse n'est démontrable.

Coût matière historique : reconstruit ingrédient par ingrédient à partir
de `PriceHistory`, qui journalise CHAQUE prix qui a été en vigueur (pas
seulement les prix dépassés — la ligne la plus récente y correspond
exactement au prix courant de l'ingrédient, ajoutée au même moment que
`Ingredient.unit_cost` est mis à jour, cf. `deliveries.record_delivery`).
Le prix en vigueur à une date donnée est donc le dernier relevé
antérieur ou égal à cette date ; à défaut d'un relevé assez ancien
(l'ingrédient n'a jamais eu de changement de prix connu avant cette
date), le prix ACTUEL sert de repli — aucune hausse n'est supposée avant
le premier relevé connu, jamais devinée.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service

COMPARISON_WINDOW_DAYS = 90  # ia-f10-f19.md §3 : « baissé de plus de 10% sur 90 jours »
MIN_PRICE_RECORDS = 2


@dataclass
class IngredientImpact:
    ingredient_id: int
    ingredient_name: str
    price_then: float
    price_now: float
    cost_impact: float  # (price_now - price_then) * grammage, positif = a renchéri le plat


@dataclass
class MarginAssessment:
    ok: bool
    message: str | None
    dish_id: int | None = None
    dish_name: str | None = None
    sale_price: float | None = None
    food_cost_now: float | None = None
    food_cost_then: float | None = None
    coefficient_now: float | None = None
    coefficient_then: float | None = None
    is_alert: bool = False
    below_threshold: bool = False
    dropped_over_window: bool = False
    impacts: list[IngredientImpact] = field(default_factory=list)
    suggested_price: float | None = None
    explanation: str = ""


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f12_enabled


def _current_sale_price(db: Session, dish_id: int) -> float | None:
    line = (
        db.query(models.SaleLine)
        .filter(models.SaleLine.dish_id == dish_id, models.SaleLine.unit_price.isnot(None))
        .order_by(models.SaleLine.sale_date.desc())
        .first()
    )
    return line.unit_price if line else None


def _price_at(db: Session, ingredient_id: int, at: datetime) -> float:
    record = (
        db.query(models.PriceHistory)
        .filter(models.PriceHistory.ingredient_id == ingredient_id, models.PriceHistory.recorded_at <= at)
        .order_by(models.PriceHistory.recorded_at.desc())
        .first()
    )
    if record is not None:
        return record.unit_price
    ingredient = db.get(models.Ingredient, ingredient_id)
    return ingredient.unit_cost


def _price_record_count(db: Session, ingredient_id: int) -> int:
    return db.query(models.PriceHistory).filter_by(ingredient_id=ingredient_id).count()


def assess_margin(db: Session, dish_id: int, *, as_of: datetime | None = None) -> MarginAssessment:
    """docs/feature-plans/ia-f10-f19.md §3 (SYN-L)."""
    if not _feature_enabled(db):
        return MarginAssessment(ok=False, message="Fonctionnalité F12 désactivée (feature flag éteint).")

    dish = db.get(models.Dish, dish_id)
    if dish is None:
        return MarginAssessment(ok=False, message="Plat introuvable.")

    sale_price = _current_sale_price(db, dish_id)
    if sale_price is None or sale_price <= 0:
        return MarginAssessment(
            ok=False, message="Aucun prix de vente connu pour ce plat : F12 reste inactif.",
            dish_id=dish_id, dish_name=dish.name,
        )

    recipe_lines = dish.recipe_lines
    if not recipe_lines:
        return MarginAssessment(ok=False, message="Ce plat n'a pas de fiche technique.", dish_id=dish_id, dish_name=dish.name)

    if not any(_price_record_count(db, rl.ingredient_id) >= MIN_PRICE_RECORDS for rl in recipe_lines):
        return MarginAssessment(
            ok=False,
            message=f"Moins de {MIN_PRICE_RECORDS} relevés de prix sur les ingrédients de ce plat : F12 reste inactif.",
            dish_id=dish_id, dish_name=dish.name,
        )

    as_of = as_of or datetime.utcnow()
    window_start = as_of - timedelta(days=COMPARISON_WINDOW_DAYS)

    food_cost_now = dish.food_cost
    food_cost_then = 0.0
    impacts: list[IngredientImpact] = []
    for rl in recipe_lines:
        price_now = rl.ingredient.unit_cost
        price_then = _price_at(db, rl.ingredient_id, window_start)
        food_cost_then += rl.quantity * price_then
        impacts.append(IngredientImpact(
            ingredient_id=rl.ingredient_id, ingredient_name=rl.ingredient.name,
            price_then=price_then, price_now=price_now,
            cost_impact=(price_now - price_then) * rl.quantity,
        ))
    impacts.sort(key=lambda i: i.cost_impact, reverse=True)

    settings = settings_service.get_settings(db)
    coefficient_now = sale_price / food_cost_now if food_cost_now > 0 else float("inf")
    coefficient_then = sale_price / food_cost_then if food_cost_then > 0 else float("inf")

    below_threshold = coefficient_now < settings.margin_coefficient_threshold
    drop_pct = (
        (coefficient_then - coefficient_now) / coefficient_then * 100.0
        if coefficient_then > 0 else 0.0
    )
    dropped_over_window = drop_pct > settings.margin_drop_pct_threshold
    is_alert = below_threshold or dropped_over_window

    # AC-F12-4 : le prix suggéré restaure le coefficient d'ORIGINE (celui
    # d'il y a COMPARISON_WINDOW_DAYS, avant la hausse), appliqué au coût
    # matière ACTUEL — pas le seuil réglable, qui est un déclencheur
    # d'alerte, pas un objectif commercial.
    suggested_price = coefficient_then * food_cost_now if coefficient_then not in (0, float("inf")) else None

    if is_alert:
        variation_pct = (food_cost_now - food_cost_then) / food_cost_then * 100.0 if food_cost_then > 0 else 0.0
        principal = impacts[0] if impacts else None
        detail_principal = (
            f", dont {principal.ingredient_name} {'+' if principal.cost_impact >= 0 else ''}{principal.cost_impact:.2f} €"
            if principal is not None and abs(principal.cost_impact) >= 0.005 else ""
        )
        explanation = (
            f"{dish.name} — coût matière passé de {food_cost_then:.2f} € à {food_cost_now:.2f} € "
            f"en {COMPARISON_WINDOW_DAYS // 30} mois ({'+' if variation_pct >= 0 else ''}{variation_pct:.0f} %)"
            f"{detail_principal}. Coefficient tombé de {coefficient_then:.1f} à {coefficient_now:.1f}."
        )
    else:
        explanation = f"{dish.name} : coefficient stable à {coefficient_now:.1f}, aucune alerte."

    return MarginAssessment(
        ok=True, message=None, dish_id=dish_id, dish_name=dish.name, sale_price=sale_price,
        food_cost_now=food_cost_now, food_cost_then=food_cost_then,
        coefficient_now=coefficient_now, coefficient_then=coefficient_then,
        is_alert=is_alert, below_threshold=below_threshold, dropped_over_window=dropped_over_window,
        impacts=impacts, suggested_price=suggested_price, explanation=explanation,
    )


def ingredient_price_impact(db: Session, ingredient_id: int, *, as_of: datetime | None = None) -> list[MarginAssessment]:
    """« Vue impact d'un ingrédient » : quand un prix bouge, la liste des
    plats touchés et de combien — un `assess_margin` par plat concerné,
    jamais un calcul séparé qui pourrait diverger du diagnostic par plat."""
    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    return [assess_margin(db, rl.dish_id, as_of=as_of) for rl in recipe_lines]
