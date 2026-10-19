# Oracle Research OS H24 recovery

Runtime: Oracle VM → systemd timer → one bounded Python stage → fresh GitHub
state → canonical task/lease/event/receipt → exit. Reasoning, when needed, uses
an explicitly configured loopback model through `ModelBackend`. No Codex,
ChatGPT, Work, paid model service or model download is part of a normal wake.
Runtime data commits carry `[skip ci]` so normal wakes do not consume hosted
GitHub Actions build minutes. Builder release commits still require exact-head CI.

All four economic/prospective/capital/live authorities remain false. A running
timer does not grant outcome access. Ordinary source/evidence gaps remain
BLOCKED with receipts; they do not cause invented facts or alternative work.

## Current external dependency

The build environment has GitHub access, but no OCI identity/configuration,
SSH key/agent or supported Oracle browser session. Inventory, VM mutation,
GPT-OSS performance and activation are **not yet live-verified**. Evidence is in
`research/research_os/runtime/CP2B_0_LOCAL_MODEL_INVENTORY_20261019.json`.
Do not label the lab RUNNING from CI or from the GitHub read-only smoke.

## 1. Inventory first, without installation

Use the intended instance OCID and exact tested code SHA, through an authenticated
OCI CLI context. The VM identity is never inferred from an old branch.

```sh
python3 deploy/oci_research_os_deploy.py \
  --vm "$QUANT_VM_OCID" --region "$QUANT_OCI_REGION" \
  --sha "$QUANT_RELEASE_SHA" --inventory
```

Alternatively execute `deploy/oracle_model_inventory.py` on that same VM over
already-configured SSH. Preserve its sanitized JSON in a Git checkpoint. The
probe reads runtime versions, model metadata/quantization/size, paths, services,
RSS/swap/CPU samples and loopback APIs. It neither loads nor replaces a model.

Select the existing healthy GPT-OSS variant from this evidence. If repair is
needed, record the observed defect before making a bounded repair. Do not
download multiple large models. Oracle A1 Free Tier requires an evidenced
envelope of at most four OCPUs and 24 GiB total memory; account-wide Free Tier
eligibility still depends on the tenancy. Do not create paid capacity.

## 2. Exact release and service-user preparation

Require a successful **Oracle Economic Loop Recovery CI** run on exactly
`QUANT_RELEASE_SHA`. On the intended VM, use Python 3.12 and the CP1 installer:

```sh
sudo python3.12 deploy/oracle_release_install.py \
  --sha "$QUANT_RELEASE_SHA" --base /opt/quant-research/releases
```

Build `/etc/quant-research/worker.json` from `deploy/oracle-worker.example.json`.
Set the exact SHA, successful `qualification_ci_run_id`, explicit VM OCID,
runtime, loopback endpoint and inventoried model ID. The example deliberately
contains unusable placeholders; it does not select a model without inventory.

```sh
sudo python3.12 -m deploy.oracle_scheduler_install \
  --release "/opt/quant-research/releases/$QUANT_RELEASE_SHA" \
  --config /path/to/nonsecret-worker.json
```

Preparation creates the unprivileged `quant-research` account, publishes the
root-owned release/current pointer and service-user configuration. It stops
an existing timer/service before a repair switches releases. It does **not**
install or enable the units. Do not switch a live pointer around this step.

Provision unattended GitHub read/write credentials outside Git using the
service user's native Git credential configuration or a root-managed
`/etc/quant-research/worker.env` (group-readable only by the service). Never put
tokens, private keys or credential-bearing URLs in worker.json, unit files,
commands, commits or receipts. OCI instance credentials do not grant GitHub access.
Check the credential helper works as `quant-research`; an interactive browser
login or the build session's token is not an H24 credential strategy.

## 3. Pre-activation live canaries

Run as the intended service user, with the same configured noninteractive Git
credentials and Python environment. If using worker.env, load it through a
transient systemd unit with `EnvironmentFile`, never print/source it in a log.

```sh
cd /opt/quant-research/current
sudo -u quant-research /usr/bin/python3.12 -m deploy.oracle_h24_canary \
  --config /etc/quant-research/worker.json \
  --output /var/lib/quant-research/qualification.json
```

The canary verifies the Oracle metadata identity and Free Tier shape envelope,
exact-head CI, non-destructive inventory, local GPT-OSS health and a bounded
structured inference. It runs a dry-run and read-only no-op, then creates a
deterministically named canonical Legacy-provenance task. A real child process
exits immediately after its durable claim. After objectively measured lease
expiry, fresh workers complete two small stages and verify exactly two artifacts
and receipts, without hypotheses, outcomes or capital changes. Its live receipt
is persisted in GitHub. Re-running reuses the same canary lineage.

This proves **process** interruption and durable reconstruction. It does not
pretend to prove a VM reboot. If a canary fails, retain its `BLOCKED` report and
repair the observed cause; activation must stay closed.

## 4. Install and activate after every gate passes

```sh
sudo python3.12 -m deploy.oracle_scheduler_install \
  --release "/opt/quant-research/releases/$QUANT_RELEASE_SHA" \
  --config /etc/quant-research/worker.json \
  --qualification /var/lib/quant-research/qualification.json --activate
systemctl is-enabled quant-research-worker.timer
systemctl is-active quant-research-worker.timer
systemctl list-timers quant-research-worker.timer --all
```

The installer rejects stale (>6 h), wrong-VM, wrong-SHA, wrong-config, CI-only,
missing-gate or unsafe-authority qualification. It verifies the actual instance
again, validates units, then enables and starts the timer. First automatic wake
is due after 45–65 s; later wakes occur every ten minutes with jitter. A oneshot
service is normally inactive between wakes; the timer must remain enabled/active.

## 5. CP4 requires automatic wake and restart evidence

After activation, observe an actual timer invocation (not just a manual start):

```sh
systemctl show quant-research-worker.timer -p ActiveState -p LastTriggerUSec -p NextElapseUSecRealtime
systemctl show quant-research-worker.service -p Result -p ExecMainStatus -p InvocationID
journalctl -u quant-research-worker.service --since '-20 minutes' --no-pager
```

Bind its journald invocation to the exact release SHA, fresh GitHub input HEAD,
output commit and durable receipt/event. Observe two automatic wakes and verify
no repeated completed stage, candidate freeze or handoff. Reboot the actual VM
only when access is reliable, then verify enabled/active timer, fresh GitHub
reconstruction and lease recovery again. Record exactly which restart was tested.

Persist the final live receipt with instance identity, exact SHA, CI run, model
runtime/variant/quantization/latency/resources, Legacy blob/count/partial status,
current corpus hash/count, ASML/readiness regressions, canary task and receipt
references, timer enabled/active and automatic invocation evidence, and all four
closed authorities. Only then report `ORACLE_H24_RESEARCH_LAB = RUNNING`.

## Operations and bounded failures

- Each successful stage is one atomic Git commit containing output, event,
  receipt and task progress. The task blob and exact HEAD are both fenced.
  Unpublished inference can repeat after a crash; economic publications cannot.
- A normal stage releases its lease and returns the same task to READY; the next
  timer wake reconstructs progress. A killed process leaves CLAIMED until its
  objectively expired lease is reclaimed with a new generation.
- A missing/failed model emits explicit retry receipts, waits at least five
  minutes, and blocks after three attempts. No hosted fallback exists.
- Unknown or unsupported source contracts block. Quant-mechanism discovery has
  no qualified real documentary adapter yet; it cannot use synthetic fixtures as
  real evidence. Current built-in real captures cover Fundamental, Event/Document
  and Institutional Flow. Reusing a source does not prove economic distinctness.
- Independent challenge is a separate lane/wake with frozen content binding.
  Missing evidence restricts claims. Integration requires a bound independent
  Red Team PASS; readiness always loads the complete current peer corpus.
- systemd limits worker memory/swap/CPU/time, uses a directory lock, journals
  output and runs without root. The existing model runtime is separate; inspect
  its actual headroom rather than assuming the worker limits constrain it.
- Monitor `free -h`, `df -h`, model RSS/swap/CPU and `journalctl --disk-usage`.
  Daily bounded Git compaction limits loose-object accumulation. No automated
  release/model deletion is performed; retain the active and rollback release,
  review receipts before pruning unused releases, and keep one evidenced model.
- Stop for repair with `systemctl stop quant-research-worker.timer`; never repair
  queue races by force-overwriting a task, deleting receipts or resetting freezes.
