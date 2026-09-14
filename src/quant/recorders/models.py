"""Data contracts for outcome-blind forward captures."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EndpointSpec:
    source_id: str
    venue: str
    market_type: str
    instrument: str | None
    purpose: str
    endpoint: str
    parser_version: str = "binance-public-v1"
    source_time_field: str | None = None
    expected_cadence_seconds: int = 60

    def __post_init__(self) -> None:
        if not self.source_id or not self.venue or not self.market_type or not self.purpose:
            raise ValueError("endpoint identity fields are required")
        if not self.endpoint.startswith("https://"):
            raise ValueError("only HTTPS public endpoints are allowed")
        if self.expected_cadence_seconds <= 0:
            raise ValueError("expected_cadence_seconds must be positive")


@dataclass(frozen=True)
class CaptureRecord:
    schema_version: int
    capture_id: str
    sequence: int
    source_id: str
    venue: str
    market_type: str
    instrument: str | None
    purpose: str
    endpoint: str
    retrieval_started_utc: str
    retrieval_completed_utc: str
    monotonic_started_ns: int
    monotonic_completed_ns: int
    duration_ms: float
    http_status: int
    response_headers: dict[str, str]
    content_type: str
    raw_sha256: str
    raw_bytes: int
    raw_path: str
    parser_version: str
    source_time_ms: int | None
    clock_skew_ms: int | None
    duplicate_of: str | None
    gap_from_previous_ms: int | None
    gap_detected: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GapRecord:
    schema_version: int
    gap_id: str
    source_id: str
    detected_utc: str
    reason: str
    previous_capture_id: str | None
    current_capture_id: str | None
    gap_ms: int | None = None
    expected_cadence_ms: int | None = None
    clock_skew_ms: int | None = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RecorderState:
    schema_version: int = 1
    mode: str = "IDLE"
    run_id: str = ""
    next_sequence: int = 1
    last_completed_utc: str = ""
    last_by_source: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RecorderState":
        return cls(
            schema_version=int(value.get("schema_version", 1)),
            mode=str(value.get("mode", "IDLE")),
            run_id=str(value.get("run_id", "")),
            next_sequence=int(value.get("next_sequence", 1)),
            last_completed_utc=str(value.get("last_completed_utc", "")),
            last_by_source=dict(value.get("last_by_source", {})),
        )
