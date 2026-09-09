"""F23 — cold start d'un plat sans historique (Lot IA-2, docs/feature-plans/
backlog-lot-ia-2.md ticket 5). Un plat neuf sur la carte n'a aucune vente :
F6 (`ai_forecast.weekday_forecast`) reste bloqué par son propre gate (6
semaines d'historique) tant que ces ventes n'existent pas, et la v1
(`ordering.rolling_avg_daily_consumption`) renvoie 0 — aucune des deux ne
peut s'appuyer sur autre chose que des ventes déjà constatées. Ce module
comble cet intervalle, jamais après : dès que F6 est lui-même disponible
pour l'ingrédient, la bascule est complète (backlog, règle métier) et cette
fonction s'efface (`ok=False`, message explicite) plutôt que de continuer à
produire un résultat concurrent.

Opère au niveau de l'INGRÉDIENT, comme F6/F7/F13/F14 (jamais du plat) — la
« fiche technique » du backlog est ici le mécanisme de conversion : la
somme, sur chaque plat utilisant cet ingrédient ET ayant une estimation
initiale du chef, de estimation × grammage.

Pourquoi agréger sur TOUS les plats de la fiche technique, sans risque de
double comptage avec un plat déjà établi qui partagerait cet ingrédient :
le gate ci-dessus (F6 non encore disponible POUR CET INGRÉDIENT) borne déjà
le cas d'usage. Si un plat déjà établi consommait cet ingrédient depuis
plusieurs semaines, l'historique combiné de l'ingrédient aurait déjà
dépassé les 6 semaines de F6 — son gate serait alors déjà vrai, et cette
fonction ne serait jamais atteinte (voir le premier `if outcome.gate_ok`
ci-dessous). Le cas réellement traité ici est donc toujours celui où TOUS
les plats consommant cet ingrédient sont eux-mêmes récents — jamais un
plat neuf qui « emprunterait » à tort le passé d'un plat ancien.

Pondération glissante (règle métier du ticket, appliquée littéralement,
jamais réinventée) : poids_réel = jours_observés / (jours_observés +
constante_lissage). Constante en `Settings.cold_start_smoothing_days`,
vérifiée empiriquement sur SYN-S avant d'être figée à 14 (jours) — voir
docstring de `tests/test_ai_cold_start.py` pour le détail du choix.

Sortie : une quantité/jour unique (pas de décomposition par jour de
semaine, contrairement à F6) — F6 exige justement l'historique que ce
cold-start n'a pas encore ; toute tentative de granularité par jour de
semaine ici serait statistiquement creuse. Même rôle que `ordering.
rolling_avg_daily_consumption` (le repli v1 déjà utilisé par F7), en mieux
informé : un repli de plus, jamais un second calcul de F6.
"""
from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from app import models
from app.services import ai_forecast, settings_service
from app.templating import pluriel


@dataclass
class ColdStartResult:
    ok: bool
    message: str | None
    chef_component: float | None = None
    real_component: float | None = None
    days_observed: int = 0
    real_weight: float | None = None
    blended_daily_qty: float | None = None
    explanation: str = ""


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f23_enabled


def _chef_component(db: Session, ingredient_id: int) -> float | None:
    """None si AUCUN plat utilisant cet ingrédient n'a d'estimation initiale
    du chef — dégradation silencieuse : rien à mélanger, F23 ne s'applique
    pas (Gate du ticket : « absent, le plat garde le comportement actuel »)."""
    lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    total = 0.0
    any_estimate = False
    for line in lines:
        if line.dish.initial_daily_estimate is not None:
            any_estimate = True
            total += line.dish.initial_daily_estimate * line.quantity
    return total if any_estimate else None


def blended_daily_consumption(
    db: Session, ingredient_id: int, *, as_of: date | None = None,
) -> ColdStartResult:
    """backlog-lot-ia-2.md ticket 5."""
    if not _feature_enabled(db):
        return ColdStartResult(ok=False, message="Fonctionnalité F23 désactivée (feature flag éteint).")

    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return ColdStartResult(ok=False, message="Ingrédient introuvable.")

    outcome = ai_forecast.weekday_forecast(db, ingredient_id, as_of=as_of)
    if outcome.gate_ok:
        return ColdStartResult(
            ok=False,
            message="F6 déjà disponible pour cet ingrédient : bascule complète déjà faite (règle métier du "
                    "ticket F23), ce repli ne s'applique plus.",
        )

    chef = _chef_component(db, ingredient_id)
    if chef is None:
        return ColdStartResult(
            ok=False,
            message="Aucun plat utilisant cet ingrédient n'a d'estimation initiale du chef : F23 ne s'applique pas.",
        )

    as_of = as_of or date.today()
    daily = ai_forecast.ingredient_daily_consumption(db, ingredient_id)
    daily = {d: qty for d, qty in daily.items() if d < as_of}

    if daily:
        window_start = min(daily)
        days_observed = (as_of - window_start).days
        real_avg = sum(daily.values()) / days_observed if days_observed > 0 else 0.0
    else:
        days_observed = 0
        real_avg = 0.0

    settings = settings_service.get_settings(db)
    k = settings.cold_start_smoothing_days
    real_weight = days_observed / (days_observed + k) if (days_observed + k) > 0 else 0.0
    blended = (1 - real_weight) * chef + real_weight * real_avg

    if days_observed == 0:
        explanation = (
            f"{blended:g}/jour estimés — aucune vente réelle encore : estimation initiale du chef "
            "seule (fiche technique appliquée)."
        )
    else:
        explanation = (
            f"{blended:g}/jour estimés — {chef:g} (estimation du chef) et {real_avg:g} (moyenne réelle "
            f"sur {days_observed} jour{pluriel(days_observed)}), pondéré à {real_weight:.0%} vers le réel."
        )

    return ColdStartResult(
        ok=True, message=None, chef_component=chef, real_component=real_avg,
        days_observed=days_observed, real_weight=real_weight, blended_daily_qty=blended,
        explanation=explanation,
    )
