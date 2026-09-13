"""Execute the first autonomous discovery cycle."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from autonomous_research import run_discovery_cycle  # noqa: E402

ticket = run_discovery_cycle(ROOT / "data/nasdaq_composite_daily.txt",
                             ROOT / "research/tickets", ROOT / "research/memory.jsonl")
print(json.dumps(ticket.to_dict(), indent=2, sort_keys=True))
