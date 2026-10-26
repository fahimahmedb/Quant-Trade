"""Exact EURUSD adoption. No ref creation, downloads, parameter overrides or retry."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from .contracts import VERDICT_FIELDS, admission
from .legacy import FROZEN_COMMIT, FREEZE_SHA256, PREFIX
from .store import Refused, digest, event, strict_json

PROTOCOL = "EURUSD-RANGE-GRID-001-exploratory-01"
REF = "refs/heads/looks/eurusd-range-grid-001-exploratory-01"
CAPTURE = Path("/workspace/scratch/eurusd-range-grid-001/capture-v1")
OUTPUT = CAPTURE.parent / "result-exploratory-01"
RUNNER = "scripts/edge_lab_legacy_runner.py"
WRAPPER_FILES = (RUNNER, "src/quant/edge_lab/legacy_adapter.py", "src/quant/edge_lab/legacy.py",
                 "src/quant/edge_lab/contracts.py", "src/quant/edge_lab/store.py",
                 "src/quant/edge_lab/engine.py", "src/quant/edge_lab/remote.py", "src/quant/state.py")


def bundle(repository, ceiling=2097152):
    """Pinned code/manifest metadata only, with limits before each body read."""
    deadline = time.monotonic() + 30
    values = {}
    def read(name):
        nonlocal ceiling
        if Path(name).name != name:
            raise Refused("Legacy bundle path escaped")
        spec = FROZEN_COMMIT + ":" + PREFIX + name
        def git(*args):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise Refused("Legacy metadata deadline")
            r = subprocess.run(["git", "--no-pager", "-C", str(repository), *args],
                               capture_output=True, timeout=min(5, remaining), check=True)
            return r.stdout
        size = int(git("cat-file", "-s", spec))
        if not 0 <= size <= ceiling:
            raise Refused("Legacy metadata cap before body read")
        value = git("show", spec)
        if len(value) != size:
            raise Refused("Legacy metadata size changed")
        ceiling -= size
        values[name] = value
        return value
    freeze = json.loads(read("freeze.json"))
    if hashlib.sha256(values["freeze.json"]).hexdigest() != FREEZE_SHA256:
        raise Refused("Immutable EURUSD freeze mismatch")
    for name, sha in freeze["files"].items():
        if hashlib.sha256(read(name)).hexdigest() != sha:
            raise Refused("Immutable EURUSD bundle changed")
    if freeze["reservation_ref"] != REF or freeze["fixed_output"] != str(OUTPUT / "result.json"):
        raise Refused("Original reservation/output changed")
    return freeze, json.loads(values["manifest.json"]), values


def original_authority():
    url = "https://api.github.com/repos/fahimahmedb/Quant-Trade/git/ref/heads/looks/eurusd-range-grid-001-exploratory-01"
    request = urllib.request.Request(url, headers={"User-Agent": "quant-edge-lab-readonly/1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        raw = response.read(65537)
    if len(raw) > 65536:
        raise Refused("Original ref metadata ceiling")
    return json.loads(raw)


def check_original(claim, remote):
    if (claim.get("schema") != 1 or claim.get("ref") != REF
            or claim.get("atomic_create_receipt") is not True
            or claim.get("freeze_sha256") != FREEZE_SHA256
            or claim.get("frozen_commit") != FROZEN_COMMIT
            or remote.get("ref") != REF or remote.get("object", {}).get("sha") != FROZEN_COMMIT):
        raise Refused("Exact existing original reservation required; lab cannot create it")


def metadata(path, ceiling=2097152):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= ceiling:
        raise Refused("Absent, unbounded or linked legacy metadata")
    return strict_json(path)


def prior_attempt(output=OUTPUT):
    # Existence is enough to stop. Never open or recalculate prior outcomes here.
    output = Path(output)
    if any((output / name).exists() for name in ("attempt.json", "result.json", "warmup-state.json")) or list(output.glob("result*.tmp")):
        raise Refused("Original attempt/result/partial exists: reconcile exact receipt, never replay")


def never_executed(packet, state):
    proof = packet.get("original_execution", {})
    ids = proof.get("evidence_ids", [])
    if (proof.get("reservation_ref") != REF or proof.get("frozen_commit") != FROZEN_COMMIT
            or proof.get("reserved_look_never_executed") is not True
            or proof.get("no_printed_or_saved_outcome") is not True
            or set(proof.get("artifact_scopes_checked", [])) != {"local", "public_logs", "remote_artifacts"}
            or not ids or any(i not in state["evidence"] for i in ids)):
        raise Refused("Prior original look must be explicitly reconciled across stores; file absence is insufficient")
    return proof


def plan(lab, repository, packet):
    from .engine import budget_check
    state, control = lab.snapshot()
    budget_check(state, control)
    family = state["families"].get("eurusd-technical-grid", {})
    if family.get("status") == "REJECTED_CLOSED" or not family.get("sha"):
        raise Refused("Only the existing immutable EURUSD family can be adopted")
    freeze, manifest, _ = bundle(repository, control["limits"]["metadata_bytes_per_tick"])
    accounting = manifest["trial_accounting"]
    ids = packet.get("evidence_ids", [])
    if not ids or any(i not in state["evidence"] for i in ids):
        raise Refused("Exact adapter needs cached qualification evidence")
    rights = packet.get("rights", {})
    if rights.get("permitted") is not True or not rights.get("url") or not rights.get("scope"):
        raise Refused("Personal proxy rights must be explicitly qualified, never inferred")
    execution_proof = never_executed(packet, state)
    code = {p: hashlib.sha256((Path(repository) / p).read_bytes()).hexdigest() for p in WRAPPER_FILES}
    protocol = {"id": PROTOCOL, "family": "eurusd-technical-grid", "dataset": family["dataset"],
        "stage": "EXPLORATION", "window": manifest["utc_outcome"],
        "expressions": accounting["economic_expressions"], "cost_paths": accounting["cost_paths"],
        "primary": accounting["primary"], "mechanism": "Exact frozen EURUSD intraday finite RSI range grid",
        "payer": "Unverified liquidity demand / inventory reversion hypothesis; proxy only",
        "clock": "Unchanged frozen EST UTC-05 tick clock and causal past-only state",
        "independent_unit": "Frozen UTC days and baskets; private/exposure history UNKNOWN",
        "benchmark": "Frozen MAIN, NO_ADDS and STATIC_GRID; no replacement winner",
        "costs": "Unchanged CENTRAL/STRESS in pinned safety_kernel; assumptions, not broker-authenticated",
        "rights": rights, "decision_contract": {"positive": "Execution validation required; no surviving/live edge claim",
            "negative": "Archive this exact frozen rule", "inconclusive": "Preserve uncertainty; no substitute cell",
            "invalid": "Preserve source/software failure separately from economic rejection"},
        "multiplicity_policy": "Original one look, three expressions/six dependent paths; lab receipt aliases original reservation, not six additional independent trials; M/private UNKNOWN",
        "runner": RUNNER, "runner_sha256": code[RUNNER], "code_sha256": code, "evidence_ids": ids,
        "legacy": {"frozen_commit": FROZEN_COMMIT, "freeze_sha256": FREEZE_SHA256,
            "reservation_ref": REF, "capture_root": str(CAPTURE), "output": str(OUTPUT / "result.json"),
            "manifest_sha256": freeze["files"]["manifest.json"], "original_charge_alias": REF},
        "frozen_at": freeze["frozen_utc"]}
    protocol["legacy"]["prior_execution_proof"] = execution_proof
    protocol["hash"] = digest({k: v for k, v in protocol.items() if k != "frozen_at"})
    return protocol


def check_inputs(protocol, proof, remote, *, capture=CAPTURE, output=OUTPUT):
    """Admission metadata, no ZIP/price/hash-body before the charged look."""
    if protocol["id"] != PROTOCOL or protocol.get("legacy", {}).get("freeze_sha256") != FREEZE_SHA256:
        raise Refused("Wrong exact legacy adapter")
    prior_attempt(output)
    claim = metadata(Path(capture) / "reservation.json")
    check_original(claim, remote)
    certificate = metadata(Path(capture) / "capture.json")
    if (certificate.get("status") != "COMPLETE_NO_ROWS_OPENED" or certificate.get("price_rows_opened") != 0
            or certificate.get("manifest_sha256") != protocol["legacy"]["manifest_sha256"]
            or len(certificate.get("archives", [])) != 21
            or proof["data_fingerprint"] != hashlib.sha256((Path(capture) / "capture.json").read_bytes()).hexdigest()):
        raise Refused("Exact complete blind capture identity required")
    return claim


def adopt(lab, repository, packet, ref_reader=original_authority):
    from .engine import budget_check
    protocol = plan(lab, repository, packet)
    proof = packet.get("admission", {})
    with lab.store.lock():
        state, control = lab.store.read(), lab.store.control()
        budget_check(state, control)
        admission(proof, protocol, state, control)
        never_executed(packet, state)
        if protocol["id"] in state["protocols"] or "look:" + protocol["id"] in state["looks"]:
            raise Refused("Exact legacy protocol already adopted/spent; no recreation")
        check_inputs(protocol, proof, ref_reader())
        state["protocols"][protocol["id"]] = protocol
        state.setdefault("admissions", {})[protocol["id"]] = proof
        event(state, "EXACT_LEGACY_ADOPTED", {"protocol": protocol["id"], "hash": protocol["hash"],
                                            "original_charge_alias": REF, "admission_digest": digest(proof)})
        lab.store.save(state)
    return protocol["id"]


def translate(result, raw_sha, protocol, look):
    """Lossless path/verdict mapping only; never calculate another statistic."""
    tags = set(result["verdict"]["RESULT"].split(";"))
    allowed = {"SOURCE_GATE_FAILED", "PROXY_COST_REJECT_THIS_RULE", "PROXY_RISK_REJECT_THIS_RULE",
        "PROXY_INCONCLUSIVE", "PROXY_POSITIVE_NEEDS_EXECUTION_VALIDATION", "GRID_OR_ADAPTATION_INCREMENT_UNSUPPORTED"}
    if not tags or not tags <= allowed or set(result["verdict"]) != set(VERDICT_FIELDS):
        raise Refused("Unrecognized original verdict; preserve without automatic promotion")
    # Source failure outranks partial P&L; only MAIN determines promotion.
    if "SOURCE_GATE_FAILED" in tags:
        kind, nature = "SOURCE_UNUSABLE", "SOURCE_FAILURE"
    elif tags & {"PROXY_COST_REJECT_THIS_RULE", "PROXY_RISK_REJECT_THIS_RULE"}:
        kind, nature = "NEGATIVE", "EXPLORATORY_BACKTEST"
    elif "PROXY_POSITIVE_NEEDS_EXECUTION_VALIDATION" in tags:
        kind, nature = "POSITIVE_EXPLORATORY", "EXPLORATORY_BACKTEST"
    else:
        kind, nature = "INSUFFICIENT_POWER", "EXPLORATORY_BACKTEST"
    expected = {e + "_" + c for e in protocol["expressions"] for c in protocol["cost_paths"]}
    if set(result.get("paths", {})) != expected:
        raise Refused("All six exact frozen paths required")
    return {"look_id": look["id"], "kind": kind, "nature": nature,
        "protocol_hash": protocol["hash"], "data_fingerprint": look["data_fingerprint"],
        "primary": protocol["primary"], "benchmark": protocol["benchmark"],
        "observations": {"qa": result.get("qa"), "opportunities": result.get("opportunities")},
        "net_after_costs": {"location": "expression_results; exact original paths", "broker_execution_authenticated": False},
        "uncertainty": result["verdict"]["UNCERTAINTY"],
        "risk_exposures": result["verdict"]["ECONOMIC_SIGNIFICANCE"], "capacity": "UNVERIFIED_QUOTE_PROXY",
        "lesson": result["verdict"]["LESSON"], "next_decision": result["verdict"]["NEXT_DECISION"],
        "expression_results": {e: {c: result["paths"][e + "_" + c] for c in protocol["cost_paths"]} for e in protocol["expressions"]},
        "verdict": result["verdict"], "original_result": {"sha256": raw_sha, "path": str(OUTPUT / "result.json"),
            "freeze_sha256": FREEZE_SHA256, "integrity": result.get("integrity"),
            "other_fields": {k: v for k, v in result.items() if k not in ("paths", "verdict", "integrity")}}}
