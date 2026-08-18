# Pré-enregistrement — **étendre la règle tolérante au #483**, sans toucher à son critère

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #497.

## L'état de la question

- Le **#483** a mesuré la convention d'auto-déclaration avec une règle
  **littérale** (`Cycle d[e']\s*\*\*…\*\*`), conclu **C — aucune structure
  temporelle**, et publié un fait très net : **380** pré-enregistrements
  antérieurs au 13/08/2026, **0 déclaré**.
- Le **#492** a montré que cette règle **décroche sur la typographie** : les
  cycles récents écrivent `**Cycle de MODIFICATION**` (phrase entière en gras).
  Sa règle **tolérante** trouve **72** déclarés au lieu de 34, et **95 %** des
  20 plus récents au lieu de 5 %.

**Le #483 n'a jamais été rejoué avec la règle tolérante.** Son verdict **C**
et son « 380 / 0 » reposent donc sur un détecteur dont on sait qu'il décroche.

## La question de légitimité, tranchée **ici**

Rejouer une mesure avec un autre détecteur après avoir vu son verdict est
**dangereux** — c'est la forme la plus discrète du retuning. Trois garde-fous,
déclarés avant toute mesure :

1. **Le critère du #483 n'est pas touché.** Il reste, mot pour mot :
   **A** si `m_d > m_n` **et** `p ≥ 50 %` ; **B** si `m_d < m_n` **et**
   `p < 20 %` ; **C** sinon — où `p` est la part des déclarés parmi les **40**
   plus récents. **Aucun seuil ne bouge.**
2. **La règle tolérante n'est pas fabriquée ici.** Elle a été établie au #492,
   sur **sa** population et **son** critère, pour une raison étrangère au
   verdict du #483. Je la reprends **verbatim**, sans l'amender.
3. **Les deux règles tournent sur la MÊME population, re-dérivée aujourd'hui.**
   Le dépôt a grossi depuis le #483 : comparer ses chiffres d'alors aux miens
   confondrait **effet de détecteur** et **effet de population**. Je publie donc
   littérale et tolérante **côte à côte sur la population du jour**.

> Sans le garde-fou 3, tout écart serait ininterprétable. C'est lui qui fait
> de ce cycle une vérification et non une illustration.

## Ce qui est mesuré

Sur la population du jour, **pour chacune des deux règles** :

1. Le nombre de **déclarés** et de **non déclarés**.
2. Les **deux médianes** de date d'introduction, `m_d` et `m_n`.
3. La part `p` parmi les **40** plus récents.
4. Le **verdict** rendu par le critère **inchangé** du #483.
5. La **chronologie par tranches**, comme au #483.
6. Le fait « **380 antérieurs, 0 déclaré** » du #483, **re-testé** : combien de
   déclarés **précèdent** la date du premier déclaré littéral ?

## Critère de succès — chiffré, il porte sur le procédé

1. Les **deux règles citées verbatim**, et le critère du #483 cité **mot pour
   mot**, inchangé.
2. Les deux mesures conduites sur **une seule et même population**, sa taille
   publiée.
3. Les **deux verdicts** publiés — y compris s'ils diffèrent.
4. Le fait « 380 / 0 » du #483 **re-testé** et son sort publié.
5. **Aucun script du dépôt exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Sous la règle tolérante, le verdict devient **A** — la convention est
   **récente et dominante** dans sa période.
2. Le « 380 / 0 » du #483 **ne survit pas** : au moins **1** déclaré tolérant
   précède la date du premier déclaré littéral.
3. Sous la règle **littérale** appliquée à la population du jour, le verdict
   reste **C** — l'écart vient bien du **détecteur**, pas de la croissance du
   dépôt.

Si la prédiction 1 est réfutée et que le verdict reste **C** même en tolérant,
alors le #483 avait raison **pour de mauvaises raisons**, et je devrai l'écrire :
son détecteur était faux **et** sa conclusion juste.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script du dépôt, ne **régénère** aucun rapport.
- Il ne **corrige** pas le rapport du #483 — un rapport est une **sortie de
  programme** ; le rejouer à la main serait fabriquer ce que cette série
  reproche depuis le #479.
- Il n'**amende** ni la règle tolérante ni le critère du #483.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il **confirme** le verdict du #483
   et rend ce cycle stérile.
2. Règles, critère et population **inchangés** après mesure.
3. Les deux verdicts publiés **côte à côte**, jamais le seul favorable.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
