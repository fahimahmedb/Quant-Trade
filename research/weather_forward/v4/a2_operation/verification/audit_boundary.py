"""Pure decisions for the offline test audit hook; no OS calls or side effects.

This audits a cooperative Python process. It is not a system sandbox or proof
of isolation on the designated VM. Tests exercise decisions without attempting
forbidden operations in the audited process.
"""
from __future__ import annotations

import os

NETWORK_PREFIXES = ("socket.", "http.client.", "urllib.", "ftplib.", "smtplib.",
                    "imaplib.", "poplib.", "nntplib.", "telnetlib.", "webbrowser.")
PROCESS_EVENTS = frozenset({"subprocess.Popen", "os.system", "os.posix_spawn",
    "os.posix_spawnp", "os.exec", "os.fork", "os.forkpty", "os.spawn",
    "os.startfile", "pty.spawn"})
MUTATION_EVENTS = frozenset({"os.remove", "os.unlink", "os.rename", "os.replace",
    "os.link", "os.symlink", "os.mkdir", "os.rmdir", "os.chmod", "os.chown",
    "os.truncate", "os.utime", "shutil.rmtree", "shutil.copyfile", "os.chdir"})


def _stdlib_source(path, root):
    return (path.startswith(root + os.sep)
            and not {"site-packages", "dist-packages"}.intersection(path.split(os.sep))
            and path.endswith((".py", ".so")))


def decide(event, args, *, allowed_reads, expected_caches, stdlib_root):
    if event.startswith(NETWORK_PREFIXES):
        return "NETWORK"
    if event in PROCESS_EVENTS:
        return "SUBPROCESS"
    if event in MUTATION_EVENTS:
        return "FILE_MUTATION"
    if event == "import" and len(args) > 1 and args[1]:
        path = os.path.realpath(args[1])
        return "ALLOW" if path in allowed_reads or _stdlib_source(path, stdlib_root) else "FILE_READ"
    if event != "open":
        return "ALLOW"
    path, mode, flags = args
    if not isinstance(path, (str, bytes)):
        return "FD_OPEN"
    path = os.path.realpath(os.fsdecode(path))
    writes = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
    if (flags is not None and flags & writes) or (mode and any(c in mode for c in "wax+")):
        return "FILE_WRITE"
    if path in expected_caches:
        return "EXPECTED_CACHE_REFUSAL"
    if path.endswith(".pyc") and path.startswith(stdlib_root + os.sep) \
            and not {"site-packages", "dist-packages"}.intersection(path.split(os.sep)):
        return "EXPECTED_CACHE_REFUSAL"
    return "ALLOW" if path in allowed_reads or _stdlib_source(path, stdlib_root) else "FILE_READ"
