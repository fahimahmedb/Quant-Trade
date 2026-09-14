import unittest

from quant.factory.experiments import EventRecord
from quant.factory.geometry import GeometryEngine
from quant.factory.power import PowerScenario, PowerSimulationEngine


def event(i, issuer, day):
    return EventRecord(f"E{i}", issuer, f"2025-01-{day:02d}T20:00:00Z", f"2025-01-{day:02d}", "SYNTHETIC", "CERTIFIED")


class GeometryAndPowerTests(unittest.TestCase):
    def test_geometry_exact_on_synthetic_fixture(self):
        events = [event(1, "A", 1), event(2, "A", 5), event(3, "B", 8), event(4, "C", 30)]
        ordinals = {"2025-01-01": 0, "2025-01-05": 4, "2025-01-08": 7, "2025-01-30": 29}
        report = GeometryEngine(20, 10).analyze(events, ordinals)
        self.assertEqual(report.n, 4)
        self.assertEqual(report.annual_distribution, {2025: 4})
        self.assertEqual(report.events_per_issuer, {"A": 2, "B": 1, "C": 1})
        self.assertAlmostEqual(report.hhi, 0.375)
        self.assertAlmostEqual(report.effective_issuers, 1 / 0.375)
        self.assertEqual(report.overlap.overlapping_pairs, 3)
        self.assertEqual(report.overlap.events_with_any_overlap, 3)
        self.assertEqual(report.clusters.cluster_size_distribution, {1: 2, 2: 1})

    def test_power_is_synthetic_and_detects_large_effect(self):
        events = [event(i + 1, f"I{i % 20:02d}", (i % 20) + 1) for i in range(60)]
        ordinals = {f"2025-01-{day:02d}": day - 1 for day in range(1, 21)}
        report = GeometryEngine().analyze(events, ordinals)
        engine = PowerSimulationEngine()
        null = engine.simulate(report, PowerScenario(0.0, simulations=600, seed=7))
        positive = engine.simulate(report, PowerScenario(0.8, simulations=600, seed=7))
        self.assertTrue(null.synthetic_only and positive.synthetic_only)
        self.assertLess(null.estimated_power, 0.15)
        self.assertGreater(positive.estimated_power, 0.80)

    def test_issuer_dependence_reduces_power_when_concentrated(self):
        events = [event(i + 1, "A" if i < 20 else "B", (i % 20) + 1) for i in range(40)]
        ordinals = {f"2025-01-{day:02d}": day - 1 for day in range(1, 21)}
        report = GeometryEngine().analyze(events, ordinals)
        engine = PowerSimulationEngine()
        independent = engine.simulate(report, PowerScenario(0.6, simulations=800, issuer_icc=0.0, seed=11))
        clustered = engine.simulate(report, PowerScenario(0.6, simulations=800, issuer_icc=0.5, seed=11))
        self.assertGreater(independent.estimated_power, clustered.estimated_power)


if __name__ == "__main__":
    unittest.main()