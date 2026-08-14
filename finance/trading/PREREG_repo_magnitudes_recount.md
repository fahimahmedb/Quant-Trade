# Pré-enregistrement — re-mesurer les **grandeurs**, pas les recopies

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #461.

## Pourquoi ce cycle existe

Le #461 a vérifié que les chiffres du backlog sont **bien recopiés** depuis les
rapports qu'ils citent : 0 erreur sur 273 jetons. Il a aussi établi, contre
lui-même, **pourquoi ce résultat ne solde pas la dette** :

> Les quatre faux connus — « 8 scripts » (#449), « 6 rapports » (#451),
> « 13 orphelins » (#453), « 29 en échec » (#457) — étaient faux **par rapport
> au dépôt**, pas par rapport au rapport cité, qui portait souvent la même
> erreur. **Un contrôle de recopie ne peut structurellement pas les voir.**

Ce cycle est l'outil manquant : il ne compare plus un texte à un texte, il
**recompte dans le dépôt**.

## Les six grandeurs — définies ici par leur glob exact

Comptées sous `finance/trading/`, à un commit donné, via `git ls-tree -r` :

| Clé | Glob |
|---|---|
| `backtests` | `scripts/nonml_*_backtest.py` |
| `resultats` | `results/nonml_*_result.md` |
| `npz` | `results/nonml_*_pnl.npz` |
| `batteries` | `results/*_pass_validation_battery.md` |
| `robustesses` | `results/nonml_*_robustness.md` |
| `audits` | `results/nonml_*_audit.md` |

Ce sont des **définitions**, pas des mesures : elles sont figées ici et ne
seront pas ajustées après avoir vu les chiffres.

## L'univers — le même qu'au #461, volontairement

Les **18** entrées **#443 à #460**, chacune à **son** commit introducteur.
Reprendre le même univers permet de comparer les deux cycles ; en changer
autoriserait à attribuer un écart à la fenêtre plutôt qu'à la méthode.

## Ce qui est produit

**1. Une table de référence** — les 6 grandeurs aux 18 commits épinglés, soit
**108** cellules. C'est le chiffre vrai, mesuré dans le dépôt, que les cycles
suivants pourront citer au lieu de recopier de la prose.

**2. Une confrontation de prose, volontairement ÉTROITE.** Seuls deux mots-clés
sont assez peu ambigus pour être appariés mécaniquement :

- un entier en gras suivi, sur la même ligne, de `.npz` → comparé à `npz` ;
- un entier en gras suivi, sur la même ligne, de « batterie » → comparé à
  `batteries`.

**Je n'apparie pas « scripts » ni « rapports »** : ces mots désignent, selon la
phrase, des ensembles différents. Un appariement large produirait des écarts
qui ne diraient rien — c'est exactement le défaut n° 2 du #461, et je refuse de
le refaire en plus grand.

**3. Les quatre faux connus, recomptés dans le dépôt** — avec la valeur vraie
au commit concerné.

## Critère de succès — chiffré, il porte sur le procédé

1. **108/108** cellules de la table produites, ou manquantes **avec leur
   raison**.
2. **Tout** appariement de prose publié, avec la ligne qui le porte et la
   valeur vraie — y compris les concordances.
3. Les **quatre** faux connus recomptés, chacun avec sa valeur vraie.
4. Les définitions de globs **inchangées** après mesure.

> **PASS** = les quatre points. **FAIL** = un seul manque.

Le critère porte sur le **procédé**. Un cycle qui ne trouve aucun écart et le
montre proprement réussit.

## Prédictions — falsifiables

1. **Les quatre faux connus sont confirmés faux** par recomptage direct : le
   dépôt donne, à leur commit, une valeur différente de celle que l'entrée
   annonçait.
2. **Au moins un** appariement de prose supplémentaire est en désaccord avec le
   recomptage. Fondement : si les quatre faux ont été trouvés **par hasard**,
   il n'y a pas de raison qu'ils soient les seuls.
3. Les six grandeurs sont **croissantes** le long des 18 commits : le dépôt ne
   fait qu'ajouter. Une décroissance signalerait soit une suppression réelle,
   soit un défaut de mon comptage — et **je publierais laquelle**.

Si la prédiction 2 est réfutée, je ne dois **pas** en conclure que le backlog
est exact : mon appariement est étroit **par construction**, et il ne regarde
que deux mots-clés sur les six grandeurs.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun chiffre du backlog : tout écart est publié et
  inscrit, pas réparé au passage — engagement tenu depuis le #450.
- Il ne **régénère** aucun rapport.
- Il ne juge **aucune stratégie**.
- Il ne **remplace** pas le #461 : recopie et grandeur sont deux contrôles
  différents, et le premier reste publié avec ses limites.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que le backlog s'est
   trompé plus souvent qu'il ne l'avoue, et y compris un **FAIL** de mon
   procédé.
2. Globs, univers et règle d'appariement **inchangés** après mesure.
3. Aucune grandeur ajoutée après coup pour rattraper un résultat décevant.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
