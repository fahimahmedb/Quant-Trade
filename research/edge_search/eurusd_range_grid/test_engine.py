"""Causal and adversarial accounting checks; generated fixtures only."""
import json
import math
import unittest
from datetime import datetime,timezone

from engine import (Bar,BarBuilder,Indicators,Path,Engine,Order,Basket,
    Quote,CENTRAL,STRESS,BAR_MS,START,END,at,encode,state_roundtrip,mean_stats)


def book(t,mid=1.1,spread=.0001):
    return Quote(t,mid-spread/2,mid+spread/2)


def active_path(expression="MAIN",direction=1,costs=CENTRAL):
    t=at("2025-02-03",8);last=book(t-1000)
    p=Path(expression,costs,current_day="2025-02-03")
    p.opportunity(t,last,direction,1.1,.001,.001)
    q=book(t+1000)
    p.on_quote(q,last)
    return p,q


class IndicatorTests(unittest.TestCase):
    def test_exact_wilder_seed_and_flat_denominators(self):
        i=Indicators()
        for k in range(28):
            old,rsi,adx,_=i.update(Bar((k+1)*BAR_MS,1,1,1))
            if k<14:self.assertIsNone(rsi)
            if k<27:self.assertIsNone(adx)
        self.assertEqual((rsi,adx),(50,0))

    def test_one_way_trend_rsi_and_adx(self):
        for sign in (-1,1):
            i=Indicators()
            for k in range(40):
                p=1+sign*k*.001
                _,rsi,adx,_=i.update(Bar((k+1)*BAR_MS,p,p,p))
            self.assertEqual(rsi,100 if sign==1 else 0)
            self.assertAlmostEqual(adx,100)

    def test_missing_bar_removes_crossing_and_return(self):
        i=Indicators(previous=Bar(BAR_MS,1,1,1),rsi=29,adx=10)
        i.reset()
        self.assertEqual(i.update(Bar(3*BAR_MS,1.2,1.2,1.2)),(None,None,None,None))

    def test_dm_ties_do_not_invent_direction(self):
        i=Indicators(previous=Bar(BAR_MS,1.01,.99,1.0))
        i.update(Bar(2*BAR_MS,1.02,.98,1.0))
        self.assertEqual((i.plus,i.minus),(0,0))

    def test_bar_never_borrows_quote_at_boundary(self):
        b=BarBuilder(0)
        for t in range(0,BAR_MS,60000):b.add(book(t))
        b.add(book(BAR_MS-1000,1.11))
        self.assertAlmostEqual(b.finish().close,1.11)
        with self.assertRaises(ValueError):b.add(book(BAR_MS,2))

    def test_unobserved_interval_is_not_forward_filled(self):
        b=BarBuilder(0);b.add(book(0));b.add(book(BAR_MS-1000))
        self.assertIsNone(b.finish())

    def test_bar_validity_exact_sixty_second_boundaries(self):
        b=BarBuilder(0)
        for t in range(60000,BAR_MS,60000):b.add(book(t))
        self.assertIsNotNone(b.finish())
        b.first=60001
        self.assertIsNone(b.finish())


class LifecycleTests(unittest.TestCase):
    def test_initial_fill_is_delayed_and_costed(self):
        p,q=active_path()
        b=p.basket
        self.assertEqual(len(b.entries),1)
        self.assertEqual(b.first_fill,b.signal_time+1000)
        self.assertGreater(b.entries[0][1],q.ask)
        self.assertLess(p.nav(q),100000)
        self.assertGreater(p.commission,0)

    def test_stop_cancels_pending_add_before_fill(self):
        p,last=active_path();b=p.basket;t=last.time_ms
        trigger=book(t+1000,b.anchor-b.spacing-.0001)
        p.clock(trigger.time_ms,last);p.on_quote(trigger,last)
        self.assertEqual(b.pending.kind,"OPEN")
        stop=book(t+2000,b.stop-.0002)
        p.clock(stop.time_ms,trigger);p.on_quote(stop,trigger)
        self.assertEqual(b.pending.kind,"CLOSE")
        self.assertEqual(len(b.entries),1)
        later=book(t+3000,b.stop-.0003)
        p.clock(later.time_ms,stop);p.on_quote(later,stop)
        self.assertIsNone(p.basket)
        self.assertEqual(len(p.completed[0]["fills"]),2)
        self.assertLess(p.completed[0]["net_pnl"],0)

    def test_no_adds_expression_never_places_second_rung(self):
        p,last=active_path("NO_ADDS")
        for k in range(1,5):
            q=book(last.time_ms+1000,p.basket.anchor-p.basket.spacing-.0001)
            p.clock(q.time_ms,last);p.on_quote(q,last);last=q
        self.assertEqual(len(p.basket.entries),1)
        self.assertIsNone(p.basket.pending)

    def test_one_group_cannot_retroactively_fill_multiple_rungs(self):
        p,last=active_path();b=p.basket
        q=book(last.time_ms+1000,b.anchor-2*b.spacing-.0001)
        p.clock(q.time_ms,last);p.on_quote(q,last)
        self.assertEqual(len(b.entries),1)
        self.assertEqual(b.pending.rung,1)
        next_q=book(q.time_ms+1000,b.anchor-2*b.spacing-.0001)
        p.clock(next_q.time_ms,q);p.on_quote(next_q,q)
        self.assertEqual(len(b.entries),2)
        self.assertIsNone(b.pending)

    def test_stale_gap_strictly_greater_than_five_seconds(self):
        p,last=active_path()
        p.clock(last.time_ms+5000,last)
        self.assertIsNone(p.basket.pending)
        p.clock(last.time_ms+5001,last)
        self.assertEqual(p.basket.pending.reason,"STALE")
        self.assertEqual(p.basket.pending.intent.time_ms,last.time_ms+5000)
        self.assertEqual(p.basket.pending.source_time,last.time_ms)

    def test_failed_close_waits_and_charges_actual_rollover_interval(self):
        p,last=active_path();b=p.basket
        later=book(at("2025-02-03",23),.9)
        p.clock(later.time_ms,last)
        self.assertEqual(b.rollovers,1)
        self.assertGreater(b.financing,0)
        p.on_quote(later,last)
        self.assertIsNone(p.basket)
        self.assertIn("ROLLOVER",p.risk_failures)
        self.assertLess(p.completed[0]["net_pnl"],-b.risk)

    def test_cash_and_basket_net_ledger_conserve_exact_costs(self):
        for direction in (-1,1):
            for costs in (CENTRAL,STRESS):
                p,last=active_path(direction=direction,costs=costs);b=p.basket
                target=book(last.time_ms+1000,b.target+direction*.0002)
                p.clock(target.time_ms,last);p.on_quote(target,last)
                close=book(target.time_ms+1000,b.target+direction*.0003)
                p.clock(close.time_ms,target);p.on_quote(close,target)
                self.assertIsNone(p.basket)
                r=p.completed[0]
                self.assertAlmostEqual(p.cash-100000,r["net_pnl"],places=9)
                self.assertAlmostEqual(r["gross_mid_pnl"]-r["spread_cost"]-r["slippage_cost"]
                                       -r["commission"]-r["financing"],r["net_pnl"],places=9)

    def test_basket_anchor_stop_target_never_move_after_adverse_add(self):
        p,last=active_path();b=p.basket
        fixed=(b.anchor,b.stop,b.target,b.risk,b.quantity)
        for k in range(2):
            q=book(last.time_ms+1000,b.anchor-b.spacing-.0001)
            p.clock(q.time_ms,last);p.on_quote(q,last);last=q
        self.assertEqual(fixed,(b.anchor,b.stop,b.target,b.risk,b.quantity))

    def test_equity_drawdown_disable_survives_new_opportunity(self):
        p,last=active_path();q=book(last.time_ms+1000,.5)
        p.clock(q.time_ms,last);p.on_quote(q,last)
        self.assertTrue(p.disabled)
        later=book(q.time_ms+1000,.5);p.clock(later.time_ms,q);p.on_quote(later,q)
        self.assertIsNone(p.basket)
        p.opportunity(later.time_ms,later,1,1.1,.001,.001)
        self.assertIsNone(p.basket)

    def test_initial_expiry_has_no_hidden_position(self):
        t=at("2025-02-03",8);p=Path("MAIN",CENTRAL,current_day="2025-02-03")
        last=book(t-1000);p.opportunity(t,last,1,1.1,.001,.001)
        p.on_quote(book(t+6001),last)
        self.assertIsNone(p.basket);self.assertEqual(p.cash,100000)

    def test_fill_cap_uses_equity_after_all_prospective_side_costs(self):
        t=at("2025-02-03",8)
        p=Path("MAIN",CENTRAL,cash=1100.06,peak=1100.06,day_equity=1100.06)
        intent=book(t,1.1,.000001)
        p.basket=Basket(1,1.1,.00001,1.09999,1.100005,10,1000,1,t,
                       pending=Order("OPEN",intent,t,"SIGNAL"))
        p.on_quote(book(t+1000,1.1,.000001),intent)
        self.assertIsNone(p.basket)
        self.assertEqual(p.cash,1100.06)

    def test_opening_cost_can_immediately_trip_drawdown_gate(self):
        t=at("2025-02-03",8);last=book(t-1000)
        p=Path("MAIN",CENTRAL,cash=95000.1,day_equity=95000.1,current_day="2025-02-03")
        p.opportunity(t,last,1,1.1,.001,.001)
        p.on_quote(book(t+1000),last)
        self.assertTrue(p.disabled)
        self.assertEqual(p.basket.pending.kind,"CLOSE")
        self.assertIn("DRAWDOWN",p.risk_failures)


class CausalAndStatisticsTests(unittest.TestCase):
    def test_streaming_warmup_to_final_result_on_generated_calendar(self):
        from engine import WARMUP_START
        e=Engine()
        for k in range(15*24*60):
            e.feed(book(WARMUP_START+k*60000,1.1+.0002*math.sin(k/7),.00001))
        # Fixed calendar is retained despite almost all future sessions missing.
        for k in range(12*60):
            e.feed(book(at("2026-09-30",5)+k*60000,1.1+.0002*math.sin(k/7),.00001))
        r=e.finalize()
        self.assertTrue(e.warmup_done)
        self.assertGreater(r["sigma_reference"],0)
        self.assertEqual(len(r["paths"]),6)
        self.assertEqual(r["verdict"]["RESULT"],"SOURCE_GATE_FAILED")
        self.assertEqual(len(r["paths"]["MAIN_CENTRAL"]["daily"]),433)
        self.assertGreater(len(r["qa"]["unqualified_days"]),400)
        self.assertEqual(len(r["verdict"]),9)

    def test_fixed_warmup_is_required_before_any_signal(self):
        e=Engine()
        with self.assertRaisesRegex(ValueError,"WARMUP_TOO_SHORT"):
            e.feed(book(START+1000))

    def test_warmup_reference_and_state_have_exact_registered_recursion(self):
        rs=[.001*math.sin(i) for i in range(1100)]
        e=Engine(warmup_returns=rs.copy());e.finish_warmup()
        self.assertAlmostEqual(e.reference,math.sqrt(sum(r*r for r in rs)/len(rs)))
        v=sum(r*r for r in rs[:96])/96
        for r in rs[96:]:v=.94*v+.06*r*r
        self.assertAlmostEqual(e.variance,v)
        saved=e.variance;e.finish_warmup();self.assertEqual(e.variance,saved)

    def test_json_saved_state_restart_preserves_open_order_and_cash(self):
        p,last=active_path();e=Engine(reference=.001,variance=.000001,warmup_done=True,
                                     paths=[p],last=last,builder=BarBuilder(last.time_ms//BAR_MS*BAR_MS),
                                     last_group_ms=last.time_ms)
        clone=state_roundtrip(e)
        self.assertEqual(encode(e),encode(clone))
        for k,mid in enumerate((1.0988,1.0988,1.1008,1.1009),1):
            q=book(last.time_ms+k*1000,mid)
            e.feed(q);clone.feed(q)
            self.assertEqual(encode(e),encode(clone))

    def test_future_suffix_never_changes_prior_ledger_or_opportunity(self):
        p,last=active_path();e=Engine(reference=.001,variance=.000001,warmup_done=True,
                                     paths=[p],last=last,builder=BarBuilder(last.time_ms//BAR_MS*BAR_MS),
                                     last_group_ms=last.time_ms)
        saved=json.loads(json.dumps(encode(e)))
        for k in range(1,5):e.feed(book(last.time_ms+k*1000,1.099))
        self.assertEqual(saved["fields"]["opportunities"],[])
        self.assertEqual(saved["fields"]["paths"][0]["fields"]["completed"],[])
        self.assertEqual(saved["fields"]["paths"][0]["fields"]["basket"]["fields"]["fills"][0]["price"],
                         e.paths[0].basket.fills[0]["price"])

    def test_weekend_financing_is_included_in_monday_return(self):
        e=Engine(reference=.001,variance=.000001,warmup_done=True)
        for p in e.paths:
            p.calendar_nav={"2025-02-07":100000.,"2025-02-08":99900.,
                            "2025-02-09":99800.,"2025-02-10":99700.}
        r=e.result();daily=r["paths"]["MAIN_CENTRAL"]["daily"]
        monday=next(d for d in daily if d["day"]=="2025-02-10")
        self.assertAlmostEqual(monday["return"],-.003)

    def test_end_window_residual_is_source_failure_not_profitable_close(self):
        p,last=active_path();e=Engine(paths=[p],last=last,reference=.001,variance=.000001,warmup_done=True)
        # Other five paths stay untouched to maintain the declared result schema.
        e.paths+=[Path(x,c) for x in ("MAIN","NO_ADDS","STATIC_GRID") for c in (CENTRAL,STRESS)
                  if not (x=="MAIN" and c==CENTRAL)]
        e.builder=BarBuilder(END-BAR_MS)
        result=e.finalize()
        self.assertEqual(result["verdict"]["RESULT"],"SOURCE_GATE_FAILED")
        self.assertIsNotNone(result["paths"]["MAIN_CENTRAL"]["residual"])
        self.assertEqual(len(p.completed),0)
        self.assertGreater(p.financing,0)

    def test_hac_uses_days_and_zero_days(self):
        r=mean_stats([.001,-.001]+[0.0]*431)
        self.assertEqual(r["n"],433)
        self.assertEqual(r["mean"],0)
        self.assertGreater(r["se_hac"],0)
        self.assertLess(r["ci95"][0],0)
        self.assertGreater(r["ci95"][1],0)

    def test_all_six_paths_and_two_paired_diagnostics_are_retained(self):
        r=Engine().result()
        self.assertEqual(len(r["paths"]),6)
        self.assertEqual(len(r["paired_central"]),2)
        self.assertEqual(r["verdict"]["RESULT"],"SOURCE_GATE_FAILED")
        self.assertEqual(len(r["verdict"]),9)


if __name__=="__main__":unittest.main()
