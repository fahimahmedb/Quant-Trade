import unittest

from protocol_model import CanonicalState, SessionBinding


class ProtocolModelTests(unittest.TestCase):
    def make(self):
        canonical = CanonicalState()
        binding = SessionBinding("s1", 1, "worker-A", "codex", "lease-1", 2.0)
        canonical.start_session(binding, 0.0)
        return canonical, binding

    def event(self, canonical, binding, **kwargs):
        base = dict(
            event_id="e1",
            session_id=binding.session_id,
            generation=binding.generation,
            worker_id=binding.worker_id,
            engine=binding.engine,
            lease_id=binding.lease_id,
            sequence=1,
            event_type="HEARTBEAT",
            now=1.0,
        )
        base.update(kwargs)
        return canonical.apply_event(**base)

    def test_fresh_lease_active(self):
        canonical, binding = self.make()
        self.event(canonical, binding)
        self.assertTrue(canonical.sessions[("s1", 1)].active)

    def test_expired_lease_stale(self):
        canonical, _ = self.make()
        canonical.expire(6.001)
        self.assertFalse(canonical.sessions[("s1", 1)].active)

    def test_previous_generation_rejected(self):
        canonical, binding = self.make()
        newer = SessionBinding("s1", 2, "worker-A", "codex", "lease-2", 2.0)
        canonical.start_session(newer, 1.0)
        with self.assertRaisesRegex(ValueError, "old_generation"):
            self.event(canonical, binding, event_id="old", now=2.0)

    def test_duplicate_idempotent(self):
        canonical, binding = self.make()
        self.event(canonical, binding, event_id="dup", sequence=1)
        before = canonical.stream_cursor
        result = self.event(canonical, binding, event_id="dup", sequence=2)
        self.assertEqual("DUPLICATE_IGNORED", result)
        self.assertEqual(before, canonical.stream_cursor)

    def test_old_sequence_no_regression(self):
        canonical, binding = self.make()
        self.event(
            canonical,
            binding,
            event_id="new",
            sequence=3,
            event_type="ACTION_STARTED",
            activity_type="AUDIT",
        )
        with self.assertRaisesRegex(ValueError, "old_sequence"):
            self.event(
                canonical,
                binding,
                event_id="old",
                sequence=2,
                event_type="ACTION_STARTED",
                activity_type="SEARCH",
            )
        self.assertEqual("AUDIT", canonical.sessions[("s1", 1)].current_activity)

    def test_restart_invalidates_old_lease(self):
        canonical, binding = self.make()
        self.event(
            canonical,
            binding,
            event_id="work",
            event_type="ACTION_STARTED",
            activity_type="READ",
        )
        canonical.stream_ready = True
        self.assertTrue(canonical.work_animation_allowed("s1", 1))
        canonical.backend_restart()
        self.assertFalse(canonical.sessions[("s1", 1)].active)
        self.assertFalse(canonical.work_animation_allowed("s1", 1))

    def test_snapshot_without_stream_never_animates(self):
        canonical, binding = self.make()
        self.event(
            canonical,
            binding,
            event_id="work",
            event_type="ACTION_STARTED",
            activity_type="READ",
        )
        snapshot = canonical.snapshot()
        self.assertFalse(snapshot["stream_ready"])
        self.assertFalse(canonical.work_animation_allowed("s1", 1))

    def test_spoof_wrong_worker_rejected(self):
        canonical, binding = self.make()
        with self.assertRaisesRegex(ValueError, "identity_binding_mismatch"):
            self.event(canonical, binding, event_id="spoof", worker_id="worker-B")

    def test_spoof_wrong_engine_rejected(self):
        canonical, binding = self.make()
        with self.assertRaisesRegex(ValueError, "identity_binding_mismatch"):
            self.event(canonical, binding, event_id="spoof", engine="chatgpt")

    def test_spoof_wrong_lease_rejected(self):
        canonical, binding = self.make()
        with self.assertRaisesRegex(ValueError, "identity_binding_mismatch"):
            self.event(canonical, binding, event_id="spoof", lease_id="lease-x")

    def test_unknown_event_counted_not_guessed(self):
        canonical, binding = self.make()
        with self.assertRaisesRegex(ValueError, "unknown_event"):
            self.event(canonical, binding, event_id="u", event_type="MAGIC")
        self.assertEqual(1, canonical.unknown_event_count)


if __name__ == "__main__":
    unittest.main(verbosity=2)
