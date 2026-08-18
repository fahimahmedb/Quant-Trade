# Pré-enregistrement — les **2 masquants restants**

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, première piste de la file ouverte au #488.

## Ce qui reste

Le **#487** a réparé 2 des 4 sections masquantes, et a laissé les 2 autres avec
cette justification :

> Les deux restants — `battery_coverage` l.159 et `net_pnl_correction` l.279 —
> **ne sont pas touchés** : **leur garde ne porte pas sur une liste de
> résultats**, et la même recette ne s'y applique pas telle quelle.

**Cette phrase n'a jamais été vérifiée.** Ce cycle la met à l'épreuve, puis
répare ce qui peut l'être.

| Script | Garde | Section masquée |
|---|---|---|
| `nonml_battery_coverage_backtest.py` l.159 | `if indet:` | « Une limite de la règle unifiée, découverte ici » |
| `nonml_net_pnl_correction_backtest.py` l.279 | `if incoh:` | « Une incohérence exposée par le rafraîchissement » |

## Volet A — la phrase du #487 est-elle exacte ?

Établi par **AST** : la variable de garde est-elle liée à une **liste** (`List`,
compréhension) ou à un **entier** (`sum`, `len`) ? Les deux cas admettent un
témoin — `len(x)` pour l'un, la valeur elle-même pour l'autre — mais **la forme
du témoin diffère**, et c'est précisément ce que le #487 n'avait pas regardé.

## Volet B — le patch, borné à une ligne par cas

Forme fixée ici, adaptée au type :

```python
# garde sur une liste
L.append(f"- <libellé> : **{len(<var>)}**")
# garde sur un entier
L.append(f"- <libellé> : **{<var>}**")
```

**Interdits, explicitement** : modifier la garde, le contenu de la section, un
seuil, un verdict, une prose. **Le diff sera publié en entier.**

Si le volet A montre qu'**aucun témoin n'est possible** pour l'un des deux, il
**n'est pas patché**, et le rapport dit pourquoi.

## Volet C — exécution, asymétrique et déclarée

Vérifié avant d'écrire ceci *(inventaire de structure, aucune mesure)* :

- `battery_coverage` **exécute la batterie de validation**
  (`subprocess.run([sys.executable, BATTERIE, …])`, l.110) → **non exécuté** ;
- `net_pnl_correction` n'appelle `subprocess` que pour **`git show`** (l.219) et
  n'écrit que **son propre rapport** (l.325) → **exécutable sans dégât**.

**Celui-ci sera donc exécuté deux fois** (empreintes SHA-256, contrôle
d'idempotence), et son rapport régénéré **committé si et seulement si** le diff
se réduit **à la ligne de témoin ajoutée**. Toute autre différence ⇒ **rapport
non committé**, diff publié.

L'autre gardera son rapport inchangé, et **le rapport devra dire que son témoin
n'est pas encore visible** — comme au #487.

## Critère de succès — chiffré, il porte sur le procédé

1. Le **type** de chaque variable de garde publié, et la phrase du #487
   **confirmée ou rétractée**.
2. **Diff du code publié en entier**, une instruction par cas patché.
3. La règle du #481 ré-appliquée **avant et après**, et le déplacement publié.
4. Exécution **asymétrique respectée** : `battery_coverage` non exécuté,
   vérifié par l'état git de son rapport.
5. Rapport régénéré committé **seulement** si son diff se réduit au témoin.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les **2** admettent un témoin — aucun n'est structurellement irréparable.
2. Après patch, le compte de masquants passe de **2** à **0**.
3. La phrase du #487 est **inexacte pour au moins l'un des deux** : `incoh` est
   bien une **liste**.

Si la prédiction 3 se vérifie, **le #487 s'est donné une raison commode de ne
pas finir le travail**, et je devrai l'écrire — c'est moi qui l'ai écrite.

## Ce que ce cycle ne fait pas

- Il n'**exécute pas** `battery_coverage`.
- Il ne **corrige pas** la règle du #481, dont les trois angles morts restent
  inscrits.
- Il ne **touche** à aucune autre section conditionnelle.

## Simulation 300 € et robustesse

**Sans objet** : aucune position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que le #487 s'est arrêté
   trop tôt.
2. Périmètre des lignes touchées **inchangé** après mesure.
3. **Diff publié en entier**, jamais résumé.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
