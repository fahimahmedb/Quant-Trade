# CP2b.1–CP2b.4 — canonical local-backend worker

Baseline: `fb831cf26060cbe6487dd953b8683dcbe82a07db`.
CP2b.0 inventory/access evidence: `8ce219fa5415fd3cc53ab7ba89cf46bd4f3094c4`.
CP2b.1 backend: `c23531e838a0a9e974de0d304c0becc5bd4fe692`.
This checkpoint's exact implementation SHA is the Git commit containing this file;
subsequent final evidence records the full tested SHA. No self-referential SHA is invented.

Implemented on the mandatory recovery branch, without merging the stale OCI rail:

- `ModelBackend` interface, local Ollama/OpenAI-compatible HTTP transport, GPT-OSS
  adapter with explicitly configured variant; loopback-only, no hosted fallback;
- fresh exact-ref GitHub snapshot at wake, before claim, before execution and before
  publication; verified pinned Legacy materialization and full current corpus;
- canonical routing, task blob lock, incrementing lease generation, expiry fencing,
  one lineage and one small stage per wake;
- producer, challenge, evidence and integration adapters onto existing scientific
  functions; model prose is unverified commentary and cannot grant a scientific PASS;
- atomic Git publication of stage output, event, receipt and task progress; exact
  HEAD compare-and-swap, including protection against a concurrently rewound ref;
- persisted completed-stage hashes, immutable artifact/freeze/handoff paths,
  bounded retries with explicit receipts; terminal tasks never re-execute;
- canonical deterministic queue replenishment, never producer execution in refill wake.

Build-environment evidence (not live Oracle evidence):

- `python -m unittest research.research_os.tests.test_model_backend`: **6 PASS**.
- `python -m unittest research.research_os.tests.test_oracle_worker`: initial **10 PASS**;
  three additional actual-worker-race/refill/fresh-state cases: **3 PASS**.
- Oracle installer/orchestrator + worker preflight + readiness integration + queue
  replenishment: **52 PASS**, including real ASML regression.
- compilation of the transport, stage adapters and worker: **PASS**.

The tested crash windows are before claim, after claim, after execution, after
event staging/before receipt, after receipt staging/before task transition, and
after successful remote publication/lost acknowledgement. Event/receipt/task
staging windows are deliberately unobservable remotely because they publish in
one transaction. An unpublished model call may repeat; a freeze, handoff or
experiment-plan publication cannot partially repeat.

Remaining: exact-head CI, scheduler packaging/canaries, authenticated Oracle
transport, actual GPT-OSS inventory/health/performance and live timer evidence.
No runtime/model installation or scheduler activation has occurred.
All four economic/prospective/capital/live authorities remain false.
