"""Credential-free Binance public market-data capture plan."""
from __future__ import annotations

from urllib.parse import urlencode

from .models import EndpointSpec

SPOT_BASE = "https://data-api.binance.vision"
USDM_BASE = "https://fapi.binance.com"
SUPPORTED = ("BTCUSDT", "ETHUSDT")


def _url(base: str, path: str, **params: object) -> str:
    query = urlencode(params)
    return f"{base}{path}" + (f"?{query}" if query else "")


def binance_public_plan(symbols: tuple[str, ...] = SUPPORTED) -> tuple[EndpointSpec, ...]:
    normalized = tuple(symbol.upper() for symbol in symbols)
    if not normalized or any(symbol not in SUPPORTED for symbol in normalized):
        raise ValueError(f"Builder D initial scope is limited to {SUPPORTED}")
    specs: list[EndpointSpec] = [
        EndpointSpec("binance-spot-time", "binance", "spot", None, "server_time", _url(SPOT_BASE, "/api/v3/time"), source_time_field="serverTime"),
    ]
    for symbol in normalized:
        specs.extend((
            EndpointSpec(f"binance-spot-exchange-{symbol.lower()}", "binance", "spot", symbol, "instrument_status", _url(SPOT_BASE, "/api/v3/exchangeInfo", symbol=symbol)),
            EndpointSpec(f"binance-spot-depth-{symbol.lower()}", "binance", "spot", symbol, "book_depth_20", _url(SPOT_BASE, "/api/v3/depth", symbol=symbol, limit=20)),
        ))
    specs.extend((
        EndpointSpec("binance-usdm-time", "binance", "perpetual", None, "server_time", _url(USDM_BASE, "/fapi/v1/time"), source_time_field="serverTime"),
        EndpointSpec("binance-usdm-exchange", "binance", "perpetual", None, "instrument_status", _url(USDM_BASE, "/fapi/v1/exchangeInfo"), source_time_field="serverTime"),
        EndpointSpec("binance-usdm-funding-info", "binance", "perpetual", None, "funding_info", _url(USDM_BASE, "/fapi/v1/fundingInfo")),
    ))
    for symbol in normalized:
        specs.extend((
            EndpointSpec(f"binance-usdm-depth-{symbol.lower()}", "binance", "perpetual", symbol, "book_depth_20", _url(USDM_BASE, "/fapi/v1/depth", symbol=symbol, limit=20), source_time_field="E"),
            EndpointSpec(f"binance-usdm-premium-{symbol.lower()}", "binance", "perpetual", symbol, "funding_mark_info", _url(USDM_BASE, "/fapi/v1/premiumIndex", symbol=symbol), source_time_field="time"),
            EndpointSpec(f"binance-usdm-funding-history-{symbol.lower()}", "binance", "perpetual", symbol, "funding_history", _url(USDM_BASE, "/fapi/v1/fundingRate", symbol=symbol, limit=10)),
        ))
    ids = [spec.source_id for spec in specs]
    if len(ids) != len(set(ids)):
        raise AssertionError("source IDs must be unique")
    return tuple(specs)
