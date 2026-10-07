"""Fail-closed L2-A qualification verdicts; never import or execute the harness.

Exit codes and configured properties alone are not measured prevention. Each
verdict needs the intended probe, its observation, and applicable accounting.
Missing, malformed, contradictory or masked evidence remains NOT_VERIFIED.
Rounded human-readable memory/CPU figures are not exact upper-bound evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

PREVENTED = "PREVENTED_OR_STOPPED"
BREACH = "DETECTED_AFTER_BREACH"
UNVERIFIED = "NOT_VERIFIED"
ONE_MIB = 1024 * 1024
MEMORY_MAX = 128 * ONE_MIB
FULLY_QUALIFIED = "ALL_LIMITS_PREVENTED_OR_STOPPED_WITH_MEASUREMENT"
UNIT_KEYS = (
    ("positive", "positive", "full"), ("time", "time", "full"), ("cpu", "cpu", "full"),
    ("memory", "memory", "full"), ("child", "child", "full"),
    ("network", "network", "full"), ("network_pn", "network", "private-network-only"),
    ("write", "write", "full"), ("output", "output", "full"), ("read", "read", "full"),
)
READ_EXPECTATIONS = {"/opt": ["a2"], "/srv": ["a2out"], "/home": None,
    "/root": None, "/var": None, "/mnt": None, "/media": None, "/tmp": None, "/dev/shm": None}
ESCAPE_PATHS = frozenset({"/tmp", "/var/tmp", "/dev/shm", "/opt/a2", "/home", "/root", "/nonexistent"})
NETWORK_KEYS = frozenset({"udp:192.0.2.1", "tcp:192.0.2.1", "udp:198.51.100.1",
                          "tcp:198.51.100.1", "udp6:2001:db8::1"})


def _read(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def parse_show(text):
    if not text:
        return {}, False
    fields = {}
    for line in text.splitlines():
        if "=" not in line:
            return {}, False
        key, value = line.split("=", 1)
        if not key or key in fields:
            return {}, False
        fields[key] = value
    return fields, True


def load_unit(dest, probe, variant, stamp):
    unit = f"a2qual-{probe}-{variant}-{stamp}"
    show, valid = parse_show(_read(dest / f"{unit}.show.txt"))
    cgroup, cgroup_valid = parse_show(_read(dest / f"{unit}.cgroup.txt"))
    journal = _read(dest / f"{unit}.journal.txt")
    text = _read(dest / f"{unit}.qual-{probe}.json")
    observation = None
    malformed = False
    entered = False
    try:
        marker = json.loads(_read(dest / f"{unit}.qual-{probe}-started.json") or "null")
        entered = marker == {"probe": probe, "phase": "ENTERED"}
    except (ValueError, TypeError):
        pass
    if text is not None:
        try:
            doc = json.loads(text)
            if type(doc) is not dict or set(doc) != {"probe", "observation"} \
                    or doc["probe"] != probe or type(doc["observation"]) is not dict:
                raise ValueError("OBSERVATION_SCHEMA")
            observation = doc["observation"]
        except (ValueError, TypeError):
            malformed = True
    return {"unit": unit, "probe": probe, "show": show, "show_available": valid,
        "cgroup": cgroup if cgroup_valid else {}, "observation": observation,
        "malformed_observation": malformed, "journal_available": journal is not None,
        "probe_entered": entered,
        "stdio_marker_in_journal": journal is not None and "A2QUAL-STDIO-MARKER" in journal}


def _integer(value):
    if type(value) is int:
        return value if value >= 0 else None
    return int(value) if type(value) is str and value.isascii() and value.isdigit() else None


def _runtime_us(unit):
    show = unit.get("show", {})
    start = _integer(show.get("ExecMainStartTimestampMonotonic"))
    end = _integer(show.get("ExecMainExitTimestampMonotonic"))
    return end - start if start is not None and end is not None and start > 0 and end >= start else None


def _memory_peak(unit):
    # Prefer exact systemd bytes; cgroup is captured before reset/collection.
    peak = _integer(unit.get("show", {}).get("MemoryPeak"))
    if peak is None:
        peak = _integer(unit.get("cgroup", {}).get("memory.peak"))
    if peak is None:
        peak = _integer((unit.get("observation") or {}).get("cgroup", {}).get("memory.peak"))
    return peak


def _valid(unit):
    return unit.get("show_available") is True and unit.get("probe_entered") is True \
        and not unit.get("malformed_observation", False)


def _exited(unit, status):
    show = unit.get("show", {})
    return _valid(unit) and show.get("ExecMainCode") == "1" and show.get("ExecMainStatus") == str(status)


def _probe_verdict(unit, check, breached=False):
    if _exited(unit, 0) or breached:
        return BREACH
    if _exited(unit, 20) and unit.get("observation") is not None and check:
        return PREVENTED
    return UNVERIFIED


def _numeric_limit(unit, *, measured, bound, property_ok, termination_ok):
    if unit.get("observation") is not None or (measured is not None and measured > bound):
        return BREACH
    if _valid(unit) and measured is not None and property_ok and termination_ok:
        return PREVENTED
    return UNVERIFIED


def summarize_units(units, stamp):
    """Pure logic; synthetic transcript tests do not qualify any host."""
    units = {key: units.get(key, {}) for key, _, _ in UNIT_KEYS}
    verdicts = {}
    time = units["time"]
    show = time.get("show", {})
    verdicts["ELAPSED_60S"] = _numeric_limit(time, measured=_runtime_us(time), bound=60_000_000,
        property_ok=show.get("RuntimeMaxUSec") in {"1min", "60s", "60000000"},
        termination_ok=show.get("Result") == "timeout" and show.get("ExecMainCode") == "2")
    cpu = units["cpu"]
    show = cpu.get("show", {})
    verdicts["CPU_5S"] = _numeric_limit(cpu, measured=_integer(show.get("CPUUsageNSec")), bound=5_000_000_000,
        property_ok=show.get("LimitCPU") == "5",
        termination_ok=show.get("ExecMainCode") in {"2", "3"}
            and (show.get("ExecMainStatus") == "24" or (show.get("ExecMainStatus") == "9"
                 and (_integer(show.get("CPUUsageNSec")) or 0) >= 5_000_000_000))
            and show.get("Result") in {"signal", "core-dump"})
    # A killed process does not prove system-wide absence of a core artifact.
    # Require the configured bound and record the observed wait status.
    verdicts["NO_CORE_DUMP"] = (BREACH if show.get("ExecMainCode") == "3" else
        PREVENTED if _valid(cpu) and show.get("ExecMainCode") == "2" and show.get("LimitCORE") == "0"
        else UNVERIFIED)
    memory = units["memory"]
    show = memory.get("show", {})
    verdicts["MEMORY_128MIB"] = _numeric_limit(memory, measured=_memory_peak(memory), bound=MEMORY_MAX,
        property_ok=_integer(show.get("MemoryMax")) == MEMORY_MAX,
        termination_ok=show.get("Result") == "oom-kill" and show.get("ExecMainCode") == "2")
    swap_peak = _integer(show.get("MemorySwapPeak"))
    if swap_peak is None:
        swap_peak = _integer(memory.get("cgroup", {}).get("memory.swap.peak"))
    verdicts["NO_SWAP"] = (BREACH if swap_peak is not None and swap_peak > 0 else
        PREVENTED if _valid(memory) and _integer(show.get("MemorySwapMax")) == 0 and swap_peak == 0
        else UNVERIFIED)
    child = units["child"]
    obs = child.get("observation") or {}
    verdicts["ONE_PROCESS_NO_CHILD"] = _probe_verdict(child,
        obs.get("fork") == "EAGAIN" and obs.get("thread") in {"RuntimeError", "EAGAIN"}
        and child.get("show", {}).get("TasksMax") == "1",
        obs.get("fork") == "CREATED" or obs.get("thread") == "CREATED")
    for key, label in (("network", "NETWORK_ZERO_FAMILY_RESTRICTION_AND_PRIVATE_NETWORK"),
                       ("network_pn", "NETWORK_ZERO_PRIVATE_NETWORK_ALONE")):
        unit = units[key]
        obs = unit.get("observation") or {}
        attempts = obs.get("attempts")
        attempts = attempts if type(attempts) is dict else {}
        refused = {"SOCKET_EAFNOSUPPORT", "SOCKET_EPERM", "SOCKET_EACCES"}
        if key == "network_pn":
            refused |= {"ENETUNREACH", "EHOSTUNREACH", "EPERM", "EACCES"}
        verdicts[label] = _probe_verdict(unit,
            obs.get("interfaces") == ["lo"] and obs.get("namespace_isolated") is True
            and set(attempts) == NETWORK_KEYS and all(v in refused for v in attempts.values())
            and unit.get("show", {}).get("PrivateNetwork") == "yes",
            any(v in {"SENT", "CONNECTED"} for v in attempts.values()))
    write = units["write"]
    obs = write.get("observation") or {}
    written = _integer(obs.get("fill_bytes_before_stop"))
    escapes = obs.get("outside_writable_directory")
    escapes = escapes if type(escapes) is dict else {}
    verdicts["WRITABLE_1MIB_AND_NO_ESCAPE"] = _probe_verdict(write,
        obs.get("fill") == "ENOSPC" and written is not None and written <= ONE_MIB
        and set(escapes) == ESCAPE_PATHS and all(v in {"EACCES", "EPERM", "EROFS", "ENOENT", "ENOTDIR"}
                                               for v in escapes.values()),
        obs.get("fill") == "COMPLETED_2_MIB" or "CREATED" in escapes.values()
        or (written is not None and written > ONE_MIB))
    output = units["output"]
    obs = output.get("observation") or {}
    verdicts["OUTPUT_64KIB_BOUNDED_WRITER"] = _probe_verdict(output,
        obs.get("bounded_writer") == "REFUSED" and obs.get("oversize_file_present") is False,
        obs.get("bounded_writer") == "WRITTEN" or obs.get("oversize_file_present") is True)
    stdio_show = output.get("show", {})
    verdicts["STDOUT_STDERR_DISCARDED"] = (BREACH if output.get("stdio_marker_in_journal") else
        PREVENTED if _exited(output, 20) and output.get("journal_available") is True
        and stdio_show.get("StandardOutput") == "null" and stdio_show.get("StandardError") == "null"
        else UNVERIFIED)
    read = units["read"]
    obs = read.get("observation") or {}
    read_ok = set(obs) == set(READ_EXPECTATIONS) and all(
        obs[d] == expected if expected is not None else type(obs[d]) is str and obs[d] in {"EMPTY", "EACCES", "EPERM", "ENOENT", "ENOTDIR"}
        for d, expected in READ_EXPECTATIONS.items())
    verdicts["READ_ISOLATION"] = _probe_verdict(read, read_ok,
        any(value in ("VISIBLE_ENTRIES", "UNEXPECTED_LAYOUT") for value in obs.values()))
    positive = units["positive"]
    positive_obs = positive.get("observation") or {}
    positive_ok = _exited(positive, 21) and positive_obs.get("checksum_mod_97") == sum(i*i for i in range(200000)) % 97
    memory_available = positive_ok and _memory_peak(positive) is not None
    cpu_available = positive_ok and _integer(positive.get("show", {}).get("CPUUsageNSec")) is not None \
        and _runtime_us(positive) is not None
    measurement = {"POSITIVE_CONTROL": "COMPLETED" if positive_ok else UNVERIFIED,
        "MEMORY_MEASUREMENT": "AVAILABLE:EXACT_BYTES" if memory_available else UNVERIFIED,
        "CPU_RUNTIME_MEASUREMENT": "AVAILABLE:EXACT_ACCOUNTING" if cpu_available else UNVERIFIED}
    overall = FULLY_QUALIFIED if all(v == PREVENTED for v in verdicts.values()) \
        and positive_ok and memory_available and cpu_available else "NOT_FULLY_QUALIFIED_OWNER_DECISION_REQUIRED"
    return {"stamp": stamp, "verdicts": verdicts, "measurement": measurement,
            "overall": overall, "units": units}


def summarize(dest, stamp):
    return summarize_units({key: load_unit(dest, probe, variant, stamp) for key, probe, variant in UNIT_KEYS}, stamp)


def main(argv):
    if len(argv) != 2 or re.fullmatch(r"[0-9]{8}T[0-9]{6}Z", argv[1]) is None:
        raise SystemExit("usage: summarize_qualification.py <transcript_dir> <YYYYMMDDTHHMMSSZ>")
    summary = summarize(Path(argv[0]), argv[1])
    for name, verdict in summary["verdicts"].items():
        print(f"{name}={verdict}")
    for name, value in summary["measurement"].items():
        print(f"{name}={value}")
    print(f"OVERALL={summary['overall']}")
    (Path(argv[0]) / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if summary["overall"] == FULLY_QUALIFIED else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
