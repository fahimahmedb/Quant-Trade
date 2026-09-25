"""H-004 frozen design. Written and committed BEFORE any outcome or P&L was looked at.

Only a volume/history census (event counts and contract volume per month, no
``result`` field, no prices) was run to choose feasible series and a sampling
rule. Nothing here may change after the analysis runs; a change is a rerun
and consumes trials.
"""
from __future__ import annotations

import datetime as dt

HYPOTHESIS_ID = "H-004"
DATASET_KEY = "kalshi_trades_daily_series"
DECLARED_TRIALS = 4  # category x evaluation, from research/fast_rail/registry.jsonl
RERUNS = 0           # bump on every rerun after a bug fix; trials = DECLARED_TRIALS + RERUNS

# Category 1: daily-high temperature, the seven US-city KXHIGH* series with
# >= 12 months of settled history on the public API.
WEATHER_SERIES = ("KXHIGHNY", "KXHIGHCHI", "KXHIGHMIA", "KXHIGHAUS",
                  "KXHIGHDEN", "KXHIGHLAX", "KXHIGHPHIL")
# Category 2: other daily-resolving series (non-weather daily-close/range
# contracts with >= 12 months of listings). Chosen before looking at outcomes.
OTHER_SERIES = ("KXINX", "KXNASDAQ100", "KXEURUSD", "KXUSDJPY", "KXWTI")

CATEGORY = {s: "weather" for s in WEATHER_SERIES} | {s: "other" for s in OTHER_SERIES}

# Sampling rule (volume too large for every day): event dates D in
# [WINDOW_START, WINDOW_END] with (D - WINDOW_START).days % SAMPLE_STEP_DAYS == 0.
# The step rotates the weekday. Fallback if the gzipped store exceeds 25 MB:
# SAMPLE_STEP_DAYS = 14 (a subset of the same dates).
WINDOW_START = dt.date(2025, 9, 25)
WINDOW_END = dt.date(2026, 9, 23)
SAMPLE_STEP_DAYS = 7

# Unit of evidence: event-day = (series, event date); all markets and prints of
# the series' event(s) on that date. Splits are on sorted distinct sampled dates.
DISCOVERY_FRACTION = 0.55
VALIDATION_FRACTION = 0.30   # remaining 0.15 is UNTOUCHED

MARKOUT_START_S = 300
MARKOUT_END_S = 600

# Fee assumption. The public API reports fee_type="quadratic" (taker-only fee
# 0.07*P*(1-P)) for every series used, i.e. no maker fee today. We nevertheless
# charge the general Kalshi maker fee 0.0175*P*(1-P) per contract (unrounded:
# assumes maker orders are large enough that cent rounding is negligible) as the
# verdict fee, and require the result to survive 2x that fee.
MAKER_FEE_RATE = 0.0175

MAKER_SHARE_OF_VOLUME = 0.10       # capacity assumption
MIN_MONTHLY_TURNOVER_USD = 10_000.0
MAX_TOP_DECILE_SHARE = 0.50


def sampled_dates(step: int = SAMPLE_STEP_DAYS) -> list[dt.date]:
    out, d = [], WINDOW_START
    while d <= WINDOW_END:
        if (d - WINDOW_START).days % step == 0:
            out.append(d)
        d += dt.timedelta(days=1)
    return out
