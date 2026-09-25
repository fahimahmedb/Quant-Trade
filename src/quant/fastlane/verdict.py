"""GO / INCONCLUSIVE / NO_GO for ``QUANT_FASTLANE_HPIT_V1`` and the single holdout look.

Sealed rules (``go_criterion``, ``outcomes``, ``multiplicity.holdout``):

* GO needs, for at least one finalist, ALL of: annualized net alpha vs SPY
  >= 3 %/yr at 1x C0 (base delisting); Holm-adjusted p < 0.05 for BOTH the
  studentized block bootstrap and the fixed-b HAC co-check (Holm over the
  finalists, each test separately); net result positive at 1x C0 after
  frictions (C4: net alpha > 0 AND net P&L in USD > 0); discovery DSR > 0.95
  with N = N_trials; vendor attestation ``go_eligible`` (a vendor without
  delisted names never passes this leg).
* Otherwise INCONCLUSIVE if some finalist's one-sided 95 % upper bound of
  annualized net alpha is >= 3 %/yr (C3: the larger of the bootstrap
  percentile-t and the fixed-b HAC bounds), else NO_GO.
* Zero finalists: NO_GO, the holdout stays unopened.
* Only GO may authorize (SHADOW_PROVISIONAL, paper) sizing.

Reporting only (never gating): capacity at 1x/10x/100x C0 with the 0.1 % ADV20
cap, the 2x friction stress, the UNKNOWN -100 % delisting stress and the seed
robustness under seeds seed+1..seed+5.

:func:`evaluate_holdout` performs the one look: it refuses without the
committed request, a matching evaluation spec, the same vendor identity as the
screen, and a ``go_eligible`` attestation, and only then asks
:func:`quant.fastlane.preregistration.require_outcome_access` for the grant.
"""

from __future__ import annotations

from typing import Any, Mapping

from quant.fastlane import evaluation as ev
from quant.fastlane import holdout as ho
from quant.fastlane import inference as inf
from quant.fastlane import prices as px
from quant.fastlane.firewall import LINEAGE_ID, Firewall
from quant.fastlane.preregistration import (OutcomeAccessRefused, canonical_json, load_sealed,
                                            require_outcome_access)

VERDICT_GO = px.VERDICT_GO
VERDICT_INCONCLUSIVE = px.VERDICT_INCONCLUSIVE
VERDICT_NO_GO = px.VERDICT_NO_GO
RESULT_NAME = "HOLDOUT_RESULT.json"
SCHEMA = "fastlane.holdout_result.v1"


def criteria(protocol: Mapping[str, Any]) -> dict:
    go = protocol["go_criterion"]
    out = protocol["outcomes"]
    return {"alpha_min_annual": float(go["alpha_min_annual"]),
            "holm_family_alpha": float(go["holm_family_alpha"]),
            "dsr_min": float(go["dsr_min"]),
            "inconclusive_upper_bound_min_annual": float(out["inconclusive_upper_bound_min_annual"]),
            "inconclusive_ci_level_one_sided": float(out["inconclusive_ci_level_one_sided"])}


def zero_finalists(attestation: px.VendorAttestation | None = None) -> dict:
    return {"verdict": VERDICT_NO_GO, "holdout": "UNOPENED", "reason": "zero finalists",
            "finalists": [], "evidence_label": attestation.evidence_label if attestation else None,
            "sizing_authorized": False}


def decide(finalists: Mapping[str, Mapping[str, Any]], attestation: px.VendorAttestation,
           rules: Mapping[str, float]) -> dict:
    """Apply the sealed outcome rules to the finalists' holdout statistics.

    Each finalist maps to: ``alpha_annual`` (net, 1x C0, base delisting),
    ``pnl_usd`` (net), ``p_bootstrap``, ``p_hac``, ``dsr`` and
    ``upper_bound_annual`` (C3).
    """
    if not finalists:
        return zero_finalists(attestation)
    holm_boot = inf.holm({v: float(s["p_bootstrap"]) for v, s in finalists.items()})
    holm_hac = inf.holm({v: float(s["p_hac"]) for v, s in finalists.items()})
    per: dict[str, dict] = {}
    for v in sorted(finalists):
        s = dict(finalists[v])
        if s.get("alpha_annual") is None:              # no invested session: every leg fails
            s["alpha_annual"], s["pnl_usd"] = float("-inf"), 0.0
        legs = {
            "alpha_at_least_min": s["alpha_annual"] >= rules["alpha_min_annual"],
            "holm_bootstrap_below_alpha": holm_boot[v] < rules["holm_family_alpha"],
            "holm_hac_below_alpha": holm_hac[v] < rules["holm_family_alpha"],
            "net_positive_at_1x_c0": s["alpha_annual"] > 0 and s["pnl_usd"] > 0,
            "dsr_above_min": s["dsr"] > rules["dsr_min"],
            "vendor_go_eligible": bool(attestation.go_eligible),
        }
        per[v] = {"legs": legs, "go": all(legs.values()),
                  "p_bootstrap_holm": holm_boot[v], "p_hac_holm": holm_hac[v],
                  "upper_bound_annual": s["upper_bound_annual"],
                  "upper_bound_reaches_min": (s["upper_bound_annual"]
                                              >= rules["inconclusive_upper_bound_min_annual"])}
    go = sorted(v for v, r in per.items() if r["go"])
    if go:
        verdict = VERDICT_GO
    elif any(r["upper_bound_reaches_min"] for r in per.values()):
        verdict = VERDICT_INCONCLUSIVE
    else:
        verdict = VERDICT_NO_GO
    return {"verdict": verdict, "holdout": "OPENED", "finalists": sorted(finalists),
            "go_finalists": go, "per_finalist": per, "evidence_label": attestation.evidence_label,
            "sizing_authorized": verdict == VERDICT_GO,
            "authority_if_go": "SHADOW_PROVISIONAL paper only" if verdict == VERDICT_GO else None}


def capacity_report(alpha_by_multiple: Mapping[float, float | None]) -> list[dict]:
    return [{"c0_multiple": m, "net_alpha_annual": alpha_by_multiple[m]}
            for m in sorted(alpha_by_multiple)]


def stress_report(summary: Mapping[str, Mapping[str, Any]]) -> dict:
    keys = ("gross", "net", "net_friction_stress", "net_delisting_stress")
    return {k: {"alpha_annual": summary[k]["alpha_annual"], "pnl_usd": summary[k]["pnl_usd"]}
            for k in keys if k in summary}


def upper_bound(boot: Mapping[str, Any], hac: Mapping[str, Any]) -> float:
    """C3: the larger (less exclusionary) of the two one-sided 95 % upper bounds."""
    return max(float(boot["upper_bound_annual"]), float(hac["upper_bound_annual"]))


def finalist_statistics(net_series: list, protocol: Mapping[str, Any], seed: int) -> dict:
    """Both holdout tests; too little data fails GO and cannot exclude 3 %/yr (UB = inf)."""
    inference = protocol["inference"]
    try:
        return _finalist_statistics(net_series, protocol, inference, seed)
    except inf.InsufficientData as exc:
        empty = {"p_value": 1.0, "upper_bound_annual": float("inf"), "insufficient": str(exc)}
        return {"bootstrap": dict(empty), "hac": dict(empty), "upper_bound_annual": float("inf")}


def _finalist_statistics(net_series: list, protocol: Mapping[str, Any],
                         inference: Mapping[str, Any], seed: int) -> dict:
    boot = inf.studentized_block_bootstrap(net_series,
                                           block=int(inference["block_length_sessions"]),
                                           draws=int(inference["bootstrap_draws"]), seed=seed,
                                           level=float(protocol["outcomes"]
                                                       ["inconclusive_ci_level_one_sided"]))
    hac = inf.fixed_b_hac_test(net_series, b=float(inference["co_check"]["bandwidth_b"]),
                               kernel=inference["co_check"]["kernel"],
                               level=float(protocol["outcomes"]["inconclusive_ci_level_one_sided"]))
    return {"bootstrap": boot, "hac": hac, "upper_bound_annual": upper_bound(boot, hac)}


def result_path(fw: Firewall):
    return fw.artifact(RESULT_NAME)


def evaluate_holdout(fw: Firewall, vendor: px.PriceVendor, *,
                     table: ev.EventTable | None = None) -> dict:
    """The single holdout look (refuses unless every precondition holds)."""
    from quant.fastlane import screen as sc
    sealed = load_sealed(fw)
    protocol = sealed["protocol"]
    request = ho.read_holdout_request(fw)
    if request is None:
        raise OutcomeAccessRefused("no committed HOLDOUT_REQUEST.json: run the screen, write the "
                                   "request, commit and push it first")
    spec_path = sc.eval_spec_path(fw)
    if not spec_path.exists():
        raise OutcomeAccessRefused(f"{spec_path.name} is missing")
    spec = fw.read_json(spec_path)
    spec_digest = ev.digest(spec)
    if spec_digest != request.get("eval_spec_digest"):
        raise OutcomeAccessRefused("evaluation spec differs from the one pinned by the request")
    if sorted(spec.get("finalists") or []) != request.get("finalists"):
        raise OutcomeAccessRefused("evaluation spec and request name different finalists")
    context = ev.VendorContext(fw, vendor)
    if context.identity() != spec["screen_config"]["vendor"]:
        raise ev.VendorMismatch("vendor identity or manifests changed since the screen")
    if not context.attestation.go_eligible:
        raise OutcomeAccessRefused(
            f"vendor evidence is {context.attestation.evidence_label}: it can never yield GO, so "
            "the one holdout look is not spent on it")
    grant = require_outcome_access(fw, "holdout", sealed["protocol_sha256"],
                                   holdout_request_id=request["request_id"],
                                   holdout_variants=request["finalists"],
                                   eval_spec_digest=spec_digest)
    table = table or ev.EventTable.load_bound(fw, protocol)
    if table.digest != spec["screen_config"]["events_digest"]:
        raise OutcomeAccessRefused("event table differs from the screened one")
    market = ev.MarketData(vendor, grant, "holdout")
    seed = int(protocol["inference"]["bootstrap_seed"])
    n_trials = max(int(request["multiplicity"]["n_trials_for_dsr"]),
                   ho.n_trials_for_dsr(sealed, ho.TrialLedger(fw).records()))
    rules = criteria(protocol)
    stats: dict[str, dict] = {}
    details: dict[str, dict] = {}
    for v in request["finalists"]:
        evaluation = ev.evaluate_variant(sealed=sealed, variant_id=v, table=table, market=market,
                                         context=context)
        net = evaluation["series"]["r_ex"]["net"]
        tests = finalist_statistics(net, protocol, seed)
        disc = spec["discovery_stats"][v]
        dsr = inf.deflated_sharpe(sr=disc["sr"], n_obs=disc["n"], skew=disc["skew"],
                                  kurtosis=disc["kurtosis"], sr_variance=spec["sr_variance"],
                                  n_trials=n_trials)
        capacity = {1.0: evaluation["summary"]["net"]["alpha_annual"]}
        for m in protocol["capacity"]["multiples_of_C0"]:
            if float(m) != 1.0:
                capacity[float(m)] = ev.evaluate_variant(
                    sealed=sealed, variant_id=v, table=table, market=market, context=context,
                    c0_multiple=float(m), scenarios=("net",))["summary"]["net"]["alpha_annual"]
        stats[v] = {"alpha_annual": evaluation["summary"]["net"]["alpha_annual"],
                    "pnl_usd": evaluation["summary"]["net"]["pnl_usd"],
                    "p_bootstrap": tests["bootstrap"]["p_value"], "p_hac": tests["hac"]["p_value"],
                    "dsr": dsr["dsr"], "upper_bound_annual": tests["upper_bound_annual"]}
        robustness = []
        for s in protocol["inference"]["seed_robustness"]["seeds"]:
            alt = ev.evaluate_variant(sealed=sealed, variant_id=v, table=table, market=market,
                                      context=context, seed=int(s), scenarios=("net",))
            alt_tests = finalist_statistics(alt["series"]["r_ex"]["net"], protocol, int(s))
            robustness.append({"seed": int(s), "admitted_digest": alt["admitted_digest"],
                               "alpha_annual": alt["summary"]["net"]["alpha_annual"],
                               "p_bootstrap": alt_tests["bootstrap"]["p_value"],
                               "p_hac": alt_tests["hac"]["p_value"],
                               "upper_bound_annual": alt_tests["upper_bound_annual"]})
        details[v] = {"fingerprint": evaluation["fingerprint"],
                      "output_digest": evaluation["output_digest"],
                      "counts": evaluation["counts"], "exits": evaluation["exits"],
                      "delisting_classes": evaluation["delisting_classes"],
                      "idle_cash": evaluation["idle_cash"],
                      "bootstrap": tests["bootstrap"], "hac": tests["hac"], "dsr": dsr,
                      "stress": stress_report(evaluation["summary"]),
                      "capacity": capacity_report(capacity),
                      "seed_robustness": {"gating": False, "runs": robustness}}
    decision = decide(stats, context.attestation, rules)
    result = sanitize({
        "schema": SCHEMA, "lineage": LINEAGE_ID, "kind": "HOLDOUT_ONE_LOOK_RESULT",
        "prereg_sha256": sealed["protocol_sha256"], "request_id": request["request_id"],
        "eval_spec_digest": spec_digest, "n_trials_for_dsr": n_trials, "criteria": rules,
        "finalist_statistics": stats, "finalists": details, "decision": decision,
        "data_quality": dict(sorted(market.quality.items())),
    })
    _write_once(fw, result_path(fw), result)
    return result


def sanitize(obj: Any) -> Any:
    """JSON-safe copy: non-finite floats become strings (canonical JSON forbids NaN/inf)."""
    if isinstance(obj, float):
        return obj if obj == obj and obj not in (float("inf"), float("-inf")) else repr(obj)
    if isinstance(obj, Mapping):
        return {str(k): sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]
    return obj


def _write_once(fw: Firewall, path, obj: Mapping[str, Any]) -> None:
    payload = canonical_json(obj) + b"\n"
    if path.exists():
        if path.read_bytes() != payload:
            raise ho.HoldoutAlreadyConsumed(f"{path.name} already holds a different result")
        return
    fw.create_exclusive(path, payload)
