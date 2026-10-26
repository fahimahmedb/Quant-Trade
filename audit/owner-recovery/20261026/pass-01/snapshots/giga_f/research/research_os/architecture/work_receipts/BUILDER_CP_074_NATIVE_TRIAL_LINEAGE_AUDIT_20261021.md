# CP074 — Native export misses trial/epoch lineage admission

Base d0a053e6c9f06514083a7aae3abbb9536bc7639e (CP073). Root 791, broader
Research OS 268 and all actual local V2 workflow steps PASS. The exact-source
read-only GitHub entrypoint has zero writes and pushes. Hosted V2 run 39590451263
has succeeded; SEC 39590451302 is still in progress at this audit, not yet claimed
successful. No dependent source edit took place during the exact local workflow.

## Reproduce / bound the evidence

Run the existing positive native claim-restriction/export test. Intercept only its
FakeSnapshot.read for the declared producer research_trial path. Separately:
change research_trial_id to OTHER and correctly rebuild the trial; change its
research_epoch_id to OTHER and correctly rebuild; replace trial_hash with zeros.
Every case still passes the native positive export assertions. The existing test
mocks the underlying V1 stage, so this is an isolated native-stage reproduction,
not proof of a full production exploit. Its declared candidate/validator binding
and closed authority remain intact.

Code inspection confirms _trial_sidecar merely reads the referenced object and
claim_restriction hashes its supplied trial_hash into exported history without
checking the trial body, candidate trial ID or candidate/trial/active epoch join.
The pure v2_pipeline already compares those identifiers; native V2StageExecutor
does not reuse that law. V2StateStore separately binds task execution to active
policy/epoch; it does not validate the referenced candidate/trial pair. Fresh
source reconstruction intentionally preserves these envelope coordinates and
cannot stand in for their canonical gate.

## Reuse / next repair

Use the existing trial constructor/hash and active epoch, not another trial ledger.
Before native independent-challenge work, require the task epoch manifest, candidate
epoch, trial epoch and candidate trial ID to agree, verify the complete trial
body/counts/hash, and join the proposed hypothesis/generation/source-candidate hash
and documentary packet hash to its recorded generation trial. A valid but unrelated
trial must not launder multiplicity history. Do not infer effective independent N
from a matching proposal or replay these trials as new scientific attempts.

Test separately hash-invalid versus correctly rehashed foreign records, native
refusal before base reasoning/writes, valid source/trial replay and actual local
Git worker paths. Existing minimal native unit fixtures must be completed with
coherent source/trial bindings rather than exempted. No outcome, prospective,
production or skipped network task; all four authority flags remain FALSE.
