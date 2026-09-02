"""F2 — migrations de schéma versionnées (AC-F2-3, TC-F2-04).

Montée puis descente de version sur une base temporaire, données préservées
par une montée « à vide », et estampillage automatique d'une base v1 créée
par create_all (installation existante).
"""
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from app.database import Base, init_db

BASE_DIR = Path(__file__).resolve().parent.parent

INSERT_FARINE = text(
    "INSERT INTO ingredients (name, unit, unit_cost, storage_zone, current_theoretical_stock,"
    " alert_threshold, is_active, created_at, updated_at)"
    " VALUES ('Farine', 'g', 0.0012, 'sec', 1000, NULL, 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00')"
)


def _cfg() -> Config:
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    return cfg


def _tables(engine) -> set[str]:
    return set(inspect(engine).get_table_names())


def _run(engine, fn):
    cfg = _cfg()
    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        fn(cfg)


def test_tc_f2_04_upgrade_then_downgrade_on_a_copy(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'migr.db'}")

    _run(engine, lambda cfg: command.upgrade(cfg, "head"))
    tables = _tables(engine)
    assert {"ingredients", "dishes", "stock_movements", "count_sessions", "alembic_version"} <= tables

    with engine.begin() as conn:
        conn.execute(INSERT_FARINE)

    # Montée à vide (déjà à jour) : données préservées.
    _run(engine, lambda cfg: command.upgrade(cfg, "head"))
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingredients")).scalar() == 1

    _run(engine, lambda cfg: command.downgrade(cfg, "base"))
    assert "ingredients" not in _tables(engine)

    _run(engine, lambda cfg: command.upgrade(cfg, "head"))
    assert "ingredients" in _tables(engine)


def test_migrations_match_models_exactly(tmp_path):
    """Dérive modèle/migration = échec : une table ou colonne ajoutée aux
    modèles sans migration est détectée ici, pas en production."""
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    engine = create_engine(f"sqlite:///{tmp_path / 'drift.db'}")
    _run(engine, lambda cfg: command.upgrade(cfg, "head"))
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn, opts={"compare_type": True, "render_as_batch": True})
        diff = compare_metadata(ctx, Base.metadata)
    assert diff == [], diff


def test_init_db_stamps_legacy_create_all_database_without_losing_data(tmp_path):
    """Base d'un pilote déjà en service sous la v1 (create_all, sans alembic_version) :
    init_db doit l'estampiller puis la migrer jusqu'à head sans perdre de données.

    On reconstitue le schéma v1 réel en jouant la migration baseline puis en
    retirant alembic_version — plus fidèle qu'un create_all des modèles actuels,
    qui contiendrait déjà les tables des versions suivantes."""
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}", connect_args={"check_same_thread": False})
    baseline = ScriptDirectory.from_config(_cfg()).get_base()
    _run(engine, lambda cfg: command.upgrade(cfg, baseline))
    with engine.begin() as conn:
        conn.execute(INSERT_FARINE)
        conn.execute(text("DROP TABLE alembic_version"))
    assert "alembic_version" not in _tables(engine)
    assert "delivery_receipts" not in _tables(engine)  # schéma v1 : F1 pas encore là

    init_db(target_engine=engine)

    assert "alembic_version" in _tables(engine)
    assert "delivery_receipts" in _tables(engine)  # migré jusqu'à head
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingredients")).scalar() == 1
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert version == ScriptDirectory.from_config(_cfg()).get_current_head()


def test_init_db_on_empty_database_creates_full_schema(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}", connect_args={"check_same_thread": False})
    init_db(target_engine=engine)
    assert {"ingredients", "dishes", "alembic_version"} <= _tables(engine)
