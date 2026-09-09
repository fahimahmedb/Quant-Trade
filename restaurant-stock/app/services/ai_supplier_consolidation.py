"""F16 — consolidation de commande par fournisseur (Lot IA-1,
docs/feature-plans/ia-f10-f19.md §7). Regroupe les suggestions F7
(app/services/ai_ordering.py) par fournisseur, avec le total de commande
et l'écart au franco de port.

Gate : aucun — « purement combinatoire », dit le document lui-même.
Zéro saisie obligatoire : un ingrédient sans fournisseur renseigné va
dans le groupe « non attribué » (AC-F16-1), jamais une erreur.

Simplification documentée : le document liste « franco de port » et
« minimum de commande » comme deux données distinctes, mais son propre
plan de test (AC/TC) n'exerce que le franco — traité ici comme un seul
seuil (`Ingredient.supplier_free_shipping_threshold`), pas deux concepts
parallèles dont l'un resterait entièrement non testé.

Jamais de sur-commande automatique (principe 2 des specs V2) : la
proposition d'atteindre le franco reste une SUGGESTION distincte, jamais
fusionnée dans la quantité déjà retenue par F7, et chaque ligne proposée
respecte encore le plafond péremption de F7 — recalculé ici comme
`shelf_life_days * consommation_quotidienne - stock_actuel` (la même
borne que F7 applique à sa propre suggestion), sur la moyenne glissante
v1 plutôt que la prévision F6 : F16 pose une question secondaire
(« combien pourrais-je ajouter sans gâcher ? »), pas une nouvelle
prévision — réutiliser l'estimateur déjà disponible partout ailleurs
plutôt qu'en calculer un second n'change rien à l'ordre de grandeur du
plafond de péremption, qui est ce qui compte ici (AC-F16-2).

Aucun envoi automatique dans aucun chemin de code (AC-F16-3) : cette
fonction produit un texte exportable, jamais un appel réseau.
"""
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import ai_ordering, ordering, settings_service
from app.templating import nom_du_jour

UNATTRIBUTED_SUPPLIER = "Non attribué"


@dataclass
class SupplierOrderLine:
    ingredient_id: int
    ingredient_name: str
    quantity: float
    unit_cost: float
    subtotal: float
    target_delivery: datetime | None


@dataclass
class ProposedAddition:
    ingredient_id: int
    ingredient_name: str
    max_addable_quantity: float
    max_addable_value: float


@dataclass
class SupplierGroup:
    supplier_name: str
    lines: list[SupplierOrderLine]
    total: float
    threshold: float | None
    under_threshold: bool
    shortfall: float | None
    proposed_additions: list[ProposedAddition] = field(default_factory=list)
    can_reach_threshold: bool = True
    message: str = ""
    export_text: str = ""


@dataclass
class ConsolidationResult:
    ok: bool
    message: str | None
    groups: list[SupplierGroup] = field(default_factory=list)


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f16_enabled


def _daily_consumption(db: Session, ingredient_id: int, today: datetime) -> float:
    """Moyenne glissante v1 — voir docstring de tête pour la justification
    de ne pas réutiliser F6 ici."""
    window_days = settings_service.get_settings(db).rolling_window_days
    return ordering.rolling_avg_daily_consumption(db, ingredient_id, window_days, as_of=today)


def _max_addable_now(ingredient: models.Ingredient, daily_consumption: float) -> float:
    """Même plafond que F7 (`ai_ordering.plan_order_cycle`) : la quantité
    totale sur étagère (stock actuel + ajout) ne doit jamais dépasser ce
    qui peut être consommé dans la fenêtre de conservation."""
    if not ingredient.shelf_life_days or daily_consumption <= 0:
        return 0.0
    ceiling = ingredient.shelf_life_days * daily_consumption
    return max(0.0, ceiling - ingredient.current_theoretical_stock)


def _export_text(supplier_name: str, lines: list[SupplierOrderLine], total: float) -> str:
    rows = "\n".join(f"- {l.ingredient_name} : {l.quantity:g}" for l in lines)
    return f"Commande {supplier_name}\n{rows}\nTotal : {total:.2f} €"


def consolidate_orders(
    db: Session, *, today: datetime | None = None, order_cutoff_passed: bool = False,
) -> ConsolidationResult:
    """docs/feature-plans/ia-f10-f19.md §7."""
    if not _feature_enabled(db):
        return ConsolidationResult(ok=False, message="Fonctionnalité F16 désactivée (feature flag éteint).")

    today = today or datetime.utcnow()
    ingredients = db.query(models.Ingredient).filter_by(is_active=True).all()

    by_supplier: dict[str, list[SupplierOrderLine]] = {}
    thresholds: dict[str, float] = {}
    in_order_ids: set[int] = set()

    for ing in ingredients:
        result = ai_ordering.plan_order_cycle_for_ingredient(
            db, ing.id, today=today, order_cutoff_passed=order_cutoff_passed,
        )
        if not result.ok or not result.suggested_quantity or result.suggested_quantity <= 0:
            continue
        in_order_ids.add(ing.id)
        supplier = ing.supplier_name or UNATTRIBUTED_SUPPLIER
        subtotal = result.suggested_quantity * ing.unit_cost
        by_supplier.setdefault(supplier, []).append(SupplierOrderLine(
            ingredient_id=ing.id, ingredient_name=ing.name, quantity=result.suggested_quantity,
            unit_cost=ing.unit_cost, subtotal=subtotal, target_delivery=result.target_delivery,
        ))
        if ing.supplier_free_shipping_threshold is not None:
            thresholds[supplier] = max(thresholds.get(supplier, 0.0), ing.supplier_free_shipping_threshold)

    if not by_supplier:
        return ConsolidationResult(ok=True, message=None, groups=[])

    groups: list[SupplierGroup] = []
    for supplier, lines in by_supplier.items():
        total = sum(l.subtotal for l in lines)
        threshold = thresholds.get(supplier)
        under = threshold is not None and total < threshold

        proposed_additions: list[ProposedAddition] = []
        can_reach = True
        shortfall = None
        message = _export_text(supplier, lines, total)

        if under:
            shortfall = threshold - total
            candidats = (
                db.query(models.Ingredient)
                .filter(
                    models.Ingredient.is_active.is_(True),
                    models.Ingredient.supplier_name == (None if supplier == UNATTRIBUTED_SUPPLIER else supplier),
                    ~models.Ingredient.id.in_(in_order_ids),
                )
                .all()
            )
            for candidat in candidats:
                consommation = _daily_consumption(db, candidat.id, today)
                addable_qty = _max_addable_now(candidat, consommation)
                if addable_qty > 0:
                    proposed_additions.append(ProposedAddition(
                        ingredient_id=candidat.id, ingredient_name=candidat.name,
                        max_addable_quantity=addable_qty,
                        max_addable_value=addable_qty * candidat.unit_cost,
                    ))

            addable_total = sum(a.max_addable_value for a in proposed_additions)
            can_reach = addable_total >= shortfall

            if can_reach:
                message = (
                    f"{total:.2f} € sur {threshold:.2f} € de franco. "
                    f"Ajouter {shortfall:.2f} € ou reporter ?"
                )
            else:
                prochaine_livraison = min(
                    (l.target_delivery for l in lines if l.target_delivery is not None), default=None,
                )
                report = (
                    f" au {nom_du_jour(prochaine_livraison)} {prochaine_livraison:%d/%m}"
                    if prochaine_livraison else ""
                )
                message = (
                    f"{total:.2f} € sur {threshold:.2f} € de franco, mais aucun ajout supplémentaire "
                    f"ne peut respecter la conservation sans gaspillage. Impossible d'atteindre le franco "
                    f"sans risquer la péremption — report de la commande recommandé{report}."
                )

        groups.append(SupplierGroup(
            supplier_name=supplier, lines=lines, total=total, threshold=threshold,
            under_threshold=under, shortfall=shortfall, proposed_additions=proposed_additions,
            can_reach_threshold=can_reach, message=message,
            export_text=_export_text(supplier, lines, total),
        ))

    return ConsolidationResult(ok=True, message=None, groups=groups)
