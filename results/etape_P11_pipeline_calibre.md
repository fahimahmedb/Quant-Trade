# Étape P11 — Pipeline de prévision calibré (national → circonscriptions → sièges)

## 0. Synthèse du projet en un pipeline honnête

Les étapes précédentes ont établi, par la mesure : le levier est **national** (pas spatial, P10) ; la désagrégation gagnante est le **swing proportionnel** ; et l'incertitude doit être **calibrée puis vérifiée** (P9/P10). Ce pipeline assemble ces trois briques honnêtes.

```
prévision NATIONALE (incertaine)  ──►  swing proportionnel sur carte réelle 2022
        │                                          │
   (maillon faible, le vrai levier)      intervalles CONFORMES par parti
        └──────────────► Monte-Carlo ──► sièges (têtes/circo) + IC
```

## 1. Incertitude calibrée : on la VÉRIFIE, on ne la suppose pas

Intervalles conformes calibrés sur la transition 2012→2017, **couverture mesurée** sur 2017→2022 (cible 80 %) :

| Parti | Demi-largeur Q | Couverture obtenue |
|---|---|---|
| Le Pen (RN) | ±2.69 pts | 78% |
| Mélenchon (LFI) | ±2.63 pts | 40% ⚠️ |
| Hidalgo (PS) | ±1.48 pts | 99% ⚠️ |
| Pécresse (LR) | ±2.23 pts | 98% ⚠️ |
| Dupont-Aignan (DLF) | ±0.74 pts | 94% ⚠️ |
| Arthaud (LO) | ±0.10 pts | 85% |
| Poutou (NPA) | ±0.19 pts | 92% ⚠️ |

Couverture moyenne **84%** (cible 80%) — correcte en moyenne, **mais très inégale** : **LFI est gravement sous-couvert (40%)** car la poussée Mélenchon 2017→2022 fut bien plus volatile que 2012→2017. La garantie conforme suppose l'échangeabilité entre scrutins — **violée** ici. Honnêtement : avec 2 transitions seulement, l'incertitude n'est pas fiablement calibrable pour un parti en mutation. Le correctif n'est pas algorithmique — il faut **plus de scrutins**.

## 2. Projection de sièges avec incertitude (démonstration)

Scénario national **illustratif** (PAS une prévision) passé dans le pipeline complet, avec une incertitude nationale de ±10 % (relatif) propagée par Monte-Carlo (2000 tirages) :

| Parti | En tête (médiane) | IC 80 % |
|---|---|---|
| Le Pen (RN) | 358 circos | [308 – 398] |
| Mélenchon (LFI) | 156 circos | [118 – 204] |
| Macron (Ensemble) | 55 circos | [26 – 93] |
| Pécresse (LR) | 4 circos | [1 – 11] |

*Entrée nationale : RN 30%, LFI 25%, ENS 20%, LR 12%, REC 6%, EELV 4%, PS 3%. La largeur des intervalles vient d'abord de l'incertitude NATIONALE (le maillon faible), pas du spatial — ce qui illustre exactement où se joue la significativité prédictive.*

## 3. Conclusion honnête du projet

Le pipeline est **complet et cohérent** : chaque brique est celle que la mesure a validée (swing proportionnel > ML pour la prévision ; incertitude vérifiée, pas supposée ; national comme vrai levier). Ce qu'il **reste** n'est pas un défaut de modélisation mais une **limite de données** :
- **Calibration inégale** (LFI) → il faut plus de transitions électorales.
- **Prévision nationale faible** (fondamentaux non significatifs à n=11) → il faut un vrai signal national (sondages/marchés live), branchable ici tel quel.
- **Downscaling ≠ prévision** : la carte spatiale est fiable pour répartir un national connu ; elle n'invente pas le national.

En l'état, c'est la réponse la plus significative **possible** sur ces données : significative là où elle peut l'être (downscaling, p≈0), honnête sur ses limites (prévision, calibration), et **prête à s'améliorer par les données** (plus de scrutins, signal national live) plutôt que par plus de complexité.
