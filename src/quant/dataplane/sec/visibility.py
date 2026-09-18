"""The P0 visibility firewall, as an executable check rather than a convention.

``P0_RAW_CAPTURE_CRITICAL_PATH_RECLASSIFICATION_2026-09-18.md`` section 5 allows
acquisition-health observability while forbidding anything that could let
observed content tune a still-open scientific rule. "Raw" is not "non
interpretable": a Form-4 payload exposes issuer, owner, codes, dates and amounts
directly.

So the firewall is checked, not asserted. ``find_leaks`` is pointed at whatever a
protocol-mutating actor can actually see - the status surface, ``CHIEF_BRIEF.md``,
the event log, exception text, the JSON snapshot - and the tests fail if any of
it carries interpretable filing content.

The rule that is easiest to break by accident is the last one: **filing counts**
are forbidden, so the lane reports work in flight as a boolean and storage
presence as a boolean, never as "3 filings captured".

It was broken by accident, exactly there. The first pre-t0 rodage artifact
published ``attempts_by_endpoint_kind.FILING = 7`` while asserting that it carried
no filing count. Under the frozen acquisition path one filing costs one FILING
request, so that number *is* a filing count by proxy. Blue observed it before it
was removed, and that exposure is irreversible; it is recorded in the checkpoint
and has no authority over any later scientific decision.

The lesson is that a prose promise is not a control. ``find_count_proxies``
therefore inspects a structured payload for the *shape* of the defect - any
numeric field whose key marks it as a count of filings or of the per-filing
request class - so the next artifact cannot make the same claim while carrying the
same number. ``find_leaks`` keeps scanning rendered text for content.
"""

from __future__ import annotations

import re
from typing import Any


#: Patterns that would mean interpretable filing content escaped the lane.
_LEAK_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("accession_number", re.compile(r"\b\d{10}-\d{2}-\d{6}\b")),
    ("filing_archive_path", re.compile(r"/Archives/edgar/data", re.IGNORECASE)),
    ("ownership_xml_body", re.compile(r"ownershipDocument|nonDerivativeT|derivativeT",
                                      re.IGNORECASE)),
    ("transaction_field", re.compile(
        r"transactionCode|transactionShares|transactionPricePerShare|"
        r"securityTitle|periodOfReport", re.IGNORECASE)),
    ("filer_identity_field", re.compile(r"issuerName|issuerTradingSymbol|rptOwnerName|"
                                        r"reportingOwnerId|officerTitle", re.IGNORECASE)),
    ("raw_markup_excerpt", re.compile(r"<\?xml|<!DOCTYPE|<SEC-DOCUMENT|<ownership",
                                      re.IGNORECASE)),
    ("sec_header_field", re.compile(r"ACCEPTANCE-DATETIME|CONFORMED SUBMISSION TYPE",
                                    re.IGNORECASE)),
)


#: Key fragments whose numeric value would be a filing count or a direct proxy
#: for one. FILING requests are listed because the acquisition path spends exactly
#: one on each filing, so publishing that count publishes the filing count.
_COUNT_PROXY_KEYS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("filing_request_count", ("filing",)),
    ("filing_count", ("filings", "filings_captured", "captured_filings")),
    ("accession_count", ("accession", "accessions")),
    ("envelope_count", ("envelope", "envelopes")),
    ("source_version_count", ("source_version", "source_versions")),
    # Found while sanitizing the first rodage artifact: the drain path completes
    # once per acquired filing, so a tally of DRAIN_COMPLETED causes or DRAINING
    # states is the filing count under a different name. Keys are matched on the
    # full path, which is how a nested per-cause breakdown is caught.
    ("drain_transition_count", ("drain_completed", "draining", "drain")),
    ("capture_transition_count", ("captured", "capture_count", "deduplicated")),
)

#: Numeric fields that describe acquisition health rather than scientific volume,
#: and are therefore permitted even though they are numbers.
_PERMITTED_NUMERIC_KEYS: frozenset[str] = frozenset({
    "raw_bytes", "byte_length", "declared_content_length", "requests_spent",
    "budget_reservations", "durable_attempt_ids", "distinct_attempt_ids",
    "limiter_waits", "limiter_wait_seconds", "backoff_step", "window_duration_seconds",
    "request_span_seconds", "average_requests_per_second", "scheduler_transitions",
    "obligations", "obligations_pending", "obligations_unexplained",
    "obligations_resolved_by_attempt", "obligations_resolved_by_supersession",
    "expected_actions", "service_starts", "supervised_service_starts",
    "attempts_recorded", "validated_polls", "objects_rehashed", "due_tolerance_seconds",
    "poll_seconds", "max_waits", "restart_delay_seconds", "restart_burst_limit",
})


def find_count_proxies(payload: Any, path: str = "") -> list[str]:
    """Paths in a structured payload that publish a filing count or a proxy.

    Walks the whole document rather than a known field list, because the defect
    this catches arrived as a nested aggregate (``attempts_by_endpoint_kind``) that
    no one thought of as a filing count when writing it.
    """
    found: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            here = f"{path}.{key}" if path else str(key)
            lowered = str(key).lower()
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)) and lowered not in _PERMITTED_NUMERIC_KEYS:
                for name, fragments in _COUNT_PROXY_KEYS:
                    haystack = f"{path}.{lowered}".lower()
                    if any(fragment in lowered or fragment in haystack
                           for fragment in fragments):
                        found.append(f"{here} ({name})")
                        break
            found.extend(find_count_proxies(value, here))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            found.extend(find_count_proxies(item, f"{path}[{index}]"))
    return sorted(set(found))


def assert_no_count_proxies(payload: Any, where: str) -> None:
    proxies = find_count_proxies(payload)
    if proxies:
        raise AssertionError(
            f"{where} publishes a filing count or proxy: {', '.join(proxies)}")


def find_leaks(text: str) -> list[str]:
    """Names of the leak classes present in ``text``. Empty means clean."""
    return sorted({name for name, pattern in _LEAK_PATTERNS if pattern.search(text)})


def assert_no_scientific_content(text: str, where: str) -> None:
    leaks = find_leaks(text)
    if leaks:
        raise AssertionError(f"{where} exposes Form-4 scientific content: {', '.join(leaks)}")


def firewall_safe_storage(storage: dict[str, Any]) -> dict[str, Any]:
    """Project storage health onto what a protocol-mutating actor may see.

    Byte totals and integrity properties are acquisition health. Object counts
    are not published: they are close enough to a filing count to be worth
    withholding while the scientific protocol is still open.
    """
    return {"raw_bytes": storage.get("raw_bytes", 0),
            "objects_present": bool(storage.get("raw_objects")),
            "incomplete_present": bool(storage.get("incomplete_objects")),
            "uncommitted_staging_present": bool(storage.get("uncommitted_staging_files")),
            "append_only": storage.get("append_only", True),
            "content_addressed": storage.get("content_addressed", True),
            "capture_state": storage.get("capture_state"),
            "visibility_state": storage.get("visibility_state"),
            "admissibility_state": storage.get("admissibility_state")}
