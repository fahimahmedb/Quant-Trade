# Format des contenus figés (`A2_FROZEN_CONTENT_V1`)

Un contenu figé est un fichier JSON :

```json
{"schema": "A2_FROZEN_CONTENT_V1", "kind": "<InputManifest|OutputManifest|HarnessPolicy>", "fields": {...}}
```

Règles :
- `fields` contient exactement les champs réels de la dataclass H : 17 pour `InputManifest`, 13 pour `OutputManifest`, 12 pour `HarnessPolicy`. Aucun champ en plus ou en moins.
- Un champ enum contient la chaîne `.value` (par exemple `"DOCUMENTATION_ONLY"`, `"RESEARCH_VIEWER"`), jamais le nom Python.
- Un tuple est un tableau JSON. L'ordre du fichier est conservé tel quel ; les deux voies trient elles-mêmes selon la recette H, sans dédupliquer.
- `permitted_recipient_actor_roles` est un tableau de paires `[actor_id, role_value]`.
- `fixture_provenance_contract` vaut `null`. Aucune autre valeur n'est acceptée dans ce mode sans fixture.
- Les chaînes sont reproduites exactement : aucune normalisation d'espaces, de casse ou d'Unicode.

Deux voies calculent l'identité de chaque document :
- `identity_via_harness.py` construit la dataclass H exacte et appelle la fonction d'identité H inchangée ;
- `identity_stdlib.py` reconstruit le payload canonique avec sa propre spécification, sans importer le harnais.

Un écart entre les deux voies, ou un étalonnage manqué, est un STOP pour le calcul concerné et ses bindings dépendants (décision lot 2, L2-E).

Les fichiers réels sous `a2_operation/frozen/` n'existent qu'après les gels ratifiés L2-C, L2-D et L2-F. Le fichier d'étalonnage de ce répertoire ne contient que les valeurs synthétiques `TEST_ONLY` des tests H.
