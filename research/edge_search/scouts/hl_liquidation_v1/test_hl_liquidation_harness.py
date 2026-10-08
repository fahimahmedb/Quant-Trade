import json
import unittest
from decimal import Decimal

import hl_liquidation_harness as h


def fill(user, side, crossed, tid, t, px="100", sz="10", liq=None):
    f = {"coin":"BTC","px":px,"sz":sz,"side":side,"time":t,
         "startPosition":"0","dir":"Close Long" if side=="A" else "Open Long",
         "closedPnl":"0","hash":"0xabc","oid":tid+1000,"crossed":crossed,
         "fee":"0","tid":tid,"feeToken":"USDC"}
    if liq is not None:
        f["liquidation"] = liq
    return [user, f]


def block(n, t, events):
    sec = t/1000
    import datetime
    dt = datetime.datetime.fromtimestamp(sec, datetime.timezone.utc).isoformat().replace('+00:00','Z')
    return json.dumps({"local_time":dt,"block_time":dt,"block_number":n,"events":events})


def bbo(t, bid, ask):
    return json.dumps({"channel":"bbo","data":{"coin":"BTC","time":t,"bbo":[{"px":str(bid),"sz":"1","n":1},{"px":str(ask),"sz":"1","n":1}]}})


class H(unittest.TestCase):
    def test_liquidation_vs_voluntary_fill(self):
        liq={"liquidatedUser":"0xliq","markPx":"99","method":"market"}
        lines=[block(1,1000,[fill("0xliq","A",True,1,1000,liq=liq),fill("0xmm","B",False,1,1000,liq=liq)]),
               block(2,2000,[fill("0xvol","B",True,2,2000),fill("0xmm2","A",False,2,2000)])]
        ts=h.canonicalize_trades(h.parse_fill_blocks(lines))
        self.assertTrue(ts[0].forced_market)
        self.assertEqual(ts[0].aggressor_side,"A")
        self.assertFalse(ts[1].forced_market)

    def test_duplicate_events_are_folded(self):
        liq={"liquidatedUser":"0xliq","markPx":"99","method":"market"}
        line=block(1,1000,[fill("0xliq","A",True,1,1000,liq=liq),fill("0xmm","B",False,1,1000,liq=liq)])
        rows=h.parse_fill_blocks([line,line])
        self.assertEqual(len(rows),2)
        self.assertEqual(len(h.canonicalize_trades(rows)),1)

    def test_out_of_order_timestamps_sorted_deterministically(self):
        lines=[block(2,2000,[fill("0xa","B",True,2,2000),fill("0xb","A",False,2,2000)]),
               block(1,1000,[fill("0xc","A",True,1,1000),fill("0xd","B",False,1,1000)])]
        ts=h.canonicalize_trades(h.parse_fill_blocks(lines))
        self.assertEqual([x.tid for x in ts],[1,2])

    def test_missing_l2_bbo_rejects_event_outcome(self):
        self.assertIsNone(h.executable_return([],"BTC",10_000,1))

    def test_multiple_forced_fills_aggregate_once_each(self):
        liq={"liquidatedUser":"0xliq","markPx":"99","method":"market"}
        lines=[block(1,1000,[fill("0xliq","A",True,1,1000,sz="2",liq=liq),fill("0xm1","B",False,1,1000,sz="2",liq=liq),
                             fill("0xliq2","A",True,2,1100,sz="3",liq=liq),fill("0xm2","B",False,2,1100,sz="3",liq=liq)])]
        bs=h.bucketize(h.canonicalize_trades(h.parse_fill_blocks(lines)))
        self.assertEqual(bs[("BTC",0)].forced_sell,Decimal("500"))

    def test_event_clustering_cooldown(self):
        # synthetic buckets with stable baseline, two qualifying forced bursts 10s apart -> one event
        bs={}
        for s in range(0,400_000,h.BUCKET_MS):
            x=h.Bucket("BTC",s); x.voluntary_buy=Decimal("100"); x.all_aggressive=Decimal("100"); bs[("BTC",s)]=x
        for s in (310_000,320_000):
            x=bs[("BTC",s)]; x.forced_buy=Decimal("120"); x.all_aggressive += Decimal("120")
        bb=[]
        for t in range(240_000,360_001,1000):
            bb.append(h.Bbo("BTC",t,Decimal("99.9"),Decimal("100.1")))
        ev=h.detect_events(bs,bb)
        starts=[e.bucket_start_ms for e in ev if e.bucket_start_ms in (310_000,320_000)]
        self.assertEqual(starts,[310_000])

    def test_quote_exchange_time_before_t0_but_received_after_t0_is_unavailable(self):
        bb=[h.Bbo("BTC",9_900,Decimal("99"),Decimal("101"),10_100),
            h.Bbo("BTC",9_800,Decimal("98"),Decimal("100"),9_900),
            h.Bbo("BTC",39_900,Decimal("100"),Decimal("102"),39_950)]
        # the fresher exchange quote was not locally received until after t0=10,000
        r=h.executable_return(bb,"BTC",10_000,1)
        self.assertIsNotNone(r)
        expected=Decimal("100")/Decimal("100")-1-Decimal("0.001")
        self.assertEqual(r,expected)

    def test_no_after_t0_leakage_for_entry(self):
        bb=[h.Bbo("BTC",9_999,Decimal("99"),Decimal("101")),
            h.Bbo("BTC",10_001,Decimal("199"),Decimal("201")),
            h.Bbo("BTC",40_000,Decimal("100"),Decimal("102"))]
        # entry must use 9,999 quote, never 10,001 future quote
        r=h.executable_return(bb,"BTC",10_000,1)
        self.assertIsNotNone(r)
        # entry ask 101; exit bid 100; fees 10bp total
        expected=Decimal("100")/Decimal("101")-1-Decimal("0.001")
        self.assertEqual(r,expected)


    def test_block_gap_fails_closed(self):
        a=block(1,1000,[fill("0xa","B",True,1,1000),fill("0xb","A",False,1,1000)])
        b=block(3,3000,[fill("0xc","B",True,2,3000),fill("0xd","A",False,2,3000)])
        with self.assertRaises(h.DataError):
            h.validate_block_continuity([a,b])

    def test_adl_not_counted_as_voluntary(self):
        f1=fill("0xa","B",True,1,1000); f1[1]["dir"]="Auto-Deleveraging"
        f2=fill("0xb","A",False,1,1000); f2[1]["dir"]="Close Long"
        bs=h.bucketize(h.canonicalize_trades(h.parse_fill_blocks([block(1,1000,[f1,f2])])))
        self.assertEqual(bs, {})

    def test_conflicting_duplicate_block_fails_closed(self):
        a=block(1,1000,[fill("0xa","B",True,1,1000),fill("0xb","A",False,1,1000)])
        b=block(1,1001,[fill("0xa","B",True,1,1001),fill("0xb","A",False,1,1001)])
        with self.assertRaises(h.DataError):
            h.parse_fill_blocks([a,b])

if __name__=='__main__':
    unittest.main()
