# Quant V1 — Independent Red-Team Review

## Scope

This review started from the verified V1 integrity-pass commit
`a5b8e5fc3a1b6aba1b43337a66e0db08822d87f0` and was performed on
`reviewer/v1-final-red-team` against the product contract in `QUANT_NORTH_STAR.md`,
`SYSTEM_ARCHITECTURE.md` and `OPERATING_MODEL.md`.

The review did not assume the initial suspicions were true. It reconstructed behavior from code,
persistent contracts and executable proof, then added adversarial regressions for defects that
could falsify research evidence, capital decisions, recovery, data integrity or reported state.
Phase 2 was not started and PR #12 was not merged or repurposed.

## Close-out verdict rule

All material V1 merge blockers demonstrated by this review are resolved in the current tree.
The final reviewer verdict is **MERGEABLE if and only if the V1 proof gate is green on this exact
commit**. This wording is deliberate: a green earlier checkpoint is evidence, but it is not a
substitute for proving the final HEAD.

The previous remaining blocker was committed-state truthfulness. It is now closed by rebuilding
`CHIEF_BRIEF.md` and the generated status checkpoint in `STATE.md` from a clean persistent replay
of the committed V1 inputs, and by making that replay a CI freshness gate. The committed status
surface can therefore no longer drift silently while the V1 proof gate remains green.

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
14. **Committed status artifacts could become stale while runtime tests stayed green.**
    `scripts/status_artifacts.py` now reconstructs canonical persistent state from committed data,
    runs the real Control Plane to IDLE, regenerates `CHIEF_BRIEF.md` plus the generated checkpoint
    in `STATE.md`, and fails CI if either artifact differs. The generated brief is normalized so
    this freshness check and `git diff --check` can both be green.

## Canonical persistent-state truth

The canonical replay over the committed market snapshot now produces and commits the same facts:

- desk cursor `2026-09-10`, **377** executable desk sessions;
- **377** authoritative capital Book marks, last mark `2026-09-11`;
- capital Book **1,000,000.00 USD**, 0 fills, 0 positions;
- tickets: **76 BOOKED, 301 NO_TRADE, 0 terminal BLOCKED**;
- evaluation NAV **993,757.74**, total return about **-0.62%**;
- counterfactual P&L **-6,242.26**;
- research queue: 3 BLOCKED, 2 COMPLETED;
- proof inventory: **104 unit tests discovered** and **35 end-to-end demo assertions**.

The superseded pre-red-team values (378 desk sessions, one terminal BLOCKED ticket, evaluation NAV
993,742.87 and counterfactual P&L -6,165.57) are no longer presented as current post-repair truth.

## Adversarial proof and proof gate

The review suite includes targeted regressions for decision-time leakage, multi-strategy session
leakage, execution-basis consistency, commission-aware final risk, frozen-cohort append/rewrite,
forward terminal-close execution, research crash transactions, refreshed rejection learning,
malformed market data, Book peak restatement and torn JSONL recovery.

The `V1 proof gate` now executes, on a clean GitHub runner:

```text
python3 scripts/status_artifacts.py --check
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/demo_quant_system.py
python3 scripts/generate_schemas.py --check
git diff --check a5b8e5fc3a1b6aba1b43337a66e0db08822d87f0...HEAD
clean working-tree assertion
```

Checkpoint `88c1f841c51821eb1f3a7badab9905985d4e8b11`, workflow run `34788806926`, passed every gate:
canonical status artifacts fresh, **104/104 tests**, **35/35 end-to-end checks**, schemas checked,
diff check clean and working tree clean. The final verdict still depends on the same proof being
green on the exact commit containing this close-out report.

## Economic boundary

No result in this review verifies profitability, and no real-capital authority is implied. The
current strategy evidence remains negative and non-tradable. The mandatory HAC/Newey-West or block
bootstrap boundary before future positive evidence can authorize capital remains a prerequisite,
not something this V1 integrity review relaxes.
