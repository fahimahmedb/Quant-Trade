"""One-shot test-fixture repair for calendar-valid synthetic session dates."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "tests" / "test_quant_system.py"
text = path.read_text(encoding="utf-8")
old = '''def session_date(index: int) -> str:\n    year, remainder = 2020 + (index // 360), index % 360\n    return f"{year}-{(remainder // 30) + 1:02d}-{(remainder % 30) + 1:02d}"\n'''
new = '''def session_date(index: int) -> str:\n    # Real calendar dates keep the synthetic fixture compatible with the same\n    # Data Plane validation imposed on market data. Weekends are harmless here:\n    # this fixture proves mechanics, not an exchange calendar.\n    return (datetime(2020, 1, 1) + timedelta(days=index)).date().isoformat()\n'''
if text.count(old) != 1:
    raise SystemExit("expected fixture session_date helper exactly once")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
for relative in ("scripts/repair_fixture_dates.py", ".github/workflows/repair-fixture-dates.yml"):
    target = root / relative
    if target.exists():
        target.unlink()
