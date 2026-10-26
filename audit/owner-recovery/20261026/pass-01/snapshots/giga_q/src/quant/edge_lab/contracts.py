"""Admission and receipt checks for the existing laboratory; no market calculations."""
from .store import Refused

VERDICT_FIELDS = ("RESULT", "EFFECT_SIZE", "UNCERTAINTY", "POWER_LIMITATION",
    "ECONOMIC_SIGNIFICANCE", "FAILED_CRITERIA", "LESSON", "FAMILY_STATUS", "NEXT_DECISION")
GATES = ("data", "rights", "timing", "costs", "risk", "resources", "software")
DECISIONS = {"NEGATIVE": {"REJECTED", "CLOSED"},
    "POSITIVE_EXPLORATORY": {"QUALIFIED", "CLOSED"},
    "INSUFFICIENT_POWER": {"INSUFFICIENT_POWER", "WAIT", "CLOSED"},
    "INVALID_SOFTWARE": {"INVALID_SOFTWARE", "WAIT", "CLOSED"},
    "SOURCE_UNUSABLE": {"WAIT", "CLOSED"},
    "PROSPECTIVE_OBSERVATION": {"WAIT", "CLOSED"}}


def admission(packet, protocol, state, control):
    if protocol["rights"].get("permitted") is not True:
        raise Refused("BLOCKED_PERMISSION: frozen rights do not authorize this input")
    if packet.get("protocol_hash") != protocol["hash"] or not packet.get("data_fingerprint"):
        raise Refused("Admission must bind the frozen protocol and exact input version")
    if packet.get("runner_sha256") != protocol["runner_sha256"] or packet.get("paid_usd") != 0:
        raise Refused("Admission cannot replace code or authorize paid access")
    for gate in GATES:
        proof = packet.get(gate, {})
        ids = proof.get("evidence_ids", [])
        if (proof.get("qualified") is not True or not proof.get("scope") or not ids
                or any(i not in state["evidence"] for i in ids)):
            raise Refused("ADMISSION_BLOCKED: " + gate)
    software = packet["software"]
    if any(software.get(k) is not True for k in ("reviewed", "synthetic_tests_passed", "challenge_passed")):
        raise Refused("Pinned code needs review, synthetic tests and challenge before a look")
    resources = packet["resources"]
    if resources.get("bound_type") != "FULL_PROTOCOL_UPPER_BOUND":
        raise Refused("A partial benchmark is not a full-protocol resource bound")
    wall = resources.get("wall_seconds_upper_bound")
    if type(wall) not in (int, float) or not 0 < wall <= control["limits"]["job_wall_seconds"]:
        raise Refused("Complete-window runtime exceeds or lacks the configured bound")
    for key in ("memory_bytes_upper_bound", "disk_bytes_upper_bound"):
        if type(resources.get(key)) is not int or resources[key] <= 0:
            raise Refused("Unmeasured full-protocol resource bound: " + key)
    if not resources.get("input_bound_evidence"):
        raise Refused("Full input bounds need explicit provenance")


def outcome(result, protocol, look):
    if result.get("look_id") != look["id"]:
        raise Refused("Outcome belongs to a different look")
    kind = result.get("kind")
    if kind == "SOFTWARE_CHECK":
        if protocol.get("purpose") != "SYNTHETIC_SOFTWARE_QA":
            raise Refused("A market protocol cannot hide a result as a software check")
        return
    if kind not in DECISIONS:
        raise Refused("Unknown outcome; no automatic proven-alpha label")
    for key in ("nature", "benchmark", "observations", "uncertainty", "risk_exposures", "capacity",
                "lesson", "next_decision", "protocol_hash", "data_fingerprint"):
        if key not in result or result[key] is None:
            raise Refused("Missing economic receipt field: " + key)
    if "net_after_costs" not in result:
        raise Refused("Net costs must be stated even when not estimable")
    if result["protocol_hash"] != protocol["hash"] or result["data_fingerprint"] != look["data_fingerprint"]:
        raise Refused("Outcome is not bound to its frozen protocol/data")
    if result["nature"] not in ("EXPLORATORY_BACKTEST", "PROSPECTIVE_OBSERVATION", "SOFTWARE_FAILURE", "SOURCE_FAILURE"):
        raise Refused("Unsupported claim of alpha or live authority")
    expected_nature = {"NEGATIVE": "EXPLORATORY_BACKTEST", "POSITIVE_EXPLORATORY": "EXPLORATORY_BACKTEST",
        "INSUFFICIENT_POWER": "EXPLORATORY_BACKTEST", "INVALID_SOFTWARE": "SOFTWARE_FAILURE",
        "SOURCE_UNUSABLE": "SOURCE_FAILURE", "PROSPECTIVE_OBSERVATION": "PROSPECTIVE_OBSERVATION"}
    if result["nature"] != expected_nature[kind]:
        raise Refused("Outcome disposition must agree with its nature")
    if result.get("primary") != protocol["primary"]:
        raise Refused("Declared primary cannot be replaced by a winning comparator")
    expressions = result.get("expression_results", {})
    if (set(expressions) != set(protocol["expressions"]) or any(
            set(paths) != set(protocol["cost_paths"]) for paths in expressions.values())):
        raise Refused("Every frozen expression/cost path must be preserved")
    verdict = result.get("verdict", {})
    if any(k not in verdict or verdict[k] is None for k in VERDICT_FIELDS):
        raise Refused("All nine verdict fields are required")
