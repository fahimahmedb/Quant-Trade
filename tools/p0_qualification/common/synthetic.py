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
from quant.dataplane.sec.supervisor import DEPLOYMENT_RESTART  # noqa: E402
from quant.dataplane.sec.timebase import FrozenTimebase  # noqa: E402
from quant.dataplane.sec.transport import SecHttpResponse  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402
from quant.state import append_jsonl  # noqa: E402

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

    def seed_lifecycle_start(self, collector: SecForm4Collector, *,
                             boot_id: str = "qualification-harness-boot",
                             supervisor_id: str = "qualification-harness-supervisor"
                             ) -> None:
        """Record one legitimate external lifecycle event, as the real
        launcher/supervisor would before ever handing control to the
        collector. Without this, ``audit_observation_window`` correctly
        reports ``LIFECYCLE_PROVENANCE_MISSING`` - a real production
        precondition, not a harness bug - because no campaign built directly
        on ``SyntheticEnvironment`` goes through the actual supervisor.
        """
        append_jsonl(collector.paths.sec_lifecycle, {
            "lifecycle_cause": DEPLOYMENT_RESTART,
            "boot_id": boot_id,
            "supervisor_id": supervisor_id,
            "recorded_at_utc": self.timebase.now_iso(),
            "boot_at_utc": self.timebase.now_iso(),
            "acquisition_critical_fingerprint": collector.fingerprint or "UNAVAILABLE",
        })


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


def empty_daily_index() -> bytes:
    """A structurally valid EDGAR master index with zero *Form-4* rows.

    Matches the real header shape (``parse_daily_index`` requires the
    ``CIK|Company Name|...`` separator line). Production deliberately treats
    a genuinely zero-row index as invalid (``daily_index_contained_no_rows``:
    "a published daily index always lists that day's filings"), so this
    carries exactly one non-Form-4 row - realistic (some other form is always
    filed) and yields zero missing Form-4 accessions, so reconciliation
    succeeds cleanly rather than failing discovery validation.
    """
    return (
        b"Description:           Master Index of EDGAR Dissemination Feed by Item Type\n"
        b"Last Data Received:    September 17, 2026\n"
        b"Comments:              webmaster@sec.gov\n"
        b"Anonymous FTP:         ftp://ftp.sec.gov/edgar/\n\n \n"
        b"CIK|Company Name|Form Type|Date Filed|Filename\n"
        b"--------------------------------------------------------------------------------\n"
        b"1000000000|UNRELATED ISSUER CORP|8-K|2026-09-17|edgar/data/1000000000/"
        b"0001000000-26-000001.txt\n"
    )


def stable_atom_feed(*, accession: str = "9000000001-26-000001",
                     updated: str = "2026-09-01T16:35:12-04:00") -> bytes:
    """One synthetic Form-4 entry, always the same identity.

    Unlike ``empty_atom_feed``, this reproduces what a real EDGAR "latest
    filings" feed actually looks like during a quiet period: it never goes
    fully empty, it keeps showing its rolling window of recent entries. A
    permanently *empty* feed cannot let the collector re-establish cursor
    continuity after the first poll (there is no entry to find the anchor
    in), which opens a ``CURSOR_FELL_OUT_OF_WINDOW`` gap on every following
    poll - a harness-methodology artefact, not a production defect. Long
    campaigns that need coverage to reach ``COMPLETE`` and stay there should
    use this feed, not ``empty_atom_feed``.
    """
    return (
        "<?xml version=\"1.0\" encoding=\"ISO-8859-1\" ?>\n"
        "<feed xmlns=\"http://www.w3.org/2005/Atom\">\n"
        "\t<title>Latest Filings - Ownership Forms</title>\n"
        "\t<link rel=\"self\" type=\"application/atom+xml\" href=\"https://www.sec.gov/"
        "cgi-bin/browse-edgar?action=getcurrent\"/>\n"
        f"\t<updated>{updated}</updated>\n"
        "\t<entry>\n"
        "\t\t<title>4 - SYNTHETIC ISSUER 1 (9000000001) (Issuer)</title>\n"
        "\t\t<link rel=\"alternate\" type=\"text/html\" href=\"https://www.sec.gov/Archives/"
        f"edgar/data/9000000001/{accession.replace('-', '')}/{accession}-index.htm\"/>\n"
        f"\t\t<updated>{updated}</updated>\n"
        "\t\t<category scheme=\"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany\" "
        "label=\"form type\" term=\"4\"/>\n"
        f"\t\t<id>urn:tag:sec.gov,2008:accession-number={accession}</id>\n"
        "\t</entry>\n"
        "</feed>\n"
    ).encode("iso-8859-1")


#: The shared production/test fixture, reused rather than duplicated: any
#: bytes SEC returns for a captured filing must still parse as a real Form-4
#: submission for the capture pipeline to accept it.
_FORM4_SUBMISSION_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "sec" / "form4_submission.txt"


def daily_index_router(atom_body: bytes, index_body: bytes | None,
                        *, index_status: int = 404,
                        filing_body: bytes | None = None
                        ) -> Callable[[str, int], SecHttpResponse]:
    """Discovery answers ``atom_body``; the daily index answers ``index_body``.

    ``index_body is None`` reproduces "no index published yet" (404), which
    the calendar matrix uses to prove ``404 != holiday``: a business day with
    no published index yet is COVERAGE_UNKNOWN, never inferred source-normal
    silence.

    ``filing_body`` answers a ``.txt`` submission fetch (defaults to the
    shared ``tests/fixtures/sec/form4_submission.txt`` fixture) so a campaign
    that calls ``collector.drain()`` after ``poll()`` - as a real service loop
    does - can actually resolve a queued filing instead of leaving it pending
    forever.
    """
    filing_bytes = filing_body if filing_body is not None else _FORM4_SUBMISSION_FIXTURE.read_bytes()

    def handler(path: str, call: int) -> SecHttpResponse:
        if path.startswith("/cgi-bin/browse-edgar"):
            return response(atom_body)
        if path.startswith("/Archives/edgar/daily-index"):
            if index_body is None:
                return response(b"", status=index_status)
            return response(index_body, headers={"Content-Type": "text/plain"})
        if path.endswith(".txt"):
            return response(filing_bytes, headers={"Content-Type": "text/plain"})
        return response(b"unexpected", status=404)

    return handler
