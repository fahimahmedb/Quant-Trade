"""Passive one-shot forward recorder with restart/gap accounting."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Iterable

from .http import NetworkFetchError, PublicHttpTransport
from .models import CaptureRecord, EndpointSpec, GapRecord, RecorderState
from .storage import AtomicCaptureStore


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _stable_id(prefix: str, *parts: object) -> str:
    material = "\x00".join(str(part) for part in parts).encode("utf-8")
    return prefix + hashlib.sha256(material).hexdigest()[:24]


@dataclass(frozen=True)
class RecorderRunSummary:
    run_id: str
    attempted: int
    captured: int
    successful: int
    failed: int
    duplicates: int
    gaps_written: int
    final_mode: str


class ForwardRecorder:
    """Capture one bounded public snapshot plan; no loops, signals, outcomes, or trading."""

    def __init__(
        self,
        store: AtomicCaptureStore,
        *,
        transport: PublicHttpTransport | object | None = None,
        now_fn: Callable[[], datetime] = _utc_now,
        monotonic_ns_fn: Callable[[], int] = time.monotonic_ns,
        gap_multiplier: float = 2.5,
        clock_skew_threshold_ms: int = 10_000,
    ) -> None:
        if gap_multiplier <= 1.0:
            raise ValueError("gap_multiplier must be > 1")
        self.store = store
        self.transport = transport or PublicHttpTransport()
        self.now_fn = now_fn
        self.monotonic_ns_fn = monotonic_ns_fn
        self.gap_multiplier = gap_multiplier
        self.clock_skew_threshold_ms = clock_skew_threshold_ms

    def run_once(
        self,
        specs: Iterable[EndpointSpec],
        *,
        timeout_seconds: float = 10.0,
        stop_on_fetch_error: bool = False,
    ) -> RecorderRunSummary:
        plan = tuple(specs)
        if not plan:
            raise ValueError("capture plan cannot be empty")
        state = self.store.recover_state()
        run_id = "run_" + uuid.uuid4().hex[:20]
        gaps = 0
        if state.mode == "RUN":
            gaps += self._persist_gap(
                state=state,
                source_id="recorder",
                reason="unclean_restart",
                previous_capture_id=None,
                current_capture_id=None,
                detail=f"prior run {state.run_id or 'unknown'} did not return to IDLE",
            )
        state.mode = "RUN"
        state.run_id = run_id
        self.store.save_state(state)
        attempted = captured = successful = failed = duplicates = 0
        try:
            for spec in plan:
                attempted += 1
                try:
                    record, duplicate, new_gaps, ok = self._capture(spec, state, timeout_seconds)
                    captured += 1
                    successful += int(ok)
                    failed += int(not ok)
                    duplicates += int(duplicate)
                    gaps += new_gaps
                    state.last_by_source[spec.source_id] = {
                        "capture_id": record.capture_id,
                        "raw_sha256": record.raw_sha256,
                        "retrieval_completed_utc": record.retrieval_completed_utc,
                        "sequence": record.sequence,
                    }
                    state.last_completed_utc = record.retrieval_completed_utc
                    state.next_sequence = record.sequence + 1
                    self.store.save_state(state)
                except NetworkFetchError as exc:
                    failed += 1
                    gaps += self._persist_gap(
                        state=state,
                        source_id=spec.source_id,
                        reason="fetch_error",
                        previous_capture_id=self._previous(state, spec.source_id).get("capture_id"),
                        current_capture_id=None,
                        detail=str(exc),
                    )
                    if stop_on_fetch_error:
                        break
            return RecorderRunSummary(run_id, attempted, captured, successful, failed, duplicates, gaps, "IDLE")
        finally:
            latest = self.store.load_state()
            latest.mode = "IDLE"
            latest.run_id = ""
            self.store.save_state(latest)

    def _capture(self, spec: EndpointSpec, state: RecorderState, timeout_seconds: float) -> tuple[CaptureRecord, bool, int, bool]:
        started_utc = self.now_fn()
        mono_start = self.monotonic_ns_fn()
        response = self.transport.fetch(spec.endpoint, timeout_seconds=timeout_seconds)
        mono_end = self.monotonic_ns_fn()
        completed_utc = self.now_fn()
        completed_iso = _iso(completed_utc)
        source_time_ms = self._source_time(response.body, spec.source_time_field)
        completed_epoch_ms = int(completed_utc.timestamp() * 1000)
        clock_skew_ms = None if source_time_ms is None else source_time_ms - completed_epoch_ms
        previous = self._previous(state, spec.source_id)
        gap_ms = None
        gap_detected = False
        utc_regression = False
        if previous.get("retrieval_completed_utc"):
            delta = completed_utc - _parse_utc(str(previous["retrieval_completed_utc"]))
            raw_gap_ms = int(delta.total_seconds() * 1000)
            utc_regression = raw_gap_ms < 0
            gap_ms = max(0, raw_gap_ms)
            gap_detected = gap_ms > int(spec.expected_cadence_seconds * 1000 * self.gap_multiplier)
        digest, raw_path, raw_already_present = self.store.persist_raw(
            utc_date=completed_iso[:10], source_id=spec.source_id, raw=response.body
        )
        duplicate_of = None
        if previous.get("raw_sha256") == digest:
            duplicate_of = str(previous.get("capture_id") or "") or None
        capture_id = _stable_id("cap_", spec.source_id, completed_iso, digest, state.next_sequence)
        record = CaptureRecord(
            schema_version=1,
            capture_id=capture_id,
            sequence=state.next_sequence,
            source_id=spec.source_id,
            venue=spec.venue,
            market_type=spec.market_type,
            instrument=spec.instrument,
            purpose=spec.purpose,
            endpoint=spec.endpoint,
            retrieval_started_utc=_iso(started_utc),
            retrieval_completed_utc=completed_iso,
            monotonic_started_ns=mono_start,
            monotonic_completed_ns=mono_end,
            duration_ms=max(0.0, (mono_end - mono_start) / 1_000_000),
            http_status=response.status,
            response_headers=dict(response.headers),
            content_type=response.headers.get("content-type", ""),
            raw_sha256=digest,
            raw_bytes=len(response.body),
            raw_path=raw_path,
            parser_version=spec.parser_version,
            source_time_ms=source_time_ms,
            clock_skew_ms=clock_skew_ms,
            duplicate_of=duplicate_of,
            gap_from_previous_ms=gap_ms,
            gap_detected=gap_detected,
        )
        self.store.persist_capture(record)
        gap_count = 0
        if gap_detected:
            gap_count += self._persist_gap(
                state=state,
                source_id=spec.source_id,
                reason="polling_gap",
                previous_capture_id=previous.get("capture_id"),
                current_capture_id=capture_id,
                gap_ms=gap_ms,
                expected_cadence_ms=spec.expected_cadence_seconds * 1000,
            )
        if utc_regression:
            gap_count += self._persist_gap(
                state=state,
                source_id=spec.source_id,
                reason="utc_clock_regression",
                previous_capture_id=previous.get("capture_id"),
                current_capture_id=capture_id,
                detail="retrieval UTC moved backwards relative to the previous committed capture",
            )
        if clock_skew_ms is not None and abs(clock_skew_ms) > self.clock_skew_threshold_ms:
            gap_count += self._persist_gap(
                state=state,
                source_id=spec.source_id,
                reason="clock_skew",
                previous_capture_id=previous.get("capture_id"),
                current_capture_id=capture_id,
                clock_skew_ms=clock_skew_ms,
            )
        ok = 200 <= response.status < 300
        if not ok:
            gap_count += self._persist_gap(
                state=state,
                source_id=spec.source_id,
                reason="http_error",
                previous_capture_id=previous.get("capture_id"),
                current_capture_id=capture_id,
                detail=f"HTTP {response.status}",
            )
        return record, bool(duplicate_of or raw_already_present), gap_count, ok

    def _persist_gap(
        self,
        *,
        state: RecorderState,
        source_id: str,
        reason: str,
        previous_capture_id: str | None,
        current_capture_id: str | None,
        gap_ms: int | None = None,
        expected_cadence_ms: int | None = None,
        clock_skew_ms: int | None = None,
        detail: str = "",
    ) -> int:
        detected = _iso(self.now_fn())
        gap_id = _stable_id("gap_", source_id, reason, previous_capture_id, current_capture_id, detected)
        record = GapRecord(
            schema_version=1,
            gap_id=gap_id,
            source_id=source_id,
            detected_utc=detected,
            reason=reason,
            previous_capture_id=previous_capture_id,
            current_capture_id=current_capture_id,
            gap_ms=gap_ms,
            expected_cadence_ms=expected_cadence_ms,
            clock_skew_ms=clock_skew_ms,
            detail=detail,
        )
        self.store.persist_gap(record)
        return 1

    @staticmethod
    def _previous(state: RecorderState, source_id: str) -> dict[str, object]:
        value = state.last_by_source.get(source_id, {})
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _source_time(raw: bytes, field: str | None) -> int | None:
        if not field:
            return None
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        if isinstance(payload, dict):
            value = payload.get(field)
            if isinstance(value, int) and value >= 0:
                return value
        return None
