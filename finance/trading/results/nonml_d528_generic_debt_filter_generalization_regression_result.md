# Régression dédiée — #531, avant/après sur l'occurrence exacte du #530

Occurrence ciblée : radical `battery_backfill_lot`, section #528, marqueur « rétracté ».

- occurrence trouvée (radical à moins de 400 caractères du marqueur) : **OUI**
- distance mesurée : **146** (le #530 rapportait 151)
- fenêtre examinée (±60/+40 autour du marqueur) : « que de la « Dette restante » listant > des numéros de cycle rétractés — pas une discussion du script »

| Filtre | Motifs testés | Exclusion |
|---|---|---|
| **Avant** (#528/#529 d'origine) | ('rétractés sur mesure',) | **NON exclu (faille du #530)** |
| **Après** (réparé au #531) | ('rétractés sur mesure', 'pas une discussion du script') | **exclu (réparé)** |

## Prédiction confrontée

- avant : non exclu (comme prévu) : **vérifiée**
- après : exclu (comme prévu) : **vérifiée**

**PASS** — la réparation du #531 comble bien la faille précise trouvée au #530, sans autre effet mesuré ici (les 4 sorties de production restent inchangées, vérifié séparément).
