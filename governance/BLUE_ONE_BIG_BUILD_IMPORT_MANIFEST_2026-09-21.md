# BLUE — ONE BIG BUILD SELECTIVE IMPORT MANIFEST — 2026-09-21

## 0. Authority

This manifest is the exact pre-build composition authority for the first vertical
Product Builder.

Whole Forward/Economic branch merges are forbidden.

Canonical sources:

```text
FORWARD = 83521dbfdd90027c90d04adfb7d814593c2355c5
ECONOMIC = 35dff27b8fac53618da434ee6d31febbddcc0e69
```

Current Blue/Product spine already descends from:

`cbf30c1bb38dd69c11fb64c523c3aec694116b9c`

## 1. Already present byte-identically on Blue — do not recopy

```text
src/quant/dataplane/__init__.py
  b13000174f88b5450858a9653d555d89d7963bd7
src/quant/dataplane/panel.py
  51fc7b847c708e027fbff8791e40c7f62fa4fa01
src/quant/dataplane/registry.py
  8dd88540191c822c0ada640e5144d76cbdf6dd1b
```

These blobs match Forward exactly at the pinned SHA.

## 2. Forward/dataplane files to import byte-identically

```text
src/quant/dataplane/admissibility.py
  45549a88e5b4d767bb1180b0e2745cbd12704ac4
src/quant/dataplane/form4_parse.py
  cf1f2602bcb2bf6acc774b9155972592217c51ff
src/quant/dataplane/forward_admissibility.py
  6864587ff0ace4851df2dd607f24b000a6bbb73d
src/quant/dataplane/forward_recorder.py
  771d1f403ca87db02208a39e8280cdd6abf9d0ad
```

## 3. Forward/science package to import byte-identically

Copy the complete current science package so its `__init__.py` import surface remains
closed and internally consistent:

```text
src/quant/science/__init__.py
  d284a3fcca22bb5fbf8f5bfec86a7bcd14c01f75
src/quant/science/eligibility.py
  8ec18b8800c12f638c71e2025fa3d5885a5d796e
src/quant/science/formation.py
  11c5d82214537a22b5ec0f23e9231926daf74a44
src/quant/science/inference.py
  0092bf359e35022bc61cc4883692193096313c72
src/quant/science/invariance.py
  1587df07a8e24613267cdb1878938477775fa5a9
src/quant/science/nulls.py
  b8c105750e4d71ef7086e15baf6a18b93dc237bd
src/quant/science/regimes.py
  7313e1b56b9c7f1a63144bdb821edc22f1112867
```

The future new `src/quant/science/effect.py` is NOT copied from Forward; it is an
ADAPT/new implementation path governed by the frozen build specification.

## 4. Economic package to import byte-identically

Copy the complete pinned Economic package:

```text
src/quant/economics/__init__.py ce981f4dbdea3b08b72ef194c38738958429c309
src/quant/economics/capacity.py 36b9e765247b0f2daef8406e48c3b82ff2fdeab9
src/quant/economics/consistency.py eb31c991b9d1041da069b5199ee598453d5793b7
src/quant/economics/coordinate.py 1dd7fc83cd6874df409c0b5a13cea7ca87810420
src/quant/economics/decision.py 68b81c2c23a9f08251159e52457e4a4f49822e46
src/quant/economics/fingerprint.py 1458e0fb75a67f103bc5c179c2eb390d1c2ee24a
src/quant/economics/frictions.py 29c80c456b3d696093188886e56da53b14950b61
src/quant/economics/journal.py d1584d32df4f25f35e061cc0472a7817e9860c22
src/quant/economics/margin.py 4262d2e3ed9b7ab4bea57ad8a0b02d732c2188d8
src/quant/economics/opening.py 380cfb767939bcde2acee99217ceeb57aee5bea7
src/quant/economics/parameters.py 9f2cf1b63f2407075cf403504b7adaa067155df2
src/quant/economics/partition.py dd95fc20d077f44e8dd5f572b3fbe27b7ee35e71
src/quant/economics/recipe.py 27d8f8d38d550cfed5329cdd7fce99c76e83c109
src/quant/economics/scenarios.py 0a4d2ebaa81fe3a7e87ab942fa2924838b9dcda4
src/quant/economics/sizing.py edfacc26d3c7e56bbee0028a407ffaf67be2cf74
src/quant/economics/states.py 19b9ef953b9b6f5c378c49e047292eb93dd29e7c
src/quant/economics/theta.py c0012ae9178a62a6cb443995974cf6e65f0c6b4b
src/quant/economics/timeline.py eaa540e84dc02295d4256fefebfb43a415451307
src/quant/economics/value.py 8c60fa311fb0d193575e320e46d51af76b22b28d
```

## 5. Import discipline

Before the first semantic Product edit, the Builder must:

1. materialize these exact files from the pinned source SHAs;
2. verify every copied blob equals this manifest;
3. run import/collection smoke tests;
4. record the imported-file/source/blob map in its handoff.

A REUSE_AS_IS file that needs modification must be reclassified explicitly as ADAPT
in the Builder handoff before edit; do not silently modify a copied authority.

Do not import:
- alternate Book/ledger implementations;
- alternate schedulers/control planes;
- whole Forward/Economic histories;
- unrelated SEC network/runtime machinery merely because it exists on the source branch.

## 6. Status

```text
SELECTIVE_IMPORT_MANIFEST = FROZEN
WHOLE_BRANCH_MERGE = FORBIDDEN
```
