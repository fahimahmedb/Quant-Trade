"""SEC "Insider Transactions Data Sets" (Forms 3/4/5 structured data) ingestion.

Source (verified 2026-09-24 against the live SEC page, not guessed):

    index page  https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets
    zip links   https://www.sec.gov/files/<publisher-path>/<YYYY>q<Q>_form345.zip

The publisher path is *not* uniform (``structureddata/data/insider-transactions-
data-sets`` for 2006q1..2026q1, ``datastandardsinnovation/data/insider-
transactions-data-sets`` for 2026q2), so quarter URLs are always taken from the
index page's own links, never constructed.

Each zip holds tab-separated tables (``SUBMISSION.tsv``, ``REPORTINGOWNER.tsv``,
``NONDERIV_TRANS.tsv``, ...) plus ``insider_transactions_metadata.json`` and a
readme. Dates are ``DD-MON-YYYY``. Quarters partition by EDGAR filing date.

SEC fair access: sequential requests, at most 5 per second, backoff on
403/429/5xx, and a declared User-Agent taken only from ``QUANT_SEC_USER_AGENT``
(there is deliberately no default). Manifests record only *that* a declared
User-Agent was used (:data:`USER_AGENT_RECORD`), never the value or any hash of
it: an unkeyed hash of a short known-format string is a guessable identifier
for the contact address, and a keyed hash whose key lives in the ephemeral
``var/`` could not be verified later anyway, so no binding is kept.
"""

from __future__ import annotations

import csv
import hashlib
import io
import os
import re
import shutil
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

from quant.fastlane.firewall import LINEAGE_ID, Firewall, sha256_bytes, sha256_file

SOURCE_ID = "SEC_INSIDER_TRANSACTIONS_DATA_SETS"
DATA_PAGE_URL = ("https://www.sec.gov/data-research/sec-markets-data/"
                 "insider-transactions-data-sets")
SEC_ORIGIN = "https://www.sec.gov"
USER_AGENT_ENV = "QUANT_SEC_USER_AGENT"
FIRST_QUARTER = "2006q1"

# href="/files/<path>/2006q1_form345.zip"
ZIP_LINK_RE = re.compile(r'href="(/files/[A-Za-z0-9_./-]+/((\d{4})q([1-4]))_form345\.zip)"')

REQUIRED_MEMBERS = ("SUBMISSION.tsv", "REPORTINGOWNER.tsv", "NONDERIV_TRANS.tsv",
                    "FOOTNOTES.tsv")

REQUIRED_COLUMNS: Mapping[str, tuple[str, ...]] = {
    "SUBMISSION.tsv": ("ACCESSION_NUMBER", "FILING_DATE", "PERIOD_OF_REPORT",
                       "DATE_OF_ORIG_SUB", "DOCUMENT_TYPE", "ISSUERCIK",
                       "ISSUERNAME", "ISSUERTRADINGSYMBOL"),
    "REPORTINGOWNER.tsv": ("ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNER_RELATIONSHIP",
                           "RPTOWNER_TITLE", "RPTOWNER_TXT"),
    "NONDERIV_TRANS.tsv": ("ACCESSION_NUMBER", "NONDERIV_TRANS_SK", "SECURITY_TITLE",
                           "TRANS_DATE", "DEEMED_EXECUTION_DATE", "TRANS_FORM_TYPE",
                           "TRANS_CODE", "EQUITY_SWAP_INVOLVED", "TRANS_SHARES",
                           "TRANS_PRICEPERSHARE", "TRANS_ACQUIRED_DISP_CD",
                           "SHRS_OWND_FOLWNG_TRANS", "DIRECT_INDIRECT_OWNERSHIP"),
    "FOOTNOTES.tsv": ("ACCESSION_NUMBER", "FOOTNOTE_ID", "FOOTNOTE_TXT"),
}

MIN_REQUEST_INTERVAL_S = 0.25          # 4 req/s < SEC's 10 req/s and the 5 req/s rule here
RETRY_STATUSES = frozenset({403, 429, 500, 502, 503, 504})
MAX_ATTEMPTS = 6
BACKOFF_BASE_S = 2.0
BACKOFF_CAP_S = 120.0
DATA_BUDGET_BYTES = 3_000_000_000
MIN_FREE_BYTES = 5_000_000_000


class MissingUserAgent(RuntimeError):
    """``QUANT_SEC_USER_AGENT`` is absent or unusable; SEC access is refused."""


class SecFetchError(RuntimeError):
    pass


class DiskBudgetExceeded(RuntimeError):
    pass


class SecParseError(ValueError):
    pass


# --- User-Agent ---------------------------------------------------------------

def require_user_agent(env: Mapping[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    declared = (source.get(USER_AGENT_ENV) or "").strip()
    if not declared:
        raise MissingUserAgent(
            f"{USER_AGENT_ENV} is not set; SEC fair-access guidance requires a declared "
            "User-Agent with a contact address. There is no default.")
    if "@" not in declared:
        raise MissingUserAgent(f"{USER_AGENT_ENV} must carry a contact email address")
    return declared


USER_AGENT_RECORD = {"source_env": USER_AGENT_ENV, "declared": True, "value_stored": False}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- HTTP client --------------------------------------------------------------

@dataclass
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes | None = None


class SecClient:
    """Sequential, rate-limited SEC client with bounded retry/backoff."""

    def __init__(self, user_agent: str, *, opener: Callable[..., Any] | None = None,
                 sleep: Callable[[float], None] = time.sleep,
                 monotonic: Callable[[], float] = time.monotonic,
                 timeout_s: float = 120.0) -> None:
        if not user_agent:
            raise MissingUserAgent(f"{USER_AGENT_ENV} is required")
        self._user_agent = user_agent
        self._opener = opener or urllib.request.urlopen
        self._sleep = sleep
        self._monotonic = monotonic
        self._timeout = timeout_s
        self._last_request = None  # type: float | None
        self.requests_made = 0

    def _pace(self) -> None:
        if self._last_request is not None:
            wait = MIN_REQUEST_INTERVAL_S - (self._monotonic() - self._last_request)
            if wait > 0:
                self._sleep(wait)
        self._last_request = self._monotonic()

    def _request(self, url: str):
        req = urllib.request.Request(url, headers={
            "User-Agent": self._user_agent,
            "Accept-Encoding": "identity",
        })
        self._pace()
        self.requests_made += 1
        return self._opener(req, timeout=self._timeout)

    def _with_retry(self, url: str, consume: Callable[[Any], Any]) -> Any:
        last_error: Exception | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                with self._request(url) as resp:
                    return consume(resp)
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code not in RETRY_STATUSES:
                    raise SecFetchError(f"GET {url} -> HTTP {exc.code}") from exc
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                delay = _backoff(attempt, retry_after)
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                last_error = exc
                delay = _backoff(attempt, None)
            if attempt < MAX_ATTEMPTS:
                self._sleep(delay)
        raise SecFetchError(f"GET {url} failed after {MAX_ATTEMPTS} attempts: {last_error}")

    def get_bytes(self, url: str) -> HttpResponse:
        def consume(resp):
            return HttpResponse(status=resp.status, headers=_headers(resp), body=resp.read())
        return self._with_retry(url, consume)

    def download(self, url: str, target: Path) -> tuple[HttpResponse, int, str]:
        """Stream ``url`` into ``target``; return (response, bytes, sha256)."""
        def consume(resp):
            digest = hashlib.sha256()
            size = 0
            with open(target, "wb") as handle:
                while True:
                    block = resp.read(1 << 20)
                    if not block:
                        break
                    digest.update(block)
                    handle.write(block)
                    size += len(block)
                handle.flush()
                os.fsync(handle.fileno())
            headers = _headers(resp)
            declared = headers.get("content-length")
            if declared is not None and int(declared) != size:
                raise ConnectionError(f"truncated body: {size} of {declared} bytes")
            return HttpResponse(status=resp.status, headers=headers), size, digest.hexdigest()
        return self._with_retry(url, consume)


def _headers(resp) -> dict[str, str]:
    return {k.lower(): v for k, v in resp.headers.items()}


def _backoff(attempt: int, retry_after: str | None) -> float:
    if retry_after:
        try:
            return min(BACKOFF_CAP_S, max(1.0, float(retry_after)))
        except ValueError:
            pass
    return min(BACKOFF_CAP_S, BACKOFF_BASE_S * (2 ** (attempt - 1)))


# --- discovery ----------------------------------------------------------------

@dataclass(frozen=True)
class QuarterLink:
    quarter: str      # "2006q1"
    url: str          # absolute URL exactly as linked by the SEC page


def parse_quarter_links(html: str) -> list[QuarterLink]:
    found: dict[str, str] = {}
    for match in ZIP_LINK_RE.finditer(html):
        path, quarter = match.group(1), match.group(2)
        url = SEC_ORIGIN + path
        if quarter in found and found[quarter] != url:
            raise SecParseError(f"quarter {quarter} linked twice with different URLs")
        found[quarter] = url
    return [QuarterLink(q, found[q]) for q in sorted(found, key=quarter_key)]


def quarter_key(quarter: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d{4})q([1-4])", quarter)
    if not m:
        raise SecParseError(f"bad quarter label {quarter!r}")
    return int(m.group(1)), int(m.group(2))


def quarter_bounds(quarter: str) -> tuple[date, date]:
    year, q = quarter_key(quarter)
    start = date(year, 3 * (q - 1) + 1, 1)
    end = date(year + 1, 1, 1) if q == 4 else date(year, 3 * q + 1, 1)
    return start, date.fromordinal(end.toordinal() - 1)


def discover(fw: Firewall, client: SecClient) -> tuple[list[QuarterLink], dict]:
    resp = client.get_bytes(DATA_PAGE_URL)
    body = resp.body or b""
    links = parse_quarter_links(body.decode("utf-8", errors="replace"))
    record = {
        "lineage": LINEAGE_ID,
        "source": SOURCE_ID,
        "url": DATA_PAGE_URL,
        "retrieved_at_utc": utc_now_iso(),
        "bytes": len(body),
        "sha256": sha256_bytes(body),
        "http_last_modified": resp.headers.get("last-modified"),
        "http_etag": resp.headers.get("etag"),
        "user_agent": USER_AGENT_RECORD,
        "quarters_linked": [link.quarter for link in links],
        "urls": {link.quarter: link.url for link in links},
    }
    fw.write_json_atomic(fw.data("manifests", "sec_insider", "_discovery.json"), record)
    return links, record


# --- manifests and fetching ---------------------------------------------------

FINGERPRINT_FIELDS = ("source", "quarter", "url", "bytes", "sha256", "members")


def manifest_fingerprint(manifest: Mapping[str, Any]) -> str:
    """Content identity of one fetched file.

    Retrieval time, HTTP validators and the User-Agent record are provenance, not
    content, so they are excluded: refetching identical bytes yields the same
    fingerprint, and any byte change yields a different one.
    """
    from quant.fastlane.preregistration import canonical_json
    subset = {k: manifest.get(k) for k in FINGERPRINT_FIELDS}
    return "sha256:" + sha256_bytes(canonical_json(subset))


def zip_members(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive:
        return [{"name": info.filename, "size": info.file_size, "crc32": f"{info.CRC:08x}"}
                for info in sorted(archive.infolist(), key=lambda i: i.filename)]


def verify_zip(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        missing = [m for m in REQUIRED_MEMBERS if m not in names]
        if missing:
            raise SecParseError(f"{path.name} lacks required members {missing}")
        bad = archive.testzip()
        if bad is not None:
            raise SecParseError(f"{path.name}: CRC failure in member {bad}")
    return zip_members(path)


def raw_path(fw: Firewall, quarter: str) -> Path:
    return fw.data("raw", "sec_insider", f"{quarter}_form345.zip")


def manifest_path(fw: Firewall, quarter: str) -> Path:
    return fw.data("manifests", "sec_insider", f"{quarter}.json")


def load_manifest(fw: Firewall, quarter: str) -> dict | None:
    path = manifest_path(fw, quarter)
    if not path.exists():
        return None
    return fw.read_json(path)


def dir_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for dirpath, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                pass
    return total


def disk_guard(fw: Firewall, *, budget_bytes: int = DATA_BUDGET_BYTES,
               min_free_bytes: int = MIN_FREE_BYTES) -> dict:
    used = dir_bytes(fw.data_root)
    free = shutil.disk_usage(fw.repo_root).free
    if used > budget_bytes:
        raise DiskBudgetExceeded(f"var/fastlane holds {used} bytes > budget {budget_bytes}")
    if free < min_free_bytes:
        raise DiskBudgetExceeded(f"only {free} bytes free < floor {min_free_bytes}")
    return {"fastlane_bytes": used, "free_bytes": free}


def fetch_quarter(fw: Firewall, client: SecClient, link: QuarterLink,
                  *, budget_bytes: int = DATA_BUDGET_BYTES,
                  min_free_bytes: int = MIN_FREE_BYTES) -> tuple[dict, str]:
    """Fetch one quarter idempotently. Returns (manifest, action)."""
    target = raw_path(fw, link.quarter)
    existing = load_manifest(fw, link.quarter)
    if existing is not None and target.exists():
        if sha256_file(target) == existing["sha256"] and existing.get("url") == link.url:
            return existing, "skipped_sha256_match"
    disk_guard(fw, budget_bytes=budget_bytes, min_free_bytes=min_free_bytes)
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    retrieved_at = utc_now_iso()
    try:
        resp, size, digest = client.download(link.url, part)
        members = verify_zip(part)
    except BaseException:
        part.unlink(missing_ok=True)
        raise
    os.replace(part, target)
    manifest = {
        "lineage": LINEAGE_ID,
        "source": SOURCE_ID,
        "quarter": link.quarter,
        "url": link.url,
        "retrieved_at_utc": retrieved_at,
        "bytes": size,
        "sha256": digest,
        "http_status": resp.status,
        "http_last_modified": resp.headers.get("last-modified"),
        "http_etag": resp.headers.get("etag"),
        "http_content_length": resp.headers.get("content-length"),
        "user_agent": USER_AGENT_RECORD,
        "members": members,
        "local_path": str(target.relative_to(fw.repo_root)),
    }
    manifest["fingerprint"] = manifest_fingerprint(manifest)
    action = "fetched"
    if existing is not None and existing.get("sha256") != digest:
        # The SEC republished the file (or the local copy was damaged): keep the
        # superseded manifest instead of silently replacing provenance.
        stamp = retrieved_at.replace(":", "").replace("-", "")
        fw.write_json_atomic(
            fw.data("manifests", "sec_insider", "superseded",
                    f"{link.quarter}.{stamp}.json"), existing)
        manifest["supersedes_sha256"] = existing.get("sha256")
        action = "refetched_content_changed"
    fw.write_json_atomic(manifest_path(fw, link.quarter), manifest)
    return manifest, action


def select_quarters(links: list[QuarterLink], start: str = FIRST_QUARTER,
                    end: str | None = None) -> list[QuarterLink]:
    lo = quarter_key(start)
    hi = quarter_key(end) if end else (9999, 4)
    return [l for l in links if lo <= quarter_key(l.quarter) <= hi]


def consolidated_manifest(fw: Firewall, quarters: list[str], discovery: Mapping | None) -> dict:
    entries = []
    for quarter in quarters:
        manifest = load_manifest(fw, quarter)
        if manifest is None:
            continue
        entries.append({k: manifest.get(k) for k in (
            "quarter", "url", "retrieved_at_utc", "bytes", "sha256", "http_last_modified",
            "http_etag", "user_agent", "fingerprint")})
    from quant.fastlane.preregistration import canonical_json
    return {
        "lineage": LINEAGE_ID,
        "source": SOURCE_ID,
        "index_page": None if discovery is None else {
            k: discovery.get(k) for k in ("url", "retrieved_at_utc", "bytes", "sha256",
                                         "http_last_modified", "http_etag", "user_agent")},
        "quarters": entries,
        "quarter_count": len(entries),
        "total_bytes": sum(e["bytes"] for e in entries),
        "set_fingerprint": "sha256:" + sha256_bytes(canonical_json(
            [[e["quarter"], e["fingerprint"]] for e in entries])),
    }


def scrub_user_agent_bindings(fw: Firewall) -> int:
    """One-time migration: drop the former unkeyed ``ua_binding`` from manifests.

    Retrieval facts (url, time, bytes, sha256, validators, fingerprint) are kept
    unchanged; only the UA-derived hash is replaced by :data:`USER_AGENT_RECORD`.
    """
    changed = 0
    for path in fw.iter_files(fw.data("manifests", "sec_insider"), "*.json"):
        record = fw.read_json(path)
        if "ua_binding" in record:
            record.pop("ua_binding")
            record["user_agent"] = USER_AGENT_RECORD
            record["ua_binding_removed_at_utc"] = utc_now_iso()
            fw.write_json_atomic(path, record)
            changed += 1
    return changed


# --- parsing ------------------------------------------------------------------

_MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
           "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
_DATE_RE = re.compile(r"(\d{1,2})-([A-Za-z]{3})-(\d{4})")


def parse_sec_date(text: str | None) -> date | None:
    """Parse the data sets' ``DD-MON-YYYY`` dates (locale-independent).

    Empty -> None. Anything else malformed raises :class:`SecParseError`.
    """
    if text is None:
        return None
    value = text.strip()
    if not value:
        return None
    m = _DATE_RE.fullmatch(value)
    if not m:
        raise SecParseError(f"unparseable SEC date {text!r}")
    month = _MONTHS.get(m.group(2).upper())
    if month is None:
        raise SecParseError(f"unknown month in SEC date {text!r}")
    try:
        return date(int(m.group(3)), month, int(m.group(1)))
    except ValueError as exc:
        raise SecParseError(f"invalid SEC date {text!r}") from exc


def parse_number(text: str | None) -> float | None:
    if text is None:
        return None
    value = text.strip().replace(",", "")
    if not value:
        return None
    try:
        number = float(value)
    except ValueError as exc:
        raise SecParseError(f"unparseable number {text!r}") from exc
    if number != number or number in (float("inf"), float("-inf")):
        raise SecParseError(f"non-finite number {text!r}")
    return number


@dataclass
class TableStats:
    member: str
    rows: int = 0
    malformed_rows: int = 0
    decode_replacement_rows: int = 0
    header: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {"member": self.member, "rows": self.rows,
                "malformed_rows": self.malformed_rows,
                "decode_replacement_rows": self.decode_replacement_rows,
                "columns": list(self.header)}


def iter_table(source: Path | zipfile.ZipFile, member: str,
               stats: TableStats | None = None) -> Iterator[dict[str, str]]:
    """Yield rows of one TSV member as dicts keyed by the file's own header.

    Rows whose field count differs from the header are counted as malformed and
    skipped (never guessed). Required columns are checked against the header.
    """
    stats = stats if stats is not None else TableStats(member)
    own = not isinstance(source, zipfile.ZipFile)
    archive = zipfile.ZipFile(source) if own else source
    try:
        with archive.open(member) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
            reader = csv.reader(text, delimiter="\t", quoting=csv.QUOTE_NONE)
            try:
                header = tuple(h.strip().lstrip("﻿") for h in next(reader))
            except StopIteration:
                raise SecParseError(f"{member} is empty")
            stats.header = header
            required = REQUIRED_COLUMNS.get(member, ())
            missing = [c for c in required if c not in header]
            if missing:
                raise SecParseError(f"{member} lacks required columns {missing}")
            width = len(header)
            for row in reader:
                if len(row) != width:
                    if len(row) == 1 and not row[0].strip():
                        continue
                    stats.malformed_rows += 1
                    continue
                stats.rows += 1
                record = dict(zip(header, row))
                if any("�" in v for v in row):
                    stats.decode_replacement_rows += 1
                yield record
    finally:
        if own:
            archive.close()
