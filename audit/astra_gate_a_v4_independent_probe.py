#!/usr/bin/env python3
"""Independent Astra Gate A v4 repository probe.

Audit-only: does not mutate the frozen Blue candidate or any target host.
It attacks the candidate through the actual repository implementation and
records current-unit assertions separately from hypothetical parser limits.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import signal
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
ASTRA_BASE = "b636a04b6f8f7786679907d01a4fa22bdfc4e329"

spec = importlib.util.spec_from_file_location(
    "astra_gate_a_v4_launcher", ROOT / "deploy" / "quant_sec_supervisor.py")
launcher = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(launcher)

BASE_EXEC = (
    "{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -I "
    "/opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --qualifying ; "
    "ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; "
    "code=(null) ; status=0/0 }"
)

results: dict[str, object] = {
    "candidate_sha": CANDIDATE,
    "astra_mission_base": ASTRA_BASE,
    "attacks": {},
    "limitations": [],
}
failures: list[str] = []


def record(name: str, ok: bool, detail: object = None) -> None:
    results["attacks"][name] = {"ok": bool(ok), "detail": detail}
    if not ok:
        failures.append(name)


def shown(root: Path, exec_start: str = BASE_EXEC, **overrides):
    target = root / "deploy" / "quant-sec-capture.service"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "deploy" / "quant-sec-capture.service", target)
    fields = {
        "FragmentPath": str(target),
        "DropInPaths": "",
        "ExecStart": exec_start,
        "WorkingDirectory": "/opt/quant",
        "Restart": "on-failure",
        "RestartUSec": "15s",
        "StartLimitIntervalUSec": "10min",
        "StartLimitBurst": "5",
        "KillMode": "control-group",
        "KillSignal": "15",
        "TimeoutStopUSec": "30s",
        "EnvironmentFiles": "/etc/quant/sec-capture.env (ignore_errors=no)",
    }
    fields.update(overrides)
    return SimpleNamespace(
        returncode=0,
        stdout="\n".join(f"{key}={value}" for key, value in fields.items()) + "\n",
        stderr="",
    )


def digest(root: Path, exec_start: str = BASE_EXEC, **overrides) -> str:
    with mock.patch.object(
            launcher.subprocess, "run",
            return_value=shown(root, exec_start, **overrides)):
        return launcher._effective_systemd_definition(root)


def rejected(root: Path, exec_start: str = BASE_EXEC, **overrides) -> bool:
    try:
        digest(root, exec_start, **overrides)
    except RuntimeError:
        return True
    return False


# A1 — independently reconstruct the old raw-property failure mechanism.
raw_before = {
    "ExecStart": BASE_EXEC,
    "Restart": "on-failure",
    "WorkingDirectory": "/opt/quant",
}
raw_after = dict(raw_before)
raw_after["ExecStart"] = BASE_EXEC.replace(
    "start_time=[n/a]", "start_time=[Sun 2026-09-20 18:42:33 UTC]"
).replace(
    "stop_time=[n/a]", "stop_time=[Sun 2026-09-20 19:58:25 UTC]"
).replace("pid=0", "pid=48213").replace(
    "code=(null)", "code=exited").replace("status=0/0", "status=0/SUCCESS")
old_before = hashlib.sha256(
    json.dumps(raw_before, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
old_after = hashlib.sha256(
    json.dumps(raw_after, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
record("A1_old_raw_execstart_digest_moves", old_before != old_after,
       {"before": old_before, "after": old_after})


# A2/A3/A4/A5/A6/A7 use one root per comparison so FragmentPath is identical.
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    baseline = digest(root)

    # A2 — each transient observation independently varies without moving digest.
    transient_variants = {
        "start_time": BASE_EXEC.replace(
            "start_time=[n/a]", "start_time=[Sun 2026-09-20 18:42:33 UTC]"),
        "stop_time": BASE_EXEC.replace(
            "stop_time=[n/a]", "stop_time=[Sun 2026-09-20 19:58:25 UTC]"),
        "pid": BASE_EXEC.replace("pid=0", "pid=48213"),
        "code": BASE_EXEC.replace("code=(null)", "code=exited"),
        "status": BASE_EXEC.replace("status=0/0", "status=1/FAILURE"),
    }
    transient_digests = {k: digest(root, v) for k, v in transient_variants.items()}
    record("A2_each_transient_field_stable",
           all(value == baseline for value in transient_digests.values()),
           transient_digests)

    # A3 — genuine command semantics must reject or move the accepted digest.
    semantic_variants = {
        "executable_path": BASE_EXEC.replace("path=/usr/bin/python3", "path=/usr/bin/python3.12"),
        "python_interpreter_argv": BASE_EXEC.replace(
            "argv[]=/usr/bin/python3 -I", "argv[]=/usr/bin/python3.12 -I"),
        "supervisor_path": BASE_EXEC.replace(
            "/opt/quant/deploy/quant_sec_supervisor.py",
            "/opt/quant/other/quant_sec_supervisor.py"),
        "root_flag": BASE_EXEC.replace("--root /opt/quant", "--rootx /opt/quant"),
        "root_value": BASE_EXEC.replace("--root /opt/quant", "--root /srv/quant"),
        "extra_arg": BASE_EXEC.replace(
            "--qualifying", "--qualifying --unexpected-acquisition-arg"),
        "removed_arg": BASE_EXEC.replace(" -I ", " "),
    }
    semantic_results = {}
    a3_ok = True
    for label, variant in semantic_variants.items():
        try:
            value = digest(root, variant)
            semantic_results[label] = {"accepted": True, "digest": value}
            a3_ok = a3_ok and value != baseline
        except RuntimeError as exc:
            semantic_results[label] = {"accepted": False, "error": str(exc)}
    record("A3_real_command_drift_rejected_or_digest_moves", a3_ok, semantic_results)
    record("A3_qualifying_removed_rejected",
           rejected(root, BASE_EXEC.replace(" --qualifying", "")))

    # A4 — parser fidelity for the current single-ExecStart Type=simple unit.
    reordered = (
        "{ status=0/0 ; pid=0 ; ignore_errors=no ; "
        "argv[]=/usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py "
        "--root /opt/quant --qualifying ; path=/usr/bin/python3 ; "
        "code=(null) ; stop_time=[n/a] ; start_time=[n/a] ; }"
    )
    record("A4_field_order_and_delimiter_whitespace_canonical",
           digest(root, reordered) == baseline)
    record("A4_malformed_no_struct_fails_closed",
           rejected(root, "garbage-no-braces"))

    unknown_a = BASE_EXEC.replace("ignore_errors=no ;", "ignore_errors=no ; future_flag=A ;")
    unknown_b = BASE_EXEC.replace("ignore_errors=no ;", "ignore_errors=no ; future_flag=B ;")
    unknown_a_digest = digest(root, unknown_a)
    unknown_b_digest = digest(root, unknown_b)
    record("A4_unknown_stable_fields_are_bound",
           unknown_a_digest != baseline and unknown_a_digest != unknown_b_digest)

    repeated = BASE_EXEC + " " + BASE_EXEC
    record("A4_repeated_struct_is_not_silently_equal",
           digest(root, repeated) != baseline)

    unit_text = (ROOT / "deploy" / "quant-sec-capture.service").read_text(encoding="utf-8")
    current_single_simple = (
        "Type=simple" in unit_text and
        sum(1 for line in unit_text.splitlines()
            if line.strip().startswith("ExecStart=")) == 1
    )
    record("A4_current_unit_single_execstart_type_simple", current_single_simple)

    duplicate_conflict = (
        "{ path=/wrong ; path=/usr/bin/python3 ; "
        "argv[]=/usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py "
        "--root /opt/quant --qualifying ; ignore_errors=no ; }"
    )
    duplicate_normal = (
        "{ path=/usr/bin/python3 ; "
        "argv[]=/usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py "
        "--root /opt/quant --qualifying ; ignore_errors=no ; }"
    )
    duplicate_collapses = (
        launcher._canonicalize_exec_start(duplicate_conflict) ==
        launcher._canonicalize_exec_start(duplicate_normal)
    )
    results["limitations"].append({
        "name": "duplicate_stable_key_last_wins",
        "observed": duplicate_collapses,
        "current_unit_reachable": False,
        "reason": "current frozen unit is Type=simple with exactly one canonical ExecStart; normal systemctl ExecStart structs contain each named field once",
    })

    escaped_semicolon = (
        "{ path=/usr/bin/python3 ; "
        "argv[]=/usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py "
        "--root /opt/quant --qualifying --label=a\\;b ; ignore_errors=no ; }"
    )
    parsed_escape = launcher._canonicalize_exec_start(escaped_semicolon)
    results["limitations"].append({
        "name": "literal_semicolon_in_argv_not_roundtrippable_by_split_semicolon_parser",
        "observed_argv": parsed_escape[0].get("argv[]") if parsed_escape else None,
        "current_unit_reachable": False,
        "reason": "frozen ExecStart has no argument containing semicolons",
    })

    # A5 — exact qualifying authority, including value-like/prefix/suffix tokens.
    qualifying_bad = {
        "removed": BASE_EXEC.replace(" --qualifying", ""),
        "prefix": BASE_EXEC.replace("--qualifying", "x--qualifying"),
        "suffix": BASE_EXEC.replace("--qualifying", "--qualifying-disabled"),
        "value_like": BASE_EXEC.replace("--qualifying", "--mode=--qualifying"),
    }
    qualifying_bad_results = {name: rejected(root, value)
                              for name, value in qualifying_bad.items()}
    record("A5_qualifying_lookalikes_rejected",
           all(qualifying_bad_results.values()), qualifying_bad_results)

    duplicate_qualifying = BASE_EXEC.replace("--qualifying", "--qualifying --qualifying")
    duplicate_digest = digest(root, duplicate_qualifying)
    record("A5_duplicate_qualifying_not_normalized_to_baseline",
           duplicate_digest != baseline,
           {"accepted": True, "digest_changed": duplicate_digest != baseline})

    argv_whitespace = BASE_EXEC.replace(
        "argv[]=/usr/bin/python3 -I",
        "argv[]=/usr/bin/python3  -I")
    whitespace_digest = digest(root, argv_whitespace)
    results["limitations"].append({
        "name": "internal_argv_whitespace_changes_digest",
        "observed": whitespace_digest != baseline,
        "current_unit_reachable": False,
        "reason": "systemctl joins the frozen argv vector with a canonical single-space rendering; frozen argv contains no embedded-space argument",
    })

    # A6 — all existing systemd contract fields remain fail-closed.
    drift_cases = {
        "DropInPaths": {"DropInPaths": "/etc/systemd/system/quant-sec-capture.service.d/x.conf"},
        "WorkingDirectory": {"WorkingDirectory": "/tmp"},
        "EnvironmentFiles": {"EnvironmentFiles": "/etc/quant/other.env (ignore_errors=no)"},
        "Restart": {"Restart": "no"},
        "RestartUSec": {"RestartUSec": "1s"},
        "StartLimitIntervalUSec": {"StartLimitIntervalUSec": "1s"},
        "StartLimitBurst": {"StartLimitBurst": "99"},
        "KillMode": {"KillMode": "process"},
        "KillSignal": {"KillSignal": "9"},
        "TimeoutStopUSec": {"TimeoutStopUSec": "1s"},
    }
    a6 = {name: rejected(root, **kwargs) for name, kwargs in drift_cases.items()}

    tampered = root / "tampered.service"
    tampered.write_text("[Service]\nExecStart=/bin/false\n", encoding="utf-8")
    a6["FragmentPath_byte_mismatch"] = rejected(root, FragmentPath=str(tampered))

    unavailable = SimpleNamespace(returncode=1, stdout="", stderr="failed")
    try:
        with mock.patch.object(launcher.subprocess, "run", return_value=unavailable):
            launcher._effective_systemd_definition(root)
        a6["systemctl_unavailable"] = False
    except RuntimeError:
        a6["systemctl_unavailable"] = True

    malformed = SimpleNamespace(returncode=0, stdout="Restart=on-failure\n", stderr="")
    try:
        with mock.patch.object(launcher.subprocess, "run", return_value=malformed):
            launcher._effective_systemd_definition(root)
        a6["systemctl_unparseable"] = False
    except RuntimeError:
        a6["systemctl_unparseable"] = True

    record("A6_existing_systemd_contract_fail_closed", all(a6.values()), a6)

    partial_duration_accepted = False
    try:
        partial_duration_accepted = launcher._systemd_duration_seconds("15s garbage") == 15.0
    except ValueError:
        pass
    results["limitations"].append({
        "name": "duration_parser_accepts_trailing_noncanonical_text",
        "observed": partial_duration_accepted,
        "current_unit_reachable": False,
        "reason": "requires noncanonical/corrupted systemctl property text; canonical target-host values are typed systemd renderings",
    })

    # A7 — canonical ordering, stable unknown config binding, no tested semantic collision.
    record("A7_equivalent_execstart_field_order_same_digest",
           digest(root, reordered) == baseline)
    record("A7_unknown_stable_field_value_changes_digest",
           unknown_a_digest != unknown_b_digest)

    accepted_semantic_digests = []
    for variant in semantic_variants.values():
        try:
            accepted_semantic_digests.append(digest(root, variant))
        except RuntimeError:
            pass
    record("A7_no_collision_across_tested_accepted_semantic_drifts",
           baseline not in accepted_semantic_digests and
           len(accepted_semantic_digests) == len(set(accepted_semantic_digests)),
           accepted_semantic_digests)

    equivalent_duration = digest(
        root,
        RestartUSec="15000ms",
        StartLimitIntervalUSec="600s",
        TimeoutStopUSec="30000ms",
    )
    results["limitations"].append({
        "name": "equivalent_duration_text_representation_moves_digest",
        "observed": equivalent_duration != baseline,
        "current_unit_reachable": False,
        "reason": "same systemctl implementation canonically renders a given typed duration; runtime-image drift is separately an entrance invalidator",
    })


# A8 — authority/materialization/child launch order.
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    with mock.patch("quant.dataplane.sec.supervisor.host_boot_id", return_value="boot-a"):
        authority = launcher._write_deployment_authority(root, "fp-a")
        consumed = launcher._consume_deployment_authority(root, "fp-a")
        first_ok = consumed["nonce"] == authority["nonce"] and not launcher.authority_path(root).exists()
        launcher.authority_path(root).write_text(
            json.dumps(authority), encoding="utf-8")
        replay_rejected = False
        try:
            launcher._consume_deployment_authority(root, "fp-a")
        except RuntimeError:
            replay_rejected = True
    record("A8_one_use_authority_replay_rejected", first_ok and replay_rejected)

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    fp_file = root / "var" / "sec" / "acquisition_fingerprint.json"
    fp_file.parent.mkdir(parents=True)
    fp_file.write_text(
        json.dumps({"acquisition_critical_fingerprint": "stale"}), encoding="utf-8")
    ok_run = SimpleNamespace(returncode=0, stdout="", stderr="")
    stale_rejected = False
    with mock.patch.object(launcher, "current_fingerprint", return_value="active"), \
         mock.patch.object(launcher.subprocess, "run", return_value=ok_run):
        try:
            launcher.materialize_if_absent(root, {})
        except RuntimeError:
            stale_rejected = True
    record("A8_stale_materialized_fingerprint_fails_closed", stale_rejected)

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    popen = mock.Mock()
    managed = {"service_managed": True, "invocation_id": "invocation-a"}
    environment = {
        "QUANT_SEC_USER_AGENT": "audit@example.invalid",
        "QUANT_SEC_SERVICE_MANAGER": "systemd",
        "INVOCATION_ID": "invocation-a",
        "QUANT_SEC_SERVICE_POLL_SECONDS": "60",
        "QUANT_SEC_QUALIFYING_MODE": "1",
        "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": "sha256:a",
    }
    with mock.patch.dict(os.environ, {
            "QUANT_SEC_USER_AGENT": "audit@example.invalid",
            "QUANT_SEC_SERVICE_MANAGER": "systemd",
            "INVOCATION_ID": "invocation-a",
        }, clear=True), \
         mock.patch.object(sys, "argv", [
            "quant_sec_supervisor.py", "--root", str(root), "--qualifying"]), \
         mock.patch("quant.dataplane.sec.supervisor.service_manager_provenance",
                    return_value=managed), \
         mock.patch("quant.dataplane.sec.supervisor.host_boot_id",
                    return_value="host-boot-a"), \
         mock.patch.object(launcher, "_effective_environment",
                           return_value=(environment, 60.0)), \
         mock.patch.object(launcher, "current_fingerprint", return_value="fp-a"), \
         mock.patch.object(launcher, "_consume_deployment_authority",
                           return_value={"nonce": "nonce-a"}), \
         mock.patch.object(launcher, "materialize_if_absent",
                           side_effect=RuntimeError("FINGERPRINT_MATERIALIZED_MISMATCH")), \
         mock.patch.object(launcher.subprocess, "Popen", popen), \
         mock.patch.object(launcher.signal, "signal", return_value=signal.SIG_DFL):
        blocked = False
        try:
            launcher.main()
        except RuntimeError as exc:
            blocked = "FINGERPRINT_MATERIALIZED_MISMATCH" in str(exc)
    events = root / "var" / "sec" / "supervisor_events.jsonl"
    record("A8_no_child_or_launch_event_before_materialization_validation",
           blocked and not popen.called and not events.exists(),
           {"blocked": blocked, "popen_called": popen.called, "events_exists": events.exists()})


# A9 — independent discriminant separates old raw behavior from corrected behavior.
record("A9_independent_discriminant_separates_old_raw_from_v4",
       old_before != old_after and
       bool(results["attacks"]["A2_each_transient_field_stable"]["ok"]))


# A10 — second-order source inspection.
source = (ROOT / "deploy" / "quant_sec_supervisor.py").read_text(encoding="utf-8")
known_transients = {"start_time", "stop_time", "pid", "code", "status"}
record("A10_all_known_execstart_runtime_observations_excluded",
       set(launcher._EXEC_START_TRANSIENT_KEYS) == known_transients,
       sorted(launcher._EXEC_START_TRANSIENT_KEYS))
record("A10_effective_unit_digest_remains_fingerprint_bound",
       "QUANT_SEC_EFFECTIVE_UNIT_DIGEST" in source and
       'parsed["ExecStart"] = exec_start_entries' in source)


results["failures"] = failures
results["overall"] = "PASS_CURRENT_UNIT_REPOSITORY_PROBE" if not failures else "FAIL"
out = ROOT / "astra_gate_a_v4_probe_results.json"
out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2, sort_keys=True))
raise SystemExit(1 if failures else 0)
