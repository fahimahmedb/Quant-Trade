import unittest

from quant.recorders.binance_public import binance_public_plan
from quant.recorders.http import PublicHttpTransport


class PublicPlanTests(unittest.TestCase):
    def test_plan_is_btc_eth_spot_perpetual_public_https_only(self):
        plan = binance_public_plan()
        self.assertEqual({spec.instrument for spec in plan if spec.instrument}, {"BTCUSDT", "ETHUSDT"})
        self.assertEqual({spec.market_type for spec in plan}, {"spot", "perpetual"})
        self.assertTrue(all(spec.endpoint.startswith("https://") for spec in plan))
        self.assertTrue(all("/api/" in spec.endpoint or "/fapi/" in spec.endpoint for spec in plan))
        self.assertTrue(any("fundingRate" in spec.endpoint for spec in plan))
        self.assertTrue(any("premiumIndex" in spec.endpoint for spec in plan))
        self.assertTrue(any("depth" in spec.endpoint for spec in plan))
        self.assertFalse(any(fragment in spec.endpoint.lower() for spec in plan for fragment in ("/order", "/account", "userdata", "listenkey")))

    def test_transport_has_no_credential_or_signature_header(self):
        headers = {key.lower(): value for key, value in PublicHttpTransport().request_headers.items()}
        self.assertNotIn("x-mbx-apikey", headers)
        self.assertNotIn("authorization", headers)
        self.assertEqual(set(headers), {"user-agent", "accept"})

    def test_scope_rejects_other_symbols(self):
        with self.assertRaises(ValueError):
            binance_public_plan(("SOLUSDT",))


if __name__ == "__main__":
    unittest.main()
