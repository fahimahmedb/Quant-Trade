# Q17-A — triage du rapport Astra lot 3 (grille Q14), 2026-10-08

```text
DOCUMENT_STATUS = TRIAGE_ARBITRATED_BY_CODEX
REPORT = research/weather_forward/v4/audit/ASTRA_V4_A2_LOT3_INDEPENDENT_REVIEW_2026-10-08.md
REPORT_COMMIT = f236ab2b…  (branche astra/weather-v4-a2-lot3-independent-review-2026-10-08, parent unique 73280c3e9d8604b2f2d8e6d2d174aa940389a760, un seul fichier ajouté)
REPORT_BLOB = 0e58db37d8bce2bc60ff1cee41b777adce780252
ASTRA_VERDICT = BLOCKED_INCOMPLETE_EVIDENCE ; CANDIDATE_ROOT_BLOCKING_DEFECT_FOUND = NONE
RECOMMENDATION_Q14_F = BLOCKED_PENDING_EXACT_EVIDENCE
```

Porte d'entrée (Q14 A) : rapport, commit, blob et ancestry résolus ; session neuve (Opus, sans accès au dossier `team/`), reproductions hors dépôt, 3.13.16 et 3.12.3. Non encore recalculé par Builder : les sorties de reproduction d'Astra (voir « Réserves » ci-dessous).

| Constat | Classe Q14 | Propriétaire | Fermeture exigée | Nouvelle revue |
|---|---|---|---|---|
| J-1 contexte d'opération final et épingles finales (blob candidat `9704a844…`) absents | T1 | Builder (Q23) | contexte D2 publié avec blobs, valeurs exactes de E B.3/B.4, test statique d'égalité à E, **sans lancement** | delta |
| J-2 constats L2-A absents | T1 | Owner (Q11-O), kit Q15 | constats expurgés publiés, avec Python et architecture hôte | delta |
| J-4 Python et architecture de l'hôte inconnus | T2 | Owner (avec J-2) | version/architecture dans les constats L2-A ; rejouer le runner L2-I si ≠ 3.12/3.13 | non |
| J-5 provenance de `1910994` et attribution des gels/E à des sessions agents (E : « Je ratifie le projet e », sans commit cité) | T2 | **Owner** (attestation de fait, non délégable) | reconnaissance explicite d'Owner au titre de E B.5(e) | non |
| J-6 anciens runners non relancés par L2-I | T3 | — | comblé par la reproduction d'Astra | non |
| J-7 `build_result` ne contrôle pas lui-même le domaine fermé de `structural_linkage_status` | T3 | — | aucun changement : aucun faux résultat permissif n'est démontré ; **tout changement de blob ⇒ nouvelle revue** | non, puisque non modifié |
| J-8 sémantique de `quarantine_state = CLEAR` à préciser | T3 | pilote du lot 4 | préciser dans la décision lot 4 | non |
| J-9 identité du dossier L2-J renvoyée à un commentaire de PR | T4 | Builder | inscrire le commit du dossier dans un objet Git ultérieur (le présent triage, `339d2d0`+) | non |
| J-3 candidat conforme à L2-H | information | — | aucune | — |

## Arbitrage Codex

Les classes Q14 de J-1 à J-9 sont confirmées sans reclassement. La recommandation reste `BLOCKED_PENDING_EXACT_EVIDENCE` et ne transforme pas le verdict Astra en PASS.

Voie unique choisie (Q14 F) : **fournir les preuves manquantes sans substitution**, puis revue Astra limitée au delta. Pas de correction du candidat.

J-5 est `T2` et non délégable : seule Owner peut reconnaître la provenance et l'attribution de ses propres autorisations au titre de E B.5(e). Une attestation d'agent constituerait une substitution de preuve.

`build_result` reste inchangé pour J-7 : aucun faux résultat permissif n'est démontré et modifier le blob déjà revu imposerait une nouvelle revue sans fermeture nécessaire du blocage actuel.

Chemin critique : J-1 (Builder, Q23), puis J-2 et J-5 (Owner), puis revue Astra limitée au delta. Aucune activation, qualification VM, autorité économique ou décision d'Owner n'est créée par cet arbitrage.

Réserves du triage : (1) les 27 tests adversariaux et les 56 évaluations d'Astra n'ont pas été rejoués par Builder (coût, et la reproduction indépendante est justement la valeur du rapport) ; (2) la décision de ne pas modifier `build_result` (J-7) évite d'invalider la revue ; (3) rien dans ce triage ne vaut `PASS`, activation, qualification de VM ou décision d'Owner.
