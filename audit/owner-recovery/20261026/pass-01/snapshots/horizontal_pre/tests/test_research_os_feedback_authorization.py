"""Future metadata release requires literal policy/closure grants, never truthiness."""
import unittest

from research.research_os.expansion.v2_core import V2ContractError, release_feedback


class FeedbackAuthorizationTests(unittest.TestCase):
    def parameters(self):
        return dict(source_epoch_id="E1", successor_epoch_id="E2", source_epoch_closed=True,
                    policy_allows_release=True, feedback_hash="metadata-only-reference")

    def test_truthy_or_missing_policy_and_closure_are_not_authorization(self):
        for key, code in (("source_epoch_closed", "FEEDBACK_BEFORE_EPOCH_CLOSE"),
                          ("policy_allows_release", "FEEDBACK_RELEASE_NOT_AUTHORIZED_BY_POLICY")):
            for value in (False, None, "false", "true", 0, 1, [], {}, [True], {"allowed": True}):
                with self.subTest(field=key, value=value):
                    params = self.parameters()
                    params[key] = value
                    with self.assertRaisesRegex(V2ContractError, code):
                        release_feedback(**params)

    def test_successor_and_feedback_reference_must_be_identified(self):
        for key in ("source_epoch_id", "successor_epoch_id"):
            for value in (None, "", " ", False, 1, [], "UNKNOWN", "UNRESOLVED"):
                with self.subTest(field=key, value=value):
                    params = self.parameters()
                    params[key] = value
                    with self.assertRaises(V2ContractError):
                        release_feedback(**params)
        for value in (None, "", " ", False, 1, {}, []):
            with self.subTest(reference=value):
                params = self.parameters()
                params["feedback_hash"] = value
                with self.assertRaisesRegex(V2ContractError, "FEEDBACK_HASH_REQUIRED"):
                    release_feedback(**params)

    def test_valid_future_metadata_keeps_successor_only_contract_and_event_shape(self):
        params = self.parameters()
        event = release_feedback(**params)
        self.assertEqual(event, release_feedback(**params))
        self.assertEqual(set(event), {"event_type", "source_epoch_id", "successor_epoch_id",
                                      "feedback_hash", "event_hash"})
        self.assertEqual(event["source_epoch_id"], params["source_epoch_id"])
        self.assertEqual(event["successor_epoch_id"], params["successor_epoch_id"])
        params["successor_epoch_id"] = params["source_epoch_id"]
        with self.assertRaisesRegex(V2ContractError, "FEEDBACK_REQUIRES_SUCCESSOR_EPOCH"):
            release_feedback(**params)


if __name__ == "__main__":
    unittest.main()
