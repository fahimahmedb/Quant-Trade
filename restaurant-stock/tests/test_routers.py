"""Tests d'intégration légers sur les routes HTTP.

Complètent les tests de service (logique métier) en couvrant des erreurs
utilisateur plausibles qui ne doivent jamais faire planter l'application
avec une 500 brute (ex. nom en double) mais un message explicite.
"""
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.main import app


@dataclass
class ClientAndDb:
    client: TestClient
    session_factory: sessionmaker


@pytest.fixture()
def app_client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield ClientAndDb(TestClient(app, follow_redirects=True), testing_session_local)
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _create_ingredient(client, name, **overrides):
    data = {
        "name": name, "unit": "g", "unit_cost": "0.002",
        "storage_zone": "sec", "current_theoretical_stock": "1000", "alert_threshold": "",
    }
    data.update(overrides)
    return client.post("/ingredients/new", data=data)


def test_create_ingredient_then_recipe_shows_food_cost(app_client):
    client = app_client.client
    _create_ingredient(client, "Farine")
    assert "Farine" in client.get("/ingredients").text

    with app_client.session_factory() as db:
        ingredient_id = db.query(models.Ingredient).filter_by(name="Farine").one().id

    r = client.post("/recipes/new", data={
        "name": "Pain", "is_active": "true",
        "ingredient_id": [str(ingredient_id)], "quantity": ["200"],
    })
    assert r.status_code == 200
    page = client.get("/recipes").text
    assert "Pain" in page and "coût matière" in page


def test_duplicate_ingredient_name_shows_friendly_error_not_500(app_client):
    client = app_client.client
    _create_ingredient(client, "Farine")
    r = _create_ingredient(client, "Farine")
    assert r.status_code == 200
    assert "existe déjà" in r.text


def test_renaming_ingredient_to_existing_name_shows_friendly_error(app_client):
    client = app_client.client
    _create_ingredient(client, "Farine")
    _create_ingredient(client, "Sucre")
    with app_client.session_factory() as db:
        sucre_id = db.query(models.Ingredient).filter_by(name="Sucre").one().id

    r = client.post(f"/ingredients/{sucre_id}/edit", data={
        "name": "Farine", "unit": "g", "unit_cost": "0.003",
        "storage_zone": "sec", "current_theoretical_stock": "500", "alert_threshold": "",
        "is_active": "true",
    })
    assert r.status_code == 200
    assert "existe déjà" in r.text


def test_duplicate_dish_name_shows_friendly_error_not_500(app_client):
    client = app_client.client
    payload = {"name": "Burger", "is_active": "true", "ingredient_id": [], "quantity": []}
    client.post("/recipes/new", data=payload)
    r = client.post("/recipes/new", data=payload)
    assert r.status_code == 200
    assert "existe déjà" in r.text


def test_recipe_form_with_duplicate_ingredient_rows_merges_not_crashes(app_client):
    client = app_client.client
    _create_ingredient(client, "Sel")
    with app_client.session_factory() as db:
        sel_id = db.query(models.Ingredient).filter_by(name="Sel").one().id

    r = client.post("/recipes/new", data={
        "name": "Plat salé", "is_active": "true",
        "ingredient_id": [str(sel_id), str(sel_id)],
        "quantity": ["5", "3"],
    })
    assert r.status_code == 200
    assert "existe déjà" not in r.text

    with app_client.session_factory() as db:
        dish = db.query(models.Dish).filter_by(name="Plat salé").one()
        assert len(dish.recipe_lines) == 1
        assert dish.recipe_lines[0].quantity == 8


def test_mapping_unmatched_dish_to_new_name_that_already_exists_reuses_it(app_client):
    client = app_client.client
    payload = {"name": "Burger", "is_active": "true", "ingredient_id": [], "quantity": []}
    client.post("/recipes/new", data=payload)

    csv_content = "date,plat,quantite\n2026-08-01,Plat mystere,1\n"
    r = client.post("/sales/import", files={"file": ("export.csv", csv_content, "text/csv")})
    import_path = r.url.path

    # On tape "Burger" comme "nouveau" nom alors qu'il existe déjà : ne doit pas planter.
    r = client.post(f"{import_path}/map", data={
        "raw_name": "Plat mystere", "dish_id": "", "new_dish_name": "Burger",
    })
    assert r.status_code == 200

    with app_client.session_factory() as db:
        assert db.query(models.Dish).filter_by(name="Burger").count() == 1
