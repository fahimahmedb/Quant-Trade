"""F24 — comparaison de prix multi-fournisseurs (backlog-lot-ia-2.md §5,
point bloquant 2 — débloqué a posteriori sur demande explicite du porteur
du projet ; voir §5 « Résolution » du backlog et docs/bilan-ia-2.md §7
pour le détail de la décision).

La question qui bloquait ce ticket (« combien de fournisseurs
alternatifs par ingrédient en pratique ? », supposée déterminer si un
champ optionnel suffit ou si une table dédiée est nécessaire) ne se pose
en réalité pas : `PriceHistory` (F1, Lot V1.1) enregistre déjà, à CHAQUE
réception, le fournisseur de cette ligne précise (`PriceHistory.supplier`,
alimenté par `deliveries.record_delivery`) — la donnée existe déjà pour 1
comme pour 10 fournisseurs par ingrédient, sans migration ni nouveau
champ. Ce module n'est qu'une agrégation EN LECTURE sur des données déjà
écrites, exactement le même geste que F16 (consolidation) ou F9 (food
cost) sur les leurs.

Regroupement par égalité STRICTE de chaîne sur `PriceHistory.supplier` —
F16 fait de même sur `Ingredient.supplier_name` (aucune normalisation ou
rapprochement flou nulle part dans ce projet) : deux libellés différents
pour un même fournisseur réel restent deux groupes distincts, une limite
connue et acceptée, pas un bug de F24.

Dernier prix connu PAR FOURNISSEUR (jamais le prix le plus bas jamais vu,
qui pourrait être une promotion ponctuelle périmée), sans seuil de
péremption du prix : `Ingredient.unit_cost` lui-même n'en a jamais eu
(`deliveries.record_delivery` l'écrase à chaque réception, quelle que
soit son ancienneté) — ce module ne s'invente pas une fraîcheur que rien
d'autre dans le projet ne vérifie déjà.

Purement consultatif (même principe que F16, « jamais de sur-commande
automatique ») : ne modifie jamais `Ingredient.supplier_name` tout seul —
signale un fournisseur moins cher que le prix actuel, la bascule reste
une décision humaine.
"""
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service

MIN_SUPPLIERS_TO_COMPARE = 2  # rien à comparer avec un seul fournisseur connu


@dataclass
class SupplierPrice:
    supplier: str
    unit_price: float
    recorded_at: datetime
    is_current: bool  # == Ingredient.supplier_name au moment de l'appel


@dataclass
class IngredientComparison:
    ingredient_id: int
    ingredient_name: str
    prices: list[SupplierPrice]  # trié du moins cher au plus cher
    best_supplier: str
    best_price: float
    current_price: float  # Ingredient.unit_cost
    potential_saving_pct: float | None  # None si rien à gagner (déjà au meilleur prix)


@dataclass
class ComparisonResult:
    ok: bool
    message: str | None
    comparisons: list[IngredientComparison] = field(default_factory=list)


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f24_enabled


def _latest_price_by_supplier(db: Session, ingredient_id: int) -> dict[str, models.PriceHistory]:
    rows = (
        db.query(models.PriceHistory)
        .filter(
            models.PriceHistory.ingredient_id == ingredient_id,
            models.PriceHistory.supplier.isnot(None),
            models.PriceHistory.supplier != "",
        )
        .order_by(models.PriceHistory.recorded_at.asc(), models.PriceHistory.id.asc())
        .all()
    )
    latest: dict[str, models.PriceHistory] = {}
    for row in rows:
        latest[row.supplier] = row  # tri croissant : la dernière affectation gagne
    return latest


def compare_suppliers(db: Session) -> ComparisonResult:
    """backlog-lot-ia-2.md §5, point bloquant 2 (résolu)."""
    if not _feature_enabled(db):
        return ComparisonResult(ok=False, message="Fonctionnalité F24 désactivée (feature flag éteint).")

    ingredients = db.query(models.Ingredient).filter_by(is_active=True).all()
    comparisons: list[IngredientComparison] = []

    for ing in ingredients:
        latest_by_supplier = _latest_price_by_supplier(db, ing.id)
        if len(latest_by_supplier) < MIN_SUPPLIERS_TO_COMPARE:
            continue

        prices = sorted(
            (
                SupplierPrice(
                    supplier=supplier, unit_price=row.unit_price, recorded_at=row.recorded_at,
                    is_current=(supplier == ing.supplier_name),
                )
                for supplier, row in latest_by_supplier.items()
            ),
            key=lambda p: p.unit_price,
        )
        best = prices[0]
        saving_pct = None
        if ing.unit_cost > 0 and best.unit_price < ing.unit_cost:
            saving_pct = (ing.unit_cost - best.unit_price) / ing.unit_cost * 100

        comparisons.append(IngredientComparison(
            ingredient_id=ing.id, ingredient_name=ing.name, prices=prices,
            best_supplier=best.supplier, best_price=best.unit_price,
            current_price=ing.unit_cost, potential_saving_pct=saving_pct,
        ))

    return ComparisonResult(ok=True, message=None, comparisons=comparisons)
