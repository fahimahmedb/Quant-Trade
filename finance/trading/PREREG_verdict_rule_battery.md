# Pré-enregistrement — étendre la règle de verdict aux rapports de batterie

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, prolongeant la série #448 → #449 → #454.

## Le défaut, découvert au #457 en cherchant autre chose

La règle de verdict unifiée lit `**PASS` / `**FAIL` en tête de ligne, décoration
retirée. Elle avait été **taillée sur les rapports de stratégie**.

Les rapports de la batterie Règle 9 énoncent leur verdict autrement :

```
**PAS de PASS RENFORCÉ — au moins un contrôle échoue…**
**PASS RENFORCÉ — tous les contrôles a-e tiennent…**
```

La forme négative commence par `**PAS ` — donc **ni** `**PASS`, **ni** `**FAIL`.
La règle répond « indéterminé » sur **tous** les rapports de batterie du dépôt.
Ni le #448, ni le #449, ni le #454 ne l'avaient vu.

## La modification — une branche, énoncée mot pour mot

Dans `scripts/nonml_verdict.py`, `porte_verdict` reconnaît en plus :

> une ligne dont la forme dénudée **commence par** `**PAS de PASS RENFORCÉ`
> vaut **FAIL**.

La forme positive `**PASS RENFORCÉ` est **déjà** reconnue par la règle existante
(elle commence bien par `**PASS`) : **rien n'est ajouté pour elle**.

**Régime déclaré** : une seule branche insérée dans `porte_verdict`. Toute ligne
touchée ailleurs vaut échec du cycle.

## Le reproche que je m'adresse d'avance

Cette branche est **taillée sur une formulation connue**, comme la couche
« étiquette » du #448 dont la robustesse avait montré qu'elle ne servait qu'à un
cas. Je le dis avant de mesurer plutôt que de le laisser découvrir : **c'est une
règle ajustée à un corpus existant**, pas une théorie générale de l'énoncé d'un
verdict.

La seule défense honnête est qu'elle est **déclarée**, **étroite** et
**vérifiable** — et que l'alternative (laisser 113 rapports « indéterminés »)
est pire.

## Ce que la mesure doit établir

1. Les rapports de batterie cessent d'être « indéterminés » — **cible chiffrée**
   annoncée : les **113** que porte le dépôt.
2. **Aucun rapport de stratégie ne change de verdict.** C'est le risque réel :
   un rapport contenant une ligne commençant par cette formule serait reclassé.
   Tout changement est publié avec la ligne qui le décide.
3. L'effet sur les **7 consommateurs** de la règle est mesuré, sans que leurs
   rapports soient régénérés — la leçon des #449/#450 : ne pas mélanger l'effet
   d'une règle et la dérive du dépôt.

## Critère de succès — chiffré

1. `git diff` **confiné** à la branche annoncée dans `nonml_verdict.py`.
2. **Tout** reclassement publié avec sa ligne décisive.
3. **Zéro** rapport de stratégie reclassé — sinon le cycle échoue et la cause
   est publiée.
4. L'équivalence est vérifiée **sur tout le dépôt**, pas sur un échantillon.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédiction — falsifiable

- **113** rapports de batterie passent d'« indéterminé » à **FAIL**.
- **Zéro** rapport de stratégie change.
- **Aucun** rapport de batterie ne passera à **PASS** : sur les 113, pas un seul
  ne porte la forme positive. **Le dépôt n'a jamais validé un seul PASS
  renforcé** — le #457 l'avait montré sur 29, je m'attends à ce que ce soit vrai
  sur les 113.

## Ce que ce cycle ne fait pas

- Il ne **régénère** aucun rapport.
- Il ne **modifie** pas la batterie ni sa formulation.
- Il ne **change** aucun verdict de stratégie : reclasser un rapport de batterie,
  c'est lire correctement ce qu'il dit déjà, pas décider autre chose.

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL** de ma correction.
2. Aucune ligne hors de la branche annoncée.
3. Le reproche ci-dessus est maintenu dans le rapport final, pas effacé s'il
   s'avère que la branche marche bien.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
