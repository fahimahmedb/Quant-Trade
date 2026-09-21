# SUPERSEDED — DO NOT USE

This branch was created from `blue/master-v2-2026-09-20@68e72392d8ee3db5cd099da43ef6c60a3ad8bd68`.

That tree contains the latest Blue target-host reception authority but does NOT contain
the accepted final F11/run-authority implementation bytes
(`scripts/quant_gate_b_runctl.py`).

Therefore this branch MUST NOT be used for Gate-B run reservation or activation
authority execution.

Use instead:

`blue/gate-b-run-reservation-host-relay-preseal-2026-09-21`

which is rooted in the accepted final F11 Blue integration and references the later
host-rebind reception by exact immutable Git ref.

No Gate-B run was reserved on this superseded branch.
No authority registry was modified.
No activation was sealed or consumed.
No target-host mutation was authorized.
