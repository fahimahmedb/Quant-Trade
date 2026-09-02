"""F2 — export/réimport des données et journal d'erreurs (AC-F2-4)."""
import io
import zipfile

from app import models, seed
from app.services import data_export


def _export(client) -> bytes:
    r = client.get("/settings/export")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    assert "attachment" in r.headers["content-disposition"]
    return r.content


def test_export_contains_one_csv_per_table_with_data(seeded_client):
    client = seeded_client.client
    archive = zipfile.ZipFile(io.BytesIO(_export(client)))

    expected = {f"{name}.csv" for name, _, _ in data_export.EXPORTS}
    assert expected <= set(archive.namelist())

    ingredients = archive.read("ingredients.csv").decode("utf-8-sig")
    assert "Farine" in ingredients and "Steak haché" in ingredients
    assert ingredients.splitlines()[0].startswith("id;name;unit")
    assert len(ingredients.strip().splitlines()) == 10  # en-tête + 9 ingrédients


def test_export_never_contains_the_password_hash(seeded_client):
    client = seeded_client.client
    archive = zipfile.ZipFile(io.BytesIO(_export(client)))
    for name in archive.namelist():
        assert "scrypt$" not in archive.read(name).decode("utf-8-sig")


def _fresh_install_session():
    """Base vierge, indépendante du client de test : simule une installation neuve."""
    from sqlalchemy.orm import sessionmaker

    from tests.conftest import _memory_engine

    return sessionmaker(bind=_memory_engine())


# AC-F2-4 ------------------------------------------------------------------
def test_ac_f2_4_export_can_be_reimported_to_rebuild_catalog(seeded_client):
    """Export d'une installation, réimport dans une installation neuve :
    ingrédients et fiches techniques sont reconstitués à l'identique."""
    payload = _export(seeded_client.client)

    with _fresh_install_session()() as fresh:
        assert fresh.query(models.Ingredient).count() == 0
        summary = data_export.import_catalog(fresh, payload)

        assert summary == {"ingredients": 9, "dishes": 5, "recipe_lines": 12}
        farine = fresh.query(models.Ingredient).filter_by(name="Farine").one()
        assert farine.unit == models.Unit.GRAMME
        assert farine.unit_cost == 0.0012
        assert farine.storage_zone == models.StorageZone.SEC
        assert farine.current_theoretical_stock == 20000

        burger = fresh.query(models.Dish).filter_by(name="Burger maison").one()
        grammages = {line.ingredient.name: line.quantity for line in burger.recipe_lines}
        assert grammages == {"Steak haché": 150, "Pain burger": 1, "Salade": 20, "Tomate": 30}
        assert burger.food_cost == seed.INGREDIENTS[0][2] * 150 + 0.35 + 0.004 * 20 + 0.003 * 30


def test_import_refuses_to_overwrite_an_existing_catalog(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    payload = _export(client)

    r = client.post("/settings/import", files={"file": ("export.zip", payload, "application/zip")})
    assert "pas vide" in r.text  # apostrophes échappées en HTML : on cible un fragment sûr
    with sessions() as db:
        assert db.query(models.Ingredient).count() == 9  # inchangé


def test_import_rejects_a_file_that_is_not_an_export(app_client):
    client = app_client.client
    r = client.post("/settings/import", files={"file": ("bidon.zip", b"pas un zip", "application/zip")})
    assert "pas une archive ZIP" in r.text


def test_import_through_the_screen_rebuilds_the_catalog(seeded_client, app_client):
    """L'écran d'import restaure bien le catalogue quand la base est vierge."""
    payload = _export(seeded_client.client)
    with seeded_client.session_factory() as db:  # on vide le catalogue existant
        db.query(models.RecipeIngredient).delete()
        db.query(models.CountLine).delete()
        db.query(models.StockMovement).delete()
        db.query(models.SaleLine).delete()
        db.query(models.DishAlias).delete()
        db.query(models.Dish).delete()
        db.query(models.Ingredient).delete()
        db.commit()

    r = app_client.client.post(
        "/settings/import", files={"file": ("export.zip", payload, "application/zip")}
    )
    assert "Import réussi" in r.text
    with app_client.session_factory() as db:
        assert db.query(models.Ingredient).count() == 9
        assert db.query(models.RecipeIngredient).count() == 12


# Journal des erreurs ------------------------------------------------------
def test_unhandled_error_is_logged_without_being_hidden(app_client):
    """L'erreur reste visible (elle remonte) mais laisse une trace consultable."""
    import pytest
    from fastapi import APIRouter

    from app.main import app

    router = APIRouter()

    @router.get("/boom-test")
    def boom():
        raise RuntimeError("panne simulée")

    app.include_router(router)
    try:
        with pytest.raises(RuntimeError):
            app_client.client.get("/boom-test")
    finally:
        app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != "/boom-test"]

    with app_client.session_factory() as db:
        logged = db.query(models.ErrorLog).one()
    assert logged.error_type == "RuntimeError"
    assert logged.message == "panne simulée"
    assert logged.path == "/boom-test" and logged.method == "GET"
    assert "RuntimeError" in logged.traceback

    page = app_client.client.get("/settings/errors").text
    assert "panne simulée" in page and "/boom-test" in page


def test_error_log_screen_is_empty_by_default(app_client):
    assert "Aucune erreur enregistrée" in app_client.client.get("/settings/errors").text
