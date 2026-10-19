# CP2b.5 / CP3.0 — worker qualification and scheduler assets

Verified worker commit: `3171c729b0bf1bdc0c8996272799b1bd1b76e1a2`.
Oracle Recovery CI: run `39268854298`, **SUCCESS** on that exact SHA.

Actual GitHub read-only smoke on the same SHA: **DRY_RUN**, zero writes, zero
hosted model calls. Real Legacy source `183ad65ff260b903a16548ce37948f54d47a9ec8`,
blob `ba9b165aaf96956776672df51233bb9bf1e6cbc9`, **20 loaded records**, manifest
census **33**, `PARTIAL_WITH_EXPLICIT_GAPS` preserved. **13** current hypotheses,
corpus `8dc9f4b770152c60887540b0f8d8047202657fd38e607c8520153dd45fc2e544`;
the ASML pair remains flagged for unresolved overlap.

Additional build-environment verification after the worker checkpoint:

- Oracle + pre-outcome regressions: **107 PASS**.
- Worker/backend/systemd gates: **25 PASS** before the additional OCI-inventory
  identity test; exact final CI records the complete count.
- `systemd-analyze verify`: **PASS**. No local unit installation/activation.
- CP1 installer now also runs worker/backend regressions before publication.
- Root status artifacts regenerated with `scripts/status_artifacts.py --write`
  to repair the observed stale unit-test count; no scientific results changed.

Scheduler assets, service-user preparation, live qualification driver, gated
activation and operational runbook are part of this checkpoint. Inventory can
also be delivered through the existing OCI orchestrator with `--inventory` and
an operation-specific resume identity, without invoking the release installer.

**Not established:** CP3.1 Oracle installation, CP3.2 actual GPT-OSS health,
CP3.3 live no-op, CP3.4 actual VM/process recovery, CP3.5 enabled timer, CP4 H24.
No OCI identity/SSH transport is configured in this build environment. The
canary code and CI are not substitutes for these live measurements.

All economic/prospective/capital/live authorities remain false. Exact-head CI
and final machine-readable evidence follow this checkpoint.
