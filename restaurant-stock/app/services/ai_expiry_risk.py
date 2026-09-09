"""F14 — risque de péremption (Lot IA-1, docs/feature-plans/ia-f10-f19.md
§5, cible SYN-M). Signale le stock qui ne sera pas consommé avant la fin
de sa durée de conservation, SANS exiger de DLC par lot — juste la durée
de conservation optionnelle déjà prévue par F7 (`Ingredient.shelf_life_days`).

Gate réel : durée de conservation renseignée. Le document dit « F6 actif
OU moyenne glissante v1 disponible », mais la moyenne glissante v1
(`ordering.rolling_avg_daily_consumption`) répond toujours 0.0 sans jamais
échouer — ce n'est donc jamais un second gate qui bloquerait quoi que ce
soit, juste une source de repli. Même hiérarchie que F7
(`ai_ordering.plan_order_cycle_for_ingredient`) : F6 si son propre gate
est atteint pour cet ingrédient, sinon la moyenne glissante v1.

Calcul, sans jamais diviser par la consommation (TC-F14-04, consommation
nulle) : plutôt que « combien de jours avant épuisement », on calcule
directement « combien restera-t-il à la fin de la conservation » —
`stock_actuel − conservation × consommation`. Une consommation nulle
donne alors directement `stock_actuel` en trop, sans jamais buter sur une
division par zéro : la formule n'en contient aucune.

Suggestion d'action volontairement limitée à réduire la prochaine
commande — jamais un plat du jour ou une promotion, hors du domaine de
compétence de l'outil (principe d'explicabilité des specs V2).
"""
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import ai_forecast, ordering, settings_service


@dataclass
class ExpiryRiskResult:
    ok: bool
    message: str | None
    at_risk: bool = False
    daily_consumption: float | None = None
    remaining_at_shelf_life_end: float | None = None
    value_at_risk: float | None = None
    explanation: str = ""


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f14_enabled


def assess_expiry_risk(db: Session, ingredient_id: int, *, today: datetime | None = None) -> ExpiryRiskResult:
    """docs/feature-plans/ia-f10-f19.md §5 (SYN-M)."""
    if not _feature_enabled(db):
        return ExpiryRiskResult(ok=False, message="Fonctionnalité F14 désactivée (feature flag éteint).")

    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return ExpiryRiskResult(ok=False, message="Ingrédient introuvable.")

    if not ingredient.shelf_life_days:
        return ExpiryRiskResult(
            ok=False,
            message="Durée de conservation non renseignée pour cet ingrédient : F14 reste inactif.",
        )

    today = today or datetime.utcnow()
    settings = settings_service.get_settings(db)
    daily_consumption = ordering.rolling_avg_daily_consumption(
        db, ingredient_id, settings.rolling_window_days, as_of=today,
    )
    forecast = ai_forecast.weekday_forecast(db, ingredient_id)
    if forecast.gate_ok and today.weekday() not in forecast.forecast.closed_days:
        daily_consumption = forecast.forecast.expected_daily_qty.get(today.weekday(), daily_consumption)

    remaining = max(0.0, ingredient.current_theoretical_stock - ingredient.shelf_life_days * daily_consumption)
    at_risk = remaining > 0.0
    value = remaining * ingredient.unit_cost if at_risk else 0.0

    explanation = (
        (
            f"Il vous restera ~{remaining:g} {ingredient.unit.value} de {ingredient.name} dans "
            f"{ingredient.shelf_life_days:g} jours, au-delà de leur conservation habituelle — "
            f"environ {value:.2f} €. Réduire la prochaine commande de cet ingrédient."
        )
        if at_risk else
        f"{ingredient.name} : tout le stock actuel sera consommé avant la fin de sa conservation."
    )

    return ExpiryRiskResult(
        ok=True, message=None, at_risk=at_risk, daily_consumption=daily_consumption,
        remaining_at_shelf_life_end=remaining if at_risk else 0.0,
        value_at_risk=value, explanation=explanation,
    )
