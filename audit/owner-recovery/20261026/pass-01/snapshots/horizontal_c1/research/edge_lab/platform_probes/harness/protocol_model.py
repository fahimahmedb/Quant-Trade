from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Tuple


@dataclass(frozen=True)
class SessionBinding:
    session_id: str
    generation: int
    worker_id: str
    engine: str
    lease_id: str
    heartbeat_interval_s: float = 2.0


@dataclass
class SessionState:
    binding: SessionBinding
    last_sequence: int = -1
    lease_expires_at: float = 0.0
    active: bool = True
    last_event_id: Optional[str] = None
    current_activity: Optional[str] = None


@dataclass
class CanonicalState:
    """Deterministic probe model only; this is not the production live backend."""

    sessions: Dict[Tuple[str, int], SessionState] = field(default_factory=dict)
    highest_generation: Dict[str, int] = field(default_factory=dict)
    seen_event_ids: Set[str] = field(default_factory=set)
    stream_ready: bool = False
    stream_cursor: int = 0
    rejected_event_count: int = 0
    unknown_event_count: int = 0

    @staticmethod
    def stale_threshold(interval_s: float) -> float:
        return max(6.0, 3.0 * interval_s)

    def start_session(self, binding: SessionBinding, now: float) -> None:
        highest = self.highest_generation.get(binding.session_id, -1)
        if binding.generation <= highest:
            self.rejected_event_count += 1
            raise ValueError("stale_or_duplicate_generation")
        self.highest_generation[binding.session_id] = binding.generation
        self.sessions[(binding.session_id, binding.generation)] = SessionState(
            binding=binding,
            lease_expires_at=now + self.stale_threshold(binding.heartbeat_interval_s),
        )

    def apply_event(
        self,
        *,
        event_id: str,
        session_id: str,
        generation: int,
        worker_id: str,
        engine: str,
        lease_id: str,
        sequence: int,
        event_type: str,
        now: float,
        activity_type: Optional[str] = None,
    ) -> str:
        if event_id in self.seen_event_ids:
            return "DUPLICATE_IGNORED"

        state = self.sessions.get((session_id, generation))
        if state is None:
            self.rejected_event_count += 1
            raise ValueError("unknown_session")

        binding = state.binding
        if (worker_id, engine, lease_id) != (binding.worker_id, binding.engine, binding.lease_id):
            self.rejected_event_count += 1
            raise ValueError("identity_binding_mismatch")

        if generation != self.highest_generation.get(session_id):
            self.rejected_event_count += 1
            raise ValueError("old_generation")

        if now > state.lease_expires_at:
            state.active = False
            self.rejected_event_count += 1
            raise ValueError("expired_lease")

        if sequence <= state.last_sequence:
            self.rejected_event_count += 1
            raise ValueError("old_sequence")

        if event_type not in {
            "HEARTBEAT",
            "ACTION_STARTED",
            "ACTION_COMPLETED",
            "SESSION_ENDED",
            "PROGRESS_PLAN_REVISED",
            "HANDOFF",
            "RESULT",
            "BLOCKED",
        }:
            self.unknown_event_count += 1
            raise ValueError("unknown_event")

        self.seen_event_ids.add(event_id)
        state.last_sequence = sequence
        state.last_event_id = event_id
        self.stream_cursor += 1

        if event_type == "HEARTBEAT":
            state.lease_expires_at = now + self.stale_threshold(binding.heartbeat_interval_s)
            state.active = True
        elif event_type == "ACTION_STARTED":
            state.current_activity = activity_type or "UNKNOWN"
        elif event_type == "ACTION_COMPLETED":
            state.current_activity = None
        elif event_type == "SESSION_ENDED":
            state.active = False
            state.current_activity = None

        return "APPLIED"

    def expire(self, now: float) -> None:
        for state in self.sessions.values():
            if state.active and now > state.lease_expires_at:
                state.active = False
                state.current_activity = None

    def backend_restart(self) -> None:
        for state in self.sessions.values():
            state.active = False
            state.current_activity = None
        self.stream_ready = False

    def snapshot(self) -> dict:
        return {
            "stream_cursor": self.stream_cursor,
            "stream_ready": self.stream_ready,
            "active_leases": [
                {
                    "session_id": s.binding.session_id,
                    "generation": s.binding.generation,
                    "worker_id": s.binding.worker_id,
                    "last_sequence": s.last_sequence,
                }
                for s in self.sessions.values()
                if s.active
            ],
        }

    def work_animation_allowed(self, session_id: str, generation: int) -> bool:
        state = self.sessions.get((session_id, generation))
        return bool(
            self.stream_ready
            and state
            and state.active
            and state.current_activity is not None
        )
