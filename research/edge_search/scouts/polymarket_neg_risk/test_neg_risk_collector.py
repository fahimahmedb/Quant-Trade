import unittest
from decimal import Decimal

import neg_risk_collector as n


def market(i, title=None, fee=False):
    return {
        "id": str(i),
        "conditionId": f"c{i}",
        "groupItemTitle": title or f"Outcome {i}",
        "active": True,
        "closed": False,
        "archived": False,
        "acceptingOrders": True,
        "enableOrderBook": True,
        "negRisk": True,
        "outcomes": '["Yes","No"]',
        "clobTokenIds": f'["y{i}","n{i}"]',
        "feesEnabled": fee,
        "feeSchedule": ({"rate": 0.05, "exponent": 1, "takerOnly": True, "rebateRate": 0.25} if fee else None),
    }


def event(aug=False, other=False, fee=False):
    ms = [market(1, "A", fee), market(2, "B", fee), market(3, "Other" if other else "C", fee)]
    return {"id": "9", "title": "E", "enableNegRisk": True, "negRiskAugmented": aug, "markets": ms}


def book(token, bids, asks, t=1700000000000, minimum="5"):
    return {
        "market": "c", "asset_id": token, "timestamp": str(t), "hash": "h",
        "bids": [{"price": str(p), "size": str(s)} for p, s in bids],
        "asks": [{"price": str(p), "size": str(s)} for p, s in asks],
        "min_order_size": minimum, "tick_size": "0.01", "neg_risk": True,
        "last_trade_price": "0.5",
    }


class NormalizeTests(unittest.TestCase):
    def test_flb_unrelated_and_standard_other_is_allowed(self):
        s = n.normalize_standard_neg_risk_event(event(other=True))
        self.assertEqual(len(s.markets), 3)
        self.assertEqual(s.markets[2].title, "Other")

    def test_augmented_rejected_even_if_current_markets_look_named(self):
        with self.assertRaises(n.DataContractError):
            n.normalize_standard_neg_risk_event(event(aug=True))

    def test_unknown_augmented_state_fails_closed(self):
        e = event()
        del e["negRiskAugmented"]
        with self.assertRaises(n.DataContractError):
            n.normalize_standard_neg_risk_event(e)

    def test_missing_component_book_state_rejected(self):
        e = event()
        e["markets"][1]["acceptingOrders"] = False
        with self.assertRaises(n.DataContractError):
            n.normalize_standard_neg_risk_event(e)


class ArithmeticTests(unittest.TestCase):
    def test_depth_walk_uses_multiple_levels(self):
        f = n.walk_book([{"price":"0.20","size":"2"},{"price":"0.21","size":"4"}], Decimal("5"), True, n.FeeSchedule(Decimal("0"), Decimal("1")))
        self.assertIsNotNone(f)
        self.assertEqual(f.gross, Decimal("1.03"))

    def test_insufficient_depth_returns_none(self):
        self.assertIsNone(n.walk_book([{"price":"0.20","size":"2"}], Decimal("3"), True, n.FeeSchedule(Decimal("0"), Decimal("1"))))

    def test_fee_rounds_up_conservatively(self):
        f = n.fee_usdc(Decimal("1"), Decimal("0.5"), n.FeeSchedule(Decimal("0.04"), Decimal("1")))
        self.assertEqual(f, Decimal("0.01000"))

    def test_profitable_conversion_route(self):
        e = n.normalize_standard_neg_risk_event(event())
        books = []
        # Source NO1 costs 0.30; YES2 + YES3 sell for 0.55 + 0.55 = 1.10.
        # Other unused sides still supplied because the batch contract requires all tokens.
        for token in e.token_ids:
            bids = [("0.55", "20")] if token in ("y2", "y3") else [("0.10", "20")]
            asks = [("0.30", "20")] if token == "n1" else [("0.90", "20")]
            books.append(book(token, bids, asks))
        rs = n.evaluate_routes(e, books)
        r = next(x for x in rs if x.source_market_id == "1")
        self.assertEqual(r.q, Decimal("5"))
        self.assertEqual(r.gap, Decimal("4.00"))
        self.assertTrue(r.violation)

    def test_fee_can_remove_small_quote_gap(self):
        e = n.normalize_standard_neg_risk_event(event(fee=True))
        books = []
        for token in e.token_ids:
            bids = [("0.255", "20")] if token in ("y2", "y3") else [("0.10", "20")]
            asks = [("0.50", "20")] if token == "n1" else [("0.90", "20")]
            books.append(book(token, bids, asks))
        r = next(x for x in n.evaluate_routes(e, books) if x.source_market_id == "1")
        self.assertLess(r.gap, Decimal("0.05"))
        self.assertFalse(r.violation)

    def test_timestamp_skew_fails_closed(self):
        e = n.normalize_standard_neg_risk_event(event())
        books = [book(t, [("0.2","10")], [("0.8","10")], t=1700000000000 + (2001 if i == 0 else 0)) for i, t in enumerate(e.token_ids)]
        with self.assertRaises(n.DataContractError):
            n.evaluate_routes(e, books)

    def test_missing_token_fails_closed(self):
        e = n.normalize_standard_neg_risk_event(event())
        books = [book(t, [("0.2","10")], [("0.8","10")]) for t in e.token_ids[:-1]]
        with self.assertRaises(n.DataContractError):
            n.evaluate_routes(e, books)


if __name__ == "__main__":
    unittest.main()
