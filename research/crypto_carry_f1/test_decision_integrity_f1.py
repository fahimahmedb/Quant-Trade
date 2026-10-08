"""Decision-changing F1 regressions; generated fixtures only, no network."""
import hashlib
import json
import os
import tempfile
import unittest
from collections import defaultdict
from contextlib import contextmanager
from unittest.mock import patch

from research.crypto_carry_f1 import test_run_f1 as fixtures

r = fixtures.r
D0 = fixtures.D0


class ManifestCompleteness(unittest.TestCase):
    def test_missing_successful_manifest_file_aborts_before_simulation(self):
        for dataset in ("funding", "spot1d", "perp1d"):
            with self.subTest(dataset=dataset), tempfile.TemporaryDirectory() as root:
                data = fixtures.fixture(root, 100)
                fixtures.write_manifest(data, "STAGE_A")
                os.remove(os.path.join(data, dataset, "AAAUSDT", "a-2020-01.zip"))
                result = os.path.join(root, "results", "a.json")
                with patch.object(r, "simulate", wraps=r.simulate) as simulate:
                    with self.assertRaisesRegex(r.FormatError, "manifest.*missing"):
                        r.run("STAGE_A", data, result)
                    simulate.assert_not_called()
                self.assertFalse(os.path.exists(result))

    def test_missing_out_of_window_file_is_never_opened(self):
        with tempfile.TemporaryDirectory() as root:
            data = fixtures.fixture(root, 100)
            sealed = os.path.join(data, "funding", "AAAUSDT", "a-2025-01.zip")
            fixtures.zipped(sealed, "not a funding CSV")
            fixtures.write_manifest(data, "STAGE_A")
            os.remove(sealed)
            original = r.sha256_file

            def guarded_hash(path):
                self.assertNotEqual(path, sealed)
                return original(path)

            with patch.object(r, "sha256_file", side_effect=guarded_hash):
                result = r.run("STAGE_A", data, os.path.join(root, "results", "a.json"))
            self.assertEqual(result["n_symbols"], 1)


class MutationDetection(unittest.TestCase):
    def test_equal_size_rewrite_with_restored_mtime_invalidates_run(self):
        with tempfile.TemporaryDirectory() as root:
            data = fixtures.fixture(root, 100)
            fixtures.write_manifest(data, "STAGE_A")
            path = os.path.join(data, "spot1d", "AAAUSDT", "a-2020-01.zip")
            before = os.stat(path)
            original = r.simulate
            changed = False

            def mutate_after_loading(*args, **kwargs):
                nonlocal changed
                if not changed:
                    with open(path, "r+b") as stream:
                        stream.seek(-1, os.SEEK_END)
                        byte = stream.read(1)
                        stream.seek(-1, os.SEEK_END)
                        stream.write(bytes([byte[0] ^ 1]))
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                    self.assertEqual(os.stat(path).st_size, before.st_size)
                    self.assertEqual(os.stat(path).st_mtime_ns, before.st_mtime_ns)
                    changed = True
                return original(*args, **kwargs)

            result = os.path.join(root, "results", "a.json")
            with patch.object(r, "simulate", side_effect=mutate_after_loading):
                with self.assertRaisesRegex(r.FormatError, "data changed"):
                    r.run("STAGE_A", data, result)
            self.assertTrue(changed)
            self.assertFalse(os.path.exists(result))

    def test_equal_size_replacement_with_restored_mtime_changes_snapshot(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "fixture.zip")
            with open(path, "wb") as stream:
                stream.write(b"original")
            before = os.stat(path)
            initial = r.snapshot(root)
            replacement = os.path.join(root, "replacement.tmp")
            with open(replacement, "wb") as stream:
                stream.write(b"modified")
            os.utime(replacement, ns=(before.st_atime_ns, before.st_mtime_ns))
            os.replace(replacement, path)
            self.assertNotEqual(initial, r.snapshot(root))


class LiquidationExitCosts(unittest.TestCase):
    def test_liquidation_uses_exit_day_rank_at_base_and_stress_costs(self):
        entry, liquidation, n = D0 + 59, D0 + 99, 120
        syms = {}
        for i in range(21):
            name = f"S{i:02d}USDT"
            raw = {"funding": defaultdict(list), "spot": {}, "perp": {}}
            for day in range(D0, D0 + n):
                volume = 6e6 if i == 0 and day >= entry + 5 else 1e9 - i * 1e6
                raw["spot"][day] = {"high": 100.0, "close": 100.0, "qv": volume}
                raw["perp"][day] = {
                    "high": 130.0 if i == 0 and day == liquidation else 100.0,
                    "close": 100.0, "qv": volume,
                }
            for day in range(D0, D0 + n + 1):
                for hour in (0, 8, 16):
                    raw["funding"][day * r.DAY_MS + hour * 3_600_000].append(
                        0.0003 if i == 0 else 0.0
                    )
            syms[name] = r.SymData(name, raw)
        notional = r.CAP_W * 0.75
        entry_cost = notional * (r.FEE_SPOT + r.FEE_PERP + 2 * r.SLIP_TOP)
        exit_cost = notional * (r.FEE_SPOT + r.SLIP_REST)
        for mult in (1.0, 2.0):
            with self.subTest(cost_mult=mult):
                _, diag = r.simulate(syms, 0.20, mult, D0, D0 + n - 1)
                self.assertEqual(diag["liquidations"], 1)
                self.assertAlmostEqual(diag["components"]["fees"], mult * (entry_cost + exit_cost), places=12)
                self.assertAlmostEqual(diag["components"]["liquidation_penalty"],
                                       r.LIQ_PEN * notional * r.LIQ_MULT, places=12)


class PublishedStageAuthentication(unittest.TestCase):
    def test_stage_b_uses_the_same_stage_a_bytes_it_authenticated(self):
        # Simulate a concurrent replacement immediately after the first read:
        # the published digest belongs to theta 0.05, while the new file would
        # consistently select 0.20. No sealed ZIP is opened in this fixture.
        with tempfile.TemporaryDirectory() as root:
            data = fixtures.fixture(root, 100)
            fixtures.write_manifest(data, "STAGE_B")
            stage_a = os.path.join(root, "stage_a.json")
            payload = {
                "stage": "STAGE_A", "harness_sha256": r.sha256_file(r.__file__),
                "selected_theta": 0.05,
                "cells": {str(th): {"base": {"sharpe_annual": 5.0 if th == 0.05 else 0.0}}
                          for th in r.THETAS},
            }
            published = json.dumps(payload, sort_keys=True).encode()
            payload["selected_theta"] = 0.20
            payload["cells"]["0.05"]["base"]["sharpe_annual"] = 0.0
            payload["cells"]["0.2"]["base"]["sharpe_annual"] = 5.0
            replacement = json.dumps(payload, sort_keys=True).encode()
            with open(stage_a, "wb") as stream:
                stream.write(published)
            original_open = open
            stage_a_opens = 0

            @contextmanager
            def open_stage_a(*args, **kwargs):
                nonlocal stage_a_opens
                stage_a_opens += 1
                with original_open(*args, **kwargs) as stream:
                    yield stream
                if stage_a_opens == 1:
                    with original_open(stage_a, "wb") as stream:
                        stream.write(replacement)

            def guarded_open(path, *args, **kwargs):
                if os.fspath(path) == stage_a:
                    return open_stage_a(path, *args, **kwargs)
                return original_open(path, *args, **kwargs)

            with patch("builtins.open", side_effect=guarded_open):
                result = r.run("STAGE_B", data, os.path.join(root, "results", "b.json"),
                               stage_a, stage_a_sha256=hashlib.sha256(published).hexdigest())
            self.assertEqual(result["selected_theta"], 0.05)
            self.assertEqual(stage_a_opens, 1)


if __name__ == "__main__":
    unittest.main()
