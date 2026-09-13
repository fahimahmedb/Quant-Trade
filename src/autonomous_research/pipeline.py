"""One complete, reproducible autonomous discovery vertical slice."""

from __future__ import annotations

import hashlib
import json
import csv
from datetime import datetime
from pathlib import Path

from .backtest import metrics, reversal_backtest, validate
from .memory import append_ticket
from .scanner import scan_lag_dependence
from .ticket import ResearchTicket


def run_discovery_cycle(data_path: Path, output_dir: Path, memory_path: Path) -> ResearchTicket:
    with data_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    observations = sorted(((datetime.strptime(row["date"], "%d/%m/%Y %H:%M"), float(row["clot"]))
                           for row in rows), key=lambda item: item[0])
    dates, close = zip(*observations)
    close = list(close)
    scan = scan_lag_dependence(close)
    selected = scan["selected"]
    fingerprint = hashlib.sha256(data_path.read_bytes()).hexdigest()
    ticket = ResearchTicket(
        ticket_id="TSR-NDX-001", lane="time_series_relative_value",
        market="NASDAQ Composite index", instruments=["NASDAQ Composite (research proxy)"],
        observation=(f"Discovery-sample lag dependence is {selected['correlation']:+.4f} "
                     f"at {selected['lookback_days']} trading-day lookback."),
        observed_at=dates[-1].date().isoformat(),
        information_available_at=dates[-1].date().isoformat() + "T23:59:59Z",
        source_refs=[str(data_path), f"sha256:{fingerprint}"], candidate_data=scan)
    # Cheap materiality gate, fixed before the deep test.
    passes = abs(selected["correlation"]) >= 0.03
    ticket.filter_result = {"passed": passes, "minimum_absolute_correlation": 0.03}
    if not passes:
        ticket.transition("FILTERED")
        ticket.lesson = "Dependence was too small to justify a deeper test."
        ticket.next_action_hint = "Scan a cross-sectional relative-value universe."
        ticket.transition("LEARNED")
    else:
        ticket.transition("RESEARCHING")
        lookback = selected["lookback_days"]
        ticket.hypothesis = {
            "mechanism": "Liquidity demand and investor overreaction may cause extreme short-horizon moves to reverse.",
            "expression": "Contrarian +/-1 position after a trailing move beyond one expanding standard deviation.",
            "expected_horizon_days": 1,
            "benchmark": "zero-return cash and explicit market-beta attribution",
            "falsification": "Reject unless net profitable at 5 and 10 bps, profitable in both OOS halves, unconcentrated, and |beta| < 0.25.",
            "timing": "Signal formed with close t information; position earns close t to close t+1 return.",
        }
        test_start = scan["discovery_observations"] + 1
        tested = reversal_backtest(close, lookback, test_start, cost_bps=5.0)
        result = metrics(tested)
        result.update({"test_start": dates[tested[0]["index"]].date().isoformat(),
                       "test_end": dates[tested[-1]["index"]].date().isoformat(), "cost_bps": 5.0})
        ticket.test_result = result
        ticket.validation_result = validate(tested, result)
        if ticket.validation_result["passed"]:
            ticket.transition("VALIDATED")
            ticket.paper_decision = {"decision": "PAPER_ACCEPT", "reason": "All predeclared checks passed."}
            ticket.lesson = "The fixed contrarian expression survived its first adversarial checks; shadow evidence is now required."
            ticket.next_action_hint = "Begin timestamped shadow decisions and track accepted versus rejected signals."
        else:
            ticket.transition("REJECTED")
            ticket.paper_decision = {"decision": "NO_TRADE", "reason": "Historical validation failed; paper deployment is prohibited."}
            failed = [name for name, passed in ticket.validation_result["tests"].items() if not passed]
            ticket.lesson = "Fixed short-horizon reversal failed: " + ", ".join(failed) + "."
            ticket.next_action_hint = "Acquire or construct a compact cross-sectional ETF universe for beta-neutral relative-value scanning."
        ticket.transition("LEARNED")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ticket.ticket_id}.json").write_text(
        json.dumps(ticket.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_ticket(memory_path, ticket)
    return ticket
