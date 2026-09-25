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
4. ``N_trials = max(M_declared, trial-ledger evaluations)``; the kept variants
   are ranked by discovery Deflated Sharpe; Romano-Wolf step-down (Hansen SPA
   as a cross-check) on the discovery net ``r_ex``.
5. Finalists: top <= 3 by DSR among variants with Romano-Wolf p < 0.10 and
   positive walk-forward net annualized alpha. Zero finalists -> NO_GO, holdout
   unopened.
6. The holdout request payload (finalists, evaluation spec and its digest) is
   built here; :func:`request_holdout` writes the spec and the write-once
   request (it does not commit: the owner/lead commits and pushes both).
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
EVAL_SPEC_NAME = "HOLDOUT_EVAL_SPEC.json"
RW_P_MAX = 0.10
STATUS_EVALUATED = "EVALUATED"
STATUS_DROPPED = "DROPPED_ADEQUACY"
FINALIST_RULE_TEXT = ("Romano-Wolf p<0.10", "positive walk-forward net annualized alpha",
                      "top <=3 by discovery DSR")


class ScreenIncomplete(OutcomeAccessRefused):
    """The trial ledger does not hold every declared variant for this screen."""


def eval_spec_path(fw: Firewall) -> Path:
    return fw.artifact(*PREREG_DIR, EVAL_SPEC_NAME)


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


def finalize_screen(fw: Firewall, screen: Mapping[str, Any]) -> dict:
    """Rank, test, select finalists and build the holdout request payload."""
    sealed = load_sealed(fw)
    if sealed["protocol_sha256"] != screen["sealed_sha256"]:
        raise OutcomeAccessRefused("the seal changed since the screen was computed")
    protocol = sealed["protocol"]
    config = screen["config"]
    screen_trials(fw, sealed, config)
    n_trials = ho.n_trials_for_dsr(sealed, ho.TrialLedger(fw).records())
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
        results[vid]["discovery_moments"] = m
        results[vid]["dsr"] = inf.deflated_sharpe(sr=m["sr"], n_obs=m["n"], skew=m["skew"],
                                                  kurtosis=m["kurtosis"], sr_variance=sr_variance,
                                                  n_trials=n_trials)
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
              "data_quality": screen["data_quality"]}
    if not finalists:
        report["verdict"] = vd.zero_finalists(screen["attestation"])
    else:
        spec = {
            "lineage": LINEAGE_ID, "kind": "HOLDOUT_EVAL_SPEC",
            "prereg_sha256": sealed["protocol_sha256"], "screen_config": config,
            "screen_results_digest": report["results_digest"], "finalists": finalists,
            "discovery_stats": {v: {"sr": moments[v]["sr"], "n": moments[v]["n"],
                                    "skew": moments[v]["skew"],
                                    "kurtosis": moments[v]["kurtosis"],
                                    "dsr_at_screen": results[v]["dsr"]["dsr"],
                                    "romano_wolf_p": results[v]["romano_wolf_p"],
                                    "walk_forward_alpha_annual_net":
                                        results[v]["walk_forward_alpha_annual_net"]}
                                for v in finalists},
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
    fw.write_json_atomic(report_path(fw, config["digest"]), report)
    return report


def run_screen(fw: Firewall, vendor: px.PriceVendor, *, table: ev.EventTable | None = None,
               crash_after: int | None = None, log: Callable[[str], None] | None = None) -> dict:
    screen = compute_screen(fw, vendor, table=table, log=log)
    record_trials(fw, screen, crash_after=crash_after)
    return finalize_screen(fw, screen)


def request_holdout(fw: Firewall, report: Mapping[str, Any]) -> dict:
    """Write the evaluation spec and the write-once HOLDOUT_REQUEST.json (not committed)."""
    sealed = load_sealed(fw)
    if report.get("prereg_sha256") != sealed["protocol_sha256"]:
        raise OutcomeAccessRefused("screen report belongs to another seal")
    if not report.get("finalists"):
        raise ho.NoFinalists("zero finalists: NO_GO is recorded and the holdout stays unopened")
    payload = report["holdout_request_payload"]
    spec = payload["eval_spec"]
    if ev.digest(spec) != payload["eval_spec_digest"] or spec["finalists"] != payload["finalists"]:
        raise OutcomeAccessRefused("holdout request payload is inconsistent")
    if spec["screen_config"] != report["config"] or list(report["finalists"]) != payload["finalists"]:
        raise OutcomeAccessRefused("holdout request payload does not match the screen report")
    screen_trials(fw, sealed, report["config"])
    existing = ho.read_holdout_request(fw)
    if existing is not None:                  # crash replay: the same request is not re-created
        same = (existing.get("request_id") == payload["request_id"]
                and existing.get("finalists") == sorted(payload["finalists"])
                and existing.get("eval_spec_digest") == payload["eval_spec_digest"]
                and eval_spec_path(fw).exists()
                and eval_spec_path(fw).read_bytes() == canonical_json(spec) + b"\n")
        if same:
            return existing
        raise ho.HoldoutAlreadyConsumed("HOLDOUT_REQUEST.json already names another look")
    path = eval_spec_path(fw)
    data = canonical_json(spec) + b"\n"
    if path.exists():
        if path.read_bytes() != data:
            raise ho.HoldoutAlreadyConsumed(f"{path.name} already holds another evaluation spec")
    else:
        fw.create_exclusive(path, data)
    return ho.write_holdout_request(fw, payload["request_id"], payload["finalists"],
                                   payload["eval_spec_digest"])
