# Inventory-led local backend candidate, not inference qualification

The baseline inventories and actual no-op wakes are checkpointed at
`0b8596b14224b82da03bed2dbf3a3fd0de53566e`. Both unprivileged and Owner-executed
root inspections found no active model runtime and no weights in the inspected
homes/model roots, with no remaining permission gaps in the root scan.
No existing model/runtime is being removed or replaced.

Candidate for one local model download:

- `leeminwaan/gpt-oss-20b-pruned-10.2B-GGUF`, immutable revision
  `456fa90a60ea5249f26c0c2e5c69aab5a91d4676`;
- `gpt-oss-10b-q4_k_m.gguf`, **7723072288 bytes**, LFS SHA256
  `f3a19b894d725229f57a80d28014ee6ad3543bcfcd5dd4496f7b3599e169d240`;
- published source `AmanPriyanshu/gpt-oss-10.2b-specialized-all-pruned-moe-only-14-experts`,
  revision `a6f98493c58e134ac44b4d1ed4516d9d2f5704af`;
- source config confirms `GptOssForCausalLM`, 24 layers, 14 experts, four active
  experts, original `openai/gpt-oss-20b`, Apache-2.0;
- **experimental pruning without retraining**: publisher examples are not
  Research OS validation. Actual local structured reasoning, instruction
  following, resource headroom and latency must pass before H24 activation.
  Model commentary remains unverified and cannot grant scientific authority.

Comparative metadata (no competing full weights downloaded): ordinary 20B
GGUF variants from unsloth/bartowski have a minimum around 11.46 GB, leaving
insufficient proven physical headroom on this 12 GiB VM before runtime buffers.
The 12B alternative's referenced source was inaccessible (HTTP 401), so no
unverified source architecture or quality claim is made about it. The selected
10.2B variant exposes its upstream config and leaves materially more headroom.

Runtime candidate: official llama.cpp `b11742`, source
`4c3c5810f87efe177949f1b85ae509d38a2a311f`, Ubuntu ARM64 CPU asset,
14054733 bytes, official GitHub asset digest
`263700393b5a0f3547ca313ef6040c25482b569dc6aa387bf5a8ecb9949b159e`.
The runtime build is pinned, not a mutable `latest` deployment identity.

The build-only installer stages assets in the unprivileged account's private
directory, bounds disk usage, resumes one partial download only when HTTP Range
is honored, verifies size/hash/GGUF magic, and publishes atomically. An existing
unverified model is not overwritten. It installs/starts no systemd unit.
Normal worker wakes never invoke this installer or download assets.

## Current free allowance and cost gate correction

The current Oracle primary documentation reports **1500 OCPU hours and 9000 GB
hours monthly**, equivalent to **2 OCPUs / 12 GiB H24**, not the historical 4/24
assumption used by the earlier canary. The canary's per-instance upper envelope
is tightened accordingly. No VM resize or extra paid compute is authorized by
service-limit capacity. Current service limits are larger; they are not free
credits and are not used to justify a resize.

A read-only OCI census found one accessible compartment, one subscribed READY
region (Paris, also home region), and exactly this nonterminated A1 VM at 2/12.
No compute resource was changed or created. Tenant-wide billing policy remains
distinct from a per-instance code check.

Sources consulted as data (no remote model-card Python code executed):

- https://huggingface.co/leeminwaan/gpt-oss-20b-pruned-10.2B-GGUF
- https://huggingface.co/AmanPriyanshu/gpt-oss-10.2b-specialized-all-pruned-moe-only-14-experts
- https://github.com/ggml-org/llama.cpp/releases/tag/b11742
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

Build checks: scheduler/inventory/free-envelope/download regression module
**11 PASS**, compilation PASS, diff whitespace check PASS. Exact-head CI and
actual runtime/model inference qualification remain pending for this commit.
All four economic/prospective/capital/live authorities remain false.

The full actual Oracle read-only wake report was reconstructed and SHA256-checked
and is now `CP3_3_ORACLE_READONLY_WAKES_20261019.json`. It adds a final newline
to the host's exact 5114-byte serialization; no report value was changed.
