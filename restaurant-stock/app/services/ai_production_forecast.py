"""F13 — prévision de mise en place (Lot IA-1, docs/feature-plans/
ia-f10-f19.md §4). « Combien je prépare demain », pas seulement « combien
je commande » — pour les ingrédients marqués comme préparés en interne
(sauces, garnitures, fonds), une sur-préparation quotidienne distincte de
la sur-commande sur carte fixe.

Gate (§4) : « F6 actif pour les ingrédients concernés » — réutilise tel
quel le gate de `ai_forecast.weekday_forecast` (F6), jamais redéfini
séparément. S'ajoutent, comme pour tout ce lot, le marqueur optionnel
lui-même (AC-F13-1 : aucun ingrédient marqué -> fonctionnalité invisible)
et le feature flag F13.

`weekday_forecast` est appelé SANS `as_of` (comme F7/F14 : `ai_ordering.
suggest_order` et `ai_expiry_risk.assess_expiry_risk` font de même) — cet
appel est un usage LIVE, pas un rejeu du passé : aucune vente future
n'existe à exclure. `as_of` sert ici uniquement à déterminer « demain » et
les jours fermés (TC-F13-04), jamais à tronquer l'historique d'entraînement
de F6, ce qui l'affaiblirait sans raison.

Fenêtre de production : « le service du lendemain, OU les N jours de
conservation de la préparation » — réutilise `Ingredient.shelf_life_days`
(champ F7 déjà prévu), pas un second champ dupliquant le même concept.
Sans durée renseignée (ou < 1 jour), fenêtre d'1 jour — le même repli que
F14 applique à la même donnée (TC-F13-05 : 3 jours de conservation ->
production couvrant 3 jours, pas 1, donc 1 jour reste le comportement par
défaut en son absence).

Stock existant déduit (AC-F13-3) : le reste de la préparation précédente
EST `Ingredient.current_theoretical_stock` — un ingrédient « préparé en
interne » est un ingrédient comme un autre, suivi par le même stock
théorique ; aucun second compteur à synchroniser.

Mémorisation de l'écart prévision/décision réelle (« indicateur de
confiance », §4) : NON CONSTRUITE. Contrairement à AC-F13-1/2/3 et
TC-F13-04/05 (entièrement couverts ci-dessous), aucun critère d'acceptation
ni cas de test de ce ticket ne la spécifie — sa forme exacte (table dédiée ?
réutilisation de `ModelDecisionLog`, F18 ? quelle définition de
« confiance » ?) resterait devinée sans détail supplémentaire du porteur
du projet. Documenté comme écart ouvert, pas implémenté sur une
supposition (même principe que le seuil de promotion de volatilité laissé
en suspens pour F10, docs/bilan-ia-1.md §1)."""
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import ai_forecast, settings_service
from app.templating import pluriel

DEFAULT_WINDOW_DAYS = 1  # sans conservation renseignée : un seul service


@dataclass
class ProductionForecastResult:
    ok: bool
    message: str | None
    ingredient_id: int | None = None
    window_days: int = 0
    expected_consumption: float | None = None
    current_stock: float | None = None
    suggested_quantity: float | None = None
    explanation: str = ""


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f13_enabled


def _window_days(ingredient: models.Ingredient) -> int:
    if ingredient.shelf_life_days and ingredient.shelf_life_days >= 1:
        return max(1, round(ingredient.shelf_life_days))
    return DEFAULT_WINDOW_DAYS


def forecast_production(db: Session, ingredient_id: int, *, as_of: date | None = None) -> ProductionForecastResult:
    """ia-f10-f19.md §4 (AC-F13-1/2/3, TC-F13-04/05, cible SYN-A pour AC-F13-2)."""
    if not _feature_enabled(db):
        return ProductionForecastResult(ok=False, message="Fonctionnalité F13 désactivée (feature flag éteint).")

    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return ProductionForecastResult(ok=False, message="Ingrédient introuvable.")

    if not ingredient.is_prepared_in_house:
        return ProductionForecastResult(
            ok=False, message="Cet ingrédient n'est pas marqué « préparé en interne ».",
            ingredient_id=ingredient_id,
        )

    outcome = ai_forecast.weekday_forecast(db, ingredient_id)
    if not outcome.gate_ok:
        return ProductionForecastResult(ok=False, message=outcome.gate_message, ingredient_id=ingredient_id)

    today = as_of or date.today()
    window_days = _window_days(ingredient)

    expected = 0.0
    for offset in range(window_days):
        jour = today + timedelta(days=offset + 1)
        expected += outcome.forecast.expected_daily_qty.get(jour.weekday(), 0.0)

    stock = ingredient.current_theoretical_stock
    suggested = max(0.0, expected - stock)

    if suggested <= 0:
        explanation = (
            f"{ingredient.name} : le stock actuel ({stock:g}) couvre la consommation attendue "
            f"des {window_days} prochain{pluriel(window_days)} jour{pluriel(window_days)} — "
            "aucune production à suggérer."
        )
    else:
        explanation = (
            f"{ingredient.name} : préparer {suggested:g} pour les {window_days} prochain"
            f"{pluriel(window_days)} jour{pluriel(window_days)} ({expected:g} attendus, "
            f"{stock:g} déjà en stock)."
        )

    return ProductionForecastResult(
        ok=True, message=None, ingredient_id=ingredient_id, window_days=window_days,
        expected_consumption=expected, current_stock=stock, suggested_quantity=suggested,
        explanation=explanation,
    )
