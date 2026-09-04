from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.services import pricing

templates = Jinja2Templates(directory=str(Path(BASE_DIR) / "app" / "templates"))


# Espace fine insécable (U+202F). C'est l'espace des milliers en typographie
# française, et celle qui précède « € » ou « % ». Insécable pour qu'un montant
# ne se coupe jamais en fin de ligne ; fine pour que « 14 400 g » ne s'écarte
# pas quand le nombre est composé en chasse fixe (direction visuelle V1.2).
ESPACE_FINE = "\u202f"


def _fr_number(value: float, decimals: int) -> str:
    """Format français : espace fine pour les milliers, virgule décimale."""
    return f"{value:,.{decimals}f}".replace(",", ESPACE_FINE).replace(".", ",")


def _euros(value) -> str:
    if value is None:
        return "—"
    # Les coûts unitaires (prix au gramme, etc.) arrondissent souvent à 0,00 €
    # avec 2 décimales : on affiche plus de précision uniquement dans ce cas,
    # pour ne pas perdre l'information sur les petits montants.
    decimals = 4 if value != 0 and round(value, 2) == 0 else 2
    return f"{_fr_number(value, decimals)}{ESPACE_FINE}€"


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


def _input_number(value) -> str:
    """Valeur d'un `<input type="number">`.

    La spécification HTML impose le point décimal et interdit le séparateur de
    milliers sur cet attribut : un `value` en virgule y serait invalide et le
    champ s'afficherait vide. Ce champ reste donc en point décimal — l'écran
    de comptage (seul restant sur `type="number"`, cf. `decimal_fr` ci-dessous
    pour les autres) a sa propre validation à venir, pas encore faite ici.
    Le filtre retire seulement le « .0 » d'un nombre entier : en chasse fixe
    et en gros corps, « 12672.0 » se lit moins vite que « 12672 » et donne
    deux caractères de plus à effacer avant de saisir la vraie quantité.

    Point corrigé après coup : une version antérieure de ce commentaire
    affirmait que « le navigateur affiche lui-même la virgule en locale
    française ». C'est faux en pratique (Chromium, notamment, ne le fait
    jamais) — l'hypothèse n'avait pas été vérifiée sur un vrai navigateur.
    """
    if value is None:
        return ""
    number = float(value)
    return str(int(number)) if number.is_integer() else f"{number:.2f}".rstrip("0").rstrip(".")


def _decimal_fr(value) -> str:
    """Valeur d'un champ décimal éditable en `<input type="text" inputmode="decimal">`.

    Contrairement à `qty` (affichage, arrondi à 2 décimales pour la lecture),
    ce filtre garde la précision stockée : un coût au gramme à 0,0025 € ne
    doit pas se retrouver arrondi à 0,00 € en rouvrant le formulaire. Comme
    ce n'est plus un `<input type="number">`, rien n'impose le point : la
    virgule française s'affiche pour de vrai, pas seulement en théorie.

    Une chaîne est laissée telle quelle plutôt que reconvertie : un
    formulaire ré-affiché après une erreur de validation passe la saisie
    brute de la personne (`SimpleNamespace`, cf. les routeurs settings et
    ingredients), virgule ou non — et parfois invalide, précisément ce
    qu'elle doit revoir. La reformater ferait perdre l'erreur qu'on lui
    montre, ou planterait sur une virgule que `float()` n'accepte pas.
    """
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value
    number = float(value)
    texte = f"{number:.10f}".rstrip("0").rstrip(".")
    return (texte or "0").replace(".", ",")


def pluriel(n) -> str:
    """« s » d'accord au pluriel (0 ou 2+), rien au singulier (1).

    Remplace le `(s)` entre parenthèses laissé sur un nombre de lignes —
    correct dans tous les cas mais illisible, et une signature reconnaissable
    de logiciel pas fini. Les pluriels de ce projet sont tous réguliers
    (ligne/lignes, ingrédient/ingrédients…) — pas besoin d'une table
    d'exceptions. Nom public (pas de `_`) : les messages flash construits
    dans les routeurs l'importent aussi, pas seulement les gabarits Jinja.
    """
    return "" if abs(n) == 1 else "s"


templates.env.filters["euros"] = _euros
templates.env.filters["input_number"] = _input_number
templates.env.filters["decimal_fr"] = _decimal_fr
templates.env.filters["pluriel"] = pluriel
templates.env.filters["qty"] = _qty
templates.env.filters["pct"] = _pct
templates.env.filters["unit_price"] = _unit_price_display
templates.env.filters["duration"] = _duration
templates.env.filters["datetime_fr"] = _datetime_fr
templates.env.filters["date_fr"] = _date_fr
templates.env.filters["line_price"] = _line_price
templates.env.filters["history_price"] = _history_price
