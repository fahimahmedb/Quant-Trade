# Discovery V4.2 — US reverse-split fractional round-up prospective L1 v2

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY
PROSPECTIVE_T0 = 2026-10-12T21:00:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Clock repair

The prior v1 file used `PROSPECTIVE_T0 = 2026-10-12T20:00:00Z`, but its creating commit `7f5f6a1199658bce0983ca5d71faebf06ab184c9` was created at `2026-10-12T20:23:34Z`, after that T0. Therefore v1 is INVALID as a prospective declaration and MUST NOT admit any event.

This v2 is a pure prospective-clock repair made before the new T0. The full protocol body, universe, selection rule, fixed Q=1, entry rule, issuer-level ceiling, frozen central/stress frictions, nominee/broker implementation gate, adverse check, family threshold and inference rights are EXACTLY those frozen in immutable commit `7f5f6a1199658bce0983ca5d71faebf06ab184c9`, with only these changes:

1. `PROSPECTIVE_T0` is replaced by `2026-10-12T21:00:00Z`.
2. v1 is explicitly invalidated for prospective sampling.
3. Only events whose relevant EDGAR `accepted` timestamp is STRICTLY AFTER the new v2 T0 are eligible.
4. Any issuer/event/document exposure occurring before the new v2 T0 remains calibration/exposure only and is excluded from the fresh prospective sample.

No market-price payload, post-effective result, broker allocation result, or economic outcome is authorized by this repair itself.
