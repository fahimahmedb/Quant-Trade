# Pré-enregistrement — les **4 autres justifications** d'irréparabilité

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #492.

## Ce que le #488 a révélé

Le **#485** avait classé **5 défauts irréparables**, chacun avec sa raison. Le
**#488** a repris **une seule** de ces raisons — celle de
`pnl_duplicate_sweep_audit` — et l'a trouvée **fausse** :

> Le #485 disait que l'audit « **ne construit pas** » le décompte du backlog.
> **C'est faux** : il en construit un. Ce qui est vrai, c'est que **le décompte
> qu'il construit n'est pas celui-là**.

**Le verdict avait survécu, la justification était fausse.** Les **4 autres**
n'ont jamais été relues. Ce cycle les relit.

## La population — les 4, nommées

| Script | Justification du #485, à éprouver |
|---|---|
| `protocol_inventory_audit` | « colonne *Après inspection* = **lecture manuelle** » |
| `marker_emitted_by_scripts` | « classification **jamais effectuée** par le script » |
| `pnl_persistence_exposed_pass_audit` | « univers du balayage #415, **disparu** » |
| `reproducibility_campaign_v3_lot2_audit` | « projection contrefactuelle, **aucun univers** » |

Chacune contient une **assertion négative** — « ne fait pas », « jamais »,
« disparu », « aucun ». **C'est exactement la forme qui s'est révélée fausse au
#488**, et c'est elle qui est testée.

## Le protocole — mécanique d'abord, lecture ensuite

Pour chacun des 4, établi par **AST** avant toute lecture :

1. **ce que le script énumère** — `glob`, `iterdir`, `read_text`, imports de
   modules du dépôt ;
2. **ce qu'il calcule et publie** — grandeurs interpolées dans son rapport ;
3. **l'assertion négative est-elle littéralement vraie** au vu de 1 et 2 ?

## L'examen à la main — DÉCLARÉ ICI

Les #480, #483, #484 et #489 ont montré ce que coûte un examen non déclaré.
**Les 4 sont lus**, chacun recevant l'un de ces verdicts :

- **JUSTIFICATION EXACTE** — l'assertion négative tient au vu du code ;
- **JUSTIFICATION FAUSSE, VERDICT SURVIVANT** — l'assertion est fausse, mais
  l'irréparabilité tient pour une autre raison, **qui doit être énoncée** ;
- **JUSTIFICATION FAUSSE, VERDICT À REVOIR** — l'assertion est fausse **et**
  l'irréparabilité ne tient plus : le compte de 5 du #485 doit baisser.

**Aucun verdict ne sera écrit sans la ligne de code qui le fonde.**

## Critère de succès — chiffré, il porte sur le procédé

1. Les **4** nommés, et **ce que chacun énumère** publié.
2. La **phrase de justification citée verbatim** pour chacun.
3. **4/4** examinés à la main, avec verdict **et** ligne de code à l'appui.
4. Tout **verdict d'irréparabilité renversé** publié comme tel, et le compte du
   #485 **corrigé à la baisse** dans le rapport.
5. Le cas déjà tranché au #488 **exclu explicitement** — il n'est pas rejugé.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 1** des 4 a une **justification fausse**, comme au #488.
2. **Aucun** verdict d'irréparabilité ne tombe : les 4 restent irréparables.
3. `marker_emitted_by_scripts` a une justification **exacte** — c'est le seul
   des cinq dont le cas a été établi **sur pièce** par un cycle dédié (#473).

Si la prédiction 2 est réfutée — un verdict tombe — alors **le compte de
5 irréparables du #485 est faux**, et je devrai le corriger dans ce rapport
plutôt que de le laisser courir dans la dette.

## Ce que ce cycle ne fait pas

- Il ne **répare** rien, ne modifie aucun script.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **rejuge pas** `pnl_duplicate_sweep_audit`, tranché au #488.
- Il ne **rouvre pas** la question `n_trials` du #421, qui relève de l'arbitrage
  de l'utilisateur.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il fait tomber un verdict que j'ai
   signé au #485.
2. Population, protocole et forme des verdicts **inchangés** après mesure.
3. **Chaque verdict adossé à une ligne de code citée**, jamais à une impression.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
