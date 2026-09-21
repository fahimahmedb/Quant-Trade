# BLUE — CHALLENGE: THREE-TIER PRODUCTIZATION / FIRST FAST ECONOMIC LANE — 2026-09-21

`STATUS = PREPARED / NON_AUTHORIZING`

Nothing in this packet activates a lane, mutates a rail, promotes a branch,
declares t0, or grants any real-capital authority.

## 0. Proposal under challenge

1. Put Quant into production quickly, in shadow/paper only.
2. Do not wait for Form-4 to obtain a first exploitable model; open a second,
   faster research lineage instead of weakening the frozen one.
3. Introduce real capital by bounded steps
   `SHADOW -> PAPER -> LIVE_CANARY -> SMALL_CAPITAL -> SCALE`,
   only for a strategy holding its own independent proof.
4. Accelerate with genuine point-in-time history, keeping a forward confirmation.
5. Never shorten the frozen Form-4 protocol (`K_target=3`, `K_max=4`,
   252 entry sessions per cohort, one-look, pooled post-merge `G>=10`).

## 1. Verdict

`DIRECTION = ACCEPTED`
`AS_STATED = NOT_ACCEPTABLE_WITHOUT_AMENDMENTS`

Points 1, 3, 4 and 5 are consistent with `QUANT_NORTH_STAR.md`. Point 5 in
particular is correct and is hereby restated as binding: lowering `G`, `K_max`,
cohort length or the one-look rule to obtain an earlier answer is forbidden and
is exactly the false-alpha failure mode Quant exists to avoid.

Point 2 is accepted only under the amendments in §3. As written it contains one
real error and three unpriced costs.

## 2. Challenge — what is wrong or unpriced

### C1. The current binding constraint is not Form-4 (blocking)

Quant is not waiting years to become useful. It is waiting on two named,
weeks-scale items:

```text
RAIL A  GATE_B = NOT_STARTED / t0 = NOT_DECLARED
        blocker = ACTIVATION_SEAL_PREP missing concrete Route-1 mutation pack
RAIL B  BUILDER_VERTICAL_SHADOW_LOOP = READY_FOR_INDEPENDENT_REVIEW
```

`governance/BLUE_WORK_ALLOCATION_PRE_GREEN_TO_ECONOMIC_LOOP_2026-09-21.md`
caps active substantial workstreams at `2` before P0 exit. Opening
`FAST_VERTICAL_V1` as live work now makes it a third workstream and competes
for the same reviewer and the same Research/Economic surfaces that Rail B is
about to integrate. The acceleration would be nominal and the contamination
risk to Rail A real.

Amendment: the lane is prepared now, started later, on an explicit gate.

### C2. "Faster observation" is not "faster proof" (substantive)

The proposal equates a higher observation rate with a shorter time to
qualification. That holds only if effect size per observation is preserved.
The lanes named — cross-sectional ETF, index/sector relative value,
momentum/reversion, volatility/regime — are the most crowded, most arbitraged,
lowest-idiosyncratic-edge space available. Expected per-unit effect there is
plausibly an order of magnitude below an insider-signal lane, and required
sample scales with the inverse square of effect size. A lane with 50x the
observations and 1/10th the effect is *slower* to a clean answer, not faster,
and arrives carrying far more selection pressure.

Amendment: a lane is admissible only with its own pre-registered power
derivation showing a minimum economically useful effect is detectable within
its declared horizon, after frictions. Speed must be argued from
`effect / sqrt(variance) * sqrt(independent units per month)`, never from
observation count alone.

### C3. Multiple lanes are a multiplicity problem, not just parallelism (substantive)

The moment lane selection becomes a repeatable factory output, "the first lane
that qualifies" is a maximum over lanes, not a single test. The project already
carries explicit multiplicity and dependence contracts for Route B; spawning
lanes ad hoc would silently discard that discipline.

Amendment: every lane is entered in a lineage registry *before* outcomes, with
its own pre-registration digest, and qualification is evaluated against a
family-wise budget across lanes, not per lane in isolation.

### C4. `LIVE_CANARY` is being asked to prove the wrong thing (framing error)

At canary size no realistic P&L series has power over anything. Treating the
canary as partial alpha evidence would be a state-enum-as-capability claim, and
`CLAUDE.md` forbids exactly that.

Amendment: `LIVE_CANARY` is defined as an *execution-realism instrument*. It
measures fills, rejects, latency, partials, borrow, financing and fees against
the simulator, and it may falsify a strategy on frictions. It may never be
cited as supporting evidence for the strategy's edge.

### C5. Missing pieces the proposal does not mention (gap)

- No demotion path. A ladder with only promotion is a ratchet toward risk.
- No authority artifact. `CLAUDE.md` grants no real-capital authority; every
  step past `PAPER` needs an explicit, dated owner authorization.
- No lane throughput expectation. `+1-3 months: first models falsified` is
  realistic for *falsification*; a qualified positive in that window is not the
  base case. Most lanes must die cheaply, and that must be stated as the
  designed outcome so a dead lane is not read as programme failure.
- Reconstructed point-in-time history is itself a research object and must pass
  the Data Plane provenance/fingerprint rules before any lane may cite it.
  "We found archives" is not a bypass of point-in-time discipline.

## 3. Amended strategy (what this packet prepares)

```text
T1  PRODUCTION-AS-SHADOW
    gate: Gate-B/t0 closed on Rail A AND Rail B vertical integrated
    Quant runs continuously in paper/shadow; real decisions, no capital

T2  PARALLEL LINEAGES
    FORM4_CONFIRMATORY_V1  frozen, untouched, multi-year, background
    FAST_VERTICAL_V1       new lineage, pre-registered, own power derivation
                           admitted only via the lineage registry

T3  EXPOSURE LADDER
    SHADOW -> PAPER -> LIVE_CANARY -> SMALL_CAPITAL -> SCALE
    promotion requires strategy-independent proof + owner authorization
    demotion is automatic and needs no authorization
```

## 4. Deliverables in this packet

- `governance/QUANT_CAPITAL_EXPOSURE_LADDER_V1_2026-09-21.md`
- `governance/RESEARCH_LINEAGE_REGISTRY_2026-09-21.md`
- `governance/FAST_VERTICAL_V1_PREREGISTRATION_TEMPLATE_2026-09-21.md`
- `handoff/BLUE_FIRST_FAST_ECONOMIC_LANE_ROADMAP_2026-09-21.md`

No source code is added. The ladder and the lineage states are deliberately
documents, not enums in `src/`: a state enum is not a capability, and none of
the behaviour behind `LIVE_CANARY` (broker adapter, kill-switch, realized-fill
reconciliation) exists yet. Enumerating it in code now would assert a
capability the system does not have.

## 5. Open decisions for the project owner

1. Confirm the T1 gate: does the fast lane start at t0, or at Rail-B
   integration, whichever is later? (This packet assumes *later of the two*.)
2. Confirm the family-wise budget for concurrent lanes (§3 of the registry
   proposes 3 concurrent, alpha budget split at admission).
3. Confirm that no step past `PAPER` may be taken without a dated authorization
   artifact signed by the owner. (This packet assumes yes.)
