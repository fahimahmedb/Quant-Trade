import io
import json
import os
import sys
import tempfile
import unittest
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(__file__))
import run_f1 as r  # noqa: E402

D0 = r._ms(2020, 1, 1) // r.DAY_MS


def zipped(path, text, name="x.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(name, text)


def kline_rows(d_first, d_last, close=100.0, high=100.0, qv=1e7, unit=1):
    lines = []
    for d in range(d_first, d_last + 1):
        ts = d * r.DAY_MS * unit
        lines.append(f"{ts},{close},{high},{close},{close},1,{ts + 1},{qv},1,0,0,0")
    return lines


def funding_rows(d_first, d_last, rate=0.0003, jitter=0):
    lines = ["calc_time,funding_interval_hours,last_funding_rate"]
    for d in range(d_first, d_last + 2):
        for h in (0, 8, 16):
            lines.append(f"{d * r.DAY_MS + h * 3_600_000 + jitter},8,{rate}")
    return lines


def make_syms(n_days=90, high=None, rate=0.0003):
    raw = {"funding": {}, "spot": {}, "perp": {}}
    from collections import defaultdict
    raw["funding"] = defaultdict(list)
    for d in range(D0, D0 + n_days):
        raw["spot"][d] = {"high": 100.0, "close": 100.0, "qv": 1e7}
        raw["perp"][d] = {"high": (high.get(d, 100.0) if high else 100.0), "close": 100.0, "qv": 1e7}
    for d in range(D0, D0 + n_days + 1):
        for h in (0, 8, 16):
            raw["funding"][d * r.DAY_MS + h * 3_600_000].append(rate)
    return {"AAAUSDT": r.SymData("AAAUSDT", raw)}


class TimestampAndFilter(unittest.TestCase):
    def test_norm_ts_and_fail_closed(self):
        self.assertEqual(r.norm_ts("1700000000000"), 1700000000000)
        self.assertEqual(r.norm_ts("1700000000000000"), 1700000000000)
        with self.assertRaises(r.FormatError):
            r.norm_ts("1700000000")  # seconds
        with self.assertRaises(r.FormatError):
            r.norm_ts("17000000000000000000")

    def test_late_rows_not_parsed_in_stage_a(self):
        late = r._ms(2024, 1, 5)
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "k.zip")
            lines = kline_rows(D0, D0 + 2) + [f"{late},GARBAGE,GARBAGE,GARBAGE,GARBAGE,1,1,GARBAGE,1,0,0,0"]
            zipped(p, "\n".join(lines))
            rows = list(r.iter_rows(p, *r.STAGES["STAGE_A"]["read"], "kline"))
            self.assertEqual(len(rows), 3)

    def test_microsecond_timestamps_accepted(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "k.zip")
            zipped(p, "\n".join(kline_rows(D0, D0 + 1, unit=1000)))
            rows = list(r.iter_rows(p, *r.STAGES["STAGE_A"]["read"], "kline"))
            self.assertEqual(int(rows[0][0]), D0 * r.DAY_MS)

    def test_header_validated_and_columns_exact(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "k.zip")
            zipped(p, r.HEADERS["kline"] + "\n" + "\n".join(kline_rows(D0, D0)))
            self.assertEqual(len(list(r.iter_rows(p, *r.STAGES["STAGE_A"]["read"], "kline"))), 1)
            zipped(p + "b", "open_time,wrong\n" + "\n".join(kline_rows(D0, D0)))
            with self.assertRaises(r.FormatError):
                list(r.iter_rows(p + "b", *r.STAGES["STAGE_A"]["read"], "kline"))
            zipped(p + "2", "abc,2,3")
            with self.assertRaises(r.FormatError):
                list(r.iter_rows(p + "2", *r.STAGES["STAGE_A"]["read"], "kline"))
            short = kline_rows(D0, D0)[0].rsplit(",", 3)[0]
            zipped(p + "3", short)
            with self.assertRaises(r.FormatError):
                list(r.iter_rows(p + "3", *r.STAGES["STAGE_A"]["read"], "kline"))
            zipped(p + "4", r.HEADERS["funding"] + "\n" + f"{D0 * r.DAY_MS},8,0.0001")
            self.assertEqual(len(list(r.iter_rows(p + "4", *r.STAGES["STAGE_A"]["read"], "funding"))), 1)

    def test_nan_and_nonpositive_prices_rejected(self):
        with self.assertRaises(r.FormatError):
            r.finite_pos("nan")
        with self.assertRaises(r.FormatError):
            r.finite_pos("0")
        with self.assertRaises(r.FormatError):
            r.finite_pos("-1")
        self.assertEqual(r.finite_pos("0", allow_zero=True), 0.0)


class Funding(unittest.TestCase):
    def test_slot_rounding_and_day_attribution(self):
        raw = {"funding": {}}
        from collections import defaultdict
        f = defaultdict(list)
        slot0 = r.MIN_MS * round((D0 * r.DAY_MS + 5) / r.MIN_MS)
        f[slot0].append(0.001)
        f[slot0 + 8 * 3_600_000].append(0.002)
        sig, earn, has = r.build_funding_days(f)
        self.assertEqual(sig[D0], 0.003)           # [D, D+1)
        self.assertNotIn(D0 - 1, sig)
        self.assertAlmostEqual(earn[D0 - 1], 0.001)  # slot == D belongs to previous day (D-1, D]
        self.assertAlmostEqual(earn[D0], 0.002)


class Simulation(unittest.TestCase):
    def test_constant_carry_exact_nav(self):
        n = 120
        syms = make_syms(n)
        d_last = D0 + n - 1
        rets, diag = r.simulate(syms, 0.20, 1.0, D0, d_last)
        # first eligible day: 60 bars (D0+59) and 7 funding days
        e = D0 + 59
        N = 0.1 * 0.75
        entry_cost = N * (0.001 + 0.0002 + 0.0005 + 0.0002)
        hold_days = d_last - e
        expected = 1 - entry_cost + hold_days * N * 0.0009 - entry_cost
        self.assertAlmostEqual(diag["final_nav"], expected, places=12)
        self.assertEqual(len(rets), n)
        self.assertTrue(all(x == 0.0 for x in rets[:59]))  # flat days included
        self.assertEqual(diag["liquidations"], 0)

    def test_below_threshold_no_trades(self):
        syms = make_syms(90, rate=0.00001)
        rets, diag = r.simulate(syms, 0.05, 1.0, D0, D0 + 89)
        self.assertEqual(diag["exposure_days"], 0)
        self.assertEqual(diag["final_nav"], 1.0)

    def test_liquidation_event_and_bar(self):
        n = 120
        e = D0 + 59
        syms = make_syms(n, high={e + 3: 130.0})
        rets, diag = r.simulate(syms, 0.20, 1.0, D0, D0 + n - 1)
        self.assertEqual(diag["liquidations"], 1)
        # barred for 30 days: no re-entry before e+3+30
        q = 0.1 * 0.75 / 100.0
        pen = r.LIQ_PEN * q * 125.0
        self.assertAlmostEqual(diag["components"]["liquidation_penalty"], pen)
        # held through e+1..e+3 (liquidated on e+3), barred through e+33, re-enters at close of e+34, held e+35..last
        self.assertEqual(diag["exposure_days"], 3 + (n - 1 - (59 + 34)))

    def test_stress_costs_lower_nav(self):
        syms = make_syms(100)
        _, base = r.simulate(syms, 0.20, 1.0, D0, D0 + 99)
        _, stress = r.simulate(syms, 0.20, 2.0, D0, D0 + 99)
        self.assertLess(stress["final_nav"], base["final_nav"])

    def test_missing_bar_for_open_position_forces_exit(self):
        syms = make_syms(100)
        del syms["AAAUSDT"].spot[D0 + 80]
        _, diag = r.simulate(syms, 0.20, 1.0, D0, D0 + 99)
        self.assertEqual(diag["forced_exits"], 1)


class Stats(unittest.TestCase):
    def test_nw_and_classification(self):
        x = [0.001, -0.001] * 50
        self.assertGreater(r.nw_se_mean(x, 7), 0)
        base = {"t_one_sided": 3.0, "quarters_positive": 7, "sharpe_annual": 2.5, "se_sharpe": 0.5}
        stress = {"mean_daily": 1e-4}
        self.assertEqual(r.classify(base, stress, 11, 0.5), "CONFIRMED")
        self.assertEqual(r.classify(base, stress, 11, 0.05), "DEGENERATE_EXPOSURE")
        low = {"t_one_sided": 0.1, "quarters_positive": 3, "sharpe_annual": 0.1, "se_sharpe": 0.3}
        self.assertEqual(r.classify(low, stress, 11, 0.5), "NOT_CONFIRMED_EXCLUDES_SR_1.5")
        mid = {"t_one_sided": 1.0, "quarters_positive": 5, "sharpe_annual": 1.0, "se_sharpe": 0.6}
        self.assertEqual(r.classify(mid, stress, 11, 0.5), "INCONCLUSIVE_UNDERPOWERED")

    def test_z_constant_matches_prereg(self):
        from statistics import NormalDist
        self.assertAlmostEqual(r.Z_ONE_SIDED, NormalDist().inv_cdf(1 - 0.05 / 3 / 3), places=6)


def write_manifest(data, stage):
    import hashlib
    recs = []
    for root, _, files in os.walk(data):
        for fn in files:
            if fn.endswith(".zip"):
                ds, sym = os.path.relpath(root, data).split(os.sep)
                recs.append({"ok": True, "dataset": ds, "symbol": sym, "key": f"x/{ds}/{sym}/{fn}",
                             "sha256": hashlib.sha256(open(os.path.join(root, fn), "rb").read()).hexdigest()})
    with open(os.path.join(data, f"manifest_{stage}.jsonl"), "w") as f:
        for rec in recs:
            f.write(json.dumps(rec) + "\n")


def fixture(t, n, name="a-2020-01.zip", sym="AAAUSDT", funding_extra=None):
    data = os.path.join(t, "data")
    zipped(os.path.join(data, "spot1d", sym, name), "\n".join(kline_rows(D0, D0 + n - 1)))
    zipped(os.path.join(data, "perp1d", sym, name), "\n".join(kline_rows(D0, D0 + n - 1)))
    zipped(os.path.join(data, "funding", sym, name), "\n".join(funding_rows(D0, D0 + n - 1) + (funding_extra or [])))
    return data


class Patched(unittest.TestCase):
    def setUp(self):
        self.old = dict(r.STAGES["STAGE_A"])

    def tearDown(self):
        r.STAGES["STAGE_A"] = self.old

    def patch(self, n):
        r.STAGES["STAGE_A"] = {"read": self.old["read"], "stat": (D0 * r.DAY_MS, (D0 + n) * r.DAY_MS)}


class EndToEnd(Patched):
    def test_result_written_once_and_late_rows_ignored(self):
        with tempfile.TemporaryDirectory() as t:
            n = 120
            late = r._ms(2024, 2, 1)
            data = fixture(t, n, funding_extra=[f"{late},8,GARBAGE"])
            write_manifest(data, "STAGE_A")
            self.patch(n)
            res_path = os.path.join(t, "res", "a.json")
            out = r.run("STAGE_A", data, res_path)
            self.assertEqual(out["n_symbols"], 1)
            self.assertIn("selected_theta", out)
            self.assertIn("daily_returns_base", out["cells"]["0.05"])
            self.assertEqual(len(out["cells"]["0.05"]["daily_returns_base"]), n)
            self.assertIn("harness_sha256", out)
            with self.assertRaises(Exception):
                r.run("STAGE_A", data, res_path)   # second run cannot overwrite
            self.assertFalse(os.path.exists(res_path + ".tmp"))

    def test_unrecognised_format_leaves_no_result(self):
        with tempfile.TemporaryDirectory() as t:
            data = os.path.join(t, "data")
            zipped(os.path.join(data, "spot1d", "AAAUSDT", "a-2020-01.zip"), "1700000000,1,2,3,4,5,6,7,8,9,10,11")
            zipped(os.path.join(data, "perp1d", "AAAUSDT", "a-2020-01.zip"), "\n".join(kline_rows(D0, D0)))
            zipped(os.path.join(data, "funding", "AAAUSDT", "a-2020-01.zip"), "\n".join(funding_rows(D0, D0)))
            write_manifest(data, "STAGE_A")
            res_path = os.path.join(t, "res", "a.json")
            with self.assertRaises(r.FormatError):
                r.run("STAGE_A", data, res_path)
            self.assertFalse(os.path.exists(res_path))

    def test_file_not_in_manifest_and_checksum_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            data = fixture(t, 100)
            write_manifest(data, "STAGE_A")
            zipped(os.path.join(data, "funding", "AAAUSDT", "extra-2020-02.zip"), "x")
            with self.assertRaises(r.FormatError):
                r.run("STAGE_A", data, os.path.join(t, "res", "a.json"))
            os.remove(os.path.join(data, "funding", "AAAUSDT", "extra-2020-02.zip"))
            zipped(os.path.join(data, "funding", "AAAUSDT", "a-2020-01.zip"), "\n".join(funding_rows(D0, D0)))
            with self.assertRaises(r.FormatError):
                r.run("STAGE_A", data, os.path.join(t, "res", "b.json"))

    def test_out_of_window_file_never_opened(self):
        with tempfile.TemporaryDirectory() as t:
            n = 100
            data = fixture(t, n)
            bad = os.path.join(data, "funding", "AAAUSDT", "a-2026-05.zip")
            os.makedirs(os.path.dirname(bad), exist_ok=True)
            open(bad, "wb").write(b"not a zip")      # Stage B-dated file present in the directory
            write_manifest(data, "STAGE_A")
            self.patch(n)
            out = r.run("STAGE_A", data, os.path.join(t, "res", "a.json"))   # must not raise
            self.assertEqual(out["n_symbols"], 1)

    def test_stage_b_requires_valid_stage_a_and_marks_ineligible(self):
        with tempfile.TemporaryDirectory() as t:
            bad = os.path.join(t, "sa.json")
            json.dump({"stage": "STAGE_B", "selected_theta": 0.1}, open(bad, "w"))
            data = fixture(t, 5)
            write_manifest(data, "STAGE_B")
            with self.assertRaises(r.FormatError):
                r.run("STAGE_B", data, os.path.join(t, "res", "b.json"), bad)


class Extra(unittest.TestCase):
    def test_forced_exit_on_delisting(self):
        n = 120
        syms = make_syms(n)
        s = syms["AAAUSDT"]
        for d in range(D0 + 80, D0 + n):
            del s.perp[d]
            del s.spot[d]
        rets, diag = r.simulate(syms, 0.20, 1.0, D0, D0 + n - 1)
        self.assertEqual(diag["forced_exits"], 1)
        self.assertGreater(diag["components"]["fees"], 0)
        self.assertTrue(all(x == 0.0 for x in rets[81:]))

    def test_no_entry_on_last_day(self):
        n = 70
        syms = make_syms(n)
        rets, diag = r.simulate(syms, 0.20, 1.0, D0, D0 + n - 1)
        # first eligible decision is day D0+59; the window ends at D0+69 so entry happens and is held
        rets2, diag2 = r.simulate(syms, 0.20, 1.0, D0, D0 + 59)
        self.assertEqual(diag2["final_nav"], 1.0)    # eligible on the last day: no entry, no round-trip cost
        self.assertEqual(diag2["exposure_days"], 0)

    def test_entry_weights_equal_regardless_of_order(self):
        n = 100
        from collections import defaultdict
        syms = {}
        for name in ("AAAUSDT", "BBBUSDT", "CCCUSDT"):
            rr = {"funding": defaultdict(list), "spot": {}, "perp": {}}
            for d in range(D0, D0 + n):
                rr["spot"][d] = {"high": 100.0, "close": 100.0, "qv": 1e7}
                rr["perp"][d] = {"high": 100.0, "close": 100.0, "qv": 1e7}
            for d in range(D0, D0 + n + 1):
                for h in (0, 8, 16):
                    rr["funding"][d * r.DAY_MS + h * 3_600_000].append(0.0003)
            syms[name] = r.SymData(name, rr)
        e = D0 + 59
        _, diag = r.simulate(syms, 0.20, 1.0, D0, e + 1)
        N = 0.1 * 0.75
        cost = 3 * N * (0.001 + 0.0002 + 0.0005 + 0.0002)
        self.assertAlmostEqual(diag["final_nav"], 1 - cost + 3 * N * 0.0009 - cost, places=12)


if __name__ == "__main__":
    unittest.main()
