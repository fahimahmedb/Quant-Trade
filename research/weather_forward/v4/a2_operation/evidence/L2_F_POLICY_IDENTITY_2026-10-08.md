# Builder — L2-F identité de la policy (route D2)

Date : 2026-10-08. Branche : `builder/weather-v4-a2-lot2-tooling-2026-10-07`. Autorité : décision lot 2 `276fd99` (L2-F) ; gel de la policy consigné dans `owner/weather-v4-a2-lot2-freezes-2026-10-08` @ `79f6e9290121869cece6d23a259249883b32941a` (acte blob `5083bcf9a348f5dc0422e6a8610fef7ff26a7038`).

| Policy gelée | Blob | Voie H | Voie standard | Accord |
|---|---|---|---|---|
| `a2_operation/frozen/harness_policy_d2_v1.json` | `6a1fa30fac327c0183b2931550bd4c730195529c` | `sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60` | identique | OUI |

Méthode et environnement identiques à L2-E (CPython 3.13.16, x86_64) ; fonction H `harness_policy_identity` ; aucun `evaluate_*`, aucune root.

Chaîne des identités de la configuration D2 :

| Objet | Identité |
|---|---|
| Input | `sha256:5c55b855b91a5c2b0bde86f3c0888905b500c086309a761ff454644d0cfbbd00` |
| Output | `sha256:b8157e4e15b4e03813b0ff43d52a2319ea589fc9aab9429f1c2894bcce990976` |
| Policy (`expected_policy_identity` de la future root) | `sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60` |

Toute modification d'un des trois fichiers gelés invalide cette chaîne.

```text
L2_E_L2_F_ALL_THREE_IDENTITIES_COMPUTED = TRUE_BOTH_WAYS_AGREE
EXECUTION_AUTHORITY_E_ISSUED = FALSE
TRUSTED_ROOT_CANDIDATE_CONSTRUCTED = FALSE
TRUSTED_ROOT_ACTIVATION_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
NEXT_SAFE_ACTION = L2_G_OWNER_FINAL_CONFIGURATION_AND_EXECUTION_AUTHORITY_E
```
