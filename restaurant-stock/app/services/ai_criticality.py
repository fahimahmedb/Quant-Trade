"""F10 — classification de criticité des ingrédients (classement ABC de
Pareto), Lot IA-1 (docs/feature-plans/ia-f10-f19.md §1, jeu SYN-J).

Socle de F11 (comptage tournant, pas construit dans ce lot) : détermine
quels ingrédients méritent le plus d'attention, sans jamais imposer de
comptage supplémentaire — c'est une lecture, pas une action.

Gate : ≥ 4 semaines de ventes PAR INGRÉDIENT, aucun comptage requis. Sous
ce seuil, un ingrédient est classé « non déterminé » (`computed_class`
`None`), jamais « C » par défaut (AC-F10-2) : une valeur non mesurée n'est
pas une valeur faible.

Rejeu du passé : `classify_ingredients` prend un paramètre `as_of`,
comme `ai_forecast.weekday_forecast` — leçon du Lot IA-0 (backlog-lot-ia-1
§3) appliquée par défaut ici aussi, pas seulement là où elle a été trouvée
la première fois.

Point volontairement non construit — à trancher, pas à deviner
(backlog-lot-ia-1 §2 règle 3, question de jugement métier) : le document
demande qu'« un ingrédient de classe B très volatil remonte en A », mais
ne fixe aucun seuil de coefficient de variation à partir duquel un
ingrédient est « très volatil ». Décider ce chiffre changerait en silence
ce qu'un restaurateur voit comme prioritaire — ce n'est pas une question
technique. Le coefficient de variation est calculé et exposé
(`IngredientCriticality.volatility`) pour tout ingrédient avec ≥ 3
comptages ; il n'est PAS utilisé pour reclasser automatiquement tant que
ce seuil n'est pas fixé. Voir le rapport de sortie du lot.

Le seul point de jugement effectivement tranché par le backlog — l'ex-æquo
entre deux ingrédients de même valeur annuelle au bord d'une classe : le
plus volatil des deux monte dans la classe supérieure — EST appliqué, sous
la forme d'une clé de tri secondaire plutôt qu'un cas particulier codé à
la main.
"""
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service
from app.templating import pluriel

MIN_WEEKS_OF_SALES = 4.0  # ia-f10-f19.md §1 : « Gate : >= 4 semaines de ventes »
DORMANT_WINDOW_DAYS = 21  # TC-F10-02 : « consommation nulle depuis 3 semaines »
CLASS_A_CUM_PCT = 0.80  # « classe A = les ingrédients cumulant 80% de la valeur »
CLASS_B_CUM_PCT = 0.95  # « classe B = les 15% suivants » -> cumul 80+15 = 95%
VALID_OVERRIDES = {"A", "B", "C"}


@dataclass
class IngredientCriticality:
    ingredient_id: int
    ingredient_name: str
    weeks_of_sales: float
    annual_value: float | None  # None si historique insuffisant (AC-F10-2)
    volatility: float | None  # coefficient de variation des écarts, None si < 3 comptages
    computed_class: str | None  # "A" | "B" | "C" | "dormant" | None (non déterminé)
    manual_override: str | None
    effective_class: str | None  # override sinon computed_class (AC-F10-3)
    explanation: str


@dataclass
class CriticalityResult:
    ok: bool
    message: str | None
    items: list[IngredientCriticality] = field(default_factory=list)
    summary: str | None = None  # jamais "A/B/C" seul (formulation métier du document)


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f10_enabled


def _daily_consumption(db: Session, ingredient_id: int) -> dict[date, float]:
    """Identique en principe à `ai_forecast._ingredient_daily_consumption` :
    dupliqué plutôt qu'importé pour ne pas coupler deux modules de
    fonctionnalités indépendantes via une fonction privée de l'un des deux."""
    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    daily: dict[date, float] = {}
    for rl in recipe_lines:
        sales = db.query(models.SaleLine).filter_by(dish_id=rl.dish_id).all()
        for sale in sales:
            d = sale.sale_date.date()
            daily[d] = daily.get(d, 0.0) + rl.quantity * sale.quantity_sold
    return daily


def _variance_history(db: Session, ingredient_id: int) -> list[float]:
    lines = (
        db.query(models.CountLine)
        .join(models.CountSession)
        .filter(
            models.CountLine.ingredient_id == ingredient_id,
            models.CountSession.ended_at.isnot(None),
            models.CountLine.counted_quantity.isnot(None),
        )
        .order_by(models.CountSession.ended_at)
        .all()
    )
    return [line.variance or 0.0 for line in lines]


def _coefficient_of_variation(variances: list[float]) -> float | None:
    if len(variances) < 3:
        return None
    mean_v = sum(variances) / len(variances)
    if mean_v == 0:
        return None
    return abs(statistics.pstdev(variances) / mean_v)


def _explain(
    weeks: float, annual_value: float | None, volatility: float | None,
    computed_class: str | None, is_dormant: bool,
) -> str:
    if is_dormant:
        return (
            f"Aucune consommation depuis {DORMANT_WINDOW_DAYS} jours malgré un "
            f"historique suffisant : signalé dormant, jamais classé A par défaut."
        )
    if annual_value is None:
        return f"{weeks:.1f} semaines de ventes sur {MIN_WEEKS_OF_SALES:.0f} nécessaires : non déterminé."
    base = f"valeur annuelle estimée {annual_value:.2f} € (classe {computed_class})"
    if volatility is not None:
        base += f", coefficient de variation des écarts {volatility:.2f}"
    return base


def classify_ingredients(db: Session, *, as_of: date | None = None) -> CriticalityResult:
    """docs/feature-plans/ia-f10-f19.md §1 (SYN-J)."""
    if not _feature_enabled(db):
        return CriticalityResult(ok=False, message="Fonctionnalité F10 désactivée (feature flag éteint).")

    as_of = as_of or datetime.utcnow().date()
    ingredients = db.query(models.Ingredient).filter_by(is_active=True).all()
    if not ingredients:
        return CriticalityResult(ok=False, message="Aucun ingrédient actif.")

    # (ingrédient, semaines, valeur_annuelle|None, volatilité|None, dormant)
    provisional: list[tuple[models.Ingredient, float, float | None, float | None, bool]] = []
    for ing in ingredients:
        daily = _daily_consumption(db, ing.id)
        volatility = _coefficient_of_variation(_variance_history(db, ing.id))
        if not daily:
            provisional.append((ing, 0.0, None, volatility, False))
            continue

        window_start, window_end = min(daily), max(daily)
        weeks = ((window_end - window_start).days + 1) / 7.0
        if weeks < MIN_WEEKS_OF_SALES:
            provisional.append((ing, weeks, None, volatility, False))
            continue

        recent_start = as_of - timedelta(days=DORMANT_WINDOW_DAYS)
        recent_consumption = sum(q for d, q in daily.items() if recent_start < d <= as_of)
        is_dormant = recent_consumption <= 0.0 and window_end <= as_of

        avg_daily = sum(daily.values()) / ((window_end - window_start).days + 1)
        annual_value = avg_daily * ing.unit_cost * 365.0
        provisional.append((ing, weeks, annual_value, volatility, is_dormant))

    # Classement Pareto sur les seuls ingrédients déterminés et non dormants
    # — un ingrédient dormant ne doit pas gonfler artificiellement le total
    # de référence des ingrédients réellement actifs.
    rankable = [
        (ing, weeks, val, vol) for ing, weeks, val, vol, dorm in provisional
        if val is not None and not dorm
    ]
    total_value = sum(val for _, _, val, _ in rankable)
    # Tri par valeur décroissante ; ex-æquo départagé par volatilité
    # décroissante (backlog-lot-ia-1, ticket 1 : « le plus volatil des deux
    # monte dans la classe supérieure »).
    rankable.sort(key=lambda t: (-t[2], -(t[3] or 0.0)))

    class_by_id: dict[int, str] = {}
    cumulative = 0.0
    for ing, _weeks, val, _vol in rankable:
        cumulative += val
        pct_cumule = cumulative / total_value if total_value > 0 else 1.0
        if pct_cumule <= CLASS_A_CUM_PCT:
            class_by_id[ing.id] = "A"
        elif pct_cumule <= CLASS_B_CUM_PCT:
            class_by_id[ing.id] = "B"
        else:
            class_by_id[ing.id] = "C"

    items: list[IngredientCriticality] = []
    for ing, weeks, val, vol, dorm in provisional:
        if dorm:
            computed = "dormant"
        elif val is not None:
            computed = class_by_id.get(ing.id)
        else:
            computed = None
        override = ing.criticality_override
        effective = override or computed
        items.append(IngredientCriticality(
            ingredient_id=ing.id, ingredient_name=ing.name, weeks_of_sales=weeks,
            annual_value=val, volatility=vol, computed_class=computed,
            manual_override=override, effective_class=effective,
            explanation=_explain(weeks, val, vol, computed, dorm),
        ))

    n_a = sum(1 for it in items if it.effective_class == "A")
    summary = (
        f"{n_a} ingrédient{pluriel(n_a)} représentent 80 % de votre coût matière"
        if n_a else "Historique encore insuffisant pour identifier vos ingrédients prioritaires"
    )
    return CriticalityResult(ok=True, message=None, items=items, summary=summary)


def set_manual_override(db: Session, ingredient_id: int, override_class: str | None) -> None:
    """AC-F10-3 : un forçage manuel prime toujours et survit à tout
    recalcul — persisté sur l'ingrédient, jamais recalculé."""
    if override_class is not None and override_class not in VALID_OVERRIDES:
        raise ValueError(f"Classe de criticité invalide : {override_class!r} (attendu A, B, C ou None).")
    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        raise ValueError(f"Ingrédient introuvable : {ingredient_id}.")
    ingredient.criticality_override = override_class
    db.commit()
