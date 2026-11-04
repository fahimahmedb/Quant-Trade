"""One-shot official CFR 242.204 source capture; not an engine or source admission."""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from datetime import datetime, timezone

URL = "https://www.govinfo.gov/content/pkg/CFR-2025-title17-vol5/html/CFR-2025-title17-vol5.htm"

class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.muted = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.muted += 1
        elif tag in {"br", "p", "pre", "div", "tr"}:
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.muted = max(0, self.muted - 1)
        elif tag in {"p", "pre", "div", "tr"}:
            self.parts.append("\n")
    def handle_data(self, data):
        if not self.muted:
            self.parts.append(data)

def extract_section(raw: bytes) -> str:
    if not raw or len(raw) > 20_000_000 or b"<" not in raw[:1000]:
        raise ValueError("CFR_RAW_HTML_INVALID_OR_TOO_LARGE")
    parser = _Text()
    parser.feed(raw.decode("utf-8"))
    text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    if not re.search(r"April\s+1,\s+2025", text[:10000], re.IGNORECASE):
        raise ValueError("CFR_2025_EDITION_NOT_PROVEN")
    heads = list(re.finditer(r"Sec\.?\s+242\.204\s+Close-out requirement\.", text, re.IGNORECASE))
    if len(heads) != 1:
        raise ValueError("RULE204_HEADING_MISSING_OR_AMBIGUOUS")
    start = heads[0].start()
    trailer = re.search(r"Regulation\s+ATS\s*--\s*Alternative Trading Systems", text[heads[0].end():], re.IGNORECASE)
    if not trailer:
        raise ValueError("RULE204_END_BOUNDARY_MISSING")
    section = text[start:heads[0].end() + trailer.start()].strip()
    if len(section) < 2500 or len(section) > 25000:
        raise ValueError("RULE204_SECTION_LENGTH_INVALID")
    for marker in (
        "a participant of a registered clearing agency",
        "third consecutive settlement day",
        "thirty-fifth consecutive calendar day",
        "bona fide market making activities",
        "a broker or dealer",
        "(b)", "(c)", "(d)", "(e)", "(f)", "(g)", "89 FR 26608",
    ):
        if marker.casefold() not in section.casefold():
            raise ValueError("RULE204_REQUIRED_CLAUSE_MISSING:" + marker)
    return section

def receipt(raw: bytes, *, captured_at: str, source_url: str = URL) -> dict:
    if source_url != URL:
        raise ValueError("NOT_OFFICIAL_PINNED_CFR_SOURCE")
    stamp = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    if stamp.utcoffset() is None or stamp.astimezone(timezone.utc).date() < datetime(2025, 4, 1, tzinfo=timezone.utc).date():
        raise ValueError("CAPTURE_CLOCK_INVALID")
    section = extract_section(raw)
    return {
        "schema_version": "f6-rule204-capture-receipt-v1",
        "status": "CAPTURED_NOT_SCIENTIFICALLY_ADMITTED",
        "source_url": source_url,
        "edition_date": "2025-04-01",
        "section": "17 CFR 242.204",
        "capture_clock_basis": "FIRST_VERIFIED_PUBLIC_CAPTURE_NOT_HISTORICAL_PIT",
        "captured_at": stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "raw_html_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_html_byte_length": len(raw),
        "extracted_section_sha256": hashlib.sha256(section.encode("utf-8")).hexdigest(),
        "extracted_section_length": len(section),
        "section_text": section,
        "claims_not_authorized": [
            "empirical_return", "forced_quantity", "economic_edge",
            "current_legal_opinion", "trading", "capital",
        ],
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--captured-at", required=True)
    args = parser.parse_args()
    result = receipt(args.input.read_bytes(), captured_at=args.captured_at)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "section_text"}, sort_keys=True))

if __name__ == "__main__":
    main()
