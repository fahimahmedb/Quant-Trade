#!/usr/bin/env python3
"""Recompute the power screen of ../puissance.json.

expected_t = (haircut × effect) / sigma × sqrt(n), haircut = 0.5 by default
(prompt section 4) or the row's own "haircut" (1.0 when the effect is already
net). Forward horizon = events for E[t] = 1.96, and for 80 % power at 1.96
(E[t] = 2.80), converted to years with n_per_year. A row whose effect after
haircut is <= 0 can never pass (status EFFET<=0).

Usage:  python puissance.py
"""
import json
import math
import os

Z_CRIT, Z_POWER80 = 1.96, 1.96 + 0.8416
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "puissance.json")


def screen(p: dict) -> dict:
    eff = p["effect"] * p.get("haircut", 0.5)
    ratio = eff / p["sigma"]
    n_hist = p["n_per_year"] * p["hist_years"]
    if ratio <= 0:
        return {**p, "effect_after_haircut": eff, "n_hist": n_hist, "expected_t_hist": 0.0,
                "status_hist": "EFFET<=0", "events_for_t196": None, "events_for_80pct": None,
                "years_for_t196": None, "years_for_80pct": None}
    t_hist = ratio * math.sqrt(n_hist) if n_hist > 0 else 0.0
    n50, n80 = (Z_CRIT / ratio) ** 2, (Z_POWER80 / ratio) ** 2
    return {**p, "effect_after_haircut": eff, "n_hist": n_hist,
            "expected_t_hist": round(t_hist, 2),
            "status_hist": "OK" if t_hist >= Z_CRIT else "UNDERPOWERED",
            "events_for_t196": math.ceil(n50), "events_for_80pct": math.ceil(n80),
            "years_for_t196": round(n50 / p["n_per_year"], 2),
            "years_for_80pct": round(n80 / p["n_per_year"], 2)}


if __name__ == "__main__":
    keys = ("piste", "stat", "effect", "sigma", "n_per_year", "hist_years", "haircut", "src")
    for row in json.load(open(PATH))["pistes"]:
        r = screen({k: row[k] for k in keys if k in row})
        print(f"{r['piste'][:36]:36} t_hist {r['expected_t_hist']:5.2f} {r['status_hist']:>13} "
              f"n(1,96) {r['events_for_t196']} ans {r['years_for_t196']} | n(80 %) {r['events_for_80pct']} "
              f"ans {r['years_for_80pct']}")
