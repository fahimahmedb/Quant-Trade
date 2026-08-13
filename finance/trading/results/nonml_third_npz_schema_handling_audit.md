# Audit — le troisième schéma `.npz` et son traitement par les balayages (#444)

Audit zéro-ML du cycle d'inventaire #444. Pré-enregistrement
`PREREG_third_npz_schema_handling.md`, committé `96fab63` **avant toute mesure**.
Anti-cheat **CONFORME** (4/4). Verdict du cycle : **FAIL**.

## 1. Le FAIL est le résultat, pas un accident

Le critère pré-enregistré était explicite : **FAIL si au moins un consommateur
applique une formule fausse**. Il y en a **2**. Le cycle échoue donc son propre
critère, et c'est publié comme tel.

Ce point mérite d'être souligné parce que ce cycle aurait été trivialement
« réussi » en n'énumérant que la concordance des 2 fichiers — connue d'avance et
concordante. Le critère avait été placé sur la question **non connue**.

## 2. Les deux D, et leur portée exacte

| Consommateur | Comment |
|---|---|
| `nonml_pnl_duplicate_sweep_backtest.py` | l.40-42 : soustrait `turn_candidate × coût` d'un `pnl_candidate` **déjà net** |
| `nonml_leaders_trend_union_pnl_persistence_audit.py` | l.55 : `sw.main()` parcourt tous les `.npz`, la branche fausse est réellement exercée |

**Ampleur** : P&L cumulé lu **+0,1705** au lieu de **+0,2028**.

**Portée, vérifiée et bornée** :
- le chiffre faux **n'apparaît dans aucun rapport publié** — le fichier n'y est
  pas nommé ;
- le seul effet possible était un **faux négatif** (doublon manqué) ; vérifié :
  **1 seule** série du dépôt a la même longueur, corrélation **+0,017**. Aucun
  doublon manqué ;
- le second fichier du schéma **échappe** au défaut, dépourvu de
  `turn_candidate`.

**Ce que je n'ai pas fait** : conclure que le défaut est donc sans importance. Il
est réel dans le code et frapperait tout futur `.npz` de ce schéma portant un
turnover. Le rapport dit les deux moitiés.

**Ce que je n'ai pas fait non plus** : le corriger. Le cycle s'était engagé à ne
faire que lire. Corriger le balayage change les séries que consomment #406, #418
et la batterie Règle 9 — c'est une modification à déclarer et mesurer dans son
propre cycle, pas un geste à glisser dans un cycle d'inventaire.

## 3. Un classement corrigé en cours de cycle

`nonml_pnl_duplicate_sweep_v2_audit.py` avait d'abord été classé **D**, au motif
qu'il importe `sw.net_pnl`. C'était une **assertion d'héritage non vérifiée** :
lecture faite, il n'appelle cette fonction que sur `A`, `B` et `PAIR_414` — des
noms codés en dur, dont aucun de ce schéma. Reclassé **A**.

Le pré-enregistrement interdisait précisément cela : « aucun classement *par
défaut* faute d'avoir lu ». La correction est publiée dans le tableau, pas
effacée.

## 4. L'écart avec le pré-enregistrement, publié

Le pré-enregistrement déclarait la concordance des 2 fichiers **connue d'avance**
et comptée zéro. **C'était trop large.** Le sondage du #443 n'avait porté que sur
`dollar_neutral_composite_pit` ; `_vol_targeted` n'avait jamais été vérifié.

L'écart n'est pas cosmétique : c'est **exactement ce fichier non sondé** qui a
livré le résultat de fond du cycle.

## 5. Le résultat de fond — le schéma ne détermine pas la convention

| Fichier | Convention | Vérifié par |
|---|---|---|
| `dollar_neutral_composite_pit` | rendements **simples** | producteur calcule sur `log1p(pnl)` |
| `dollar_neutral_composite_vol_targeted` | rendements **log** | producteur appelle `trading_metrics(r_vt)` directement, total par `np.exp(sum)` |

**Deux fichiers, mêmes clés, conventions opposées.** Aucun balayage ne peut donc
déduire la convention du schéma : quel que soit son choix, il se trompe sur l'un
des deux. C'est une contrainte réelle sur tout outillage futur, et elle n'était
pas connue avant ce cycle.

## 6. Encore une fois, mon outillage avant le dépôt

Mon premier passage appliquait `log1p` aux deux fichiers et déclarait
`_vol_targeted` **discordant**. Le pré-enregistrement engageait à me méfier
d'abord de ma reconstruction : appliqué, il a évité une fausse accusation.

Troisième fois sur cet axe : #442 (`r_alt` ignoré), #443 (coûts comptés deux
fois), #444 (`log1p` appliqué aux deux).

## 7. Une entorse de classification, signalée

`nonml_npz_report_consistency_backtest.py` (#442) **ne rentre proprement dans
aucune des quatre catégories déclarées** : il compte ces fichiers — donc pas C au
sens strict — mais sous une raison **fausse** (« schéma panier ») — donc pas B.

Classé **C**, parce que l'effet sur le lecteur est celui d'un silence. L'entorse
est signalée dans le rapport plutôt que résolue en élargissant une catégorie
après avoir vu le cas — ce qui aurait été le retuning que le protocole interdit.

## 8. Ce que le cycle ne permet pas de conclure

- **Aucune stratégie n'est validée ni invalidée.**
- Le classement porte sur **ce schéma seulement**. Rien n'est établi sur d'autres
  schémas non catalogués — ce cycle ne les a pas cherchés.
- Les catégories A pour les scripts qui ne font que compter signifient « aucune
  formule appliquée, donc rien de faussé », pas « traitement exemplaire ».

## 9. Conformité au protocole

| Point | État |
|---|---|
| Pré-enregistrement committé avant mesure | ✔ (`96fab63` < résultat) |
| `n_trials = 1` déclaré | ✔ |
| Critère susceptible d'échouer, et ayant échoué | ✔ **FAIL publié** |
| Aucun retuning après résultat | ✔ — catégories inchangées ; l'entorse signalée, pas absorbée |
| Écart au pré-enregistrement publié | ✔ (§ 4) |
| Périmètre non élargi après coup | ✔ (refus #437 appliqué) |
| Aucun rapport ni `.npz` modifié | ✔ — le cycle ne fait que lire |
| Relecture intégrale avant commit (#414) | ✔ — a corrigé « quatrième fois » → « troisième », et une phrase de la section C contredite par l'un de ses trois cas |
| Zéro ML | ✔ |
