"""Export et réimport des données de l'établissement (Specs V2, F2).

Réversibilité : le restaurateur doit pouvoir repartir avec ses données s'il
arrête. Un ZIP d'un CSV par table, lisible dans n'importe quel tableur, et
un réimport du catalogue (ingrédients + fiches techniques) pour vérifier
que l'export n'est pas un fichier mort (AC-F2-4).
"""
import csv
import io
import zipfile
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import recipes

# (nom du fichier, modèle, colonnes exportées). Le hachage du mot de passe
# et les jetons ne sortent jamais : l'export circule par e-mail ou clé USB.
EXPORTS = [
    ("ingredients", models.Ingredient,
     ["id", "name", "unit", "unit_cost", "storage_zone", "current_theoretical_stock",
      "alert_threshold", "is_active"]),
    ("plats", models.Dish, ["id", "name", "is_active"]),
    ("fiches_techniques", models.RecipeIngredient, ["id", "dish_id", "ingredient_id", "quantity"]),
    ("alias_plats", models.DishAlias, ["id", "raw_name", "dish_id"]),
    ("ventes", models.SaleLine,
     ["id", "sales_import_id", "sale_date", "raw_dish_name", "dish_id", "quantity_sold", "unit_price"]),
    ("imports_ventes", models.SalesImport, ["id", "filename", "imported_at", "row_count", "unmatched_count"]),
    ("mouvements_stock", models.StockMovement,
     ["id", "ingredient_id", "movement_type", "quantity_delta", "resulting_stock", "reference", "created_at"]),
    ("comptages", models.CountSession, ["id", "started_at", "ended_at", "counted_by"]),
    ("lignes_comptage", models.CountLine,
     ["id", "count_session_id", "ingredient_id", "theoretical_quantity", "counted_quantity",
      "variance_reason", "confirmed_at"]),
    ("receptions", models.DeliveryReceipt, ["id", "received_on", "supplier", "note", "created_at"]),
    ("lignes_reception", models.DeliveryLine,
     ["id", "receipt_id", "ingredient_id", "quantity", "unit_price", "previous_unit_price"]),
    ("historique_prix", models.PriceHistory,
     ["id", "ingredient_id", "unit_price", "recorded_at", "supplier", "receipt_id"]),
    ("suggestions_commande", models.OrderSuggestionLine,
     ["id", "batch_id", "ingredient_id", "current_stock", "avg_daily_consumption",
      "threshold_used", "suggested_quantity", "final_quantity", "decision", "validated_at"]),
]


def _cell(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return getattr(value, "value", value)


def export_zip(db: Session) -> bytes:
    """ZIP contenant un CSV par table (UTF-8 avec BOM, lisible par Excel)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, model, columns in EXPORTS:
            text = io.StringIO()
            writer = csv.writer(text, delimiter=";")
            writer.writerow(columns)
            for row in db.query(model).order_by(model.id).all():
                writer.writerow([_cell(getattr(row, column)) for column in columns])
            archive.writestr(f"{name}.csv", text.getvalue().encode("utf-8-sig"))
    return buffer.getvalue()


def export_filename(now: datetime | None = None) -> str:
    return f"export_stock_{(now or datetime.now()):%Y%m%d_%H%M}.zip"


class ImportError_(ValueError):
    """Export illisible ou incomplet."""


def _read_csv(archive: zipfile.ZipFile, name: str) -> list[dict]:
    try:
        raw = archive.read(f"{name}.csv").decode("utf-8-sig")
    except KeyError as exc:
        raise ImportError_(f"Fichier {name}.csv absent de l'archive.") from exc
    return list(csv.DictReader(io.StringIO(raw), delimiter=";"))


def import_catalog(db: Session, payload: bytes) -> dict:
    """Reconstitue ingrédients et fiches techniques depuis un export (AC-F2-4).

    Ne restaure que le catalogue, pas l'historique : c'est ce dont on a besoin
    pour repartir sur une installation neuve. Refuse d'écraser un catalogue
    existant, pour qu'un import ne puisse pas effacer des données réelles.
    """
    if db.query(models.Ingredient).count() or db.query(models.Dish).count():
        raise ImportError_(
            "Le catalogue n'est pas vide : l'import ne peut pas écraser des "
            "ingrédients ou des fiches techniques existants."
        )
    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except zipfile.BadZipFile as exc:
        raise ImportError_("Fichier illisible : ce n'est pas une archive ZIP d'export.") from exc

    ingredient_ids: dict[str, int] = {}
    for row in _read_csv(archive, "ingredients"):
        ingredient = models.Ingredient(
            name=row["name"],
            unit=models.Unit(row["unit"]),
            unit_cost=float(row["unit_cost"] or 0),
            storage_zone=models.StorageZone(row["storage_zone"]),
            current_theoretical_stock=float(row["current_theoretical_stock"] or 0),
            alert_threshold=float(row["alert_threshold"]) if row["alert_threshold"] else None,
            is_active=row["is_active"] in ("True", "1", "true"),
        )
        db.add(ingredient)
        db.flush()
        ingredient_ids[row["id"]] = ingredient.id

    dish_ids: dict[str, int] = {}
    for row in _read_csv(archive, "plats"):
        dish = models.Dish(name=row["name"], is_active=row["is_active"] in ("True", "1", "true"))
        db.add(dish)
        db.flush()
        dish_ids[row["id"]] = dish.id

    lines_by_dish: dict[int, list[recipes.RecipeLineInput]] = {}
    for row in _read_csv(archive, "fiches_techniques"):
        dish_id = dish_ids.get(row["dish_id"])
        ingredient_id = ingredient_ids.get(row["ingredient_id"])
        if dish_id is None or ingredient_id is None:
            continue
        lines_by_dish.setdefault(dish_id, []).append(
            recipes.RecipeLineInput(ingredient_id=ingredient_id, quantity=float(row["quantity"]))
        )
    for dish_id, lines in lines_by_dish.items():
        for line in lines:
            db.add(models.RecipeIngredient(
                dish_id=dish_id, ingredient_id=line.ingredient_id, quantity=line.quantity
            ))

    db.commit()
    return {
        "ingredients": len(ingredient_ids),
        "dishes": len(dish_ids),
        "recipe_lines": sum(len(v) for v in lines_by_dish.values()),
    }
