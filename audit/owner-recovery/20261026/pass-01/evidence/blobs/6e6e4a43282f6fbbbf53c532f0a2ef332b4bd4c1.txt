# BRANCH FAMILY DISPOSITION — 2026-10-20

Authority: CP12 deep organizational audit.

Observed repository branch count: **229**.

This family map covers the largest branch-sprawl clusters and defines what must happen before refs can be retired. It is semantic cleanup guidance, not destructive authorization.

## Summary

| Family | Observed refs | Current class | Intended consolidation |
|---|---:|---|---|
| Weather V4 | 48 | governance + scientific evidence | consolidate Owner decisions, audits, implementation and memory |
| Gate B | 29 | historical governance/host evidence | compress into final Gate-B historical authority record |
| P0 / post-P0 | 31 | historical governance/data/product evidence | preserve canonical/falsifier/product capabilities, retire intermediate refs |
| Live Lab | 10 | active parallel product + historical product evidence | reconcile to one canonical Live Lab rail |
| F1 | 9 | scientific evidence chain | import capture/discovery/final REJECT memory, then retire intermediates |
| Research OS named family | 6 | mixed live source / absorbed / historical | import aggressive source, keep V1/V2, retire proven ancestors |

These six families alone account for **133 / 229** branch refs.

---

# 1. Weather V4 — 48 refs

Observed branches:

### Astra — independent audit/recheck evidence

- `astra/weather-v4-a2-bounded-runtime-test-evidence-audit-2026-10-05`
- `astra/weather-v4-a2-d1-d5-static-recheck-2026-10-05`
- `astra/weather-v4-a2-d5-type-repair-runtime-evidence-audit-2026-10-05`
- `astra/weather-v4-a2-dedicated-harness-static-audit-2026-10-04`
- `astra/weather-v4-a2-doc-integration-lot1-review-2026-10-07`
- `astra/weather-v4-a2-lot3-independent-review-2026-10-08`
- `astra/weather-v4-a2-residual-d5-final-static-recheck-2026-10-05`
- `astra/weather-v4-edge-map-overfit-audit-2026-10-04`
- `astra/weather-v4-pre-op-contract-audit-2026-10-04`

Disposition: `SCIENTIFIC_AUDIT_MEMORY -> CANONICAL_WEATHER_MEMORY -> RETIRE_INTERMEDIATE_REFS`.

### Blue — decision support / integration / governance evidence

- `blue/weather-v4-a1-documentation-2026-10-04`
- `blue/weather-v4-a2-consolidated-preparation-2026-10-06`
- `blue/weather-v4-a2-governance-configuration-draft-2026-10-05`
- `blue/weather-v4-a2-harness-attestation-2026-10-04`
- `blue/weather-v4-a2-harness-suitability-assessment-2026-10-04`
- `blue/weather-v4-od04-od12-decision-support-2026-10-04`
- `blue/weather-v4-phase-gate-decision-support-2026-10-04`
- `blue/weather-v4-research-design-repair-2026-10-04`
- `blue/weather-v4-structural-pre-op-contract-2026-10-04`

Disposition: `GOVERNANCE_SUPPORT_MEMORY`; never upgrade Blue support into Owner authority.

### Builder — implementation/test/dossier evidence

- `builder/weather-v4-a2-astra-d1-d5-static-repair-2026-10-05`
- `builder/weather-v4-a2-bounded-offline-harness-tests-2026-10-05`
- `builder/weather-v4-a2-d5-public-state-type-repair-tests-2026-10-05`
- `builder/weather-v4-a2-dedicated-harness-construction-2026-10-04`
- `builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08`
- `builder/weather-v4-a2-lot2-j1-context-pins-2026-10-08`
- `builder/weather-v4-a2-lot2-l2i-verification-2026-10-08`
- `builder/weather-v4-a2-lot2-l2j-dossier-2026-10-08`
- `builder/weather-v4-a2-lot2-owner-package-2026-10-08`
- `builder/weather-v4-a2-lot2-q22-host-attestation-2026-10-08`
- `builder/weather-v4-a2-lot2-q27-retention-2026-10-08`
- `builder/weather-v4-a2-lot2-tooling-2026-10-07`
- `builder/weather-v4-a2-lot2-vm-kit-2026-10-08`
- `builder/weather-v4-a2-residual-d5-final-state-invariant-repair-2026-10-05`

Disposition: preserve unique implementation/test evidence until the Weather memory package identifies which files are imported, historical-only or rejected. The `doc-integration-root-candidate` is an evidence anchor, NOT final activated authority.

### Owner — authority/decision evidence

- `owner/weather-v4-a2-bounded-offline-harness-test-authority-2026-10-05`
- `owner/weather-v4-a2-dedicated-harness-builder-decision-2026-10-04`
- `owner/weather-v4-a2-execution-authority-draft-2026-10-08`
- `owner/weather-v4-a2-execution-authority-e-d2-2026-10-08`
- `owner/weather-v4-a2-harness-attestation-decision-2026-10-04`
- `owner/weather-v4-a2-harness-suitability-decision-2026-10-04`
- `owner/weather-v4-a2-lot2-freezes-2026-10-08`
- `owner/weather-v4-a2-lot2-technical-authorization-2026-10-07`
- `owner/weather-v4-a2-partial-configuration-decision-2026-10-06`
- `owner/weather-v4-a2-residual-d5-final-state-invariant-repair-2026-10-05`
- `owner/weather-v4-a2-static-audit-repair-decision-2026-10-05`
- `owner/weather-v4-a2-team-charter-ratification-2026-10-08`
- `owner/weather-v4-od01-od03-decision-2026-10-04`
- `owner/weather-v4-od04-od12-structural-decision-2026-10-04`
- `owner/weather-v4-phase-gate-a1-decision-2026-10-04`

Disposition: `OWNER_GOVERNANCE_REQUIRED`. Each must be normalized by explicit artifact status: ratified, partially ratified, structurally ratified, conditional, draft, superseded. `draft` is never authority.

### Team coordination

- `team/weather-v4-a2-coordination-2026-10-08`

Disposition: historical coordination channel. Once all referenced Owner/Builder/Astra evidence is indexed, this ref should not remain current routing.

### Family exit condition

Create one canonical Weather memory package containing:

- Owner decision registry with exact source SHA;
- Builder implementation/test index;
- Astra review index;
- scientific result/exposure state;
- explicit unresolved fields;
- branch-tip mapping.

After independent verification of that package, most of these 48 refs should be retireable as refs without losing evidence.

---

# 2. Gate B — 29 refs

Observed branches span:

- 5 Astra review/recheck refs;
- 8 Blue activation/integration/repair/preseal refs;
- 11 Builder evidence/schema/lock/lifecycle/mutation/run-authority refs;
- 4 Operator host/preflight refs;
- 1 Parallel adversarial precheck ref.

Current class:

`HISTORICAL_GOVERNANCE_AND_TARGET_HOST_EVIDENCE`

Gate B is not current V2 routing authority.

Required consolidation:

1. identify final Gate-B disposition and exact final authority/evidence SHAs;
2. retain host evidence and any false-pass/falsifier lesson required for future audit;
3. record which Builder fixes were absorbed by later runtime/product lines;
4. reduce intermediate dispatch/prestage/preseal refs after proof.

Do not preserve 29 active branch refs merely to keep Git history reachable; Git commits/tags/indexed evidence can carry that history.

---

# 3. P0 / post-P0 — 31 refs

This family includes:

- Astra deep-adversarial/Gate-A/hybrid/restart reviews;
- Blue audit/calendar/continuity/Gate-A/manual-probe refs;
- Builder Gate-A/hybrid/Post-P0/SEC raw-capture refs;
- Parallel Post-P0 design/preparation refs.

Current class:

`HISTORICAL_GOVERNANCE_EVIDENCE + SOME_SOURCE_IMPORT_REQUIRED`

Important exception:

`builder/sec-form4-p0-raw-capture` and related SEC lineage cannot be blindly retired while Evidence/Identity/SEC Census V2 sources are still unabsorbed.

Historical cleanup already established that some divergent P0 falsifier/audit/recovery refs carried unique evidentiary value even after a Gate PASS. Preserve that principle.

Target state:

- compact final P0/Gate-A authority record;
- compact falsifier/audit record;
- Data/SEC product capabilities explicitly imported/rejected;
- intermediate branch namespace retired.

---

# 4. Live Lab — 10 refs

Observed:

- `builder/live-lab-3d-full-build-20261015`
- `builder/live-lab-full-autonomy-20261015`
- `builder/live-lab-native-integration-20261015`
- `builder/live-lab-oracle-canonical-20261020`
- `builder/live-lab-oracle-integration-20261020`
- `builder/live-lab-owner-ux-rebuild-20261015-checkpoint`
- `builder/live-lab-owner-ux-rebuild-20261015-checkpoint-2`
- `builder/live-lab-owner-ux-rebuild-20261015`
- `builder/live-lab-platform-probes-20261013`
- `builder/live-lab-ux-vision-20261014`

Current class:

`LIVE_PARALLEL_PRODUCT_RECONCILIATION_REQUIRED`

Important facts:

- two `owner-ux-rebuild` checkpoint refs point to the same old 3D tip and are obvious namespace-redundancy candidates after reconciliation;
- the old 3D branch retains unique commits/capability;
- Oracle canonical and Oracle integration rails diverge.

Target state:

`ONE_CANONICAL_LIVE_LAB_RAIL + PRODUCT_EVIDENCE_INDEX + RETIRED_CHECKPOINT/INTERMEDIATE_REFS`

---

# 5. F1 — 9 refs

Observed:

- `builder/f1-decision-integrity-repair-2026-10-08`
- `builder/f1-persistent-stage-a-2026-10-08`
- `builder/f1-sealed-stage-b-capture-2026-10-09`
- `builder/f1-stage-a-evidence-37900200192-1`
- `builder/f1-stage-a-evidence-37903239892-1`
- `builder/f1-stage-a-evidence-37915190172-1`
- `builder/f1-stage-a-execution-2026-10-09`
- `builder/f1-stage-b-evidence-38006324356-1`
- `executor/f1-trailing-volume-ranking-fix-2026-10-08`

Current class:

`SCIENTIFIC_EVIDENCE_CHAIN`

Final scientific memory must preserve:

- exact acquisition evidence;
- Stage A discovery result/exposure;
- Stage B final fixed-family `REJECT`;
- decision-integrity repairs that affect interpretation;
- no rerun of consumed A/B looks merely to consolidate Git.

After exact result/protocol/capture SHAs are indexed, most evidence-run branches should become ref-retirement candidates.

---

# 6. Named Research OS — 6 refs

Observed:

- `build-review/research-os-depth-64a6c455-20261015`
- `builder/research-os-aggressive-architecture-20261015`
- `builder/research-os-autonomous-econ-readiness-port-20261016`
- `builder/research-os-autonomous-loop-20261015`
- `builder/research-os-econ-readiness-activation-20261017`
- `builder/research-os-vm-autonomy-20261019`

Disposition:

- aggressive architecture: `SOURCE_IMPORT_REQUIRED`;
- autonomous loop: verified absorbed ancestor;
- autonomous econ readiness port: verified absorbed ancestor;
- econ readiness activation: verified absorbed ancestor;
- VM autonomy: historical implementation side rail, small divergence to index;
- build-review depth: review whether proof is already represented by aggressive architecture/current V2 tests.

This family can likely shrink aggressively after the aggressive-source and VM/proof deltas are explicitly reconciled.

---

# 7. Remaining ~96 refs

The remaining namespace consists of mixed:

- opaque `claude/*` session branches;
- `parallel/*` architecture/research proposals;
- other `research/*` source/readiness/economic-test branches;
- `sol/scout-*` source/edge scouting;
- operator/recovery/UX refs;
- historical Blue/Astra branches outside the major patterns above.

Default disposition:

`UNKNOWN_REVIEW_REQUIRED`

They require a second-pass semantic sweep using the same tests:

1. strict ancestor/duplicate?
2. unique capability?
3. scientific result/exposure?
4. Owner/governance evidence?
5. active work?
6. imported/rejected/indexed elsewhere?

No opaque branch should survive forever merely because it might matter; conversely no opaque branch should be deleted merely because its name is unhelpful.

---

# 8. Family-level cleanup principle

The efficient cleanup unit is now the **completed workstream**, not the individual branch.

For each family:

`DISCOVER ALL REFS -> IDENTIFY FINAL/UNIQUE INFORMATION -> IMPORT/INDEX -> INDEPENDENTLY VERIFY -> MARK ALL INTERMEDIATE REFS RETIREABLE -> OWNER DELETES BATCH`

This is how the repository can fall from 229 branches to a small active set without throwing away the project history that V2 still needs.