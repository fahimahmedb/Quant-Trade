"""HTTP transport for the SEC capture lane.

Two requirements shape this module and rule out ``urllib``/``requests`` defaults.

**Exact received bytes.** The mission forbids hashing a transparently
decompressed representation. ``http.client`` does not decode ``Content-Encoding``,
so ``read()`` returns the body exactly as it arrived; decoding happens later, on
a throwaway copy, only to *parse*. The stored object and its SHA-256 are always
the bytes on the wire.

**Completeness must be provable.** A transfer cut short is not a capture. The
declared ``Content-Length`` is compared against what was actually read, a
premature end of a chunked body raises rather than returning a short body, and
a whole-request deadline stops a trickling response from stalling liveness
silently.

The connection is kept alive and reused across requests, which is the cheapest
possible thing to do to SEC infrastructure: the frozen policy already spaces
requests, and reuse removes a TLS handshake per filing.
"""

from __future__ import annotations

import gzip
import http.client
import socket
import ssl
import zlib
from dataclasses import dataclass, field
from typing import Any

from .policy import SecAccessPolicy
from .timebase import Timebase


SEC_HOST = "www.sec.gov"

#: Transfer outcomes. Only ``COMPLETE`` may become a valid raw capture.
COMPLETE = "COMPLETE"
TRUNCATED = "TRUNCATED"
DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
OVERSIZED = "OVERSIZED"
TRANSPORT_ERROR = "TRANSPORT_ERROR"

#: Response headers worth preserving to establish whether the body is complete.
PRESERVED_HEADERS = ("Content-Type", "Content-Encoding", "Content-Length",
                     "Transfer-Encoding", "Retry-After", "Date", "Last-Modified", "ETag")


class SecTransportError(RuntimeError):
    """A request did not produce a usable HTTP response."""

    def __init__(self, error_class: str, outcome: str = TRANSPORT_ERROR,
                 partial: bytes = b""):
        # The message carries a class name, never response content: exception
        # text reaches logs, and logs are inside the visibility firewall.
        super().__init__(error_class)
        self.error_class = error_class
        self.outcome = outcome
        self.partial = partial


@dataclass
class SecHttpResponse:
    """One HTTP response, described well enough to prove what was received."""

    status: int
    reason: str
    #: Exact bytes received, before any content decoding.
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)
    transfer_outcome: str = COMPLETE

    @property
    def byte_length(self) -> int:
        return len(self.body)

    @property
    def content_encoding(self) -> str | None:
        return self.headers.get("Content-Encoding")

    @property
    def media_type(self) -> str | None:
        value = self.headers.get("Content-Type")
        return value.split(";")[0].strip().lower() if value else None

    @property
    def declared_content_length(self) -> int | None:
        value = self.headers.get("Content-Length")
        try:
            return int(value) if value is not None else None
        except ValueError:
            return None

    @property
    def retry_after(self) -> str | None:
        return self.headers.get("Retry-After")

    @property
    def complete(self) -> bool:
        return self.transfer_outcome == COMPLETE

    def decoded_body(self) -> bytes:
        """A decoded *copy* for parsing. The stored object stays untouched.

        Decoding failure is a transport-integrity failure: a body that claims an
        encoding it does not honour cannot be shown to be complete.
        """
        encoding = (self.content_encoding or "identity").lower().strip()
        if encoding in ("identity", ""):
            return self.body
        try:
            if encoding == "gzip":
                return gzip.decompress(self.body)
            if encoding == "deflate":
                try:
                    return zlib.decompress(self.body)
                except zlib.error:
                    return zlib.decompress(self.body, -zlib.MAX_WBITS)
        except (OSError, zlib.error, EOFError) as exc:
            raise SecTransportError(f"content_decode_failed:{encoding}:{type(exc).__name__}",
                                    TRUNCATED, partial=self.body) from exc
        raise SecTransportError(f"unsupported_content_encoding:{encoding}", TRANSPORT_ERROR)

    def transport_metadata(self) -> dict[str, Any]:
        return {"http_status": self.status,
                "content_encoding": self.content_encoding,
                "declared_content_length": self.declared_content_length,
                "byte_length": self.byte_length,
                "media_type": self.media_type,
                "transfer_outcome": self.transfer_outcome,
                "transfer_encoding": self.headers.get("Transfer-Encoding")}


class SecHttpTransport:
    """Keep-alive HTTPS client for ``www.sec.gov``.

    Substituted wholesale in tests: every offline test drives the collector
    through a fake transport with the same ``fetch`` contract, so no test needs
    the network and the production path has no test-only branch.
    """

    def __init__(self, policy: SecAccessPolicy, timebase: Timebase | None = None,
                 host: str = SEC_HOST, context: ssl.SSLContext | None = None):
        self.policy = policy
        self.timebase = timebase or Timebase()
        self.host = host
        self.context = context or ssl.create_default_context()
        self._connection: http.client.HTTPSConnection | None = None
        self.connections_opened = 0
        self.requests_sent = 0

    # --- connection reuse --------------------------------------------------
    def _connect(self) -> http.client.HTTPSConnection:
        if self._connection is None:
            self._connection = http.client.HTTPSConnection(
                self.host, timeout=self.policy.connect_timeout_seconds, context=self.context)
            self.connections_opened += 1
        return self._connection

    def close(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except OSError:
                pass
            self._connection = None

    def fetch(self, path: str) -> SecHttpResponse:
        """Issue one GET. The caller has already spent a limiter slot."""
        try:
            return self._fetch_once(path)
        except SecTransportError:
            # A broken connection is never reused: the next request would fail
            # for a reason unrelated to the next request.
            self.close()
            raise

    def _fetch_once(self, path: str) -> SecHttpResponse:
        connection = self._connect()
        headers = dict(self.policy.headers())
        headers["Connection"] = "keep-alive"
        headers.setdefault("Accept", "*/*")
        started = self.timebase.now()
        try:
            connection.request("GET", path, headers=headers)
            response = connection.getresponse()
        except (http.client.HTTPException, socket.timeout, TimeoutError, ssl.SSLError,
                OSError) as exc:
            self.close()
            # One retry on a fresh connection covers the ordinary case of a
            # keep-alive socket the far end closed while the lane was idle.
            if self.requests_sent == 0:
                raise SecTransportError(f"request_failed:{type(exc).__name__}") from exc
            try:
                connection = self._connect()
                connection.request("GET", path, headers=headers)
                response = connection.getresponse()
            except (http.client.HTTPException, socket.timeout, TimeoutError, ssl.SSLError,
                    OSError) as retry_exc:
                raise SecTransportError(
                    f"request_failed:{type(retry_exc).__name__}") from retry_exc
        self.requests_sent += 1
        preserved = {name: value for name in PRESERVED_HEADERS
                     if (value := response.getheader(name)) is not None}
        body, outcome = self._read_body(response, started)
        if outcome != COMPLETE and response.status == 200:
            # A nominally successful status with an unprovable body is evidence
            # of an incomplete transfer, never a capture.
            return SecHttpResponse(status=response.status, reason=response.reason or "",
                                   body=body, headers=preserved, transfer_outcome=outcome)
        declared = preserved.get("Content-Length")
        if outcome == COMPLETE and declared is not None:
            try:
                if len(body) != int(declared):
                    outcome = TRUNCATED
            except ValueError:
                outcome = TRUNCATED
        return SecHttpResponse(status=response.status, reason=response.reason or "",
                               body=body, headers=preserved, transfer_outcome=outcome)

    def _read_body(self, response: http.client.HTTPResponse,
                   started: Any) -> tuple[bytes, str]:
        chunks: list[bytes] = []
        total = 0
        deadline = self.policy.total_deadline_seconds
        while True:
            if (self.timebase.now() - started).total_seconds() > deadline:
                return b"".join(chunks), DEADLINE_EXCEEDED
            try:
                chunk = response.read(65536)
            except http.client.IncompleteRead as exc:
                chunks.append(exc.partial)
                return b"".join(chunks), TRUNCATED
            except (socket.timeout, TimeoutError) as exc:
                raise SecTransportError(f"read_timeout:{type(exc).__name__}",
                                        DEADLINE_EXCEEDED, b"".join(chunks)) from exc
            except (http.client.HTTPException, ssl.SSLError, OSError):
                # Bytes already read are partial evidence, not a capture.
                return b"".join(chunks), TRUNCATED if chunks else TRANSPORT_ERROR
            if not chunk:
                return b"".join(chunks), COMPLETE
            chunks.append(chunk)
            total += len(chunk)
            if total > self.policy.max_response_bytes:
                return b"".join(chunks), OVERSIZED
