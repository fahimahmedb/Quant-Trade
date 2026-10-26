# Builder — L2-E identités input et output, et transcription de la policy L2-F

Date : 2026-10-08. Branche : `builder/weather-v4-a2-lot2-tooling-2026-10-07`, base `492bd05f86ed643ecfe32ce4007f90368232be18`. Autorité : décision lot 2 `276fd99` (L2-E, L2-F) ; gels L2-C/L2-D consignés dans `owner/weather-v4-a2-lot2-freezes-2026-10-08` @ `245f193edb158a6cee653f176ae7b93cf2f3ae80`.

## L2-E — résultats

| Manifest gelé | Blob | Voie H | Voie standard | Accord |
|---|---|---|---|---|
| Input | `f85205f33a232de6fabd83c17c52a25d4634e374` | `sha256:5c55b855b91a5c2b0bde86f3c0888905b500c086309a761ff454644d0cfbbd00` | identique | OUI |
| Output (D2) | `7651de7e718a276b596f2256aff0877e771e5d6d` | `sha256:b8157e4e15b4e03813b0ff43d52a2319ea589fc9aab9429f1c2894bcce990976` | identique | OUI |

Méthode : `identity/identity_via_harness.py` (fonctions H `input_manifest_identity` et `output_manifest_identity`, sources H inchangées) et `identity/identity_stdlib.py` (json + hashlib, sans import du harnais). Étalonnage préalable des deux voies sur le vecteur `sha256:54bfcafc…` : concordant (343 tests du lot L2-B, revérifiés). Environnement : CPython 3.13.16, x86_64. Aucun appel `evaluate_*`, aucune root importée ou construite. Ces identités ne sont pas encore liées à une policy ni à une root.

## L2-F — transcription de la policy

`frozen/harness_policy_d2_v1.json` (blob `6a1fa30fac327c0183b2931550bd4c730195529c`) : 12 champs. Les 10 valeurs non dérivées viennent de D §14.2C (dossier `49d3d00`, blob `c3271812…`) ; les deux cellules `DERIVE_…` sont remplacées par les identités ci-dessus. Générateur : `identity/build_policy_from_dossier.py`. `expected_owner_authority_sha` reste C (`37e3b25f17a7c5d3b3bc8d37df730aa988585b6c`). `fixture_provenance_contract` vaut `null`.

Cette transcription n'est pas un gel. L'identité de la policy n'est pas calculée tant que son gel n'est pas consigné.

```text
L2_E_INPUT_OUTPUT_IDENTITIES_COMPUTED = TRUE_BOTH_WAYS_AGREE
POLICY_TRANSCRIBED = TRUE
POLICY_CONTENT_FROZEN = FALSE
POLICY_IDENTITY_COMPUTED = FALSE
EXECUTION_AUTHORITY_E_ISSUED = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
NEXT_SAFE_ACTION = OWNER_ASSISTANT_CONSIGNS_POLICY_FREEZE_THEN_BUILDER_COMPUTES_POLICY_IDENTITY
```
