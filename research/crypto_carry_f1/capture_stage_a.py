"""Persist/recover the registered Stage A capture; never decompress or analyse.

python3 -I capture_stage_a.py OUT_DIR CANDIDATES_TXT CANDIDATES_SHA256
python3 -I capture_stage_a.py OUT_DIR CANDIDATES_TXT CANDIDATES_SHA256 --verify-only

The immutable plan is built from archive names before the first download. A
complete certificate requires every planned archive to match its public
checksum. The existing acquire_f1 transport remains sequential at <=5 req/s.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile
import time

_spec = importlib.util.spec_from_file_location("f1_capture_transport", Path(__file__).with_name("acquire_f1.py"))
transport = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(transport)

STAGE = "STAGE_A"
NAMES = {"funding": "{s}-fundingRate-{m}.zip", "perp1d": "{s}-1d-{m}.zip", "spot1d": "{s}-1d-{m}.zip"}


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(value, f, sort_keys=True, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def validate_plan(plan, symbols, candidate_sha):
    lo, hi = transport.WINDOWS[STAGE]
    if (plan.get("schema") != 1 or plan.get("stage") != STAGE
            or plan.get("window") != [lo, hi] or plan.get("candidates_sha256") != candidate_sha
            or plan.get("persistent_404_prefixes")):
        raise ValueError("capture plan identity/window/listing failure")
    seen = set()
    counts = {(ds, sym): 0 for sym in symbols for ds in NAMES}
    for ds, sym, key in plan["jobs"]:
        m = transport.month_of(key)
        if (ds not in NAMES or sym not in symbols or not m or not lo <= m <= hi
                or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", m)):
            raise ValueError("capture plan job outside registered universe/window")
        expected = transport.DATASETS[ds].format(s=sym) + NAMES[ds].format(s=sym, m=m)
        if key != expected or key in seen:
            raise ValueError("capture plan malformed or duplicate key")
        seen.add(key)
        counts[ds, sym] += 1
    if not seen:
        raise ValueError("empty capture plan")
    prefixes = {(p["dataset"], p["symbol"]): p["planned"] for p in plan["prefixes"]}
    if len(plan["prefixes"]) != len(counts) or prefixes != counts:
        raise ValueError("capture plan listing coverage/count mismatch")


def get_plan(out, symbols, candidate_sha):
    path = out / "plan_STAGE_A.json"
    if path.exists():
        plan = json.loads(path.read_bytes())
    else:
        lo, hi = transport.WINDOWS[STAGE]
        jobs, prefixes = [], []
        transport.LISTING_404.clear()
        for i, sym in enumerate(symbols, 1):
            for ds, pattern in transport.DATASETS.items():
                keys = transport.list_files(pattern.format(s=sym))
                selected = sorted(k for k in keys if transport.month_of(k) and lo <= transport.month_of(k) <= hi)
                prefixes.append({"dataset": ds, "symbol": sym, "planned": len(selected)})
                jobs.extend([ds, sym, k] for k in selected)
            if i % 25 == 0:
                print(f"names only: {i}/{len(symbols)} symbols listed", flush=True)
        plan = {"schema": 1, "stage": STAGE, "window": [lo, hi],
                "candidates_sha256": candidate_sha, "jobs": jobs, "prefixes": prefixes,
                "persistent_404_prefixes": list(transport.LISTING_404)}
        validate_plan(plan, symbols, candidate_sha)
        # Exclusive publication: never overwrite an earlier planned capture.
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", dir=out, delete=False) as f:
                tmp = f.name
                json.dump(plan, f, sort_keys=True, indent=1)
                f.flush()
                os.fsync(f.fileno())
            os.link(tmp, path)
        finally:
            if tmp:
                os.unlink(tmp)
    validate_plan(plan, symbols, candidate_sha)
    print(f"frozen plan sha256: {digest(path)}", flush=True)
    return plan


def read_manifest(path, repair_tail=False):
    """Only an interrupted final record may be repaired; interior corruption aborts."""
    if not path.exists():
        return []
    raw = path.read_bytes()
    lines = raw.splitlines(keepends=True)
    records, valid_bytes = [], 0
    for i, line in enumerate(lines):
        try:
            records.append(json.loads(line))
        except ValueError:
            if not (repair_tail and i == len(lines) - 1 and not line.endswith(b"\n")):
                raise ValueError("corrupt acquisition manifest")
            break
        valid_bytes += len(line)
    if repair_tail and raw and not raw.endswith(b"\n"):
        repaired = raw[:valid_bytes]
        if repaired and not repaired.endswith(b"\n"):
            repaired += b"\n"
        with open(path, "wb") as f:
            f.write(repaired)
            f.flush()
            os.fsync(f.fileno())
    return records


def verified_jobs(out, plan, records):
    jobs = {key: (ds, sym) for ds, sym, key in plan["jobs"]}
    successful = {}
    for rec in records:
        key = rec["key"]
        if key not in jobs or (rec["dataset"], rec["symbol"]) != jobs[key]:
            raise ValueError("manifest record outside frozen capture plan")
        if rec.get("ok"):
            sha = rec.get("sha256", "")
            if not re.fullmatch(r"[0-9a-f]{64}", sha) or sha != rec.get("checksum_sha256"):
                raise ValueError("manifest checksum authentication missing")
            successful[key] = rec
    verified, total_bytes = set(), 0
    for key, rec in successful.items():
        ds, sym = jobs[key]
        path = out / ds / sym / key.rsplit("/", 1)[-1]
        if path.is_file() and path.stat().st_size == rec["bytes"] and digest(path) == rec["sha256"]:
            verified.add(key)
            total_bytes += rec["bytes"]
    return verified, total_bytes


def certificate(out, plan, records):
    verified, nbytes = verified_jobs(out, plan, records)
    missing = sorted(key for _, _, key in plan["jobs"] if key not in verified)
    manifest = out / "manifest_STAGE_A.jsonl"
    report = {"stage": STAGE, "status": "COMPLETE" if not missing else "INCOMPLETE",
              "planned": len(plan["jobs"]), "verified": len(verified), "missing_keys": missing,
              "archive_bytes": nbytes, "rows_parsed": 0,
              "candidates_sha256": plan["candidates_sha256"],
              "plan_sha256": digest(out / "plan_STAGE_A.json"),
              "manifest_sha256": digest(manifest) if manifest.exists() else None,
              "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    atomic_json(out / "capture_STAGE_A.json", report)
    return report


def capture(out, candidates, candidate_sha, verify_only=False):
    raw = Path(candidates).read_bytes()
    if hashlib.sha256(raw).hexdigest() != candidate_sha:
        raise ValueError("candidate list hash mismatch")
    symbols = raw.decode("ascii").split()
    if len(set(symbols)) != len(symbols) or any(not re.fullmatch(r"[A-Z0-9]+USDT", s) for s in symbols):
        raise ValueError("malformed candidate universe")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if verify_only and not (out / "plan_STAGE_A.json").exists():
        raise ValueError("verification requires the frozen plan; no network permitted")
    plan = get_plan(out, symbols, candidate_sha)
    manifest = out / "manifest_STAGE_A.jsonl"
    records = read_manifest(manifest, repair_tail=not verify_only)
    done, _ = verified_jobs(out, plan, records)
    print(f"{STAGE}: {len(done)}/{len(plan['jobs'])} archives verified before capture", flush=True)
    if not verify_only:
        try:
            with open(manifest, "a") as mf:
                for ds, sym, key in plan["jobs"]:
                    if key in done:
                        continue
                    rec = transport.fetch_one((ds, sym, key), str(out))
                    records.append(rec)
                    mf.write(json.dumps(rec, sort_keys=True) + "\n")
                    mf.flush()
                    os.fsync(mf.fileno())
                    if rec.get("ok"):
                        done.add(key)
                    if len(records) % 100 == 0:
                        print(f"{STAGE}: {len(done)}/{len(plan['jobs'])} compressed archives captured", flush=True)
        finally:
            report = certificate(out, plan, records)
    else:
        report = certificate(out, plan, records)
    print(json.dumps({k: report[k] for k in ("stage", "status", "planned", "verified", "rows_parsed")}), flush=True)
    if report["status"] != "COMPLETE":
        raise RuntimeError("incomplete capture: analysis remains blocked")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir")
    parser.add_argument("candidates")
    parser.add_argument("candidate_sha256")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    capture(args.out_dir, args.candidates, args.candidate_sha256, args.verify_only)
