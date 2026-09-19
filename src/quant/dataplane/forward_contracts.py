"""Non-P0 source inventory and the descriptive contract a source must satisfy.

The mission this module serves is explicit that a source is not chosen because
it produces attractive results: "Data capture peut etre priorisee par
irreversibility, future information value, breadth, capital applicability,
operational cost. Jamais par outcomes futurs." So this inventory records only
what is already true in the repository -- what is authorized, what is
reachable, what its point-in-time semantics and failure modes actually are --
and names every other candidate source's real, existing blocker instead of
inventing access to it.

Nothing here reads the P0 SEC/Form-4 reservoir or infers anything from its
counts, identities or rhythm. The P0 lane is out of scope by mission boundary,
not silently included as "just another source"; see ``SEC_FORM4_P0`` below,
which carries no coverage/frequency/field claims because none were read.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .ingest import BENCHMARK, CONTEXT, SECTOR_UNIVERSE

#: A source already authorized and used elsewhere in this repository, reachable
#: without new credentials, and safe to point a forward-capture adapter at.
SOURCE_AUTHORIZED = "AUTHORIZED_ALREADY_IN_REPOSITORY"
#: A static, operator-supplied historical export with no live update mechanism.
#: It is a legitimate dataset, but there is nothing forward-capture can do here:
#: there is no vendor endpoint to poll.
SOURCE_NOT_LIVE_CAPTURABLE = "NOT_LIVE_CAPTURABLE_STATIC_HISTORICAL_EXPORT"
#: A real candidate this project has already named (research/opportunity_map.json)
#: whose blocker is a new data provider, credential or licence this Builder
#: session has no authority to obtain. Left named-blocked rather than invented.
SOURCE_BLOCKED_NEW_PROVIDER = "BLOCKED_REQUIRES_NEW_PROVIDER_CREDENTIAL_OR_LICENCE"
#: Exists, is real, and is explicitly out of scope for this mission by boundary,
#: not by capability. No content, count, identity or rhythm from it was read to
#: produce this entry.
SOURCE_P0_EXCLUSIVE_OUT_OF_SCOPE = "BLOCKED_P0_EXCLUSIVE_OUT_OF_SCOPE"

ADMISSIBILITY_STATES = (SOURCE_AUTHORIZED, SOURCE_NOT_LIVE_CAPTURABLE,
                        SOURCE_BLOCKED_NEW_PROVIDER, SOURCE_P0_EXCLUSIVE_OUT_OF_SCOPE)


@dataclass(frozen=True)
class SourceProfile:
    """What is known about one candidate source, and why it is or is not usable.

    ``evidence`` names the exact repository artifact each claim is derived
    from, so this profile is falsifiable against the same repository a reviewer
    can read -- nothing here is a claim from memory or from the source vendor.
    """

    source_id: str
    admissibility: str
    coverage: str
    frequency: str
    fields: tuple[str, ...]
    pit_semantics: dict[str, Any]
    failure_modes: tuple[str, ...]
    restatement_behavior: str
    expected_calendar: str
    universe: tuple[str, ...]
    licence_note: str
    evidence: str
    blocker: str | None = None

    def __post_init__(self) -> None:
        if self.admissibility not in ADMISSIBILITY_STATES:
            raise ValueError(f"unrecognised admissibility state: {self.admissibility}")
        if self.admissibility != SOURCE_AUTHORIZED and not self.blocker:
            raise ValueError(f"{self.source_id}: a non-authorized source must name "
                             "its exact blocker, not just a category")

    @property
    def capturable_now(self) -> bool:
        return self.admissibility == SOURCE_AUTHORIZED

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


YAHOO_DAILY_CHART = SourceProfile(
    source_id="yahoo_daily_chart",
    admissibility=SOURCE_AUTHORIZED,
    coverage="US-listed equities/ETFs on the requested symbol list; consolidated "
             "daily bars only, not venue-level quotes",
    frequency="one bar per completed exchange session per symbol",
    fields=("open", "high", "low", "close", "adj_close", "volume"),
    pit_semantics={
        "information_available_at": "the close of the dated session",
        "minimum_decision_lag_days": 1,
        "timestamp_semantics": "bar timestamp is the session open; the bar is "
                               "only complete after that session's close",
    },
    # Exactly the exceptions `dataplane.adapters.fetch_yahoo_daily` raises
    # DataUnavailable for. HTTP-level failures (429 rate-limit, 403, 5xx) are
    # not distinguished by that adapter today: urllib surfaces them as
    # URLError/HTTPError, which the adapter already catches generically. This
    # profile does not claim finer granularity than the adapter code provides.
    failure_modes=("DNS_OR_NETWORK_FAILURE", "TIMEOUT", "HTTP_ERROR_INCLUDING_RATE_LIMIT",
                  "MALFORMED_JSON_RESPONSE", "SOURCE_REPORTED_ERROR_PAYLOAD",
                  "ADJUSTED_CLOSE_SERIES_ABSENT", "NO_COMPLETE_BARS_RETURNED"),
    restatement_behavior="adj_close is retroactively restated for dividends and "
                         "splits -- a later fetch of an old session can legitimately "
                         "disagree with what was captured; raw OHLCV for a closed "
                         "session is not expected to change, though the endpoint is "
                         "undocumented with no contractual guarantee against a "
                         "vendor-side correction",
    expected_calendar="no authoritative exchange holiday calendar ships with this "
                      "source or this repository; the already-validated "
                      "us_sector_etf_daily dataset's own aligned session list is "
                      "used as the current authoritative expected-session "
                      "declaration (see forward_coverage.seed_expected_sessions_"
                      "from_dataset) until an independent exchange calendar is "
                      "integrated",
    universe=tuple(SECTOR_UNIVERSE + [BENCHMARK] + CONTEXT),
    licence_note="public endpoint, personal research use; not redistributed as a "
                "data product -- identical to the existing us_sector_etf_daily "
                "licence note this repository already operates under",
    evidence="src/quant/dataplane/adapters.py:fetch_yahoo_daily (already used by "
            "src/quant/dataplane/ingest.py:ingest_sector_panel); reachability "
            "re-verified live in this session (HTTP 200 from "
            "query1.finance.yahoo.com)",
)

LOCAL_TSV_INDEX = SourceProfile(
    source_id="local_tsv_index",
    admissibility=SOURCE_NOT_LIVE_CAPTURABLE,
    coverage="NASDAQ composite historical export, one fixed file",
    frequency="none -- static, one-time operator-supplied export",
    fields=("open", "high", "low", "close", "adj_close", "volume"),
    pit_semantics={"information_available_at": "the close of the dated session",
                   "minimum_decision_lag_days": 1},
    failure_modes=("FILE_ABSENT", "FILE_CONTAINS_NO_ROWS"),
    restatement_behavior="none observed; the file has never been refreshed since "
                         "it was committed",
    expected_calendar="not applicable: there is no live feed to schedule against",
    universe=("NDXCOMP",),
    licence_note="operator-supplied export already committed to this repository",
    evidence="src/quant/dataplane/adapters.py:load_local_tsv, "
            "data/nasdaq_composite_daily.txt",
    blocker="there is no vendor endpoint behind this file to poll; forward "
           "capture has nothing to attempt going forward",
)

FACTOR_RESIDUAL_PANEL = SourceProfile(
    source_id="factor_residual_panel",
    admissibility=SOURCE_BLOCKED_NEW_PROVIDER,
    coverage="not available", frequency="not available", fields=(),
    pit_semantics={}, failure_modes=(), restatement_behavior="not available",
    expected_calendar="not available", universe=(),
    licence_note="not available",
    evidence="research/opportunity_map.json: factor_residual, constraint "
            "'no survivorship-controlled security and factor panel'",
    blocker="requires a survivorship-controlled security and factor panel from a "
           "new, currently unauthorized data provider; not fabricated here",
)

VOLATILITY_SURFACE_PANEL = SourceProfile(
    source_id="volatility_surface_panel",
    admissibility=SOURCE_BLOCKED_NEW_PROVIDER,
    coverage="not available", frequency="not available", fields=(),
    pit_semantics={}, failure_modes=(), restatement_behavior="not available",
    expected_calendar="not available", universe=(),
    licence_note="not available",
    evidence="research/opportunity_map.json: volatility_surface, constraint "
            "'historical option chains, quotes, rates, dividends, and corporate "
            "actions absent'",
    blocker="requires historical option chains/quotes/rates/dividends/corporate "
           "actions from a new, currently unauthorized data provider; not "
           "fabricated here",
)

SEC_FORM4_P0 = SourceProfile(
    source_id="sec_form4_p0",
    admissibility=SOURCE_P0_EXCLUSIVE_OUT_OF_SCOPE,
    coverage="not read", frequency="not read", fields=(),
    pit_semantics={}, failure_modes=(), restatement_behavior="not read",
    expected_calendar="not read", universe=(),
    licence_note="not read",
    evidence="NEXT_BUILD_MISSION.md; owned exclusively by "
            "astra/p0-deep-adversarial-pre-t0. This entry exists only to record "
            "that the lane was named and deliberately excluded, not omitted by "
            "oversight -- no file under src/quant/dataplane/sec/**, var/sec/** or "
            "handoff/SEC_FORM4_*.json was read to populate it.",
    blocker="out of scope by explicit mission boundary, not by capability or "
           "authorization",
)

#: Every candidate this Builder session is aware of, real ones only.
SOURCE_INVENTORY: tuple[SourceProfile, ...] = (
    YAHOO_DAILY_CHART, LOCAL_TSV_INDEX, FACTOR_RESIDUAL_PANEL,
    VOLATILITY_SURFACE_PANEL, SEC_FORM4_P0,
)


def admissible_for_forward_capture() -> tuple[SourceProfile, ...]:
    """Sources this mission may actually point a capture adapter at, right now."""
    return tuple(source for source in SOURCE_INVENTORY if source.capturable_now)


def inventory_as_dict() -> dict[str, Any]:
    return {source.source_id: source.to_dict() for source in SOURCE_INVENTORY}
