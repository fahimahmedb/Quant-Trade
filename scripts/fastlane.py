"""Operator CLI for the fast lane ``QUANT_FASTLANE_HPIT_V1`` (outcome-blind weeks 0-2).

    python3 scripts/fastlane.py fetch-insider [--start 2006q1] [--end 2026q2] [--limit N]
        Download SEC Insider Transactions Data Sets (needs QUANT_SEC_USER_AGENT).
    python3 scripts/fastlane.py build-events
        Build original-Form-4 P/A events and issuer filing-day aggregates.
    python3 scripts/fastlane.py census
        Outcome-blind census -> research/fastlane/census_v1.{json,md}.
    python3 scripts/fastlane.py draft-protocol
        Write the DRAFT (unsealed) protocol from the census.
    python3 scripts/fastlane.py seal-prereg --protocol PATH
        Seal a FINAL_FOR_SEAL protocol once (refuses drafts and overwrites).
    python3 scripts/fastlane.py refresh-manifest
        Drop legacy User-Agent hashes from fetch manifests and rewrite the
        consolidated manifest (no network).

Raw data and derived tables live under var/fastlane/ (git-ignored); only small
artifacts go to research/fastlane/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.fastlane.firewall import Firewall  # noqa: E402


def _log(message: str) -> None:
    print(message, flush=True)


def cmd_fetch_insider(fw: Firewall, args) -> int:
    from quant.fastlane import sec_insider as si
    user_agent = si.require_user_agent()
    usage = si.disk_guard(fw)
    _log(f"disk before: fastlane={usage['fastlane_bytes']} bytes, free={usage['free_bytes']} bytes")
    client = si.SecClient(user_agent)
    links, discovery = si.discover(fw, client)
    selected = si.select_quarters(links, args.start, args.end)
    if args.limit:
        selected = selected[: args.limit]
    _log(f"index page lists {len(links)} quarters "
         f"({links[0].quarter}..{links[-1].quarter}); fetching {len(selected)}")
    actions = {}
    for link in selected:
        manifest, action = si.fetch_quarter(fw, client, link)
        actions[action] = actions.get(action, 0) + 1
        _log(f"{link.quarter}: {action} {manifest['bytes']} bytes sha256={manifest['sha256'][:16]}")
    quarters = [l.quarter for l in links]
    consolidated = si.consolidated_manifest(fw, quarters, discovery)
    fw.write_json_atomic(fw.artifact("sec_insider_manifest_v1.json"), consolidated)
    usage = si.disk_guard(fw)
    _log(json.dumps({"actions": actions, "requests": client.requests_made,
                     "quarters_in_manifest": consolidated["quarter_count"],
                     "total_bytes": consolidated["total_bytes"], **usage}))
    return 0


def cmd_build_events(fw: Firewall, args) -> int:
    from quant.fastlane import events as ev
    from quant.fastlane import sec_insider as si
    manifests = sorted(p.stem for p in fw.iter_files(fw.data("manifests", "sec_insider"), "*.json")
                       if not p.stem.startswith("_"))
    quarters = si.select_quarters([si.QuarterLink(q, "") for q in manifests], args.start, args.end)
    manifest = ev.build_all(fw, [q.quarter for q in quarters], log=_log)
    summary = {k: manifest[k] for k in ("lineage", "schema", "code_fingerprint", "population_rule",
                                         "primary_filters", "inputs", "outputs", "counts",
                                         "duplicate_accession_check")}
    summary["malformed_rows_total"] = {
        member: sum(q.get(member, 0) for q in manifest["malformed_rows_by_quarter"].values())
        for member in ("SUBMISSION.tsv", "REPORTINGOWNER.tsv", "NONDERIV_TRANS.tsv",
                       "FOOTNOTES.tsv")}
    fw.write_json_atomic(fw.artifact("events_build_manifest_v1.json"), summary)
    _log(json.dumps({"outputs": manifest["outputs"], "counts": manifest["counts"]}, indent=1))
    return 0


def cmd_refresh_manifest(fw: Firewall, args) -> int:
    from quant.fastlane import sec_insider as si
    changed = si.scrub_user_agent_bindings(fw)
    discovery_path = fw.data("manifests", "sec_insider", "_discovery.json")
    discovery = fw.read_json(discovery_path) if discovery_path.exists() else None
    quarters = (discovery or {}).get("quarters_linked") or sorted(
        p.stem for p in fw.iter_files(fw.data("manifests", "sec_insider"), "*.json")
        if not p.stem.startswith("_"))
    consolidated = si.consolidated_manifest(fw, quarters, discovery)
    fw.write_json_atomic(fw.artifact("sec_insider_manifest_v1.json"), consolidated)
    _log(json.dumps({"manifests_scrubbed": changed,
                     "set_fingerprint": consolidated["set_fingerprint"]}))
    return 0


def cmd_census(fw: Firewall, args) -> int:
    from quant.fastlane import census
    result = census.run_census(fw)
    _log(json.dumps(result["headline"], indent=1))
    return 0


def cmd_draft_protocol(fw: Firewall, args) -> int:
    from quant.fastlane import protocol_draft
    protocol = protocol_draft.write_draft(fw)
    _log(f"draft protocol written: {len(protocol['variants'])} variants, status={protocol['status']}")
    return 0


def cmd_seal_prereg(fw: Firewall, args) -> int:
    from quant.fastlane import preregistration as pr
    protocol = fw.read_json(args.protocol)
    record = pr.seal_protocol(fw, protocol)
    _log(json.dumps({"sealed": str(pr.sealed_path(fw)), "protocol_sha256": record["protocol_sha256"],
                     "sealed_at_utc": record["sealed_at_utc"]}))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT), help="repository root (default: this repo)")
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch-insider")
    fetch.add_argument("--start", default="2006q1")
    fetch.add_argument("--end", default=None)
    fetch.add_argument("--limit", type=int, default=0)
    build = sub.add_parser("build-events")
    build.add_argument("--start", default="2006q1")
    build.add_argument("--end", default=None)
    sub.add_parser("census")
    sub.add_parser("draft-protocol")
    sub.add_parser("refresh-manifest")
    seal = sub.add_parser("seal-prereg")
    seal.add_argument("--protocol", required=True)
    args = parser.parse_args(argv)
    fw = Firewall(Path(args.root))
    handler = {
        "fetch-insider": cmd_fetch_insider,
        "build-events": cmd_build_events,
        "census": cmd_census,
        "draft-protocol": cmd_draft_protocol,
        "refresh-manifest": cmd_refresh_manifest,
        "seal-prereg": cmd_seal_prereg,
    }[args.command]
    return handler(fw, args)


if __name__ == "__main__":
    raise SystemExit(main())
