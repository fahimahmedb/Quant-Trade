"""Research workers.

A worker executes one lane end to end and returns a machine-readable result the
Control Plane can act on. It always produces a lesson and a next action, so an
ordinary negative result reprioritizes the factory instead of escalating to a
human, as ``AGENTS.md`` requires.
"""

from __future__ import annotations

import sys
import hashlib
import json
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from autonomous_research.ticket import ResearchTicket  # noqa: E402

from ..dataplane.panel import PricePanel  # noqa: E402
from ..dataplane.registry import DatasetRegistry  # noqa: E402
from ..events import EventLog  # noqa: E402
from ..paths import QuantPaths  # noqa: E402
from ..state import append_jsonl, write_json  # noqa: E402
from .evaluate import falsify, summarize, walk_forward  # noqa: E402
from .lanes import BENCHMARK, COST_BPS, WINDOWS, lane_definitions  # noqa: E402
from .signals import StrategySpec  # noqa: E402
from .strategies import StrategyDefinition, StrategyRegistry  # noqa: E402


class ResearchContext:
    """Everything a worker is allowed to touch."""

    def __init__(self, paths: QuantPaths, datasets: DatasetRegistry,
                 strategies: StrategyRegistry, log: EventLog):
        self.paths = paths
        self.datasets = datasets
        self.strategies = strategies
        self.log = log


def research_panel(panel: PricePanel, universe: list[str]) -> tuple[PricePanel, dict[str, Any]]:
    """The view research is allowed to see: everything up to the shadow boundary.

    Truncation happens here, once, so no worker can reach the desk's reserved
    window even by accident.
    """
    windows = panel.split(WINDOWS, symbols=universe)
    visible = panel.restrict(end=windows["VALIDATION"].end)
    return visible, {name: window.to_dict() for name, window in windows.items()}


def run_lane(context: ResearchContext, lane_name: str, universe: list[str],
             dataset_id: str) -> dict[str, Any]:
    """Scan, filter, hypothesize, test, falsify, register, learn."""
    record = context.datasets.get(dataset_id)
    if record is None or record.availability != "AVAILABLE":
        return {"status": "BLOCKED", "reason": f"dataset {dataset_id} is not available",
                "lesson": None, "next_action_hint": f"ingest or repair {dataset_id}"}

    definition = lane_definitions(universe, dataset_id)[lane_name]
    panel = PricePanel.load(context.paths.root / record.path)
    declared = panel.split(WINDOWS, symbols=universe)
    frozen = context.strategies.preserve_research_partition(dataset_id, declared)
    from ..dataplane.panel import Window
    partition = {name: Window(**value) for name, value in frozen.items()}
    discovery, validation = partition["DISCOVERY"], partition["VALIDATION"]
    visible = panel.restrict(end=validation.end)
    windows = frozen
    cohort_rows = [dict(bar) for (date, symbol), bar in sorted(visible.bars.items())
                   if date <= validation.end and symbol in universe]
    cohort_key = context.strategies.preserve_research_cohort(dataset_id, cohort_rows)
    dataset_key = f"{dataset_id}@{cohort_key}"

    ticket = ResearchTicket(
        ticket_id=f"{lane_name.upper().replace('_', '-')}-{record.fingerprint[7:15]}",
        lane=definition["lane"], market="US sector ETFs",
        instruments=list(universe),
        observation=definition["question"],
        observed_at=validation.end,
        information_available_at=validation.end + "T21:00:00Z",
        source_refs=[record.path, record.fingerprint or ""])
    ticket.candidate_data = {"expressions_declared": len(definition["grid"]),
                             "windows": windows, "benchmark": BENCHMARK,
                             "cost_bps_one_way": COST_BPS}

    # --- SCAN + FILTER on the discovery window only -----------------------
    scanned = []
    for spec in definition["grid"]:
        rows = walk_forward(visible, spec, discovery, COST_BPS)
        summary = summarize(rows, visible, BENCHMARK, COST_BPS)
        scanned.append({"expression": spec.label, "spec": spec.to_dict(),
                        "discovery": {key: summary.get(key) for key in
                                      ("net_return", "gross_return", "sharpe_zero_rate",
                                       "market_beta", "annual_turnover", "t_statistic",
                                       "observations")}})
    scanned.sort(key=lambda item: item["discovery"]["sharpe_zero_rate"], reverse=True)
    # Lane-level diagnosis, taken from the whole grid rather than one expression:
    # does this family of signals earn something before frictions and lose it to
    # them? That is a statement about implementation, and it is what justifies
    # promoting a lower-turnover successor rather than re-rolling parameters.
    cost_dominated = [item for item in scanned
                      if item["discovery"]["gross_return"] > 0 >= item["discovery"]["net_return"]]
    turnovers = sorted(item["discovery"]["annual_turnover"] for item in scanned)
    median_turnover = turnovers[len(turnovers) // 2] if turnovers else 0.0
    cost_diagnosis = {
        "expressions_gross_positive_but_net_negative": len(cost_dominated),
        "median_annual_turnover": median_turnover,
        "cost_is_binding_constraint": bool(cost_dominated) and median_turnover > 50.0}
    grid_document = [spec.to_dict() for spec in definition["grid"]]
    grid_hash = hashlib.sha256(json.dumps(grid_document, sort_keys=True).encode()).hexdigest()
    experiment_key = f"{dataset_key}:{lane_name}:{grid_hash}"
    trials = context.strategies.record_trials(
        dataset_key, len(definition["grid"]), experiment_key=experiment_key)
    best = scanned[0]
    ticket.candidate_data["ranked_expressions"] = scanned[:5]
    ticket.candidate_data["cumulative_expressions_tested_on_dataset"] = trials
    ticket.candidate_data["cost_diagnosis"] = cost_diagnosis

    context.log.emit("RESEARCH", "RESEARCH", "lane_scanned", lane_name,
                     expressions=len(definition["grid"]), best=best["expression"],
                     best_discovery_sharpe=best["discovery"]["sharpe_zero_rate"],
                     cumulative_trials=trials)

    # The validation window is spent only on a candidate that survived discovery.
    if best["discovery"]["sharpe_zero_rate"] <= 0:
        ticket.filter_result = {"passed": False,
                                "rule": "the best discovery-window expression must have a "
                                        "positive cost-adjusted Sharpe before the "
                                        "validation window is spent on it",
                                "best_expression": best["expression"],
                                "best_discovery_sharpe": best["discovery"]["sharpe_zero_rate"]}
        ticket.transition("FILTERED")
        ticket.lesson = (f"No expression in {lane_name} survived the discovery window: the "
                         f"best reached a Sharpe of "
                         f"{best['discovery']['sharpe_zero_rate']:.2f} after costs. The "
                         f"validation window was preserved rather than spent.")
        ticket.next_action_hint = ("reduce implementation cost or change lane; this signal "
                                   "family is not merely unlucky here")
        return _finish(context, ticket, lane_name, None, dataset_id, record.fingerprint)

    ticket.filter_result = {"passed": True, "best_expression": best["expression"],
                            "best_discovery_sharpe": best["discovery"]["sharpe_zero_rate"]}
    ticket.transition("RESEARCHING")
    ticket.hypothesis = {"mechanism": definition["mechanism"],
                         "expression": best["expression"],
                         "selection_rule": "highest cost-adjusted Sharpe on the discovery "
                                           "window; selected before the validation window "
                                           "was read",
                         "benchmark": f"zero-return cash, with {BENCHMARK} beta attributed",
                         "falsification": definition["falsification"],
                         "timing": "signal formed on the close of session t; orders execute "
                                   "at the open of t+1"}

    # --- TEST on the untouched validation window --------------------------
    spec = StrategySpec(**best["spec"])
    rows = walk_forward(visible, spec, validation, COST_BPS)
    summary = summarize(rows, visible, BENCHMARK, COST_BPS)
    verdict = falsify(rows, summary, visible, BENCHMARK, spec, trials)
    ticket.test_result = summary
    ticket.validation_result = verdict

    context.log.emit("RESEARCH", "RESEARCH", "lane_validated", lane_name,
                     severity="INFO", expression=spec.label, decision=verdict["decision"],
                     failed_tests=verdict["failed_tests"],
                     t_statistic=verdict["t_statistic"],
                     required_t_statistic=verdict["required_t_statistic"],
                     net_return=summary["net_return"], market_beta=summary["market_beta"])

    if verdict["passed"]:
        ticket.transition("VALIDATED")
        ticket.lesson = (f"{spec.label} survived every declared falsification attempt on "
                         f"the untouched validation window "
                         f"({summary['net_return']:+.2%} net, beta "
                         f"{summary['market_beta']:+.3f}). Shadow evidence is now required "
                         f"before it earns full capital.")
        ticket.next_action_hint = "run the strategy in the shadow book and watch for decay"
    else:
        ticket.transition("REJECTED")
        ticket.paper_decision = {"decision": "NO_TRADE",
                                 "reason": "validation failed; capital deployment prohibited"}
        ticket.lesson = _diagnose(spec, summary, verdict)
        ticket.next_action_hint = _next_action(lane_name, summary, verdict)
    ticket.transition("LEARNED")
    return _finish(context, ticket, lane_name, (spec, summary, verdict), dataset_id,
                   record.fingerprint)


def _diagnose(spec: StrategySpec, summary: dict[str, Any], verdict: dict[str, Any]) -> str:
    """Say why it failed in mechanism terms, not just which assertion tripped."""
    gross, net = summary["gross_return"], summary["net_return"]
    costs = gross - net
    parts = [f"{spec.label} was rejected out of sample ({net:+.2%} net)."]
    if gross > 0 and net <= 0:
        parts.append(f"The signal was gross-positive ({gross:+.2%}) but "
                     f"{summary['annual_turnover']:.0f}x annual turnover cost "
                     f"{costs:.2%}, so implementation, not direction, is the binding "
                     f"constraint.")
    elif gross <= 0:
        parts.append(f"The signal was gross-negative ({gross:+.2%}), so the hypothesis "
                     f"itself is wrong here, not merely too expensive to trade.")
    if "t_statistic_survives_multiple_testing" in verdict["failed_tests"]:
        parts.append(f"Its t-statistic of {verdict['t_statistic']:.2f} is far below the "
                     f"{verdict['required_t_statistic']:.2f} required after "
                     f"{verdict['expressions_tested_on_dataset']} expressions were tried "
                     f"on this dataset, so the result is indistinguishable from search luck.")
    attribution = verdict["beta_attribution"]
    parts.append(f"Market beta was {attribution['market_beta']:+.3f} against a benchmark "
                 f"that returned {attribution['benchmark_return_same_window']:+.2%}, so "
                 f"{attribution['return_explained_by_beta']:+.2%} of the result is passive "
                 f"exposure rather than skill.")
    return " ".join(parts)


def _next_action(lane_name: str, summary: dict[str, Any], verdict: dict[str, Any]) -> str:
    if summary["gross_return"] > 0 and summary["net_return"] <= 0:
        return ("attack turnover: test the same residual with a holding period and a "
                "no-trade band before abandoning the lane")
    if lane_name == "xs_execution_aware_relative_value":
        return ("cross-sectional sector relative value is exhausted on this dataset; the "
                "next credible lane needs data this repository does not hold")
    return "move to an independent lane rather than re-rolling parameters on this evidence"


def _finish(context: ResearchContext, ticket: ResearchTicket, lane_name: str,
            outcome: tuple[StrategySpec, dict[str, Any], dict[str, Any]] | None,
            dataset_id: str, fingerprint: str | None) -> dict[str, Any]:
    """Persist the ticket, register the strategy and report to the Control Plane."""
    context.paths.research_tickets.mkdir(parents=True, exist_ok=True)
    write_json(context.paths.research_tickets / f"{ticket.ticket_id}.json", ticket.to_dict())
    append_jsonl(context.paths.research_memory, ticket.to_dict())

    strategy_id = None
    if outcome is not None:
        spec, summary, verdict = outcome
        strategy_id = f"STR-{lane_name.upper().replace('_', '-')}-{spec.label}"
        existing = context.strategies.get(strategy_id)
        definition = StrategyDefinition(
            strategy_id=strategy_id, version=(existing.version + 1) if existing else 1,
            lane=ticket.lane, spec=spec.to_dict(), hypothesis=ticket.hypothesis,
            evidence={"validation": summary, "falsification": verdict,
                      "research_ticket": ticket.ticket_id},
            dataset_id=dataset_id, dataset_fingerprint=fingerprint)
        if verdict["passed"]:
            definition.transition("VALIDATED", "survived every declared falsification test")
            definition.transition("SHADOW", "evidence accepted; shadow track record required "
                                            "before full capital")
        else:
            # Not tradable. It goes on the evaluation track so the system can find
            # out whether rejecting it was right, which is the false-reject
            # measurement the North Star asks for.
            definition.evaluation_track = True
        context.strategies.upsert(definition)
        context.log.emit("RESEARCH", "RESEARCH", "strategy_registered", strategy_id,
                         lifecycle=definition.lifecycle,
                         evaluation_track=definition.evaluation_track)
    diagnosis = ticket.candidate_data.get("cost_diagnosis", {})
    return {"ticket_id": ticket.ticket_id, "status": ticket.status,
            "outcome": ticket.validation_result.get("decision", ticket.status),
            "strategy_id": strategy_id, "lesson": ticket.lesson,
            "next_action_hint": ticket.next_action_hint,
            # Lane-level: this family earns before frictions and loses to them. The
            # Control Plane uses it to decide whether attacking turnover is a
            # justified follow-up or merely another roll of the same dice.
            "cost_bound": bool(diagnosis.get("cost_is_binding_constraint")),
            "cost_diagnosis": diagnosis}
