# CP2b.0 live Oracle access resumed

Baseline exact code and remote HEAD: `0599240dd951ff7b128a8cf43537c6073a6c5c7a`.
Its Oracle Recovery CI `39272929333` and SEC P0 CI `39272926363` were rechecked
completed/successful before the first authenticated VM operation.

An Owner-registered dedicated API signing identity now permits the build session
to use OCI HTTPS APIs. Private key/configuration remain outside the repository.
The durable H24 worker must never depend on this build-session identity.

Live OCI `GetInstance` and `ListVnics` verified the exact Owner-provided instance
`ocid1.instance.oc1.eu-paris-1.anrwiljrtoradqacmugziwzu3sls2orieua6i7vkjveiq7q5wsiypa3mejpa`:
RUNNING, `VM.Standard.A1.Flex`, 2 OCPUs, 12 GiB RAM, no GPU, public IP
`158.178.206.208`, private IP `10.0.0.233`. This is within the per-instance
A1 Free Tier resource envelope; account-wide billing eligibility is not inferred.

Owner-supplied live Run Command evidence establishes SSH service/socket active
and listening on IPv4/IPv6 port 22. The build environment still has no TCP grants;
earlier direct connection refusal did not establish a stopped VM SSH service.
No SSH service repair is necessary based on the available evidence.

Actual build-session read-only probe command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaavbsukt2zlvnxaze2wepchcpnozyjnlfq2pf3uc2wx3mq`.
The original exact-SHA inventory probe failed on `PermissionError` while stating
`/home/ubuntu/.ollama/models` under `ocarun`. This is not evidence that the model
directory is empty or that GPT-OSS is absent. No runtime/model/service was changed.

The bounded repair records inaccessible roots/directories/files as explicit
inspection gaps and retains accessible inventory. It never turns a permission
gap into an absence/health/compatibility PASS. A regression reproduces the denied
root alongside an accessible GGUF and verifies both findings survive.

Build-session validation: scheduler/inventory regressions **7 PASS**, inventory
Python compilation PASS, `git diff --check` PASS. CI on the containing repair
commit is pending; these local checks are not a live GPT-OSS canary.

All four economic/prospective/capital/live authorities remain false. H24 remains
NOT_PROVEN. Pending: complete live inventory, actual backend qualification,
unattended durable GitHub credentials, privileged host preparation/systemd,
canaries and automatic/restart evidence. `ocarun` has no noninteractive sudo;
administrative installation cannot be claimed from API access alone.

## Completed unprivileged inventory

Probe release: `b54dc2fa4c9ae294927c63f9056a5c4dc7746973`.
Oracle Recovery CI `39330759022`: SUCCESS, **136 PASS** (16 Oracle, 29
backend/worker/scheduler/inventory, 91 scientific pre-outcome including ASML).
SEC P0 CI `39330759002` subsequently completed SUCCESS: **555 tests**, **267
SEC-lane tests**, **35/35 V1 checks** and a matching exact-head verification artifact.

Successful actual VM command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaa4xrdtuq5kgihuexc4wgwheyqbqrjzenr4immr4bx674a`.
Observed `2026-10-19T21:54:20.361935+00:00`; execution user `ocarun`.
The sanitized full inventory is `CP2B_0_LIVE_INVENTORY_20261019.json`.
The original 5290-byte host serialization has SHA256
`e4eb6b7f29209ac2a4545a86cb26396357fce524e194260effa95c7848eee6c7`.
Four bounded compressed Run Command responses reconstructed those exact bytes
before JSON validation. The Git copy adds a final newline only.

Live findings: aarch64 Ubuntu 24.04.5, two Neoverse-N1 CPUs, 12506759168 bytes
physical memory, 11845550080 bytes available at observation, **no swap**,
43893039104 bytes root-filesystem space free. No runtime executable was found
on the `ocarun` PATH, no matching model process was observed, no GPT-OSS/Ollama/
llama service fragment was registered under the inspected names, and local
Ollama 11434/OpenAI-compatible 8080 APIs were unreachable. The only listening
ports observed were 22, 53 and 111. No model weights were found in the accessible
requested model roots. `/home/ubuntu/.ollama/models` is an explicit permission
gap, so this is **not** proof that no stored model exists anywhere on the VM.
Model variant, quantization, format, path and inference resource/latency envelope
remain unestablished. No model/runtime was installed, replaced or loaded.

`quant-research-worker.timer` had no installed fragment and was inactive at
observation. No timer was installed or activated by these diagnostics.

Independent SSH host-identity command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaaxd7zbljpuswvky47rytoaq6yaeeyexz4n662pmbdnolq`.
ED25519 server fingerprint:
`SHA256:Ts3tHM+yIBTM7uGLjuMPknpfRB1/ewHnJc/b11yTyAg`.
`ubuntu` belongs to `sudo`; its actual noninteractive privilege and SSH-key
authentication still require a successful login. Owner reports having a local
computer terminal and the matching private SSH key.

Subsequent fingerprint-only comparison against `GetInstance.metadata` established
that the attached private key fingerprint
`SHA256:KjnhlJm+XJc0PrKLIejVygCYW7CNdzB736bn32ZsCs8` does **not** match the
launch-metadata public key fingerprint
`SHA256:0h7LYSESNdPmDnQ2fsGX+YB1gjVPl3TYQXSqdzgwHZM`. Owner's actual Mac SSH
attempt reaches the VM but returns `Permission denied (publickey)`; another
local key file needs permissions corrected before its fingerprint can be checked.
Launch metadata alone does not enumerate later authorized-key changes. No private
key contents were emitted and no guest authorized_keys file was changed.

## Actual VM release qualification, scheduler disabled

Command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaa6pr7lz3aj4slyatcyfdsjyh7duojvby7lbdvvoe53icq`.
The exact `b54dc2fa4c9ae294927c63f9056a5c4dc7746973` release was installed only
into `/var/lib/ocarun/.cache/quant-qualification/releases/` for qualification,
preserving the Owner's previously installed `e980d201d3c84d16d7d91fde0d27a06c9a2c3121`
release and its installation pointer. The versioned installer source SHA256 was
checked before execution.

Result: `INSTALLED_VERIFIED_NO_SCHEDULER`, Python 3.12/aarch64; **98 tests PASS
on the actual Oracle VM**. These installer tests include disposable local Git/HTTP
fixtures on Oracle, not real GitHub task claims or local GPT-OSS inference.
The actual Legacy ledger loaded **20 records**, verified Git blob
`ba9b165aaf96956776672df51233bb9bf1e6cbc9`; all four authorities were false,
`scheduler_started=false`. No economic/prospective/live operation was performed.

## Owner's root inventory and actual fresh-state wakes

Owner successfully logged in as `ubuntu` from the Mac using the original
September 20 key. A pinned-source-hash root inventory then returned
`execution_uid=0`, observed `2026-10-19T22:06:49.655152+00:00`.
`CP2B_0_ROOT_INVENTORY_20261019.json` preserves its JSON extracted from the Owner's
terminal capture; it is explicitly Owner-executed evidence, not an OCI command
silently run as root. The expanded roots include Ubuntu's home and `ocarun`'s
home. No runtime/model/service was found in the inspected scope; the scan was
not truncated and had **no permission gaps**. No model was installed or replaced.
Administrative actions are now available through the Owner's SSH terminal;
OCI Run Command itself still runs as unprivileged `ocarun`.

Actual Oracle read-only worker command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaavylodaoizfe3sa2z6bdmaf5mvtpup6ofjtcgpjgf46oa`.
Both `DRY_RUN` and `READ_ONLY_CANARY` succeeded from the qualified release,
binding fresh GitHub HEAD `b54dc2fa4c9ae294927c63f9056a5c4dc7746973`, with **zero
GitHub writes and zero model calls**. This is not proof of a real claim,
GPT-OSS inference or H24 scheduling. The 5114-byte host JSON SHA256 is
`1452d8be094d22aa98fa7e365473f84ae3e64e1cb9fc51d2071e263fde7612f5`;
the complete report is being retrieved through bounded output segments.
