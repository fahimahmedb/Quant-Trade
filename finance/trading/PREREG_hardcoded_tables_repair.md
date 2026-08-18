# Pré-enregistrement — **réparer les 2 tableaux tapés à la main**

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, première piste de la file ouverte au #481. Le premier
depuis longtemps qui **touche** au dépôt plutôt que de le lire.

## Ce qui est réparé, et pourquoi ces deux-là

Le **#479** a dénombré **18** chiffres publiés sans code qui les produise. Il
n'en a désigné que **deux** comme réparables en priorité — les seuls où **un
tableau entier de résultats** est tapé à la main, si bien qu'un lecteur **ne
peut pas distinguer une mesure d'une saisie** :

| Script | Ce qui est écrit en dur |
|---|---|
| `nonml_pnl_persistence_exposed_pass_audit.py` | `\| candidats mesurés \| 33 \| **42** \|`, `\| détectés non mesurés \| 29 \| **20** \|`, `\| dont portant un PASS \| 10 \| **0** \|` |
| `nonml_reproducibility_sample_lot3_audit.py` | `\| scripts de backtest non-ML du dépôt \| **284** \|`, `\| **couverture non-ML** \| **73.2 %** \|` |

Les **16 autres** ne sont **pas** touchés : citations, seuils pré-enregistrés,
constantes de protocole, et défauts en prose dont la réparation demanderait de
réécrire un raisonnement. **Ce cycle ne se donne pas ce droit.**

## La modification — minimale et bornée

Pour chacun des deux scripts : **remplacer la chaîne littérale par une
interpolation de la grandeur déjà calculée dans le script**, ou la calculer si
elle ne l'est pas.

**Interdits, explicitement :** changer un seuil, une population, un critère, un
verdict, une prose de conclusion. **Seules les lignes nommées ci-dessus sont
touchées.** Le diff du code sera publié en entier.

## Le risque central, dit d'avance

**Un chiffre recalculé aujourd'hui peut ne pas valoir le chiffre tapé hier.**
C'est même l'intérêt de la réparation : elle rend visible une dérive
qu'une saisie fige. Trois issues, toutes publiables :

- **IDENTIQUE** — le rapport régénéré est octet pour octet celui qui est
  publié : la saisie était juste, et devient reproductible ;
- **DIFFÉRENT** — les chiffres ont bougé : **le diff est publié**, et le
  verdict du cycle d'origine **n'est pas réécrit** ;
- **ERREUR** — le script ne s'exécute plus : publié tel quel.

## Ce qui sera committé, et ce qui ne le sera pas

- Le **code réparé** : committé dans tous les cas.
- Le **rapport régénéré** : committé **uniquement si IDENTIQUE**.

**Si le rapport diffère, il n'est pas committé.** Remplacer un résultat publié
par un autre est un acte plus lourd que ce cycle n'en autorise : la décision
serait prise sans que personne ait relu ce que le nouveau chiffre signifie.
**Le diff est publié, la décision est inscrite et laissée ouverte.**

## Le protocole d'exécution

Chaque script réparé est **exécuté deux fois** (empreintes SHA-256 comparées —
contrôle d'idempotence, leçons #463 et #468). L'arbre est **restauré après la
dernière exécution**, pas entre elles, et les **résidus vérifiés ensuite** par
`git status --porcelain finance/trading/results/`.

Budget **300 s** par exécution.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **2** scripts modifiés, **diff du code publié en entier**.
2. Chacun exécuté **deux fois**, les **deux empreintes** publiées.
3. Le **diff avant/après du rapport** publié pour chacun.
4. Rapport régénéré committé **seulement** si identique — et le rapport le dit
   explicitement pour chacun.
5. **Zéro résidu** sous `results/` hors des deux rapports visés et du mien.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les **2** s'exécutent sans erreur dans le budget.
2. **Au moins un** produit des chiffres **différents** de ceux qui sont tapés —
   le dépôt a grossi depuis leur rédaction.
3. Les **2** sont **idempotents** : deux passages, même empreinte.

Si la prédiction 2 est réfutée — **les deux identiques** — alors les saisies
étaient exactes et le sont restées, et la réparation n'apporte que la
**reproductibilité**. C'est le résultat le moins spectaculaire et il devra être
rapporté comme tel, sans le grossir.

## Ce que ce cycle ne fait pas

- Il ne touche **aucun** des 16 autres chiffres littéraux.
- Il ne **réécrit** aucun verdict, aucune entrée de backlog existante.
- Il ne **commite pas** un rapport dont le contenu a changé.

## Simulation 300 € et robustesse

**Sans objet** : aucune position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si la réparation révèle que les
   chiffres publiés étaient faux.
2. Périmètre des lignes touchées **inchangé** après mesure.
3. **Diff du code publié en entier**, jamais résumé — leçon « code contre
   discours sur le code » des #446 à #449.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
