"""Policy-compliant SEC/EDGAR Form-4 P0 raw collector.

Only discovery identity needed to fetch complete submission text is interpreted.
Form-4 body content is never parsed here and never exposed by status_snapshot.
"""
from __future__ import annotations

import os
import random
import re
import subprocess
import urllib.error
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

from ..events import EventLog
from ..paths import QuantPaths
from ..state import parse_ts, read_json, write_json
from .sec_form4_raw import (CAPTURED, NOT_ADMISSIBLE, NOT_VISIBLE, SecAttemptRecord,
                            SecCaptureStore)

COLLECTOR_VERSION = "sec-form4-raw-capture-v1"
SEC_POLICY_SOURCE = "https://www.sec.gov/about/developer-resources"
SEC_ACCESS_SOURCE = (
    "https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data"
)
SEC_LATEST_FORM4_ATOM = (
    "https://www.sec.gov/cgi-bin/browse-edgar?"
    "action=getcurrent&CIK=&type=4&company=&dateb=&owner=include&start=0&count=40&output=atom"
)
DISCOVERY_ENDPOINT_CLASS = "sec_latest_filings_atom_form4"
FILING_ENDPOINT_CLASS = "sec_complete_submission_text"
BACKOFF_SECONDS = (5, 15, 60, 300, 900)
POLL_SECONDS = 60
REQUEST_RATE_PER_SECOND = 2.0
MAX_CONCURRENCY = 1
RATE_CONTROL_BACKOFF_SECONDS = 900
PERMANENT_4XX_BACKOFF_SECONDS = 300
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ARCHIVE_RE = re.compile(
    r"^https?://www\.sec\.gov/Archives/edgar/data/\d+/(?:\d+/)?"
    r"(?P<accession>\d{10}-\d{2}-\d{6})-index\.htm$"
)


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _git_commit(root: Path) -> str:
    configured = os.environ.get("QUANT_GIT_COMMIT") or os.environ.get("GITHUB_SHA")
    if configured:
        return configured
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                                capture_output=True, text=True, timeout=5)
        return result.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


@dataclass(frozen=True)
class SecCapturePolicy:
    discovery_url: str = SEC_LATEST_FORM4_ATOM
    poll_seconds: int = POLL_SECONDS
    request_rate_per_second: float = REQUEST_RATE_PER_SECOND
    max_concurrency: int = MAX_CONCURRENCY
    backoff_seconds: list[int] = field(default_factory=lambda: list(BACKOFF_SECONDS))
    rate_control_backoff_seconds: int = RATE_CONTROL_BACKOFF_SECONDS
    permanent_4xx_backoff_seconds: int = PERMANENT_4XX_BACKOFF_SECONDS
    policy_source: str = SEC_POLICY_SOURCE
    access_documentation: str = SEC_ACCESS_SOURCE
    policy_reviewed_date: str = "2026-09-18"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SecCollectorConfig:
    enabled: bool
    requester_name: str | None
    contact_email: str | None
    git_commit: str
    timeout_seconds: float = 30.0
    max_documents_per_poll: int = 1

    @classmethod
    def from_env(cls, root: Path) -> "SecCollectorConfig":
        enabled = os.environ.get("QUANT_SEC_FORM4_CAPTURE", "").strip().lower() in {
            "1", "true", "yes", "on"
        }
        return cls(
            enabled=enabled,
            requester_name=(os.environ.get("SEC_REQUESTER_NAME") or "").strip() or None,
            contact_email=(os.environ.get("SEC_CONTACT_EMAIL") or "").strip() or None,
            git_commit=_git_commit(root),
            timeout_seconds=float(os.environ.get("SEC_REQUEST_TIMEOUT_SECONDS", "30")),
            max_documents_per_poll=max(1, int(os.environ.get("SEC_MAX_DOCUMENTS_PER_POLL", "1"))),
        )

    def user_agent(self) -> str:
        if not self.enabled:
            raise ValueError("SEC/Form-4 capture is not enabled")
        if not self.requester_name:
            raise ValueError("SEC_REQUESTER_NAME is required for live SEC access")
        if not self.contact_email or not _EMAIL_RE.match(self.contact_email):
            raise ValueError("a valid SEC_CONTACT_EMAIL is required for live SEC access")
        return f"{self.requester_name} {self.contact_email}"


@dataclass
class SecCollectorState:
    status: str = "IDLE"
    last_poll_result: str | None = None
    last_attempt_at_utc: str | None = None
    last_successful_poll_at_utc: str | None = None
    last_receipt_at_utc: str | None = None
    last_http_status: int | None = None
    last_error_class: str | None = None
    last_raw_object_sha256: str | None = None
    last_byte_length: int | None = None
    last_endpoint_class: str | None = None
    next_poll_at_utc: str | None = None
    blocked_until_utc: str | None = None
    pending: list[dict[str, str]] = field(default_factory=list)
    known_source_ids: list[str] = field(default_factory=list)
    collector_version: str = COLLECTOR_VERSION
    git_commit: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FilingReference:
    source_identity: str
    source_locator: str


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: bytes
    headers: dict[str, str]


class SecTransport(Protocol):
    def fetch(self, url: str, headers: dict[str, str], timeout: float) -> HttpResponse: ...


class UrllibSecTransport:
    def fetch(self, url: str, headers: dict[str, str], timeout: float) -> HttpResponse:
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return HttpResponse(int(response.status), response.read(),
                                    {k.lower(): v for k, v in response.headers.items()})
        except urllib.error.HTTPError as exc:
            return HttpResponse(int(exc.code), exc.read(),
                                {k.lower(): v for k, v in exc.headers.items()})


class SecRateLimiter:
    """Global single-process no-burst limiter. Retries use the same gate."""

    def __init__(self, rate_per_second: float, now: Callable[[], datetime],
                 sleep: Callable[[float], None]):
        if rate_per_second <= 0:
            raise ValueError("rate_per_second must be positive")
        self.minimum_interval = 1.0 / rate_per_second
        self.now, self.sleep = now, sleep
        self.last_request_at: datetime | None = None

    def acquire(self) -> None:
        current = self.now()
        if self.last_request_at is not None:
            elapsed = max(0.0, (current - self.last_request_at).total_seconds())
            wait = self.minimum_interval - elapsed
            if wait > 0:
                self.sleep(wait)
                current = self.now()
        self.last_request_at = current


def parse_latest_form4_feed(body: bytes) -> list[FilingReference]:
    """Extract accession + complete-submission locator only; no Form-4 body fields."""
    root = ET.fromstring(body)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    found: dict[str, FilingReference] = {}
    for entry in root.findall("atom:entry", ns):
        for link in entry.findall("atom:link", ns):
            href = link.attrib.get("href", "")
            match = _ARCHIVE_RE.match(href)
            if match is None:
                continue
            accession = match.group("accession")
            locator = href[:-len("-index.htm")] + ".txt"
            if locator.startswith("http://"):
                locator = "https://" + locator[len("http://"):]
            found.setdefault(accession, FilingReference(accession, locator))
            break
    return list(found.values())


class SecForm4Collector:
    """P0 raw collector owned by Quant's Control Plane."""

    def __init__(self, paths: QuantPaths, log: EventLog, components: Any,
                 config: SecCollectorConfig | None = None,
                 policy: SecCapturePolicy | None = None,
                 transport: SecTransport | None = None,
                 now: Callable[[], datetime] | None = None,
                 sleep: Callable[[float], None] | None = None,
                 jitter: Callable[[float], float] | None = None,
                 fault_hook: Callable[[str], None] | None = None):
        self.paths, self.log, self.components = paths, log, components
        self.config = config or SecCollectorConfig.from_env(paths.root)
        self.policy = policy or SecCapturePolicy()
        self.transport = transport or UrllibSecTransport()
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.sleep = sleep or __import__("time").sleep
        self.jitter = jitter or (lambda base: random.uniform(0.0, min(1.0, base * 0.1)))
        self.rate_limiter = SecRateLimiter(self.policy.request_rate_per_second,
                                           self.now, self.sleep)
        self.store = SecCaptureStore(paths, fault_hook=fault_hook)
        payload = read_json(paths.sec_form4_state)
        self.state = SecCollectorState(**payload) if payload else SecCollectorState()
        self.state.git_commit = self.config.git_commit
        self.storage_health = "UNKNOWN"

    def save(self) -> None:
        write_json(self.paths.sec_form4_state, self.state.to_dict())

    def recover(self) -> dict[str, Any]:
        result = self.store.reconcile()
        self.storage_health = result["storage_health"]
        if not self.config.enabled:
            self.state.status = "IDLE"
            self.components.set("SEC_CAPTURE", "IDLE", "disabled by configuration")
        elif self.storage_health != "HEALTHY":
            self.state.status = "BLOCKED"
            self.state.last_error_class = "STORAGE_INTEGRITY"
            self.components.set("SEC_CAPTURE", "BLOCKED", "raw-store integrity review required")
        else:
            self.components.set("SEC_CAPTURE",
                                "BLOCKED" if self.state.status == "BLOCKED" else "IDLE",
                                "restart recovery complete")
        self.save()
        return {"recovered_staged_response": bool(result["recovered"]),
                "storage_health": self.storage_health}

    def enabled(self) -> bool:
        return self.config.enabled

    def due(self) -> bool:
        if not self.config.enabled or self.storage_health == "DEGRADED":
            return False
        now = self.now()
        if self.state.blocked_until_utc and now < parse_ts(self.state.blocked_until_utc):
            return False
        return not self.state.next_poll_at_utc or now >= parse_ts(self.state.next_poll_at_utc)

    def _schedule(self, seconds: float, blocked: bool = False) -> None:
        target = _iso(self.now() + timedelta(seconds=seconds))
        self.state.next_poll_at_utc = target
        self.state.blocked_until_utc = target if blocked else None

    def _start_attempt(self, kind: str, locator: str, endpoint_class: str) -> SecAttemptRecord:
        record = SecAttemptRecord(
            attempt_id=uuid.uuid4().hex, attempt_kind=kind, phase="STARTED",
            source_locator=locator, request_attempted_at_utc=_iso(self.now()),
            response_received_at_utc=None, result_state="STARTED", http_status=None,
            raw_object_sha256=None, byte_length=None, collector_version=COLLECTOR_VERSION,
            git_commit=self.config.git_commit, endpoint_class=endpoint_class)
        self.store.append_attempt(record)
        self.state.last_attempt_at_utc = record.request_attempted_at_utc
        self.save()
        return record

    def _finish_attempt(self, started: SecAttemptRecord, result_state: str,
                        response_received_at_utc: str | None = None,
                        http_status: int | None = None, body: bytes | None = None,
                        media_type: str | None = None, error_class: str | None = None,
                        source_identity: str | None = None) -> tuple[SecAttemptRecord, bool]:
        digest = SecCaptureStore.digest(body) if body is not None else None
        record = SecAttemptRecord(
            attempt_id=started.attempt_id, attempt_kind=started.attempt_kind, phase="COMPLETED",
            source_locator=started.source_locator,
            request_attempted_at_utc=started.request_attempted_at_utc,
            response_received_at_utc=response_received_at_utc, result_state=result_state,
            http_status=http_status, raw_object_sha256=digest,
            byte_length=len(body) if body is not None else None,
            collector_version=COLLECTOR_VERSION, git_commit=self.config.git_commit,
            endpoint_class=started.endpoint_class, media_type=media_type,
            error_class=error_class)
        conflict = False
        if body is None:
            self.store.append_attempt(record)
        else:
            raw, conflict = self.store.capture_response(record, body, source_identity)
            self.state.last_receipt_at_utc = response_received_at_utc
            self.state.last_http_status = http_status
            self.state.last_raw_object_sha256 = raw.sha256
            self.state.last_byte_length = raw.byte_length
            self.state.last_endpoint_class = started.endpoint_class
        self.state.last_error_class = error_class
        self.save()
        return record, conflict

    @staticmethod
    def _http_result(status: int) -> str:
        if status == 200:
            return "RESPONSE_CAPTURED"
        if status == 429:
            return "RATE_LIMITED"
        if status == 403:
            return "BLOCKED_403"
        if status >= 500:
            return "TRANSIENT_HTTP_ERROR"
        return "HTTP_ERROR"

    def _request_once(self, kind: str, locator: str, endpoint_class: str,
                      source_identity: str | None = None) -> tuple[HttpResponse | None, bool]:
        started = self._start_attempt(kind, locator, endpoint_class)
        user_agent = self.config.user_agent()
        self.rate_limiter.acquire()
        try:
            response = self.transport.fetch(locator, {
                "User-Agent": user_agent,
                "Accept": "application/atom+xml,text/plain,*/*;q=0.1",
                "Accept-Encoding": "identity",
            }, self.config.timeout_seconds)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            self._finish_attempt(started, "NETWORK_ERROR", error_class=type(exc).__name__)
            return None, False
        received = _iso(self.now())
        content_length = response.headers.get("content-length")
        if content_length is not None:
            try:
                expected_length = int(content_length)
            except ValueError as exc:
                self._finish_attempt(
                    started, "CONTENT_LENGTH_MISMATCH", received, response.status,
                    response.body, response.headers.get("content-type"),
                    error_class="ContentLengthMismatch", source_identity=source_identity)
                raise IOError("invalid HTTP content-length header") from exc
            if expected_length != len(response.body):
                self._finish_attempt(
                    started, "CONTENT_LENGTH_MISMATCH", received, response.status,
                    response.body, response.headers.get("content-type"),
                    error_class="ContentLengthMismatch", source_identity=source_identity)
                raise IOError("HTTP content-length does not match received bytes")
        _, conflict = self._finish_attempt(
            started, self._http_result(response.status), received, response.status,
            response.body, response.headers.get("content-type"), source_identity=source_identity)
        return response, conflict

    def _request_with_retries(self, kind: str, locator: str, endpoint_class: str,
                              source_identity: str | None = None) -> tuple[HttpResponse | None, bool]:
        for index in range(len(self.policy.backoff_seconds) + 1):
            response, conflict = self._request_once(kind, locator, endpoint_class, source_identity)
            if response is not None and (response.status == 200 or response.status in {403, 429}
                                         or 400 <= response.status < 500):
                return response, conflict
            if index >= len(self.policy.backoff_seconds):
                return response, conflict
            base = self.policy.backoff_seconds[index]
            self.sleep(base + self.jitter(float(base)))
        return None, False

    def _start_poll(self) -> SecAttemptRecord:
        return self._start_attempt("POLL", self.policy.discovery_url, DISCOVERY_ENDPOINT_CLASS)

    def _complete_poll(self, started: SecAttemptRecord, result: str,
                       error_class: str | None = None) -> None:
        self._finish_attempt(started, result, error_class=error_class)

    def _block(self, error_class: str, seconds: int) -> str:
        self.state.status = "BLOCKED"
        self.state.last_error_class = error_class
        self._schedule(seconds, blocked=True)
        self.components.set("SEC_CAPTURE", "BLOCKED", error_class)
        self.save()
        return "BLOCKED"

    def _queue_discovery(self, body: bytes) -> str:
        refs = parse_latest_form4_feed(body)
        known = set(self.state.known_source_ids)
        pending = {item["source_identity"] for item in self.state.pending}
        added = False
        for ref in refs:
            if ref.source_identity in known or ref.source_identity in pending:
                continue
            self.state.pending.append(asdict(ref))
            self.state.known_source_ids.append(ref.source_identity)
            pending.add(ref.source_identity)
            added = True
        self.save()
        return "QUEUED" if added else "NO_NEW_DATA"

    def poll_once(self) -> str:
        if not self.config.enabled:
            self.state.status = "IDLE"
            self.components.set("SEC_CAPTURE", "IDLE", "disabled by configuration")
            self.save()
            return "DISABLED"
        poll = self._start_poll()
        try:
            self.config.user_agent()
        except ValueError as exc:
            self._complete_poll(poll, "BLOCKED_CONFIG", type(exc).__name__)
            return self._block("CONFIGURATION_REQUIRED", self.policy.poll_seconds)
        self.state.status = "RUN"
        self.components.set("SEC_CAPTURE", "RUN", "polling SEC latest Form-4 feed")
        self.save()
        try:
            response, _ = self._request_with_retries(
                "DISCOVERY", self.policy.discovery_url, DISCOVERY_ENDPOINT_CLASS)
        except Exception as exc:
            self._complete_poll(poll, "POLL_FAILED", type(exc).__name__)
            return self._block(type(exc).__name__, self.policy.rate_control_backoff_seconds)
        if response is None:
            self._complete_poll(poll, "TRANSIENT_FAILURE_EXHAUSTED", "NETWORK_ERROR")
            return self._block("NETWORK_ERROR", self.policy.rate_control_backoff_seconds)
        if response.status in {403, 429}:
            label = f"HTTP_{response.status}"
            self._complete_poll(
                poll, "RATE_LIMITED" if response.status == 429 else "BLOCKED_403", label)
            return self._block(label, self.policy.rate_control_backoff_seconds)
        if response.status >= 500:
            label = f"HTTP_{response.status}"
            self._complete_poll(poll, "TRANSIENT_FAILURE_EXHAUSTED", label)
            return self._block(label, self.policy.rate_control_backoff_seconds)
        if response.status != 200:
            label = f"HTTP_{response.status}"
            self._complete_poll(poll, "HTTP_ERROR", label)
            return self._block(label, self.policy.permanent_4xx_backoff_seconds)
        try:
            discovery = self._queue_discovery(response.body)
        except ET.ParseError as exc:
            self._complete_poll(poll, "DISCOVERY_PARSE_FAILURE", type(exc).__name__)
            return self._block("DISCOVERY_PARSE_FAILURE",
                               self.policy.permanent_4xx_backoff_seconds)

        captured = False
        for _ in range(min(self.config.max_documents_per_poll, len(self.state.pending))):
            item = self.state.pending[0]
            filing, conflict = self._request_with_retries(
                "FILING", item["source_locator"], FILING_ENDPOINT_CLASS,
                source_identity=item["source_identity"])
            if filing is None:
                self._complete_poll(poll, "FILING_TRANSIENT_FAILURE", "NETWORK_ERROR")
                return self._block("NETWORK_ERROR", self.policy.rate_control_backoff_seconds)
            if filing.status in {403, 429}:
                label = f"HTTP_{filing.status}"
                self._complete_poll(
                    poll, "RATE_LIMITED" if filing.status == 429 else "BLOCKED_403", label)
                return self._block(label, self.policy.rate_control_backoff_seconds)
            if filing.status != 200:
                label = f"HTTP_{filing.status}"
                self._complete_poll(poll, "FILING_HTTP_ERROR", label)
                delay = (self.policy.rate_control_backoff_seconds if filing.status >= 500
                         else self.policy.permanent_4xx_backoff_seconds)
                return self._block(label, delay)
            if not filing.body:
                self._complete_poll(poll, "EMPTY_FILING_RESPONSE", "EMPTY_RESPONSE")
                return self._block("EMPTY_RESPONSE",
                                   self.policy.permanent_4xx_backoff_seconds)
            if conflict:
                self._complete_poll(poll, "SOURCE_IDENTITY_CONFLICT", "CONTENT_CONFLICT")
                return self._block("SOURCE_IDENTITY_CONFLICT",
                                   self.policy.rate_control_backoff_seconds)
            self.state.pending.pop(0)
            captured = True
            self.save()

        result = "CAPTURED" if captured else discovery
        self._complete_poll(poll, result)
        self.state.status = "IDLE"
        self.state.last_poll_result = result
        self.state.last_successful_poll_at_utc = _iso(self.now())
        self.state.last_error_class = None
        self._schedule(self.policy.poll_seconds)
        self.components.set("SEC_CAPTURE", "IDLE", "capture poll complete")
        self.save()
        self.log.emit("DATA", "SEC_CAPTURE", "sec_form4_capture_poll", "SEC/Form-4",
                      result=result, endpoint_class=DISCOVERY_ENDPOINT_CLASS,
                      storage_health=self.storage_health)
        return result

    def status_snapshot(self) -> dict[str, Any]:
        """Opaque-only telemetry. No source identity, body, parsed field or content count."""
        return {
            "enabled": self.config.enabled,
            "state": self.state.status,
            "last_poll_result": self.state.last_poll_result,
            "last_attempt_at_utc": self.state.last_attempt_at_utc,
            "last_successful_poll_at_utc": self.state.last_successful_poll_at_utc,
            "last_receipt_at_utc": self.state.last_receipt_at_utc,
            "last_http_status": self.state.last_http_status,
            "last_error_class": self.state.last_error_class,
            "last_raw_object_sha256": self.state.last_raw_object_sha256,
            "last_byte_length": self.state.last_byte_length,
            "last_endpoint_class": self.state.last_endpoint_class,
            "next_poll_at_utc": self.state.next_poll_at_utc,
            "blocked_until_utc": self.state.blocked_until_utc,
            "storage_health": self.storage_health,
            "policy": self.policy.to_dict(),
            "visibility": {
                "capture_state": CAPTURED if self.state.last_raw_object_sha256 else "NONE",
                "scientific_visibility": NOT_VISIBLE,
                "confirmation_admissibility": NOT_ADMISSIBLE,
            },
        }
