"""Discovery and walk-forward screen of every declared variant (``QUANT_FASTLANE_HPIT_V1``).

Sealed rules (``multiplicity``, ``variant_grid_rule.post_eligibility_recheck``):

1. Grants for discovery and walk-forward come from
   :func:`quant.fastlane.preregistration.require_outcome_access`; no holdout
   price is reachable (both price windows end at their split ends).
2. Before any return is computed, PIT mapping and pre-entry eligibility are
   applied to discovery and walk-forward events only; a variant with fewer than
   50 eligible issuer-days per year in either split is dropped and logged,
   never replaced (holdout eligibility is not inspected).
3. Every declared variant gets one trial-ledger record per split (discovery
   and walk-forward) through :class:`quant.fastlane.holdout.TrialLedger`, with
   a deterministic trial id bound to the screen configuration, so a crash and
   replay never duplicates a record; a changed configuration (code, vendor,
   event table) is a new trial and raises ``N_trials``.
4. ``N_trials`` = :func:`quant.fastlane.holdout.n_trials_conservative` (at least
   the sealed ``max(M_declared, trial-ledger evaluations)``, at least
   2 x M_declared, and at least the number of distinct discovery/walk-forward
   access configurations); the kept variants are ranked by discovery Deflated
   Sharpe (V[SR] floored at the SR sampling variance, C21); Romano-Wolf
   step-down (Hansen SPA as a cross-check) on the discovery net ``r_ex``.
5. Finalists: top <= 3 by DSR among variants with Romano-Wolf p < 0.10 and
   positive walk-forward net annualized alpha. Zero finalists -> NO_GO, holdout
   unopened.
6. :func:`request_holdout` trusts no caller-supplied report: it re-runs the whole
   screen under normal grants, checks every declared variant's discovery AND
   walk-forward trial records against the recomputed specs, derives finalists and
   DSR inputs from that run, and writes (create-exclusive) ``SCREEN_REPORT.json``,
   ``HOLDOUT_EVAL_SPEC.json`` and ``HOLDOUT_REQUEST.json``; the owner/lead commits
   and pushes all three before the look. :func:`recompute_and_verify` is the same
   recomputation, reused by ``verdict.evaluate_holdout`` before the grant.
"""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any, Callable, Mapping

from quant.fastlane import evaluation as ev
from quant.fastlane import holdout as ho
from quant.fastlane import inference as inf
from quant.fastlane import prices as px
from quant.fastlane import verdict as vd
from quant.fastlane.firewall import LINEAGE_ID, Firewall
from quant.fastlane.preregistration import (PREREG_DIR, OutcomeAccessRefused, canonical_json,
                                            load_sealed, require_outcome_access)

SCHEMA = "fastlane.screen.v1"
SCREEN_SPLITS = ("discovery", "walk_forward")
EVAL_SPEC_NAME = ho.EVAL_SPEC_NAME
RW_P_MAX = 0.10
STATUS_EVALUATED = "EVALUATED"
STATUS_DROPPED = "DROPPED_ADEQUACY"
FINALIST_RULE_TEXT = ("Romano-Wolf p<0.10", "positive walk-forward net annualized alpha",
                      "top <=3 by discovery DSR")


class ScreenIncomplete(OutcomeAccessRefused):
    """The trial ledger does not hold every declared variant for this screen."""


def eval_spec_path(fw: Firewall) -> Path:
    return ho.eval_spec_path(fw)


def screen_report_path(fw: Firewall) -> Path:
    return ho.screen_report_path(fw)


def report_path(fw: Firewall, config_digest: str) -> Path:
    return fw.data("screen", f"SCREEN_REPORT_{config_digest[7:23]}.json")


def screen_config(sealed: Mapping[str, Any], table: ev.EventTable,
                  context: ev.VendorContext) -> dict:
    protocol = sealed["protocol"]
    core = {"schema": SCHEMA, "lineage": LINEAGE_ID, "prereg_sha256": sealed["protocol_sha256"],
            "code_fingerprint": ho.code_fingerprint(), "events_digest": table.digest,
            "vendor": context.identity(),
            "inference": {"block": protocol["inference"]["block_length_sessions"],
                          "draws": protocol["inference"]["bootstrap_draws"],
                          "seed": protocol["inference"]["bootstrap_seed"]}}
    return {**core, "digest": ev.digest(core)}


def trial_id(variant_id: str, split: str, config: Mapping[str, Any]) -> str:
    return f"{variant_id}|{split}|{config['digest'][7:23]}"


def _check_rule_text(protocol: Mapping[str, Any]) -> None:
    rule = protocol["multiplicity"]["finalist_rule"]
    for needle in FINALIST_RULE_TEXT:
        if needle not in rule:
            raise ev.EvaluationError(f"sealed finalist rule no longer says {needle!r}")


def compute_screen(fw: Firewall, vendor: px.PriceVendor, *, table: ev.EventTable | None = None,
                   log: Callable[[str], None] | None = None) -> dict:
    """Evaluate every declared variant in discovery and walk-forward (no ledger writes)."""
    sealed = load_sealed(fw)
    protocol = sealed["protocol"]
    params = ev.Params.from_protocol(protocol)
    _check_rule_text(protocol)
    context = ev.VendorContext(fw, vendor)
    table = table or ev.EventTable.load_bound(fw, protocol)
    grants = {s: require_outcome_access(fw, s, sealed["protocol_sha256"]) for s in SCREEN_SPLITS}
    markets = {s: ev.MarketData(vendor, grants[s], s) for s in SCREEN_SPLITS}
    config = screen_config(sealed, table, context)
    floor = float(protocol["variant_grid_rule"]["adequacy"]["min_issuer_days_per_year_each_split"])
    variants: dict[str, dict] = {}
    # pass 1: post-eligibility recheck for every variant before any return is computed
    for declared in protocol["variants"]:
        vid = declared["variant_id"]
        variant = ev.Variant.from_protocol(protocol, vid)
        adequacy = {s: ev.adequacy_counts(variant, table, markets[s], params)
                    for s in SCREEN_SPLITS}
        kept = all(a["per_year"] >= floor for a in adequacy.values())
        variants[vid] = {"variant_id": vid, "adequacy": adequacy,
                         "status": STATUS_EVALUATED if kept else STATUS_DROPPED,
                         "evaluations": {}}
    # pass 2: returns for the kept variants only
    for vid, entry in variants.items():
        adequacy = entry["adequacy"]
        if entry["status"] == STATUS_EVALUATED:
            for s in SCREEN_SPLITS:
                result = ev.evaluate_variant(sealed=sealed, variant_id=vid, table=table,
                                             market=markets[s], context=context)
                entry["evaluations"][s] = {
                    "fingerprint": result["fingerprint"]["digest"],
                    "output_digest": result["output_digest"],
                    "counts": result["counts"], "summary": result["summary"],
                    "idle_cash": result["idle_cash"],
                    "net_start_index": result["series"]["start_index"],
                    "net_r_ex": result["series"]["r_ex"]["net"]}
        if log:
            log(f"{vid}: {entry['status']} "
                + " ".join(f"{s}={adequacy[s]['per_year']:.1f}/yr" for s in SCREEN_SPLITS))
    return {"sealed_sha256": sealed["protocol_sha256"], "config": config, "variants": variants,
            "data_quality": {s: dict(sorted(markets[s].quality.items())) for s in SCREEN_SPLITS},
            "attestation": context.attestation}


def trial_spec(screen: Mapping[str, Any], variant_id: str, split: str) -> dict:
    entry = screen["variants"][variant_id]
    evaluation = entry["evaluations"].get(split)
    return {"lineage": LINEAGE_ID, "kind": "SCREEN_TRIAL", "variant_id": variant_id,
            "split": split, "screen_config": screen["config"]["digest"],
            "status": entry["status"], "adequacy": entry["adequacy"][split],
            "evaluation": None if evaluation is None else {
                "fingerprint": evaluation["fingerprint"],
                "output_digest": evaluation["output_digest"],
                "alpha_annual_net": evaluation["summary"]["net"]["alpha_annual"]}}


def record_trials(fw: Firewall, screen: Mapping[str, Any], *,
                  crash_after: int | None = None) -> list[dict]:
    """One trial record per declared variant and split (idempotent on replay)."""
    ledger = ho.TrialLedger(fw)
    written = []
    for vid in screen["variants"]:
        for split in SCREEN_SPLITS:
            written.append(ledger.record(trial_id(vid, split, screen["config"]), vid, split,
                                         trial_spec(screen, vid, split)))
            if crash_after is not None and len(written) >= crash_after:
                raise ho.SimulatedCrash(f"crash injected after {len(written)} trial records")
    return written


def screen_trials(fw: Firewall, sealed: Mapping[str, Any],
                  config: Mapping[str, Any]) -> dict[str, list[dict]]:
    """This screen's trial records by split; raises unless every declared variant is there once."""
    suffix = "|" + config["digest"][7:23]
    declared = [v["variant_id"] for v in sealed["protocol"]["variants"]]
    m_declared = int(sealed["protocol"]["multiplicity"]["M_declared"])
    records = [r for r in ho.TrialLedger(fw).records()
               if r.get("prereg_sha256") == sealed["protocol_sha256"]
               and str(r.get("trial_id", "")).endswith(suffix)]
    by_split = {s: [r for r in records if r["split"] == s] for s in SCREEN_SPLITS}
    for split, recs in by_split.items():
        ids = [r["variant_id"] for r in recs]
        if len(recs) != m_declared or sorted(ids) != sorted(declared):
            raise ScreenIncomplete(
                f"the trial ledger holds {len(recs)} {split} records for this screen; exactly "
                f"M_declared = {m_declared}, one per declared variant, are required")
    return by_split


def verify_trials(fw: Firewall, sealed: Mapping[str, Any],
                  screen: Mapping[str, Any]) -> dict[str, dict[str, dict]]:
    """Every declared variant's discovery AND walk-forward record must carry the spec (hence
    the output digest) of THIS recomputation; returns the listing pinned in the report."""
    by_split = screen_trials(fw, sealed, screen["config"])
    listing: dict[str, dict[str, dict]] = {}
    for split, recs in by_split.items():
        for rec in recs:
            vid = rec["variant_id"]
            expected = ho.json_digest(trial_spec(screen, vid, split))
            if rec.get("spec_digest") != expected:
                raise ScreenIncomplete(
                    f"{vid} {split} trial record does not match the recomputed evaluation "
                    "(different outputs or a fabricated record)")
            listing.setdefault(vid, {})[split] = {"trial_id": rec["trial_id"],
                                                  "spec_digest": rec["spec_digest"]}
    return {vid: listing[vid] for vid in sorted(listing)}


def derive_screen(sealed: Mapping[str, Any], screen: Mapping[str, Any], *, n_trials: int,
                  trials: Mapping[str, Any]) -> dict:
    """Deterministic ranking, tests, finalists and holdout payload (no I/O)."""
    if sealed["protocol_sha256"] != screen["sealed_sha256"]:
        raise OutcomeAccessRefused("the seal changed since the screen was computed")
    protocol = sealed["protocol"]
    config = screen["config"]
    inference = protocol["inference"]
    block, draws, seed = (int(inference["block_length_sessions"]),
                          int(inference["bootstrap_draws"]), int(inference["bootstrap_seed"]))
    results: dict[str, dict] = {}
    moments: dict[str, dict] = {}
    for vid, entry in screen["variants"].items():
        row: dict[str, Any] = {"status": entry["status"],
                               "adequacy": {s: entry["adequacy"][s]["per_year"]
                                            for s in SCREEN_SPLITS}}
        if entry["status"] == STATUS_EVALUATED:
            disc, wf = entry["evaluations"]["discovery"], entry["evaluations"]["walk_forward"]
            row["discovery_alpha_annual_net"] = disc["summary"]["net"]["alpha_annual"]
            row["walk_forward_alpha_annual_net"] = wf["summary"]["net"]["alpha_annual"]
            try:
                moments[vid] = inf.sharpe_moments(disc["net_r_ex"])
            except inf.InsufficientData as exc:
                row["status"] = "INSUFFICIENT_DATA"
                row["insufficient"] = str(exc)
        results[vid] = row
    srs = [m["sr"] for m in moments.values()]
    sr_variance = statistics.variance(srs) if len(srs) >= 2 else 0.0
    for vid, m in moments.items():
        used = inf.floored_sr_variance(sr_variance, m["sr"], m["n"])
        results[vid]["discovery_moments"] = m
        results[vid]["dsr"] = {**inf.deflated_sharpe(
            sr=m["sr"], n_obs=m["n"], skew=m["skew"], kurtosis=m["kurtosis"],
            sr_variance=used, n_trials=n_trials), "sr_variance_used": used}
    rw = None
    if moments:
        start, aligned = inf.align({vid: (screen["variants"][vid]["evaluations"]["discovery"]
                                          ["net_start_index"],
                                          screen["variants"][vid]["evaluations"]["discovery"]
                                          ["net_r_ex"]) for vid in moments})
        rw = inf.romano_wolf_stepdown(aligned, block=block, draws=draws, seed=seed)
        for vid in moments:
            results[vid]["romano_wolf_p"] = rw["p_adjusted"][vid]
    eligible = [vid for vid in moments
                if results[vid]["romano_wolf_p"] < RW_P_MAX
                and (results[vid]["walk_forward_alpha_annual_net"] or 0.0) > 0.0]
    ranked = sorted(moments, key=lambda v: (-results[v]["dsr"]["dsr"], v))
    max_finalists = int(protocol["multiplicity"]["max_finalists"])
    finalists = sorted(sorted(eligible, key=lambda v: (-results[v]["dsr"]["dsr"], v))[:max_finalists])
    results_core = {"results": results, "ranking_by_dsr": ranked, "finalists": finalists,
                    "n_trials_for_dsr": n_trials, "sr_variance": sr_variance,
                    "romano_wolf": None if rw is None else {k: rw[k] for k in (
                        "method", "block", "draws", "seed", "n_sessions", "p_adjusted", "spa")}}
    results_core = vd.sanitize(results_core)
    report = {"schema": SCHEMA, "lineage": LINEAGE_ID, "prereg_sha256": sealed["protocol_sha256"],
              "config": config, **results_core, "results_digest": ev.digest(results_core),
              "trials": trials, "data_quality": screen["data_quality"]}
    if not finalists:
        report["verdict"] = vd.zero_finalists(screen["attestation"])
        return report
    spec = {
        "lineage": LINEAGE_ID, "kind": "HOLDOUT_EVAL_SPEC",
        "prereg_sha256": sealed["protocol_sha256"], "screen_config": config,
        "screen_results_digest": report["results_digest"], "finalists": finalists,
        "discovery_stats": {v: {"sr": moments[v]["sr"], "n": moments[v]["n"],
                                "skew": moments[v]["skew"], "kurtosis": moments[v]["kurtosis"],
                                "sr_variance_used": results[v]["dsr"]["sr_variance_used"],
                                "dsr_at_screen": results[v]["dsr"]["dsr"],
                                "romano_wolf_p": results[v]["romano_wolf_p"],
                                "walk_forward_alpha_annual_net":
                                    results[v]["walk_forward_alpha_annual_net"]}
                            for v in finalists},
        "discovery_stats_role": "documentation only: the look recomputes them from the screen",
        "sr_variance": sr_variance, "n_trials_for_dsr_at_screen": n_trials,
        "holdout_rules": {
            "block": block, "draws": draws, "seed": seed,
            "hac": {"kernel": inference["co_check"]["kernel"],
                    "b": inference["co_check"]["bandwidth_b"],
                    "null": {k: inf.FIXED_B_NULL[k] for k in ("method", "steps", "reps",
                                                              "seed")}},
            "robustness_seeds": inference["seed_robustness"]["seeds"],
            "capacity_multiples": protocol["capacity"]["multiples_of_C0"],
            "criteria": vd.criteria(protocol)},
    }
    spec = vd.sanitize(spec)
    report["holdout_request_payload"] = {
        "request_id": f"{LINEAGE_ID}-LOOK-1-{config['digest'][7:19]}",
        "finalists": finalists, "eval_spec": spec, "eval_spec_digest": ev.digest(spec)}
    return report


def finalize_screen(fw: Firewall, screen: Mapping[str, Any]) -> dict:
    """Verify this screen's trial records, derive the report and cache it under var/."""
    sealed = load_sealed(fw)
    trials = verify_trials(fw, sealed, screen)
    n_trials = ho.n_trials_conservative(fw, sealed)["n_trials_for_dsr"]
    report = derive_screen(sealed, screen, n_trials=n_trials, trials=trials)
    fw.write_json_atomic(report_path(fw, screen["config"]["digest"]), report)
    return report


def run_screen(fw: Firewall, vendor: px.PriceVendor, *, table: ev.EventTable | None = None,
               crash_after: int | None = None, log: Callable[[str], None] | None = None) -> dict:
    screen = compute_screen(fw, vendor, table=table, log=log)
    record_trials(fw, screen, crash_after=crash_after)
    return finalize_screen(fw, screen)


def recompute_and_verify(fw: Firewall, vendor: px.PriceVendor, *,
                         table: ev.EventTable | None = None,
                         n_trials: int | None = None) -> tuple[dict, dict]:
    """Re-run the whole screen under normal grants and check it against the trial ledger.

    Returns (screen, report). Nothing is taken from a caller-supplied report or spec.
    """
    sealed = load_sealed(fw)
    screen = compute_screen(fw, vendor, table=table)
    trials = verify_trials(fw, sealed, screen)
    if n_trials is None:
        n_trials = ho.n_trials_conservative(fw, sealed)["n_trials_for_dsr"]
    return screen, derive_screen(sealed, screen, n_trials=int(n_trials), trials=trials)


def _write_or_match(fw: Firewall, path: Path, obj: Mapping[str, Any]) -> None:
    data = canonical_json(obj) + b"\n"
    if path.exists():
        if path.read_bytes() != data:
            raise ho.HoldoutAlreadyConsumed(f"{path.name} already holds other content; inspect "
                                            "it (uncommitted leftovers may be removed)")
        return
    fw.create_exclusive(path, data)


def request_holdout(fw: Firewall, vendor: px.PriceVendor, *,
                    table: ev.EventTable | None = None) -> dict:
    """Recompute the screen, then write SCREEN_REPORT, HOLDOUT_EVAL_SPEC and the request.

    Nothing is committed here; commit and push all three before evaluate-holdout.
    """
    sealed = load_sealed(fw)
    _, report = recompute_and_verify(fw, vendor, table=table)
    if not report["finalists"]:
        raise ho.NoFinalists("zero finalists: NO_GO is recorded and the holdout stays unopened")
    payload = report["holdout_request_payload"]
    spec, spec_digest = payload["eval_spec"], payload["eval_spec_digest"]
    report_digest = ho.json_digest(report)
    existing = ho.read_holdout_request(fw)
    if existing is not None:              # crash replay: the same request is not re-created
        if (existing.get("request_id") == payload["request_id"]
                and existing.get("finalists") == sorted(payload["finalists"])
                and existing.get("eval_spec_digest") == spec_digest
                and existing.get("screen_report_digest") == report_digest):
            return existing
        raise ho.HoldoutAlreadyConsumed("HOLDOUT_REQUEST.json already names another look")
    _write_or_match(fw, screen_report_path(fw), report)
    _write_or_match(fw, eval_spec_path(fw), spec)
    receipt = ho._screen_receipt(fw, sealed["protocol_sha256"], payload["request_id"],
                                 payload["finalists"], spec_digest, report_digest)
    return ho._write_holdout_request(fw, payload["request_id"], payload["finalists"], spec_digest,
                                    report_digest, receipt=receipt)
