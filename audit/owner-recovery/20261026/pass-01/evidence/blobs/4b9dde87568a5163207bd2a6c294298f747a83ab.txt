# CP096 — Shared temporal admission for generation trials

CP095 proves that both pure qualification and native lineage admitted a trial
with generation time outside its epoch window or an invalid timestamp. This
change closes that scientific attribution gap without another runtime clock.

## Reuse and integration

`assert_trial_epoch_window` reuses the existing timezone-aware timestamp parser
and native start-inclusive/end-exclusive research window semantics. It compares
instants, retains the original timestamp strings, and performs no current-time
lookup. Missing, malformed, naive, empty or reversed temporal declarations cannot
pass. Pure qualification invokes the guard before export. Native lineage invokes
it before all five independent challenge stages, retrieval and base execution,
with durable StageBlocked diagnostics through the existing worker mechanism.

Native execution-time and export-cutoff checks stay in force. Generation time,
knowledge cutoff, execution time, export time and feedback time remain distinct.
This checks declared temporal membership, not external proof of when a model ran,
source/model PIT, cognitive independence, permission to execute, or economic value.
No active manifest, policy, trial, freeze or canonical Oracle state is rewritten.

## Qualification

Four new regression methods exercise the actual pure pipeline, rehashed native
trials at all five challenge stages, malformed declarations, timezone-equivalent
boundaries, and unchanged valid receipt/hash/closed-authority replay. Existing
native tests also replay actual disposable Git producer/Validator lifecycles.
The focused package passes 21 tests; full root 827 and broader Research OS 268
PASS (overlapping suites). Ruff F and whitespace checks PASS. The official
status generator records the new inventory. Actual workflow includes the new
module. Exact-source workflow and hosted qualification follow in CP097.

The current JSON fixture remains byte-identical and its entire valid receipt
retains hash 48ec56afa0be00bcd198c38a37b49c89f2b0d00d05b7f055346e887f7b2480e8.
No positive fixture migration or fabricated economic/cohort/capacity premises.
Four authority flags remain literally FALSE. No outcomes accessed, economic
experiment, prospective capture, Site/API probe, VM/Site deployment, cloud config
change, new scheduler, Book, or remote scientific-state write.
