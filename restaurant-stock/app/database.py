import sys

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import BASE_DIR, DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _alembic_config():
    from alembic.config import Config

    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    return cfg


def init_db(target_engine=None) -> None:
    """Amène la base au dernier schéma via Alembic (F2 : plus de create_all).

    Une base créée par la v1 (`create_all`, sans table alembic_version) est
    d'abord estampillée à la révision de base, puis migrée normalement :
    la mise à jour d'une installation existante ne perd aucune donnée.
    """
    from alembic import command
    from alembic.script import ScriptDirectory

    from app import models  # noqa: F401  (enregistre les modèles sur Base)

    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    target_engine = target_engine or engine
    cfg = _alembic_config()

    with target_engine.connect() as conn:
        tables = set(inspect(conn).get_table_names())
    legacy_v1_schema = "ingredients" in tables and "alembic_version" not in tables

    with target_engine.begin() as conn:
        cfg.attributes["connection"] = conn
        if legacy_v1_schema:
            command.stamp(cfg, ScriptDirectory.from_config(cfg).get_base())
        command.upgrade(cfg, "head")
