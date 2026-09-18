#!/usr/bin/env python3
"""Demonstrate SEC/Form-4 P0 capture and restart without exposing filing content."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.clock import QuantSystem
from quant.dataplane.sec_form4 import HttpResponse, SecCollectorConfig
from quant.status.brief import build_chief_brief
from quant.status.render import render_status

ACCESSION = "0000000001-26-000001"
INDEX_URL = ("https://www.sec.gov/Archives/edgar/data/1/000000000126000001/"
             f"{ACCESSION}-index.htm")
SYNTHETIC_FEED = (f'<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
                  f'<link href="{INDEX_URL}" /></entry></feed>').encode()
SYNTHETIC_RAW = b"synthetic SEC fixture: exact bytes only\r\n\x00\xff"


class SyntheticTransport:
    def __init__(self):
        self.calls = 0

    def fetch(self, url, headers, timeout):
        self.calls += 1
        if self.calls == 1:
            return HttpResponse(200, SYNTHETIC_FEED,
                                {"content-type": "application/atom+xml",
                                 "content-length": str(len(SYNTHETIC_FEED))})
        if self.calls == 2:
            return HttpResponse(200, SYNTHETIC_RAW,
                                {"content-type": "text/plain",
                                 "content-length": str(len(SYNTHETIC_RAW))})
        raise AssertionError("synthetic proof made an unexpected request")


def safe_proof(system: QuantSystem, outcome: str, before_history: str,
               after_history: str, raw_reload_verified: bool) -> dict:
    capture = system.snapshot()["data"]["sec_form4_capture"]
    policy = capture["policy"]
    digest = capture["last_raw_object_sha256"]
    layout = None
    if digest:
        hexdigest = digest.split(":", 1)[1]
        layout = f"var/sec_form4/raw/sha256/{hexdigest[:2]}/{hexdigest}.bin"
    return {
        "proof_kind": "SEC_FORM4_P0_RAW_CAPTURE",
        "git_commit": system.sec_capture.config.git_commit,
        "clock_outcome": outcome,
        "collector_state": capture["state"],
        "last_poll_result": capture["last_poll_result"],
        "last_attempt_at_utc": capture["last_attempt_at_utc"],
        "last_receipt_at_utc": capture["last_receipt_at_utc"],
        "last_http_status": capture["last_http_status"],
        "last_endpoint_class": capture["last_endpoint_class"],
        "last_raw_object_sha256": digest,
        "last_byte_length": capture["last_byte_length"],
        "storage_health": capture["storage_health"],
        "next_poll_at_utc": capture["next_poll_at_utc"],
        "blocked_until_utc": capture["blocked_until_utc"],
        "raw_store_layout": layout,
        "access_policy": {
            "poll_seconds": policy["poll_seconds"],
            "request_rate_per_second": policy["request_rate_per_second"],
            "max_concurrency": policy["max_concurrency"],
            "backoff_seconds": policy["backoff_seconds"],
            "policy_reviewed_date": policy["policy_reviewed_date"],
        },
        "visibility": capture["visibility"],
        "restart": {
            "attempt_history_digest_before": before_history,
            "attempt_history_digest_after": after_history,
            "history_preserved": before_history == after_history,
            "raw_reload_verified": raw_reload_verified,
        },
    }


def run(root: Path, live: bool) -> dict:
    first = QuantSystem(root)
    if not live:
        first.sec_capture.config = SecCollectorConfig(
            True, "Quant Synthetic Proof", "synthetic@example.com", "synthetic-proof",
            timeout_seconds=1, max_documents_per_poll=1)
        first.sec_capture.transport = SyntheticTransport()
        first.sec_capture.jitter = lambda _: 0.0
    first.boot()
    outcome = first.tick()
    before = first.sec_capture.store.attempt_history_digest()
    digest = first.sec_capture.state.last_raw_object_sha256

    resumed = QuantSystem(root)
    if not live:
        resumed.sec_capture.config = replace(first.sec_capture.config)
    resumed.boot()
    after = resumed.sec_capture.store.attempt_history_digest()
    raw_reload_verified = False
    if digest:
        raw = resumed.sec_capture.store.read_raw(digest)
        raw_reload_verified = ("sha256:" + hashlib.sha256(raw).hexdigest()) == digest

    snapshot = resumed.snapshot()
    render_status(snapshot, resumed.paths.status_surface)
    build_chief_brief(snapshot, root / "CHIEF_BRIEF.live.md")
    return safe_proof(resumed, outcome, before, after, raw_reload_verified)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--proof-out", type=Path)
    args = parser.parse_args()
    if args.root:
        root = args.root.resolve()
        proof = run(root, args.live)
    else:
        if args.live:
            parser.error("--live requires --root")
        with tempfile.TemporaryDirectory() as directory:
            proof = run(Path(directory), False)
    text = json.dumps(proof, indent=2, sort_keys=True) + "\n"
    if args.proof_out:
        args.proof_out.parent.mkdir(parents=True, exist_ok=True)
        args.proof_out.write_text(text, encoding="utf-8")
    print(text, end="")
    if proof["collector_state"] == "BLOCKED":
        return 2
    if not proof["restart"]["history_preserved"] or not proof["restart"]["raw_reload_verified"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
