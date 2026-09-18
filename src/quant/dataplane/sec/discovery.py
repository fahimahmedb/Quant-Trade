"""SEC discovery semantics: what counts as a discovery poll that actually worked.

``NEXT_BUILD_MISSION.md`` P0 blocker: "A transport-level HTTP success is not
sufficient evidence of a successful discovery poll." Everything in this module
exists to make that true in code. The parser is deliberately unforgiving: it
would rather report ``DISCOVERY_INVALID`` than hand the collector a page it
cannot fully account for, because the failure mode being prevented is a silent
``NO_NEW_DATA`` on a broken response.

Two SEC surfaces are used, both chosen for compactness rather than breadth.

* **Latest Filings, Ownership/Form-4, Atom** - one small request per poll. It
  carries a stable accession identity per entry, from which the raw document
  locator is derived deterministically, so no crawl around the filing is needed.
* **Daily index (``master.<YYYYMMDD>.idx``)** - one compact pipe-delimited file
  per closed day, which is what the SEC publishes for exactly this purpose. It
  is the authority for *coverage*: expected Form-4 accessions versus captured.

The feed establishes continuity cheaply; the index proves completeness. Neither
is a crawl, which is what keeps the lane inside "download only what you need".
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable

from .policy import DISCOVERY_ENDPOINT_CLASS, FILING_ENDPOINT_CLASS


ATOM = "{http://www.w3.org/2005/Atom}"

#: Ownership form types. The lane captures Form 4 and its amendments.
FORM_4_TYPES = frozenset({"4", "4/A"})
OWNERSHIP_FORM_TYPES = frozenset({"3", "3/A", "4", "4/A", "5", "5/A"})

#: ``0001234567-26-000123``
ACCESSION_PATTERN = re.compile(r"\b(\d{10}-\d{2}-\d{6})\b")
#: ``/Archives/edgar/data/<cik>/<accession-no-dashes>/<accession>-index.htm``
INDEX_HREF_PATTERN = re.compile(
    r"/Archives/edgar/data/(?P<cik>\d+)/(?P<nodash>\d{18})/(?P<accession>\d{10}-\d{2}-\d{6})"
    r"-index\.html?", re.IGNORECASE)

_HTML_MARKERS = (b"<!doctype html", b"<html", b"<head", b"<body")

DAILY_INDEX_SEPARATOR = re.compile(rb"^-{4,}", re.MULTILINE)


class DiscoveryInvalid(RuntimeError):
    """A response cannot be shown to be a correctly completed discovery.

    The message is a stable reason class, never response content: it reaches the
    attempt journal and the event log, which are inside the visibility firewall.
    """

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def discovery_path(start: int = 0, count: int = 40, form_type: str = "4") -> str:
    """The Latest Filings Ownership/Form-4 Atom request for one page."""
    return ("/cgi-bin/browse-edgar?action=getcurrent"
            f"&type={form_type}&company=&dateb=&owner=include"
            f"&start={int(start)}&count={int(count)}&output=atom")


def discovery_url(start: int = 0, count: int = 40, form_type: str = "4") -> str:
    return "https://www.sec.gov" + discovery_path(start, count, form_type)


def daily_index_path(day: date) -> str:
    quarter = (day.month - 1) // 3 + 1
    return (f"/Archives/edgar/daily-index/{day.year}/QT{quarter}/"
            f"master.{day:%Y%m%d}.idx")


def daily_index_url(day: date) -> str:
    return "https://www.sec.gov" + daily_index_path(day)


@dataclass(frozen=True)
class DiscoveryEntry:
    """One discovered filing, reduced to what acquisition needs.

    Deliberately carries no title, issuer, owner or summary. The lane has no use
    for them, and a field that does not exist cannot leak.
    """

    accession: str
    form_type: str
    cik: str
    #: Path of the complete submission text file: one request, no crawl.
    raw_document_path: str
    index_path: str
    source_published_at_utc: str | None = None

    @property
    def raw_document_url(self) -> str:
        return "https://www.sec.gov" + self.raw_document_path

    @property
    def is_form_4(self) -> bool:
        return self.form_type in FORM_4_TYPES


@dataclass
class DiscoveryPage:
    """One validated discovery page plus the continuation facts it supplies."""

    requested_start: int
    requested_count: int
    form_type: str
    feed_updated: str | None
    entries: list[DiscoveryEntry] = field(default_factory=list)

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    @property
    def page_full(self) -> bool:
        """A full page is the endpoint's way of saying "there may be more"."""
        return self.entry_count >= self.requested_count

    @property
    def next_start(self) -> int:
        return self.requested_start + self.requested_count

    def form_4_entries(self) -> list[DiscoveryEntry]:
        return [entry for entry in self.entries if entry.is_form_4]

    def pagination_metadata(self) -> dict[str, Any]:
        """Firewall-safe continuation metadata: offsets, never filing counts."""
        return {"requested_start": self.requested_start,
                "requested_count": self.requested_count,
                "page_full": self.page_full,
                "next_start": self.next_start if self.page_full else None}


def looks_like_html(body: bytes) -> bool:
    head = body[:2048].lstrip().lower()
    return any(head.startswith(marker) or marker in head for marker in _HTML_MARKERS)


def parse_discovery_page(body: bytes, *, requested_start: int, requested_count: int,
                         form_type: str = "4") -> DiscoveryPage:
    """Validate and parse one discovery page, or raise ``DiscoveryInvalid``.

    Every rejection here is a case the mission requires to become ERROR/BLOCKED
    rather than ``NO_NEW_DATA``.
    """
    if not body.strip():
        raise DiscoveryInvalid("empty_discovery_body")
    if looks_like_html(body):
        # An HTML error/maintenance page served with a nominal 200 is the
        # canonical false-success this check exists to stop.
        raise DiscoveryInvalid("html_page_returned_for_atom_discovery")
    try:
        root = ElementTree.fromstring(body)
    except ElementTree.ParseError as exc:
        raise DiscoveryInvalid(f"discovery_xml_parse_failed:{type(exc).__name__}") from exc
    if root.tag != f"{ATOM}feed":
        raise DiscoveryInvalid("discovery_root_is_not_an_atom_feed")

    # Structural markers are what establish that the query itself completed,
    # rather than that some XML was returned.
    updated = root.findtext(f"{ATOM}updated")
    title = root.findtext(f"{ATOM}title")
    links = root.findall(f"{ATOM}link")
    if not title or not str(title).strip():
        raise DiscoveryInvalid("discovery_feed_missing_title")
    if not updated or not str(updated).strip():
        raise DiscoveryInvalid("discovery_feed_missing_updated_marker")
    if not links:
        raise DiscoveryInvalid("discovery_feed_missing_self_description")

    raw_entries = root.findall(f"{ATOM}entry")
    if len(raw_entries) > requested_count:
        # The endpoint returned more than the window asked for, so the
        # continuation arithmetic this poll relies on does not hold.
        raise DiscoveryInvalid("discovery_returned_more_entries_than_requested")

    entries = [_parse_entry(element, form_type) for element in raw_entries]
    return DiscoveryPage(requested_start=requested_start, requested_count=requested_count,
                         form_type=form_type, feed_updated=str(updated).strip(),
                         entries=entries)


def _parse_entry(element: ElementTree.Element, requested_form_type: str) -> DiscoveryEntry:
    category = element.find(f"{ATOM}category")
    term = (category.get("term") if category is not None else None)
    if not term or not term.strip():
        # Without a form type the filter cannot be shown to work, so this is an
        # error rather than an entry to skip.
        raise DiscoveryInvalid("discovery_entry_missing_form_type")
    term = term.strip()
    if term not in OWNERSHIP_FORM_TYPES:
        raise DiscoveryInvalid(f"discovery_form_type_filter_mismatch:{_safe_term(term)}")
    if requested_form_type in FORM_4_TYPES and term not in FORM_4_TYPES:
        # The request asked for Form 4 and the source answered with something
        # else: the filter configuration cannot be trusted this poll.
        raise DiscoveryInvalid(f"discovery_form_type_filter_mismatch:{_safe_term(term)}")

    identifier = element.findtext(f"{ATOM}id") or ""
    from_id = ACCESSION_PATTERN.search(identifier)
    href = ""
    for link in element.findall(f"{ATOM}link"):
        candidate = link.get("href") or ""
        if INDEX_HREF_PATTERN.search(candidate):
            href = candidate
            break
        href = href or candidate
    match = INDEX_HREF_PATTERN.search(href)
    if match is None:
        raise DiscoveryInvalid("discovery_entry_locator_unrecognized")
    accession = match.group("accession")
    if from_id and from_id.group(1) != accession:
        # Two disagreeing identities mean the stable source identity this lane
        # keys everything on is not established.
        raise DiscoveryInvalid("discovery_entry_accession_identity_conflict")
    if not from_id and not accession:
        raise DiscoveryInvalid("discovery_entry_missing_accession")

    cik = match.group("cik")
    nodash = match.group("nodash")
    published = element.findtext(f"{ATOM}updated")
    return DiscoveryEntry(
        accession=accession, form_type=term, cik=cik,
        raw_document_path=f"/Archives/edgar/data/{cik}/{nodash}/{accession}.txt",
        index_path=INDEX_HREF_PATTERN.search(href).group(0),
        source_published_at_utc=(published.strip() if published else None))


def _safe_term(term: str) -> str:
    """Keep a reason class bounded and free of arbitrary source text."""
    cleaned = re.sub(r"[^A-Za-z0-9/._-]", "", term)[:12]
    return cleaned or "unknown"


@dataclass
class DailyIndexPage:
    """Expected Form-4 accessions for one closed day, from the SEC daily index."""

    day: date
    accessions: list[str] = field(default_factory=list)
    total_rows: int = 0

    def entry_count(self) -> int:
        return len(self.accessions)


def parse_daily_index(body: bytes, day: date) -> DailyIndexPage:
    """Parse ``master.<YYYYMMDD>.idx``, or raise ``DiscoveryInvalid``.

    The pipe-delimited master index is used rather than the space-padded form
    index because column alignment is not something to guess at when the answer
    decides whether coverage is claimed complete.
    """
    if not body.strip():
        raise DiscoveryInvalid("empty_daily_index_body")
    if looks_like_html(body):
        raise DiscoveryInvalid("html_page_returned_for_daily_index")
    separator = DAILY_INDEX_SEPARATOR.search(body)
    if separator is None:
        raise DiscoveryInvalid("daily_index_missing_header_separator")
    payload = body[separator.end():]
    accessions: list[str] = []
    rows = 0
    for line in payload.splitlines():
        text = line.decode("latin-1", errors="replace").strip()
        if not text:
            continue
        fields = text.split("|")
        if len(fields) != 5:
            raise DiscoveryInvalid("daily_index_row_shape_unexpected")
        rows += 1
        _cik, _company, form_type, _filed, filename = (value.strip() for value in fields)
        if form_type not in FORM_4_TYPES:
            continue
        match = ACCESSION_PATTERN.search(filename)
        if match is None:
            raise DiscoveryInvalid("daily_index_row_missing_accession")
        accessions.append(match.group(1))
    if rows == 0:
        # A published daily index always lists that day's filings. An empty one
        # cannot confirm coverage, so it is an error rather than "nothing filed".
        raise DiscoveryInvalid("daily_index_contained_no_rows")
    return DailyIndexPage(day=day, accessions=accessions, total_rows=rows)


def endpoint_class_for(kind: str) -> str:
    return {"DISCOVERY": DISCOVERY_ENDPOINT_CLASS,
            "FILING": FILING_ENDPOINT_CLASS,
            "RECONCILE": "edgar_daily_index"}.get(kind, "sec_unknown")


def form_4_identities(entries: Iterable[DiscoveryEntry]) -> list[str]:
    return [entry.accession for entry in entries if entry.is_form_4]
