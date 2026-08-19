# Le compte « 3 justifications du #485 jamais vérifiées » tient-il ? (pré-enregistré)

Phrase répétée dans la « Dette restante » de chaque cycle depuis le
**#511** : *« 2 justifications du #485 sur 5 sont tombées (#493,
#511) ; 3 n'ont jamais été vérifiées »*. Jamais nommées. Ce cycle
vérifie mécaniquement plutôt que de recopier la phrase.

## 1. Les 5 noms, extraits par script

- `protocol_inventory_audit`
- `marker_emitted_by_scripts`
- `pnl_duplicate_sweep_audit`
- `pnl_persistence_exposed_pass_audit`
- `reproducibility_campaign_v3_lot2_audit`

- extraction conforme au tableau attendu du #485 : **OUI**

## 2. Couverture par #488 / #493 — chacun cherché, verdict cité

| Script | Verdict trouvé | Cycle | Extrait |
|---|---|---|---|
| `protocol_inventory_audit` | exacte | #493 | « protocol_inventory_audit` | « colonne *Après inspection* = lecture manuelle » | **exacte**… » |
| `marker_emitted_by_scripts` | exacte | #493 | « marker_emitted_by_scripts` | « classification jamais effectuée » | **exacte** | | `pnl_per… » |
| `pnl_duplicate_sweep_audit` | **aucun** | #— | « — » |
| `pnl_persistence_exposed_pass_audit` | exacte | #493 | « pnl_persistence_exposed_pass_audit` | « univers du balayage #415, disparu » | **exacte** |… » |
| `reproducibility_campaign_v3_lot2_audit` | FAUSSE | #493 | « reproducibility_campaign_v3_lot2_audit` | « projection contrefactuelle, aucun univers » | … » |

- justifications du tableau des 5 couvertes par un verdict écrit dans #488 ou #493 : **4** sur **5**

> **1** des 5 n'ont **aucun** verdict
> retrouvé **par la règle de proximité pré-enregistrée** dans
> #488/#493.

### Ce que ces cas manqués sont réellement — mesuré après coup

La règle de proximité (marqueur dans les 400 caractères suivant
le nom) capture le format **tableau** du #493 (marqueur à ~50
caractères) mais peut manquer une conclusion écrite en **prose**,
plus loin dans la même section. Recherche élargie, **descriptive
uniquement** — elle ne change pas le compte pré-enregistré
ci-dessus, même convention que le #516 pour ses 11 exceptions :

- `pnl_duplicate_sweep_audit` : absent de la règle de proximité, mais
  la section **#488** contient ailleurs « irréparabilité tient » —
  la conclusion existe, en prose, hors de la fenêtre.

> **La règle pré-enregistrée est donc elle-même un proxy avec un
> angle mort** — exactement le constat que le #485 faisait déjà
> sur son propre proxy mécanique. Le compte `4/5` ci-dessus reste
> le chiffre pré-enregistré et publié tel quel ; cette note ne le
> révise pas, elle en documente la limite.

## 3. Le fait du #511 appartient-il à cet ensemble de 5 ?

- script cité par le #511 : `nonml_battery_backfill_lot_audit.py`
- appartient au tableau des 5 du #485 : **NON**

> **Non.** Le fait du #511 porte sur une justification de
> classification **RÉPARABLE** (une des 12-13 autres figures du
> #485), pas sur l'une des 5 lignes du tableau IRRÉPARABLE. Le
> `2 sur 5` additionne donc une chute dans le tableau des 5
> (#493) et une chute **hors** de ce tableau (#511) — **deux
> populations différentes comptées comme une seule.**

## 4. Combien de cycles ont recopié la phrase sans la ré-établir

- sections #511 à #516 contenant la phrase : **6** — [511, 512, 513, 514, 515, 516]

## Conclusion — sans forcer la lecture inverse

**Au sens strict de la règle pré-enregistrée, 4/5 sont
couverts ; en y ajoutant les 1 cas retrouvés en
prose (section « Ce que ces cas manqués sont réellement » plus
haut), les 5/5 le sont** — le second fait préliminaire se
confirme aussi mécaniquement. La phrase « 3 justifications du
#485 jamais vérifiées », recopiée depuis le #511 dans **6** cycles, est **imprécise**
pour la population qu'elle semble désigner (le tableau des 5
irréparables) : cette population est **entièrement couverte**
depuis le #493 (une fois la limite de la règle de proximité elle-
même documentée ci-dessus). Le fait réellement non
couvert est **ailleurs** — les justifications des figures classées
RÉPARABLE par le #485, dont une seule (`battery_backfill_lot_audit`,
#511) a été relue à ce jour. **Reformulation proposée pour la
dette de CE cycle**, sans réviser rétroactivement les cycles
#511-#516 :

> Sur les 5 justifications du tableau IRRÉPARABLE du #485 :
> **0 non vérifiée** (5/5 couvertes, #488+#493), **1 tombée**
> (#493). Sur les 12-13 justifications RÉPARABLE du #485 :
> **1 relue et tombée** (#511, `battery_backfill_lot_audit`),
> **11-12 jamais relues** — c'est cette population, pas les
> « 3 restantes » du tableau des 5, qui reste actionnable.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| 5/5 couverts par #488/#493 | 5 | 4 | **réfutée** |
| script #511 hors du tableau des 5 | hors | hors | **vérifiée** |
| phrase recopiée ≥ 10 fois sans nommer les 3 | ≥ 10 | 6 | **réfutée** |

## Critères de succès

1. Les 5 noms extraits par script et publiés — **OUI**.
2. Verdict (ou son absence) publié pour chacun, avec citation — **OUI**.
3. Appartenance du script du #511 à l'ensemble des 5 publiée — **OUI**.
4. Nombre de cycles ayant recopié la phrase publié — **OUI**.
5. Si 5/5 couverts : reformulation proposée, non appliquée rétroactivement — **OUI**.

**PASS** — le critère porte sur le **procédé** : une
bibliographie interne du backlog, pas une nouvelle mesure de marché.

Simulation 300 € et robustesse **sans objet** : cycle de vérification
bibliographique, aucune position, aucun paramètre numérique.

> **Rapport dépendant du dépôt** — il décrit l'état du backlog à la
> date de son exécution.
