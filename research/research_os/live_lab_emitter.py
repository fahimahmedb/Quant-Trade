"""Independent delivery of Oracle V2 Live Lab outbox events to the existing Site.

The bearer secret is read only from the process environment. It is never written
to GitHub, the outbox, receipts, stdout or stderr. Delivery failures leave events
pending and cannot modify Research OS authority or state.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .live_lab_bridge import DEFAULT_OUTBOX, LocalLiveLabOutbox

SITE_HOST = "quant-trade-lab.sassylime.chatgpt.site"
SESSION_PATH = "/api/oracle/session"
EVENT_PATH = "/api/oracle/event"
PRINCIPAL = "oracle-research-live"
DEFAULT_SITE_WORKER_PREFIX = "oracle-research."


class LiveLabDeliveryError(RuntimeError):
    pass


@dataclass(frozen=True)
class SiteConfig:
    base_url: str
    ingress_key: str = field(repr=False)
    principal: str = PRINCIPAL
    allowed_worker_prefix: str = DEFAULT_SITE_WORKER_PREFIX

    @classmethod
    def from_env(cls) -> "SiteConfig":
        base = os.environ.get("QT_ORACLE_SITE_BASE_URL", "").strip().rstrip("/")
        key = os.environ.get("QT_ORACLE_INGRESS_KEY", "")
        principal = os.environ.get("QT_ORACLE_PRINCIPAL", "").strip()
        prefix = os.environ.get("QT_ORACLE_SITE_WORKER_PREFIX", DEFAULT_SITE_WORKER_PREFIX).strip()
        if not base or not key or not principal or not prefix:
            raise LiveLabDeliveryError("LIVE_LAB_SITE_ENV_INCOMPLETE")
        parsed = urlparse(base)
        if parsed.scheme != "https" or parsed.hostname != SITE_HOST or parsed.path not in ("", "/"):
            raise LiveLabDeliveryError("LIVE_LAB_SITE_ORIGIN_NOT_PINNED")
        if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.port not in (None, 443):
            raise LiveLabDeliveryError("LIVE_LAB_SITE_ORIGIN_UNSAFE")
        if principal != PRINCIPAL:
            raise LiveLabDeliveryError("LIVE_LAB_PRINCIPAL_NOT_CANONICAL")
        if not prefix.startswith("oracle-research"):
            raise LiveLabDeliveryError("LIVE_LAB_WORKER_PREFIX_UNSAFE")
        return cls(base, key, principal, prefix)


class SiteClient:
    def __init__(self, config: SiteConfig, *, opener=urlopen, timeout: float = 15.0):
        self.config = config
        self.opener = opener
        self.timeout = timeout

    def _post(self, path: str, body: Mapping[str, Any]) -> dict[str, Any]:
        data = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        request = Request(
            self.config.base_url + path,
            data=data,
            method="POST",
            headers={
                "Authorization": "Bearer " + self.config.ingress_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Quant-Trade-Oracle-Live-Lab/1",
            },
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                status = getattr(response, "status", response.getcode())
                payload = response.read(1024 * 1024)
        except HTTPError as exc:
            raise LiveLabDeliveryError(f"LIVE_LAB_HTTP_{exc.code}") from None
        except (URLError, TimeoutError, OSError) as exc:
            raise LiveLabDeliveryError("LIVE_LAB_NETWORK_ERROR:" + type(exc).__name__) from None
        if not 200 <= int(status) < 300:
            raise LiveLabDeliveryError("LIVE_LAB_HTTP_STATUS_" + str(status))
        if not payload:
            return {"status": "ACCEPTED"}
        try:
            value = json.loads(payload)
        except json.JSONDecodeError:
            raise LiveLabDeliveryError("LIVE_LAB_RESPONSE_NOT_JSON") from None
        if not isinstance(value, dict):
            raise LiveLabDeliveryError("LIVE_LAB_RESPONSE_NOT_OBJECT")
        return value

    def _validate_worker(self, event: Mapping[str, Any]) -> None:
        worker_id = str(event.get("worker_id", ""))
        if not worker_id.startswith(self.config.allowed_worker_prefix):
            raise LiveLabDeliveryError(
                "LIVE_LAB_WORKER_PREFIX_MISMATCH:"
                + worker_id
                + ":expected="
                + self.config.allowed_worker_prefix
            )

    @staticmethod
    def session_payload(event: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "session_id": event["session_id"],
            "worker_id": event["worker_id"],
            "action_id": event["action_id"],
            "generation": event["generation"],
            "started_at": event["emitted_at"],
        }

    def ensure_session(self, event: Mapping[str, Any]) -> dict[str, Any]:
        self._validate_worker(event)
        return self._post(SESSION_PATH, self.session_payload(event))

    def deliver_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        self._validate_worker(event)
        return self._post(EVENT_PATH, event)


def deliver_pending(outbox: LocalLiveLabOutbox, client: SiteClient, *, limit: int = 100) -> dict[str, Any]:
    delivered = 0
    session_posts = 0
    remaining = outbox.pending()
    for path in remaining[:limit]:
        envelope = json.loads(path.read_text())
        if envelope.get("schema_version") != "oracle-live-lab-outbox-v1":
            raise LiveLabDeliveryError("LIVE_LAB_OUTBOX_SCHEMA_UNKNOWN")
        event = envelope.get("event")
        if not isinstance(event, dict):
            raise LiveLabDeliveryError("LIVE_LAB_OUTBOX_EVENT_INVALID")
        session_id = str(event["session_id"])
        if not outbox.session_marker(session_id).exists():
            client.ensure_session(event)
            outbox.mark_session(session_id)
            session_posts += 1
        client.deliver_event(event)
        outbox.mark_sent(path)
        delivered += 1
    return {
        "status": "PASS" if delivered else "NOOP",
        "delivered": delivered,
        "session_posts": session_posts,
        "pending": len(outbox.pending()),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outbox", default=str(DEFAULT_OUTBOX))
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args(argv)
    if args.interval < 0.5 or args.limit < 1 or args.limit > 1000:
        raise LiveLabDeliveryError("LIVE_LAB_EMITTER_BOUNDS_INVALID")

    config = SiteConfig.from_env()
    outbox = LocalLiveLabOutbox(Path(args.outbox))
    client = SiteClient(config)

    while True:
        result = deliver_pending(outbox, client, limit=args.limit)
        print(json.dumps(result, sort_keys=True))
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LiveLabDeliveryError as exc:
        print(json.dumps({"status": "RETRY", "reason": str(exc)}, sort_keys=True))
        raise SystemExit(75)
