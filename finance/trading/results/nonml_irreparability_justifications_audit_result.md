# Les **4 autres justifications** d'irréparabilité (pré-enregistré)

Le **#488** a repris **une** des cinq raisons d'irréparabilité du #485 et
l'a trouvée **fausse** — le verdict survivant. **Les 4 autres n'avaient
jamais été relues.**

> `nonml_pnl_duplicate_sweep_audit`, tranché au #488, est **exclu** de ce cycle : il
> n'est pas rejugé.

## Ce que chacun énumère — mécanique, avant toute lecture

| Script | Énumère | Constantes en dur | Interpolations | Fonctions |
|---|---|---|---|---|
| `nonml_protocol_inventory_audit.py` | **rien** | — | **4** | 1 |
| `nonml_marker_emitted_by_scripts_backtest.py` | `read_text` | `CIBLES` | **9** | 3 |
| `nonml_pnl_persistence_exposed_pass_audit.py` | **rien** | `TARGETS` | **13** | 2 |
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | `glob`, `read_text` | `SENTINEL_NAMES` | **16** | 3 |

## Les verdicts, un par un

**Écrits à la main après lecture, chacun adossé à une ligne de code.**

### `nonml_protocol_inventory_audit.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « colonne « Après inspection » = **lecture manuelle** »

Le script **n'énumère rien** — ni `glob`, ni `iterdir`, ni `read_text` — et n'importe aucun module du dépôt. Ses **4** seules interpolations sont `len(names)` et `total` dans une boucle de listage. **Les valeurs de la colonne « Après inspection » (1, 0, 6, 0, 0) ne sont dérivables de rien dans ce fichier.** L'assertion négative tient.

### `nonml_marker_emitted_by_scripts_backtest.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « classification **jamais effectuée** par le script »

`CIBLES` est une liste de **5 entrées codées en dur** (l.25), et le script ne lit que ces fichiers-là. Il **n'énumère jamais** `results/`. **Le #473 l'avait établi sur pièce** ; la relecture le confirme.

### `nonml_pnl_persistence_exposed_pass_audit.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « univers du balayage #415, **disparu** »

`TARGETS` est une liste de **10 entrées codées en dur** (l.31). Les seuls accès disque sont des tests d'existence **par cible** — `(RESULTS / f"nonml_{n}_pnl.npz").exists()` (l.123) — jamais un `glob`. **L'univers du balayage #415 n'est ni construit ni atteignable.**

### `nonml_reproducibility_campaign_v3_lot2_audit.py` — **JUSTIFICATION FAUSSE, VERDICT À REVOIR**

Justification du #485, **verbatim** : « projection contrefactuelle, **aucun univers** »

**L'assertion est fausse, et le verdict tombe avec elle.** Le script définit `def bound(n)` **au niveau module** (l.29), lie `cum` dans `main()` (l.59), et publie **déjà** `{100*bound(cum):.1f} %` aux lignes **126, 145 et 176**. Le « **6,2 %** » écrit en dur l.159 est **exactement cette valeur**, et le « **~4,1 %** » est `100*bound(cum + 24)`. **Les deux sont dérivables d'une fonction que le script possède.**

## Le compte

- justifications **exactes** : **3 / 4**
- justifications **fausses** : **1**
- **verdicts d'irréparabilité qui tombent** : **1**
  - `nonml_reproducibility_campaign_v3_lot2_audit.py`

### Le compte du #485 est corrigé

| | #485 | Ici |
|---|---|---|
| irréparables | 5 | **4** |
| réparables | 12 | **13** |

> **Ma prédiction 2 annonçait qu'aucun verdict ne tomberait. Elle est
> réfutée**, et c'est un verdict que **j'ai signé au #485**.

**Le cas est aggravant, pas anodin** : le même rapport publie
`6,2 %` **comme valeur interpolée** aux lignes 126, 145 et 176, **et**
**comme littéral** à la ligne 159. **Deux sources pour un même chiffre
dans un même document** — exactement la famille de défauts que les
#479 à #488 ont passé dix cycles à dénombrer, et qui a échappé au
recensement parce que j'ai cru une phrase au lieu de lire le code.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 1 justification fausse | ≥ 1 | 1 | **vérifiée** |
| aucun verdict ne tombe | 0 | 1 | **réfutée** |
| `marker_emitted_by_scripts` exacte | exacte | exacte | **vérifiée** |

**La prédiction 2 est réfutée, et c'est le résultat qui compte.**
J'annonçais que les 4 tiendraient ; l'un tombe. **Le #485 avait donc
un irréparable de trop**, et il aurait suffi de lire son code plutôt
que de relire ma propre phrase.

> **Deux cycles sur cinq justifications relues, deux justifications
> fausses** (#488 et celui-ci). **Le taux ne se généralise pas** — il
> ne reste plus rien à relire, les 5 le sont toutes.

## Critères de succès

1. Les **4** nommés, ce qu'ils énumèrent publié — **OUI**.
2. Justifications citées verbatim — **OUI**.
3. **4/4** examinés, chacun adossé à une ligne de code — **OUI**.
4. Verdict renversé publié et compte du #485 corrigé — **OUI**.
5. `nonml_pnl_duplicate_sweep_audit` exclu explicitement — **OUI**.

**PASS** — le critère porte sur le **procédé** :
un cycle qui fait tomber un de ses propres verdicts et le publie réussit.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).