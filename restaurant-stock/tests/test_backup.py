"""F2 — sauvegarde/restauration (AC-F2-2, TC-F2-05).

Restauration réelle sur une base jetable : sauvegarde, mutation, restauration,
données de la « veille » retrouvées ; purge des sauvegardes > 30 jours.
"""
import importlib.util
import os
import time
from pathlib import Path

from sqlalchemy import create_engine, text

from app.database import Base

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_backup_module():
    spec = importlib.util.spec_from_file_location("backup_script", BASE_DIR / "scripts" / "backup.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_live_db(path: Path):
    engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO ingredients (name, unit, unit_cost, storage_zone, current_theoretical_stock,"
            " is_active, created_at, updated_at) VALUES ('Farine','g',0.0012,'sec',1000,1,"
            "'2026-01-01 00:00:00','2026-01-01 00:00:00')"
        ))
    engine.dispose()
    return engine


def test_tc_f2_05_backup_then_restore_brings_back_yesterdays_data(tmp_path, monkeypatch):
    backup = _load_backup_module()
    live = tmp_path / "live.db"
    _make_live_db(live)
    monkeypatch.setattr(backup, "DATABASE_URL", f"sqlite:///{live}")
    monkeypatch.setattr(backup, "BACKUP_DIR", tmp_path / "backups")

    started = time.monotonic()
    dest = backup.backup()
    assert dest.exists() and backup.verify(dest)

    engine = create_engine(f"sqlite:///{live}")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM ingredients"))
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingredients")).scalar() == 0
    engine.dispose()

    backup.restore(dest)
    elapsed = time.monotonic() - started
    assert elapsed < 15 * 60  # TC-F2-05 : restauration chronométrée < 15 min

    engine = create_engine(f"sqlite:///{live}")
    with engine.connect() as conn:
        assert conn.execute(text("SELECT name FROM ingredients")).scalar() == "Farine"
    engine.dispose()
    # Une copie de sécurité de la base remplacée a été prise avant restauration.
    assert list((tmp_path / "backups").glob("pre_restore_*.db"))


def test_prune_removes_backups_older_than_retention(tmp_path, monkeypatch):
    backup = _load_backup_module()
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setattr(backup, "BACKUP_DIR", backup_dir)
    old = backup_dir / "old.db"
    recent = backup_dir / "recent.db"
    old.write_bytes(b"")
    recent.write_bytes(b"")
    forty_days_ago = time.time() - 40 * 86400
    os.utime(old, (forty_days_ago, forty_days_ago))

    removed = backup.prune()

    assert removed == [old]
    assert not old.exists() and recent.exists()


def test_verify_rejects_database_missing_expected_tables(tmp_path, monkeypatch):
    backup = _load_backup_module()
    bogus = tmp_path / "bogus.db"
    create_engine(f"sqlite:///{bogus}").connect().close()
    assert backup.verify(bogus) is False
