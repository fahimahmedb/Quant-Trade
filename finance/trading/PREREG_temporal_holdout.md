# Pré-enregistrement — un hors-échantillon temporel sur les PASS

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.
**Piste C**, dernière des trois proposées au #455.

## Ce que ce test est — et ce qu'il n'est pas

Les PASS du dépôt ont été établis sur **l'historique complet disponible**. Aucun
n'a jamais été jugé sur une tranche que son auteur n'avait pas vue.

Ce cycle découpe chaque série de P&L sauvegardée en **avant / après**, et compare
le Sharpe des deux moitiés.

> **Ce n'est pas un vrai hors-échantillon**, et il faut le dire d'emblée. Les
> règles sont déterministes — rien n'a été « appris » sur la période — mais
> **elles ont été choisies en connaissant tout l'échantillon**. La tranche
> finale est donc contaminée par la **sélection**, pas par l'estimation.
>
> C'est le meilleur test disponible sans données nouvelles, et il est **plus
> faible** qu'un vrai OOS. Le présenter autrement serait malhonnête.

## Ce qu'il peut néanmoins établir

Si un edge réel existe, il devrait **persister** sur la tranche récente. S'il
s'évapore, deux lectures restent possibles — surapprentissage de sélection, ou
disparition réelle de l'anomalie — et ce cycle **ne les départagera pas**.

En revanche, un effondrement massif serait cohérent avec le **0/29** du #457 et
en constituerait une confirmation indépendante.

## L'univers et les découpes — figés ici

- **Univers** : candidats dont le rapport porte un **PASS** (règle unifiée) et
  qui possèdent un `.npz` reconstructible — **100** au #457.
- **Découpe principale** : les **252 dernières séances** (≈ 1 an de bourse).
- **Découpe secondaire** : les **504 dernières** (≈ 2 ans), déclarée d'avance
  pour que la principale ne puisse pas être choisie après coup.
- **Exclusion** : toute série de moins de **756 séances** (3 × 252), pour que la
  tranche retenue ne dépasse pas le tiers de l'échantillon. Les exclues sont
  **listées**, pas écartées en silence.

**Métriques**, sur chaque moitié : Sharpe annualisé, et le **signe** du Sharpe
hors-échantillon.

## Critère de succès — chiffré, et il porte sur le procédé

1. **100 %** des PASS sont traités, ou listés comme exclus **avec leur raison**.
2. Les deux découpes sont publiées, **pas seulement la plus favorable**.
3. Sont publiés : la **médiane** du Sharpe avant / après, la **fraction** à
   Sharpe hors-échantillon positif, et la **fraction** qui bat son propre
   Sharpe d'avant.
4. Aucun verdict de stratégie réécrit.

> **PASS** = les quatre points. **FAIL** = un seul manque.

**Le verdict du cycle ne dépend d'aucun chiffre de marché.** Un effondrement
général est un résultat aussi publiable qu'une persistance.

## Prédiction — falsifiable et chiffrée

- **Le Sharpe médian s'effondrera** entre les deux moitiés. J'annonce une
  médiane hors-échantillon **inférieure de plus de moitié** à la médiane
  d'avant.
- La fraction à Sharpe hors-échantillon **positif** sera **proche de 50 %** —
  c'est-à-dire indiscernable du hasard.
- Je m'attends à ce que **moins d'un quart** battent leur propre Sharpe
  d'avant.

Si ces trois-là sont démenties — persistance nette, majorité positive — je
devrai **d'abord douter de ma découpe** avant de conclure à un edge : une
tranche finale qui ressemble trop à l'ensemble signalerait un chevauchement,
pas une victoire.

## Ce que ce cycle ne fait pas

- Il ne **retire** aucun PASS, ne réécrit aucun verdict.
- Il ne **promeut** rien : un Sharpe positif sur 252 séances contaminées par la
  sélection ne prouve pas un edge.
- Il ne cherche **pas** de seuil à franchir : il n'y a pas de barre ici, et il
  n'y en aura pas ajoutée après coup.

## Engagements

1. Résultat rapporté tel quel, y compris un effondrement complet.
2. Les **deux** découpes publiées, quelle que soit celle qui « arrange ».
3. Aucun seuil, aucune fenêtre ajoutés ou modifiés après mesure.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
