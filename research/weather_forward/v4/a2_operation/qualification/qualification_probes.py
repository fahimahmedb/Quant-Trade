"""Dummy qualification probes for the lot-2 resource controls (L2-A0 / L2-A).

Each probe deliberately attempts one forbidden behaviour so the operator can
check, on the designated host, that the systemd profile stops or refuses it.
No probe imports the A2 harness, reads data or contacts a real endpoint: the
network probe only targets the RFC 5737 / RFC 3849 documentation ranges.

stdout and stderr are expected to be discarded by the unit profile. A probe
records its own observation through the shared bounded writer as
``qual-<probe>.json`` in the writable directory when it can; probes that are
expected to be killed write only if they were NOT stopped.

Probe exit codes: 0 forbidden behaviour completed (control NOT effective);
20 forbidden behaviour refused as expected; 21 positive control completed;
1 unexpected probe error.
"""
from __future__ import annotations

import argparse
import errno
import os
from pathlib import Path
import socket
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT))

from research.weather_forward.v4.a2_operation.common import bounded_output  # noqa: E402

EXIT_FORBIDDEN_COMPLETED = 0
EXIT_REFUSED_AS_EXPECTED = 20
EXIT_POSITIVE_OK = 21
EXIT_PROBE_ERROR = 1
DOCUMENTATION_TARGETS = (("192.0.2.1", 9), ("198.51.100.1", 9))
DOCUMENTATION_TARGET_V6 = ("2001:db8::1", 9)


def record(out_dir: str, probe: str, observation: dict) -> None:
    payload = bounded_output.encode_result({"probe": probe, "observation": observation})
    bounded_output.write_bounded(out_dir, f"qual-{probe}.json", payload)


def probe_time(out_dir):
    time.sleep(120)
    record(out_dir, "time", {"slept_seconds": 120, "stopped": False})
    return EXIT_FORBIDDEN_COMPLETED


def probe_cpu(out_dir):
    while True:
        times = os.times()
        if times.user + times.system >= 30.0:
            break
    record(out_dir, "cpu", {"cpu_seconds": round(times.user + times.system, 3), "stopped": False})
    return EXIT_FORBIDDEN_COMPLETED


def probe_memory(out_dir):
    chunks = []
    for _ in range(25):  # 25 x 8 MiB = 200 MiB of touched pages
        chunk = bytearray(8 * 1024 * 1024)
        for offset in range(0, len(chunk), 4096):
            chunk[offset] = 1
        chunks.append(chunk)
    record(out_dir, "memory", {"allocated_mib": 200, "stopped": False})
    return EXIT_FORBIDDEN_COMPLETED


def probe_child(out_dir):
    observation = {}
    try:
        pid = os.fork()
    except OSError as error:
        observation["fork"] = errno.errorcode.get(error.errno, str(error.errno))
    else:
        if pid == 0:
            os._exit(0)
        os.waitpid(pid, 0)
        observation["fork"] = "CREATED"
    try:
        import threading
        thread = threading.Thread(target=lambda: None)
        thread.start()
        thread.join()
        observation["thread"] = "CREATED"
    except (RuntimeError, OSError) as error:
        observation["thread"] = type(error).__name__
    record(out_dir, "child", observation)
    return EXIT_FORBIDDEN_COMPLETED if observation["fork"] == "CREATED" else EXIT_REFUSED_AS_EXPECTED


def _attempt(family, kind, target):
    try:
        sock = socket.socket(family, kind)
    except OSError as error:
        return "SOCKET_" + errno.errorcode.get(error.errno, str(error.errno))
    try:
        sock.settimeout(2.0)
        if kind == socket.SOCK_DGRAM:
            sock.sendto(b"x", target)
            return "SENT"
        sock.connect(target)
        return "CONNECTED"
    except OSError as error:
        return errno.errorcode.get(error.errno, type(error).__name__) if error.errno else type(error).__name__
    finally:
        sock.close()


def probe_network(out_dir):
    try:
        interfaces = sorted(os.listdir("/sys/class/net"))
    except OSError as error:
        interfaces = ["UNREADABLE_" + errno.errorcode.get(error.errno, "?")]
    attempts = {}
    for host, port in DOCUMENTATION_TARGETS:
        attempts[f"udp:{host}"] = _attempt(socket.AF_INET, socket.SOCK_DGRAM, (host, port))
        attempts[f"tcp:{host}"] = _attempt(socket.AF_INET, socket.SOCK_STREAM, (host, port))
    attempts["udp6:" + DOCUMENTATION_TARGET_V6[0]] = _attempt(
        socket.AF_INET6, socket.SOCK_DGRAM, DOCUMENTATION_TARGET_V6)
    reached = any(value in ("SENT", "CONNECTED") for value in attempts.values())
    record(out_dir, "network", {"interfaces": interfaces, "attempts": attempts})
    return EXIT_FORBIDDEN_COMPLETED if reached else EXIT_REFUSED_AS_EXPECTED


def probe_write(out_dir):
    observation = {}
    fill = os.path.join(out_dir, "fill.bin")
    written = 0
    try:
        with open(fill, "wb") as handle:
            block = b"\0" * 65536
            while written < 2 * 1024 * 1024:
                handle.write(block)
                handle.flush()
                os.fsync(handle.fileno())
                written += len(block)
        observation["fill"] = "COMPLETED_2_MIB"
    except OSError as error:
        observation["fill"] = errno.errorcode.get(error.errno, str(error.errno))
    finally:
        observation["fill_bytes_before_stop"] = written
        try:
            os.unlink(fill)
        except OSError:
            pass
    escapes = {}
    for directory in ("/tmp", "/var/tmp", "/dev/shm", str(REPO_ROOT), "/home", "/root",
                      os.path.expanduser("~")):
        target = os.path.join(directory, "a2qual-escape-probe")
        try:
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except OSError as error:
            escapes[directory] = errno.errorcode.get(error.errno, str(error.errno))
        else:
            os.close(descriptor)
            os.unlink(target)
            escapes[directory] = "CREATED"
    observation["outside_writable_directory"] = escapes
    record(out_dir, "write", observation)
    breached = observation["fill"] == "COMPLETED_2_MIB" or "CREATED" in escapes.values()
    return EXIT_FORBIDDEN_COMPLETED if breached else EXIT_REFUSED_AS_EXPECTED


def probe_output(out_dir):
    big = b"x" * (100 * 1024)
    observation = {}
    try:
        bounded_output.write_bounded(out_dir, "qual-output-oversize.json", big)
        observation["bounded_writer"] = "WRITTEN"
    except bounded_output.OutputLimitExceeded:
        observation["bounded_writer"] = "REFUSED"
    observation["oversize_file_present"] = os.path.lexists(
        os.path.join(out_dir, "qual-output-oversize.json"))
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.write("A2QUAL-STDIO-MARKER " + "y" * (100 * 1024) + "\n")
            stream.flush()
        except (OSError, ValueError):
            pass
    record(out_dir, "output", observation)
    refused = observation["bounded_writer"] == "REFUSED" and not observation["oversize_file_present"]
    return EXIT_REFUSED_AS_EXPECTED if refused else EXIT_FORBIDDEN_COMPLETED


READ_EXPECTATIONS = {
    # directory: exact visible names allowed, or None when it must be unreadable/empty
    "/opt": ["a2"],
    "/srv": ["a2out"],
    "/home": None,
    "/root": None,
    "/var": None,
    "/mnt": None,
    "/media": None,
    "/tmp": None,
    "/dev/shm": None,
}


def probe_read(out_dir):
    """Directory-level read isolation; records names only, never file contents."""
    observation = {}
    breached = False
    for directory, allowed in READ_EXPECTATIONS.items():
        try:
            names = sorted(os.listdir(directory))
        except OSError as error:
            observation[directory] = errno.errorcode.get(error.errno, str(error.errno))
            if allowed is not None:
                breached = True  # required path not visible: profile not as designed
            continue
        observation[directory] = names
        if allowed is None:
            breached = breached or bool(names)
        else:
            breached = breached or names != allowed
    record(out_dir, "read", observation)
    return EXIT_FORBIDDEN_COMPLETED if breached else EXIT_REFUSED_AS_EXPECTED


def _cgroup_values():
    values = {}
    try:
        with open("/proc/self/cgroup", "r", encoding="ascii") as handle:
            lines = handle.read().splitlines()
        path = next(line.split(":", 2)[2] for line in lines if line.startswith("0::"))
        base = "/sys/fs/cgroup" + path
    except (OSError, StopIteration, ValueError) as error:
        return {"cgroup": "UNAVAILABLE_" + type(error).__name__}
    for name in ("memory.peak", "memory.max", "memory.swap.max", "memory.swap.peak",
                 "pids.max", "pids.peak", "memory.events"):
        try:
            with open(os.path.join(base, name), "r", encoding="ascii") as handle:
                values[name] = handle.read().strip()
        except OSError as error:
            values[name] = "UNAVAILABLE_" + errno.errorcode.get(error.errno, "?")
    return values


def probe_positive(out_dir):
    started = time.monotonic()
    total = sum(index * index for index in range(200000))
    times = os.times()
    record(out_dir, "positive", {
        "checksum_mod_97": total % 97,
        "wall_seconds": round(time.monotonic() - started, 3),
        "cpu_seconds": round(times.user + times.system, 3),
        "cgroup": _cgroup_values(),
        "python": sys.version.split()[0],
    })
    return EXIT_POSITIVE_OK


PROBES = {
    "time": probe_time, "cpu": probe_cpu, "memory": probe_memory, "child": probe_child,
    "network": probe_network, "write": probe_write, "output": probe_output,
    "read": probe_read, "positive": probe_positive,
}


def main(argv) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--probe", required=True, choices=sorted(PROBES))
    parser.add_argument("--out-dir", default="/srv/a2out")
    options = parser.parse_args(argv)
    try:
        return PROBES[options.probe](options.out_dir)
    except Exception:  # noqa: BLE001 - reported only through the exit code
        return EXIT_PROBE_ERROR


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
