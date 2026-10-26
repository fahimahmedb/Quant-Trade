# CP3 local GPT-OSS policy-bound qualification

Executable qualification release: e20e8530a177ae9e197cf9578fae0a503f3b3d09.
Oracle Recovery CI 39337086694: SUCCESS, 145 tests. General SEC P0 CI
39337086596: SUCCESS. These remain CI evidence, not native scheduler evidence.

Actual Oracle requalification command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaaltcji5sgqrfy3zl672eijrfnik4yilyd567t4g3t7zba`.
The command returned exit 0 after 4m3.971s. Its long-command TEXT output was
empty, so a separate actual-file probe verified the result rather than treating
the exit code alone as scientific quality evidence:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaabvknh5vbrehqjlbifla66lddif53jfejdyhqz34npsoa`.

Actual result: PASS_LOCAL_COMMENTARY_BACKEND_ONLY, all five cases passed:
closed authority, unresolved structural overlap, missing correlation,
independent validation, and proved-distinct structural-only screening. The
representative production structured critique also completed. This qualifies
bounded unverified commentary with the explicit production policy, not general
autonomous scientific competence or economic correctness.

The complete successful host serialization is preserved byte-for-byte in
CP3_LOCAL_MODEL_POLICY_QUALIFIED_20261020.json: 5244 bytes, SHA256
6535991128be78afc59d0dcceffe88ade06677a23b2709b76454daf2ef9a0631.
Four bounded initial transport chunks and a fifth verified chunk reconstructed
these exact bytes. The production critique took 49.641 seconds. Scored case
latencies were 48.215, 28.478, 18.893, 19.048 and 38.275 seconds.

The proposed operational release is f138c980c94eea313fd77532c20857da5c02d3fe,
with Oracle CI 39338286363 and SEC P0 CI 39338286411 both SUCCESS. Its worker,
backend and policy are identical to the locally qualified e20e853 release; the
host model memory cap is the measured 10G adjustment described below.

The original failed attempt is preserved byte-for-byte in
CP3_LOCAL_MODEL_FIRST_REJECTION_20261020.json (3818 bytes, SHA256
4d960fec523d71cc4c6b00acea06332b4f486b97a7781c5f65ba779b354a62fd).
Its incorrect PASS for unresolved overlap is not hidden or relabeled a pass.

One and the same verified 7723072288-byte GGUF was reused; no competing model
weights were downloaded. Actual local model metadata reports 10160237712
parameters, Q4_K - Medium, active context 8192, embedding 2880, training context
131072. Runtime: ARM64 CPU llama.cpp b11742 / 4c3c5810f; alias
gpt-oss-10.2b-q4-k-m. Model bytes SHA256:
f3a19b894d725229f57a80d28014ee6ad3543bcfcd5dd4496f7b3599e169d240.

Measured end-of-qualification RSS 9564652 KiB; peak RSS 9883908 KiB (~9.43 GiB),
MemAvailable 8888588 KiB, no swap. The temporary server was stopped and the
subsequent probe found no llama-server process. Model service MemoryMax is
therefore raised from the previously proposed 9G to 10G, leaving the independent
768M worker budget and OS headroom inside this VM's 12 GiB shape. Actual service
cgroup behavior and inference must still be canaried; RSS is not a cgroup proof.

The VM-native repository deploy key successfully authenticated as this exact
GitHub repository. No private half was exported. Real canonical writes, root
preparation, live claim/process-death recovery, timer activation, automatic
wakes and reboot recovery remain pending. No model or worker service/timer was
installed or enabled by this temporary qualification. Authorities remain false;
ORACLE_H24_RESEARCH_LAB is still NOT_PROVEN.
