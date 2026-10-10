"""Adversarial synthetic cases only; never opens a market file."""
import math
import unittest
from datetime import datetime, timezone

from safety_kernel import (CENTRAL, STRESS, PIP, Quote, source_time_utc,
    envelope, opening_fill, closing_fill, planned_quantity, fill_admissible,
    rollover_charge, stale_trigger)


class SafetyTests(unittest.TestCase):
    def test_histdata_fixed_est_in_summer_and_winter(self):
        for month in (1, 7):
            s = f"2025{month:02}01 120000123"
            t = source_time_utc(s)
            self.assertEqual((t.hour, t.microsecond), (17, 123000))

    def test_bad_timestamp_not_rounded(self):
        for s in ("20250101 120000", "20250101 1200001234", "20250230 120000000"):
            with self.assertRaises(ValueError):
                source_time_utc(s)

    def test_equal_time_adverse_envelope_is_order_invariant(self):
        qs = [Quote(0, 1.10, 1.1001), Quote(0, 1.09, 1.0901)]
        self.assertEqual(envelope(qs), envelope(qs[::-1]))
        self.assertEqual(envelope(qs), Quote(0, 1.09, 1.1001))

    def test_duplicates_do_not_create_a_better_quote(self):
        q = Quote(0, 1.10, 1.1001)
        self.assertEqual(envelope([q]*12), q)

    def test_mixed_times_and_invalid_quotes_fail_closed(self):
        with self.assertRaises(ValueError):
            envelope([Quote(0, 1, 1), Quote(1, 1, 1)])
        for bid, ask in ((0, 1), (1.1, 1), (math.nan, 1), (1, math.inf)):
            with self.assertRaises(ValueError):
                Quote(0, bid, ask)

    def test_both_open_directions_pay_adverse_delayed_quote(self):
        a, b = Quote(0, 1.10, 1.1001), Quote(1000, 1.11, 1.1101)
        self.assertAlmostEqual(opening_fill(a,b,1,CENTRAL),1.110125)
        self.assertAlmostEqual(opening_fill(a,b,-1,CENTRAL),1.099975)

    def test_pre_latency_open_and_close_are_forbidden(self):
        a,b=Quote(0,1,1.0001),Quote(999,1,1.0001)
        for f in (opening_fill,closing_fill):
            with self.assertRaises(ValueError):
                f(a,b,1,CENTRAL)

    def test_open_deadline_includes_exact_boundary_only(self):
        a=Quote(0,1,1.0001)
        self.assertIsNotNone(opening_fill(a,Quote(6000,1,1.0001),1,CENTRAL))
        self.assertIsNone(opening_fill(a,Quote(6001,1,1.0001),1,CENTRAL))

    def test_failed_close_never_expires(self):
        a=Quote(0,1,1.0001);b=Quote(86400000,.9,.9001)
        self.assertLess(closing_fill(a,b,1,CENTRAL),.9)

    def test_stop_gap_never_caps_loss_at_stop(self):
        a=Quote(0,1,1.0001);b=Quote(1000,.9,.9001)
        self.assertLess(closing_fill(a,b,1,CENTRAL,stop=.95),.9)

    def test_equal_time_stop_bound_overrides_optimistic_target(self):
        a=Quote(0,1.1,1.1001);b=Quote(1000,1.2,1.2001)
        self.assertLess(closing_fill(a,b,1,CENTRAL,stop=1.0),1.0)
        self.assertGreater(closing_fill(a,b,-1,CENTRAL,stop=1.3),1.3)

    def test_stress_never_improves_same_quote_fills(self):
        a,b=Quote(0,1.1,1.1001),Quote(1000,1.11,1.1101)
        self.assertGreater(opening_fill(a,b,1,STRESS),opening_fill(a,b,1,CENTRAL))
        self.assertLess(opening_fill(a,b,-1,STRESS),opening_fill(a,b,-1,CENTRAL))
        self.assertLess(closing_fill(a,b,1,STRESS),closing_fill(a,b,1,CENTRAL))
        self.assertGreater(closing_fill(a,b,-1,STRESS),closing_fill(a,b,-1,CENTRAL))

    def test_all_rungs_fit_stress_planned_budget(self):
        for d in (.00005,.0005,.005):
            q=planned_quantity(100000,1.1,d,250,3)
            loss=q*sum((3-k)*d+PIP+2*(STRESS.commission+STRESS.slippage)
                       for k in range(3))
            self.assertLessEqual(loss,250)
            self.assertLessEqual(3*q*(1.1+3*d+2*PIP),100000)

    def test_gap_add_rejected_without_resizing(self):
        self.assertFalse(fill_admissible([(10000,1.1)],10000,1.12,1.09,1,
                                        .5,250,100000,1.12))

    def test_gross_cap_includes_existing_inventory(self):
        self.assertFalse(fill_admissible([(50000,1.1)],50000,1.1,1.099,1,
                                        1,250,100000,1.1))

    def test_fourth_rung_forbidden(self):
        self.assertFalse(fill_admissible([(1,1.1)]*3,1,1.1,1.0,1,0,250,100000,1.1))

    def test_small_finite_add_can_pass(self):
        self.assertTrue(fill_admissible([(100,1.1)],100,1.099,1.097,1,
                                       .005,250,100000,1.099))

    def test_staleness_is_strict_and_does_not_invent_future_quote(self):
        a=Quote(0,1.1,1.1001)
        self.assertIsNone(stale_trigger(a,Quote(5000,1.1,1.1001)))
        self.assertEqual(stale_trigger(a,Quote(5001,1,1.0001)),Quote(5000,1.1,1.1001))
        with self.assertRaises(ValueError):
            stale_trigger(a,Quote(-1,1,1.0001))

    def test_wednesday_failed_exit_pays_triple_swap(self):
        a=datetime(2025,7,2,16,tzinfo=timezone.utc)
        b=datetime(2025,7,2,22,tzinfo=timezone.utc)
        self.assertEqual(rollover_charge(a,b,10000,CENTRAL),(3.,1))
        self.assertEqual(rollover_charge(a,b,10000,STRESS),(6.,1))

    def test_rollover_uses_dst_but_source_conversion_does_not(self):
        for month,roll_hour in ((1,22),(7,21)):
            a=datetime(2025,month,3,16,tzinfo=timezone.utc)
            before=datetime(2025,month,3,roll_hour-1,59,tzinfo=timezone.utc)
            at=datetime(2025,month,3,roll_hour,tzinfo=timezone.utc)
            self.assertEqual(rollover_charge(a,before,10000,CENTRAL),(0.,0))
            self.assertEqual(rollover_charge(a,at,10000,CENTRAL),(1.,1))
            self.assertEqual(rollover_charge(at,at,10000,CENTRAL),(0.,0))


if __name__ == "__main__":
    unittest.main()
