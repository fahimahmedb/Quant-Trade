"""Source adapters.

Adapters normalize an external source into the panel schema. They never invent
a bar: if a source is unreachable or returns an incomplete series they raise
``DataUnavailable`` so the Control Plane can mark dependent work BLOCKED with a
named reason, exactly as ``QUANT_NORTH_STAR.md`` requires.

When an ``EvidenceStore`` is supplied, adapters commit the exact source bytes
before parsing them. URI/path values remain provenance only; content identity is
the immutable SHA-256 address returned by the evidence store.
"""

from __future__ import annotations

import csv
import io
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import EvidenceStore, RawObject
from .panel import PricePanel


class DataUnavailable(RuntimeError):
    """A source could not be read. This is a blocked dependency, not a fault."""


YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
YAHOO_CAVEATS = [
    "adj_close is restated retroactively for dividends and splits, so adjusted "
    "levels are not strictly point-in-time; returns are standard practice but "
    "embed later corporate-action information",
    "the endpoint is an undocumented public JSON API with no availability "
    "guarantee and no vendor support",
    "prices are consolidated daily bars, not the venue-level quotes an "
    "execution model would eventually need",
]


def _evidence_projection(receipt: RawObject) -> dict[str, str]:
    """Expose only immutable evidence identity + acquisition receipt identity."""
    return {
        "sha256": receipt.sha256,
        "receipt_id": receipt.receipt_id,
        "source_uri": receipt.source_uri,
        "retrieved_at": receipt.retrieved_at,
    }


def fetch_yahoo_daily(
    symbols: list[str],
    range_: str = "10y",
    timeout: int = 45,
    *,
    evidence_store: EvidenceStore | None = None,
) -> tuple[PricePanel, dict[str, Any]]:
    """Fetch daily bars for several symbols from the free Yahoo chart endpoint.

    If ``evidence_store`` is provided, a successful transport is committed as
    exact bytes before JSON parsing. A parse/source-semantic failure can
    therefore never masquerade as an available normalized dataset, while the
    complete response that caused the failure remains auditable evidence.
    """
    rows: list[dict[str, Any]] = []
    per_symbol: dict[str, int] = {}
    evidence: list[dict[str, str]] = []
    for symbol in symbols:
        url = YAHOO_CHART.format(symbol=symbol) + f"?range={range_}&interval=1d"
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw_payload = response.read()
            retrieved_at = datetime.now(timezone.utc).isoformat()
            if evidence_store is not None:
                receipt = evidence_store.put_bytes(
                    raw_payload,
                    source_uri=url,
                    retrieved_at=retrieved_at,
                    media_type="application/json",
                    source_type="public_http",
                )
                evidence.append(_evidence_projection(receipt))
            payload = json.loads(raw_payload)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError,
                UnicodeDecodeError, OSError) as exc:
            raise DataUnavailable(f"{symbol}: {type(exc).__name__}: {exc}") from exc
        error = (payload.get("chart") or {}).get("error")
        if error:
            raise DataUnavailable(f"{symbol}: source returned error {error}")
        try:
            result = payload["chart"]["result"][0]
            quote = result["indicators"]["quote"][0]
            adjusted = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
        except (KeyError, IndexError, TypeError) as exc:
            raise DataUnavailable(f"{symbol}: malformed source payload: {exc}") from exc
        if adjusted is None:
            raise DataUnavailable(f"{symbol}: source returned no adjusted close series")
        kept = 0
        for index, stamp in enumerate(result["timestamp"]):
            values = [quote["open"][index], quote["high"][index], quote["low"][index],
                      quote["close"][index], adjusted[index]]
            if any(value is None for value in values):
                continue  # A partial bar is dropped, never interpolated.
            volume = quote["volume"][index] or 0
            rows.append({
                "date": datetime.fromtimestamp(stamp, tz=timezone.utc).date().isoformat(),
                "symbol": symbol, "open": values[0], "high": values[1], "low": values[2],
                "close": values[3], "adj_close": values[4], "volume": float(volume)})
            kept += 1
        if kept == 0:
            raise DataUnavailable(f"{symbol}: source returned no complete bars")
        per_symbol[symbol] = kept
    provenance = {
        "source": "Yahoo Finance chart API (public, credential-free)",
        "source_identity": "yahoo_finance",
        "source_product_identity": "chart_api_v8_daily",
        "adapter": "yahoo_daily", "requested_range": range_,
        "requested_symbols": symbols, "bars_per_symbol": per_symbol,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "evidence_status": "CAPTURED" if evidence_store is not None else "UNCAPTURED",
        "evidence": evidence,
        "timestamp_semantics": "bar timestamp is the session open; the date is the "
                               "exchange session and the bar is complete only after "
                               "that session's close",
        "caveats": YAHOO_CAVEATS}
    return PricePanel(rows), provenance


def load_local_tsv(
    path: Path,
    symbol: str,
    *,
    evidence_store: EvidenceStore | None = None,
) -> tuple[PricePanel, dict[str, Any]]:
    """Adapt the historical tab-separated index export already in the repository.

    The supplied file is read once as bytes. When an evidence store is present,
    those exact bytes are committed before the parser sees them.
    """
    if not path.exists():
        raise DataUnavailable(f"{path} is absent")
    try:
        raw_payload = path.read_bytes()
        retrieved_at = datetime.now(timezone.utc).isoformat()
        evidence: list[dict[str, str]] = []
        if evidence_store is not None:
            receipt = evidence_store.put_bytes(
                raw_payload,
                source_uri=path.resolve().as_uri(),
                retrieved_at=retrieved_at,
                media_type="text/tab-separated-values",
                source_type="operator_supplied_file",
            )
            evidence.append(_evidence_projection(receipt))
        raw = list(csv.DictReader(io.StringIO(raw_payload.decode("utf-8")), delimiter="\t"))
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise DataUnavailable(f"{path}: {type(exc).__name__}: {exc}") from exc
    rows = []
    for record in raw:
        date = datetime.strptime(record["date"], "%d/%m/%Y %H:%M").date().isoformat()
        close = float(record["clot"])
        rows.append({"date": date, "symbol": symbol, "open": float(record["ouv"]),
                     "high": float(record["haut"]), "low": float(record["bas"]),
                     "close": close, "adj_close": close, "volume": float(record["vol"] or 0)})
    if not rows:
        raise DataUnavailable(f"{path} contained no rows")
    provenance = {
        "source": "operator-supplied historical export committed to the repository",
        "source_identity": "operator_supplied_repository",
        "source_product_identity": "historical_index_tsv_export",
        "adapter": "local_tsv", "requested_symbols": [symbol],
        "retrieved_at": retrieved_at,
        "evidence_status": "CAPTURED" if evidence_store is not None else "UNCAPTURED",
        "evidence": evidence,
        "timestamp_semantics": "daily index close; the index is not directly tradable",
        "caveats": ["price index without dividends; not a tradable instrument",
                    "no corporate-action or constituent history"]}
    return PricePanel(rows), provenance