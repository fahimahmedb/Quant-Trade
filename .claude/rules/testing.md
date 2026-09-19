---
paths:
  - "tests/**/*.py"
  - "scripts/demo_quant_system.py"
---

# Quant testing rules

- Test the failure mode, not only the happy path.
- For persistence changes, include kill/restart/replay cases at the dangerous state boundary.
- For timeline changes, include a fixture where the forbidden interval dominates the apparent result.
- For multi-strategy state, include overlapping and opposing ownership of the same symbol.
- For risk/state transformations, assert limits on the final transformed state.
- For liveness, distinguish healthy running work from genuinely stale work with an injectable clock or deterministic timing fixture.
- Keep synthetic fixtures clearly separated from market evidence and never report fixture performance as research evidence.
