"""Summarize an L2-A transcript directory into per-limit verdicts.

Verdict vocabulary (ratified lot-2 decision, L2-A):
PREVENTED_OR_STOPPED, DETECTED_AFTER_BREACH, NOT_VERIFIED.
A breach that was only detected is never a success. Standard library only;
does not import the A2 harness.
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

_RESULT = re.compile(r"Finished with result:\s*(\S+)")
_MAIN = re.compile(r"Main processes terminated with:\s*code=(\w+)/status=(\S+)")
_RUNTIME = re.compile(r"Service runtime:\s*(.+)")
_CPU = re.compile(r"CPU time consumed:\s*(.+)")
_MEMORY = re.compile(r"Memory peak:\s*(.+)")
_JOURNAL_MEMORY = re.compile(r"([0-9.]+[KMG]?B?) memory peak")


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _first(pattern, text):
    match = pattern.search(text)
    return match.groups() if match else None


def load_unit(dest: Path, probe: str, variant: str, stamp: str) -> dict:
    unit = f"a2qual-{probe}-{variant}-{stamp}"
    run_text = _read(dest / f"{unit}.systemd-run.txt")
    journal = _read(dest / f"{unit}.journal.txt")
    observation_text = _read(dest / f"{unit}.qual-{probe}.json")
    observation = json.loads(observation_text)["observation"] if observation_text else None
    main = _first(_MAIN, run_text)
    return {
        "unit": unit,
        "result": (_first(_RESULT, run_text) or (None,))[0],
        "main_code": main[0] if main else None,
        "main_status": main[1] if main else None,
        "runtime": (_first(_RUNTIME, run_text) or (None,))[0],
        "cpu": (_first(_CPU, run_text) or (None,))[0],
        "memory_peak_systemd_run": (_first(_MEMORY, run_text) or (None,))[0],
        "memory_peak_journal": (_first(_JOURNAL_MEMORY, journal) or (None,))[0],
        "stdio_marker_in_journal": "A2QUAL-STDIO-MARKER" in journal,
        "oom_in_journal": "oom" in journal.lower(),
        "observation": observation,
    }


def _exited(unit, status):
    return unit["main_code"] == "exited" and unit["main_status"] == str(status)


def _refusal_verdict(unit):
    if unit["observation"] is not None and _exited(unit, 20):
        return PREVENTED
    if _exited(unit, 0):
        return BREACH
    return UNVERIFIED


UNIT_KEYS = (
    ("positive", "positive", "full"), ("time", "time", "full"), ("cpu", "cpu", "full"),
    ("memory", "memory", "full"), ("child", "child", "full"),
    ("network", "network", "full"),
    ("network_pn", "network", "private-network-only"),
    ("write", "write", "full"), ("output", "output", "full"), ("read", "read", "full"),
)


def summarize(dest: Path, stamp: str) -> dict:
    units = {key: load_unit(dest, probe, variant, stamp) for key, probe, variant in UNIT_KEYS}
    return summarize_units(units, stamp)


def summarize_units(units: dict, stamp: str) -> dict:
    """Pure verdict logic over parsed unit records (testable without a host)."""
    verdicts = {}

    time_unit = units["time"]
    if time_unit["observation"] is not None:
        verdicts["ELAPSED_60S"] = BREACH
    elif time_unit["result"] == "timeout":
        verdicts["ELAPSED_60S"] = PREVENTED
    else:
        verdicts["ELAPSED_60S"] = UNVERIFIED

    cpu_unit = units["cpu"]
    killed = cpu_unit["main_code"] in ("killed", "dumped") and \
        (cpu_unit["main_status"] or "").upper().removeprefix("SIG") in ("XCPU", "KILL")
    if cpu_unit["observation"] is not None:
        verdicts["CPU_5S"] = BREACH
    elif killed:
        verdicts["CPU_5S"] = PREVENTED
    else:
        verdicts["CPU_5S"] = UNVERIFIED
    verdicts["NO_CORE_DUMP"] = (PREVENTED if cpu_unit["main_code"] == "killed"
                                else UNVERIFIED)

    memory_unit = units["memory"]
    if memory_unit["observation"] is not None:
        verdicts["MEMORY_128MIB"] = BREACH
    elif memory_unit["result"] == "oom-kill":
        verdicts["MEMORY_128MIB"] = PREVENTED
    else:
        verdicts["MEMORY_128MIB"] = UNVERIFIED

    verdicts["ONE_PROCESS_NO_CHILD"] = _refusal_verdict(units["child"])

    network_full = _refusal_verdict(units["network"])
    network_pn = _refusal_verdict(units["network_pn"])
    pn_observation = units["network_pn"]["observation"] or {}
    if network_pn == PREVENTED and pn_observation.get("interfaces") != ["lo"]:
        network_pn = UNVERIFIED
    verdicts["NETWORK_ZERO_FAMILY_RESTRICTION_AND_PRIVATE_NETWORK"] = network_full
    verdicts["NETWORK_ZERO_PRIVATE_NETWORK_ALONE"] = network_pn

    write_verdict = _refusal_verdict(units["write"])
    write_observation = units["write"]["observation"] or {}
    if write_verdict == PREVENTED and write_observation.get("fill_bytes_before_stop", ONE_MIB + 1) > ONE_MIB:
        write_verdict = BREACH
    verdicts["WRITABLE_1MIB_AND_NO_ESCAPE"] = write_verdict

    verdicts["OUTPUT_64KIB_BOUNDED_WRITER"] = _refusal_verdict(units["output"])
    output_unit = units["output"]
    if output_unit["main_code"] is None:
        verdicts["STDOUT_STDERR_DISCARDED"] = UNVERIFIED
    elif output_unit["stdio_marker_in_journal"]:
        verdicts["STDOUT_STDERR_DISCARDED"] = BREACH
    else:
        verdicts["STDOUT_STDERR_DISCARDED"] = PREVENTED

    verdicts["READ_ISOLATION"] = _refusal_verdict(units["read"])

    positive = units["positive"]
    cgroup = ((positive["observation"] or {}).get("cgroup") or {})
    peak_cgroup = cgroup.get("memory.peak", "")
    sources = []
    if positive["memory_peak_systemd_run"]:
        sources.append("SYSTEMD_RUN")
    if positive["memory_peak_journal"]:
        sources.append("JOURNAL")
    if peak_cgroup.isdigit():
        sources.append("CGROUP_MEMORY_PEAK")
    positive_ok = _exited(positive, 21) and positive["observation"] is not None
    measurement = {
        "POSITIVE_CONTROL": "COMPLETED" if positive_ok else UNVERIFIED,
        "MEMORY_MEASUREMENT": ("AVAILABLE:" + "+".join(sources)) if positive_ok and sources
        else "NOT_VERIFIED",
        "CPU_RUNTIME_MEASUREMENT": "AVAILABLE:SYSTEMD_RUN"
        if positive_ok and positive["cpu"] and positive["runtime"] else "NOT_VERIFIED",
    }
    overall = ("ALL_LIMITS_PREVENTED_OR_STOPPED_WITH_MEASUREMENT"
               if all(v == PREVENTED for v in verdicts.values())
               and measurement["MEMORY_MEASUREMENT"] != "NOT_VERIFIED"
               and measurement["CPU_RUNTIME_MEASUREMENT"] != "NOT_VERIFIED"
               and positive_ok
               else "NOT_FULLY_QUALIFIED_OWNER_DECISION_REQUIRED")
    return {"stamp": stamp, "verdicts": verdicts, "measurement": measurement,
            "overall": overall, "units": units}


def main(argv) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: summarize_qualification.py <transcript_dir> <stamp>")
    summary = summarize(Path(argv[0]), argv[1])
    for name, verdict in summary["verdicts"].items():
        print(f"{name}={verdict}")
    for name, value in summary["measurement"].items():
        print(f"{name}={value}")
    print(f"OVERALL={summary['overall']}")
    (Path(argv[0]) / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
