# Minimal C0 confirmation-count repair review

FACT: Work began on `codex/c0-confirmation-repair-20261027` at immutable mission base `d19b1237636d2311cd42f97f0b02feb55168347b`. Product edit is confined to the existing C2 adapter `research/research_os/expansion/scientific_adjudication.py`; new regression/attack tests are `tests/test_c0_confirmation_count_repair.py`. No commit created by this agent. No production source, scientific object, root, variant, proposal, trial, exposure, memory, authority, outcome or economic state was mutated.

FACT: Preserved historical kernel `research/research_os/expansion/_scientific_adjudication_c0.py` remains byte-identical Git blob `3f0e1b7bae53e9513f0061cabcfae2505a6795f3`. No new module, schema, mutation owner, ledger, external proof format or provenance resolver was introduced.

## Exact gap and chosen scope

FACT: Historical kernel computed `independent_confirmation_count=1` whenever structural axes passed and support relation was PRIMARY_SOURCE_RECONSTRUCTION, even when semantic review explicitly said NOT_PROVEN_NO_SEMANTIC_PASS_GRANTED. Current C2 public adapter delegated unchanged. The original mission's immutable failing witness, `continuity/one_shot/oneshot_c0_current_attack.py`, directly proved this using target's own fixture; claim ceiling and all economic authorities remained bounded but the exposed confirmation count overstated the recorded semantic review state.

FACT: Latest immutable source `6dc84f35e80aec709e67e3d5d3ce0cdcfaee3bcf:research/research_os/expansion/scientific_adjudication.py:403-464` and its tests at `tests/test_mega_c0_scientific_adjudication.py:305-317` identify the existing exact semantic-review token. They are evidence, not canonical ownership authority. Source repair adds a redundant semantic boolean; this repair instead derives count from existing bound fields, retaining existing schema.

DECISION: In the existing caller-supplied record trust boundary, count is exactly integer one only when ALL are recorded: semantic_diverse_review exactly PROVEN_INDEPENDENT_SEMANTIC_REVIEW; structural_independence_proven literally True; every existing structural axis literally True; outcome_accessed literally False; status PASS; support_relation PRIMARY_SOURCE_RECONSTRUCTION. Otherwise count is exactly integer zero. Unknown/missing/null/unproven review remains unknown/missing/null/unproven in its native field. Zero counts available confirmations; it does not assert semantic independence is false.

## Implementation and downstream behavior

FACT: Adapter captures the original kernel bind/validate functions before installing wrappers. Binding reuses the original structural/Factory/provenance logic, derives the narrower count, rehashes the ref, and validates it. Validation preserves the original identity/authority/selfhash checks and additionally requires a literal int equal to the derived count. Both `_impl.bind_independence_ref` and `_impl.validate_independence_ref` are wired to the current wrappers, so direct inner entrypoints and preserved adjudication cannot accept an old unproven overcount ref. Capturing originals avoids recursion.

FACT: Historical refs/records are not rewritten. A historical overcount ref remains immutable evidence and fails current validation/composition. Rebinding its original record produces a new ref/hash with count zero. Valid zero-count refs remain valid; explicit exact semantic-review assertions can count once within the existing trust boundary. Structural PASS, claim ceiling, economic UNKNOWN, authority closure and outcome isolation retain their existing meaning.

FACT: Public standalone adjudication validation now accepts confirmation count only when type(count) is int and count is 0 or 1. It rejects booleans, floats, negative/unsupported integers and strings even after attacker recomputes selfhash. Ordinary composed output receives its count only after the strengthened input-ref validation; no new embedded-provenance architecture was added.

## Test coverage and execution evidence

FACT: New class contains **11 test methods**, with subcases covering unknown/null/wrong-type semantic states, exact existing semantic assertion with Factory identity and record_hash binding, duplicate/wrapper/unknown support, failed axes and missing outcome isolation, rehashed count forgery and boolean/float/string counts, rehashed positive-basis drift, frozen identity mismatch, immutable stale historical refs rejected through public and inner composition, composed zero/one counts with authority/claim/UNKNOWN invariants, and standalone unsupported counts.

FACT: Imported fixture module is referenced through a module alias; its TestCase class is not copied into the new test module's discovery namespace. New test inventory increases by 11, not by duplicate imported fixture methods.

FACT: Timed working-tree focused run: **42 tests PASS** (new tests + canonical C2 adjudication + scientific/economic seam). Original formerly failing witness now PASS without any change to its logic. `git diff --check` PASS. Full commands, environment, observed HEAD, exact working product/test blob IDs, start/end timestamps, exit codes, results and complete logs are `/tmp/c0_repair_runs/TEST_RUNS.json` and sibling logs.

LIMIT: Those agent runs execute dirty working files while observed HEAD remains mission base. They establish local development evidence only, not final exact-head qualification. Root must commit, run required local qualification at the resulting candidate, then complete hosted qualification/attestation as applicable.

## Trust limits and remaining risks

FACT: The exact semantic token is an asserted review-proof state already present in the source contract. Neither a token nor an ordinary SHA selfhash authenticates its author, proves a real independent reviewer, resolves authority to issue that assertion, or establishes actual cognitive/semantic independence. Positive tests use synthetic explicit proof-state assertions and prove binding/counting behavior only. No verified real semantic-review artifact was discovered or manufactured.

FACT: Standalone adjudication validation receives opaque component hashes, not the component bodies or an authenticated signature. A fully self-consistent attacker rewriting a standalone result's admissible count from zero to one and recomputing every relevant selfhash cannot be authenticated against its original ref by this API alone. The repair rejects unsupported values and secures actual ref-to-composition paths; it does not claim arbitrary selfhashed payload authenticity. Adding a new provenance store/resolver or proof schema would exceed this repair.

FACT: Independent adversary noted inherited direct-reference validation can accept some arbitrary extra raw-outcome-shaped fields because that validator does not recursively reject every extension. This predates and is separate from the confirmation-count defect. No related product expansion was made. Record it for a separate scoped firewall mission; do not claim all C0 safety properties globally qualified by this count repair.

INFERENCE: Historical persisted counts may need a separately authorized read-only audit/reprojection before scientific use. This mission does not rewrite historical production truth or infer a complete trial/exposure denominator.

## Self-challenge

- Exact W2 gap: direct original witness count one despite explicitly unproven semantic review; current public C2 composition exposes that count. Existing native structural checks do not supply semantic proof.
- Necessity: tests/evidence alone cannot change the erroneous current callable count. The small existing adapter seam fixes it without kernel replacement.
- Ownership: existing C2 adapter still binds/validates refs; preserved scientific/control owners and all authority firewalls remain unchanged.
- Sunk cost/recency: source rail was used only to identify token semantics; no wholesale source port or new source-owned truth was introduced.
- UNKNOWN: review field and scientific uncertainty are preserved. Count zero means no qualifying recorded confirmation; it is not a FALSE declaration about actual independence.
- Fixtures: all new inputs are isolated synthetic fixtures; no production state or protected outcomes were read or written.
- Revert consequence: removing the adapter count gate restores the original failing count-one witness. Removing validator wiring lets stale ref inputs bypass corrected binding through preserved composition.

RECOMMENDATION: Root should qualify the committed exact target and report the narrow count contract plus explicit trust limits. Keep actual reviewer-proof provenance, full C0 payload firewall review, UST authority, engineering loop and economic readiness as separately scoped work.
