"""Atomic, serialized state with an append-only, hash-chained evidence ledger."""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path

from quant.state import utc_now, write_json


class Refused(RuntimeError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def strict_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Refused(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    def invalid(value):
        raise Refused(f"Non-finite JSON: {value}")
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_constant=invalid)


def event(state, kind, payload):
    events = state["events"]
    previous = events[-1]["hash"] if events else "0" * 64
    row = {"sequence": len(events) + 1, "at": utc_now(), "kind": kind,
           "payload": copy.deepcopy(payload), "previous": previous}
    row["hash"] = digest(row)
    events.append(row)
    return row


def verify(state):
    if state.get("schema") != 1:
        raise Refused("Unknown state schema; do not reset or silently migrate")
    if state.get("integrity") != digest({k: v for k, v in state.items() if k != "integrity"}):
        raise Refused("State checksum failed; preserve the damaged evidence")
    previous = "0" * 64
    for sequence, row in enumerate(state["events"], 1):
        if (row["sequence"] != sequence or row["previous"] != previous
                or row["hash"] != digest({k: v for k, v in row.items() if k != "hash"})):
            raise Refused("Evidence chain failed")
        previous = row["hash"]
    if state.get("real_capital_authorized") is not False or state.get("live_trading_authorized") is not False:
        raise Refused("Capital/trading authority must remain FALSE")


class Store:
    def __init__(self, directory):
        self.root = Path(directory).resolve()
        self.state_path = self.root / "STATE.json"
        self.control_path = self.root / "CONTROL.json"

    @contextmanager
    def lock(self):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / ".state.lock"
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            if os.fstat(fd).st_ino != path.stat().st_ino:
                raise Refused("Lock replaced during use")
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def read(self):
        state = strict_json(self.state_path)
        verify(state)
        return state

    def save(self, state):
        if self.state_path.exists():
            old = self.read()
            if state["events"][:len(old["events"])] != old["events"]:
                raise Refused("Evidence cannot be removed or rewritten")
            for key in ("imported", "baseline"):
                if state[key] != old[key]:
                    raise Refused(f"Imported history is immutable: {key}")
            for key in ("protocols", "looks", "evidence", "admissions"):
                for identity, prior in old.get(key, {}).items():
                    if identity not in state[key]:
                        raise Refused(f"Cannot delete {key}/{identity}")
                    if key != "looks" and state[key][identity] != prior:
                        raise Refused(f"Cannot rewrite {key}/{identity}")
                    if key == "looks" and any(state[key][identity].get(k) != v
                                               for k, v in prior.items() if k != "status"):
                        raise Refused("Look identity/scope/charge cannot change")
            for scope, count in old["trial_charges"].items():
                if state["trial_charges"].get(scope, -1) < count:
                    raise Refused("Trial accounting cannot go backwards")
            for meter, prior in old["usage"].items():
                if prior is not None and (state["usage"].get(meter) is None or state["usage"][meter] < prior):
                    raise Refused("Measured cost cannot be erased/reset: " + meter)
            terminal = {"COMPLETED_SPENT", "UNKNOWN_OUTCOME"}
            for identity, look in old["looks"].items():
                if look["status"] in terminal and state["looks"][identity]["status"] != look["status"]:
                    raise Refused("A spent/uncertain look cannot return to the queue")
            for identity, family in old["families"].items():
                if identity not in state["families"] or (family["status"] == "REJECTED_CLOSED"
                        and state["families"][identity] != family):
                    raise Refused("Do not delete or reopen a closed mechanism")
        state["updated_at"] = utc_now()
        state["integrity"] = digest({k: v for k, v in state.items() if k != "integrity"})
        verify(state)
        write_json(self.state_path, state)

    def control(self):
        control = strict_json(self.control_path)
        if (type(control.get("paused")) is not bool or control.get("schema") != 1
                or control.get("real_capital_authorized") is not False
                or control.get("live_trading_authorized") is not False):
            raise Refused("Invalid controls; fail closed")
        limits = control["limits"]
        for key, value in limits.items():
            if value is not None and (type(value) not in (int, float) or value < 0):
                raise Refused(f"Invalid budget: {key}")
        if not 0 < limits["job_wall_seconds"] <= 600:
            raise Refused("Job wall-time must be bounded at 600 seconds or less")
        if limits["paid_usd_total"] != 0:
            raise Refused("Purchases have not been authorized")
        return control

    def pause(self, paused, reason):
        with self.lock():
            control = self.control()
            control.update(paused=paused, pause_reason=reason, changed_at=utc_now())
            write_json(self.control_path, control)
            state = self.read()
            event(state, "CONTROL_CHANGED", {"paused": paused, "reason": reason})
            self.save(state)
