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
