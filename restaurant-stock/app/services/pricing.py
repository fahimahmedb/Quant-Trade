"""Conversion entre prix stocké et prix affiché/saisi (OBS-2, F1).

Le prix est stocké par unité de référence de l'ingrédient (le gramme pour
la farine). Personne n'achète ni ne lit un prix au gramme : à l'écran et à
la saisie d'une réception, on manipule des €/kg et des €/L. Une seule
table de conversion, ici, pour que l'affichage et la saisie ne puissent pas
diverger.
"""

# unité de référence -> (facteur, unité d'achat affichée)
_DISPLAY = {"g": (1000.0, "kg"), "mL": (1000.0, "L")}


def _unit_value(unit) -> str:
    return getattr(unit, "value", unit)


def display_unit(unit) -> str:
    """Unité dans laquelle le prix se lit et se saisit : kg, L, ou l'unité elle-même."""
    return _DISPLAY.get(_unit_value(unit), (1.0, _unit_value(unit)))[1]


def factor(unit) -> float:
    """Nombre d'unités de référence dans une unité d'achat (1000 g par kg)."""
    return _DISPLAY.get(_unit_value(unit), (1.0, None))[0]


def to_display_price(storage_price: float, unit) -> float:
    """0,0012 €/g -> 1,20 €/kg."""
    return storage_price * factor(unit)


def to_storage_price(display_price: float, unit) -> float:
    """1,20 €/kg -> 0,0012 €/g."""
    return display_price / factor(unit)
