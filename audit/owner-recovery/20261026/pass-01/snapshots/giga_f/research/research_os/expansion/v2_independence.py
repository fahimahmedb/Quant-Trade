"""Independent retrieval and process provenance for deterministic structural gates."""
import os
from pathlib import Path

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.github_state import PREFIX
from research.research_os.worker_stages import StageBlocked
from .v2_bridge import adapt_engine_output_to_v2_candidate
from .v2_core import canonical_hash

AXES = ("information_isolation", "retrieval_independence", "cognitive_independence", "state_isolation")


def process_identity():
    # PID alone can be reused, including across a reboot.
    stat = Path("/proc/self/stat").read_text().rsplit(")", 1)[1].split()
    return dict(boot_id=Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                pid=os.getpid(), start_ticks=stat[19])


def independent_context(snapshot, candidate):
    producer = candidate["producer_identity"]
    process = process_identity()
    previous = producer.get("process")
    if not previous or previous == process:
        raise StageBlocked("V2_VALIDATOR_DISTINCT_PROCESS_NOT_PROVEN")
    manifest = candidate["evidence_manifest"]
    path = manifest.get("source_path", "")
    if (not path.startswith(PREFIX + "sources/") or ".." in Path(path).parts
            or snapshot.blobs.get(path) != manifest.get("source_blob")):
        raise StageBlocked("V2_VALIDATOR_SOURCE_BINDING_NOT_PROVEN")
    # Snapshot.read independently verifies the fresh Git blob. Re-run the
    # registered parser from primary evidence, never from producer commentary.
    source = snapshot.read(path)
    engine = next((e for e in ENGINE_REGISTRY.values() if e.engine_id == manifest["engine_id"]), None)
    if engine is None or source.get("documentary_packet", {}).get("evidence_class") != "DOCUMENTARY":
        raise StageBlocked("V2_VALIDATOR_PRIMARY_SOURCE_NOT_QUALIFIED")
    rebuilt = engine.run(source, EngineContext(producer["task_id"], synthetic_only=False))
    if canonical_hash(rebuilt["candidate"]) != manifest.get("source_candidate_hash"):
        raise StageBlocked("V2_VALIDATOR_INDEPENDENT_RECONSTRUCTION_MISMATCH")
    projected = adapt_engine_output_to_v2_candidate(
        rebuilt, research_trial_id=candidate["research_trial_id"],
        research_epoch_id=candidate["research_epoch_id"], producer_identity=producer,
        disconfirmation_manifest=candidate["disconfirmation_manifest"],
        source_binding={key: manifest[key] for key in ("source_path", "source_blob", "source_candidate_hash")},
    )
    actual_hash = canonical_hash({key: value for key, value in candidate.items() if key != "candidate_hash"})
    if projected["candidate_hash"] != actual_hash or candidate.get("candidate_hash") != actual_hash:
        raise StageBlocked("V2_VALIDATOR_CANDIDATE_RECONSTRUCTION_MISMATCH")
    return dict(**dict.fromkeys(AXES, True), process=process,
                retrieval={"snapshot_head": snapshot.head, "source_path": path, "source_blob": snapshot.blobs[path],
                           "reconstructed_candidate_hash": canonical_hash(rebuilt["candidate"]),
                           "reconstructed_v2_candidate_hash": projected["candidate_hash"]},
                information_scope="PRIMARY_SOURCE_AND_FROZEN_CANDIDATE_NO_PRODUCER_MODEL_COMMENTARY",
                cognitive_scope="R0_DETERMINISTIC_STRUCTURAL_CHECKS_ONLY",
                semantic_diverse_review="NOT_PROVEN_NO_SEMANTIC_PASS_GRANTED", outcome_accessed=False)
