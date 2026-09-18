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
    def desk_journal(self) -> Path:
        return self.var / "desk_journal.json"

    @property
    def evaluation_ledger(self) -> Path:
        return self.var / "evaluation_ledger.json"

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

    # --- SEC / Form-4 P0 raw capture --------------------------------------
    # The capture lane keeps its own subtree so an immutable raw object can
    # never share a path with mutable operational state, and so the restricted
    # journal that carries identifying locators is a separate directory from
    # the firewall-safe journals a status surface may read.
    @property
    def sec(self) -> Path:
        return self.var / "sec"

    @property
    def sec_raw_objects(self) -> Path:
        """Content-addressed immutable raw response bodies."""
        return self.sec / "raw"

    @property
    def sec_incomplete_objects(self) -> Path:
        """Partial bodies from truncated transfers. Never a valid capture."""
        return self.sec / "incomplete"

    @property
    def sec_staging(self) -> Path:
        """Uncommitted writes. A crash here leaves no acknowledged evidence."""
        return self.sec / "staging"

    @property
    def sec_raw_manifest(self) -> Path:
        return self.sec / "raw_manifest.jsonl"

    @property
    def sec_attempts(self) -> Path:
        return self.sec / "attempts.jsonl"

    @property
    def sec_coverage(self) -> Path:
        return self.sec / "coverage.jsonl"

    @property
    def sec_collector_state(self) -> Path:
        return self.sec / "collector_state.json"

    @property
    def sec_budget(self) -> Path:
        """Global SEC traffic budget, shared by every SEC consumer."""
        return self.sec / "sec_traffic_budget.json"

    # Restricted tier. These journals carry source identity, so no status
    # surface, brief, log or exception may read them. They exist because
    # point-in-time reconstructability requires knowing which source produced
    # which bytes, which the firewall-safe tier deliberately cannot say.
    @property
    def sec_restricted(self) -> Path:
        return self.sec / "restricted"

    @property
    def sec_locators(self) -> Path:
        return self.sec_restricted / "locators.jsonl"

    @property
    def sec_envelopes(self) -> Path:
        return self.sec_restricted / "envelopes.jsonl"

    @property
    def sec_source_versions(self) -> Path:
        return self.sec_restricted / "source_versions.jsonl"

    def sec_firewall_safe_journals(self) -> tuple[Path, ...]:
        """Capture state a protocol-mutating surface is allowed to read."""
        return (self.sec_attempts, self.sec_raw_manifest, self.sec_coverage,
                self.sec_collector_state, self.sec_budget)

    def sec_restricted_journals(self) -> tuple[Path, ...]:
        return (self.sec_locators, self.sec_envelopes, self.sec_source_versions)

    def ensure(self) -> "QuantPaths":
        self.var.mkdir(parents=True, exist_ok=True)
        return self

    def ensure_sec(self) -> "QuantPaths":
        """Create the capture subtree. Called by the collector, not by boot."""
        for directory in (self.sec, self.sec_raw_objects, self.sec_incomplete_objects,
                          self.sec_staging, self.sec_restricted):
            directory.mkdir(parents=True, exist_ok=True)
        return self
