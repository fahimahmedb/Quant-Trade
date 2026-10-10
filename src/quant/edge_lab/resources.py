"""One fixed synthetic capacity probe; never read archives or accept price inputs."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from .engine import budget_check, timestamp
from .legacy import FROZEN_COMMIT, FREEZE_SHA256, PREFIX, _git
from .store import Refused

QUESTION = "build:eurusd-technical-grid:synthetic-resource-envelope"
WORKER = '''
import json, math, resource, sys, time
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
def offline(event, args):
    if event.startswith("socket.") or event in ("subprocess.Popen", "os.system"):
        raise RuntimeError("Synthetic worker has no network or child-process permission")
sys.addaudithook(offline)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import Engine, WARMUP_START, START, END
from safety_kernel import Quote
cpu, wall = time.process_time(), time.monotonic()
e = Engine()
count = 0
for ms in range(WARMUP_START, END, 60000):
    mid = 1.10 + .001*math.sin(count*.17) + .0002*math.cos(count*.031)
    e.feed(Quote(ms, mid-.00005, mid+.00005))
    count += 1
# Include the original final calendar pass/statistics, but discard all synthetic P&L.
discarded = e.finalize()
del discarded
print(json.dumps({"fixture": "FIXED_ONE_MINUTE_FULL_FROZEN_CALENDAR_V1",
    "groups": count, "first_ms": WARMUP_START, "end_exclusive_ms": END,
    "outcome_start_ms": START, "cost_paths": len(e.paths),
    "cpu_seconds": time.process_time()-cpu, "wall_seconds": time.monotonic()-wall,
    "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
    "rss_unit": "Linux ru_maxrss KiB converted to bytes", "finalize_completed": True}))
'''


def probe_eurusd(lab, repository, claim_id):
    started = time.monotonic()
    with lab.store.lock():
        control = lab.store.control()
        if control["paused"]:
            raise Refused("PAUSED: no resource probe")
        state = lab.store.read()
        budget_check(state, control)
        if control["limits"]["cpu_seconds_total"] is not None:
            raise Refused("BUDGET_UNMEASURED: total resource-job CPU accounting unavailable")
    q = state["decisions"].get(QUESTION, {})
    if q.get("status") != "RESEARCHING" or not claim_id or q.get("claim_id") != claim_id:
        raise Refused("Exact resource construction claim required")
    elapsed_lease = (datetime.now(timezone.utc)-timestamp(q["claimed_at"])).total_seconds()
    if elapsed_lease > q["lease_seconds"]:
        raise Refused("Expired claim: reconcile the saved probe receipt")
    if sys.version_info[:2] != (3, 12) or sys.platform != "linux":
        raise Refused("Synthetic resource probe requires qualified Linux/Python 3.12")
    deadline = started + control["limits"]["job_wall_seconds"]
    ceiling, consumed = control["limits"]["metadata_bytes_per_tick"], 0

    def blob(ref, path):
        nonlocal consumed
        spec = ref+":"+path
        size = int(_git(repository, ["cat-file", "-s", spec], deadline))
        if size < 0 or consumed+size > ceiling:
            raise Refused("Resource metadata ceiling before body read")
        value = _git(repository, ["show", spec], deadline)
        if len(value) != size:
            raise Refused("Resource metadata changed during read")
        consumed += size
        return value

    if (json.loads(blob("HEAD", "research/edge_lab/STATE.json")) != state or
            json.loads(blob("HEAD", "research/edge_lab/CONTROL.json")) != control):
        raise Refused("Publish exact resource claim/control with CAS first")
    freeze_bytes = blob(FROZEN_COMMIT, PREFIX+"freeze.json")
    if hashlib.sha256(freeze_bytes).hexdigest() != FREEZE_SHA256:
        raise Refused("Immutable freeze mismatch")
    freeze = json.loads(freeze_bytes)
    code = {}
    for name in ("engine.py", "safety_kernel.py"):
        code[name] = blob(FROZEN_COMMIT, PREFIX+name)
        if hashlib.sha256(code[name]).hexdigest() != freeze["files"][name]:
            raise Refused("Immutable synthetic engine code mismatch")
    # Timezone data influences even synthetic rollover; qualify these bytes again.
    for path, expected in freeze["runtime_data"].items():
        size = Path(path).stat().st_size
        if consumed+size > ceiling:
            raise Refused("Timezone metadata ceiling before body read")
        data = Path(path).read_bytes()
        consumed += len(data)
        if len(data) != size or hashlib.sha256(data).hexdigest() != expected:
            raise Refused("Immutable timezone data mismatch")
    remaining_lease = q["lease_seconds"] - (datetime.now(timezone.utc)-timestamp(q["claimed_at"])).total_seconds()
    child_budget = min(90, deadline-time.monotonic()-2, remaining_lease-2)
    if child_budget <= 0:
        raise Refused("No measurable time remains for the synthetic probe")
    with tempfile.TemporaryDirectory(prefix="quant-synthetic-only-") as directory:
        root = Path(directory)
        for name, data in code.items():
            (root/name).write_bytes(data)
        (root/"fixture.py").write_text(WORKER)
        try:
            child = subprocess.run([sys.executable, "-I", "-B", str(root/"fixture.py")],
                cwd=root, capture_output=True, timeout=child_budget)
            observation = json.loads(child.stdout) if child.returncode == 0 else {
                "status": "SYNTHETIC_LIMIT_OR_SOFTWARE_FAILURE", "returncode": child.returncode}
        except subprocess.TimeoutExpired:
            observation = {"status": "SYNTHETIC_WALL_LIMIT_REACHED", "wall_limit_seconds": child_budget}
    return {"schema": 1, "scope": "SYNTHETIC_RESOURCE_PROBE_NOT_MARKET_LOOK",
        "claim_id": claim_id, "frozen_commit": FROZEN_COMMIT, "freeze_sha256": FREEZE_SHA256,
        "worker_sha256": hashlib.sha256(WORKER.encode()).hexdigest(),
        "observation": observation, "metadata_body_bytes": consumed,
        "operation_wall_seconds": time.monotonic()-started,
        "worker_limits": {"cpu_seconds": 60, "address_space_bytes": 256*1024*1024,
                          "wall_seconds": child_budget},
        "network_bytes": 0, "paid_usd": 0, "tokens": None,
        "full_protocol_admitted": False, "outcome_access_authorized": False,
        "limitations": ["Synthetic path only, not an upper bound on real quote/event density",
            "Synthetic active-basket/event density is not a worst-case bound",
            "21 real archives: sizes, row counts, duplicate group sizes and parser/CRC/capture costs UNKNOWN",
            "Historical executable fills/costs, original reservation and launcher gates unchanged",
            "No real prices, performance result, trial charge or legacy run/capture import"]}
