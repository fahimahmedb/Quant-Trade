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


@pytest.fixture()
def app_client():
    """Client HTTP sur l'appli complète, base SQLite en mémoire isolée par test."""
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
    try:
        yield ClientAndDb(TestClient(app, follow_redirects=True), testing_session_local)
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture()
def seeded_client(app_client):
    """Comme app_client, avec le jeu de démo (9 ingrédients, 5 fiches) chargé."""
    from app import seed

    with app_client.session_factory() as db:
        seed.seed_demo(db)
    return app_client
