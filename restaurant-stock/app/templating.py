from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR

templates = Jinja2Templates(directory=str(Path(BASE_DIR) / "app" / "templates"))


def _euros(value) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", " ").replace(".", ",")


def _qty(value) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}".replace(",", " ") if float(value).is_integer() else f"{value:,.2f}"


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
