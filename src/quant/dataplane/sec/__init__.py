"""P0 SEC/EDGAR Form-4 durable raw capture.

The lane preserves what cannot be reconstructed later - exact response bytes,
local receipt timing, attempt liveness and honest coverage - and deliberately
stops short of interpreting what it captured.

``P0_RAW_CAPTURE_CRITICAL_PATH_RECLASSIFICATION_2026-09-18.md`` section 7:

    DATA_CAPTURED != DATA_VISIBLE_FOR_SCIENTIFIC_PROTOCOL
                  != DATA_ADMISSIBLE_FOR_CONFIRMATION

Nothing in this package grants the second or third state.
"""
