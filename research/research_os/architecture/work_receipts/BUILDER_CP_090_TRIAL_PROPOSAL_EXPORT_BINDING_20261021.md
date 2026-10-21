# CP090 — Shared proposal attribution before export

CP089 reproduced an actual composed READY/export while every generated proposal
referred to another scientific subject. Reuse the qualified CP075 native join
as assert_trial_proposal_binding in the existing V2 core, called by both the pure
pipeline and native challenge admission. No new trial or candidate store.

Generic V2 proposals must identify hypothesis, generation and exact V2 Candidate
hash. Source-adapted native proposals instead identify the original source
Candidate hash and matching documentary packet. The two hashes remain distinct.
Partial/null/malformed declared source bindings cannot fall back to the generic
mode. Native trial integrity, epoch binding, literal source-hash requirements,
fail-before-retrieval/model behavior and existing blocker codes are preserved.

The pure pipeline runs the join after its existing Validator/candidate integrity
check and before any export. A freshly rebound Validator cannot attest that an
unrelated trial generated a changed same-generation candidate. Missing proposal
identity is now a blocker, not a qualified ideation count attached to an export.

Only synthetic positive fixtures gain explicit first-proposal references; candidate
fields/hash, Validator and generated/discarded counts are unchanged. The committed
fixture receipt golden deliberately changes from 01fa1c77... to 48ec56af... because
the trial body and derived history/export/receipt hashes now include attribution.
The golden assertion is accompanied by hypothesis/generation/hash join assertions.
The trial golden likewise changes from dbb5e858... to a0205840... with an explicit
proposal join assertion; epoch and all four family Candidate goldens are unchanged.
Old persisted trials, receipts, epochs and scientific outcomes are not rewritten.

Five new tests exercise the actual pure entrypoint's foreign/unattributed proposals,
changed candidate with a fresh Validator, coherent generic replay/accounting,
distinct native source/V2 hashes plus source-packet mismatch, and malformed/partial
source metadata with no fallback. They assert failure before export construction
and input immutability. Existing CP075 tests continue to exercise all five native
challenge stages, actual disposable Git state and rejection before model work.
Focused 22, root 818 and broader Research OS 268 PASS; suites overlap. Official
inventory regenerated to 818. Ruff F and whitespace PASS. Exact-source workflow
qualification follows this stable source; local counts alone do not establish it.

North Star edge advanced: ideation accounting -> exact scientific candidate ->
validation/export attribution. This does not establish source truth, cognitive
independence, economic validation or transport/storage isolation. No outcome data,
economic experiment, live/prospective observation or canonical Oracle write.
Four authorities remain FALSE; skipped network/production remains excluded.
