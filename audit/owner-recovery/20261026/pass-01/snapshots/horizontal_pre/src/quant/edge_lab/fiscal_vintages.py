"""Software-only prototype for prospective byte vintages. No network/real capture.

Receipt time is a conservative usable-from time, never a historical release
time. Byte changes are not automatically revisions of an economic statistic.
Empirical activation needs a separately evidenced admission; it is refused here.
"""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

from quant.state import write_json
from .engine import timestamp
from .store import Refused, digest


class FiscalVintages:
    def __init__(self, directory, clock=None, max_bytes=262144):
        self.root = Path(directory)
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        if type(max_bytes) is not int or not 0 < max_bytes <= 262144:
            raise Refused("A fixed measurable payload ceiling is required")
        self.max_bytes = max_bytes

    def record(self, body, *, source_url, synthetic=False, provider_release_at=None):
        # This build admits synthetic QA only, even with a real source URL.
        if synthetic is not True or not source_url.startswith("https://example.invalid/"):
            raise Refused("EMPIRICAL_CAPTURE_NOT_ADMITTED: synthetic fixtures only")
        if not isinstance(body, bytes) or not 0 < len(body) <= self.max_bytes:
            raise Refused("Payload missing or exceeds the frozen software ceiling")
        try:
            fixture = json.loads(body)
        except (ValueError, UnicodeDecodeError) as exc:
            raise Refused("Synthetic JSON payload required") from exc
        if not isinstance(fixture, dict) or fixture.get("synthetic_fixture") is not True:
            raise Refused("Unlabelled payload is not a software fixture")
        now = timestamp(self.clock()).isoformat()
        if provider_release_at is not None:
            timestamp(provider_release_at)  # validate; never use it as our receipt time
        self.root.mkdir(parents=True, exist_ok=True)
        # Same process safety as the lab: lock, exclusive payload writes, atomic index.
        import fcntl
        fd = os.open(self.root / ".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            manifest_path = self.root / "manifest.json"
            if manifest_path.is_symlink():
                raise Refused("Linked vintage index is not admitted")
            if manifest_path.exists():
                manifest = json.loads(manifest_path.read_text())
                if manifest.get("integrity") != digest({k:v for k,v in manifest.items() if k != "integrity"}):
                    raise Refused("Damaged vintage index: preserve it, never reset")
            else:
                manifest = {"schema": 1, "source_url": source_url, "purpose": "SYNTHETIC_SOFTWARE_QA", "receipts": []}
            if manifest["source_url"] != source_url:
                raise Refused("One exact source per vintage index")
            if manifest.get("schema") != 1 or manifest.get("purpose") != "SYNTHETIC_SOFTWARE_QA":
                raise Refused("No silent adoption of empirical/legacy vintages")
            rows = manifest["receipts"]
            if rows and timestamp(now) < timestamp(rows[-1]["recorded_at_utc"]):
                raise Refused("Clock regression: retain prior receipts")
            sha = hashlib.sha256(body).hexdigest()
            payload = self.root / (sha + ".json")
            known = any(r["sha256"] == sha for r in rows)
            if known:
                if payload.is_symlink() or not payload.is_file() or payload.read_bytes() != body:
                    raise Refused("Saved payload differs or is missing: do not recapture")
            elif payload.exists():
                raise Refused("Unindexed interrupted write: reconcile saved bytes, never retry")
            else:
                with payload.open("xb") as output:
                    output.write(body)
                    output.flush()
                    os.fsync(output.fileno())
            row = {"sequence": len(rows)+1, "sha256": sha, "payload_bytes": len(body),
                "recorded_at_utc": now, "usable_from_utc": now,
                "provider_release_at_unverified": provider_release_at,
                "publication_time_authenticated": False, "new_byte_version": not known,
                "economic_revision_authenticated": False,
                "previous": rows[-1]["receipt_hash"] if rows else "0"*64}
            row["receipt_hash"] = digest(row)
            rows.append(row)
            manifest["integrity"] = digest({k:v for k,v in manifest.items() if k != "integrity"})
            write_json(manifest_path, manifest)
            return row
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
