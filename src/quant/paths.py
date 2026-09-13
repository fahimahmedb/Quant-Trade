"""Filesystem layout.

``NEXT_BUILD_MISSION.md`` requires a clear separation between repository
fixtures and local operational state:

``data/``, ``research/``, ``schemas/``   committed inputs and contracts
``var/``                                 live operational state (git-ignored)

A different ``root`` gives a fully isolated system, which is how the tests and
the restart demonstration avoid touching the operator's real state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QuantPaths:
    root: Path

    @property
    def var(self) -> Path:
        return self.root / "var"

    # --- committed repository content -------------------------------------
    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def datasets(self) -> Path:
        return self.data / "datasets"

    # --- live operational state -------------------------------------------
    @property
    def events(self) -> Path:
        return self.var / "events.jsonl"

    @property
    def components(self) -> Path:
        return self.var / "components.json"

    @property
    def control(self) -> Path:
        return self.var / "control_state.json"

    @property
    def work_queue(self) -> Path:
        return self.var / "work_queue.json"

    @property
    def dataset_registry(self) -> Path:
        return self.var / "dataset_registry.json"

    @property
    def strategies(self) -> Path:
        return self.var / "strategies.json"

    @property
    def book(self) -> Path:
        return self.var / "book.json"

    @property
    def opportunities(self) -> Path:
        return self.var / "opportunities.jsonl"

    @property
    def research_tickets(self) -> Path:
        return self.var / "research_tickets"

    @property
    def research_memory(self) -> Path:
        return self.var / "research_memory.jsonl"

    @property
    def learning(self) -> Path:
        return self.var / "learning.json"

    @property
    def status_surface(self) -> Path:
        return self.var / "status.txt"

    def ensure(self) -> "QuantPaths":
        self.var.mkdir(parents=True, exist_ok=True)
        return self
