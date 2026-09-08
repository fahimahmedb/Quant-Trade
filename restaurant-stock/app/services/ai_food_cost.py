"""F9 — food cost théorique vs réel sur une période (Lot IA-0,
docs/feature-plans/ia-f5-f9.md §1.9, cible SYN-H).

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
import statistics
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service

QUADRANT_LABELS = {
    "stars": "stars",
    "a_retravailler": "à retravailler",
    "a_pousser": "à pousser",
    "a_questionner": "à questionner",
}


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
    """docs/feature-plans/ia-f5-f9.md §1.9 (SYN-H) : théorique et réel, sur [start, end]."""
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


@dataclass
class MatrixEntry:
    dish_id: int
    dish_name: str
    quantity_sold: float
    popularity: float  # part des ventes en volume, sur les plats retenus
    unit_price: float  # prix de vente moyen réellement constaté sur la période
    unit_cost: float  # coût matière de la fiche technique, au prix courant
    unit_margin: float
    total_margin: float
    quadrant: str
    label: str
    explanation: str


@dataclass
class MatrixResult:
    ok: bool
    message: str | None
    entries: list[MatrixEntry] = field(default_factory=list)
    excluded_without_price: list[str] = field(default_factory=list)
    popularity_threshold: float | None = None
    margin_threshold: float | None = None


def popularity_margin_matrix(db: Session, start: datetime, end: datetime) -> MatrixResult:
    """specs-v2-ia-plan-test.md §4 (F9) : « matrice par plat : popularité
    (part des ventes) × marge brute unitaire, 4 quadrants nommés en clair
    ("stars", "à retravailler", "à pousser", "à questionner"), avec le
    chiffre derrière chaque position ».

    « Pas de recommandation de carte automatique — un éclairage, pas une
    décision » : cette fonction classe et chiffre, elle ne conseille jamais
    de retirer un plat.

    Les deux axes sont séparés par la MÉDIANE des plats de la période, pas
    par une constante : un seuil absolu de marge n'a aucun sens commun entre
    une pizzeria et un bistrot, et la médiane résiste à un plat d'appel très
    vendu qui écraserait une moyenne. Conséquence assumée : la matrice est
    toujours relative à la carte du moment — la moitié des plats est
    forcément « sous la médiane », ce qui n'est pas un jugement de valeur
    absolu et doit être lu comme tel.
    """
    if not _feature_enabled(db):
        return MatrixResult(ok=False, message="Fonctionnalité F9 désactivée (feature flag éteint).")

    sales = (
        db.query(models.SaleLine)
        .filter(models.SaleLine.sale_date >= start, models.SaleLine.sale_date <= end)
        .all()
    )
    par_plat: dict[int, list[models.SaleLine]] = {}
    for sale in sales:
        if sale.dish is not None:
            par_plat.setdefault(sale.dish_id, []).append(sale)
    if not par_plat:
        return MatrixResult(ok=False, message="Aucune vente sur cette période.")

    retenus: list[tuple[models.Dish, float, float]] = []  # (plat, qté, CA)
    exclus: list[str] = []
    for dish_id, lignes in par_plat.items():
        dish = lignes[0].dish
        qty = sum(l.quantity_sold for l in lignes)
        revenue = sum(l.quantity_sold * l.unit_price for l in lignes if l.unit_price)
        # TC-F9-06 : un plat vendu 0 fois n'a pas de position sur la matrice.
        if qty <= 0:
            continue
        # AC-F9-3 : sans prix de vente, la marge est inconnue — le plat est
        # écarté AVEC mention, jamais compté à marge nulle (ce qui le
        # rangerait faussement en « à questionner »).
        if revenue <= 0:
            exclus.append(dish.name)
            continue
        retenus.append((dish, qty, revenue))

    if not retenus:
        return MatrixResult(
            ok=False, message="Aucun plat avec un prix de vente sur cette période.",
            excluded_without_price=sorted(exclus),
        )

    total_qty = sum(qty for _, qty, _ in retenus)
    mesures = []
    for dish, qty, revenue in retenus:
        prix_moyen = revenue / qty
        cout = dish.food_cost
        mesures.append((dish, qty, qty / total_qty, prix_moyen, cout, prix_moyen - cout))

    seuil_popularite = statistics.median([m[2] for m in mesures])
    seuil_marge = statistics.median([m[5] for m in mesures])

    entries: list[MatrixEntry] = []
    for dish, qty, popularite, prix_moyen, cout, marge in mesures:
        populaire = popularite >= seuil_popularite
        rentable = marge >= seuil_marge
        if populaire and rentable:
            quadrant = "stars"
        elif populaire:
            quadrant = "a_retravailler"
        elif rentable:
            quadrant = "a_pousser"
        else:
            quadrant = "a_questionner"
        entries.append(MatrixEntry(
            dish_id=dish.id, dish_name=dish.name, quantity_sold=qty, popularity=popularite,
            unit_price=prix_moyen, unit_cost=cout, unit_margin=marge, total_margin=marge * qty,
            quadrant=quadrant, label=QUADRANT_LABELS[quadrant],
            explanation=(
                f"{popularite * 100:.1f} % des ventes ({qty:g} vendus), marge brute "
                f"{marge:.2f} € par plat ({prix_moyen:.2f} € − {cout:.2f} € de matière), "
                f"soit {marge * qty:.2f} € sur la période"
            ),
        ))
    entries.sort(key=lambda e: e.total_margin, reverse=True)
    return MatrixResult(
        ok=True, message=None, entries=entries, excluded_without_price=sorted(exclus),
        popularity_threshold=seuil_popularite, margin_threshold=seuil_marge,
    )
