"""Small credential-free HTTP transport."""
from __future__ import annotations

from dataclasses import dataclass
import urllib.error
import urllib.request


@dataclass(frozen=True)
class FetchResponse:
    status: int
    headers: dict[str, str]
    body: bytes


class NetworkFetchError(RuntimeError):
    pass


class PublicHttpTransport:
    """GET-only transport that never reads or sends API credentials."""

    USER_AGENT = "Quant-Passive-Forward-Recorder/2.0"

    @property
    def request_headers(self) -> dict[str, str]:
        return {"User-Agent": self.USER_AGENT, "Accept": "application/json"}

    def fetch(self, endpoint: str, *, timeout_seconds: float) -> FetchResponse:
        request = urllib.request.Request(endpoint, method="GET", headers=self.request_headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                body = response.read()
                return FetchResponse(int(response.status), self._headers(response.headers), body)
        except urllib.error.HTTPError as exc:
            body = exc.read()
            return FetchResponse(int(exc.code), self._headers(exc.headers), body)
        except urllib.error.URLError as exc:
            raise NetworkFetchError(str(exc.reason)) from exc

    @staticmethod
    def _headers(headers: object) -> dict[str, str]:
        result: dict[str, str] = {}
        for name in ("Content-Type", "Date", "ETag", "Last-Modified", "X-MBX-USED-WEIGHT-1M"):
            value = headers.get(name) if hasattr(headers, "get") else None
            if value is not None:
                result[name.lower()] = str(value)
        return result
