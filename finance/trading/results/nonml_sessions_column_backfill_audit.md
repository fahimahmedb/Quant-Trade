# Audit — colonne « Séances test. » ajoutée aux 3 rapports non vérifiables (pré-enregistré)

Cycle d'**outillage documentaire**, sous le régime déclaratif du #429. Aucune
stratégie évaluée, aucun verdict recalculé, aucun paramètre touché.

Comble la lacune chiffrée au #427 : son contrôle de cohérence atteignait **13/16**,
les 3 restants ne publiant ni séances ni taux d'activation. La colonne n'invente
aucune valeur — elle **publie une grandeur que le script calculait déjà** et que
cinq rapports frères affichent depuis toujours.

## Contrôle 1 — structurel : colonne retirée ⇒ rapport identique à l'avant

Ajouter une colonne réécrit **toutes** les lignes du tableau : en-tête,
séparateur, une ligne par marché. Un contrôle « N suppressions » ne dirait rien.
Le garde-fou est donc structurel — la seule différence admise est l'insertion
d'une cellule par ligne.

| Rapport | Colonne retirée = version d'avant | |
|---|---|---|
| `halloween_effect` | identique | ✔ |
| `intraday_range_regime_overlay` | identique | ✔ |
| `tom_overlay` | identique | ✔ |

**3/3.** Aucune autre valeur n'a bougé : ni Sharpe, ni
rendement, ni MDD, ni verdict, ni aucune ligne hors tableau.

## Contrôle 2 — la colonne NDX doit égaler le `.npz`

Écart toléré, fixé avant calcul : **0**. C'est le contrôle qui donne son sens au
cycle : sans lui, la colonne serait un ornement.

| Rapport | Colonne NDX | Séances au `.npz` | Écart | |
|---|---|---|---|---|
| `halloween_effect` | 10272 | 10272 | 0 | ✔ |
| `intraday_range_regime_overlay` | 10020 | 10020 | 0 | ✔ |
| `tom_overlay` | 10272 | 10272 | 0 | ✔ |

**3/3 à écart nul.** Le `.npz` de chacun est désormais
confrontable à un chiffre publié par son propre script.

Le cas `intraday_range_regime_overlay` valide le choix fait au
pré-enregistrement : ce script évalue une fenêtre **tronquée**, et la colonne
annonce `len(pnl_bh)`, la série évaluée. Publier `len(bh_full)` y aurait affiché
un nombre que rien ne vérifie — l'écart aurait été de 252 séances.

## Contrôle 3 — verdicts inchangés

| Rapport | Avant | Après | |
|---|---|---|---|
| `halloween_effect` | PASS | PASS | ✔ |
| `intraday_range_regime_overlay` | PASS | PASS | ✔ |
| `tom_overlay` | PASS | PASS | ✔ |

**3/3.** Ce cycle ne pouvait pas changer un verdict et ne l'a
pas fait ; le contrôle le vérifie plutôt que de le supposer.

## Contrôle 4 — non-débordement : aucun autre rapport touché

Vérifié par `git status`, et non affirmé : l'ensemble des rapports modifiés dans
l'arbre de travail doit être **exactement** les 3 cibles.

- rapports modifiés : **3** — `halloween_effect`, `intraday_range_regime_overlay`, `tom_overlay`
- attendus : **3**

**Aucun débordement.**

## Effet mesuré — le contrôle de cohérence du #427

Recalculé ici sur les **16** candidats du lot 5, en appliquant la règle du #427 :
le `.npz` doit reproduire un chiffre publié par le rapport (nombre de séances, ou
taux d'activation de la ligne NDX).

| | #427 | #430 |
|---|---|---|
| candidats vérifiés | 13 / 16 | **16 / 16** |

**Plus aucun candidat du lot 5 n'échappe au contrôle de cohérence.** La lacune
ouverte au #427 est fermée, et par une mesure, pas par un renoncement.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| rapports dotés de la colonne | 3/3 | 3/3 | ✔ |
| contrôle structurel | 3/3 | 3/3 | ✔ |
| cohérence colonne ↔ `.npz` | 3/3 écart nul | 3/3 | ✔ |
| non-débordement | 3 rapports | aucun | ✔ |
| contrôle du #427 | 16/16 | 16/16 | ✔ |

**Prédiction déductive vérifiée sur les cinq critères.** Quatre régimes de
modification auront été déclarés puis tenus sans élargissement : **0 différence**
(#416 → #427), **insertions seulement** (#428), **remplacement d'une ligne**
(#429), **ajout d'une colonne sous contrôle structurel** (#430).

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
