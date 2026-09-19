"""Frozen SEC fair-access policy for the P0 Form-4 capture lane.

``NEXT_BUILD_MISSION.md`` requires that the authoritative SEC documentation be
re-checked before the first live request and that the consulted source and date
be recorded rather than inherited from a stale project assumption. The result of
that check is the ``SEC_POLICY_SOURCES`` table below; it is data, so a test can
assert the implementation never exceeds what the source actually permits.

The implemented policy is deliberately far below the SEC ceiling. The ceiling is
what the SEC tolerates; the policy is what Quant asks for.

One further rule is structural rather than numeric: the limiter is a **global
SEC traffic budget**. It is keyed on a file, not on a collector instance, so a
second SEC consumer added later cannot collectively exceed the frozen rate.
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass, field
from typing import Any


#: Authoritative SEC documentation consulted before the first live request of
#: this mission. ``consulted_at_utc`` is the local date of the re-check;
#: ``reviewed_or_updated`` is the revision date the SEC page itself publishes.
SEC_POLICY_SOURCES: tuple[dict[str, Any], ...] = (
    {
        "url": "https://www.sec.gov/os/webmaster-faq",
        "title": "SEC.gov | Webmaster Frequently Asked Questions",
        "reviewed_or_updated": "2024-08-23",
        "consulted_at_utc": "2026-09-18",
        "quoted_max_request_rate": "Our current maximum access rate is 10 requests per second.",
        "quoted_identity_requirement": "Please declare your user agent in request headers",
        "quoted_monitoring": "This is carefully monitored to preserve equitable access for all users.",
    },
    {
        "url": "https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data",
        "title": "Accessing EDGAR Data",
        "reviewed_or_updated": "2024-06-26",
        "consulted_at_utc": "2026-09-18",
        "quoted_max_request_rate": "Current max request rate: 10 requests/second.",
        "quoted_identity_requirement": (
            "Please declare your user agent in request headers "
            "[format: Sample Company Name AdminContact@<sample company domain>.com]"),
        "quoted_moderation": (
            "Download only what you need and please moderate requests to minimize server load."),
        "quoted_enforcement": (
            "The SEC does not allow botnets or automated tools to crawl the site. Any request "
            "that has been identified as part of a botnet or an automated tool outside of the "
            "acceptable policy will be managed to ensure fair access for all users."),
    },
)

#: The rate the sources above state the SEC currently tolerates. Never the
#: rate Quant uses; it exists so a test can prove the policy stays under it.
SEC_DOCUMENTED_MAX_REQUESTS_PER_SECOND = 10.0

#: Environment variable carrying the declared requester identity and contact.
USER_AGENT_ENV = "QUANT_SEC_USER_AGENT"

#: A declared identity must carry a contact address, because that is what the
#: SEC guidance asks for. A bare product string is not compliant.
_CONTACT_PATTERN = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")

#: Endpoint classes this lane is allowed to touch. Recorded on every attempt so
#: a reviewer can see which SEC surface was used without seeing which filing.
DISCOVERY_ENDPOINT_CLASS = "edgar_browse_getcurrent_atom"
FILING_ENDPOINT_CLASS = "edgar_archives_submission_text"
DOCUMENTATION_ENDPOINT_CLASS = "sec_documentation"


class SecPolicyNotConfigured(RuntimeError):
    """The declared SEC identity is absent. The lane fails closed, never open."""


@dataclass(frozen=True)
class SecAccessPolicy:
    """Everything the collector is permitted to do to SEC infrastructure."""

    user_agent: str
    #: Seconds between discovery polls while the collector is enabled.
    discovery_poll_seconds: float = 60.0
    #: Global concurrent SEC requests, across every consumer.
    max_concurrency: int = 1
    #: Steady-state cap across every SEC endpoint used by any consumer.
    max_requests_per_second: float = 2.0
    #: Strict spacing: no burst credit accumulates while the lane is idle.
    allow_burst: bool = False
    connect_timeout_seconds: float = 10.0
    read_timeout_seconds: float = 20.0
    #: A kept-alive connection idle longer than this is replaced *before* the
    #: next request rather than retried after it fails. This is the permitted
    #: reconnect that replaced the removed hidden HTTP retry, so it is
    #: acquisition-critical: it changes when a reconnect happens, never how many
    #: requests are emitted.
    idle_reuse_seconds: float = 20.0
    #: Whole-request deadline, so a trickling response cannot stall liveness.
    total_deadline_seconds: float = 60.0
    #: Bounded exponential backoff with jitter, per NEXT_BUILD_MISSION.md.
    backoff_schedule_seconds: tuple[float, ...] = (5.0, 15.0, 60.0, 300.0, 900.0)
    jitter_ratio: float = 0.25
    #: HTTP 429 / explicit rate control, when no Retry-After is supplied.
    rate_limit_cooldown_seconds: float = 300.0
    #: HTTP 403 consistent with automated-access control: long cooldown, no loop.
    forbidden_cooldown_seconds: float = 3600.0
    #: Discovery page size. The endpoint caps ``count`` at 100.
    discovery_page_size: int = 40
    #: Pages one poll may walk. Exceeding it is COVERAGE_UNKNOWN, not success.
    max_discovery_pages_per_poll: int = 10
    #: Filing acquisitions drained per tick. Backlog never drains faster.
    filings_per_drain: int = 1
    #: Accepted response encodings. Exact received bytes are hashed either way.
    accept_encoding: str = "gzip, deflate, identity"
    max_response_bytes: int = 32 * 1024 * 1024
    sources: tuple[dict[str, Any], ...] = field(default=SEC_POLICY_SOURCES)

    def __post_init__(self) -> None:
        if not self.user_agent or not self.user_agent.strip():
            raise SecPolicyNotConfigured(
                f"{USER_AGENT_ENV} is empty; SEC guidance requires a declared user agent")
        if not _CONTACT_PATTERN.search(self.user_agent):
            raise SecPolicyNotConfigured(
                f"{USER_AGENT_ENV} must carry a contact email address, as SEC guidance requires")
        if self.max_requests_per_second > SEC_DOCUMENTED_MAX_REQUESTS_PER_SECOND:
            raise SecPolicyNotConfigured(
                "configured request rate exceeds the documented SEC maximum")
        numeric = (
            self.discovery_poll_seconds, self.max_requests_per_second,
            self.connect_timeout_seconds, self.read_timeout_seconds,
            self.idle_reuse_seconds, self.total_deadline_seconds,
            self.rate_limit_cooldown_seconds, self.forbidden_cooldown_seconds,
            self.max_response_bytes, self.max_discovery_pages_per_poll,
            self.filings_per_drain, *self.backoff_schedule_seconds,
        )
        if any(not math.isfinite(float(value)) or float(value) <= 0 for value in numeric):
            raise SecPolicyNotConfigured("acquisition policy values must be finite and positive")
        if self.max_concurrency != 1:
            raise SecPolicyNotConfigured("this limiter implements exactly one global SEC request")
        if self.allow_burst:
            raise SecPolicyNotConfigured("burst credit is not implemented and cannot be enabled")
        if not self.backoff_schedule_seconds or not 0 <= self.jitter_ratio <= 1:
            raise SecPolicyNotConfigured("invalid backoff/jitter policy")
        if "\r" in self.user_agent or "\n" in self.user_agent:
            raise SecPolicyNotConfigured("user agent contains HTTP header control characters")
        if self.connect_timeout_seconds > self.total_deadline_seconds:
            raise SecPolicyNotConfigured("connect timeout exceeds whole-request deadline")
        if self.read_timeout_seconds > self.total_deadline_seconds:
            raise SecPolicyNotConfigured("read timeout exceeds whole-request deadline")
        if self.discovery_page_size < 1 or self.discovery_page_size > 100:
            raise SecPolicyNotConfigured("discovery page size must be between 1 and 100")

    @property
    def min_request_interval_seconds(self) -> float:
        return 1.0 / self.max_requests_per_second

    def headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent,
                "Accept-Encoding": self.accept_encoding,
                "Host": "www.sec.gov"}

    def backoff_seconds(self, step: int) -> float:
        """Bounded schedule. Past the last step the cooldown stops growing."""
        index = min(max(step, 0), len(self.backoff_schedule_seconds) - 1)
        return self.backoff_schedule_seconds[index]

    def to_dict(self) -> dict[str, Any]:
        """Firewall-safe description of the request controls in force."""
        return {
            "discovery_poll_seconds": self.discovery_poll_seconds,
            "max_concurrency": self.max_concurrency,
            "max_requests_per_second": self.max_requests_per_second,
            "allow_burst": self.allow_burst,
            "documented_sec_max_requests_per_second": SEC_DOCUMENTED_MAX_REQUESTS_PER_SECOND,
            "connect_timeout_seconds": self.connect_timeout_seconds,
            "read_timeout_seconds": self.read_timeout_seconds,
            "total_deadline_seconds": self.total_deadline_seconds,
            "idle_reuse_seconds": self.idle_reuse_seconds,
            "backoff_schedule_seconds": list(self.backoff_schedule_seconds),
            "jitter_ratio": self.jitter_ratio,
            "rate_limit_cooldown_seconds": self.rate_limit_cooldown_seconds,
            "forbidden_cooldown_seconds": self.forbidden_cooldown_seconds,
            "discovery_page_size": self.discovery_page_size,
            "max_discovery_pages_per_poll": self.max_discovery_pages_per_poll,
            "user_agent_declared": True,
            "policy_sources": [{"url": source["url"],
                                "reviewed_or_updated": source["reviewed_or_updated"],
                                "consulted_at_utc": source["consulted_at_utc"]}
                               for source in self.sources],
        }


def policy_from_environment(environ: dict[str, str] | None = None,
                            **overrides: Any) -> SecAccessPolicy:
    """Build the policy, failing closed when the declared identity is absent.

    There is no default User-Agent on purpose. A shared placeholder would make
    every Quant deployment indistinguishable to the SEC, which is the opposite
    of what the fair-access guidance asks for.
    """
    source = os.environ if environ is None else environ
    declared = (source.get(USER_AGENT_ENV) or "").strip()
    if not declared:
        raise SecPolicyNotConfigured(
            f"{USER_AGENT_ENV} is not set; SEC guidance requires a declared user agent "
            f"with a contact address before any automated request")
    return SecAccessPolicy(user_agent=declared, **overrides)


def is_configured(environ: dict[str, str] | None = None) -> bool:
    try:
        policy_from_environment(environ)
    except SecPolicyNotConfigured:
        return False
    return True
