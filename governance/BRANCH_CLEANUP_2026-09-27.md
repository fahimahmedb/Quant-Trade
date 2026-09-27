# Ménage des branches — 2026-09-27

Inventaire des 99 branches distantes de `fahimahmedb/Quant-Trade`. Référence : `governance/GITHUB_BRANCH_HYGIENE_2026-09-21.md`.
« Unique » = commits non atteignables depuis les branches CONSERVER. Rien n'a été supprimé par cette session (le proxy Git refuse les écritures hors de sa branche).

Règles : CONSERVER = master, ACTIVE, FROZEN de l'index d'hygiène, et sessions `claude/*` actives depuis le 2026-09-25. SUPPRIMER = rien d'unique hors documents, et ces documents sont copiés octet pour octet dans `archive/branches/` (`archive/branches/INDEX.md`). DÉCISION = du code ou des preuves qui n'existent nulle part ailleurs ; suppression seulement après tag.

## SUPPRIMER (38) — sans perte

| Branche | Dernier commit | Tip | Raison |
|---|---|---|---|
| `astra/first-vertical-independent-review-2026-09-21` | 2026-09-21 | `264f31aebf93` | documents seulement, copiés dans `archive/branches/` |
| `astra/gate-b-evidence-schema-false-pass-recheck-2026-09-21` | 2026-09-21 | `65e05aa86d54` | code déjà identique ailleurs ; documents copiés |
| `astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21` | 2026-09-21 | `02432fae0ceb` | documents seulement, copiés dans `archive/branches/` |
| `astra/gate-b-v4-transition-independent-preactivation-review-2026-09-21` | 2026-09-21 | `aff6b7a2ca63` | documents seulement, copiés dans `archive/branches/` |
| `astra/p0-deep-adversarial-pre-t0` | 2026-09-20 | `643deacdf5bb` | aucun commit hors branches conservées |
| `blue/checkpoint-gate-a-v2-audit-2026-09-20` | 2026-09-20 | `4678c29eb8cd` | documents seulement, copiés dans `archive/branches/` |
| `blue/gate-b-route1-seal-integration-2026-09-21` | 2026-09-22 | `738c4a5425e1` | documents seulement, copiés dans `archive/branches/` |
| `blue/gate-b-run-authority-repair-dispatch-2026-09-21` | 2026-09-21 | `58b559767ddb` | aucun commit hors branches conservées |
| `blue/gate-b-run-authority-repair-integration-2026-09-21` | 2026-09-21 | `644da76eb022` | aucun commit hors branches conservées |
| `blue/gate-b-run-reservation-activation-preseal-2026-09-21` | 2026-09-21 | `5041df45da2d` | documents seulement, copiés dans `archive/branches/` |
| `blue/integration-readiness-2026-09-20` | 2026-09-20 | `37e9f95f3e24` | documents seulement, copiés dans `archive/branches/` |
| `blue/long-horizon-research-2026-09-20` | 2026-09-20 | `7e0fae86834d` | documents seulement, copiés dans `archive/branches/` |
| `blue/p0-calendar-dst-proof-2026-09-20` | 2026-09-20 | `99a64981b7f3` | code déjà identique ailleurs ; documents copiés |
| `blue/p0-gate-a-v2-final-2026-09-20` | 2026-09-20 | `db166fd04c68` | aucun commit hors branches conservées |
| `blue/p0-gate-a-v3-frozen-2026-09-20` | 2026-09-20 | `2da079d8ad75` | aucun commit hors branches conservées |
| `builder/gate-b-deployed-byte-verifier-m4-repair-2026-09-21` | 2026-09-21 | `e19f45709b9e` | aucun commit hors branches conservées |
| `builder/gate-b-evidence-reception-prestage-2026-09-21` | 2026-09-21 | `f5721d62bd02` | documents seulement, copiés dans `archive/branches/` |
| `builder/gate-b-evidence-schema-false-pass-fix-2026-09-21` | 2026-09-21 | `12a666fde821` | code déjà identique ailleurs ; documents copiés |
| `builder/gate-b-f11-lock-identity-repair-2026-09-21` | 2026-09-21 | `8a30bd385f6f` | documents seulement, copiés dans `archive/branches/` |
| `builder/gate-b-lock-path-identity-repair-2026-09-21` | 2026-09-21 | `e600295b2aa7` | aucun commit hors branches conservées |
| `builder/gate-b-offline-lifecycle-sanitization-prestage-2026-09-21` | 2026-09-21 | `6693b1e91feb` | documents seulement, copiés dans `archive/branches/` |
| `builder/gate-b-run-authority-m1-m3-repair-2026-09-21` | 2026-09-21 | `2d2ff4e32f23` | aucun commit hors branches conservées |
| `builder/gate-b-run-authority-mechanisms-2026-09-21` | 2026-09-21 | `845dfa3609a9` | aucun commit hors branches conservées |
| `builder/gate-b-run-authority-retention-prestage-2026-09-21` | 2026-09-21 | `51a2b9074340` | documents seulement, copiés dans `archive/branches/` |
| `builder/gate-c-prospective-event-plan-prestage-2026-09-21` | 2026-09-21 | `4c8312582e28` | documents seulement, copiés dans `archive/branches/` |
| `builder/p0-effective-unit-digest-stability-v4-2026-09-20` | 2026-09-20 | `b10cde0dd193` | documents seulement, copiés dans `archive/branches/` |
| `builder/p0-gate-a-v3-2026-09-20` | 2026-09-20 | `2da079d8ad75` | aucun commit hors branches conservées |
| `claude/confident-allen-xw7eb6` | 2026-09-21 | `edd130790506` | documents seulement, copiés dans `archive/branches/` |
| `claude/nasdaq-trading-model-design-h3mp4n` | 2026-09-13 | `8fea558143d0` | aucun commit hors branches conservées |
| `operator/gate-b-f5-route1-host-feasibility-2026-09-21` | 2026-09-21 | `a5493f052c45` | documents seulement, copiés dans `archive/branches/` |
| `operator/gate-b-read-only-preflight-2026-09-21` | 2026-09-21 | `44285788fce3` | documents seulement, copiés dans `archive/branches/` |
| `parallel/antigravity-gate-b-run-authority-adversarial-precheck-2026-09-21` | 2026-09-21 | `644da76eb022` | aucun commit hors branches conservées |
| `parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21` | 2026-09-21 | `568eea1e0283` | documents seulement, copiés dans `archive/branches/` |
| `parallel/claude-economic-question-falsification-map-2026-09-21` | 2026-09-21 | `7a411524d623` | documents seulement, copiés dans `archive/branches/` |
| `parallel/claude-research-frozen-effect-estimate-prestage-2026-09-21` | 2026-09-21 | `1226427082e5` | documents seulement, copiés dans `archive/branches/` |
| `parallel/claude-s11-dependence-interval-challenge-2026-09-21` | 2026-09-21 | `7080288b5c88` | documents seulement, copiés dans `archive/branches/` |
| `parallel/economic-acceleration-2026-09-21` | 2026-09-21 | `8af21cf2df14` | documents seulement, copiés dans `archive/branches/` |
| `reviewer/v1-final-red-team` | 2026-09-14 | `37f298423ca4` | aucun commit hors branches conservées |

## DÉCISION DU PROPRIÉTAIRE (31) — code ou preuve unique

Supprimer seulement après un tag `archive/<branche>` sur le tip (commande en bas), sinon ces fichiers disparaissent. La plupart sont des itérations de preuve P0 / Gate A (l'index d'hygiène demande de ne pas détruire les commits de preuve).

| Branche | Dernier commit | Tip | Fichiers non-doc perdus sans tag | Exemples |
|---|---|---|---|---|
| `astra/checkpoint-gate-a-v2-independent-audit-2026-09-20` | 2026-09-20 | `357b0e58bcf2` | 1 | `tests/test_gate_a_v2_independent_audit.py` |
| `astra/gate-b-run-authority-mechanisms-recheck-2026-09-21` | 2026-09-21 | `41c3f291f46b` | 1 | `tests/test_astra_gate_b_run_authority_recheck_probe.py` |
| `astra/p0-deep-adversarial-2026-09-19` | 2026-09-19 | `816b999832d3` | 20 | `.github/workflows/sec-p0-pre-t0-gate.yml`, `deploy/quant-sec-capture.service`, `deploy/quant_sec_supervisor.py` … |
| `astra/p0-gate-a-v2-independent-audit-2026-09-20` | 2026-09-20 | `64b105f5a2cc` | 2 | `tests/test_gate_a_v2_independent_audit.py`, `tests/test_gate_a_v2_red.py` |
| `astra/p0-gate-a-v3-independent-audit-2026-09-20` | 2026-09-20 | `33995d03c863` | 1 | `tests/test_astra_gate_a_v3_audit.py` |
| `astra/p0-hybrid-fault-matrix-independent-review-2026-09-21` | 2026-09-21 | `c6be804e99e4` | 14 | `.github/workflows/astra-p0-hybrid-fault-matrix-independent-review.yml`, `audit/astra_p0_hybrid_fault_matrix_independent_probe.py`, `tools/p0_qualification/__init__.py` … |
| `astra/p0-restart-burst-proof-recheck-2026-09-21` | 2026-09-21 | `61facacdcdc4` | 12 | `tools/p0_qualification/__init__.py`, `tools/p0_qualification/common/evidence.py`, `tools/p0_qualification/common/launcher_loader.py` … |
| `blue/forward-finalization-2026-09-20` | 2026-09-20 | `d209348159c4` | 3 | `.github/workflows/forward-live-smoke.yml`, `scripts/forward_capture_runner.py`, `tests/test_forward_capture_runner.py` |
| `blue/p0-audit-authority-fix-2026-09-20` | 2026-09-20 | `a98bc8aef3a3` | 1 | `tests/test_astra_pre_t0.py` |
| `blue/p0-audit-authority-red-2026-09-20` | 2026-09-20 | `ca0f6b00c3e8` | 1 | `tests/test_astra_pre_t0.py` |
| `blue/p0-calendar-direct-reconcile-red-2026-09-20` | 2026-09-20 | `c81fa1cdf93d` | 1 | `tests/test_p0_continuity_compression.py` |
| `blue/p0-continuity-qualification-2026-09-20` | 2026-09-20 | `3dfc54a4219f` | 1 | `tests/test_p0_continuity_compression.py` |
| `blue/p0-gate-a-long-history-2026-09-20` | 2026-09-20 | `d79387f06821` | 1 | `tests/test_p0_continuity_compression.py` |
| `blue/p0-gate-a-v2-staging-2026-09-20` | 2026-09-20 | `fd2e0f3b546f` | 2 | `scripts/quant.py`, `tests/test_astra_pre_t0.py` |
| `blue/p0-manual-operator-provenance-fix-2026-09-20` | 2026-09-20 | `927f496a58fe` | 2 | `scripts/quant.py`, `tests/test_astra_pre_t0.py` |
| `blue/p0-manual-probe-fix-2026-09-20` | 2026-09-20 | `a6924958e88c` | 3 | `scripts/quant.py`, `src/quant/dataplane/sec/collector.py`, `tests/test_astra_pre_t0.py` |
| `blue/p0-manual-probe-red-2026-09-20` | 2026-09-20 | `efbf72484e5e` | 1 | `tests/test_astra_pre_t0.py` |
| `builder/codex-p0-hybrid-fault-matrix-2026-09-21` | 2026-09-20 | `e5c4c720e758` | 12 | `tools/p0_qualification/__init__.py`, `tools/p0_qualification/common/evidence.py`, `tools/p0_qualification/common/launcher_loader.py` … |
| `builder/codex-p0-hybrid-known-bad-replay-2026-09-21` | 2026-09-21 | `565e4eb4c124` | 15 | `tools/p0_qualification/__init__.py`, `tools/p0_qualification/common/evidence.py`, `tools/p0_qualification/common/launcher_loader.py` … |
| `builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21` | 2026-09-21 | `1fa82a754856` | 12 | `tools/p0_qualification/__init__.py`, `tools/p0_qualification/common/evidence.py`, `tools/p0_qualification/common/launcher_loader.py` … |
| `builder/evidence-store-identity-v2` | 2026-09-14 | `b8f7dffbe040` | 15 | `.github/workflows/builder-c-proof.yml`, `schemas/corporate_action_event.schema.json`, `schemas/corporate_action_leg.schema.json` … |
| `builder/forward-market-recorder-v2` | 2026-09-15 | `87bd049574ec` | 14 | `schemas/forward_capture_gap.json`, `schemas/forward_capture_record.json`, `schemas/forward_capture_state.json` … |
| `builder/p0-hybrid-qualification-harness-2026-09-20` | 2026-09-20 | `d4d446c41225` | 10 | `tools/p0_qualification/__init__.py`, `tools/p0_qualification/common/evidence.py`, `tools/p0_qualification/common/launcher_loader.py` … |
| `builder/research-factory-core-v2` | 2026-09-14 | `ca8ffe439953` | 10 | `schemas/experiment_preregistration.json`, `schemas/experiment_registry.json`, `scripts/experiment_factory_proof.py` … |
| `builder/sec-form4-census-v2a` | 2026-09-19 | `08dcfc39b4b2` | 17 | `.github/workflows/sec-form4-census-proof.yml`, `data/calendars/xnys_sessions_2019_2026.csv`, `schemas/sec_form4_candidate_record.schema.json` … |
| `builder/sec-form4-p0-raw-capture` | 2026-09-18 | `348c4e42bf4e` | 15 | `.github/workflows/sec-form4-p0-proof.yml`, `schemas/sec_attempt_record.schema.json`, `schemas/sec_collector_state.schema.json` … |
| `claude/restaurant-stock-management-mvp-6oq43e` | 2026-09-11 | `e083cc70e3f4` | 182 | `.github/workflows/restaurant-stock-tests.yml`, `.gitignore`, `restaurant-stock/alembic.ini` … |
| `codex/test` | 2026-09-12 | `723a778e302b` | 6 | `research/ledger.jsonl`, `results/phase0_e1.json`, `scripts/run_phase0_e1.py` … |
| `parallel/codex-wave1-economic-system-2026-09-19` | 2026-09-20 | `738a5879ef86` | 3 | `src/quant/economics/__init__.py`, `src/quant/economics/engine.py`, `tests/test_economic_engine.py` |
| `recovery/claude-sec-local-20260914` | 2026-09-14 | `ac37339ed31b` | 26 | `.github/workflows/sec-form4-census-proof.yml`, `artifacts/sec_form4_census/acceptance_manifest.json`, `artifacts/sec_form4_census/census_summary.json` … |
| `research/design-v1` | 2026-09-13 | `2da2d1b6786e` | 1 | `research/ledger.jsonl` |

## CONSERVER (30)

- `astra/gate-b-f11-lock-identity-recheck-2026-09-21` (2026-09-21)
- `astra/p0-gate-a-v4-independent-audit-2026-09-20` (2026-09-21)
- `blue/gate-b-activation-seal-host-relay-2026-09-21` (2026-09-21)
- `blue/gate-b-f11-final-integration-2026-09-21` (2026-09-21)
- `blue/gate-b-post-astra-convergence-2026-09-21` (2026-09-21)
- `blue/gate-b-run-reservation-host-relay-preseal-2026-09-21` (2026-09-21)
- `blue/master-v2-2026-09-20` (2026-09-21)
- `blue/p0-gate-a-v4-frozen-2026-09-20` (2026-09-20)
- `builder/gate-b-route1-concrete-mutation-pack-2026-09-21` (2026-09-21)
- `builder/gate-b-v4-materialization-activation-prestage-2026-09-21` (2026-09-21)
- `builder/post-p0-first-vertical-shadow-loop-2026-09-21` (2026-09-21)
- `builder/post-p0-vertical-interface-map-2026-09-21` (2026-09-21)
- `claude/confident-mendel-h4qqo4` (2026-09-21)
- `claude/data-feeds-6vr22g` (2026-09-25)
- `claude/deep-research-project-6vr22g` (2026-09-25)
- `claude/new-session-0ydmkg` (2026-09-27)
- `claude/new-session-3ujgeu` (2026-09-27)
- `claude/new-session-3ujgeu-wip-h006` (2026-09-27)
- `claude/new-session-8msq33` (2026-09-27)
- `claude/new-session-kfwf1b` (2026-09-25)
- `claude/new-session-z4pdlx` (2026-09-25)
- `claude/project-review-audit-q5kfb9` (2026-09-25)
- `claude/prototype-futures-trend-carry-6vr22g` (2026-09-25)
- `claude/two-speed-cleanup-6vr22g` (2026-09-25)
- `operator/gate-b-f5-route1-host-evidence-closure-2026-09-21` (2026-09-21)
- `operator/gate-b-target-host-read-only-rebind-2026-09-21` (2026-09-21)
- `parallel/claude-economic-v2-2026-09-20` (2026-09-20)
- `parallel/claude-first-slice-cohort-geometry-2026-09-21` (2026-09-21)
- `parallel/claude-forward-data-2026-09-20` (2026-09-20)
- `parallel/claude-post-p0-vertical-build-prep-2026-09-21` (2026-09-21)

## Commandes (machine avec git et accès en écriture)

Supprimer la liste SUPPRIMER :

```bash
git fetch origin
for b in \
  astra/first-vertical-independent-review-2026-09-21 \
  astra/gate-b-evidence-schema-false-pass-recheck-2026-09-21 \
  astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21 \
  astra/gate-b-v4-transition-independent-preactivation-review-2026-09-21 \
  astra/p0-deep-adversarial-pre-t0 \
  blue/checkpoint-gate-a-v2-audit-2026-09-20 \
  blue/gate-b-route1-seal-integration-2026-09-21 \
  blue/gate-b-run-authority-repair-dispatch-2026-09-21 \
  blue/gate-b-run-authority-repair-integration-2026-09-21 \
  blue/gate-b-run-reservation-activation-preseal-2026-09-21 \
  blue/integration-readiness-2026-09-20 \
  blue/long-horizon-research-2026-09-20 \
  blue/p0-calendar-dst-proof-2026-09-20 \
  blue/p0-gate-a-v2-final-2026-09-20 \
  blue/p0-gate-a-v3-frozen-2026-09-20 \
  builder/gate-b-deployed-byte-verifier-m4-repair-2026-09-21 \
  builder/gate-b-evidence-reception-prestage-2026-09-21 \
  builder/gate-b-evidence-schema-false-pass-fix-2026-09-21 \
  builder/gate-b-f11-lock-identity-repair-2026-09-21 \
  builder/gate-b-lock-path-identity-repair-2026-09-21 \
  builder/gate-b-offline-lifecycle-sanitization-prestage-2026-09-21 \
  builder/gate-b-run-authority-m1-m3-repair-2026-09-21 \
  builder/gate-b-run-authority-mechanisms-2026-09-21 \
  builder/gate-b-run-authority-retention-prestage-2026-09-21 \
  builder/gate-c-prospective-event-plan-prestage-2026-09-21 \
  builder/p0-effective-unit-digest-stability-v4-2026-09-20 \
  builder/p0-gate-a-v3-2026-09-20 \
  claude/confident-allen-xw7eb6 \
  claude/nasdaq-trading-model-design-h3mp4n \
  operator/gate-b-f5-route1-host-feasibility-2026-09-21 \
  operator/gate-b-read-only-preflight-2026-09-21 \
  parallel/antigravity-gate-b-run-authority-adversarial-precheck-2026-09-21 \
  parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21 \
  parallel/claude-economic-question-falsification-map-2026-09-21 \
  parallel/claude-research-frozen-effect-estimate-prestage-2026-09-21 \
  parallel/claude-s11-dependence-interval-challenge-2026-09-21 \
  parallel/economic-acceleration-2026-09-21 \
  reviewer/v1-final-red-team \
  ; do git push origin --delete "$b"; done
```

Pour une branche DÉCISION, tag puis suppression :

```bash
b=<branche>; git tag -a "archive/$b" "origin/$b" -m "archived before deletion" && git push origin "refs/tags/archive/$b" && git push origin --delete "$b"
```
