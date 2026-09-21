#!/usr/bin/env python3
"""Fail-closed Gate-B run registry / activation consumer (M1-M3)."""
from __future__ import annotations

import contextlib
import datetime as dt
import errno
import fcntl
import hashlib
import json
import os
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable

REGISTRY_SCHEMA = "quant-gate-b-run-registry/v1"
ACTIVATION_SCHEMA = "quant-gate-b-activation/v1"
RECEIPT_SCHEMA = "quant-gate-b-consumption-receipt/v1"
EVIDENCE_BINDING_SCHEMA = "quant-gate-b-evidence-binding/v1"

ZERO = "sha256:" + "0" * 64
SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
HEX = re.compile(r"^[0-9a-f]{40}$")
RID = re.compile(r"^gate-b-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
ARTIFACT_TYPE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
TERMINAL = {"RUN_COMPLETED", "RUN_BLOCKED_TERMINAL", "FAILED_TERMINAL"}


class AuthorityError(RuntimeError):
    pass


def canonical_json_bytes(o: Any) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256_digest(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def utc_text(v: dt.datetime | None = None) -> str:
    return (
        (v or dt.datetime.now(dt.timezone.utc))
        .astimezone(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _time(s: str) -> dt.datetime:
    if not isinstance(s, str) or not s.endswith("Z"):
        raise AuthorityError("invalid UTC timestamp")
    try:
        parsed = dt.datetime.fromisoformat(s[:-1] + "+00:00")
    except ValueError as e:
        raise AuthorityError("invalid UTC timestamp") from e
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise AuthorityError("invalid UTC timestamp")
    return parsed.astimezone(dt.timezone.utc)


def _cand(o: dict[str, Any]) -> tuple[str, str, str]:
    c = (o.get("candidate_sha"), o.get("git_tree"), o.get("verified_input_tree_digest"))
    if (
        not all(isinstance(x, str) for x in c)
        or not HEX.fullmatch(c[0])
        or not HEX.fullmatch(c[1])
        or not SHA.fullmatch(c[2])
    ):
        raise AuthorityError("invalid candidate identity")
    return c


def _inside(p: Path, root: Path) -> bool:
    try:
        return os.path.commonpath([str(p.resolve(strict=False)), str(root.resolve())]) == str(root.resolve())
    except ValueError:
        return False


def _seal(e: dict[str, Any]) -> dict[str, Any]:
    x = dict(e)
    x["event_digest"] = sha256_digest(canonical_json_bytes(x))
    return x


def _state(es: list[dict[str, Any]], rid: str) -> str | None:
    xs = [e["event_type"] for e in es if e.get("run_id") == rid]
    return xs[-1] if xs else None


def _reserve(es: list[dict[str, Any]], rid: str) -> dict[str, Any] | None:
    return next((e for e in es if e["event_type"] == "RUN_RESERVED" and e.get("run_id") == rid), None)


def _epoch(es: list[dict[str, Any]]) -> tuple[int, str] | None:
    xs = [e for e in es if e["event_type"] == "REVOCATION_EPOCH_SET"]
    return (xs[-1]["revocation_epoch"], xs[-1]["revocation_reference"]) if xs else None


def _strict_artifact_type(value: Any) -> str:
    if not isinstance(value, str) or not ARTIFACT_TYPE.fullmatch(value):
        raise AuthorityError("invalid artifact type")
    return value


def _write_all(fd: int, data: bytes) -> None:
    """Write every byte or fail; retry EINTR and reject zero progress."""
    view = memoryview(data)
    offset = 0
    while offset < len(view):
        try:
            written = os.write(fd, view[offset:])
        except InterruptedError:
            continue
        except OSError as e:
            if e.errno == errno.EINTR:
                continue
            raise AuthorityError("write failed") from e
        if not isinstance(written, int) or written <= 0:
            raise AuthorityError("write made zero progress")
        offset += written


def _fsync_dir(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _read_exact_regular(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def load_registry(p: Path) -> list[dict[str, Any]]:
    if not p.exists():
        return []
    if p.is_symlink() or not p.is_file():
        raise AuthorityError("registry must be regular non-symlink file")
    b = p.read_bytes()
    if b and not b.endswith(b"\n"):
        raise AuthorityError("registry is truncated")
    out: list[dict[str, Any]] = []
    for i, line in enumerate(b.splitlines(), 1):
        try:
            o = json.loads(line)
        except Exception as e:
            raise AuthorityError(f"registry line {i} malformed") from e
        if not isinstance(o, dict) or canonical_json_bytes(o) != line:
            raise AuthorityError(f"registry line {i} malformed/noncanonical")
        out.append(o)
    validate_registry(out)
    return out


def validate_registry(es: list[dict[str, Any]]) -> None:
    prev = ZERO
    last: dict[str, str] = {}
    rs: dict[str, dict[str, Any]] = {}
    states: dict[str, str] = {}
    attempts: dict[tuple[str, str, str, str], int] = {}
    acts: dict[str, str] = {}
    consumed: dict[str, str] = {}
    arts: dict[str, str] = {}
    ords: set[tuple[str, int]] = set()
    ep: tuple[int, str] | None = None

    for i, e in enumerate(es, 1):
        if e.get("schema") != REGISTRY_SCHEMA or not isinstance(e.get("event_type"), str):
            raise AuthorityError(f"registry event {i} malformed")
        d = e.get("event_digest")
        u = dict(e)
        u.pop("event_digest", None)
        if (
            e.get("prev_registry_digest") != prev
            or not isinstance(d, str)
            or not SHA.fullmatch(d)
            or sha256_digest(canonical_json_bytes(u)) != d
        ):
            raise AuthorityError(f"registry event {i} digest mismatch")
        prev = d
        t = e["event_type"]

        if t == "REVOCATION_EPOCH_SET":
            x = e.get("revocation_epoch")
            r = e.get("revocation_reference")
            if (
                not isinstance(x, int)
                or isinstance(x, bool)
                or x < 0
                or not isinstance(r, str)
                or not r
                or (ep and x <= ep[0])
            ):
                raise AuthorityError("revocation epoch invalid/nonmonotonic")
            ep = (x, r)
            continue

        if t == "ACTIVATION_REVOKED":
            if (
                not ep
                or (e.get("revocation_epoch"), e.get("revocation_reference")) != ep
                or not isinstance(e.get("revoked_activation_id"), str)
                or not e.get("revoked_activation_id")
            ):
                raise AuthorityError("activation revocation stale/malformed")
            continue

        rid = e.get("run_id")
        a = e.get("attempt_number")
        host = e.get("target_host_opaque_id")
        if (
            not isinstance(rid, str)
            or not RID.fullmatch(rid)
            or not isinstance(a, int)
            or isinstance(a, bool)
            or a < 1
            or not isinstance(host, str)
            or not host
        ):
            raise AuthorityError("run fields invalid")
        if e.get("prev_run_event_digest") != last.get(rid, ZERO):
            raise AuthorityError("per-run digest mismatch")
        last[rid] = d
        _cand(e)

        if t == "RUN_RESERVED":
            if rid in rs:
                raise AuthorityError("duplicate run id")
            key = (*_cand(e), host)
            expected = attempts.get(key, 0) + 1
            if a != expected:
                raise AuthorityError("attempt not monotonic")
            if any(states[r] not in TERMINAL and rs[r]["target_host_opaque_id"] == host for r in rs):
                raise AuthorityError("concurrent nonterminal mutating run")
            rs[rid] = e
            states[rid] = t
            attempts[key] = a
            continue

        r = rs.get(rid)
        if not r:
            raise AuthorityError(f"{t} without reservation")
        for k in ("attempt_number", "candidate_sha", "git_tree", "verified_input_tree_digest", "target_host_opaque_id"):
            if e.get(k) != r[k]:
                raise AuthorityError("reserved identity changed")
        if e.get("reservation_digest") != r["event_digest"]:
            raise AuthorityError("reservation digest mismatch")
        if states[rid] in TERMINAL:
            raise AuthorityError("event after terminal run")

        if t == "ACTIVATION_SEALED":
            ad = e.get("activation_digest")
            aid = e.get("activation_id")
            if (
                states[rid] != "RUN_RESERVED"
                or not isinstance(ad, str)
                or not SHA.fullmatch(ad)
                or not isinstance(aid, str)
                or not aid
                or ad in acts
                or any(x.get("activation_id") == aid for x in es[: i - 1])
            ):
                raise AuthorityError("activation reused/invalid")
            if not ep or (e.get("revocation_epoch"), e.get("revocation_reference")) != ep:
                raise AuthorityError("activation stale")
            acts[ad] = rid
            states[rid] = t
            continue

        if t == "ACTIVATION_CONSUMED":
            ad = e.get("activation_digest")
            if (
                states[rid] != "ACTIVATION_SEALED"
                or not isinstance(ad, str)
                or acts.get(ad) != rid
                or not SHA.fullmatch(e.get("receipt_digest", ""))
            ):
                raise AuthorityError("invalid/second activation consumption")
            consumed[rid] = ad
            states[rid] = t
            continue

        if t == "EVIDENCE_BOUND":
            art = e.get("artifact_digest")
            ordinal = e.get("artifact_ordinal")
            activation_digest = e.get("activation_digest")
            if (
                states[rid] != "ACTIVATION_CONSUMED"
                or not isinstance(art, str)
                or not SHA.fullmatch(art)
                or not SHA.fullmatch(e.get("binding_digest", ""))
                or not isinstance(activation_digest, str)
                or activation_digest != consumed.get(rid)
                or not isinstance(ordinal, int)
                or isinstance(ordinal, bool)
                or ordinal < 1
            ):
                raise AuthorityError("invalid evidence binding")
            _strict_artifact_type(e.get("artifact_type"))
            if art in arts and arts[art] != rid:
                raise AuthorityError("artifact belongs to another run")
            if (rid, ordinal) in ords:
                raise AuthorityError("duplicate evidence ordinal")
            arts[art] = rid
            ords.add((rid, ordinal))
            continue

        if t in TERMINAL:
            if t == "FAILED_TERMINAL" and rid not in consumed:
                raise AuthorityError("FAILED_TERMINAL requires consumed activation")
            states[rid] = t
            continue

        raise AuthorityError("unknown registry event")


def _activation(raw: bytes, digest: str) -> dict[str, Any]:
    if not isinstance(digest, str) or not SHA.fullmatch(digest) or sha256_digest(raw) != digest:
        raise AuthorityError("activation digest mismatch")
    try:
        a = json.loads(raw)
    except Exception as e:
        raise AuthorityError("activation malformed") from e
    keys = {
        "schema",
        "activation_id",
        "run_id",
        "attempt_number",
        "reservation_digest",
        "candidate_sha",
        "git_tree",
        "verified_input_tree_digest",
        "target_host_opaque_id",
        "issued_at_utc",
        "not_before_utc",
        "expires_at_utc",
        "revocation_epoch",
        "revocation_reference",
        "gate_b_mutation_authorized",
    }
    if (
        not isinstance(a, dict)
        or canonical_json_bytes(a) != raw
        or set(a) != keys
        or a.get("schema") != ACTIVATION_SCHEMA
        or a.get("gate_b_mutation_authorized") is not True
    ):
        raise AuthorityError("activation schema/fields invalid")
    if not isinstance(a.get("activation_id"), str) or not a["activation_id"]:
        raise AuthorityError("activation schema/fields invalid")
    if not isinstance(a.get("run_id"), str) or not RID.fullmatch(a["run_id"]):
        raise AuthorityError("activation schema/fields invalid")
    if not isinstance(a.get("attempt_number"), int) or isinstance(a["attempt_number"], bool) or a["attempt_number"] < 1:
        raise AuthorityError("activation schema/fields invalid")
    if not isinstance(a.get("reservation_digest"), str) or not SHA.fullmatch(a["reservation_digest"]):
        raise AuthorityError("activation schema/fields invalid")
    if not isinstance(a.get("target_host_opaque_id"), str) or not a["target_host_opaque_id"]:
        raise AuthorityError("activation schema/fields invalid")
    if not isinstance(a.get("revocation_epoch"), int) or isinstance(a["revocation_epoch"], bool) or a["revocation_epoch"] < 0:
        raise AuthorityError("activation schema/fields invalid")
    if not isinstance(a.get("revocation_reference"), str) or not a["revocation_reference"]:
        raise AuthorityError("activation schema/fields invalid")
    _cand(a)
    _time(a["issued_at_utc"])
    _time(a["not_before_utc"])
    _time(a["expires_at_utc"])
    return a


def _binding(raw: bytes, digest: str) -> dict[str, Any]:
    if not isinstance(digest, str) or not SHA.fullmatch(digest) or sha256_digest(raw) != digest:
        raise AuthorityError("binding digest mismatch")
    try:
        b = json.loads(raw)
    except Exception as e:
        raise AuthorityError("binding malformed") from e
    keys = {
        "schema",
        "run_id",
        "attempt_number",
        "activation_digest",
        "reservation_digest",
        "candidate_sha",
        "git_tree",
        "verified_input_tree_digest",
        "target_host_opaque_id",
        "artifact_type",
        "artifact_ordinal",
        "artifact_digest",
        "created_at_utc",
    }
    if (
        not isinstance(b, dict)
        or canonical_json_bytes(b) != raw
        or set(b) != keys
        or b.get("schema") != EVIDENCE_BINDING_SCHEMA
    ):
        raise AuthorityError("binding malformed")
    if not isinstance(b.get("run_id"), str) or not RID.fullmatch(b["run_id"]):
        raise AuthorityError("binding malformed")
    if not isinstance(b.get("attempt_number"), int) or isinstance(b["attempt_number"], bool) or b["attempt_number"] < 1:
        raise AuthorityError("binding malformed")
    for key in ("activation_digest", "reservation_digest", "artifact_digest"):
        if not isinstance(b.get(key), str) or not SHA.fullmatch(b[key]):
            raise AuthorityError("binding malformed")
    if not isinstance(b.get("target_host_opaque_id"), str) or not b["target_host_opaque_id"]:
        raise AuthorityError("binding malformed")
    ordinal = b.get("artifact_ordinal")
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 1:
        raise AuthorityError("binding artifact ordinal invalid")
    _strict_artifact_type(b.get("artifact_type"))
    _cand(b)
    _time(b["created_at_utc"])
    return b


class Registry:
    def __init__(self, path: Path, source_checkout: Path):
        self.path = Path(path)
        self.checkout = Path(source_checkout).resolve()
        self.lock = Path(str(path) + ".lock")
        if _inside(self.path, self.checkout):
            raise AuthorityError("registry must be outside source checkout")

    @contextlib.contextmanager
    def _locked(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(
            self.lock,
            os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        try:
            if self.lock.is_symlink():
                raise AuthorityError("lock symlink rejected")
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def _append(self, es: list[dict[str, Any]], e: dict[str, Any]) -> dict[str, Any]:
        payload = dict(e)
        event_time_utc = payload.pop("event_time_utc", utc_text())
        x = {
            "schema": REGISTRY_SCHEMA,
            "event_time_utc": event_time_utc,
            "prev_registry_digest": es[-1]["event_digest"] if es else ZERO,
            **payload,
        }
        if x.get("run_id"):
            x["prev_run_event_digest"] = next(
                (z["event_digest"] for z in reversed(es) if z.get("run_id") == x["run_id"]),
                ZERO,
            )
        x = _seal(x)
        validate_registry(es + [x])
        data = canonical_json_bytes(x) + b"\n"
        existed_before = os.path.lexists(self.path)
        fd = os.open(
            self.path,
            os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        try:
            _write_all(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)
        if not existed_before:
            _fsync_dir(self.path.parent)
        return x

    def _mut(self, fn):
        with self._locked():
            return fn(load_registry(self.path))

    def set_revocation_epoch(self, *, epoch, reference, event_time=None):
        return self._mut(
            lambda es: self._append(
                es,
                {
                    "event_type": "REVOCATION_EPOCH_SET",
                    "event_time_utc": utc_text(event_time),
                    "revocation_epoch": epoch,
                    "revocation_reference": reference,
                },
            )
        )

    def reserve(
        self,
        *,
        candidate_sha,
        git_tree,
        verified_input_tree_digest,
        target_host_opaque_id,
        blue_reference,
        operator_identity_reference,
        run_id_factory: Callable[[], str] = lambda: f"gate-b-{uuid.uuid4()}",
        event_time=None,
    ):
        def f(es):
            rid = run_id_factory()
            base = {
                "candidate_sha": candidate_sha,
                "git_tree": git_tree,
                "verified_input_tree_digest": verified_input_tree_digest,
                "target_host_opaque_id": target_host_opaque_id,
            }
            _cand(base)
            if _reserve(es, rid):
                raise AuthorityError("duplicate run id")
            key = (*_cand(base), target_host_opaque_id)
            prev = [
                x["attempt_number"]
                for x in es
                if x["event_type"] == "RUN_RESERVED"
                and (*_cand(x), x["target_host_opaque_id"]) == key
            ]
            return self._append(
                es,
                {
                    "event_type": "RUN_RESERVED",
                    "event_time_utc": utc_text(event_time),
                    "run_id": rid,
                    "attempt_number": max(prev, default=0) + 1,
                    **base,
                    "blue_reference": blue_reference,
                    "operator_identity_reference": operator_identity_reference,
                },
            )

        return self._mut(f)

    def revoke_activation(self, *, activation_id, reference=None, event_time=None):
        def f(es):
            ep = _epoch(es)
            if not ep:
                raise AuthorityError("revocation authority not initialized")
            return self._append(
                es,
                {
                    "event_type": "ACTIVATION_REVOKED",
                    "event_time_utc": utc_text(event_time),
                    "revoked_activation_id": activation_id,
                    "revocation_epoch": ep[0],
                    "revocation_reference": reference or ep[1],
                },
            )

        return self._mut(f)

    def seal_activation(self, *, activation_bytes, activation_digest, event_time=None):
        a = _activation(activation_bytes, activation_digest)

        def f(es):
            r = _reserve(es, a["run_id"])
            if not r:
                raise AuthorityError("reservation missing")
            for k in (
                "attempt_number",
                "candidate_sha",
                "git_tree",
                "verified_input_tree_digest",
                "target_host_opaque_id",
            ):
                if a[k] != r[k]:
                    raise AuthorityError("activation reservation mismatch")
            if (
                a["reservation_digest"] != r["event_digest"]
                or _epoch(es) != (a["revocation_epoch"], a["revocation_reference"])
            ):
                raise AuthorityError("activation stale/reservation mismatch")
            return self._append(
                es,
                {
                    "event_type": "ACTIVATION_SEALED",
                    "event_time_utc": utc_text(event_time),
                    **{
                        k: r[k]
                        for k in (
                            "run_id",
                            "attempt_number",
                            "candidate_sha",
                            "git_tree",
                            "verified_input_tree_digest",
                            "target_host_opaque_id",
                        )
                    },
                    "reservation_digest": r["event_digest"],
                    "activation_digest": activation_digest,
                    "activation_id": a["activation_id"],
                    "revocation_epoch": a["revocation_epoch"],
                    "revocation_reference": a["revocation_reference"],
                },
            )

        return self._mut(f)

    def consume_activation(
        self,
        *,
        activation_bytes,
        activation_digest,
        receipt_dir: Path,
        expected_run_id,
        expected_candidate=None,
        now=None,
    ):
        a = _activation(activation_bytes, activation_digest)

        def f(es):
            # Production time authority is acquired only after the exclusive flock is held.
            decision_now = (
                now if now is not None else dt.datetime.now(dt.timezone.utc)
            ).astimezone(dt.timezone.utc)
            issued = _time(a["issued_at_utc"])
            not_before = _time(a["not_before_utc"])
            expires = _time(a["expires_at_utc"])

            r = _reserve(es, a["run_id"])
            if not r:
                raise AuthorityError("reservation missing")
            if any(
                x["event_type"] == "ACTIVATION_CONSUMED" and x.get("run_id") == a["run_id"]
                for x in es
            ):
                raise AuthorityError("activation has already been consumed")
            if _state(es, a["run_id"]) != "ACTIVATION_SEALED" or a["run_id"] != expected_run_id:
                raise AuthorityError("activation not sealed/run mismatch")
            if expected_candidate and _cand(a) != expected_candidate:
                raise AuthorityError("activation does not match expected candidate")
            if _epoch(es) != (a["revocation_epoch"], a["revocation_reference"]):
                raise AuthorityError("activation is stale")
            if any(
                x["event_type"] == "ACTIVATION_REVOKED"
                and x.get("revoked_activation_id") == a["activation_id"]
                for x in es
            ):
                raise AuthorityError("activation explicitly revoked")
            if issued > decision_now:
                raise AuthorityError("activation issued in the future")
            if not (issued <= not_before < expires):
                raise AuthorityError("activation chronology invalid")
            if decision_now < not_before:
                raise AuthorityError("activation is not yet valid")
            if decision_now >= expires:
                raise AuthorityError("activation is stale/expired")

            receipt = {
                "schema": RECEIPT_SCHEMA,
                "run_id": a["run_id"],
                "attempt_number": a["attempt_number"],
                "activation_id": a["activation_id"],
                "activation_digest": activation_digest,
                "reservation_digest": r["event_digest"],
                "candidate_sha": a["candidate_sha"],
                "git_tree": a["git_tree"],
                "verified_input_tree_digest": a["verified_input_tree_digest"],
                "target_host_opaque_id": a["target_host_opaque_id"],
                "consumed_at_utc": utc_text(decision_now),
            }
            rb = canonical_json_bytes(receipt) + b"\n"
            rd = sha256_digest(rb)
            p = Path(receipt_dir) / (rd.split(":", 1)[1] + ".json")
            ev = self._append(
                es,
                {
                    "event_type": "ACTIVATION_CONSUMED",
                    "event_time_utc": utc_text(decision_now),
                    **{
                        k: r[k]
                        for k in (
                            "run_id",
                            "attempt_number",
                            "candidate_sha",
                            "git_tree",
                            "verified_input_tree_digest",
                            "target_host_opaque_id",
                        )
                    },
                    "reservation_digest": r["event_digest"],
                    "activation_digest": activation_digest,
                    "receipt_digest": rd,
                    "receipt_reference": str(p),
                },
            )
            _write_once(p, rb)
            return ev, {"path": str(p), "digest": rd}

        return self._mut(f)

    def bind_evidence(self, *, binding_bytes, binding_digest, event_time=None):
        b = _binding(binding_bytes, binding_digest)

        def f(es):
            r = _reserve(es, b["run_id"])
            consumed = next(
                (
                    x
                    for x in reversed(es)
                    if x["event_type"] == "ACTIVATION_CONSUMED" and x.get("run_id") == b["run_id"]
                ),
                None,
            )
            if not r or not consumed:
                raise AuthorityError("evidence requires consumed run")
            if b["activation_digest"] != consumed["activation_digest"]:
                raise AuthorityError("evidence activation digest mismatch")
            if (
                any(
                    b[k] != r[k]
                    for k in (
                        "attempt_number",
                        "candidate_sha",
                        "git_tree",
                        "verified_input_tree_digest",
                        "target_host_opaque_id",
                    )
                )
                or b["reservation_digest"] != r["event_digest"]
            ):
                raise AuthorityError("evidence cross-run relabel mismatch")
            if any(
                x["event_type"] == "EVIDENCE_BOUND"
                and x.get("artifact_digest") == b["artifact_digest"]
                and x.get("run_id") != b["run_id"]
                for x in es
            ):
                raise AuthorityError("artifact already belongs to another run")
            if any(
                x["event_type"] == "EVIDENCE_BOUND"
                and x.get("run_id") == b["run_id"]
                and x.get("artifact_ordinal") == b["artifact_ordinal"]
                for x in es
            ):
                raise AuthorityError("duplicate evidence ordinal")
            return self._append(
                es,
                {
                    "event_type": "EVIDENCE_BOUND",
                    "event_time_utc": utc_text(event_time),
                    **{
                        k: r[k]
                        for k in (
                            "run_id",
                            "attempt_number",
                            "candidate_sha",
                            "git_tree",
                            "verified_input_tree_digest",
                            "target_host_opaque_id",
                        )
                    },
                    "reservation_digest": r["event_digest"],
                    "activation_digest": b["activation_digest"],
                    "binding_digest": binding_digest,
                    "artifact_type": b["artifact_type"],
                    "artifact_digest": b["artifact_digest"],
                    "artifact_ordinal": b["artifact_ordinal"],
                },
            )

        return self._mut(f)

    def terminal(self, *, run_id, status, reason, event_time=None):
        if status not in TERMINAL:
            raise AuthorityError("invalid terminal status")

        def f(es):
            r = _reserve(es, run_id)
            if not r or _state(es, run_id) in TERMINAL:
                raise AuthorityError("terminal run invalid/already terminal")
            return self._append(
                es,
                {
                    "event_type": status,
                    "event_time_utc": utc_text(event_time),
                    **{
                        k: r[k]
                        for k in (
                            "run_id",
                            "attempt_number",
                            "candidate_sha",
                            "git_tree",
                            "verified_input_tree_digest",
                            "target_host_opaque_id",
                        )
                    },
                    "reservation_digest": r["event_digest"],
                    "terminal_reason": reason,
                },
            )

        return self._mut(f)


def _write_once(p: Path, b: bytes) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(p):
        raise AuthorityError("receipt already exists")

    fd, tmp_name = tempfile.mkstemp(dir=p.parent, prefix=".receipt-")
    tmp = Path(tmp_name)
    linked = False
    try:
        _write_all(fd, b)
        os.fsync(fd)
        os.close(fd)
        fd = -1
        try:
            os.link(tmp, p)
        except FileExistsError as e:
            raise AuthorityError("receipt already exists") from e
        linked = True
        _fsync_dir(p.parent)
        final_bytes = _read_exact_regular(p)
        if final_bytes != b or sha256_digest(final_bytes) != sha256_digest(b):
            raise AuthorityError("receipt final bytes mismatch")
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        # Never delete a linked final receipt after the consumption event committed.
        # Any failure above remains fail-closed and the registry stays consumed.
        _ = linked
