import os
import sys
import unittest
from collections import defaultdict

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(__file__))
import run_f1 as r  # noqa: E402

D0 = r._ms(2020, 1, 1) // r.DAY_MS


def make_raw(last_30_qv):
    raw = {"funding": defaultdict(list), "spot": {}, "perp": {}}
    for i in range(60):
        d = D0 + i
        qv = 10_000_000.0 if i < 30 else float(last_30_qv[i - 30])
        bar = {"high": 100.0, "close": 100.0, "qv": qv}
        raw["spot"][d] = dict(bar)
        raw["perp"][d] = dict(bar)
    return raw


class LiquidityRanking(unittest.TestCase):
    def test_low_slippage_ranking_uses_trailing_30d_aggregate_volume(self):
        # Both symbols pass the preregistered 5m median eligibility gate.
        # A has the higher median, but B has the higher trailing-30d volume.
        a = r.SymData("AUSDT", make_raw([10_000_000.0] * 30))
        b = r.SymData("BUSDT", make_raw([9_000_000.0] * 29 + [100_000_000.0]))
        d = D0 + 59

        ok_a, volume_a = a.eligible(d)
        ok_b, volume_b = b.eligible(d)
        self.assertTrue(ok_a)
        self.assertTrue(ok_b)
        self.assertEqual(volume_a, 300_000_000.0)
        self.assertEqual(volume_b, 361_000_000.0)

        ranked = sorted(
            {"AUSDT": volume_a, "BUSDT": volume_b},
            key=lambda sym: (-{"AUSDT": volume_a, "BUSDT": volume_b}[sym], sym),
        )
        self.assertEqual(ranked, ["BUSDT", "AUSDT"])


if __name__ == "__main__":
    unittest.main()
