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

**One request per permit.** ``P0_ACQUISITION_CRITICAL_FINGERPRINT_V1.md`` §6
requires

    ONE_BUDGET_RESERVATION == ONE_NETWORK_REQUEST_ATTEMPT == ONE_AUDITABLE_ATTEMPT_ID

so this module may never decide by itself to send a second request. An earlier
version retried once on a fresh connection after a connection-level failure,
which could put two SEC requests under one limiter reservation and one attempt
id. That retry is gone, and its absence is now structural rather than a matter
of reading the code: ``fetch`` requires a :class:`RequestPermit` that the
collector mints from a budget reservation, and a permit is consumed by the
first ``request()`` that goes out. A second send under the same permit raises.

That understates nothing to the SEC either: a limiter counting reservations
while the transport could emit more requests than reservations misstates real
traffic, which is the failure that risks throttling and an irreversible gap.

A *reconnect* is still allowed, because it changes no semantics and emits no
extra request. Since a keep-alive socket the far end closed while the lane was
idle is the ordinary cause of the failure the old retry papered over, the
connection is now closed **before** it goes stale: a connection older than
``idle_reuse_seconds`` is replaced during permit issue, not after a failure.
"""

from __future__ import annotations

import gzip
import http.client
import socket
import ssl
import time
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
class RequestPermit:
    """Authority to emit exactly one HTTP request.

    Minted by the collector from one traffic-budget reservation and carrying the
    attempt id that will journal the result, so the permit is the object that
    makes reservation, request and audit record one-to-one. It is single use:
    ``consume`` succeeds once and raises afterwards.
    """

    attempt_id: str
    reserved_at_utc: str
    endpoint_class: str
    spent: bool = False

    def consume(self) -> None:
        if self.spent:
            raise PermitAlreadySpent(
                f"attempt {self.attempt_id} already emitted its single permitted request")
        self.spent = True


class PermitAlreadySpent(RuntimeError):
    """A second HTTP request was attempted under one reservation/attempt id.

    This is a capture-integrity fault, not a retryable error: it would mean the
    real SEC traffic exceeded what the budget and the attempt journal record.
    """


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

    def decoded_body(self, max_decoded_bytes: int | None = None) -> bytes:
        """A bounded decoded copy for parsing. Stored bytes remain untouched."""
        return decode_body(self.body, self.content_encoding,
                           max_decoded_bytes=max_decoded_bytes)

    def transport_metadata(self) -> dict[str, Any]:
        return {"http_status": self.status,
                "content_encoding": self.content_encoding,
                "declared_content_length": self.declared_content_length,
                "byte_length": self.byte_length,
                "media_type": self.media_type,
                "transfer_outcome": self.transfer_outcome,
                "transfer_encoding": self.headers.get("Transfer-Encoding")}


def decode_body(body: bytes, content_encoding: str | None,
                *, max_decoded_bytes: int | None = None) -> bytes:
    """Decode a parsing copy with an explicit expansion bound."""
    limit = max_decoded_bytes if max_decoded_bytes is not None else 64 * 1024 * 1024
    if limit <= 0:
        raise SecTransportError("decoded_body_limit_invalid", OVERSIZED, partial=body)
    encoding = (content_encoding or "identity").lower().strip()
    if encoding in ("identity", ""):
        if len(body) > limit:
            raise SecTransportError("decoded_body_oversized", OVERSIZED, partial=body)
        return body
    try:
        wbits = zlib.MAX_WBITS | 16 if encoding == "gzip" else zlib.MAX_WBITS
        if encoding not in ("gzip", "deflate"):
            raise SecTransportError(f"unsupported_content_encoding:{encoding}",
                                    TRANSPORT_ERROR)
        decoder = zlib.decompressobj(wbits)
        decoded = decoder.decompress(body, limit + 1)
        if len(decoded) > limit or decoder.unconsumed_tail:
            raise SecTransportError("decoded_body_oversized", OVERSIZED, partial=body)
        decoded += decoder.flush(limit + 1 - len(decoded))
        if len(decoded) > limit:
            raise SecTransportError("decoded_body_oversized", OVERSIZED, partial=body)
        if not decoder.eof:
            # Raw-deflate fallback is permitted only for deflate.
            if encoding == "deflate":
                decoder = zlib.decompressobj(-zlib.MAX_WBITS)
                decoded = decoder.decompress(body, limit + 1)
                decoded += decoder.flush(max(0, limit + 1 - len(decoded)))
                if len(decoded) <= limit and decoder.eof:
                    return decoded
            raise SecTransportError(f"content_decode_failed:{encoding}:IncompleteStream",
                                    TRUNCATED, partial=body)
        return decoded
    except SecTransportError:
        raise
    except (OSError, zlib.error, EOFError) as exc:
        raise SecTransportError(f"content_decode_failed:{encoding}:{type(exc).__name__}",
                                TRUNCATED, partial=body) from exc


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
        self._connection_last_used: Any = None
        self.connections_opened = 0
        #: Actual HTTP requests put on the wire. The audit compares this against
        #: budget reservations and durable attempt ids; they must be equal.
        self.requests_sent = 0

    # --- connection reuse --------------------------------------------------
    def _connect(self) -> http.client.HTTPSConnection:
        if self._connection is None:
            self._connection = http.client.HTTPSConnection(
                self.host,
                timeout=min(self.policy.connect_timeout_seconds,
                            self.policy.total_deadline_seconds),
                context=self.context)
            self.connections_opened += 1
        return self._connection

    def _recycle_if_idle(self) -> None:
        """Drop a connection old enough that the far end has likely closed it.

        This replaces the removed retry. Reconnecting before sending costs no
        request and changes no semantics; reconnecting *after* a failure would
        have meant a second request under the first one's reservation.
        """
        if self._connection is None or self._connection_last_used is None:
            return
        idle = (self.timebase.now() - self._connection_last_used).total_seconds()
        if idle >= self.policy.idle_reuse_seconds:
            self.close()

    def close(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except OSError:
                pass
            self._connection = None
            self._connection_last_used = None

    def fetch(self, path: str, permit: RequestPermit) -> SecHttpResponse:
        """Issue exactly one GET against the permit the collector minted.

        There is no retry here, by design. A failure returns to the collector,
        which records the attempt, applies the frozen backoff and schedules the
        next try as its own reservation, attempt id and scheduler transition.
        """
        try:
            return self._fetch_once(path, permit)
        except SecTransportError:
            # A broken connection is never reused: the next request would fail
            # for a reason unrelated to the next request.
            self.close()
            raise

    def _fetch_once(self, path: str, permit: RequestPermit) -> SecHttpResponse:
        self._recycle_if_idle()
        connection = self._connect()
        headers = dict(self.policy.headers())
        headers["Connection"] = "keep-alive"
        headers.setdefault("Accept", "*/*")
        started = self.timebase.now()
        deadline = time.monotonic() + self.policy.total_deadline_seconds
        # The permit is spent at the moment the request goes out, so a failure
        # after this point can never be re-sent under the same attempt id.
        permit.consume()
        self.requests_sent += 1
        try:
            connection.request("GET", path, headers=headers)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("total deadline exceeded before response headers")
            if connection.sock is not None:
                connection.sock.settimeout(min(self.policy.read_timeout_seconds, remaining))
            response = connection.getresponse()
        except (http.client.HTTPException, socket.timeout, TimeoutError, ssl.SSLError,
                OSError) as exc:
            self.close()
            raise SecTransportError(f"request_failed:{type(exc).__name__}") from exc
        self._connection_last_used = self.timebase.now()
        preserved = {name: value for name in PRESERVED_HEADERS
                     if (value := response.getheader(name)) is not None}
        body, outcome = self._read_body(response, deadline, connection)
        if outcome != COMPLETE:
            # An unread/truncated body must never contaminate the next keep-alive response.
            self.close()
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

    def _read_body(self, response: http.client.HTTPResponse, deadline: float,
                   connection: http.client.HTTPSConnection) -> tuple[bytes, str]:
        chunks: list[bytes] = []
        total = 0
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return b"".join(chunks), DEADLINE_EXCEEDED
            sock = connection.sock
            if sock is None:
                try:
                    sock = response.fp.raw._sock
                except AttributeError:
                    sock = None
            if sock is not None:
                sock.settimeout(min(self.policy.read_timeout_seconds, remaining))
            try:
                # read1 performs at most one underlying socket read, so the total
                # deadline is re-applied between chunks rather than after a large
                # blocking read returns.
                chunk = response.read1(65536)
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
