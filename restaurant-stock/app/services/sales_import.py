"""Import CSV des ventes (4.2) et décrémentation du stock théorique (4.3).

Le schéma CSV exact varie selon le logiciel de caisse (Zelty, L'Addition,
Square...) — cf. section 9 du brief. On reste tolérant sur les en-têtes et
les formats de date/nombre plutôt que d'imposer un format unique dès la v1.
"""
import csv
import io
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import stock

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]

HEADER_ALIASES = {
    "date": {"date", "jour"},
    "dish": {"plat", "nom du plat", "produit", "article", "dish", "item"},
    "quantity": {"quantite", "qte", "qty", "quantity", "quantite vendue"},
    "unit_price": {"prix_unitaire", "prix unitaire", "pu", "unit_price", "prix"},
}


@dataclass
class ParsedRow:
    sale_date: datetime
    raw_dish_name: str
    quantity_sold: float
    unit_price: float | None


@dataclass
class ParseResult:
    rows: list[ParsedRow] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _normalize_header(h: str) -> str:
    h = h.strip().lower()
    for accented, plain in (("é", "e"), ("è", "e"), ("ê", "e"), ("à", "a")):
        h = h.replace(accented, plain)
    return h


def _match_column(fieldnames: list[str], aliases: set[str]) -> str | None:
    normalized = {_normalize_header(f): f for f in fieldnames}
    for alias in aliases:
        key = _normalize_header(alias)
        if key in normalized:
            return normalized[key]
    return None


def _parse_date(raw: str) -> datetime:
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"date invalide {raw!r}")


def _detect_dialect(content: str) -> type[csv.Dialect]:
    """Les exports Excel en français utilisent souvent ';' (la virgule étant
    déjà le séparateur décimal). On détecte plutôt que d'imposer un format."""
    try:
        return csv.Sniffer().sniff(content[:4096], delimiters=",;\t")
    except csv.Error:
        return csv.excel


def parse_csv(content: str) -> ParseResult:
    result = ParseResult()
    reader = csv.DictReader(io.StringIO(content), dialect=_detect_dialect(content))
    if not reader.fieldnames:
        result.errors.append("Fichier CSV vide ou sans ligne d'en-tête.")
        return result

    date_col = _match_column(reader.fieldnames, HEADER_ALIASES["date"])
    dish_col = _match_column(reader.fieldnames, HEADER_ALIASES["dish"])
    qty_col = _match_column(reader.fieldnames, HEADER_ALIASES["quantity"])
    price_col = _match_column(reader.fieldnames, HEADER_ALIASES["unit_price"])

    missing = [
        label
        for label, col in [("date", date_col), ("plat", dish_col), ("quantité", qty_col)]
        if col is None
    ]
    if missing:
        result.errors.append(
            "Colonnes obligatoires manquantes : "
            + ", ".join(missing)
            + f" (en-têtes trouvés : {', '.join(reader.fieldnames)})"
        )
        return result

    for line_no, row in enumerate(reader, start=2):  # la ligne 1 est l'en-tête
        raw_date = (row.get(date_col) or "").strip()
        raw_dish = (row.get(dish_col) or "").strip()
        raw_qty = (row.get(qty_col) or "").strip()
        raw_price = (row.get(price_col) or "").strip() if price_col else ""

        if not raw_date or not raw_dish or not raw_qty:
            result.errors.append(f"Ligne {line_no} : champ obligatoire manquant, ignorée.")
            continue
        try:
            sale_date = _parse_date(raw_date)
        except ValueError as exc:
            result.errors.append(f"Ligne {line_no} : {exc}, ignorée.")
            continue
        try:
            quantity = float(raw_qty.replace(",", "."))
        except ValueError:
            result.errors.append(f"Ligne {line_no} : quantité invalide {raw_qty!r}, ignorée.")
            continue

        unit_price = None
        if raw_price:
            try:
                unit_price = float(raw_price.replace(",", "."))
            except ValueError:
                unit_price = None

        result.rows.append(
            ParsedRow(
                sale_date=sale_date,
                raw_dish_name=raw_dish,
                quantity_sold=quantity,
                unit_price=unit_price,
            )
        )
    return result


def _resolve_dish(db: Session, raw_name: str) -> models.Dish | None:
    """Résolution par nom (insensible à la casse/accents) puis par alias.

    Comparaison faite côté Python plutôt qu'en SQL : la carte d'un
    restaurant indépendant reste petite (quelques dizaines de plats), et ça
    évite les subtilités de collation SQLite sur les caractères accentués.
    """
    target = raw_name.strip().casefold()
    for dish in db.query(models.Dish).all():
        if dish.name.strip().casefold() == target:
            return dish
    alias = (
        db.query(models.DishAlias)
        .filter(models.DishAlias.raw_name == raw_name.strip())
        .one_or_none()
    )
    return alias.dish if alias else None


def apply_stock_for_line(db: Session, sale_line: models.SaleLine) -> None:
    """Décrémente le stock théorique de chaque ingrédient de la fiche technique du plat vendu."""
    if sale_line.stock_applied or sale_line.dish_id is None:
        return
    for recipe_line in sale_line.dish.recipe_lines:
        stock.record_movement(
            db,
            recipe_line.ingredient,
            models.MovementType.VENTE,
            -recipe_line.quantity * sale_line.quantity_sold,
            reference=f"import#{sale_line.sales_import_id}",
        )
    sale_line.stock_applied = True


def import_sales(
    db: Session, filename: str, content: str
) -> tuple[models.SalesImport, ParseResult]:
    parsed = parse_csv(content)

    sales_import = models.SalesImport(filename=filename, row_count=len(parsed.rows))
    db.add(sales_import)
    db.flush()

    unmatched = 0
    for row in parsed.rows:
        dish = _resolve_dish(db, row.raw_dish_name)
        sale_line = models.SaleLine(
            sales_import_id=sales_import.id,
            sale_date=row.sale_date,
            raw_dish_name=row.raw_dish_name,
            dish_id=dish.id if dish else None,
            quantity_sold=row.quantity_sold,
            unit_price=row.unit_price,
        )
        db.add(sale_line)
        db.flush()
        if dish:
            apply_stock_for_line(db, sale_line)
        else:
            unmatched += 1

    sales_import.unmatched_count = unmatched
    db.commit()
    db.refresh(sales_import)
    return sales_import, parsed


def unmatched_raw_names(db: Session, sales_import_id: int) -> list[str]:
    rows = (
        db.query(models.SaleLine.raw_dish_name)
        .filter(
            models.SaleLine.sales_import_id == sales_import_id,
            models.SaleLine.dish_id.is_(None),
        )
        .distinct()
        .all()
    )
    return [r[0] for r in rows]


def map_raw_name_to_dish(
    db: Session, raw_name: str, dish_id: int, remember_alias: bool = True
) -> int:
    """Rattache les lignes non résolues portant ce nom brut à un plat.

    Applique aussitôt la décrémentation de stock et mémorise l'alias pour
    que les imports futurs n'aient plus besoin de ce mappage manuel.
    Renvoie le nombre de lignes mises à jour.
    """
    dish = db.get(models.Dish, dish_id)
    if dish is None:
        raise ValueError(f"Plat introuvable : {dish_id}")

    if remember_alias:
        existing = (
            db.query(models.DishAlias)
            .filter(models.DishAlias.raw_name == raw_name)
            .one_or_none()
        )
        if existing is None:
            db.add(models.DishAlias(raw_name=raw_name, dish_id=dish_id))

    lines = (
        db.query(models.SaleLine)
        .filter(
            models.SaleLine.raw_dish_name == raw_name,
            models.SaleLine.dish_id.is_(None),
        )
        .all()
    )
    affected_imports = set()
    for line in lines:
        line.dish_id = dish_id
        db.flush()
        apply_stock_for_line(db, line)
        affected_imports.add(line.sales_import_id)

    for import_id in affected_imports:
        sales_import = db.get(models.SalesImport, import_id)
        sales_import.unmatched_count = len(unmatched_raw_names(db, import_id))

    db.commit()
    return len(lines)
