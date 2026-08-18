# Pré-enregistrement — **ajouter un témoin** aux 2 sections masquantes

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, première piste de la file ouverte au #486. Le second
qui touche au dépôt — après le #482, **qui n'a finalement rien modifié**.

## Ce qui est réparé

Les **#481** et **#484** ont établi, par lecture à la main, **4 sections
masquantes** : des sections dont la garde peut être fausse et dont **aucun
compte publié hors garde** ne signale l'absence. Deux d'entre elles sont
désignées ici — les seules dont la garde porte sur une **liste de résultats**,
donc réparables par l'ajout d'une ligne :

| Script | Garde | Section masquée |
|---|---|---|
| `nonml_six_reports_regeneration_backtest.py` l.232 | `if perdus:` | « Un effet de bord découvert — les marqueurs du #439 sont effacés » |
| `nonml_sweep_pass_prose_fix_backtest.py` l.134 | `if strategies:` | « Le résultat qui prime sur la correction de prose » |

Les **2 autres masquants** ne sont **pas** touchés : ils appartiennent aux
#481/#484 et n'ont pas été réexaminés ici.

## La modification — une ligne par cas, et rien d'autre

Pour chacun : **une seule ligne ajoutée**, **hors de la garde**, publiant
l'effectif par interpolation. Forme fixée ici :

```python
L.append(f"- <libellé> : **{len(<variable de garde>)}**")
```

**Interdits, explicitement** : modifier la garde, le contenu de la section, un
seuil, un verdict, une prose de conclusion, ou toute autre ligne. **Le diff du
code sera publié en entier.**

## Ce cycle n'exécutera **ni l'un ni l'autre** — et pourquoi

Vérifié avant d'écrire ceci *(inventaire de structure, aucune mesure)* :

- `six_reports_regeneration` **exécute d'autres scripts du dépôt** et réécrit
  leurs rapports (`subprocess.run([sys.executable, …])`, ligne 75) ;
- `sweep_pass_prose_fix` **écrit deux fichiers**, dont un rapport qui n'est pas
  le sien (lignes 248 et 314).

> **Les exécuter pour « vérifier » la réparation causerait plus de dégâts que le
> défaut réparé.** Le #482 avait déjà refusé d'exécuter le premier pour cette
> raison exacte.

**La vérification sera donc statique** : la règle du #481 est ré-appliquée au
code, avant et après patch, et les deux cas doivent passer de **SANS TÉMOIN** à
**AVEC TÉMOIN**. Les rapports publiés porteront le témoin **à leur prochaine
exécution légitime** — et le rapport devra le dire, sans laisser croire que la
réparation est déjà visible.

## Critère de succès — chiffré, il porte sur le procédé

1. **Diff du code publié en entier**, et **exactement 2 lignes ajoutées**,
   aucune supprimée ni modifiée.
2. La règle du #481 ré-appliquée **avant et après**, et le déplacement des deux
   cas publié.
3. **Aucune exécution** des deux scripts — vérifié et déclaré.
4. **Aucun autre fichier** modifié, et **aucun rapport régénéré**.
5. Le fait que les rapports publiés **ne portent pas encore** le témoin, écrit
   explicitement.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Après patch, la règle du #481 classe les **2** cas **AVEC TÉMOIN** — le
   compte de masquants passe de **4** à **2**.
2. Le nombre **total** de titres conditionnels est **inchangé** : on ajoute un
   témoin, pas une garde.
3. **Aucun autre cas** ne change de classe — le patch est borné.

Si la prédiction 1 est réfutée, c'est que ma forme de témoin ne satisfait pas ma
propre règle, et **le patch sera publié comme insuffisant plutôt que retouché
jusqu'à passer**.

## Ce que ce cycle ne fait pas

- Il ne touche **aucun** des 2 autres masquants, ni aucune des 11 sections
  anodines.
- Il n'**exécute** aucun script du dépôt.
- Il ne **régénère** ni ne **committe** aucun rapport modifié.
- Il ne **corrige pas** la règle du #481, dont les trois angles morts restent
  inscrits.

## Simulation 300 € et robustesse

**Sans objet** : aucune position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si le patch ne satisfait pas ma propre
   règle.
2. Périmètre des lignes touchées **inchangé** après mesure.
3. **Diff publié en entier**, jamais résumé — leçon « code contre discours sur
   le code » des #446 à #449.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
