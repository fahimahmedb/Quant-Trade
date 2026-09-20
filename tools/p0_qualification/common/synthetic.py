"""Synthetic (offline, no-network) SEC collector factory for Gate A campaigns.

Builds real instances of the production ``SecForm4Collector`` against an
isolated temporary root, exactly as ``tests/test_sec_form4_capture.py`` does,
so campaigns exercise actual acquisition-critical code rather than a
reimplementation of it. No network request is ever possible: the fake
transport never opens a socket.

This module is qualification-harness code, not a change to production
semantics: it only *calls* ``src/quant/dataplane/sec`` through its existing
public constructors.
"""

from __future__ import annotations

import random
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from quant.dataplane.sec.budget import SecTrafficBudget  # noqa: E402
from quant.dataplane.sec.collector import SecForm4Collector  # noqa: E402
from quant.dataplane.sec.policy import SecAccessPolicy  # noqa: E402
from quant.dataplane.sec.timebase import FrozenTimebase  # noqa: E402
from quant.dataplane.sec.transport import SecHttpResponse  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402

HARNESS_USER_AGENT = "Quant P0 Qualification Harness harness@quant.example.com"


def response(body: bytes, *, status: int = 200, headers: dict[str, str] | None = None,
             reason: str = "OK") -> SecHttpResponse:
    return SecHttpResponse(status=status, reason=reason, body=body, headers=headers or {})


class FakeTransport:
    """Same ``fetch`` contract as the real transport; never touches a socket."""

    def __init__(self, handler: Callable[[str, int], SecHttpResponse | BaseException]):
        self.handler = handler
        self.requested: list[str] = []
        self.permits_consumed: list[str] = []

    def fetch(self, path: str, permit: Any) -> SecHttpResponse:
        permit.consume()
        self.requested.append(path)
        self.permits_consumed.append(permit.attempt_id)
        outcome = self.handler(path, len(self.requested) - 1)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    def close(self) -> None:
        pass


class SyntheticEnvironment:
    """One isolated ``QuantPaths`` root plus a frozen clock, held for cleanup."""

    def __init__(self, *, start=None, seed: int = 3):
        self._directory = tempfile.TemporaryDirectory(prefix="quant-p0-qualification-")
        self.root = Path(self._directory.name)
        self.paths = QuantPaths(self.root).ensure()
        self.timebase = FrozenTimebase(start=start)
        self.seed = seed

    def close(self) -> None:
        self._directory.cleanup()

    def __enter__(self) -> "SyntheticEnvironment":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def policy(self, **overrides: Any) -> SecAccessPolicy:
        return SecAccessPolicy(user_agent=HARNESS_USER_AGENT, **overrides)

    def collector(self, handler: Callable[[str, int], SecHttpResponse | BaseException], *,
                  enable: bool = True, policy: SecAccessPolicy | None = None,
                  **policy_overrides: Any) -> tuple[SecForm4Collector, FakeTransport]:
        policy = policy or self.policy(**policy_overrides)
        transport = FakeTransport(handler)
        budget = SecTrafficBudget(self.paths.sec_budget, policy, timebase=self.timebase,
                                  rng=random.Random(self.seed))
        collector = SecForm4Collector(
            self.paths, policy=policy, transport=transport, timebase=self.timebase,
            budget=budget, root=REPO_ROOT)
        if enable:
            collector.enable()
        return collector, transport

    def reborn(self, handler: Callable[[str, int], SecHttpResponse | BaseException], *,
               policy: SecAccessPolicy | None = None, **policy_overrides: Any
               ) -> tuple[SecForm4Collector, FakeTransport]:
        """A fresh collector over the same durable state root: a restart."""
        return self.collector(handler, enable=False, policy=policy, **policy_overrides)


def empty_router(*, status: int = 404) -> Callable[[str, int], SecHttpResponse]:
    """Every request answered the same way; useful for cadence-only campaigns."""

    def handler(path: str, call: int) -> SecHttpResponse:
        return response(b"", status=status)

    return handler


def atom_only_router(atom_body: bytes) -> Callable[[str, int], SecHttpResponse]:
    def handler(path: str, call: int) -> SecHttpResponse:
        if path.startswith("/cgi-bin/browse-edgar"):
            return response(atom_body)
        return response(b"", status=404)

    return handler


def empty_atom_feed(*, updated: str = "2026-09-18T16:35:12-04:00") -> bytes:
    """A structurally valid, zero-entry EDGAR "latest filings" feed.

    Self-contained rather than imported from ``tests/test_sec_form4_capture``:
    this package must not depend on the production test suite's internals to
    stay usable if that suite's fixtures change shape.
    """
    return ("<?xml version=\"1.0\" encoding=\"ISO-8859-1\" ?>\n"
            "<feed xmlns=\"http://www.w3.org/2005/Atom\">\n"
            "\t<title>Latest Filings - Ownership Forms</title>\n"
            "\t<link rel=\"self\" type=\"application/atom+xml\" href=\"https://www.sec.gov/"
            "cgi-bin/browse-edgar?action=getcurrent\"/>\n"
            f"\t<updated>{updated}</updated>\n"
            "</feed>\n").encode("iso-8859-1")


def daily_index_router(atom_body: bytes, index_body: bytes | None,
                        *, index_status: int = 404) -> Callable[[str, int], SecHttpResponse]:
    """Discovery answers ``atom_body``; the daily index answers ``index_body``.

    ``index_body is None`` reproduces "no index published yet" (404), which
    the calendar matrix uses to prove ``404 != holiday``: a business day with
    no published index yet is COVERAGE_UNKNOWN, never inferred source-normal
    silence.
    """

    def handler(path: str, call: int) -> SecHttpResponse:
        if path.startswith("/cgi-bin/browse-edgar"):
            return response(atom_body)
        if path.startswith("/Archives/edgar/daily-index"):
            if index_body is None:
                return response(b"", status=index_status)
            return response(index_body, headers={"Content-Type": "text/plain"})
        return response(b"unexpected", status=404)

    return handler
