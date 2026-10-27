# PASS B — DISCLOSURE ANCHOR

PASS_B_START_STATE=AUTHORIZED
BLIND_RECONSTRUCTION_SHA=b9b0f351de8cb9838e83222fea87c81a68074934
BLIND_FREEZE_MESSAGE=review: freeze blind Pass A reconstruction
BLIND_PARENT=df513ec327b09277c83d6a153181a8fb989d79c6
BLIND_IMMUTABILITY=review/blind-roadmap/* MUST NOT CHANGE
POST_DISCLOSURE_BRANCH=review/post-disclosure-pass-b-20261027

## Disclosure boundary

Pass A was treated as immutable. Prior Owner/audit/roadmap narratives, the architecture challenger, the one-shot final decision/handoff, follow-up register, current remediation branches and external literature were inspected only after the blind freeze.

Any changed view is recorded as POST_DISCLOSURE_REVISION and never back-written into Pass A.

## Verified historical refs

- W2 engineering candidate: `ebc72b9fd14f91420c37e0b7607f9bfb584a289a` — exists; cumulative W2 closure candidate, not proven Owner-promoted.
- Post-challenge checkpoint: `40c590189e1389502d179e63f6e0925df8513d2c` — exists; resume anchor/evidence checkpoint.
- One-shot branch: `codex/verified-autonomous-continuity-oneshot-20261027`.
- One-shot branch head: `d19b1237636d2311cd42f97f0b02feb55168347b`.
- One-shot prequalification tested candidate: `0b6cc21a8aead178549966789b1e063dcfab8245`.
- Architecture challenger requested historical ref: `642b551985f499b37286c3bc21b89c57294f63ca` — exists.

## Direct ancestry correction

POST_DISCLOSURE_REVISION

OLD_BLIND_CONCLUSION: Pass A `REF_VECTOR.json` recorded `d19b123... -> a8339a02... -> df513ec...` as ancestry.

NEW_CONCLUSION: Direct Git commit evidence shows `d19b1237636d2311cd42f97f0b02feb55168347b` has parent `0b6cc21a8aead178549966789b1e063dcfab8245`. The one-shot identity chain must therefore use `0b6cc21...` as the tested/prequalification candidate and must not infer qualification of `d19b123...` from tests on its parent.

NEW_EVIDENCE: GitHub commit object for `d19b123...`; one-shot final attestation and handoff.

WHY_THE_NEW_EVIDENCE_CHANGES_THE_RESULT: Qualification is SHA-specific. A wrong ancestry vector could collapse candidate and attestation identities and create a false promotion/qualification claim.

## Post-freeze remediation refs

These did not exist in the blind evidence set and are therefore post-disclosure evidence only:

- `codex/c0-confirmation-repair-20261027`: count repair proven targeted; `df513ec...` exact candidate remained globally non-pass because of a separate direct-reference outcome membrane invariant.
- `codex/c0-membrane-qualification-20261027`: candidate `c028bc866d8dbca56028b4b859b00d34bfb7dbe1` local+hosted PASS; final attestation head `13721384fe5b94b0136fb4548192e05d5e34e605` has exact hosted PASS in run `40437918834`. This is scoped C0 membrane engineering evidence only.

No post-freeze C0 pass is treated as proof of scientific-review authenticity, full autonomous E2 continuity, Owner promotion, deployment, economic validation or capital readiness.

## Evidence-order law

1. Repository facts first.
2. Blind-vs-prior comparison second.
3. External research properties third.
4. Program recommendation last.

External literature is not used to infer repository state.
