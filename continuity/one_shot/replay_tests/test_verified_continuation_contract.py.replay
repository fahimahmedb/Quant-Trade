import unittest

from research.research_os.continuation import (
    ContinuationContractError, reopen_event, validate_closure, validate_obligations,
)


class VerifiedContinuationContractTests(unittest.TestCase):
    def obligation(self, oid="O-1"):
        return {"OBLIGATION_ID": oid, "PARENT_OBJECT_ID": "P-1", "OWNER": "CONTROL_PLANE_ORACLE"}

    def block(self, oid="O-1"):
        return {
            "CLOSURE_TYPE": "BLOCK",
            "OBLIGATION_ID": oid,
            "PARENT_OBJECT_ID": "P-1",
            "OWNER": "CONTROL_PLANE_ORACLE",
            "REASON_CODE": "AUTHORITY_UNRESOLVED",
            "CLAIM_SCOPE": "FROZEN_PRE_OUTCOME_SCREEN_ONLY",
            "MISSING_CONDITION": "NORMATIVE_AUTHORITY_PRECEDENCE_OR_REVOCATION_RULE",
            "OBSERVABLE_REOPEN_PREDICATE": "repository-committed applicable authority resolution",
            "AUTHORITY_SCOPE": "BOUNDED_ECONOMIC_OUTCOME_ACCESS",
            "DATA_SCOPE": "PROTECTED_OUTCOMES_UNOPENED",
            "SOURCE_SCOPE": "PREDECLARED_OFFICIAL_SOURCES",
            "CREATED_AT": "2026-10-26T23:33:00+01:00",
            "IDEMPOTENCY_KEY": "ust-authority-unresolved-v1",
            "HISTORICAL_DISPOSITION_MUTATED": False,
        }

    def test_every_declared_obligation_has_exactly_one_closure(self):
        proof = validate_obligations([self.obligation()], [self.block()])
        self.assertEqual(proof["declared_obligation_count"], 1)
        self.assertEqual(proof["durably_closed_obligation_count"], 1)
        self.assertFalse(proof["silent_obligation_loss"])
        self.assertFalse(proof["scheduler_mutation"])
        self.assertFalse(proof["authority_expanded"])

    def test_multiple_independent_obligations_close_independently(self):
        terminal = {
            "CLOSURE_TYPE": "TERMINAL", "OBLIGATION_ID": "O-2", "PARENT_OBJECT_ID": "P-1",
            "IDEMPOTENCY_KEY": "terminal-o2", "TERMINAL_DISPOSITION": "NO_ACTION",
            "REASON_CODE": "NO_LAWFUL_ACTION_REQUIRED",
        }
        proof = validate_obligations(
            [self.obligation("O-1"), self.obligation("O-2")],
            [self.block("O-1"), terminal],
        )
        self.assertEqual(proof["durably_closed_obligation_count"], 2)

    def test_orphan_and_duplicate_closure_fail_closed(self):
        with self.assertRaisesRegex(ContinuationContractError, "ORPHANED"):
            validate_obligations([self.obligation()], [])
        with self.assertRaisesRegex(ContinuationContractError, "MULTIPLE"):
            validate_obligations([self.obligation()], [self.block(), self.block()])

    def test_block_requires_full_reopen_contract(self):
        broken = self.block()
        del broken["OBSERVABLE_REOPEN_PREDICATE"]
        with self.assertRaisesRegex(ContinuationContractError, "STOP_CLOSURE_FIELDS_MISSING"):
            validate_closure(broken)

    def test_reopen_is_append_only_and_binds_original_closure_hash(self):
        original = validate_closure(self.block())
        event = reopen_event(
            original,
            reopened_at="2026-10-27T12:00:00Z",
            predicate_evidence_ref="continuity/evidence/new-authority-resolution.json",
            event_id="REOPEN-O-1-001",
        )
        self.assertEqual(event["ORIGINAL_CLOSURE_HASH"], original["CLOSURE_HASH"])
        self.assertFalse(event["HISTORICAL_DISPOSITION_MUTATED"])
        self.assertEqual(original["CLOSURE_TYPE"], "BLOCK")


if __name__ == "__main__":
    unittest.main()
