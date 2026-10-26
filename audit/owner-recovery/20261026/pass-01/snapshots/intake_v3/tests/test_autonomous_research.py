import tempfile
import unittest
from pathlib import Path

import math

from autonomous_research.backtest import reversal_backtest
from autonomous_research.memory import append_ticket
from autonomous_research.ticket import ResearchTicket


class TicketTests(unittest.TestCase):
    def test_state_machine_rejects_skipped_stage(self):
        ticket = ResearchTicket(ticket_id="x", lane="test", observation="fact")
        with self.assertRaises(ValueError):
            ticket.transition("VALIDATED")

    def test_memory_is_append_only_jsonl(self):
        ticket = ResearchTicket(ticket_id="x", lane="test", observation="fact")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.jsonl"
            append_ticket(path, ticket)
            append_ticket(path, ticket)
            self.assertEqual(len(path.read_text().splitlines()), 2)


class TimingTests(unittest.TestCase):
    def test_signal_does_not_earn_same_day_return(self):
        returns = [0.0] * 100
        returns[70] = 0.20
        close = [100 * math.exp(sum(returns[:i + 1])) for i in range(100)]
        result = reversal_backtest(close, lookback=1, test_start=60, cost_bps=0)
        by_index = {row["index"]: row for row in result}
        self.assertEqual(by_index[70]["position"], 0.0)
        self.assertEqual(by_index[71]["position"], -1.0)


if __name__ == "__main__":
    unittest.main()
