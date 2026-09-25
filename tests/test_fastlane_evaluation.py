"""Fast-lane evaluation engine, inference and verdict (``QUANT_FASTLANE_HPIT_V1``).

Every price, volume, action, mapping and benchmark return here is SYNTHETIC and
generated in-process from fixed seeds; nothing is market evidence. Outcome data
is only reachable through real grants: each scenario runs in a throw-away git
repository with a bare 'origin', a sealed/committed/pushed protocol and
committed vendor manifests, and the synthetic vendor re-verifies the grant on
every call exactly as the real adapter does.
"""

import copy
import gzip
import json
import math
import random
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from quant.fastlane import constructor as ct
from quant.fastlane import evaluation as ev
from quant.fastlane import frictions as fr
from quant.fastlane import inference as inf
from quant.fastlane import preregistration as pr
from quant.fastlane import prices as px
from quant.fastlane import verdict as vd
from quant.fastlane.firewall import LINEAGE_ID, Firewall
from tests.test_fastlane_firewall_prereg import DOC_SOURCE, final_protocol, git

SYNTH = "SYNTH"
DELIST_CODES = {"A": "CASH_ACQUISITION", "B": "BANKRUPTCY_OR_CAUSE", "S": "STOCK_MERGER",
                "Z": "UNKNOWN"}
HOLIDAYS = {(1, 1), (7, 4), (12, 25)}


def synthetic_calendar(start=date(2005, 10, 3), end=date(2026, 9, 30)):
    """SYNTHETIC vendor calendar: weekdays minus three fixed holidays."""
    out, d = [], start
    while d <= end:
        if d.weekday() < 5 and (d.month, d.day) not in HOLIDAYS:
            out.append(d)
        d += timedelta(days=1)
    return out


CALENDAR = synthetic_calendar()


def attestation(**changes):
    base = dict(vendor_id=SYNTH, includes_delisted=True,
                corporate_actions="RAW_PRICES_PLUS_ACTIONS_LEDGER", pit_security_mapping=True,
                license_note="synthetic test vendor", verified=True)
    base.update(changes)
    return px.VendorAttestation(**base)


class SynthVendor:
    """SYNTHETIC PriceVendor. Every data call re-verifies the grant (px.check_grant)."""

    vendor_id = SYNTH

    def __init__(self, bars, actions=None, mappings=None, spy=None, att=None,
                 calendar=CALENDAR):
        self.calendar = list(calendar)
        self._bars = bars
        self._actions = actions or {}
        self._maps = mappings or {}
        self._spy = spy or {}
        self._att = att or attestation()
        self.calls = 0

    def _check(self, grant, start, end):
        self.calls += 1
        px.check_grant(grant, start, end)

    def attestation(self):
        return self._att

    def sessions(self, start, end, *, grant):
        self._check(grant, start, end)
        return [d for d in self.calendar if start <= d <= end]

    def daily_bars(self, security_id, start, end, *, grant):
        self._check(grant, start, end)
        return [b for b in self._bars.get(security_id, []) if start <= b.session <= end]

    def corporate_actions(self, security_id, start, end, *, grant):
        self._check(grant, start, end)
        return [a for a in self._actions.get(security_id, []) if start <= a.ex_date <= end]

    def security_mappings(self, cik, *, grant):
        self._check(grant, grant.price_window_start, grant.price_window_end)
        return px.clip_mappings(self._maps.get(cik, []), grant)

    def benchmark_total_returns(self, start, end, *, grant):
        self._check(grant, start, end)
        return {d: r for d, r in self._spy.items() if start <= d <= end}


def cik(i):
    return f"{9000000 + i:010d}"


def sid(i):
    return f"S{i:03d}"


def event_row(n, issuer, day, owners, value=50_000.0):
    """One compact primary-table row (see events.COMPACT_FIELDS); SYNTHETIC."""
    return {"accession": f"{9000000000 + n:010d}-{day.year % 100:02d}-{n:06d}",
            "quarter": f"{day.year}q{(day.month - 1) // 3 + 1}", "issuer_cik": issuer,
            "filing_date": day.isoformat(), "ticker_as_filed": "SYN", "value_usd": value,
            "shares": value / 20.0, "filing_lag_days": 2,
            "owners": [[o, role, 1 if role == "DIRECTOR" else 0, 0 if role == "DIRECTOR" else 1, 0]
                       for o, role in owners],
            "tx": [[(day - timedelta(days=2)).isoformat(), value / 20.0, 20.0, "D"]]}


def make_events(n_issuers, start, end, *, spacing, seed, pair_prob=0.5, ceo_prob=0.4,
                big_prob=0.0, weekend_prob=0.1):
    """SYNTHETIC insider-purchase filings: per issuer, a cluster every ~spacing sessions."""
    rng = random.Random(seed)
    rows, n = [], 0
    sessions = [d for d in CALENDAR if start <= d <= end]
    for i in range(n_issuers):
        k = rng.randrange(spacing)
        while k < len(sessions):
            day = sessions[k]
            if rng.random() < weekend_prob:
                day = day + timedelta(days=(5 - day.weekday()) % 7 or 7)   # a Saturday
            owners = [(f"{8000000 + i * 10 + 1:010d}",
                       "CEO_CFO" if rng.random() < ceo_prob else "DIRECTOR")]
            value = 2_000_000.0 if rng.random() < big_prob else 50_000.0
            rows.append(event_row(n, cik(i), day, owners, value))
            n += 1
            if rng.random() < pair_prob:
                later = sessions[min(k + rng.randrange(1, 4), len(sessions) - 1)]
                rows.append(event_row(n, cik(i), later,
                                      [(f"{8000000 + i * 10 + 2:010d}", "DIRECTOR")], value))
                n += 1
            k += spacing + rng.randrange(-3, 4)
    return rows


def spy_series(seed, calendar=CALENDAR, mu=0.0003, sd=0.01):
    rng = random.Random(seed)
    return {d: mu + sd * rng.gauss(0.0, 1.0) for d in calendar}


def entry_index(day, calendar=CALENDAR):
    import bisect
    return bisect.bisect_right(calendar, day)


def make_bars(n_issuers, spy, rows, *, seed, delta=0.0, boost_horizon=20, eps_sd=0.015,
              mirror_spy=False, first=None, last=None, calendar=CALENDAR, dollar_volume=5e6,
              filing_day_jump=0.0):
    """SYNTHETIC OHLCV: beta-1 on the synthetic SPY, idiosyncratic noise, an injected
    intraday drift ``delta`` on the ``boost_horizon`` sessions starting at each event's entry,
    and optionally a jump on the filing-day session of each cluster's first filing (a move
    that happens before any admissible entry and outside any earlier hold)."""
    rng = random.Random(seed)
    first = 0 if first is None else first
    last = len(calendar) - 1 if last is None else last
    boosted = {i: set() for i in range(n_issuers)}
    jumps = {i: set() for i in range(n_issuers)}
    index = {d: k for k, d in enumerate(calendar)}
    previous = {}
    for row in sorted(rows, key=lambda r: (r["issuer_cik"], r["filing_date"])):
        i = int(row["issuer_cik"]) - 9000000
        filed = date.fromisoformat(row["filing_date"])
        e = entry_index(filed, calendar)
        boosted.setdefault(i, set()).update(range(e, e + boost_horizon))
        if filed in index and e - previous.get(i, -10 ** 6) > boost_horizon + 1:
            jumps.setdefault(i, set()).add(index[filed])
        previous[i] = e
    bars = {}
    for i in range(n_issuers):
        close = 20.0 + i
        out = []
        for t in range(first, last + 1):
            d = calendar[t]
            rs = spy[d]
            if mirror_spy:
                o, c = close, close * (1.0 + rs)
            else:
                shock = rs + eps_sd * rng.gauss(0.0, 1.0)
                o = close * math.exp(0.3 * shock)
                c = close * math.exp(shock + (delta if t in boosted[i] else 0.0))
                if t in jumps[i]:
                    c *= 1.0 + filing_day_jump
            hi, lo = max(o, c) * 1.01, min(o, c) * 0.99
            out.append(px.DailyBar(sid(i), d, o, hi, lo, c, dollar_volume / c))
            close = c
        bars[sid(i)] = out
    return bars


def mappings_for(n_issuers):
    return {cik(i): [px.SecurityMapping(cik(i), sid(i), f"T{i}", date(2000, 1, 3), None)]
            for i in range(n_issuers)}


class EvalWorld:
    """Temp git repo + bare origin; synthetic event table bound, sealed, committed, pushed."""

    def __init__(self, tmp, rows, variant_ids, *, overrides=None):
        base = Path(tmp)
        self.remote, self.root = base / "remote.git", base / "work"
        self.root.mkdir()
        git(base, "init", "-q", "--bare", "-b", "main", str(self.remote))
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "remote", "add", "origin", str(self.remote))
        (self.root / "README").write_text("synthetic fast-lane evaluation repository\n")
        self.commit_all("base")
        self.publish()
        self.fw = Firewall(self.root)
        events = self.fw.artifact("data", "events_primary_v1.jsonl.gz")
        text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
        self.fw.write_bytes_atomic(events, gzip.compress(text.encode("utf-8"), mtime=0))
        self.protocol = final_protocol(self.fw.sha256_file(events),
                                       events.relative_to(self.root).as_posix())
        self.protocol["variants"] = [v for v in self.protocol["variants"]
                                     if v["variant_id"] in variant_ids]
        assert len(self.protocol["variants"]) == len(variant_ids), variant_ids
        self.protocol["multiplicity"]["M_declared"] = len(variant_ids)
        for dotted, value in (overrides or {}).items():
            node = self.protocol
            *head, leaf = dotted.split(".")
            for part in head:
                node = node[part]
            node[leaf] = value
        self.fw.write_json_atomic(pr.delisting_map_path(self.fw), {
            "lineage": LINEAGE_ID, "vendor_id": SYNTH, "derivation": "VENDOR_DOCUMENTATION_ONLY",
            "source": DOC_SOURCE, "mapping": DELIST_CODES})
        self.fw.write_json_atomic(pr.benchmark_manifest_path(self.fw), {
            "lineage": LINEAGE_ID, "series": "SPY", "return_type": "TOTAL_RETURN",
            "vendor_id": SYNTH, "dataset": "SYNTH/SFP", "fallback": "NONE"})
        self.record = pr.seal_protocol(self.fw, self.protocol)
        self.commit_all("seal")
        self.publish()
        self.sealed = pr.load_sealed(self.fw)
        self.table = ev.EventTable.load_bound(self.fw, self.protocol)

    @property
    def sha(self):
        return self.record["protocol_sha256"]

    def commit_all(self, msg):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "--allow-empty", "-m", msg)

    def publish(self):
        git(self.root, "push", "-q", "origin", "HEAD:main")

    def grant(self, split="discovery"):
        return pr.require_outcome_access(self.fw, split, self.sha)

    def market(self, vendor, split="discovery"):
        return ev.MarketData(vendor, self.grant(split), split)

    def evaluate(self, vendor, variant_id, *, market=None, **kw):
        market = market or self.market(vendor)
        return ev.evaluate_variant(sealed=self.sealed, variant_id=variant_id, table=self.table,
                                   market=market, context=ev.VendorContext(self.fw, vendor), **kw)


N_ISSUERS = 16
EFFECT = 0.002
ENGINE_VARIANTS = ["OD_V10K_H20", "CEO_CFO_V10K_H5"]


class EngineTests(unittest.TestCase):
    """One sealed world, several synthetic vendors (effect, SPY mirror, perturbed, delisted)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.rows = make_events(N_ISSUERS, date(2016, 1, 4), date(2018, 12, 28), spacing=25,
                               seed=11)
        cls.w = EvalWorld(cls.tmp.name, cls.rows, ENGINE_VARIANTS)
        cls.spy = spy_series(5)
        first = entry_index(date(2015, 9, 1))
        last = entry_index(date(2018, 12, 31)) - 1
        cls.bars = make_bars(N_ISSUERS, cls.spy, cls.rows, seed=3, delta=EFFECT, first=first,
                             last=last)
        cls.vendor = SynthVendor(cls.bars, mappings=mappings_for(N_ISSUERS), spy=cls.spy)
        cls.market = cls.w.market(cls.vendor)
        cls.result = cls.w.evaluate(cls.vendor, "OD_V10K_H20", market=cls.market,
                                    keep_positions=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_injected_effect_is_recovered_with_a_small_bootstrap_p(self):
        s = self.result["summary"]
        self.assertGreater(self.result["counts"]["admitted"], 300)
        self.assertAlmostEqual(s["gross"]["alpha_annual"], 252 * EFFECT, delta=0.12)
        net = self.result["series"]["r_ex"]["net"]
        boot = inf.studentized_block_bootstrap(net, block=80, draws=2000, seed=20260924)
        self.assertLess(boot["p_value"], 0.01)
        self.assertGreater(boot["upper_bound_annual"], s["net"]["alpha_annual"])
        hac = inf.fixed_b_hac_test(net, b=0.1)
        self.assertLess(hac["p_value"], 0.01)
        self.assertEqual(hac["critical_value"], inf.fixed_b_critical_value(0.05))

    def test_outputs_are_deterministic_and_fingerprinted(self):
        again = self.w.evaluate(self.vendor, "OD_V10K_H20", market=self.market,
                                keep_positions=True)
        self.assertEqual(again["output_digest"], self.result["output_digest"])
        fp = self.result["fingerprint"]
        for key in ("code_fingerprint", "prereg_sha256", "events_digest", "vendor"):
            self.assertIn(key, fp)
        self.assertEqual(fp["prereg_sha256"], self.w.sha)
        self.assertEqual(fp["events_digest"], self.w.table.digest)
        self.assertEqual(set(fp["vendor"]["manifest_sha256"]),
                         {"delisting_map", "benchmark_manifest"})
        other_seed = self.w.evaluate(self.vendor, "OD_V10K_H20", market=self.market, seed=7)
        self.assertNotEqual(other_seed["fingerprint"]["digest"], fp["digest"])

    def test_frictions_strictly_reduce_returns_and_stress_reduces_further(self):
        s = self.result["summary"]
        self.assertGreater(s["gross"]["alpha_annual"], s["net"]["alpha_annual"])
        self.assertGreater(s["net"]["alpha_annual"], s["net_friction_stress"]["alpha_annual"])
        self.assertGreater(s["gross"]["pnl_usd"], s["net"]["pnl_usd"])
        self.assertGreater(s["net"]["pnl_usd"], s["net_friction_stress"]["pnl_usd"])
        self.assertAlmostEqual(s["net_friction_stress"]["costs_usd"], 2 * s["net"]["costs_usd"],
                               delta=0.02 * s["net"]["costs_usd"])
        for p in self.result["positions"]:
            self.assertGreater(p["pnl_usd"]["gross"], p["pnl_usd"]["net"])
            self.assertGreater(p["pnl_usd"]["net"], p["pnl_usd"]["net_friction_stress"])

    def test_entry_timing_and_allocation(self):
        for p in self.result["positions"][:50]:
            filed = date.fromisoformat(p["filing_date"])
            entry = date.fromisoformat(p["entry_session"])
            self.assertGreater(entry, filed)
            self.assertEqual(entry, px.first_session_strictly_after(filed, CALENDAR))
            e = CALENDAR.index(entry)
            self.assertEqual(p["scheduled_exit_session"], CALENDAR[e + 19].isoformat())
            self.assertEqual(p["exit_session"], p["scheduled_exit_session"])
            self.assertAlmostEqual(p["notional_usd"], min(100_000 / 100, 0.001 * p["adv20_usd"]))

    def test_no_look_ahead_in_adv20_or_admission(self):
        params = ev.Params.from_protocol(self.w.protocol)
        variant = ev.Variant.from_protocol(self.w.protocol, "OD_V10K_H20")
        base = ev.candidates(variant, self.w.table, self.market, params)
        rng = random.Random(99)
        picks = rng.sample([c for c in base if c.reason is None], 3)
        before = ev.evaluate_variant(sealed=self.w.sealed, variant_id="OD_V10K_H20",
                                     table=self.w.table, market=self.market,
                                     context=ev.VendorContext(self.w.fw, self.vendor),
                                     scenarios=("gross",), keep_positions=True)
        for pick in picks:
            e = pick.entry_index
            bars = copy.copy(self.bars)
            bars[pick.security_id] = [
                b if CALENDAR.index(b.session) < e else
                px.DailyBar(b.security_id, b.session, b.open * 3, b.high * 3, b.low * 3,
                            b.close * 3, b.volume * 50) for b in self.bars[pick.security_id]]
            vendor = SynthVendor(bars, mappings=mappings_for(N_ISSUERS), spy=self.spy)
            market = self.w.market(vendor)
            again = {(c.issuer, c.filing_date): c
                     for c in ev.candidates(variant, self.w.table, market, params)}
            twin = again[(pick.issuer, pick.filing_date)]
            self.assertEqual(twin.adv20, pick.adv20)
            self.assertEqual(twin.reason, pick.reason)
            after = ev.evaluate_variant(sealed=self.w.sealed, variant_id="OD_V10K_H20",
                                        table=self.w.table, market=market,
                                        context=ev.VendorContext(self.w.fw, vendor),
                                        scenarios=("gross",), keep_positions=True)

            def admitted_through(result):
                return sorted((p["issuer"], p["entry_session"]) for p in result["positions"]
                              if CALENDAR.index(date.fromisoformat(p["entry_session"])) <= e)
            self.assertEqual(admitted_through(before), admitted_through(after))

    def test_filing_day_move_is_never_captured(self):
        # forbidden interval dominates: a +10 % jump on every filing-day session would add
        # ~126 %/yr if entry were at or before that close; entry is strictly after it
        bars = make_bars(N_ISSUERS, self.spy, self.rows, seed=3, filing_day_jump=0.10,
                         first=self.market.index[self.bars[sid(0)][0].session],
                         last=self.market.index[self.bars[sid(0)][-1].session])
        vendor = SynthVendor(bars, mappings=mappings_for(N_ISSUERS), spy=self.spy)
        result = self.w.evaluate(vendor, "OD_V10K_H20", scenarios=("gross",))
        self.assertLess(abs(result["summary"]["gross"]["alpha_annual"]), 0.15)

    def test_purge_at_the_split_end(self):
        counts = self.result["counts"]
        self.assertGreater(counts[ev.REASON_PURGED], 0)
        end = pr.SPLITS["discovery"][1]
        for p in self.result["positions"]:
            self.assertLessEqual(date.fromisoformat(p["scheduled_exit_session"]), end)
        params = ev.Params.from_protocol(self.w.protocol)
        variant = ev.Variant.from_protocol(self.w.protocol, "OD_V10K_H20")
        for c in ev.candidates(variant, self.w.table, self.market, params):
            if c.reason == ev.REASON_PURGED:
                e = entry_index(c.filing_date)
                self.assertTrue(e + 19 >= len(self.market.calendar)
                                or CALENDAR[e + 19] > end)
        self.assertLessEqual(self.market.calendar[-1], end)             # no holdout price

    def test_cash_drag_is_never_counted_as_alpha(self):
        bars = make_bars(N_ISSUERS, self.spy, self.rows, seed=3, mirror_spy=True,
                         first=self.market.index[self.bars[sid(0)][0].session],
                         last=self.market.index[self.bars[sid(0)][-1].session])
        vendor = SynthVendor(bars, mappings=mappings_for(N_ISSUERS), spy=self.spy)
        result = self.w.evaluate(vendor, "OD_V10K_H20")
        self.assertLess(abs(result["summary"]["gross"]["alpha_annual"]), 1e-9)
        self.assertLess(result["summary"]["net"]["alpha_annual"], 0.0)       # frictions only
        idle = result["idle_cash"]
        self.assertGreater(idle["idle_cash_share_mean_over_span"], 0.5)      # mostly idle cash
        self.assertGreater(idle["spy_total_return_annual_same_span"], 0.0)
        self.assertLess(idle["c0_basis_return_annual_idle_cash_at_0"],
                        idle["spy_total_return_annual_same_span"])          # drag exists...
        self.assertTrue(all(abs(v) < 1e-12 for v in result["series"]["r_ex"]["gross"]
                            if v is not None))                               # ...but not in r_ex

    def test_benchmark_has_no_fallback(self):
        spy = dict(self.spy)
        del spy[CALENDAR[entry_index(date(2017, 3, 1)) + 3]]
        vendor = SynthVendor(self.bars, mappings=mappings_for(N_ISSUERS), spy=spy)
        with self.assertRaises(ev.BenchmarkMissing):
            self.w.evaluate(vendor, "OD_V10K_H20")

    def test_vendor_manifests_must_name_the_vendor(self):
        class Other(SynthVendor):
            vendor_id = "OTHER"
        with self.assertRaises(ev.VendorMismatch):
            ev.VendorContext(self.w.fw, Other(self.bars))

    def test_market_data_needs_a_real_grant(self):
        forged = pr.OutcomeAccessGrant(LINEAGE_ID, "discovery", self.w.sha, date(2005, 10, 1),
                                       date(2018, 12, 31), None, str(self.w.root), "0" * 64)
        with self.assertRaises(pr.OutcomeAccessRefused):
            ev.MarketData(self.vendor, forged, "discovery")
        with self.assertRaises(pr.OutcomeAccessRefused):
            ev.MarketData(self.vendor, self.w.grant("discovery"), "walk_forward")

    def test_delisting_classes_produce_the_sealed_returns(self):
        params = ev.Params.from_protocol(self.w.protocol)
        variant = ev.Variant.from_protocol(self.w.protocol, "OD_V10K_H20")
        cand = next(c for c in ev.candidates(variant, self.w.table, self.market, params)
                    if c.reason is None and c.security_id == sid(0))
        e = cand.entry_index
        stop = CALENDAR[e + 6]                                  # last trade mid-hold
        expected = {"A": ("CASH_ACQUISITION", 0.0, 0.0), "B": ("BANKRUPTCY_OR_CAUSE", -1.0, -1.0),
                    "S": ("STOCK_MERGER", 0.0, 0.0), "Z": ("UNKNOWN", -0.3, -1.0),
                    "QQ": ("UNKNOWN", -0.3, -1.0), None: ("UNKNOWN", -0.3, -1.0)}
        for code, (cls_name, base, stress) in expected.items():
            bars = dict(self.bars)
            bars[sid(0)] = [b for b in self.bars[sid(0)]
                            if b.session <= stop or b.session > CALENDAR[e + 60]]
            actions = {} if code is None else {sid(0): [px.CorporateAction(
                sid(0), CALENDAR[e + 7], px.ACTION_DELISTING, None, code)]}
            vendor = SynthVendor(bars, actions=actions, mappings=mappings_for(N_ISSUERS),
                                 spy=self.spy)
            market = self.w.market(vendor)
            plan = ev.plan_position(market, cand, 0, variant, params, 1.0,
                                    ev.VendorContext(self.w.fw, vendor).delisting_map)
            self.assertEqual(plan.exit_kind, ev.EXIT_DELISTING)
            self.assertEqual(plan.delisting_class, cls_name)
            self.assertEqual(plan.delist_index, e + 7)
            for scenario, extra in (("net", base), ("net_delisting_stress", stress)):
                sim = ev.simulate(plan, scenario, params)
                idx, w, r = sim["rows"][-1]
                self.assertEqual((idx, r), (e + 7, extra))
                self.assertAlmostEqual(sim["final_value"], w * (1.0 + extra))
                self.assertEqual(sim["cost_out"], 0.0)
            last_close = next(b.close for b in bars[sid(0)] if b.session == stop)
            gross = ev.simulate(plan, "gross", params)
            self.assertAlmostEqual(gross["rows"][-1][1], plan.shares * last_close, places=6)

    def test_missing_exit_bar_exits_at_the_next_open(self):
        params = ev.Params.from_protocol(self.w.protocol)
        variant = ev.Variant.from_protocol(self.w.protocol, "OD_V10K_H20")
        cand = next(c for c in ev.candidates(variant, self.w.table, self.market, params)
                    if c.reason is None and c.security_id == sid(1))
        e = cand.entry_index
        x = e + 19
        bars = dict(self.bars)
        bars[sid(1)] = [b for b in self.bars[sid(1)]
                        if b.session not in (CALENDAR[x], CALENDAR[x + 1], CALENDAR[e + 5])]
        vendor = SynthVendor(bars, mappings=mappings_for(N_ISSUERS), spy=self.spy)
        market = self.w.market(vendor)
        plan = ev.plan_position(market, cand, 0, variant, params, 1.0, {})
        self.assertEqual((plan.exit_kind, plan.exit_index), (ev.EXIT_NEXT_OPEN, x + 2))
        self.assertEqual(plan.exit_price, next(b.open for b in bars[sid(1)]
                                               if b.session == CALENDAR[x + 2]))
        self.assertEqual(dict(plan.path)[e + 5], 0.0)            # stale carry mid-hold

    def test_split_adjusted_total_return(self):
        params = ev.Params.from_protocol(self.w.protocol)
        variant = ev.Variant.from_protocol(self.w.protocol, "OD_V10K_H20")
        cand = next(c for c in ev.candidates(variant, self.w.table, self.market, params)
                    if c.reason is None and c.security_id == sid(2))
        e = cand.entry_index
        split_at = e + 5
        bars = dict(self.bars)
        bars[sid(2)] = [b if CALENDAR.index(b.session) < split_at else
                        px.DailyBar(b.security_id, b.session, b.open / 2, b.high / 2, b.low / 2,
                                    b.close / 2, b.volume * 2) for b in self.bars[sid(2)]]
        actions = {sid(2): [px.CorporateAction(sid(2), CALENDAR[split_at], px.ACTION_SPLIT, 2.0),
                            px.CorporateAction(sid(2), CALENDAR[split_at + 2],
                                               px.ACTION_CASH_DIVIDEND, 0.0)]}
        split_vendor = SynthVendor(bars, actions=actions, mappings=mappings_for(N_ISSUERS),
                                   spy=self.spy)
        split_plan = ev.plan_position(self.w.market(split_vendor), cand, 0, variant, params, 1.0,
                                      {})
        plain_plan = ev.plan_position(self.market, cand, 0, variant, params, 1.0, {})
        for (i, g1), (j, g2) in zip(split_plan.path, plain_plan.path):
            self.assertEqual(i, j)
            self.assertAlmostEqual(g1, g2, places=12)


class CalendarTests(unittest.TestCase):
    def test_vendor_calendar_must_cover_what_the_rules_need(self):
        check = ev.MarketData._check_calendar
        disc = [d for d in CALENDAR if date(2005, 10, 1) <= d <= date(2018, 12, 31)]
        self.assertEqual(check(disc, "discovery", date(2005, 10, 1), date(2018, 12, 31)), disc)
        gap = [d for d in disc if not date(2012, 3, 1) <= d <= date(2012, 3, 20)]
        short = [d for d in disc if d <= date(2018, 11, 30)]
        late = [d for d in disc if d >= date(2005, 12, 20)]
        for bad in (gap, short, late, list(reversed(disc)), []):
            with self.assertRaises(ev.CalendarIncomplete):
                check(bad, "discovery", date(2005, 10, 1), date(2018, 12, 31))
        hold = [d for d in CALENDAR if date(2021, 4, 1) <= d <= date(2026, 6, 30)]
        with self.assertRaises(ev.CalendarIncomplete):
            check(hold, "holdout", date(2021, 4, 1), date(2026, 9, 30))

    def test_holdout_exit_beyond_the_vendor_calendar_refuses(self):
        import types
        rows = [event_row(1, cik(1), date(2026, 6, 26), [(f"{7000001:010d}", "DIRECTOR")])]
        table = ev.EventTable(rows)
        protocol = final_protocol()
        params = ev.Params.from_protocol(protocol)
        variant = ev.Variant.from_protocol(protocol, "OD_V10K_H60")
        stub = types.SimpleNamespace(
            calendar=[d for d in CALENDAR if date(2021, 4, 1) <= d <= date(2026, 7, 31)],
            split="holdout", _candidates={})
        with self.assertRaises(ev.CalendarIncomplete):
            ev.candidates(variant, table, stub, params)


class CapacityAndTieBreakTests(unittest.TestCase):
    """Slot capacity with a burst larger than the book (protocol K overridden to 5)."""

    def test_slot_capacity_and_deterministic_tie_break(self):
        burst_day = date(2017, 3, 15)
        rows = [event_row(i, cik(i), burst_day, [(f"{7000000 + i:010d}", "DIRECTOR")])
                for i in range(8)]
        rows += make_events(8, date(2016, 1, 4), date(2016, 12, 30), spacing=40, seed=2)
        rows = [dict(r, accession=f"{r['accession'][:-6]}{k:06d}") for k, r in enumerate(rows)]
        spy = spy_series(1)
        with tempfile.TemporaryDirectory() as tmp:
            w = EvalWorld(tmp, rows, ["OD_V10K_H20"], overrides={"constructor.slots": 5})
            bars = make_bars(8, spy, rows, seed=4, first=entry_index(date(2015, 10, 1)),
                             last=entry_index(date(2017, 12, 29)))
            vendor = SynthVendor(bars, mappings=mappings_for(8), spy=spy)
            market = w.market(vendor)
            result = w.evaluate(vendor, "OD_V10K_H20", market=market, keep_positions=True)
            burst_entry = px.first_session_strictly_after(burst_day, CALENDAR).isoformat()
            burst = [p for p in result["positions"] if p["entry_session"] == burst_entry]
            self.assertEqual(len(burst), 5)
            self.assertGreaterEqual(result["counts"][ct.REJECT_BOOK_FULL], 3)
            keys = sorted((ct.tie_break_key(20260924, [r["accession"]]), r["issuer_cik"])
                          for r in rows if r["filing_date"] == burst_day.isoformat())
            self.assertEqual(sorted(p["issuer"] for p in burst),
                             sorted(issuer for _, issuer in keys[:5]))
            self.assertEqual(sorted(p["slot"] for p in burst), [0, 1, 2, 3, 4])
            again = w.evaluate(vendor, "OD_V10K_H20", market=market)
            self.assertEqual(again["admitted_digest"], result["admitted_digest"])
            other = w.evaluate(vendor, "OD_V10K_H20", market=market, seed=20260925)
            self.assertNotEqual(other["admitted_digest"], result["admitted_digest"])

    def test_constructor_capacity_at_the_sealed_k(self):
        entries = [ct.Entry(10, f"{i:010d}", (f"ACC-{i}",)) for i in range(150)]
        admitted, rejected = ct.admit_detailed(entries, slots=100, horizon=20, seed=20260924)
        self.assertEqual(len(admitted), 100)
        self.assertEqual(len(rejected), 50)
        shuffled = entries[:]
        random.Random(3).shuffle(shuffled)
        again, _ = ct.admit_detailed(shuffled, slots=100, horizon=20, seed=20260924)
        self.assertEqual([a.entry for a in admitted], [a.entry for a in again])
        self.assertEqual(sorted(a.slot for a in admitted), list(range(100)))
        self.assertEqual(ct.admit(entries, slots=100, horizon=20, seed=20260924),
                         [a.entry for a in admitted])


def ar1(n, phi, seed, mu=0.0):
    rng = inf.SplitMix64(seed)
    out, prev = [], 0.0
    while len(out) < n:
        for z in rng.normal_pair():
            prev = phi * prev + z * 0.01
            out.append(mu + prev)
    return out[:n]


class InferenceTests(unittest.TestCase):
    def test_null_p_values_are_not_anti_conservative(self):
        reps, rej_boot, rej_hac = 120, 0, 0
        for r in range(reps):
            x = ar1(640, 0.3, 1000 + r)
            if inf.studentized_block_bootstrap(x, block=80, draws=199, seed=r)["p_value"] <= 0.05:
                rej_boot += 1
            if inf.fixed_b_hac_test(x, b=0.1)["p_value"] <= 0.05:
                rej_hac += 1
        # 5 % nominal; binomial(120, 0.05) exceeds 13 with probability < 0.2 %
        self.assertLessEqual(rej_boot, 13)
        self.assertLessEqual(rej_hac, 13)

    def test_gaps_are_handled_as_a_ratio_mean(self):
        x = ar1(400, 0.2, 5, mu=0.001)
        gappy = [None if i % 7 == 3 else v for i, v in enumerate(x)]
        boot = inf.studentized_block_bootstrap(gappy, block=80, draws=300, seed=1)
        self.assertAlmostEqual(boot["mean"], inf.ratio_mean(gappy))
        self.assertEqual(boot["n_active"], sum(v is not None for v in gappy))
        again = inf.studentized_block_bootstrap(gappy, block=80, draws=300, seed=1)
        self.assertEqual(boot, again)                                   # seeded, deterministic

    def test_bartlett_identity_matches_direct_sum(self):
        x = ar1(300, 0.5, 9)
        m = sum(x) / len(x)
        u = [v - m for v in x]
        direct = sum(v * v for v in u) / 300 + 2 * sum(
            (1 - j / 30) * sum(u[t] * u[t + j] for t in range(300 - j)) / 300 for j in range(1, 30))
        self.assertAlmostEqual(inf.bartlett_lrv(u, 30), direct, places=12)
        self.assertAlmostEqual(inf.bartlett_lrv(u, 30.0000001), direct, places=6)

    def test_fixed_b_table_is_reproducible_in_distribution(self):
        table = inf._FIXED_B_QUANTILES
        self.assertEqual(tuple(p for p, _ in table), inf.FIXED_B_TAIL_PROBS)
        self.assertTrue(all(a[1] < b[1] for a, b in zip(table, table[1:])))
        small = inf.simulate_fixed_b_null(b=0.1, steps=400, reps=3000, seed=20260924)
        q05 = dict(inf.fixed_b_quantile_table(small, [0.05]))[0.05]
        self.assertAlmostEqual(q05, inf.fixed_b_critical_value(0.05), delta=0.12)
        self.assertGreater(inf.fixed_b_critical_value(0.05), 1.6449)   # fatter than normal
        self.assertAlmostEqual(inf.fixed_b_pvalue(inf.fixed_b_critical_value(0.05)), 0.05)
        self.assertAlmostEqual(inf.fixed_b_pvalue(0.0), 0.5)
        # Negative statistics are not deflated, so their p-value is never smaller than the
        # symmetric complement (conservative for a one-sided test).
        self.assertGreaterEqual(inf.fixed_b_pvalue(-1.0), 1.0 - inf.fixed_b_pvalue(1.0))

    def test_fixed_b_co_check_is_never_looser_than_kiefer_vogelsang(self):
        # Lead decision on C16: use the more conservative of the simulated table and the
        # Kiefer-Vogelsang (2005) Bartlett polynomials at every tabulated level.
        b = inf.FIXED_B_NULL["b"]
        self.assertGreaterEqual(inf.conservative_scale(), 1.0)
        for tail in inf.KV2005_BARTLETT_POLY:
            kv = inf._kv_poly(tail, b)
            self.assertGreaterEqual(inf.fixed_b_pvalue(kv), tail - 1e-9)
            self.assertGreaterEqual(inf.fixed_b_pvalue(inf._simulated_quantile(tail)), tail - 1e-9)
        self.assertAlmostEqual(inf.fixed_b_critical_value(0.05), inf._kv_poly(0.05, b), places=3)
        self.assertGreater(inf.fixed_b_pvalue(1.8373), 0.05)   # the raw simulated cv no longer rejects

    def test_holm_and_dsr(self):
        adj = inf.holm({"a": 0.01, "b": 0.04, "c": 0.03})
        for key, value in {"a": 0.03, "c": 0.06, "b": 0.06}.items():
            self.assertAlmostEqual(adj[key], value)
        self.assertEqual(inf.holm({"a": 0.2}), {"a": 0.2})
        m = inf.sharpe_moments(ar1(500, 0.0, 3, mu=0.002))
        one = inf.deflated_sharpe(sr=m["sr"], n_obs=m["n"], skew=m["skew"],
                                  kurtosis=m["kurtosis"], sr_variance=0.0, n_trials=22)
        many = inf.deflated_sharpe(sr=m["sr"], n_obs=m["n"], skew=m["skew"],
                                   kurtosis=m["kurtosis"], sr_variance=0.01, n_trials=44)
        self.assertEqual(one["sr0"], 0.0)
        self.assertGreater(many["sr0"], 0.0)
        self.assertLess(many["dsr"], one["dsr"])                        # deflation bites
        self.assertGreater(inf.expected_max_sharpe(0.01, 100), inf.expected_max_sharpe(0.01, 10))

    def test_romano_wolf_controls_and_orders(self):
        strong = ar1(800, 0.1, 1, mu=0.003)
        null1, null2 = ar1(800, 0.1, 2), ar1(800, 0.1, 3)
        rw = inf.romano_wolf_stepdown({"s": strong, "n1": null1, "n2": null2}, block=80,
                                      draws=299, seed=4)
        self.assertLess(rw["p_adjusted"]["s"], 0.05)
        self.assertGreater(min(rw["p_adjusted"]["n1"], rw["p_adjusted"]["n2"]), 0.05)
        self.assertLessEqual(rw["p_adjusted"]["s"], rw["p_adjusted"]["n1"])
        self.assertLess(rw["spa"]["p_value"], 0.05)


class VerdictTruthTableTests(unittest.TestCase):
    RULES = {"alpha_min_annual": 0.03, "holm_family_alpha": 0.05, "dsr_min": 0.95,
             "inconclusive_upper_bound_min_annual": 0.03, "inconclusive_ci_level_one_sided": 0.95}
    PASS = {"alpha_annual": 0.08, "pnl_usd": 5000.0, "p_bootstrap": 0.001, "p_hac": 0.002,
            "dsr": 0.99, "upper_bound_annual": 0.15}

    def decide(self, att=None, **changes):
        return vd.decide({"V1": {**self.PASS, **changes}}, att or attestation(), self.RULES)

    def test_go_needs_every_leg(self):
        self.assertEqual(self.decide()["verdict"], vd.VERDICT_GO)
        self.assertTrue(self.decide()["sizing_authorized"])
        failing = {"alpha_annual": 0.029, "p_bootstrap": 0.05, "p_hac": 0.051, "dsr": 0.95,
                   "pnl_usd": -1.0}
        for key, value in failing.items():
            d = self.decide(**{key: value})
            self.assertEqual(d["verdict"], vd.VERDICT_INCONCLUSIVE, key)   # UB 15 % >= 3 %
            self.assertFalse(d["sizing_authorized"])

    def test_inconclusive_versus_no_go_on_the_upper_bound(self):
        self.assertEqual(self.decide(p_hac=0.2, upper_bound_annual=0.03)["verdict"],
                         vd.VERDICT_INCONCLUSIVE)
        self.assertEqual(self.decide(p_hac=0.2, upper_bound_annual=0.0299)["verdict"],
                         vd.VERDICT_NO_GO)
        self.assertEqual(self.decide(alpha_annual=-0.02, pnl_usd=-10.0, p_bootstrap=0.9,
                                     p_hac=0.9, upper_bound_annual=0.01)["verdict"],
                         vd.VERDICT_NO_GO)

    def test_vendor_without_delisted_names_is_never_go(self):
        for att in (attestation(includes_delisted=False), attestation(verified=False),
                    attestation(pit_security_mapping=False)):
            d = self.decide(att)
            self.assertNotEqual(d["verdict"], vd.VERDICT_GO)
            self.assertFalse(d["per_finalist"]["V1"]["legs"]["vendor_go_eligible"])
        self.assertEqual(self.decide(attestation(includes_delisted=False))["evidence_label"],
                         px.LABEL_SURVIVORSHIP_BIASED)

    def test_zero_finalists_is_no_go_with_the_holdout_unopened(self):
        d = vd.decide({}, attestation(), self.RULES)
        self.assertEqual((d["verdict"], d["holdout"]), (vd.VERDICT_NO_GO, "UNOPENED"))
        self.assertFalse(d["sizing_authorized"])

    def test_holm_is_applied_across_finalists(self):
        three = {"V1": {**self.PASS, "p_bootstrap": 0.02}, "V2": {**self.PASS, "p_bootstrap": 0.2},
                 "V3": {**self.PASS, "p_bootstrap": 0.3}}
        d = vd.decide(three, attestation(), self.RULES)
        self.assertAlmostEqual(d["per_finalist"]["V1"]["p_bootstrap_holm"], 0.06)
        self.assertEqual(d["verdict"], vd.VERDICT_INCONCLUSIVE)          # 0.02 alone would pass
        one = vd.decide({"V1": three["V1"]}, attestation(), self.RULES)
        self.assertEqual(one["verdict"], vd.VERDICT_GO)
        mixed = vd.decide({"V1": self.PASS, "V2": {**self.PASS, "dsr": 0.5}}, attestation(),
                          self.RULES)
        self.assertEqual((mixed["verdict"], mixed["go_finalists"]), (vd.VERDICT_GO, ["V1"]))

    def test_upper_bound_takes_the_larger_of_both_tests(self):
        self.assertEqual(vd.upper_bound({"upper_bound_annual": 0.02},
                                        {"upper_bound_annual": 0.05}), 0.05)


if __name__ == "__main__":
    unittest.main()
