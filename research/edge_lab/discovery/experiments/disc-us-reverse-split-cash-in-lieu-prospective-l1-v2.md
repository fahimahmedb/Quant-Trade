# Discovery V4.2 — US reverse-split cash-in-lieu prospective L1 v2

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY
PROSPECTIVE_T0 = 2026-10-12T21:00:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Clock repair

The prior v1 file used `PROSPECTIVE_T0 = 2026-10-12T20:00:00Z` but its creating commit `ca23532498b77d5eb3310f9c080909a2a239a221` was created at 2026-10-12T20:22:38Z. Therefore v1 is INVALID as a prospective declaration and MUST NOT be used to admit any event.

This v2 is a pure clock repair made before the new T0. Its protocol body, universe, event-selection rule, quantity rule, payout reconstruction, frozen frictions, decision rule, implementation check, adverse check and inference rights are EXACTLY those fixed in commit `ca23532498b77d5eb3310f9c080909a2a239a221`, with only these changes:

1. `PROSPECTIVE_T0` is replaced by `2026-10-12T21:00:00Z`.
2. v1 is explicitly invalidated for prospective sampling.
3. Eligible events must have EDGAR `accepted` STRICTLY AFTER the new v2 T0.

No historical event exposed before v2 T0 may enter the sample. No market-price payload or payout outcome is authorized by this repair itself.
