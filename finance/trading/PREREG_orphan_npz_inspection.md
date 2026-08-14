# Pré-enregistrement — les `.npz` sans rapport publié, inspectés nom par nom

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.

## La dette, ouverte au #442 et jamais traitée

Le #442 a vérifié la concordance `.npz` / rapport sur **165** fichiers, et en a
écarté **20** faute de rapport publié à leur nom. Ces vingt sont restés inscrits
sans être regardés, à travers dix cycles.

Un `.npz` sans rapport est **une série que rien ne documente**. Elle est
pourtant lue par tous les balayages : doublons (#406/#445), activation (#415),
concordance (#442). Si elle correspondait à une stratégie dont le verdict est
publié ailleurs, sous un autre nom, elle serait comptée deux fois ; si elle ne
correspondait à rien, elle gonflerait des dénominateurs sans rien mesurer.

## Le chiffre de 20 est lui aussi présumé faux

Il vient du #442, et **n'a pas été revérifié depuis** — dix cycles pendant
lesquels le dépôt a grossi de plusieurs dizaines de fichiers. Les #449 et #451
ont chacun montré qu'un compte de backlog non revérifié était faux.

Il sera **recompté**, et l'écart publié.

## Le contrôle — classer chacun, par lecture, avec sa preuve

Pour chaque `.npz` sans `nonml_<nom>_result.md` :

| Code | Classe | Preuve exigée |
|---|---|---|
| **V** | **variante** dont le rapport porte un autre nom | le rapport trouvé est **nommé** |
| **M** | série **ML / Étape D**, hors univers non-ML | le nom ne commence pas par `nonml_` |
| **O** | **orphelin réel** — aucun rapport nulle part | recherche du nom dans tout `results/`, **négative** |

La classe **V** ne peut pas être affirmée : elle exige de **désigner** le
rapport. Un candidat dont je ne trouve pas le rapport est **O**, même si je
soupçonne qu'il existe — c'est la discipline du contrôle B du #431.

## Critère de succès — chiffré, et il peut échouer

1. **100 %** des `.npz` sans rapport homonyme sont classés V, M ou O.
2. **Aucun V sans son rapport nommé.** Un seul V affirmé sans preuve fait
   échouer le cycle.
3. Le **compte réel** est publié, avec l'écart au chiffre de 20 du #442.
4. **Aucun rapport ni `.npz` modifié.**

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédiction — falsifiable

- **Le chiffre de 20 est faux.** Je ne sais pas dans quel sens : le dépôt a
  grandi, donc il peut y avoir **plus** d'orphelins ; mais des cycles récents ont
  aussi publié des rapports qui en ont **résorbé**. Je m'abstiens de parier sur
  le sens — dire « il est faux » sans direction est une prédiction plus faible,
  et c'est la seule que je puisse honnêtement faire.
- J'attends que la classe **M** (séries ML / Étape D) en absorbe une partie
  notable : le balayage lit `results/*_pnl.npz` **sans filtre de préfixe**, ce
  que son propre rapport signale depuis le #428.
- J'attends **au moins un O** — un orphelin réel. S'il n'y en a aucun, la dette
  ouverte au #442 était vide, et il faudra le dire.

## Ce que ce cycle ne fait pas

- Il ne **supprime** aucun fichier, même orphelin confirmé.
- Il ne **produit** aucun rapport manquant.
- Il ne **retire** rien d'aucun décompte : requalifier est un cycle à part.

## Engagements

1. Résultat rapporté tel quel, y compris **0 orphelin**.
2. Aucun classement V sans le rapport désigné.
3. Le compte réel publié, même s'il contredit le backlog.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
