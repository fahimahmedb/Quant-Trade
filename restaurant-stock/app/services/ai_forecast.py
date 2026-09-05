"""F6 — prévision de consommation par jour de semaine, EN MODE OMBRE
(Lot IA-0, docs/IA scope.md §1.2/1.7/1.10 pour les jeux SYN correspondants ;
section 4 : « F6 (prévision par jour de semaine) en mode ombre, jamais
visible »).

Mode ombre : cette fonction n'est appelée par aucun chemin de code qui
affiche son résultat à un restaurateur — rien dans ce lot ne l'expose. Elle
existe pour être comparée à la règle v1 (`app/services/ordering.py`) sur
l'historique disponible une fois le pilote en cours (IA-06, le seul gate
d'activation réel), jamais pour remplacer quoi que ce soit ici.

Opère au niveau de l'INGRÉDIENT (comme F13/F14 le supposent), pas du plat :
la consommation d'un ingrédient un jour donné est la somme, sur tous les
plats de sa fiche technique, de grammage × quantité vendue ce jour-là.

Robustesse (SYN-F, IA-08) : la MÉDIANE par jour de semaine est utilisée
plutôt que la moyenne — une moyenne serait faussée par une seule vente
aberrante (×100), une médiane sur une douzaine de semaines ne bouge pas
pour un seul point extrême. C'est le même principe qu'ailleurs dans le
projet : préférer l'estimateur le plus simple qui résiste au bruit réel,
pas le plus sophistiqué.
"""
import statistics
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service

MIN_WEEKS_OF_SALES = 6.0


@dataclass
class PartialDish:
    dish_id: int
    dish_name: str
    first_sale_on: date


@dataclass
class WeekdayForecast:
    ingredient_id: int
    expected_daily_qty: dict[int, float]  # weekday() -> quantité médiane attendue ; jamais un jour fermé
    closed_days: set[int]
    weeks_of_history: float
    partial_dishes: list[PartialDish] = field(default_factory=list)


@dataclass
class ForecastResult:
    gate_ok: bool
    gate_message: str | None
    forecast: WeekdayForecast | None


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f6_enabled


def _ingredient_daily_consumption(db: Session, ingredient_id: int) -> dict[date, float]:
    """{date -> quantité consommée ce jour, tous plats confondus} pour cet
    ingrédient — dérivé des VENTES, jamais du stock théorique (qui mélange
    réceptions, comptages, ajustements sans rapport avec la saisonnalité)."""
    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    daily: dict[date, float] = {}
    for rl in recipe_lines:
        sales = db.query(models.SaleLine).filter_by(dish_id=rl.dish_id).all()
        for sale in sales:
            d = sale.sale_date.date()
            daily[d] = daily.get(d, 0.0) + rl.quantity * sale.quantity_sold
    return daily


def _partial_dishes(db: Session, ingredient_id: int, window_start: date) -> list[PartialDish]:
    """Un plat dont la première vente arrive après le début de la fenêtre
    d'historique a un historique partiel (SYN-I, cold start) : F6 continue
    de fonctionner au niveau de l'ingrédient (il ne fabrique aucune vente
    rétroactive pour ce plat), mais un appelant doit pouvoir le signaler
    plutôt que de laisser croire que tout l'historique est plein."""
    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    out = []
    for rl in recipe_lines:
        first = (
            db.query(models.SaleLine)
            .filter_by(dish_id=rl.dish_id)
            .order_by(models.SaleLine.sale_date)
            .first()
        )
        if first is not None and first.sale_date.date() > window_start:
            out.append(PartialDish(dish_id=rl.dish_id, dish_name=rl.dish.name, first_sale_on=first.sale_date.date()))
    return out


def weekday_forecast(db: Session, ingredient_id: int) -> ForecastResult:
    """docs/IA scope.md §1.2 (SYN-A), §1.7 (SYN-F), §1.10 (SYN-I)."""
    if not _feature_enabled(db):
        return ForecastResult(
            gate_ok=False, gate_message="Fonctionnalité F6 désactivée (feature flag éteint).", forecast=None,
        )

    daily = _ingredient_daily_consumption(db, ingredient_id)
    if not daily:
        return ForecastResult(gate_ok=False, gate_message="Aucune vente pour cet ingrédient.", forecast=None)

    window_start, window_end = min(daily), max(daily)
    weeks = ((window_end - window_start).days + 1) / 7.0
    if weeks < MIN_WEEKS_OF_SALES:
        return ForecastResult(
            gate_ok=False,
            gate_message=f"{weeks:.1f} semaines de ventes sur {MIN_WEEKS_OF_SALES:.0f} nécessaires",
            forecast=None,
        )

    par_jour: dict[int, list[float]] = {}
    for d, qty in daily.items():
        par_jour.setdefault(d.weekday(), []).append(qty)
    closed_days = set(range(7)) - set(par_jour)

    expected = {wd: statistics.median(vals) for wd, vals in par_jour.items()}

    forecast = WeekdayForecast(
        ingredient_id=ingredient_id, expected_daily_qty=expected, closed_days=closed_days,
        weeks_of_history=weeks, partial_dishes=_partial_dishes(db, ingredient_id, window_start),
    )
    return ForecastResult(gate_ok=True, gate_message=None, forecast=forecast)
