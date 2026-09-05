"""F7 — suggestion de commande consciente du cycle de livraison (Lot IA-0,
docs/IA scope.md §1.8, cible SYN-G). Complète (ne remplace pas)
`app/services/ordering.py`, qui reste la règle v1 par seuil simple.

Deux couches :
- `plan_order_cycle` : fonction pure (aucun accès DB), le cœur testable de
  F7 — étant donné un rythme de consommation déjà connu, calcule QUAND
  commander et COMBIEN, en tenant compte des jours de livraison, de
  l'heure limite, du conditionnement et du plafond de péremption.
- `plan_order_cycle_for_ingredient` : la version branchée sur la base,
  gatée par `Settings.feature_f7_enabled`. Consulte F6 (mode ombre) pour le
  rythme de consommation si son propre gate est atteint pour cet
  ingrédient, sinon retombe sur la moyenne glissante v1
  (`ordering.rolling_avg_daily_consumption`) — jamais d'erreur faute de
  F6, juste une estimation moins fine.
"""
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import ai_forecast, ordering, settings_service


@dataclass
class OrderCycleResult:
    ok: bool
    message: str
    order_now: bool = False
    target_delivery: datetime | None = None
    covers_until: datetime | None = None
    suggested_quantity: float | None = None
    warnings: list[str] = field(default_factory=list)


def _next_weekday_on_or_after(d: datetime, weekdays: set[int]) -> datetime:
    for offset in range(8):
        candidate = d + timedelta(days=offset)
        if candidate.weekday() in weekdays:
            return candidate
    raise ValueError("Aucun jour de livraison dans la semaine.")


def plan_order_cycle(
    *, today: datetime, delivery_weekdays: set[int], shelf_life_days: float,
    daily_consumption: float, current_stock: float, pack_size: float,
    order_cutoff_passed: bool = False,
) -> OrderCycleResult:
    """docs/IA scope.md §1.8 (SYN-G, variantes G1/G2/G3). Fonction pure :
    le feature flag et le choix de `daily_consumption` (F6 ou v1) sont la
    responsabilité de l'appelant."""
    if not delivery_weekdays:
        return OrderCycleResult(ok=False, message="Aucun jour de livraison connu pour cet ingrédient.")
    if pack_size <= 0:
        return OrderCycleResult(ok=False, message="Conditionnement inconnu ou invalide pour cet ingrédient.")

    first_reachable = _next_weekday_on_or_after(today + timedelta(days=1), delivery_weekdays)
    if order_cutoff_passed:
        target_delivery = _next_weekday_on_or_after(first_reachable + timedelta(days=1), delivery_weekdays)
    else:
        target_delivery = first_reachable
    next_after_target = _next_weekday_on_or_after(target_delivery + timedelta(days=1), delivery_weekdays)

    coverage_days = (next_after_target - target_delivery).days
    days_until_target = (target_delivery - today).days
    stock_at_target = max(0.0, current_stock - daily_consumption * days_until_target)
    needed = max(0.0, coverage_days * daily_consumption - stock_at_target)
    suggested = math.ceil(needed / pack_size) * pack_size if needed > 0 else 0.0

    warnings: list[str] = []
    max_within_shelf_life = shelf_life_days * daily_consumption
    if suggested > max_within_shelf_life:
        capped = math.ceil(max_within_shelf_life / pack_size) * pack_size if max_within_shelf_life > 0 else 0.0
        if pack_size > max_within_shelf_life:
            warnings.append(
                f"Fréquence de livraison insuffisante face à la conservation "
                f"({shelf_life_days:g} j) : même {pack_size:g} (conditionnement minimal) "
                f"dépasserait la limite de péremption avant d'être consommé."
            )
        else:
            warnings.append(
                f"Quantité plafonnée à {capped:g} pour respecter la conservation "
                f"({shelf_life_days:g} j) au lieu de {suggested:g}, qui aurait suffi "
                f"jusqu'à la prochaine livraison."
            )
        suggested = capped

    message = (
        f"Livraison visée le {target_delivery:%A %d/%m}"
        + (" (heure limite dépassée pour la précédente)" if order_cutoff_passed else "")
        + f", à couvrir jusqu'au {next_after_target:%d/%m}."
    )
    return OrderCycleResult(
        ok=True, message=message, order_now=True, target_delivery=target_delivery,
        covers_until=next_after_target, suggested_quantity=suggested, warnings=warnings,
    )


def _parse_delivery_weekdays(raw: str | None) -> set[int]:
    if not raw:
        return set()
    return {int(x) for x in raw.split(",") if x.strip() != ""}


def plan_order_cycle_for_ingredient(
    db: Session, ingredient_id: int, *, today: datetime | None = None,
    order_cutoff_passed: bool = False,
) -> OrderCycleResult:
    if not settings_service.get_settings(db).feature_f7_enabled:
        return OrderCycleResult(ok=False, message="Fonctionnalité F7 désactivée (feature flag éteint).")

    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return OrderCycleResult(ok=False, message="Ingrédient introuvable.")

    delivery_weekdays = _parse_delivery_weekdays(ingredient.delivery_weekdays)
    if not delivery_weekdays or not ingredient.shelf_life_days or not ingredient.pack_size:
        return OrderCycleResult(
            ok=False,
            message="Conservation, jours de livraison ou conditionnement non renseignés pour cet "
                    "ingrédient : F7 reste inactif, la règle v1 (suggestions par seuil) s'applique.",
        )

    today = today or datetime.utcnow()
    settings = settings_service.get_settings(db)
    daily_consumption = ordering.rolling_avg_daily_consumption(db, ingredient_id, settings.rolling_window_days, as_of=today)
    forecast = ai_forecast.weekday_forecast(db, ingredient_id)
    if forecast.gate_ok and today.weekday() not in forecast.forecast.closed_days:
        daily_consumption = forecast.forecast.expected_daily_qty.get(today.weekday(), daily_consumption)

    return plan_order_cycle(
        today=today, delivery_weekdays=delivery_weekdays, shelf_life_days=ingredient.shelf_life_days,
        daily_consumption=daily_consumption, current_stock=ingredient.current_theoretical_stock,
        pack_size=ingredient.pack_size, order_cutoff_passed=order_cutoff_passed,
    )
