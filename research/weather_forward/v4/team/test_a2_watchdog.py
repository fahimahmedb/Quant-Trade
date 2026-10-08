"""Tests deterministes du garde-fou A2 (commentaires synthetiques, aucun reseau)."""
import importlib.util
from datetime import datetime, timezone
import pathlib
import unittest

spec = importlib.util.spec_from_file_location("wd", pathlib.Path(__file__).with_name("a2_watchdog.py"))
wd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wd)
NOW = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)


def c(cid, at, sender, target, extra="", demande="faire x"):
    return {"id": cid, "created_at": f"2026-10-08T{at}:00Z",
            "body": f"[A2-TEAM] DE: {sender} → À: {target}\nOBJET: x\nDEMANDE: {demande}\n{extra}"}


class Watchdog(unittest.TestCase):
    def test_overdue_wait_on_codex_pings_codex(self):
        a = wd.evaluate([c(1, "08:00", "builder", "orchestrateur", "ATTENTE: arbitrage avant 2026-10-08T09:00Z")], NOW, False)
        self.assertEqual(len(a), 1)
        self.assertIn("PING_CODEX", a[0])

    def test_answered_wait_is_closed(self):
        a = wd.evaluate([c(1, "08:00", "builder", "orchestrateur", "ATTENTE: x avant 2026-10-08T09:00Z"),
                         c(2, "08:30", "orchestrateur", "builder", demande="aucune")], NOW, False)
        self.assertEqual(a, [])

    def test_wait_not_yet_due_is_silent(self):
        a = wd.evaluate([c(1, "11:30", "builder", "orchestrateur", "ATTENTE: x avant 2026-10-08T13:00Z")], NOW, False)
        self.assertEqual(a, [])

    def test_overdue_wait_on_builder_wakes_builder(self):
        a = wd.evaluate([c(1, "08:00", "orchestrateur", "builder", "ATTENTE: contre-lecture avant 2026-10-08T09:00Z")], NOW, False)
        self.assertEqual(len(a), 1)
        self.assertIn("WAKE_BUILDER", a[0])

    def test_unanswered_request_without_deadline_after_3h(self):
        a = wd.evaluate([c(1, "08:00", "builder", "orchestrateur")], NOW, False)
        self.assertTrue(any("PING_CODEX" in x for x in a))
        recent = wd.evaluate([c(1, "10:30", "builder", "orchestrateur")], NOW, False)
        self.assertEqual(recent, [])

    def test_no_duplicate_ping_for_same_agent(self):
        a = wd.evaluate([c(1, "06:00", "builder", "orchestrateur", "ATTENTE: x avant 2026-10-08T07:00Z"),
                         c(2, "06:30", "builder", "orchestrateur")], NOW, False)
        self.assertEqual(len([x for x in a if "PING_CODEX" in x]), len(a) - len([x for x in a if "ALERT" in x]))

    def test_team_silent_with_open_work_alerts_owner(self):
        a = wd.evaluate([c(1, "04:00", "builder", "orchestrateur"), c(2, "04:10", "orchestrateur", "builder", demande="aucune")], NOW, True)
        self.assertTrue(any("ALERT_OWNER" in x for x in a))
        self.assertFalse(any("ALERT_OWNER" in x for x in wd.evaluate(
            [c(1, "04:00", "builder", "orchestrateur"), c(2, "04:10", "orchestrateur", "builder", demande="aucune")], NOW, False)))

    def test_reply_with_no_request_does_not_wake_the_other_side(self):
        a = wd.evaluate([c(1, "04:00", "builder", "orchestrateur"), c(2, "04:10", "orchestrateur", "builder", demande="aucune")],
                        NOW, False)
        self.assertFalse(any("WAKE_BUILDER" in x for x in a))

    def test_non_team_and_malformed_comments_are_ignored(self):
        junk = [{"id": 1, "created_at": "2026-10-08T01:00:00Z", "body": "Je ratifie"},
                {"id": 2, "created_at": "2026-10-08T01:00:00Z", "body": "[A2-TEAM] DE: owner → À: builder\nATTENTE: x avant 2026-10-08T02:00Z"}]
        self.assertEqual(wd.evaluate(junk, NOW, False), [])

    def test_ascii_arrow_and_two_targets(self):
        body = {"id": 9, "created_at": "2026-10-08T06:00:00Z",
                "body": "[A2-TEAM] DE: orchestrateur -> A: Owner, builder\nATTENTE: avis avant 2026-10-08T07:00Z"}
        a = wd.evaluate([body], NOW, False)
        self.assertEqual(len(a), 1)
        self.assertIn("WAKE_BUILDER", a[0])

    def test_open_work_detection(self):
        self.assertTrue(wd.open_work_in("| Q1 | x | READY |"))
        self.assertFalse(wd.open_work_in("| Q1 | x | DONE |\n| Q2 | y | OWNER_GATED |\n| Q3 | z | BLOCKED |"))


if __name__ == "__main__":
    unittest.main()
