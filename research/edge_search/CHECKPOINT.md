# CHECKPOINT (overwritten at each significant batch)

STATE (2026-10-08 22:12Z): Owner EDGE-FLOW baseline (PR comment 6064142254). PRIMARY = FIND_OR_FALSIFY_REAL_EDGE. ACTIVE_WIP = 1: F1 CRYPTO-CARRY-001. F2 = BLOCKED. F3 and any new family: not before the F1 verdict. A2 frozen. Owner reports Claude has no tokens; Codex continues independently.

CANONICAL F1: PR #22 remote head last verified `1e88c6b82d682ae6d6d71b0732cb1bdb232cea3a`; supersedes `a895e1a`. Latest acquisition report is Claude's comment `6068136072` (20:09Z): resumed private Stage A/Stage B downloads, no outcome reported. Detached-process status is UNKNOWN here. No RESULT A, acquisition artifact or release archive was found on GitHub at the latest read. Stage B remains sealed.

REPAIR: PR #23, branch `builder/f1-decision-integrity-repair-2026-10-08`. Four synthetic defects reproduced and fixed: missing successful manifest files; liquidation exit-day slippage; equal-size data mutations; Stage A hash/parse race selecting a different theta. Current proposed `run_f1.py` sha256 = `5a773f45c630c559532ccfbf6888bf506adf6e8a3c31b9fbe09f65ef33ec239c`; 32 synthetic F1 tests pass. Initial repair `b1b792eaae90a444eeb55dacf6c3782f9d1e4a32` has green push CI `37850413334` and PR CI `37850498521`; check final PR head/CI before adopting. No real outcome was downloaded or parsed by this Codex task.

ACCESS: this worker now reaches both Binance Vision and its S3 listing endpoint (metadata-only HEAD probes: HTTP 200). The earlier Codex HTTP 403 is not the current blocker. Candidate-list sha256 remains `f586b666d8950f9f98983a869eea012ef5e3ac7ac0c96f5d39a4dbbf0b65c9e4`.

NEXT: recover the existing private acquisition (`scratchpad/f1data/stageA`) and determine whether Stage A has already exposed an outcome. If unexposed, pin the exact reviewed repair commit, verify manifest/window/checksums and acquisition completion, then execute Stage A once and publish the RESULT and its hash. If already exposed, preserve that result and its original harness; do not rerun it under new bytes. Do not blindly duplicate downloads whose detached status is unknown. Then falsify the published A result before the single Stage B run.

ROLE: Codex = RESEARCH_LEAD / convergence + FALSIFIER; Claude = network/data executor when available (agreement `6068175268`). No new scout, family, A2 expansion or paid data. The two-round limit concerns substantive F1 challenges; the repairs above are one grouped pre-outcome integrity correction.
