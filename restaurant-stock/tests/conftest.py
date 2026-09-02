import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db


def _memory_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from app import models  # noqa: F401  (enregistre les tables sur Base)

    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session():
    engine = _memory_engine()
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@dataclass
class ClientAndDb:
    client: TestClient
    session_factory: sessionmaker


TEST_EMAIL = "chef@bistrot.fr"
TEST_PASSWORD = "motdepasse123"


@pytest.fixture()
def anonymous_client():
    """Client HTTP sans session : sert aux tests d'authentification (F2)."""
    from app.main import app

    engine = _memory_engine()
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # Le middleware de session n'utilise pas les dépendances FastAPI : on lui
    # injecte la fabrique de sessions du test.
    app.state.session_factory = testing_session_local
    try:
        yield ClientAndDb(TestClient(app, follow_redirects=True), testing_session_local)
    finally:
        app.dependency_overrides.clear()
        app.state.session_factory = None
        engine.dispose()


@pytest.fixture()
def app_client(anonymous_client):
    """Client connecté au compte de test : les écrans métier sont protégés (F2)."""
    from app.services import auth

    with anonymous_client.session_factory() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD,
                            restaurant_name="Bistrot de test")
    response = anonymous_client.client.post(
        "/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD, "next": "/"}
    )
    assert response.status_code < 400, "connexion du client de test impossible"
    return anonymous_client


@pytest.fixture()
def seeded_client(app_client):
    """Comme app_client, avec le jeu de démo (9 ingrédients, 5 fiches) chargé."""
    from app import seed

    with app_client.session_factory() as db:
        seed.seed_demo(db)
    return app_client
