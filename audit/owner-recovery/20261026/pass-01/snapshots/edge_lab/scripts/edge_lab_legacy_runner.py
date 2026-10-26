#!/usr/bin/env python3
"""Dual-reserved exact upstream runner. No alternate parameters or retry option."""
import argparse
import contextlib
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quant.edge_lab.legacy_adapter import (CAPTURE, OUTPUT, PROTOCOL, bundle, check_inputs,
                                         original_authority, translate)
from quant.edge_lab.store import Store, Refused, strict_json, digest
from quant.edge_lab.remote import GitAuthority


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--look", required=True)
    args = parser.parse_args()
    store = Store(ROOT / "research/edge_lab")
    if store.control()["paused"]:
        raise Refused("PAUSED before legacy access")
    state = store.read()
    protocol, look = state["protocols"][args.protocol], state["looks"][args.look]
    if args.protocol != PROTOCOL or look["status"] != "RUNNING_SPENT" or args.look != "look:" + PROTOCOL:
        raise Refused("Durable lab RUNNING and exact original protocol required")
    authority = GitAuthority(ROOT, store.root).snapshot()
    if authority["control"].get("paused") is True:
        raise Refused("PAUSED remote authority before original source access")
    if (authority["state"]["looks"].get(args.look) != look
            or authority["state"]["protocols"].get(args.protocol) != protocol
            or authority["state"].get("admissions", {}).get(args.protocol) != state["admissions"][args.protocol]
            or any(authority["runner_versions"].get(p) != sha for p, sha in protocol["code_sha256"].items())):
        raise Refused("Original wrapper requires the exact published RUNNING/code/admission, not a local flag")
    check_inputs(protocol, state["admissions"][args.protocol], original_authority())
    freeze, manifest, values = bundle(ROOT)
    # The upstream runner retains its own original-ref check, attempt marker,
    # code/TZ revalidation, fixed output/capture paths and write-once result.
    # Its economic source bytes are copied unchanged, never patched/imported early.
    with tempfile.TemporaryDirectory(prefix="edge-lab-exact-legacy-") as temp:
        directory = Path(temp)
        for name, value in values.items():
            (directory / name).write_bytes(value)
        sys.path.insert(0, str(directory))
        spec = importlib.util.spec_from_file_location("edge_lab_exact_eurusd_run", directory / "run.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.verify_freeze(directory, freeze)
        capture_manifest = json.loads(values["manifest.json"])
        if capture_manifest != manifest:
            raise Refused("Pinned manifest identity")
        original_stdout = store.root / "receipts" / digest(args.look) / "original-stdout.bin"
        with original_stdout.open("x") as stream, contextlib.redirect_stdout(stream):
            sys.argv = [str(directory / "run.py")]
            module.main()
        result_path = OUTPUT / "result.json"
        raw = result_path.read_bytes()
        saved = store.root / "receipts" / digest(args.look) / "original-result.json"
        with saved.open("xb") as stream:
            stream.write(raw)
        result = strict_json(saved)
        module.validate_result(result, json.loads(values["result_schema.json"]))
        sha = hashlib.sha256(raw).hexdigest()
        attempt = strict_json(OUTPUT / "attempt.json")
        if not attempt.get("result_written") or attempt.get("result_sha256") != sha:
            raise Refused("Original saved result/attempt mismatch; never recalculate")
        print(json.dumps(translate(result, sha, protocol, look), allow_nan=False))


if __name__ == "__main__":
    main()
