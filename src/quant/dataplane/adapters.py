"""Source adapters.

Adapters normalize an external source into the panel schema. They never invent
a bar: if a source is unreachable or returns an incomplete series they raise
``DataUnavailable`` so the Control Plane can mark dependent work BLOCKED with a
named reason, exactly as ``QUANT_NORTH_STAR.md`` requires.
"""

from __future__ import annotations

import csv
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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


def fetch_yahoo_daily(symbols: list[str], range_: str = "10y",
                      timeout: int = 45) -> tuple[PricePanel, dict[str, Any]]:
    """Fetch daily bars for several symbols from the free Yahoo chart endpoint."""
    rows: list[dict[str, Any]] = []
    per_symbol: dict[str, int] = {}
    for symbol in symbols:
        url = YAHOO_CHART.format(symbol=symbol) + f"?range={range_}&interval=1d"
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            raise DataUnavailable(f"{symbol}: {type(exc).__name__}: {exc}") from exc
        error = (payload.get("chart") or {}).get("error")
        if error:
            raise DataUnavailable(f"{symbol}: source returned error {error}")
        result = payload["chart"]["result"][0]
        quote = result["indicators"]["quote"][0]
        adjusted = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
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
        "adapter": "yahoo_daily", "requested_range": range_,
        "requested_symbols": symbols, "bars_per_symbol": per_symbol,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "timestamp_semantics": "bar timestamp is the session open; the date is the "
                               "exchange session and the bar is complete only after "
                               "that session's close",
        "caveats": YAHOO_CAVEATS}
    return PricePanel(rows), provenance


def load_local_tsv(path: Path, symbol: str) -> tuple[PricePanel, dict[str, Any]]:
    """Adapt the historical tab-separated index export already in the repository."""
    if not path.exists():
        raise DataUnavailable(f"{path} is absent")
    with path.open(encoding="utf-8") as handle:
        raw = list(csv.DictReader(handle, delimiter="\t"))
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
        "adapter": "local_tsv", "requested_symbols": [symbol],
        "timestamp_semantics": "daily index close; the index is not directly tradable",
        "caveats": ["price index without dividends; not a tradable instrument",
                    "no corporate-action or constituent history"]}
    return PricePanel(rows), provenance
