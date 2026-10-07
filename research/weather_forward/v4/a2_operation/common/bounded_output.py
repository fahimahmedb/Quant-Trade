"""Bounded, non-overwriting result write shared by the operation and its qualification.

The payload is fully encoded and size-checked in memory before any file is
created. A write goes to a dot-prefixed partial name and is then hard-linked to
the final name, so an interrupted write never leaves a file under the final
name. An existing final file is never overwritten. The ``_os`` parameter exists
only so tests can substitute a synthetic filesystem; production uses ``os``.
"""
from __future__ import annotations

import json
import os
import re

MAX_RESULT_BYTES = 65536
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
PARTIAL_PREFIX = ".partial-"


class OutputLimitExceeded(Exception):
    """The encoded payload is larger than the permitted output bound."""


class OutputTargetExists(Exception):
    """A file with the final result name already exists."""


class InvalidOutputName(Exception):
    """The requested result name is not a single safe file name."""


def encode_result(value: object) -> bytes:
    """Deterministic ASCII JSON encoding with a trailing newline."""
    text = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return text.encode("ascii") + b"\n"


def partial_name(final_name: str) -> str:
    return PARTIAL_PREFIX + final_name


def write_bounded(directory: str, final_name: str, payload: bytes, *,
                  max_bytes: int = MAX_RESULT_BYTES, _os=os) -> int:
    """Write ``payload`` to ``directory/final_name``; return the byte count.

    Raises before touching the filesystem when the payload type, size or name
    is not acceptable.
    """
    if type(payload) is not bytes:
        raise TypeError("BYTES_PAYLOAD_REQUIRED")
    if type(max_bytes) is not int or max_bytes < 0:
        raise ValueError("NON_NEGATIVE_INTEGER_BOUND_REQUIRED")
    if len(payload) > max_bytes:
        raise OutputLimitExceeded(f"PAYLOAD_{len(payload)}_EXCEEDS_{max_bytes}")
    if type(final_name) is not str or not _NAME_PATTERN.match(final_name):
        raise InvalidOutputName("SINGLE_SAFE_FILE_NAME_REQUIRED")
    final_path = _os.path.join(directory, final_name)
    partial_path = _os.path.join(directory, partial_name(final_name))
    if _os.path.lexists(final_path):
        raise OutputTargetExists(final_name)
    flags = _os.O_WRONLY | _os.O_CREAT | _os.O_EXCL | getattr(_os, "O_NOFOLLOW", 0)
    descriptor = _os.open(partial_path, flags, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = _os.write(descriptor, view)
            if written <= 0:
                raise OSError("SHORT_WRITE")
            view = view[written:]
        _os.fsync(descriptor)
    except BaseException:
        _os.close(descriptor)
        _os.unlink(partial_path)
        raise
    _os.close(descriptor)
    try:
        _os.link(partial_path, final_path)
    finally:
        _os.unlink(partial_path)
    return len(payload)
