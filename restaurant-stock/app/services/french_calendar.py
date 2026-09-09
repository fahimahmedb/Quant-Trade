"""Calendrier français : jours fériés (calculés) et vacances scolaires
(données embarquées, zones A/B/C) — F20 (Lot IA-2, docs/feature-plans/
backlog-lot-ia-2.md ticket 4). Aucune dépendance réseau : « calendrier
déterministe, connu des années à l'avance » (décision actée du ticket).
Fonctions pures, sans accès base de données — testables indépendamment
de la logique métier de F20 (`ai_calendar_signals.py`).

Jours fériés : calculés par formule, jamais une liste figée par année —
les dates fixes ne varient jamais, les dates mobiles (lundi de Pâques,
Ascension, lundi de Pentecôte) se déduisent du dimanche de Pâques par
l'algorithme de Meeus/Jones/Butcher (calendrier grégorien), standard et
vérifiable indépendamment.

Vacances scolaires : contrairement aux jours fériés, ces dates sont
fixées administrativement chaque année par le ministère de l'Éducation
nationale et ne se calculent PAS par formule — données embarquées ici
pour les années scolaires 2025-2026 et 2026-2027 (sources : education.
gouv.fr et presse spécialisée, vérifiées au moment de l'écriture,
septembre 2026). À COMPLÉTER chaque nouvelle année scolaire annoncée —
c'est le seul entretien manuel que ce module demande, anticipé par le
backlog lui-même (« à mettre à jour manuellement chaque année scolaire »).
"""
from datetime import date, timedelta

VACATION_ZONES = ("A", "B", "C")


def _easter_sunday(year: int) -> date:
    """Dimanche de Pâques, algorithme de Meeus/Jones/Butcher."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def public_holidays(year: int) -> set[date]:
    """Les 11 jours fériés légaux français d'une année donnée (France
    métropolitaine — Alsace-Moselle et DOM-TOM ont des jours
    supplémentaires, hors périmètre de ce MVP mono-établissement)."""
    easter = _easter_sunday(year)
    return {
        date(year, 1, 1),  # Jour de l'an
        easter + timedelta(days=1),  # Lundi de Pâques
        date(year, 5, 1),  # Fête du travail
        date(year, 5, 8),  # Victoire 1945
        easter + timedelta(days=39),  # Ascension
        easter + timedelta(days=50),  # Lundi de Pentecôte
        date(year, 7, 14),  # Fête nationale
        date(year, 8, 15),  # Assomption
        date(year, 11, 1),  # Toussaint
        date(year, 11, 11),  # Armistice
        date(year, 12, 25),  # Noël
    }


def is_public_holiday(d: date) -> bool:
    return d in public_holidays(d.year)


# Vacances scolaires par zone — voir docstring du module pour les sources
# et la nécessité d'un entretien manuel annuel. Chaque entrée est un
# intervalle FERMÉ (début et fin inclus, samedi à lundi comme publié).
# "Toussaint"/"Noël"/"Été" communes aux 3 zones ; "Hiver"/"Printemps"
# varient par zone.
_VACATIONS_COMMON: list[tuple[date, date]] = [
    (date(2025, 10, 18), date(2025, 11, 3)),  # Toussaint 2025
    (date(2025, 12, 20), date(2026, 1, 5)),  # Noël 2025-2026
    (date(2026, 7, 4), date(2026, 8, 31)),  # Été 2026 (jusqu'à la rentrée du 1er sept.)
    (date(2026, 10, 17), date(2026, 11, 2)),  # Toussaint 2026
    (date(2026, 12, 19), date(2027, 1, 4)),  # Noël 2026-2027
    (date(2027, 7, 3), date(2027, 8, 31)),  # Été 2027, fin approximative (hors sources vérifiées)
]

_VACATIONS_BY_ZONE: dict[str, list[tuple[date, date]]] = {
    "A": [
        (date(2026, 2, 7), date(2026, 2, 23)),  # Hiver 2026
        (date(2026, 4, 4), date(2026, 4, 20)),  # Printemps 2026
        (date(2027, 2, 13), date(2027, 3, 1)),  # Hiver 2027
        (date(2027, 4, 10), date(2027, 4, 26)),  # Printemps 2027
    ],
    "B": [
        (date(2026, 2, 14), date(2026, 3, 2)),
        (date(2026, 4, 11), date(2026, 4, 27)),
        (date(2027, 2, 20), date(2027, 3, 8)),
        (date(2027, 4, 17), date(2027, 5, 3)),
    ],
    "C": [
        (date(2026, 2, 21), date(2026, 3, 9)),
        (date(2026, 4, 18), date(2026, 5, 4)),
        (date(2027, 2, 6), date(2027, 2, 22)),
        (date(2027, 4, 3), date(2027, 4, 19)),
    ],
}


def is_school_vacation(d: date, zone: str | None) -> bool:
    """`zone` optionnel (dégradation silencieuse, backlog §1 règle 2) :
    sans zone connue, seules les vacances COMMUNES aux 3 zones (Toussaint,
    Noël, Été) sont détectées — jamais une zone devinée."""
    for start, end in _VACATIONS_COMMON:
        if start <= d <= end:
            return True
    if zone and zone in _VACATIONS_BY_ZONE:
        for start, end in _VACATIONS_BY_ZONE[zone]:
            if start <= d <= end:
                return True
    return False
