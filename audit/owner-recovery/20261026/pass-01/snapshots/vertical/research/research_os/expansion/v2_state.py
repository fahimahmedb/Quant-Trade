"""V2 evidence on the existing GitHub transactions; no separate task authority."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict
import hashlib

from research.research_os.github_state import PREFIX
from research.research_os.oracle_worker import clock, lineage_key, next_stage, routing
from research.research_os.worker_stages import DEFAULT_SOURCES, PRODUCERS, StageBlocked
from research.research_os.worker_preflight import run_worker_preflight
from .v2_core import assert_authority_closed, assert_model_allowed, build_priority_decision, canonical_hash
from .v2_stage_executor import _active_epoch, v2_artifact_path

POLICY_PATH = PREFIX + "runtime/V2_CORE_POLICY.json"
RESEARCH_STAGES = {"mechanism_research", "document_or_fundamental_research"}


class V2ModelAudit:
    """Hash actual model inputs, including failures, without trusting model prose."""
    def __init__(self, backend):
        self.backend, self.calls = backend, []

    def __getattr__(self, name):
        return getattr(self.backend, name)

    def healthcheck(self):
        return self.backend.healthcheck()

    def _call(self, method, prompt, schema=None):
        record = dict(method=method, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                      schema_hash=canonical_hash(schema), model=self.backend.model,
                      sampling_parameters=asdict(self.backend.budget), model_pit="NOT_PROVABLE")
        self.calls.append(record)
        try:
            result = (self.backend.generate_structured(prompt, schema) if method == "structured"
                      else self.backend.generate_text(prompt))
            record["execution_state"] = "COMPLETE"
            return result
        except Exception as exc:
            record.update(execution_state="RETRYABLE_ERROR", error_type=type(exc).__name__)
            raise

    def generate_structured(self, prompt, schema):
        return self._call("structured", prompt, schema)

    def generate_text(self, prompt):
        return self._call("text", prompt)


class V2StateStore:
    def __init__(self, store, model_identity="DETERMINISTIC_ENGINE", audit=None, lane="auto"):
        self.store, self.model_identity, self.audit = store, model_identity, audit
        self.lane = lane
        self.last_preflight = None

    def __getattr__(self, name):
        return getattr(self.store, name)

    def _preflight(self, snapshot):
        policy = snapshot.read(POLICY_PATH)
        assert_authority_closed(policy["authority"])
        membrane = policy["evaluation_membrane"]
        if membrane["status"] != "SEALED" or any(membrane[k] is not False for k in (
                "research_outcome_read_capability", "research_supervisor_outcome_read_capability",
                "evaluation_research_write_capability")):
            raise StageBlocked("V2_EVALUATION_MEMBRANE_NOT_SEALED")
        if policy["model_routing"]["silent_hosted_fallback"] is not False:
            raise StageBlocked("V2_HOSTED_FALLBACK_FORBIDDEN")
        resource = policy["resource_policy"]
        if (resource["max_heavy_local_inference"] != 1 or resource["max_authoritative_write_transition"] != 1
                or resource["orchestration_backend"] != "GITHUB_BOUNDED_WRITER"
                or resource["dual_authoritative_backends_allowed"] is not False):
            raise StageBlocked("V2_RESOURCE_OR_ORCHESTRATION_POLICY_NOT_QUALIFIED")
        epoch = _active_epoch(snapshot)
        for key, value in (("research_policy_hash", policy), ("model_routing_policy_hash", policy["model_routing"]),
                           ("source_policy_hash", policy["source_policy"]), ("retrieval_policy_hash", policy["retrieval_policy"]),
                           ("validator_policy_hash", policy["validator_policy"])):
            if epoch[key] != canonical_hash(value):
                raise StageBlocked("V2_EPOCH_POLICY_HASH_MISMATCH:" + key)
        # _active_epoch applies the shared clean/explicit-blinding admission law.
        assert_model_allowed(epoch, self.model_identity)
        self.last_preflight = dict(status="PASS", research_epoch_id=epoch["research_epoch_id"],
                                   epoch_manifest_hash=epoch["epoch_manifest_hash"],
                                   policy_hash=canonical_hash(policy), snapshot_head=snapshot.head)
        return epoch, policy

    @contextmanager
    def snapshot(self):
        with self.store.snapshot() as snapshot:
            self._preflight(snapshot)
            yield snapshot

    def commit(self, snapshot, writes, **kwargs):
        epoch, policy = self._preflight(snapshot)
        writes = deepcopy(writes)
        immutable = list(kwargs.get("create_only", ()))
        binding = {k: self.last_preflight[k] for k in ("research_epoch_id", "epoch_manifest_hash", "policy_hash")}
        for path, task in list(writes.items()):
            if not path.startswith(PREFIX + "tasks/") or not isinstance(task, dict):
                continue
            if path not in snapshot.blobs:
                task["research_contract_version"] = "v2-core"
            execution = task.get("execution") or {}
            prior_binding = execution.get("v2_epoch_binding")
            if prior_binding is not None and prior_binding != binding:
                raise StageBlocked("V2_TASK_EPOCH_OR_POLICY_CHANGED")
            generation = task.get("lease", {}).get("generation", 0)
            intent = v2_artifact_path(task, f"trial_intents/g{generation:06d}")
            if task.get("status") == "CLAIMED":
                execution = task.setdefault("execution", {})
                execution["v2_epoch_binding"] = binding
                lane = routing(snapshot, task)
                stage = next_stage(task, lane)
                decision = self._priority(snapshot, task, policy)
                decision_path = v2_artifact_path(task, f"priority/g{generation:06d}")
                writes[decision_path] = decision
                immutable.append(decision_path)
                if stage in RESEARCH_STAGES:
                    key = PRODUCERS[task["task_type"]]
                    source = task.get("inputs", {}).get("documentary_source")
                    source = source or (PREFIX + "sources/" + DEFAULT_SOURCES[key] if key in DEFAULT_SOURCES else None)
                    writes[intent] = dict(schema_version="v2-ideation-intent-v1", **binding,
                                          task_id=task["task_id"], generation=generation,
                                          session_id=execution["session_id"], state="STARTED_BEFORE_IDEATION",
                                          started_at=task["lease"]["claimed_at"], source_path=source,
                                          source_blob=snapshot.blobs.get(source), model_identity="DETERMINISTIC_ENGINE",
                                          critic_model_identity=self.model_identity,
                                          generated_proposal_count="NOT_YET_KNOWN", outcome_accessed=False)
                    execution["v2_trial_intent"] = intent
                    immutable.append(intent)
            elif intent in snapshot.blobs:
                outputs = [v for p, v in writes.items() if p.startswith(PREFIX + "artifacts/")
                           and isinstance(v, dict) and v.get("stage") in RESEARCH_STAGES]
                if outputs:
                    result = outputs[0]
                    completion = intent.removesuffix(".json") + "-completion.json"
                    writes[completion] = dict(intent=intent, generation=generation, task_status=task["status"],
                                              disposition="RETRYABLE_ERROR" if result.get("retryable") else
                                              "GENERATED_AND_SCREENED" if result.get("engine_output") else "EXECUTION_BLOCKED",
                                              blocker=result.get("blocker"), model_calls=deepcopy(self.audit.calls) if self.audit else [],
                                              scientific_decision=None, outcome_accessed=False)
                    immutable.append(completion)
        kwargs["create_only"] = immutable
        return self.store.commit(snapshot, writes, **kwargs)

    def _priority(self, snapshot, selected, policy):
        tasks = snapshot.tasks()
        now = clock(selected["lease"]["claimed_at"])
        eligible = []
        for task in tasks:
            if task.get("status") not in ("READY", "CLAIMED"):
                continue
            try:
                lane = routing(snapshot, task)
                if self.lane != "auto" and lane != self.lane:
                    continue
            except StageBlocked:
                continue
            lease = task.get("lease") or {}
            if task["status"] == "CLAIMED" and (not lease.get("expires_at") or clock(lease["expires_at"]) > now):
                continue
            retry = (task.get("execution") or {}).get("retry_after")
            if retry and clock(retry) > now:
                continue
            if any(t.get("status") == "CLAIMED" and t["task_id"] != task["task_id"]
                   and lineage_key(t) == lineage_key(task) for t in tasks):
                continue
            run_worker_preflight(snapshot.base, task=task)
            eligible.append(dict(task_id=task["task_id"], priority=int(task.get("priority", 0)),
                                 reason_codes=["CANONICAL_PRIORITY_DESC_TASK_ID_ASC"], resource_cost=1, starvation_factor=0))
        decision = build_priority_decision(policy_version=policy["schema_version"], eligible=eligible)
        if decision["selected_task"] != selected["task_id"]:
            raise StageBlocked("V2_PRIORITY_EXPLANATION_DIFFERS_FROM_CANONICAL_SELECTION")
        decision.update(resource_cost_semantics="UNIFORM_DECLARED_UNIT_NOT_MEASURED", starvation_policy="DISABLED",
                        snapshot_head=snapshot.head, policy_hash=canonical_hash(policy))
        return decision
