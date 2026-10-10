"""One bounded metadata read. No market data, sealed outcomes or paid APIs."""
import subprocess
import time

from .engine import Lab, budget_check
from .store import Refused, event
from quant.state import utc_now


def monitor(directory, repository, actor="manual", enabled_confirmed=False):
    lab = Lab(directory)
    state, control = lab.snapshot()
    try:
        budget_check(state, control)
    except Refused:
        return lab.tick(actor=actor)
    # Terminal families are retained in memory but not repeatedly polled.
    refs = {identity: family["ref"] for identity, family in state["families"].items()
            if family.get("ref") and family["status"] != "REJECTED_CLOSED"}
    started = time.monotonic()
    try:
        result = subprocess.run(["git", "ls-remote", "--heads", "origin",
                                 *["refs/heads/" + ref for ref in refs.values()]],
                                cwd=repository, capture_output=True, text=True,
                                timeout=min(control["limits"]["job_wall_seconds"], 30))
        if result.returncode:
            raise Refused("REMOTE_METADATA_UNAVAILABLE")
        size = len(result.stdout.encode())
        if size > control["limits"]["metadata_bytes_per_tick"]:
            raise Refused("METADATA_PAYLOAD_LIMIT")
        heads = dict(line.split("\t", 1)[::-1] for line in result.stdout.splitlines())
        if any("refs/heads/" + ref not in heads for ref in refs.values()):
            raise Refused("MONITORED_REF_MISSING")
        observations = {identity: {"ref": ref, "sha": heads["refs/heads/" + ref], "kind": "BRANCH_HEAD_ONLY"}
                        for identity, ref in refs.items()}
        updated = lab.tick(observations, actor=actor, enabled_confirmed=enabled_confirmed)
        with lab.store.lock():
            updated = lab.store.read()
            updated["usage"]["metadata_bytes"] += size
            updated["usage"]["wall_seconds"] += time.monotonic() - started
            updated["scheduler"]["metadata_probe"] = {"at": updated["scheduler"]["last_tick"]["at"],
                                                        "status": "COMPLETE", "refs": len(refs), "payload_bytes": size}
            lab.store.save(updated)
        return updated
    except (subprocess.TimeoutExpired, Refused) as exc:
        with lab.store.lock():
            updated = lab.store.read()
            reason = str(exc) if isinstance(exc, Refused) else "REMOTE_METADATA_TIMEOUT"
            previous = updated["scheduler"].get("metadata_probe", {})
            updated["scheduler"]["metadata_probe"] = {"status": reason, "at": utc_now()}
            updated["scheduler"]["last_tick"] = {"at": utc_now(), "actor": actor, "status": reason, "new_events": 0}
            if previous.get("status") != reason:
                event(updated, "SOURCE_UNAVAILABLE", {"reason": reason, "economic_verdict": None})
            updated["usage"]["wall_seconds"] += time.monotonic() - started
            lab.store.save(updated)
        return updated
