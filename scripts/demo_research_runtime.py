"""Reproducible run -> stop -> restart demonstration using an isolated directory."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from autonomous_research.orchestrator import ResearchCampaign  # noqa: E402


def emit(event: str, campaign: ResearchCampaign) -> None:
    print(json.dumps({"event": event, "status": campaign.state.status,
                      "cycles": campaign.state.cycles_completed,
                      "last_ticket": campaign.state.last_completed_ticket_id,
                      "lesson": campaign.state.latest_lesson,
                      "next_action": campaign.state.next_action,
                      "queue": campaign.queue.counts()}, sort_keys=True))


with tempfile.TemporaryDirectory(prefix="quant-runtime-demo-") as directory:
    demo = Path(directory)
    (demo / "data").mkdir()
    (demo / "research").mkdir()
    shutil.copy2(ROOT / "data" / "nasdaq_composite_daily.txt", demo / "data")
    shutil.copy2(ROOT / "research" / "opportunity_map.json", demo / "research")
    (demo / "research" / "memory.jsonl").write_text(
        '{"record_type":"demo_initialization","status":"ACTIVE"}\n', encoding="utf-8")

    first_process = ResearchCampaign(demo, "restart-demo")
    first_process.seed_from_opportunity_map()
    emit("campaign_starts_queue_loaded", first_process)
    first_process.run_once()
    emit("worker_executed_ticket_closed_lesson_stored", first_process)
    first_process.run_once()
    emit("runtime_idles_with_blocked_next_research", first_process)

    del first_process  # Explicit process-lifetime boundary for the demonstration.
    restarted_process = ResearchCampaign(demo, "restart-demo")
    emit("process_restarted_state_recovered", restarted_process)
    restarted_process.run_once()
    emit("no_duplicate_work_campaign_remains_alive", restarted_process)
