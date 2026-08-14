# Idempotence — **épuiser la famille capable** (pré-enregistré)

Le **#470** avait tiré dix scripts **par ordre alphabétique** et n'avait
rien trouvé — puis constaté qu'**aucun ne pouvait porter le défaut**.

> Le pré-enregistrement protège contre le choix des cas **après coup**.
> Il ne protège pas contre le choix des **mauvais cas**.

Ce cycle vise la **bonne population**, assez petite pour être épuisée.

## Les deux couvertures — publiées côte à côte

L'engagement 3 l'exige : **publier la favorable seule serait trompeur.**

| Périmètre | Éprouvés | Total | Couverture |
|---|---|---|---|
| **famille capable** | 22 | 22 | **100,0 %** |
| **dépôt entier** | 37 | 324 | **11,4 %** |

Le premier chiffre dit que la population **où le défaut peut exister**
est couverte. Le second dit que **l'immense majorité du dépôt ne l'est
pas** — et les deux sont vrais en même temps.

## Le résultat

- scripts **capables** dans le dépôt : **22** sur **324**
- restaient à éprouver : **3**
- **éprouvés ici** : **3**
- **non idempotents** : **0**

| Script | État | Passage 1 | Passage 2 |
|---|---|---|---|
| `nonml_marker_emitter_crossing_backtest.py` | idempotent | `337f65f7f59307` | `337f65f7f59307` |
| `nonml_protocol_inventory_backtest.py` | idempotent | `865ce74d184071` | `865ce74d184071` |
| `nonml_sameday_timestamp_resolution_backtest.py` | idempotent | `5bfedde0a48a0e` | `5bfedde0a48a0e` |

## Les non idempotents — avec le diff qui le prouve

**Aucun.**

## Ce que « famille épuisée » ne veut pas dire

Ma règle « capable » est la condition d'énumération du détecteur du
**#466**, dont le **#467** a montré qu'il était **inutilisable comme
prédicteur de défaut** (0/6 en validation). **Ici elle ne prédit rien :
elle délimite une population** — usage différent et légitime.

Mais sa faiblesse demeure : un script qui **construirait** son
énumération autrement — variable, appel indirect — y échapperait. Le
**#469** a montré exactement ce cas sur la détection d'émission, où une
marque écrite par variable était invisible à une règle littérale.

> **Épuiser la famille capable n'est pas épuiser les scripts qui peuvent
> s'auto-inclure.** C'est épuiser ceux que **ma règle** sait reconnaître.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| 0 non idempotent | 0 | 0 | **vérifiée** |
| les 3 tiennent dans le budget | 3 | 3 | **vérifiée** |
| famille 100 %, dépôt < 12 % | — | 100,0 % / 11,4 % | **vérifiée** |

**La prédiction 1 était faible et elle passe.** Zéro défaut sur trois
scripts n'établit rien de fort : le taux observé dans cette famille
était d'environ **10 %**, soit **0,3** défaut attendu. **Ce résultat
est compatible avec à peu près n'importe quelle hypothèse.**

## L'effet de bord

Restauration **après la dernière exécution** (leçon du #468).

- résidus sous `results/` : **0**

## Critères de succès

1. **3/3** scripts traités — **OUI**.
2. Les deux empreintes publiées — **OUI**.
3. Tout non idempotent publié avec son diff — **OUI**.
4. Les deux couvertures publiées côte à côte — **OUI**.

**PASS** — le critère porte sur le
**procédé**.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).