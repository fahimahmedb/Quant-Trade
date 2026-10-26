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
