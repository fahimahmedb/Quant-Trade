"""Anytime-valid betting test vs the plug-in t-SPRT (ORDRE 12b, adversarial).

H0 paths have mean exactly 0 (the worst case of H0: mean <= 0), values in
[-1, 1], H-001 parameters (alpha 0.025, beta 0.05, h1 0.00475, sigma 0.05),
matches arriving in evenings of 5-10. Each path is judged three ways: the new
test per match, the new test per evening (``groups``), and the old t-SPRT per
match exactly as forward.py calls it (floor = declared sigma).

MEASURED (seeded; ``python3 tests/test_anytime_valid_sequential.py`` reprints it).
False ACCEPT under H0, 20 000 paths, horizon 2000 (new/match | new/evening | old):
    normal 0.0021 | 0.0000 | 0.0212      student_t3 0.0014 | 0.0000 | 0.0135
    rare_loss 0.0040 | 0.0000 | 0.0032   evening_shock 0.0826 | 0.0000 | 0.1950
    vol_drift 0.0052 | 0.0000 | 0.0231
Per evening at horizon 12 000 (QUANT_SLOW_TESTS=1): 0.0000 in all five.
H1 (0.00475, sigma 0.05), accept / median matches to accept:
    iid:           new/match 0.991 / 1254 (p90 2044)   old 0.950 / 648
    evening shock: new/evening 1.000 / 8159 (p90 10837; 82% by 10 000)
                   new/match 0.851, false REJECT 0.149; old 0.710, false REJECT 0.290
Synthetic fixtures only: none of this is market evidence.
"""

from __future__ import annotations

import math
import multiprocessing
import os
import random
import statistics
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "src"))

from quant.learning.sequential import (anytime_valid_mean_test,  # noqa: E402
                                      event_sequential_test)

ALPHA, BETA, H1, SIGMA = 0.025, 0.05, 0.00475, 0.05
LOWER, UPPER = -1.0, 1.0
H0_PATHS, H0_HORIZON, CHUNKS = 20_000, 2000, 4
RHO = 0.3


def _clip(x: float) -> float:
    return LOWER if x < LOWER else UPPER if x > UPPER else x


def _evenings(rng: random.Random, n: int, draw) -> tuple[list[float], list[int]]:
    """``draw(rng, t, size, shock)`` gives one value; evenings of 5-10 matches."""
    values: list[float] = []
    groups: list[int] = []
    evening = 0
    while len(values) < n:
        size, shock = rng.randint(5, 10), rng.gauss(0.0, 1.0)
        for _ in range(size):
            values.append(_clip(draw(rng, len(values), n, shock)))
            groups.append(evening)
        evening += 1
    return values[:n], groups[:n]


def _t3(rng: random.Random) -> float:
    return rng.gauss(0.0, 1.0) / math.sqrt(rng.gammavariate(1.5, 2.0) / 3.0)


def scenario(name: str, mean: float = 0.0):
    """Symmetric clipping keeps the mean exact for the symmetric laws."""
    s = SIGMA
    return {
        "normal": lambda r, t, n, z: mean + r.gauss(0.0, s),
        "student_t3": lambda r, t, n, z: mean + s / math.sqrt(3.0) * _t3(r),
        # 99% small wins, 1% large losses: mean 0, sigma 0.0497.
        "rare_loss": lambda r, t, n, z: mean + (0.005 if r.random() < 0.99 else -0.495),
        "evening_shock": lambda r, t, n, z: mean + s * (math.sqrt(RHO) * z
                                                        + math.sqrt(1 - RHO) * r.gauss(0, 1)),
        # Volatility drifts from 0.03 to 0.12: the plug-in sigma lags behind.
        "vol_drift": lambda r, t, n, z: mean + r.gauss(0.0, 0.03 + 0.09 * t / n),
    }[name]


H0_SCENARIOS = ("normal", "student_t3", "rare_loss", "evening_shock", "vol_drift")


def _judge(values, groups, horizon, grouped_only=False):
    if grouped_only:
        return (None, anytime_valid_mean_test(values, LOWER, UPPER, ALPHA, BETA, H1, horizon,
                                              groups=groups), None)
    return (anytime_valid_mean_test(values, LOWER, UPPER, ALPHA, BETA, H1, horizon),
            anytime_valid_mean_test(values, LOWER, UPPER, ALPHA, BETA, H1, horizon,
                                    groups=groups),
            event_sequential_test(values, H1 / SIGMA, ALPHA, BETA, max_observations=horizon,
                                  sigma_floor=SIGMA))


def _run(job):
    """One seeded chunk: decisions and stopping times of the three tests."""
    name, mean, seed, paths, horizon, *grouped_only = job
    rng, draw = random.Random(seed), scenario(name, mean)
    out = {"new": [], "grouped": [], "old": []}
    for _ in range(paths):
        values, groups = _evenings(rng, horizon, draw)
        for key, verdict in zip(out, _judge(values, groups, horizon, bool(grouped_only))):
            if verdict is not None:
                out[key].append((verdict["decision"], verdict["observations"]))
    return name, mean, out


def _simulate(jobs):
    with multiprocessing.get_context("fork").Pool(min(os.cpu_count() or 1, 8)) as pool:
        merged: dict = {}
        for name, mean, out in pool.map(_run, jobs):
            slot = merged.setdefault((name, mean), {"new": [], "grouped": [], "old": []})
            for key in slot:
                slot[key] += out[key]
    return merged


def _rate(rows, decision):
    return sum(d == decision for d, _ in rows) / len(rows)


def _median_to_accept(rows):
    stops = [n for d, n in rows if d == "ACCEPT_EDGE"]
    return statistics.median(stops) if stops else None


#: Long-horizon H0 check of the per-evening mode, at the horizon it needs for
#: power (QUANT_SLOW_TESTS=1; about 25 CPU-minutes).
LONG_HORIZON = 12_000

H1_CASES = (("normal", 2000, 4000), ("evening_shock", 1000, 16000))


class AnytimeValidUnderH0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        per = H0_PATHS // CHUNKS
        cls.h0 = _simulate([(name, 0.0, 1_000 * i + j, per, H0_HORIZON)
                            for i, name in enumerate(H0_SCENARIOS) for j in range(CHUNKS)])

    def test_twenty_thousand_paths_per_scenario(self):
        for name in H0_SCENARIOS:
            self.assertEqual(len(self.h0[(name, 0.0)]["grouped"]), H0_PATHS)

    def test_grouped_false_accept_at_most_alpha_in_every_scenario(self):
        for name in H0_SCENARIOS:
            rate = _rate(self.h0[(name, 0.0)]["grouped"], "ACCEPT_EDGE")
            self.assertLessEqual(rate, ALPHA, name)

    def test_per_match_false_accept_at_most_alpha_when_assumption_holds(self):
        for name in H0_SCENARIOS:
            if name != "evening_shock":
                rate = _rate(self.h0[(name, 0.0)]["new"], "ACCEPT_EDGE")
                self.assertLessEqual(rate, ALPHA, name)

    def test_per_match_betting_breaks_under_common_evening_shocks(self):
        # Documented failure: the conditional-mean condition fails inside an evening.
        self.assertGreater(_rate(self.h0[("evening_shock", 0.0)]["new"], "ACCEPT_EDGE"), ALPHA)

    def test_old_t_sprt_is_reported_not_corrected(self):
        # Audit Astra 2026-09-29: alpha not guaranteed under dependence.
        self.assertGreater(_rate(self.h0[("evening_shock", 0.0)]["old"], "ACCEPT_EDGE"),
                           2 * ALPHA)


@unittest.skipUnless(os.environ.get("QUANT_SLOW_TESTS") == "1", "slow: QUANT_SLOW_TESTS=1")
class GroupedAnytimeValidLongHorizon(unittest.TestCase):
    def test_grouped_false_accept_at_most_alpha_at_long_horizon(self):
        per = H0_PATHS // CHUNKS
        runs = _simulate([(name, 0.0, 50_000 + 1_000 * i + j, per, LONG_HORIZON, True)
                          for i, name in enumerate(H0_SCENARIOS) for j in range(CHUNKS)])
        for name in H0_SCENARIOS:
            rows = runs[(name, 0.0)]["grouped"]
            self.assertEqual(len(rows), H0_PATHS)
            print(f"{name}: grouped false ACCEPT {_rate(rows, 'ACCEPT_EDGE'):.4f} "
                  f"at horizon {LONG_HORIZON}", file=sys.stderr)
            self.assertLessEqual(_rate(rows, "ACCEPT_EDGE"), ALPHA, name)


class AnytimeValidUnderH1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h1 = _simulate([(name, H1, 7_000 + 10 * i + j, paths // CHUNKS, horizon)
                            for i, (name, paths, horizon) in enumerate(H1_CASES)
                            for j in range(CHUNKS)])

    def test_power_and_false_reject(self):
        for name, _, _ in H1_CASES:
            runs = self.h1[(name, H1)]
            # Per match is only guaranteed without shared evening shocks.
            for key in ("new", "grouped") if name != "evening_shock" else ("grouped",):
                self.assertLessEqual(_rate(runs[key], "REJECT_EDGE"), BETA, (name, key))
        independent = self.h1[("normal", H1)]
        self.assertGreater(_rate(independent["new"], "ACCEPT_EDGE"), 0.9)
        self.assertGreater(_rate(self.h1[("evening_shock", H1)]["grouped"], "ACCEPT_EDGE"), 0.9)


class AnytimeValidMechanics(unittest.TestCase):
    def setUp(self):
        rng = random.Random(3)
        self.values = [_clip(rng.gauss(0.02, 0.05)) for _ in range(3000)]
        self.groups = [i // 6 for i in range(3000)]

    def test_replay_is_identical_and_final(self):
        first = anytime_valid_mean_test(self.values, LOWER, UPPER, ALPHA, BETA, H1, 3000)
        self.assertEqual(first["decision"], "ACCEPT_EDGE")
        self.assertEqual(first, anytime_valid_mean_test(list(self.values), LOWER, UPPER, ALPHA,
                                                        BETA, H1, 3000))
        n = first["observations"]
        later = self.values[:n] + [-1.0] * 500
        self.assertEqual(first, anytime_valid_mean_test(later, LOWER, UPPER, ALPHA, BETA, H1,
                                                        3000))
        grouped = anytime_valid_mean_test(self.values, LOWER, UPPER, ALPHA, BETA, H1, 3000,
                                          groups=self.groups)
        self.assertEqual(grouped, anytime_valid_mean_test(self.values, LOWER, UPPER, ALPHA, BETA,
                                                          H1, 3000, groups=list(self.groups)))
        self.assertEqual(grouped["observations"] % 6, 0)     # decisions only at round ends

    def test_horizon_is_inconclusive_and_short_history_continues(self):
        flat = [0.001 * (1 if i % 2 else -1) for i in range(500)]
        verdict = anytime_valid_mean_test(flat, LOWER, UPPER, ALPHA, BETA, H1, 400)
        self.assertEqual((verdict["decision"], verdict["observations"]), ("INCONCLUSIVE", 400))
        short = anytime_valid_mean_test(flat[:50], LOWER, UPPER, ALPHA, BETA, H1, 400)
        self.assertEqual((short["decision"], short["observations"]), ("CONTINUE", 50))

    def test_invalid_input_raises(self):
        for bad in (1.01, -1.5, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                anytime_valid_mean_test([0.0, bad], LOWER, UPPER, ALPHA, BETA, H1, 10)
        with self.assertRaises(ValueError):
            anytime_valid_mean_test([0.0], LOWER, UPPER, ALPHA, BETA, 0.0, 10)
        with self.assertRaises(ValueError):
            anytime_valid_mean_test([0.0], 0.0, UPPER, ALPHA, BETA, H1, 10)
        with self.assertRaises(ValueError):
            anytime_valid_mean_test([0.0], LOWER, UPPER, ALPHA, BETA, H1, 0)
        with self.assertRaises(ValueError):
            anytime_valid_mean_test([0.0, 0.0], LOWER, UPPER, ALPHA, BETA, H1, 10, groups=[1])
        with self.assertRaises(ValueError):
            anytime_valid_mean_test([0.0] * 3, LOWER, UPPER, ALPHA, BETA, H1, 10,
                                    groups=["a", "b", "a"])


def _report():
    per = H0_PATHS // CHUNKS
    h0 = _simulate([(name, 0.0, 1_000 * i + j, per, H0_HORIZON)
                    for i, name in enumerate(H0_SCENARIOS) for j in range(CHUNKS)])
    print(f"H0 false ACCEPT, {H0_PATHS} paths, horizon {H0_HORIZON}, alpha {ALPHA}")
    for name in H0_SCENARIOS:
        runs = h0[(name, 0.0)]
        print(f"  {name:14s} new/match {_rate(runs['new'], 'ACCEPT_EDGE'):.4f}  "
              f"new/evening {_rate(runs['grouped'], 'ACCEPT_EDGE'):.4f}  "
              f"old t-SPRT {_rate(runs['old'], 'ACCEPT_EDGE'):.4f}")
    h1 = _simulate([(name, H1, 7_000 + 10 * i + j, paths // CHUNKS, horizon)
                    for i, (name, paths, horizon) in enumerate(H1_CASES) for j in range(CHUNKS)])
    for name, paths, horizon in H1_CASES:
        print(f"H1 {name}, {paths} paths, horizon {horizon}")
        for key, rows in h1[(name, H1)].items():
            accepts = sorted(n for d, n in rows if d == "ACCEPT_EDGE")
            at = {h: sum(n <= h for n in accepts) / len(rows)
                  for h in (1500, 3000, 6000, 10000, 12000)}
            print(f"  {key:8s} accept {_rate(rows, 'ACCEPT_EDGE'):.3f} "
                  f"reject {_rate(rows, 'REJECT_EDGE'):.3f} median {_median_to_accept(rows)} "
                  f"p90 {accepts[int(0.9 * len(accepts))] if accepts else None} "
                  f"power<=h {at}")


if __name__ == "__main__":
    _report()
