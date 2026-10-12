#!/usr/bin/env python3
"""Refresh derived LIVE.json from durable repo facts without changing research authority.

This is observability only. It never creates/claims/completes an experiment.  It
bridges the small gap between durable Discovery claim receipts and the canonical
Discovery STATE so the Site can show work that has actually been attested.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMINAL = {
    "KILL_EXPRESSION", "KILL_MECHANISM", "PARK_DATA", "PARK_ECONOMICS",
    "PROMOTE_EXPRESSION", "PROMOTE_MECHANISM", "PROMOTE_HIGH", "INCONCLUSIVE",
    "KILL", "PROMOTE",
}


def _json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _iso(value: str | None):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _head():
    explicit = os.environ.get("EDGE_LAB_SOURCE_HEAD") or os.environ.get("GITHUB_SHA")
    if explicit:
        return explicit
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def _unresolved_claim(discovery_dir: Path, now: datetime):
    claims_dir = discovery_dir / "claims"
    state_path = discovery_dir / "STATE.json"
    experiments = discovery_dir / "experiments"
    cards = {}
    if state_path.exists():
        try:
            cards = {c.get("id"): c for c in _json(state_path).get("queue", []) if isinstance(c, dict)}
        except Exception:
            cards = {}
    candidates = []
    if not claims_dir.exists():
        return None
    for path in claims_dir.glob("*.json"):
        try:
            claim = _json(path)
        except Exception:
            continue
        identity = claim.get("experiment_id")
        if not identity:
            continue
        card = cards.get(identity) or {}
        if card.get("status") in TERMINAL or (experiments / f"{identity}.result.json").exists():
            continue
        # A canonical RUNNING card already carries richer lease semantics; no overlay needed.
        if card.get("status") == "RUNNING":
            continue
        claimed = _iso(claim.get("claimed_at_utc") or claim.get("claimed_at"))
        if claimed is None:
            continue
        candidates.append((claimed, path.name, claim))
    if not candidates:
        return None
    claimed, filename, claim = max(candidates, key=lambda item: (item[0], item[1]))
    age_seconds = max(0.0, (now - claimed).total_seconds())
    # External/manual claims have no canonical lease in STATE. 90 minutes is display-only:
    # fresh => CLAIMED/WORKING; older => RECOVERY_REQUIRED. It does not authorize execution.
    display_status = "CLAIMED" if age_seconds < 5400 else "RECOVERY_REQUIRED"
    return claim | {
        "_claim_file": filename,
        "_claimed_at": claimed.isoformat(),
        "_age_seconds": age_seconds,
        "_display_status": display_status,
    }


def refresh(state_dir: Path):
    live_path = state_dir / "LIVE.json"
    if not live_path.exists():
        raise SystemExit("LIVE.json missing; run scripts/edge_lab.py render first")
    live = _json(live_path)
    now = datetime.now(timezone.utc)
    source_head = _head()
    claim = _unresolved_claim(state_dir / "discovery", now)

    overlay = "NONE"
    if claim is not None:
        overlay = "UNRESOLVED_DURABLE_DISCOVERY_CLAIM"
        status = claim["_display_status"]
        identity = claim["experiment_id"]
        invocation = claim.get("invocation_id")
        active = {
            "id": identity,
            "status": status,
            "claim_id": invocation,
            "question": "Discovery V4.2 — claim économique publié avant lecture des outcomes",
            "next": "Exécuter une seule fois le contrat pré-déclaré, puis publier le verdict typé.",
            "claimed_at": claim["_claimed_at"],
            "source_scope": claim.get("source_scope"),
            "authority": "durable-claim-receipt",
        }
        live["active_task"] = active
        live["next_action"] = active["next"]
        live["operational_status"] = "WORKING" if status == "CLAIMED" else "RECOVERY_REQUIRED"
        discovery = live.setdefault("discovery", {})
        discovery["status"] = live["operational_status"]
        discovery["active_lease"] = active
        discovery["active_external_claim"] = active
        groups = discovery.setdefault("groups", {})
        running = groups.setdefault("running", [])
        recovery = groups.setdefault("recovery", [])
        target = running if status == "CLAIMED" else recovery
        other = recovery if status == "CLAIMED" else running
        other[:] = [item for item in other if item.get("id") != identity]
        if not any(item.get("id") == identity for item in target):
            target.insert(0, active)
        counts = discovery.setdefault("counts", {})
        counts["running"] = len(running)
        counts["recovery"] = len(recovery)
        discovery["telemetry_overlay"] = overlay

    live["generated_at"] = now.isoformat()
    live["telemetry"] = {
        "source_head": source_head,
        "generated_at": live["generated_at"],
        "overlay": overlay,
        "generator": "scripts/edge_lab_live.py",
        "authority": "DERIVED_DISPLAY_ONLY",
    }
    live_path.write_text(json.dumps(live, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return live


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", default=str(ROOT / "research/edge_lab"))
    args = parser.parse_args()
    value = refresh(Path(args.state_dir))
    print(json.dumps({
        "generated_at": value.get("generated_at"),
        "operational_status": value.get("operational_status"),
        "source_head": value.get("telemetry", {}).get("source_head"),
        "overlay": value.get("telemetry", {}).get("overlay"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
