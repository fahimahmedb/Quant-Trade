# Pré-enregistrement — les littéraux périmés restants dans le script du #485

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de RÉPARATION**, première piste de la file
ouverte au #520 (« le littéral périmé « chacun des 12 » »).

## Ce que le #520 a signalé sans corriger

Le #520 a réparé les **5 verdicts** périmés du dictionnaire `V`, mais a
délibérément laissé de côté un littéral en dur trouvé en cours de route
(« chacun des 12 », hors du périmètre déclaré de ce cycle-là). Ce cycle
reprend cette dette, et **l'étend par un balayage mécanique déclaré
d'avance** plutôt que de ne corriger que le seul cas déjà nommé.

## Le balayage — mécanique, avant toute lecture

`grep -noE` sur les mots-nombres français (`un` à `dix-sept`) dans
`nonml_irreparable_figures_census_backtest.py`, puis **lecture manuelle
de chaque occurrence** pour distinguer :
- un **article indéfini** (« un cas », « une réserve ») — pas un compte ;
- un **compte figé intentionnellement** (ex. seuils de prédiction
  `≥ 5 irréparables`, annoncés au #485 et jamais censés bouger) — pas un
  bug ;
- un **compte qui décrit l'état actuel du dépôt** et qui ne suit plus la
  valeur réelle depuis que le #493/#511/#518 ont changé la partition —
  **c'est la population de ce cycle.**

## La population trouvée — 3 littéraux, nommés avant correction

| Ligne | Texte actuel | Défaut |
|---|---|---|
| 247 | « actionnable **aux deux tiers** » | qualitatif, calculé sur 12/17 (70,6 %) ; la partition réelle est désormais 9/17 (52,9 %) |
| 284 | « une des **cinq** renvoie à une question en attente d'arbitrage » | comptait les 5 irréparables d'origine ; il y en a **8** aujourd'hui |
| 288 | « chacun des **12** demande sa propre vérification » | comptait les 12 réparables d'origine ; il y en a **9** aujourd'hui |

Les seuils de prédiction (`≥ 5 irréparables`, `≥ 8 réparables`) **ne
sont pas dans cette population** : ce sont les annonces originales du
#485, figées par construction — les changer serait un retuning rétroactif
de sa propre prédiction, explicitement interdit.

## Le geste

1. **Ligne 247** : remplacer la fraction qualitative fixe par une
   description qui **se recalcule** depuis `len(rep)`/`len(pop)` — pas
   un nouveau mot choisi à la main qui pourrait se périmer pareil.
2. **Ligne 284** : remplacer « cinq » par `{len(irrep)}` interpolé.
3. **Ligne 288** : remplacer « 12 » par `{len(rep)}` interpolé.
4. **Rien d'autre** — même discipline que le #520 : diff borné aux 3
   lignes déclarées.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **3** littéraux trouvés par le balayage mécanique, publiés avec
   leur ligne et leur défaut, **avant** toute correction.
2. Les **3** corrigés par interpolation, **aucun nouveau littéral
   introduit** à leur place.
3. Rapport régénéré : **aucune ligne changée hors celles dépendant des
   3 corrections** (diff mesuré).
4. Le compte final (8 irréparables / 9 réparables) **inchangé** par ce
   cycle — il ne fait que corriger la *description*, pas la mesure.
5. Aucun script de marché exécuté.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Le balayage mécanique trouve **exactement 3** littéraux périmés
   (ni plus, ni moins) une fois les articles et les seuils de
   prédiction exclus.
2. Le nouveau texte de la ligne 247 publie un pourcentage **inférieur à
   60 %** (puisque 9/17 ≈ 52,9 % < 66,7 %).
3. Aucune des lignes de prédiction (seuils `≥ 5`/`≥ 8`) n'est modifiée.

## Ce que ce cycle ne fait pas

- Il ne **rejuge** aucun verdict de `V` — ceux-là sont réparés depuis le
  #520.
- Il ne **change** aucun seuil de prédiction annoncé au #485.
- Il n'**exécute** aucun script de marché.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de réparation de dépôt, aucune position, aucun
paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si le balayage trouve plus ou
   moins de 3 cas.
2. Population et protocole **inchangés** après mesure.
3. **Chaque correction adossée à la ligne de code et au calcul qui la
   remplace.**
4. **Relecture intégrale du rapport régénéré avant commit** (engagement
   #414).
