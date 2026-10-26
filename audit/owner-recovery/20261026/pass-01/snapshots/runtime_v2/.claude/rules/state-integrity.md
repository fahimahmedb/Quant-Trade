---
paths:
  - "src/quant/book/**/*.py"
  - "src/quant/desk/**/*.py"
  - "src/quant/factory/**/*.py"
  - "src/quant/clock.py"
---

# State and timeline integrity

- Use one causal timeline from observation through decision, simulated operation and state update.
- A result may only include effects that occur after the simulated operation can happen.
- Persistent state changes must be idempotent under crash, restart and replay.
- Preserve per-strategy ownership when several strategies reference the same instrument; aggregate ownership separately for portfolio state.
- Validate limits on the final transformed state that would actually be applied.
- Keep research, simulated execution and Book price bases consistent and document unavoidable mismatches.
- Do not present derived metrics as authoritative while a known timing or accounting invariant is broken.
