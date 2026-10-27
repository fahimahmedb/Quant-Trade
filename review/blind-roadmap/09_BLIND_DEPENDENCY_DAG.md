# BLIND DEPENDENCY DAG

Legend: HP=HARD_PREREQUISITE, SP=SCIENTIFIC_PREREQUISITE, AP=AUTONOMY_PREREQUISITE, PP=PROMOTION_PREREQUISITE, SAF=SAFETY_PREREQUISITE, OPT=OPTIONAL, PAR=PARALLELIZABLE, UNK=UNKNOWN.

## Nodes

- N0 Exact identity + explicit authority/contract
- N1 Qualified documentary/source binding
- N2 Frozen proposal/candidate/hypothesis identity
- N3 Valid named quant observations with PIT provenance
- N4 Frozen experiment protocol + cost assumptions
- N5 Deterministic execution harness
- N6 Evaluator
- N7 Independent scientific adjudication
- N8 Denominator/trial accounting
- N9 Scientific Memory append
- N10 Proposal Ledger / discovery / Candidate handoff
- N11 Task materialization
- N12 Control Plane validation
- N13 Oracle claim/lease/retry
- N14 Runner/executor
- N15 Canonical evaluator/sink binding
- N16 Replenishment/continuation
- N17 Economic Identity
- N18 Portfolio Readiness/lifecycle
- N19 Exact local qualification
- N20 Exact hosted qualification
- N21 Formal promotion
- N22 Installed release identity
- N23 Active runtime observation

## Edges

N0 -> N2 [HP,SP,AP,SAF]
N0 -> N19 [PP]
N1 -> N2 [SP,AP; experiment/source dependent]
N2 -> N4 [SP,AP]
N3 -> N5 [SP]
N4 -> N5 [SP]
N5 -> N6 [SP]
N6 -> N7 [SP,SAF]
N8 -> N7 [SP,SAF]
N7 -> N9 [SP]
N2 -> N10 [AP]
N10 -> N11 [AP]
N12 -> N11 [AP,SAF]
N11 -> N13 [AP]
N13 -> N14 [AP]
N14 -> N15 [AP]
N15 -> N7 [AP,SAF]
N9 -> N16 [AP]
N7 -> N17 [OPT for first scientific validity; HP for economic-readiness claim]
N17 -> N18 [HP for portfolio/lifecycle claim]
N19 -> N20 [PP]
N20 -> N21 [PP]
N21 -> N22 [PP]
N22 -> N23 [PP]

## Parallelism

- N3 source/capture readiness, N10-N15 synthetic autonomy-continuity proof, and N19-N20 code-state qualification can be pursued in parallel because they establish different claims.
- N17-N18 need not block first scientific validity and should not be serialized before N7 unless the milestone explicitly demands economic readiness.
- Runtime install observation N22-N23 is downstream of formal promotion for a production claim but can be inventoried independently as NO_CODE_EVIDENCE.
- Documentary-source hardening is parallel to quant-data acquisition unless the selected named experiment consumes that documentary source.

## Current blocked edges

- N3 -> N5 is blocked for the selected BitMEX witness by invalid BBO capture.
- N10 -> N11 -> N13 -> N14 -> N15 -> N7 is not proven as one identity-conserving canonical path.
- N20 -> N21 is blocked for df513ec because exact hosted qualification failed.
- N21 -> N22 -> N23 is UNKNOWN because no formal promoted SHA/installed identity was recovered.

Do not infer serialization between these blocks. A failed promotion gate does not prevent an isolated lawful scientific harness; an invalid real-data capture does not prevent synthetic autonomy qualification; an autonomy gap does not invalidate an already fair deterministic scientific test.
