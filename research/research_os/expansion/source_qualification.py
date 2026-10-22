from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, Iterable, List

from research.research_os.scientific_store import sha256_json


ALLOWED_SOURCE_CLASSES = {
    "PRIMARY_PUBLIC",
    "OFFICIAL_API",
    "EXCHANGE_PUBLIC",
    "REGULATORY_FILING",
    "AUTHORIZED_INTERNAL",
    "SYNTHETIC_FIXTURE",
}
ALLOWED_PIT_MODES = {"EVENT_TIME", "PUBLICATION_TIME", "VERSIONED_SNAPSHOT"}
ALLOWED_PERMISSION_STATES = {"PUBLIC", "AUTHORIZED_INTERNAL", "FIXTURE_ONLY"}

PRODUCER_TEST_READINESS_FIELDS = {
    "mechanism",
    "universe",
    "clock",
    "expression_requirements",
    "data_requirements",
    "cost_capacity_requirements",
    "falsification",
}
PRODUCER_READINESS_STATES = {"SUPPORTED", "PARTIAL", "REQUIRED", "UNKNOWN"}
UNKNOWN_ONLY_CLAIMS = {
    "payer",
    "quantity_mechanism",
    "directional_mechanism",
    "novelty",
    "consensus",
    "surprise",
    "market_response",
    "empirical_return",
    "capacity_estimate",
    "mispricing",
    "valuation_edge",
    "earnings_forecast",
    "rerating_alpha",
}
UNKNOWN_VALUES = {"UNKNOWN", "UNAVAILABLE", "NOT_OBSERVED", "NOT_ESTIMATED"}


def _parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("explicit availability/freeze clock required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("availability/freeze clock requires an explicit timezone")
    return parsed.astimezone(timezone.utc)


def _walk_mapping(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk_mapping(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_mapping(item)


def qualify_producer_test_readiness(readiness: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a producer-side pre-outcome economic-test specification.

    The contract deliberately accepts UNKNOWN/REQUIRED fields. It qualifies whether
    the producer has stated the exact remaining work without promoting documentary
    facts into an economic result. New producer claims must carry an explicit legacy
    screen; existing bound candidates may declare that the gate applies only to any
    future claim extension.
    """
    blockers: List[str] = []
    required = PRODUCER_TEST_READINESS_FIELDS | {
        "engine_family",
        "legacy_screen",
        "unsupported_economic_claims",
        "outcome_accessed",
        "economic_result",
    }
    missing = sorted(required - readiness.keys())
    blockers.extend(f"MISSING_{field.upper()}" for field in missing)

    if readiness.get("outcome_accessed") is not False:
        blockers.append("OUTCOME_ACCESS_NOT_ALLOWED")
    if readiness.get("economic_result") != "NOT_OBSERVED":
        blockers.append("ECONOMIC_RESULT_NOT_ALLOWED")

    legacy = readiness.get("legacy_screen")
    if not isinstance(legacy, dict):
        blockers.append("LEGACY_SCREEN_MISSING")
    else:
        state = legacy.get("status")
        if state not in {"PASS", "REQUIRED_BEFORE_NEW_CLAIM", "NOT_APPLICABLE_EXISTING_BOUND_CANDIDATE"}:
            blockers.append("LEGACY_SCREEN_STATE_INVALID")
        if legacy.get("new_claim") is True and state != "PASS":
            blockers.append("LEGACY_SCREEN_REQUIRED_BEFORE_NEW_PRODUCER_CLAIM")

    for field in sorted(PRODUCER_TEST_READINESS_FIELDS):
        record = readiness.get(field)
        if not isinstance(record, dict):
            blockers.append(f"{field.upper()}_RECORD_INVALID")
            continue
        status = record.get("status")
        if status not in PRODUCER_READINESS_STATES:
            blockers.append(f"{field.upper()}_STATUS_INVALID")
        if status in {"SUPPORTED", "PARTIAL"} and not record.get("support"):
            blockers.append(f"{field.upper()}_SUPPORT_MISSING")
        if status == "UNKNOWN" and record.get("support"):
            blockers.append(f"{field.upper()}_UNKNOWN_WITH_SUPPORT")
        if "value" not in record:
            blockers.append(f"{field.upper()}_VALUE_MISSING")

    unsupported = readiness.get("unsupported_economic_claims")
    if not isinstance(unsupported, dict):
        blockers.append("UNSUPPORTED_ECONOMIC_CLAIMS_INVALID")
    else:
        for field in UNKNOWN_ONLY_CLAIMS:
            if field in unsupported and (not isinstance(unsupported[field], str)
                                         or unsupported[field] not in UNKNOWN_VALUES):
                blockers.append(f"UNSUPPORTED_{field.upper()}_PROMOTED")

    # Defense in depth: these keys may appear nested in readiness records, but they
    # still cannot be populated from an announcement or rule packet alone.
    for key, value in _walk_mapping(readiness):
        if key in UNKNOWN_ONLY_CLAIMS and (not isinstance(value, str) or value not in UNKNOWN_VALUES):
            blockers.append(f"UNSUPPORTED_{key.upper()}_PROMOTED")

    canonical = deepcopy(readiness)
    canonical.pop("readiness_hash", None)
    return {
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "readiness_hash": sha256_json(canonical),
        "field_statuses": {
            field: readiness.get(field, {}).get("status", "MISSING")
            if isinstance(readiness.get(field), dict) else "MISSING"
            for field in sorted(PRODUCER_TEST_READINESS_FIELDS)
        },
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
    }


def build_producer_test_readiness(
    output: Dict[str, Any],
    dossier_detail: Dict[str, Any],
    *,
    legacy_screen: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Project an existing producer candidate into a bounded economic-test spec.

    This is intentionally non-mutating and outcome-free. It does not make a blocked
    dossier pass; it exposes which documentary facts are usable and which exact
    expression/data/cost-capacity inputs remain required before an authorized test.
    """
    family = output.get("engine_family")
    if family not in {"INSTITUTIONAL_FLOW", "EVENT_DOCUMENT", "QUANT_MECHANISM", "FUNDAMENTAL"}:
        raise ValueError("producer test-readiness requires a supported native engine family")
    candidate = output.get("candidate")
    if not isinstance(candidate, dict):
        raise ValueError("candidate required")
    if output.get("outcome_accessed") not in (None, False):
        raise ValueError("outcome-bearing producer output not allowed")
    if output.get("economic_result") not in (None, "NOT_OBSERVED"):
        raise ValueError("economic result not allowed")

    def rec(status: str, value: Any, support: List[str] | None = None) -> Dict[str, Any]:
        return {"status": status, "value": deepcopy(value), "support": list(support or [])}

    common = {
        "engine_family": family,
        "mechanism": rec("SUPPORTED", candidate.get("mechanism"), ["candidate.mechanism"]),
        "falsification": rec(
            "SUPPORTED",
            candidate.get("falsification_scope"),
            ["candidate.falsification_scope"],
        ),
        "legacy_screen": deepcopy(legacy_screen) if legacy_screen is not None else {
            "status": "NOT_APPLICABLE_EXISTING_BOUND_CANDIDATE",
            "new_claim": False,
            "future_claim_extension": "LEGACY_SCREEN_REQUIRED_BEFORE_NEW_CLAIM",
        },
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
    }

    if family == "INSTITUTIONAL_FLOW":
        actor = dossier_detail.get("forced_actor", {})
        rule = dossier_detail.get("constraint_rule", {})
        clock = dossier_detail.get("implementation_clock", {})
        universe = dossier_detail.get("affected_universe", {})
        common.update({
            "universe": rec(
                "PARTIAL" if universe.get("status") in {"PARTIAL", "SUPPORTED"} else "UNKNOWN",
                deepcopy(universe.get("values") or {"eligible_scope": "UNKNOWN"}),
                ["dossier.affected_universe"] if universe.get("status") in {"PARTIAL", "SUPPORTED"} else [],
            ),
            "clock": rec(
                "PARTIAL" if clock.get("status") in {"PARTIAL", "SUPPORTED"} else "UNKNOWN",
                deepcopy(clock.get("values") or {"economic_clock": "UNKNOWN"}),
                ["dossier.implementation_clock"] if clock.get("status") in {"PARTIAL", "SUPPORTED"} else [],
            ),
            "expression_requirements": rec("REQUIRED", [
                "eligible security/transaction identifier bound to the rule scope",
                "economically justified direction; do not derive direction from T+1 alone",
                "entry/exit clock and executable instrument",
            ]),
            "data_requirements": rec("REQUIRED", [
                "point-in-time transaction/security eligibility evidence",
                "binding/constrained actor evidence beyond the rule text",
                "quantity/funding-pressure evidence if a flow-magnitude claim is proposed",
                "current-rule/exemption check at protocol freeze",
            ]),
            "cost_capacity_requirements": rec("REQUIRED", [
                "fees/spread/slippage and financing/borrow where applicable",
                "eligible quantity and participation/capacity bound",
                "market-impact assumptions declared before outcome access",
            ]),
            "unsupported_economic_claims": {
                "payer": "UNKNOWN",
                "quantity_mechanism": "UNKNOWN",
                "directional_mechanism": "UNKNOWN",
                "empirical_return": "NOT_OBSERVED",
                "capacity_estimate": "NOT_ESTIMATED",
            },
            "documentary_support": {
                "actor": deepcopy(actor),
                "rule": deepcopy(rule),
            },
        })
    elif family == "EVENT_DOCUMENT":
        identity = dossier_detail.get("event_identity", {})
        clock = dossier_detail.get("document_clock", {})
        eligibility = dossier_detail.get("eligibility_rule", {})
        common.update({
            "universe": rec(
                "PARTIAL" if identity.get("status") in {"PARTIAL", "SUPPORTED"} else "UNKNOWN",
                {
                    "event_identity": deepcopy(identity.get("values") or {}),
                    "holder_record_ex_date_eligibility": deepcopy(eligibility.get("values") or "UNKNOWN"),
                },
                ["dossier.event_identity"] if identity.get("status") in {"PARTIAL", "SUPPORTED"} else [],
            ),
            "clock": rec(
                "PARTIAL" if clock.get("status") in {"PARTIAL", "SUPPORTED"} else "UNKNOWN",
                {
                    "information_availability": deepcopy(clock.get("values") or "UNKNOWN"),
                    "tradable_event_clock": "UNKNOWN" if eligibility.get("status") != "SUPPORTED" else deepcopy(eligibility.get("values")),
                },
                ["dossier.document_clock"] if clock.get("status") in {"PARTIAL", "SUPPORTED"} else [],
            ),
            "expression_requirements": rec("REQUIRED", [
                "security identifier and executable venue/instrument",
                "record/ex-date or other holder eligibility when the expression depends on entitlement",
                "predeclared entry/exit clock; announcement capture time is not a trading horizon",
            ]),
            "data_requirements": rec("REQUIRED", [
                "point-in-time event availability",
                "official holder/record/ex-date data when eligibility matters",
                "point-in-time consensus only if a surprise thesis is proposed",
                "concurrent-news/confounder controls declared before outcome access",
            ]),
            "cost_capacity_requirements": rec("REQUIRED", [
                "fees/spread/slippage and borrow/financing where applicable",
                "liquidity/participation limit and capacity declaration",
            ]),
            "unsupported_economic_claims": {
                "novelty": "UNKNOWN",
                "consensus": "UNKNOWN",
                "surprise": "UNKNOWN",
                "market_response": "NOT_OBSERVED",
                "empirical_return": "NOT_OBSERVED",
                "capacity_estimate": "NOT_ESTIMATED",
            },
            "documentary_support": {
                "event_identity": deepcopy(identity),
                "eligibility": deepcopy(eligibility),
            },
        })
    elif family == "FUNDAMENTAL":
        issuer = dossier_detail.get("issuer_identity", {})
        supported_issuer = issuer.get("status") in {"PARTIAL", "SUPPORTED"}
        common.update({
            "universe": rec(
                "PARTIAL" if supported_issuer else "UNKNOWN",
                {"issuer_identity": deepcopy(issuer.get("values") or "UNKNOWN"),
                 "security_eligibility": "UNKNOWN"},
                ["dossier.issuer_identity"] if supported_issuer else [],
            ),
            # An accounting period or capture timestamp is not an executable
            # research clock. The frozen protocol must declare that separately.
            "clock": rec("UNKNOWN", "UNKNOWN"),
            "expression_requirements": rec("REQUIRED", [
                "issuer-to-security mapping and executable instrument",
                "predeclared entry/exit clock and falsifiable valuation or fundamental thesis",
                "benchmark and economic expression distinct from accounting quality",
            ]),
            "data_requirements": rec("REQUIRED", [
                "point-in-time financial statements and immutable revision history",
                "point-in-time estimates only for a declared expectations thesis",
                "declared valuation inputs and benchmark for any mispricing thesis",
                "predeclared catalyst or falsification conditions",
                "security mapping, corporate actions and survivorship controls",
            ]),
            "cost_capacity_requirements": rec("REQUIRED", [
                "fees/spread/slippage and borrow/financing where applicable",
                "liquidity/participation limit and capacity declaration",
            ]),
            "unsupported_economic_claims": {
                "mispricing": "UNKNOWN", "valuation_edge": "UNKNOWN",
                "earnings_forecast": "UNKNOWN", "rerating_alpha": "UNKNOWN",
                "empirical_return": "NOT_OBSERVED", "capacity_estimate": "NOT_ESTIMATED",
            },
            "documentary_support": {field: deepcopy(dossier_detail.get(field, {})) for field in (
                "issuer_identity", "financial_statements", "cash_flow_quality", "valuation_frame",
                "earnings_and_guidance", "estimate_revisions", "catalysts",
            )},
        })
    else:
        universe = dossier_detail.get("universe_definition", {})
        expression = dossier_detail.get("expression", {})
        common.update({
            "universe": rec(
                "SUPPORTED" if universe.get("status") == "SUPPORTED" else "PARTIAL"
                if universe.get("status") == "PARTIAL" else "UNKNOWN",
                deepcopy(universe.get("values") or "UNKNOWN"),
                ["dossier.universe_definition"] if universe.get("status") in {"PARTIAL", "SUPPORTED"} else [],
            ),
            "clock": rec("UNKNOWN", "UNKNOWN"),
            "expression_requirements": rec(
                "PARTIAL" if expression.get("status") in {"PARTIAL", "SUPPORTED"} else "REQUIRED",
                deepcopy(expression.get("values") or ["executable expression", "entry/exit clock"]),
                ["dossier.expression"] if expression.get("status") in {"PARTIAL", "SUPPORTED"} else [],
            ),
            "data_requirements": rec("REQUIRED", [
                "point-in-time mechanism inputs",
                "universe membership and clock semantics",
                "reproducible source snapshots",
            ]),
            "cost_capacity_requirements": rec("REQUIRED", [
                "cost model declaration",
                "capacity declaration",
            ]),
            "unsupported_economic_claims": {
                "empirical_return": "NOT_OBSERVED",
                "capacity_estimate": "NOT_ESTIMATED",
            },
        })

    qualification = qualify_producer_test_readiness(common)
    return {
        "readiness_version": "producer-test-readiness.v1",
        "hypothesis_id": candidate.get("hypothesis_id"),
        "specification": common,
        "qualification": qualification,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
    }


def _qualified_route_text(value: Any) -> bool:
    return (isinstance(value, str) and bool(value.strip()) and value.strip().upper() not in {
        "UNKNOWN", "UNAVAILABLE", "UNRESOLVED", "CONFLICTED", "BLOCKED", "UNEXECUTED",
        "INVALIDATED_PROTOCOL", "NONE", "NULL", "N/A",
    })


def qualify_source_route(route: Dict[str, Any], *, freeze_time: str) -> Dict[str, Any]:
    blockers: List[str] = []
    required = {
        "route_id",
        "source_class",
        "transport",
        "locator",
        "permission_state",
        "pit_mode",
        "revision_policy",
        "survivorship_policy",
        "timezone",
        "availability_start",
        "contains_outcome",
    }
    missing = sorted(required - route.keys())
    blockers.extend(f"MISSING_{field.upper()}" for field in missing)

    if route.get("source_class") not in ALLOWED_SOURCE_CLASSES:
        blockers.append("SOURCE_CLASS_NOT_ALLOWED")
    if route.get("pit_mode") not in ALLOWED_PIT_MODES:
        blockers.append("PIT_MODE_NOT_ALLOWED")
    if route.get("permission_state") not in ALLOWED_PERMISSION_STATES:
        blockers.append("PERMISSION_NOT_QUALIFIED")
    for field in ("route_id", "transport"):
        if not _qualified_route_text(route.get(field)):
            blockers.append(field.upper() + "_INVALID")
    if not _qualified_route_text(route.get("locator")):
        blockers.append("LOCATOR_MISSING")
    if route.get("contains_outcome") is not False:
        blockers.append("UNAUTHORIZED_OUTCOME_BEARING_ROUTE")
    if not _qualified_route_text(route.get("revision_policy")):
        blockers.append("REVISION_POLICY_UNKNOWN")
    if not _qualified_route_text(route.get("survivorship_policy")):
        blockers.append("SURVIVORSHIP_POLICY_UNKNOWN")
    if not _qualified_route_text(route.get("timezone")):
        blockers.append("TIMEZONE_UNKNOWN")

    availability_start = route.get("availability_start")
    try:
        if _parse_utc(availability_start) > _parse_utc(freeze_time):
            blockers.append("ROUTE_NOT_AVAILABLE_AT_FREEZE")
    except ValueError:
        blockers.append("AVAILABILITY_CLOCK_INVALID")

    canonical = {
        "route_id": route.get("route_id"),
        "source_class": route.get("source_class"),
        "transport": route.get("transport"),
        "locator": route.get("locator"),
        "permission_state": route.get("permission_state"),
        "pit_mode": route.get("pit_mode"),
        "event_time_field": route.get("event_time_field"),
        "publication_time_field": route.get("publication_time_field"),
        "revision_policy": route.get("revision_policy"),
        "survivorship_policy": route.get("survivorship_policy"),
        "timezone": route.get("timezone"),
        "availability_start": route.get("availability_start"),
        "contains_outcome": route.get("contains_outcome"),
        "content_scope": route.get("content_scope", "DESIGN_METADATA_ONLY"),
    }
    return {
        "route_id": route.get("route_id"),
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "route_hash": sha256_json(canonical),
        "freeze_time": freeze_time,
        "point_in_time_qualified": not any(
            blocker in blockers
            for blocker in (
                "PIT_MODE_NOT_ALLOWED",
                "REVISION_POLICY_UNKNOWN",
                "SURVIVORSHIP_POLICY_UNKNOWN",
                "TIMEZONE_UNKNOWN",
                "ROUTE_NOT_AVAILABLE_AT_FREEZE",
                "AVAILABILITY_CLOCK_INVALID",
            )
        ),
        "outcome_accessed": False,
        "canonical_route": canonical,
    }


class ImmutableSourceRouteRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()

    def register(self, qualification: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            try:
                expected = qualify_source_route(qualification["canonical_route"],
                                                freeze_time=qualification["freeze_time"])
                route_id = qualification["route_id"]
            except (KeyError, TypeError, AttributeError) as exc:
                raise ValueError("source qualification malformed") from exc
            if not _qualified_route_text(route_id) or qualification != expected:
                raise ValueError("source qualification binding mismatch")
            current = self._entries.get(route_id)
            if current is not None:
                if current != qualification:
                    raise ValueError(f"immutable source qualification mutation rejected: {route_id}")
                return deepcopy(current)
            self._entries[route_id] = deepcopy(qualification)
            return deepcopy(qualification)

    def register_many(self, qualifications: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.register(item) for item in qualifications]

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            entries = [deepcopy(self._entries[key]) for key in sorted(self._entries)]
            return {
                "registry_id": "source-route-registry.v1",
                "entry_count": len(entries),
                "entries": entries,
                "immutable": True,
                "outcome_routes_authorized": False,
            }
