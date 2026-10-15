from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import re
from urllib.parse import urlparse

from research.research_os.scientific_store import sha256_json
from research.research_os.engines.protocol import EngineContractError, build_candidate


DOCUMENT_FACTS = {
    "FUNDAMENTAL": {"revenue", "operating_income", "operating_cash_flow", "capital_expenditure"},
    "EVENT_DOCUMENT": {"previous_low", "previous_high", "current_low", "current_high"},
    "QUANT_MECHANISM": {"constrained_quantity", "eligible_quantity"},
    "INSTITUTIONAL_FLOW": {"constrained_quantity", "eligible_quantity"},
    "EDGE_ARCHAEOLOGY": {"constrained_quantity", "eligible_quantity"},
}


def _clock(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("document clocks must include a timezone")
    return parsed


def qualify_document_packet(packet: Dict[str, Any], family: str, freeze_time: str) -> Dict[str, Any]:
    """Qualify an outcome-free structured input, not a live source connector.

    Documentary mode is limited to qualified captured primary accounting cells
    and declared distribution announcement excerpts. It does not authorize market outcomes or a source network.
    """
    required = {"evidence_class", "source_ref", "issuer_id", "published_at", "available_at",
                "revision_status", "period", "unit", "facts", "content_hash"}
    constraint_fields = {"actor", "constraint", "instrument", "horizon"}
    optional = constraint_fields | {"capture", "event_kind", "rule_kind"}
    blockers = []
    if required - packet.keys() or packet.keys() - required - optional:
        blockers.append("DOCUMENT_FIELDS_INVALID")
    documentary = packet.get('evidence_class') == 'DOCUMENTARY'
    if not documentary and (packet.get("evidence_class") != "SYNTHETIC" or not str(packet.get("source_ref", "")).startswith("synthetic://")):
        blockers.append("DOCUMENT_CLASS_OUTSIDE_STABLE_ENGINE_CONTRACT")
    event_distribution = documentary and family == 'EVENT_DOCUMENT'
    settlement_constraint = documentary and family == 'INSTITUTIONAL_FLOW'
    if settlement_constraint:
        try:
            from .source_adapters_v1 import sec_t1_packet
            if packet != sec_t1_packet(packet['capture']):
                raise ValueError('rule explanation differs from captured facts')
        except (KeyError, ValueError, TypeError, AttributeError, InvalidOperation):
            blockers.append('DOCUMENT_CAPTURE_NOT_QUALIFIED')
    elif event_distribution:
        try:
            from .source_adapters_v1 import apple_dividend_packet
            expected = apple_dividend_packet(packet['capture']['records'])
            if packet != expected:
                raise ValueError('event facts or metadata differ from captured declarations')
        except (KeyError, ValueError, TypeError, AttributeError, InvalidOperation):
            blockers.append('DOCUMENT_CAPTURE_NOT_QUALIFIED')
    elif documentary:
        capture = packet.get('capture') or {}
        try:
            capture_fields = {'source_url','retrieved_at','publication_clock_basis','raw_sha256','representation',
                              'extractor','period','unit','text','text_sha256','fact_spans'}
            if set(capture) != capture_fields:
                raise ValueError('capture fields invalid')
            if family != 'FUNDAMENTAL':
                raise ValueError('only the Fundamental documentary adapter is qualified')
            locator = urlparse(packet['source_ref'])
            if locator.scheme != 'https' or locator.hostname != 'www.apple.com' or not locator.path.startswith('/newsroom/pdfs/'):
                raise ValueError('primary provider not qualified')
            if capture['representation'] != 'NUMERIC_CELLS' or capture['source_url'] != packet['source_ref']:
                raise ValueError('capture representation invalid')
            if not re.fullmatch('[0-9a-f]{64}', capture['raw_sha256']):
                raise ValueError('raw PDF digest missing')
            if capture['period'] != packet['period'] or capture['unit'] != packet['unit']:
                raise ValueError('capture period/unit mismatch')
            if capture['period'] != 'FY2025_TWELVE_MONTHS_ENDED_2025-09-27' or capture['unit'] != 'USD_millions':
                raise ValueError('provider basis not qualified')
            if capture['publication_clock_basis'] != 'FIRST_VERIFIED_PUBLIC_CAPTURE_NOT_HISTORICAL_PIT':
                raise ValueError('publication clock basis not qualified')
            if capture['extractor'] != 'apple-statement-cells.v1/pdftotext-layout':
                raise ValueError('extractor not qualified')
            lines = capture['text'].splitlines()
            if len(lines) != 4 or {line.split('=')[0] for line in lines} != DOCUMENT_FACTS[family] or any(
                    not re.fullmatch(r'[a-z_]+=-?\d+(?:\.\d+)?', line) for line in lines):
                raise ValueError('only declared numeric accounting cells are admissible')
            if capture['text_sha256'] != hashlib.sha256(capture['text'].encode()).hexdigest():
                raise ValueError('numeric capture hash mismatch')
            if set(capture['fact_spans']) != DOCUMENT_FACTS[family]:
                raise ValueError('numeric capture spans missing')
            for key, span in capture['fact_spans'].items():
                if set(span) != {'start','end','page','column','normalization'} or span['column'] != 'FY2025_TWELVE_MONTHS':
                    raise ValueError('capture column not qualified')
                if span['page'] != (1 if key in {'revenue','operating_income'} else 3):
                    raise ValueError('capture statement page not qualified')
                if type(span['start']) is not int or type(span['end']) is not int or not 0 <= span['start'] < span['end'] <= len(capture['text']):
                    raise ValueError('invalid numeric capture span')
                literal = capture['text'][span['start']:span['end']].replace(',', '')
                value = Decimal(literal)
                if span.get('normalization') == 'OUTFLOW_MAGNITUDE':
                    value = abs(value)
                elif span.get('normalization') != 'AS_REPORTED':
                    raise ValueError('unknown numeric normalization')
                if value != Decimal(str(packet['facts'][key])):
                    raise ValueError('fact not bound to captured numeric cell')
            if not _clock(capture['retrieved_at']) <= _clock(packet['available_at']):
                raise ValueError('capture occurred after claimed availability')
        except (KeyError, ValueError, TypeError, AttributeError, InvalidOperation):
            blockers.append('DOCUMENT_CAPTURE_NOT_QUALIFIED')
    expected_revision = 'CAPTURED_VERSION_AS_OF_RETRIEVAL' if documentary else 'ORIGINAL_AS_PUBLISHED'
    if packet.get("revision_status") != expected_revision:
        blockers.append("DOCUMENT_REVISION_NOT_QUALIFIED")
    for field in ("issuer_id", "period", "unit"):
        if not isinstance(packet.get(field), str) or not packet[field].strip() or packet[field] == "UNKNOWN":
            blockers.append(f"DOCUMENT_{field.upper()}_MISSING")
    payload = {k: v for k, v in packet.items() if k != "content_hash"}
    if packet.get("content_hash") != sha256_json(payload):
        blockers.append("DOCUMENT_HASH_MISMATCH")
    try:
        published, available, freeze = (_clock(v) for v in (packet["published_at"], packet["available_at"], freeze_time))
        if not published <= available <= freeze:
            blockers.append("DOCUMENT_CLOCK_NOT_PIT")
    except (KeyError, TypeError, ValueError, AttributeError):
        blockers.append("DOCUMENT_CLOCK_INVALID")
    facts = packet.get("facts", {})
    required_facts = ({"previous_distribution", "current_distribution"} if event_distribution
                      else {"standard_settlement_business_days"} if settlement_constraint
                      else DOCUMENT_FACTS.get(family))
    if not event_distribution and "event_kind" in packet:
        blockers.append("DOCUMENT_EVENT_KIND_NOT_QUALIFIED")
    if not settlement_constraint and "rule_kind" in packet:
        blockers.append("DOCUMENT_RULE_KIND_NOT_QUALIFIED")
    if required_facts is None or not isinstance(facts, dict) or set(facts) != required_facts:
        blockers.append("DOCUMENT_FACTS_INVALID")
    else:
        try:
            values = {k: Decimal(str(v)) for k, v in facts.items()}
            if not all(v.is_finite() for v in values.values()):
                raise ValueError("nonfinite fact")
            if family == "FUNDAMENTAL":
                if values["revenue"] <= 0 or values["capital_expenditure"] < 0:
                    raise ValueError("invalid statement magnitude")
            elif settlement_constraint:
                if values["standard_settlement_business_days"] != 1:
                    raise ValueError("unqualified settlement standard")
            elif event_distribution:
                if any(v <= 0 for v in values.values()):
                    raise ValueError("invalid distribution magnitude")
            elif family == "EVENT_DOCUMENT":
                if any(values[f"{p}_low"] > values[f"{p}_high"] for p in ("previous", "current")):
                    raise ValueError("inverted guidance interval")
            else:
                if not 0 <= values["constrained_quantity"] <= values["eligible_quantity"] or values["eligible_quantity"] <= 0:
                    raise ValueError("invalid eligible population")
                if packet.get("unit") != "units":
                    raise ValueError("population units must be units")
                if any(not isinstance(packet.get(k), str) or not packet[k].strip() for k in constraint_fields):
                    raise ValueError("missing constraint identity")
        except (InvalidOperation, ValueError):
            blockers.append("DOCUMENT_FACT_VALUES_INVALID")
    return {"status": "BLOCK" if blockers else "PASS", "blockers": sorted(set(blockers)),
            "source_hash": packet.get("content_hash"), "evidence_class": packet.get('evidence_class'),
            "outcome_accessed": False}


def documentary_candidate(engine: Any, source: Dict[str, Any], context: Any, hypothesis_id: str) -> Dict[str, Any]:
    packet = source["documentary_packet"]
    if context.synthetic_only != (packet.get('evidence_class') == 'SYNTHETIC'):
        raise EngineContractError('source evidence class does not match the execution context')
    freeze = source["freeze_time"]
    qualification = qualify_document_packet(packet, engine.family, freeze)
    if qualification["status"] != "PASS":
        raise EngineContractError(",".join(qualification["blockers"]))
    facts = {k: Decimal(str(v)) for k, v in packet["facts"].items()}
    issuer, period, unit = (packet[k] for k in ("issuer_id", "period", "unit"))
    if engine.family == "FUNDAMENTAL":
        margin = facts["operating_income"] / facts["revenue"]
        fcf = facts["operating_cash_flow"] - facts["capital_expenditure"]
        measurements = {"operating_margin": str(margin), "free_cash_flow": str(fcf)}
        mechanism = "Cash generation and operating profitability may support a valuation thesis; market pricing remains untested."
        claim = f"{issuer} {period}: operating margin={margin}; free cash flow={fcf} {unit}."
        disconfirm = "Withdraw the profitability premise if an admissible same-basis statement shows nonpositive margin or free cash flow."
        tags, horizon = ["quality", "cash_flow", "equity_beta"], "2q"
    elif engine.family == "EVENT_DOCUMENT" and packet.get('event_kind') == 'DECLARED_CASH_DISTRIBUTION_COMPARISON':
        before, after = facts['previous_distribution'], facts['current_distribution']
        delta = after - before
        measurements = {'previous_declared_distribution':str(before), 'current_declared_distribution':str(after),
                        'year_over_year_declared_change':str(delta),
                        'year_over_year_declared_change_fraction':str(delta / before)}
        mechanism = ('A change in declared cash distributions may motivate a capital-return thesis; '
                     'payer, expectations, consensus surprise and market response remain unqualified.')
        claim = (f'{issuer} {period}: declared distribution changed from {before} to {after} {unit}; '
                 f'year-over-year difference={delta}. This compares annual Q2 announcements, '
                 'not consecutive payments; historical PIT, consensus surprise and price effect are not established.')
        disconfirm = ('Withdraw the distribution-change premise if either declaration is corrected or superseded, '
                     'or issuer, cash-versus-special classification, per-share basis, currency or annual Q2 comparison differ. '
                     'Reject a positive-change premise if the comparable declared difference is nonpositive. '
                     'Payment receipt, eligibility, tradable horizon and economic payoff are untested.')
        tags, horizon = ['declared_distribution', 'capital_return', 'equity_beta'], 'UNQUALIFIED'
    elif engine.family == "EVENT_DOCUMENT":
        before = (facts["previous_low"] + facts["previous_high"]) / 2
        after = (facts["current_low"] + facts["current_high"]) / 2
        delta = after - before
        measurements = {"previous_midpoint": str(before), "current_midpoint": str(after), "guidance_change": str(delta)}
        mechanism = "A same-period guidance change may alter expectations; consensus surprise and price response remain untested."
        claim = f"{issuer} {period}: guidance midpoint changed by {delta} {unit}, from {before} to {after}."
        disconfirm = "Withdraw the revision premise if the document is corrected, superseded, or the periods/units differ."
        tags, horizon = ["guidance_revision", "information_processing", "equity_beta"], "1-20d"
    elif engine.family == "INSTITUTIONAL_FLOW" and packet.get('rule_kind') == 'STANDARD_SETTLEMENT_CONSTRAINT_EXPLANATION':
        measurements = {'standard_settlement_business_days':str(facts['standard_settlement_business_days']),
                        'constrained_share':'UNKNOWN', 'directional_flow':'UNKNOWN'}
        mechanism = (f"{packet['actor']} face a settlement deadline for covered transactions; "
                     "this may motivate a funding or processing-constraint thesis, not an inferred forced buy or sale.")
        claim = (f"SEC staff FAQ explains a standard T+1 settlement constraint for covered transactions; "
                 "exemptions and agreed extensions require applicability review. The FAQ is nonbinding; "
                 "no eligible quantity, actual funding pressure, current legal opinion or economic payoff is established.")
        disconfirm = ('Reject the constraint premise for an exempt transaction, a valid agreed extension, '
                     'a superseding rule, or an actor outside scope. Reject a directional-flow thesis without '
                     'independent evidence of binding funding pressure, an eligible instrument and implementation costs. '
                     'Prior closed research families remain closed.')
        tags, horizon = ['settlement_constraint', 'funding', 'liquidity'], 'UNQUALIFIED'
    else:
        share = facts["constrained_quantity"] / facts["eligible_quantity"]
        measurements = {"constrained_share": str(share)}
        mechanism = f"{packet['actor']} faces {packet['constraint']} in {packet['instrument']}; pressure/reversal remains untested."
        claim = f"{issuer} {period}: declared constrained share={share} of {facts['eligible_quantity']} units."
        disconfirm = "Reject if the actor is not constrained, the universe is ineligible, or the legacy family has already spent this scope."
        tags, horizon = ["forced_flow", "liquidity", "constraint"], packet["horizon"]
    if not context.synthetic_only:
        prefix = {'EVENT_DOCUMENT':'DOC-EVENT-', 'INSTITUTIONAL_FLOW':'DOC-FLOW-', 'FUNDAMENTAL':'DOC-FUND-'}[engine.family]
        hypothesis_id = prefix + packet['content_hash'][:16]
    evidence = {
        "packet": deepcopy(packet), "freeze_time": freeze, "measurements": measurements,
        "claim_source_hash": packet["content_hash"], "economic_result": "NOT_OBSERVED",
    }
    output = build_candidate(
        engine_id=engine.engine_id, engine_family=engine.family, hypothesis_id=hypothesis_id,
        mechanism=mechanism, claim=claim, falsification_scope=disconfirm,
        decision_map={"premise_survives": "EXPLORE", "premise_fails": "KILL_GENERATION"},
        economic_tags=tags, source_refs=([r["source_url"] for r in packet["capture"]["records"]]
                                        if packet.get("event_kind") == "DECLARED_CASH_DISTRIBUTION_COMPARISON"
                                        else [packet["source_ref"]]), horizon=horizon, context=context,
        documentary_evidence=evidence,
    )
    return output


REQUIRED_BY_FAMILY = {
    "QUANT_MECHANISM": {
        "trigger",
        "payer_or_forced_actor",
        "structural_reason",
        "expression",
        "universe_definition",
        "confounders",
        "disconfirmation_checks",
    },
    "FUNDAMENTAL": {
        "issuer_identity",
        "financial_statements",
        "earnings_and_guidance",
        "estimate_revisions",
        "valuation_frame",
        "balance_sheet_quality",
        "cash_flow_quality",
        "competitive_position",
        "catalysts",
        "disconfirmation_checks",
    },
    "EVENT_DOCUMENT": {
        "event_identity",
        "document_clock",
        "eligibility_rule",
        "novel_information",
        "diffusion_hypothesis",
        "confounders",
        "disconfirmation_checks",
    },
    "INSTITUTIONAL_FLOW": {
        "forced_actor",
        "constraint_rule",
        "implementation_clock",
        "affected_universe",
        "expected_footprint",
        "capacity_constraints",
        "confounders",
        "disconfirmation_checks",
    },
}


def build_engine_dossier(output: Dict[str, Any], detail_input: Dict[str, Any]) -> Dict[str, Any]:
    family = output["engine_family"]
    if family not in REQUIRED_BY_FAMILY:
        raise ValueError(f"unsupported deep-dossier family: {family}")
    candidate = output["candidate"]
    required = REQUIRED_BY_FAMILY[family]
    missing = sorted(field for field in required if detail_input.get(field) in (None, "", [], {}))
    blockers: List[str] = [f"MISSING_{field.upper()}" for field in missing]
    if detail_input.get("outcome_accessed") is not False:
        blockers.append("OUTCOME_ACCESS_NOT_ALLOWED")
    if detail_input.get("source_clock_frozen") is not True:
        blockers.append("SOURCE_CLOCK_NOT_FROZEN")
    if detail_input.get("active_disconfirmation") is not True:
        blockers.append("ACTIVE_DISCONFIRMATION_MISSING")

    dossier = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "engine_id": output["engine_id"],
        "engine_family": family,
        "mechanism": candidate["mechanism"],
        "claim": candidate["claim"],
        "falsification_scope": candidate["falsification_scope"],
        "horizon": candidate.get("horizon"),
        "source_refs": list(output.get("source_refs") or []),
        "dossier": deepcopy(detail_input),
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": blockers,
        "candidate_mutated": False,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
    }
    return dossier


def build_engine_dossiers(
    outputs: Iterable[Dict[str, Any]],
    detail_by_hypothesis: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    for output in outputs:
        family = output["engine_family"]
        if family not in REQUIRED_BY_FAMILY:
            continue
        hid = output["candidate"]["hypothesis_id"]
        records.append(build_engine_dossier(output, detail_by_hypothesis[hid]))
    return {
        "engine_depth_version": "engine-dossiers.v1",
        "record_count": len(records),
        "records": records,
        "pass_count": sum(item["status"] == "PASS" for item in records),
        "block_count": sum(item["status"] != "PASS" for item in records),
        "economic_results_observed": 0,
        "candidate_mutations": 0,
    }
