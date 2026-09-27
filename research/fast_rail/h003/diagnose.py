"""H-003 tail diagnostic for the selected expression (discovery + validation only; no new trial).

Per-contract YES-resolution (loss) rates and the probability that validation shows its
observed number of losses if the discovery loss rate were true. Holdout is never touched.

    PYTHONPATH=src python3 research/fast_rail/h003/diagnose.py
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import analyze as a  # noqa: E402


def contracts(events, thr, hours):
    out = []
    for ev in events:
        for m in ev["markets"]:
            entry = m["close_ts"] - hours * 3600
            price = a.no_entry_price(a.select_candle(m["candles"], entry), thr)
            if price is not None:
                out.append((price, m["result"]))
    return out


def main():
    disc, val, _ = a.split_events(a.group_events(a.load()))
    thr, hours = 0.05, 1
    report = {}
    for name, events in (("discovery", disc), ("validation", val)):
        c = contracts(events, thr, hours)
        losses = sum(1 for _, r in c if r == "yes")
        report[name] = {"contracts": len(c), "yes_losses": losses,
                        "mean_no_price": sum(p for p, _ in c) / len(c) if c else 0.0,
                        "breakeven_loss_rate": 1 - (sum(p + a.kalshi_taker_fee(p, 1) for p, _ in c) / len(c))
                        if c else 0.0}
    p_loss = report["discovery"]["yes_losses"] / report["discovery"]["contracts"]
    n_val, k_val = report["validation"]["contracts"], report["validation"]["yes_losses"]
    report["p_validation_losses_le_observed_given_discovery_rate"] = sum(
        math.comb(n_val, k) * p_loss ** k * (1 - p_loss) ** (n_val - k) for k in range(k_val + 1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
