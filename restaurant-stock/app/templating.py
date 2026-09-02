from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.services import pricing

templates = Jinja2Templates(directory=str(Path(BASE_DIR) / "app" / "templates"))


def _fr_number(value: float, decimals: int) -> str:
    """Format français : espace pour les milliers, virgule décimale."""
    return f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")


def _euros(value) -> str:
    if value is None:
        return "—"
    # Les coûts unitaires (prix au gramme, etc.) arrondissent souvent à 0,00 €
    # avec 2 décimales : on affiche plus de précision uniquement dans ce cas,
    # pour ne pas perdre l'information sur les petits montants.
    decimals = 4 if value != 0 and round(value, 2) == 0 else 2
    return f"{_fr_number(value, decimals)} €"


def _qty(value) -> str:
    if value is None:
        return "—"
    if float(value).is_integer():
        return _fr_number(value, 0)
    return _fr_number(value, 2)


def _pct(value) -> str:
    """Pourcentage signé, virgule décimale, espace insécable avant % (OBS-3)."""
    if value is None:
        return "n/a"
    return f"{value:+.1f}".replace(".", ",") + " %"


def _unit_price_display(ingredient) -> str:
    """Prix unitaire lisible : « 1,20 €/kg » pour un ingrédient suivi en grammes.

    Tolère un objet de secours (formulaire ré-affiché après erreur) dont le
    coût est encore une chaîne brute : on affiche « — » plutôt que planter.
    """
    try:
        unit_cost = float(str(ingredient.unit_cost).replace(",", "."))
    except (TypeError, ValueError):
        return "—"
    display = pricing.to_display_price(unit_cost, ingredient.unit)
    return f"{_euros(display)}/{pricing.display_unit(ingredient.unit)}"


def _duration(seconds) -> str:
    if seconds is None:
        return "—"
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes} min {secs:02d} s" if minutes else f"{secs} s"


def _datetime_fr(value) -> str:
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y %H:%M")


def _date_fr(value) -> str:
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y")


def _line_price(line) -> str:
    """Prix d'une ligne de réception dans son unité d'achat : « 1,20 €/kg »."""
    unit = line.ingredient.unit
    return f"{_euros(pricing.to_display_price(line.unit_price, unit))}/{pricing.display_unit(unit)}"


def _history_price(entry) -> str:
    """Idem pour une entrée d'historique de prix."""
    unit = entry.ingredient.unit
    return f"{_euros(pricing.to_display_price(entry.unit_price, unit))}/{pricing.display_unit(unit)}"


templates.env.filters["euros"] = _euros
templates.env.filters["qty"] = _qty
templates.env.filters["pct"] = _pct
templates.env.filters["unit_price"] = _unit_price_display
templates.env.filters["duration"] = _duration
templates.env.filters["datetime_fr"] = _datetime_fr
templates.env.filters["date_fr"] = _date_fr
templates.env.filters["line_price"] = _line_price
templates.env.filters["history_price"] = _history_price
