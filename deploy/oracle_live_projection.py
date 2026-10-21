#!/usr/bin/env python3
"""Optional native Site projection around an unchanged, exact-SHA V2 worker.

GitHub commits remain scientific authority. The Site has a separate visual
session/generation/sequence; receipts bind it explicitly to canonical event IDs.
Only a currently executing, durably claimed action can start business motion.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
import sys

SITE = "https://quant-trade-lab.sassylime.chatgpt.site"
PRINCIPAL = "oracle-research-live"
OBSERVATION_PREFIX = "research/research_os/artifacts/live-observation/"
MAX_LOCAL_RECEIPT_BYTES = 65536
RECEIPT_KEYS = {"schema_version", "source", "site_session", "records", "authority", "canonical_terminal",
                "source_events_mutated", "stale_starts_replayed", "credentials_included"}
FORBIDDEN_RECEIPT_KEYS = {"authorization", "secret", "credential", "credentials", "ingress_key", "api_key",
                          "access_token", "refresh_token", "bearer"}
EVENT_TYPES = {"ACTION_STARTED", "ACTION_COMPLETED", "WORKER_HEARTBEAT", "SESSION_ENDED"}
SHA40 = re.compile(r"^[a-f0-9]{40}$")
LANES = {"market_discovery": ("researcher", "Oracle · Discovery"),
         "fundamental_events": ("researcher", "Oracle · Documents"),
         "independent_challenge": ("auditor", "Oracle · Validator"),
         "evidence_data": ("data", "Oracle · Evidence"),
         "integrator_portfolio": ("manager", "Oracle · Integration")}
ACTIVITIES = {"legacy_duplicate_check": "data-qualification", "mechanism_research": "hypothesis-generation",
              "document_or_fundamental_research": "document-reading", "disconfirmation": "audit-red-team",
              "freeze_hypothesis": "commit-persistence", "validation_handoff": "handoff",
              "independent_validation": "audit-red-team", "cross_examination": "audit-red-team",
              "red_team": "audit-red-team", "claim_restriction": "audit-red-team", "integration_handoff": "handoff",
              "recover_or_qualify": "data-qualification", "provenance_check": "data-qualification",
              "economic_identity": "data-qualification", "overlap_map": "data-qualification",
              "portfolio_map": "data-qualification", "shadow_readiness": "audit-red-team",
              "ledger_and_telemetry_update": "commit-persistence"}


def timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def persist(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    pending = path.with_suffix(".pending")
    with pending.open("wb") as stream:
        os.chmod(pending, 0o600); stream.write(encode(value)); stream.flush(); os.fsync(stream.fileno())
    pending.replace(path)


def _bounded_text(value, label, limit=256):
    if not isinstance(value, str) or not value or len(value) > limit or "\x00" in value:
        raise ValueError("LOCAL_OBSERVATION_" + label + "_INVALID")
    return value


def _reject_credential_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str) or key.lower() in FORBIDDEN_RECEIPT_KEYS:
                raise ValueError("LOCAL_OBSERVATION_CREDENTIAL_FIELD_FORBIDDEN")
            _reject_credential_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_credential_keys(nested)


def validate_local_observation_receipt(value):
    """Accept only the bounded observer receipt shape; never infer a Site ACK."""
    if not isinstance(value, dict) or set(value) != RECEIPT_KEYS:
        raise ValueError("LOCAL_OBSERVATION_RECEIPT_SHAPE_INVALID")
    if len(encode(value)) > MAX_LOCAL_RECEIPT_BYTES:
        raise ValueError("LOCAL_OBSERVATION_RECEIPT_TOO_LARGE")
    _reject_credential_keys(value)
    if (value.get("schema_version") != "oracle-live-projection-v1"
            or value.get("authority") != "OBSERVATIONAL_ONLY"
            or value.get("source_events_mutated") is not False
            or value.get("stale_starts_replayed") is not False
            or value.get("credentials_included") is not False):
        raise ValueError("LOCAL_OBSERVATION_RECEIPT_AUTHORITY_OR_PROVENANCE_INVALID")

    source = value.get("source")
    if not isinstance(source, dict):
        raise ValueError("LOCAL_OBSERVATION_SOURCE_INVALID")
    required_source = {"event_id", "session_id", "worker_id", "action_id", "generation", "event_seq",
                       "input_commit", "lane", "stage"}
    if set(source) != required_source:
        raise ValueError("LOCAL_OBSERVATION_SOURCE_SHAPE_INVALID")
    for key in ("event_id", "session_id", "worker_id", "action_id", "lane", "stage"):
        _bounded_text(source.get(key), "SOURCE_" + key.upper())
    if not source["worker_id"].startswith("oracle-research.") or source["lane"] not in LANES:
        raise ValueError("LOCAL_OBSERVATION_SOURCE_ROUTE_INVALID")
    if type(source.get("generation")) is not int or source["generation"] < 1:
        raise ValueError("LOCAL_OBSERVATION_SOURCE_GENERATION_INVALID")
    if type(source.get("event_seq")) is not int or source["event_seq"] < 1:
        raise ValueError("LOCAL_OBSERVATION_SOURCE_SEQUENCE_INVALID")
    if not isinstance(source.get("input_commit"), str) or not SHA40.fullmatch(source["input_commit"]):
        raise ValueError("LOCAL_OBSERVATION_SOURCE_COMMIT_INVALID")

    session = value.get("site_session")
    if not isinstance(session, dict) or set(session) != {"session_id", "generation", "lease_id", "heartbeat_interval_ms"}:
        raise ValueError("LOCAL_OBSERVATION_SITE_SESSION_INVALID")
    _bounded_text(session.get("session_id"), "SITE_SESSION_ID")
    _bounded_text(session.get("lease_id"), "SITE_LEASE_ID")
    if type(session.get("generation")) is not int or session["generation"] < 1:
        raise ValueError("LOCAL_OBSERVATION_SITE_GENERATION_INVALID")
    if type(session.get("heartbeat_interval_ms")) is not int or not 1000 <= session["heartbeat_interval_ms"] <= 20000:
        raise ValueError("LOCAL_OBSERVATION_HEARTBEAT_INTERVAL_INVALID")

    records = value.get("records")
    if not isinstance(records, list) or not records or len(records) > 128:
        raise ValueError("LOCAL_OBSERVATION_RECORDS_INVALID")
    pending_ids, acknowledged = set(), 0
    for record in records:
        if not isinstance(record, dict) or record.get("state") not in ("PENDING", "ACKNOWLEDGED", "DELIVERY_BLOCKED"):
            raise ValueError("LOCAL_OBSERVATION_RECORD_STATE_INVALID")
        if record["state"] == "PENDING":
            if set(record) != {"state", "packet"} or not isinstance(record["packet"], dict):
                raise ValueError("LOCAL_OBSERVATION_PENDING_SHAPE_INVALID")
            packet = record["packet"]
            required_packet = {"principal", "event_id", "trace_id", "worker_id", "session_id", "generation",
                               "lease_id", "event_seq", "event_type", "action_id", "emitted_at", "payload"}
            if set(packet) not in (required_packet, required_packet | {"effect_proof"}):
                raise ValueError("LOCAL_OBSERVATION_PACKET_SHAPE_INVALID")
            if (packet.get("principal") != PRINCIPAL or packet.get("worker_id") != source["worker_id"]
                    or packet.get("trace_id") != source["session_id"] or packet.get("action_id") != source["action_id"]
                    or packet.get("session_id") != session["session_id"] or packet.get("generation") != session["generation"]
                    or packet.get("lease_id") != session["lease_id"] or packet.get("event_type") not in EVENT_TYPES
                    or type(packet.get("event_seq")) is not int or packet["event_seq"] < 1
                    or not isinstance(packet.get("payload"), dict)):
                raise ValueError("LOCAL_OBSERVATION_PACKET_BINDING_INVALID")
            _bounded_text(packet.get("event_id"), "PACKET_EVENT_ID")
            _bounded_text(packet.get("emitted_at"), "PACKET_EMITTED_AT")
            if "effect_proof" in packet and not isinstance(packet["effect_proof"], dict):
                raise ValueError("LOCAL_OBSERVATION_EFFECT_PROOF_INVALID")
            pending_ids.add(packet["event_id"])
        elif record["state"] == "ACKNOWLEDGED":
            allowed = {"state", "event_id", "cursor", "status", "accepted_at"}
            if set(record) != allowed or record.get("status") not in ("APPLIED", "DUPLICATE_IGNORED"):
                raise ValueError("LOCAL_OBSERVATION_ACK_SHAPE_INVALID")
            _bounded_text(record.get("event_id"), "ACK_EVENT_ID")
            if record["event_id"] not in pending_ids or type(record.get("cursor")) is not int or record["cursor"] < 0:
                raise ValueError("LOCAL_OBSERVATION_ACK_BINDING_INVALID")
            if record.get("accepted_at") is not None:
                _bounded_text(record["accepted_at"], "ACK_ACCEPTED_AT")
            acknowledged += 1
        else:
            if set(record) != {"state", "error_type"}:
                raise ValueError("LOCAL_OBSERVATION_BLOCKED_SHAPE_INVALID")
            _bounded_text(record.get("error_type"), "BLOCKED_ERROR_TYPE", 128)

    terminal = value.get("canonical_terminal")
    if terminal is not None:
        if (not isinstance(terminal, dict)
                or set(terminal) - {"event_id", "session_id", "generation", "event_seq", "source_commit"}
                or terminal.get("session_id") != source["session_id"]):
            raise ValueError("LOCAL_OBSERVATION_TERMINAL_INVALID")
        for key in ("event_id", "session_id"):
            if key in terminal: _bounded_text(terminal[key], "TERMINAL_" + key.upper())
        for key in ("generation", "event_seq"):
            if key in terminal and (type(terminal[key]) is not int or terminal[key] < 1):
                raise ValueError("LOCAL_OBSERVATION_TERMINAL_COUNTER_INVALID")
        if "source_commit" in terminal and (not isinstance(terminal["source_commit"], str) or not SHA40.fullmatch(terminal["source_commit"])):
            raise ValueError("LOCAL_OBSERVATION_TERMINAL_COMMIT_INVALID")
    if acknowledged < 1:
        raise ValueError("LOCAL_OBSERVATION_ACK_NOT_PROVEN")
    # JSON round-trip yields a detached, canonical JSON-compatible object.
    return json.loads(json.dumps(value, sort_keys=True, allow_nan=False))


def durable_observation_path(receipt):
    session_id = receipt["source"]["session_id"]
    return OBSERVATION_PREFIX + hashlib.sha256(session_id.encode()).hexdigest() + ".json"


def persist_durable_observation_receipt(store, receipt):
    receipt = validate_local_observation_receipt(receipt)
    path = durable_observation_path(receipt)
    with store.snapshot() as snapshot:
        if path in snapshot.blobs:
            if snapshot.read(path) != receipt:
                raise RuntimeError("LIVE_OBSERVATION_RECEIPT_CONFLICT")
            return "ALREADY_DURABLE"
        store.commit(snapshot, {path: receipt}, create_only=[path], message="Oracle native Site observation receipt")
        return "RECONCILED"


def reconcile_local_observation_receipts(store, state):
    """Drain only proven Site ACK evidence into GitHub; never retransmit Site events."""
    state = Path(state)
    summary = {"reconciled": 0, "already_durable": 0, "pending_or_invalid": 0, "conflicts": 0, "unavailable": 0}
    try:
        paths = sorted(state.glob("*.json")) if state.exists() else []
    except OSError:
        summary["unavailable"] += 1
        return summary
    for path in paths[:255]:
        if path.is_symlink() or not path.is_file():
            summary["pending_or_invalid"] += 1
            continue
        try:
            raw = path.read_bytes()
            if not raw or len(raw) > MAX_LOCAL_RECEIPT_BYTES:
                raise ValueError("LOCAL_OBSERVATION_FILE_SIZE_INVALID")
            receipt = validate_local_observation_receipt(json.loads(raw))
            status = persist_durable_observation_receipt(store, receipt)
            summary["reconciled" if status == "RECONCILED" else "already_durable"] += 1
            path.unlink(missing_ok=True)
        except RuntimeError as exc:
            if str(exc) == "LIVE_OBSERVATION_RECEIPT_CONFLICT":
                summary["conflicts"] += 1
            else:
                summary["unavailable"] += 1
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            summary["pending_or_invalid"] += 1
    return summary


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class SiteTransport:
    def __init__(self, key, base=SITE, *, opener=None):
        if base != SITE or not key or "\n" in key or "\r" in key:
            raise ValueError("EXACT_HTTPS_SITE_AND_NONEMPTY_SINGLE_LINE_SECRET_REQUIRED")
        self.key, self.base = key, base
        self.opener = opener or urllib.request.build_opener(NoRedirect())

    def post(self, route, body):
        if route not in ("session", "event"):
            raise ValueError("ORACLE_ROUTE_NOT_ALLOWLISTED")
        data = encode(body)
        if len(data) > 16384: raise ValueError("OBSERVATION_PACKET_TOO_LARGE")
        request = urllib.request.Request(self.base + "/api/oracle/" + route, data=data,
                    headers={"Content-Type": "application/json", "User-Agent": "Quant-Trade-Oracle/1.0",
                             "Authorization": "Bearer " + self.key})
        # Repeat the identical packet after an uncertain response. Never renew
        # a visual session silently or replay a start during another wake.
        attempts = 2 if route == "event" else 1
        for attempt in range(attempts):
            try:
                with self.opener.open(request, timeout=2) as response:
                    raw = response.read(16385)
                if len(raw) > 16384: raise ValueError("SITE_RESPONSE_TOO_LARGE")
                value = json.loads(raw)
                if not isinstance(value, dict): raise ValueError("INVALID_SITE_RESPONSE")
                return value
            except urllib.error.HTTPError as exc:
                raise RuntimeError("SITE_HTTP_" + str(exc.code)) from None
            except (OSError, urllib.error.URLError, TimeoutError):
                if attempt + 1 == attempts:
                    raise RuntimeError("SITE_TRANSPORT_UNAVAILABLE") from None


class LiveProjection:
    def __init__(self, transport, state):
        self.transport, self.state = transport, Path(state)
        self.lock, self.stop = threading.Lock(), threading.Event()
        self.session = self.source = self.terminal = self.thread = None
        self.closed = False
        # Keep bounded local recovery evidence. Durable ACK reconciliation runs
        # before this constructor; old files never become a queue of Site starts.
        try:
            if self.state.exists():
                files = sorted(self.state.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
                for path in files[255:]:
                    if path.is_file() and not path.is_symlink(): path.unlink()
        except OSError:
            pass  # Observation storage failure must never prevent a native wake.
        self.sequence, self.records = 0, []

    def _record(self, record):
        self.records.append(record)
        if len(self.records) > 128: self.records = self.records[-128:]
        # One bounded file per wake; no credentials, scientific authority or
        # pending-start replay queue. Interrupted sessions expire server-side.
        identity = hashlib.sha256(self.source["session_id"].encode()).hexdigest() if self.source else "unbound"
        persist(self.state / (identity + ".json"), self.receipt())

    def receipt(self):
        return dict(schema_version="oracle-live-projection-v1", source=self.source,
                    site_session=self.session, records=self.records, authority="OBSERVATIONAL_ONLY",
                    canonical_terminal={k: self.terminal[k] for k in ("event_id", "session_id", "generation", "event_seq", "source_commit")
                                        if k in self.terminal} if self.terminal else None,
                    source_events_mutated=False, stale_starts_replayed=False, credentials_included=False)

    def _post_event(self, kind, event_id, payload, emitted_at, effect=None):
        with self.lock:
            self.sequence += 1
            packet = dict(principal=PRINCIPAL, event_id=event_id, trace_id=self.source["session_id"],
                          worker_id=self.source["worker_id"], session_id=self.session["session_id"],
                          generation=self.session["generation"], lease_id=self.session["lease_id"],
                          event_seq=self.sequence, event_type=kind, action_id=self.source["action_id"],
                          emitted_at=emitted_at, payload=payload)
            if effect: packet["effect_proof"] = effect
            # Pending packet is persisted before delivery; it is deliberately
            # never replayed after this process loses the scientific lease.
            self._record(dict(state="PENDING", packet=packet))
            ack = self.transport.post("event", packet)
            if (ack.get("status") not in ("APPLIED", "DUPLICATE_IGNORED")
                    or ack.get("event_id") != event_id or type(ack.get("cursor")) is not int):
                raise ValueError("SITE_ACK_IDENTITY_NOT_PROVEN")
            self._record(dict(state="ACKNOWLEDGED", event_id=event_id,
                              cursor=ack["cursor"], status=ack["status"], accepted_at=ack.get("accepted_at")))

    def started(self, event, lane, stage, commit):
        if self.source is not None: raise ValueError("ONE_VISUAL_LINEAGE_PER_WAKE")
        if lane not in LANES or not event["worker_id"].startswith("oracle-research."):
            raise ValueError("CANONICAL_LANE_AND_NATIVE_ORACLE_WORKER_REQUIRED")
        self.source = dict(event_id=event["event_id"], session_id=event["session_id"],
                           worker_id=event["worker_id"], action_id=event["action_id"],
                           generation=event["generation"], event_seq=event["event_seq"], input_commit=commit,
                           lane=lane, stage=stage)
        opened = self.transport.post("session", dict(principal=PRINCIPAL, worker_id=event["worker_id"],
                                      native_session_id=event["session_id"], trace_id=event["session_id"]))
        if (opened.get("status") != "SESSION_ACCEPTED" or opened.get("principal") != PRINCIPAL
                or opened.get("worker_id") != event["worker_id"] or type(opened.get("generation")) is not int
                or not 1000 <= opened.get("heartbeat_interval_ms", 0) <= 20000):
            raise ValueError("SITE_SESSION_BINDING_NOT_PROVEN")
        self.session = {k: opened[k] for k in ("session_id", "generation", "lease_id", "heartbeat_interval_ms")}
        role, label = LANES[lane]
        self._post_event("ACTION_STARTED", event["event_id"], dict(stage=stage, label=event["action_id"],
                         ui_role=role, ui_label=label, ui_activity=ACTIVITIES.get(stage, "none")), event["emitted_at"])
        self.thread = threading.Thread(target=self._heartbeat, daemon=True); self.thread.start()

    def _heartbeat(self):
        while not self.stop.wait(self.session["heartbeat_interval_ms"] / 1000):
            try:
                event_id = "heartbeat-" + hashlib.sha256((self.source["session_id"] + str(self.sequence + 1)).encode()).hexdigest()
                self._post_event("WORKER_HEARTBEAT", event_id, {}, timestamp())
            except Exception as exc:
                self.failure(exc)
                return

    def failure(self, exc):
        # Exception values/HTTP bodies/headers can contain credentials. Only
        # bounded error categories are recorded, never str(exc).
        try: self._record(dict(state="DELIVERY_BLOCKED", error_type=type(exc).__name__))
        except OSError: pass

    def finished(self, stdout, exit_code):
        if self.closed: return
        self.closed = True
        self.stop.set()
        if self.thread: self.thread.join(timeout=5)
        if not self.session: return
        event = self.terminal
        kind = event["event_type"] if event else "SESSION_ENDED"
        event_id = event["event_id"] if event else "ended-" + hashlib.sha256(self.source["session_id"].encode()).hexdigest()
        try:
            self._post_event(kind, event_id, {"ui_activity": "none"},
                             event["emitted_at"] if event else timestamp(),
                             dict(stdout_sha256=hashlib.sha256(stdout).hexdigest(), exit_code=exit_code)
                             if kind == "ACTION_COMPLETED" else None)
            if kind != "SESSION_ENDED":
                self._post_event("SESSION_ENDED", "closed-" + hashlib.sha256(event_id.encode()).hexdigest(),
                                 {}, timestamp())
        except Exception as exc: self.failure(exc)


class ProjectionStore:
    """Observe only a successful canonical CAS; never rewrite its writes."""
    def __init__(self, store, projection, routing, next_stage):
        self.store, self.projection, self.routing, self.next_stage = store, projection, routing, next_stage

    def __getattr__(self, name): return getattr(self.store, name)

    def commit(self, snapshot, writes, **kwargs):
        commit = self.store.commit(snapshot, writes, **kwargs)
        for path, event in writes.items():
            if not path.startswith("research/research_os/events/") or not isinstance(event, dict): continue
            try:
                if event.get("event_type") == "ACTION_STARTED":
                    task = writes["research/research_os/tasks/" + event["action_id"] + ".json"]
                    lane = self.routing(snapshot, task)
                    self.projection.started(event, lane, self.next_stage(task, lane), commit)
                elif (self.projection.source and event.get("session_id") == self.projection.source["session_id"]
                      and event.get("event_type") in ("ACTION_COMPLETED", "SESSION_ENDED")):
                    self.projection.terminal = dict(event, source_commit=commit)
            except Exception as exc: self.projection.failure(exc)
        return commit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-release", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--state-dir", required=True, type=Path)
    args = parser.parse_args()
    core = args.core_release.resolve()
    config = json.loads(args.config.read_text())
    sys.path.insert(0, str(core))
    from deploy.oracle_release_install import _validate_release_receipt
    receipt = _validate_release_receipt(json.loads((core / ".quant_release_receipt.json").read_text()), config["release_sha"])
    if Path(receipt["path"]).resolve() != core: raise ValueError("QUALIFIED_CORE_RELEASE_PATH_MISMATCH")
    def core_only():
        print("LIVE_PROJECTION_DISABLED_CANONICAL_CORE_CONTINUES", file=sys.stderr)
        os.chdir(core)
        os.execv(sys.executable, [sys.executable, "-B", "-s", "-m", "research.research_os.oracle_worker_v2", "--config", str(args.config)])
    key = os.environ.pop("QT_ORACLE_INGRESS_KEY", "")
    if not key: core_only()
    base = os.environ.get("QT_ORACLE_SITE_BASE_URL", SITE)
    try:
        if os.environ.get("QT_ORACLE_PRINCIPAL", PRINCIPAL) != PRINCIPAL:
            raise ValueError("CANONICAL_ORACLE_PRINCIPAL_REQUIRED")
        transport = SiteTransport(key, base)
    except ValueError:
        core_only()
    from research.research_os.github_state import GitHubStateStore, StateConflict
    from research.research_os.oracle_worker import AUTHORITY, routing, next_stage
    from research.research_os.oracle_worker_v2 import build_v2_worker
    # Explicit runtime actor configuration, not a UI alias inferred from names.
    config = dict(config, worker_id="oracle-research")
    store = GitHubStateStore(cache=Path(config["cache"]), repository=config["repository"], branch=config["branch"])
    # Observation-only durability is repaired before any new scientific wake.
    # This path never contacts the Site and therefore cannot replay stale starts.
    reconciliation = reconcile_local_observation_receipts(store, args.state_dir)
    if any(reconciliation.values()):
        print("LIVE_RECEIPT_RECONCILIATION " + json.dumps(reconciliation, sort_keys=True), file=sys.stderr)
    projection = LiveProjection(transport, args.state_dir)
    observed = ProjectionStore(store, projection, routing, next_stage)
    worker = build_v2_worker(config, store=observed)
    exit_code = 0
    try:
        result = worker.wake()
        worker.store.compact_if_due()
        result.update(research_contract_version="v2-core", v2_preflight=worker.store.last_preflight,
                      observation_runtime_worker_id=config["worker_id"])
    except StateConflict:
        result = dict(status="RETRY_FRESH_STATE_NEXT_WAKE", authority=AUTHORITY)
    except Exception as exc:
        result = dict(status="RETRY_OR_BLOCKED", error_type=type(exc).__name__, authority=AUTHORITY)
        exit_code = 1
    stdout = (json.dumps(result, sort_keys=True) + "\n").encode()
    sys.stdout.write(stdout.decode()); sys.stdout.flush()
    projection.finished(stdout, exit_code)
    # ACK persistence runs only after the scientific wake has ended. UI I/O
    # never changes HEAD while a stage is reasoning or holding a claim.
    if projection.source:
        try:
            persist_durable_observation_receipt(store, projection.receipt())
        except Exception:
            print("LIVE_RECEIPT_PENDING_LOCAL_DURABILITY_PRESERVED", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
