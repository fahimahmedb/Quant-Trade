"""Aide à la lecture des formulaires saisis par un utilisateur français.

Les champs `<input type="number">` imposent un point décimal côté navigateur,
mais certains navigateurs en locale française acceptent et soumettent quand
même une virgule (ex. Firefox). On l'accepte partout plutôt que de laisser
un ValueError remonter en 500.
"""


class InvalidNumberError(ValueError):
    def __init__(self, raw: str, message: str | None = None):
        super().__init__(message or f"« {raw} » n'est pas un nombre valide.")
        self.raw = raw


def parse_float_fr(raw: str) -> float:
    cleaned = (raw or "").strip()
    if not cleaned:
        raise InvalidNumberError(raw, message="Ce champ numérique est obligatoire.")
    try:
        return float(cleaned.replace(",", "."))
    except ValueError as exc:
        raise InvalidNumberError(raw) from exc


def parse_optional_float_fr(raw: str) -> float | None:
    raw = (raw or "").strip()
    return parse_float_fr(raw) if raw else None


def parse_int_fr(raw: str) -> int:
    cleaned = (raw or "").strip()
    if not cleaned:
        raise InvalidNumberError(raw, message="Ce champ numérique est obligatoire.")
    try:
        return int(float(cleaned.replace(",", ".")))
    except ValueError as exc:
        raise InvalidNumberError(raw) from exc
