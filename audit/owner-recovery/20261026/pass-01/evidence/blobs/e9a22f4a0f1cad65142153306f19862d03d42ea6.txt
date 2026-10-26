# GIGA F research exposure specification

Implementation: `research/research_os/idea_feed/registry.py::expose` and
`exposure_state`; enforcement in `idea_feed/intake.py` and `idea_feed/feeder.py`.

Exposure events share the durable append-only journal with seed births, but do
not mutate the original seed's epistemic state. They bind root, exposure kind,
reference, timestamp, contamination state and bounded metadata. Kinds cover:
SOURCE_SEEN, PAPER_SEEN, HISTORICAL_RESULT_CONSULTED, DATASET_EXPOSED,
PREVIOUS_EXPERIMENT, MODEL_PROMPT and PROVENANCE_GAP.

Enrolment records the source/version and evidence refs. Replication adds a known
paper/claim exposure with publication availability. Model source work records its
model identity, prompt hash and prompt/agent family; raw health/provenance hashes
also remain in the immutable seed uncertainty declaration. All generated model
alternatives are enrolled before Policy C selects a registered alternative.

UNKNOWN, KNOWN_EXPOSURE and CONTAMINATED are distinct. UNKNOWN is never proof of
independent discovery. The known published claim remains known even when a
replication later succeeds. Contamination is sticky at root scope; a later
exposure removes that root from eligible policy context and rejects an earlier
proposal's stale Discovery attempt until legitimate requalification.

Market PIT does not erase future published-result knowledge. This ledger cannot
reconstruct an unknown model training set, forgotten human exposures, undocumented
prior experiments or every external interaction. Record PROVENANCE_GAP and UNKNOWN
rather than declaring independence. No contamination score or scientific verdict
is inferred from a source's prestige.

Qualification: `tests/test_giga_f_idea_feed.py` tests pending state after restart,
known claim exposures, later contamination of an eligible proposal, the three
identity axes and recursive outcome/authority rejection.
