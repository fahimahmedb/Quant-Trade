"""Sauvegarde / restauration de la base (Specs V2, F2).

    python scripts/backup.py backup     # sauvegarde + vérification + purge
    python scripts/backup.py restore <fichier>
    python scripts/backup.py list

Utilise l'API `sqlite3.Connection.backup` : copie cohérente même si
l'application tourne, contrairement à un simple `cp`. Une sauvegarde non
vérifiée ne vaut rien, donc `backup()` relit systématiquement le fichier
produit avant de le déclarer bon.
"""
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.config import DATABASE_URL  # noqa: E402

BACKUP_DIR = BASE_DIR / "data" / "backups"
RETENTION_DAYS = 30
EXPECTED_TABLES = {"ingredients", "dishes", "recipe_ingredients", "stock_movements",
                   "count_sessions", "count_lines", "sale_lines"}


def _db_path(database_url: str | None = None) -> Path:
    url = database_url or DATABASE_URL
    if not url.startswith("sqlite:///"):
        raise SystemExit(f"Sauvegarde SQLite uniquement, URL non gérée : {url}")
    return Path(url.removeprefix("sqlite:///"))


def backup() -> Path:
    """Copie cohérente et vérifiée de la base ; renvoie le chemin produit."""
    source = _db_path()
    if not source.exists():
        raise SystemExit(f"Base introuvable : {source}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dest = BACKUP_DIR / f"{datetime.now():%Y%m%d_%H%M%S}.db"

    with sqlite3.connect(source) as src, sqlite3.connect(dest) as dst:
        src.backup(dst)
    if not verify(dest):
        dest.unlink(missing_ok=True)
        raise SystemExit("Sauvegarde produite mais illisible — annulée.")
    return dest


def verify(path: Path) -> bool:
    """Une sauvegarde est valable si SQLite la relit et qu'elle porte le schéma métier."""
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
            if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                return False
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    except sqlite3.DatabaseError:
        return False
    return EXPECTED_TABLES <= tables


def restore(path: Path) -> Path:
    """Remet la base à l'état d'une sauvegarde, après copie de sécurité de l'actuelle."""
    path = Path(path)
    if not verify(path):
        raise SystemExit(f"Sauvegarde invalide, restauration refusée : {path}")

    target = _db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if target.exists():
        safety = BACKUP_DIR / f"pre_restore_{datetime.now():%Y%m%d_%H%M%S}.db"
        with sqlite3.connect(target) as src, sqlite3.connect(safety) as dst:
            src.backup(dst)

    with sqlite3.connect(path) as src, sqlite3.connect(target) as dst:
        src.backup(dst)
    return target


def prune(retention_days: int = RETENTION_DAYS) -> list[Path]:
    """Supprime les sauvegardes plus vieilles que la rétention ; renvoie la liste."""
    if not BACKUP_DIR.exists():
        return []
    cutoff = time.time() - retention_days * 86400
    removed = []
    for candidate in sorted(BACKUP_DIR.glob("*.db")):
        if candidate.stat().st_mtime < cutoff:
            candidate.unlink()
            removed.append(candidate)
    return removed


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else "backup"
    if command == "backup":
        started = time.monotonic()
        dest = backup()
        removed = prune()
        print(f"Sauvegarde vérifiée : {dest} ({dest.stat().st_size / 1024:.0f} Ko, "
              f"{time.monotonic() - started:.1f} s)")
        if removed:
            print(f"Purge : {len(removed)} sauvegarde(s) de plus de {RETENTION_DAYS} jours supprimée(s).")
    elif command == "restore":
        if len(argv) < 3:
            print("Usage : python scripts/backup.py restore <fichier>")
            return 2
        started = time.monotonic()
        target = restore(Path(argv[2]))
        print(f"Restauré dans {target} en {time.monotonic() - started:.1f} s.")
    elif command == "list":
        for candidate in sorted(BACKUP_DIR.glob("*.db")) if BACKUP_DIR.exists() else []:
            state = "ok" if verify(candidate) else "ILLISIBLE"
            print(f"{candidate.name}  {candidate.stat().st_size / 1024:8.0f} Ko  {state}")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
