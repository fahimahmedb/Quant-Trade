# Étape P10 — Vraie prévision inter-scrutins (downscaling ≠ prévision)

## 0. La question honnête

P9 a montré qu'un Gradient Boosting **répartit** un résultat national déjà connu vers les circonscriptions mieux que le swing (skill de *downscaling*, p ≈ 0). Mais **prédit-il un scrutin futur** ? Test décisif : apprendre la transition **2012→2017**, puis prédire la transition **2017→2022** — jamais vue à l'entraînement. Partis présents aux trois présidentielles : RN, LFI, PS, LR, DLF, LO, NPA (LFI = Mélenchon, explicite).

## 1. Résultat : le swing proportionnel gagne, le ML sur-apprend

Prédiction de la part 2022 par circonscription (n = 3962 paires circo × parti), modèles appris sur 2012→2017 :

| Prédicteur | MAE (points) | Verdict |
|---|---|---|
| Persistance (= 2017) | 4.184 |  |
| Swing additif | 1.701 |  |
| **Swing proportionnel** | 1.050 | 🏆 **champion** |
| Régression linéaire (apprise 2012→2017) | 1.629 |  |
| Gradient Boosting (appris 2012→2017) | 2.408 | sur-apprend |

**Le swing proportionnel (1.05) bat tout le monde**, y compris le Gradient Boosting (2.41, +129 % d'erreur) qui **sur-apprend** la transition d'entraînement. La régression linéaire (1.63) fait à peine mieux que le swing additif mais reste battue par le proportionnel.

## 2. Vérifié avant de conclure (robustesse)

- **Sens inverse** (apprendre 2017→2022, prédire 2012→2017) : même verdict, le GB explose (~7 pts d'erreur). Le sur-apprentissage n'est pas un accident d'un sens de test.
- **Modèle simple** (linéaire) : généralise, le GB non — cohérent avec « la complexité sur-apprend » quand chaque transition électorale est idiosyncratique (Macron 2017, Zemmour 2022…).
- **Baseline forte** : le swing proportionnel n'est pas un homme de paille — c'est lui le champion, pas le modèle.

## 3. Ce que ça signifie (et ça corrige P9)

- **P9 reste vrai mais restreint** : le ML de circonscription est excellent pour **désagréger un résultat connu** (downscaling), PAS pour **prévoir** un scrutin futur. La significativité de P9 ne s'étend pas à la prévision.
- **La leçon (conforme à la littérature)** : en prévision de circonscription, le **vote précédent + swing proportionnel** est une baseline redoutable ; ajouter de la complexité ML dégrade la généralisation. Le levier de significativité n'est donc **pas** un modèle spatial plus riche.
- **Où est vraiment le levier** : la qualité de la **prévision NATIONALE** (fondamentaux + sondages/marchés) — puis un simple swing proportionnel pour descendre aux circos, plus une **incertitude calibrée**. Voir `results/ROADMAP_SIGNIFICATIVITE.md`.

## 4. Limites honnêtes de ce test

- Deux transitions seulement (2012→2017, 2017→2022) : on ne peut pas encore moyenner la skill de prévision sur de nombreux scrutins.
- Lignée des partis imparfaite (Mélenchon 2012 = Front de Gauche incluant le PCF ; Macron absent de 2012 donc hors du jeu tri-scrutins).
- Le test suppose le résultat NATIONAL cible connu (comme le swing) : c'est un test de **désagrégation prédictive**, la brique nationale restant à fournir par ailleurs (P1/P6 ou sondages).
