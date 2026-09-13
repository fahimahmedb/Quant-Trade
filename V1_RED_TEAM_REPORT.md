# Quant V1 — Independent Red-Team Review

## Scope

This review started from the verified V1 integrity-pass commit
`a5b8e5fc3a1b6aba1b43337a66e0db08822d87f0` and was performed on
`reviewer/v1-final-red-team` against the product contract in `QUANT_NORTH_STAR.md`,
`SYSTEM_ARCHITECTURE.md` and `OPERATING_MODEL.md`.

The review did not assume the initial suspicions were true. It reconstructed behavior from code,
persistent contracts and executable proof, then added adversarial regressions for defects that
could falsify research evidence, capital decisions, recovery, data integrity or reported state.
Phase 2 was not started.

## Verdict

**NOT MERGEABLE as a truthful V1 snapshot yet.**

The repaired code path has passed the independent proof gate on review checkpoints, and the final
review tree must pass the same gate before this report is closed. The remaining merge blocker is
not a known failing runtime invariant: it is a source-of-truth mismatch in the committed project
state artifacts. `STATE.md` and `CHIEF_BRIEF.md` still contain pre-red-team counts/economic values
that are no longer the output of the repaired causal desk semantics. They must be regenerated from
the intended persistent operator state after these repairs rather than hand-edited from a test
fixture.

This matters because the North Star treats the status surface as an architectural checksum: a
committed artifact presented as live/current must not report superseded economic state.

## Material defects demonstrated and repaired

1. **Schema drift under Python 3.12.** PEP 604 unions were not generated correctly, so committed
   schemas could disagree with dataclasses. The schema generator now handles `types.UnionType` and
   drift is checked in CI.
2. **Malformed/stale market data could pass too far.** Validation now rejects duplicate keys,
   non-finite prices, negative volume, non-positive execution prices, missing required symbols on
   the latest session, malformed ISO session dates and impossible OHLC geometry. Registry
   availability is rebound to the fingerprint of the bytes actually validated and detects bytes
   changing during validation.
3. **Close-time desk decisions leaked `open(t+1)`.** VET, SIZE and pre-fill RISK now use the
   close(t) information set. Execution open prices are confined to FILLS/post-fill verification.
4. **Strategy ordering leaked future fills within one session.** A durable session decision
   snapshot makes every strategy for close(t) see the same pre-execution Book, including after a
   crash/restart midway through the session.
5. **Final RISK mixed valuation bases and ignored commissions.** Existing and newly filled
   quantities are revalued on one final price vector, and cash-only commission loss is included in
   the NAV/drawdown floor check before booking.
6. **Append-only data incorrectly recycled frozen historical research.** Once the discovery /
   validation cohort is frozen, forward appends extend SHADOW evidence without purchasing another
   historical experiment or moving the validation boundary.
7. **Historical rewrites could be mistaken for new evidence.** A changed value inside the frozen
   cohort now creates a durable research-integrity block and prevents desk progression until the
   lineage is reviewed/restored.
8. **The terminal close was consumed before it had an execution session.** The last close remains
   pending until a later aligned session exists; a future append can therefore execute the prior
   information set instead of losing it as a permanent BLOCKED ticket.
9. **Research completion was not transactional across crash boundaries.** Worker output, research
   memory, strategy registration, learning and Control completion are now replay/idempotence safe;
   crash/retry cannot manufacture duplicate science, lessons or strategy versions.
10. **Decision-quality learning was one-shot.** Rejected-strategy assessment now refreshes when
    new counterfactual evidence arrives while remaining idempotent on identical evidence.
11. **Same-session Book restatement could leave a phantom peak NAV.** `peak_nav` is recomputed from
    authoritative NAV history after a restatement, so superseded marks cannot create false future
    drawdown throttles.
12. **Append-only JSONL state could be torn by process death.** A final unterminated append is
    recoverable and repaired on the next append; malformed newline-terminated committed records
    remain loud rather than being silently skipped.
13. **The synthetic proof fixture itself used calendar-invalid dates.** Test sessions now use valid
    ISO calendar dates, so Data Plane date validation is exercised rather than bypassed by the
    fixture.

## Adversarial proof added

The review suite now includes targeted regressions for decision-time leakage, multi-strategy
session leakage, execution-basis consistency, commission-aware final risk, frozen-cohort append
and rewrite behavior, forward terminal-close execution, research crash transactions, refreshed
false-reject learning, malformed market data, Book peak restatement and torn JSONL recovery.

The independent `V1 proof gate` executes, on a clean GitHub runner:

```text
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/demo_quant_system.py
python3 scripts/generate_schemas.py --check
git diff --check a5b8e5fc3a1b6aba1b43337a66e0db08822d87f0...HEAD
clean working-tree assertion
```

A successful pre-report proof checkpoint ran 100 tests plus the 35/35 end-to-end restart/crash
checks. Subsequent adversarial additions are required to pass the same gate on the final review
head before any merge decision is revisited.

## Demonstrated state-artifact mismatch

A successful repaired replay over the committed market snapshot produced:

- desk cursor `2026-09-10`, **377** desk sessions;
- **377** authoritative Book marks, last mark `2026-09-11`;
- tickets: **76 BOOKED, 301 NO_TRADE, 0 terminal BLOCKED**;
- evaluation NAV **993,757.74**, total return about **-0.62%**;
- counterfactual P&L **-6,242.26**;
- capital Book unchanged at **1,000,000.00**, 0 fills, 0 positions.

The committed pre-red-team state artifacts still report, among other differences, 378 desk
sessions / one terminal BLOCKED ticket, evaluation NAV 993,742.87 and counterfactual P&L
-6,165.57. Those values describe superseded desk semantics and must not be presented as current
post-repair truth.

The research claims themselves remain non-financial evidence only. No result in this review
verifies profitability, and no real-capital authority is implied.

## Required close-out before merge

Regenerate `CHIEF_BRIEF.md` (and reconcile `STATE.md`) from the intended persistent operator state
using the repaired V1 code, verify that no superseded economic numbers remain, then rerun the full
proof gate on that exact commit. Until that is done, the review verdict remains **NOT MERGEABLE**.
