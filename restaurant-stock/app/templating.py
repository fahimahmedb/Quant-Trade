from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR

templates = Jinja2Templates(directory=str(Path(BASE_DIR) / "app" / "templates"))


def _euros(value) -> str:
    if value is None:
        return "—"
    # Les coûts unitaires (prix au gramme, etc.) arrondissent souvent à 0,00 €
    # avec 2 décimales : on affiche plus de précision uniquement dans ce cas,
    # pour ne pas perdre l'information sur les petits montants.
    decimals = 4 if value != 0 and round(value, 2) == 0 else 2
    return f"{value:,.{decimals}f} €".replace(",", " ").replace(".", ",")


def _qty(value) -> str:
    if value is None:
        return "—"
    if float(value).is_integer():
        return f"{value:,.0f}".replace(",", " ")
    return f"{value:,.2f}".replace(",", " ").replace(".", ",")


def _duration(seconds) -> str:
    if seconds is None:
        return "—"
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes} min {secs:02d} s" if minutes else f"{secs} s"


def _datetime_fr(value) -> str:
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y %H:%M")


templates.env.filters["euros"] = _euros
templates.env.filters["qty"] = _qty
templates.env.filters["duration"] = _duration
templates.env.filters["datetime_fr"] = _datetime_fr
