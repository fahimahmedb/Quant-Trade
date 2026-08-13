# Audit indépendant — le détecteur de verdict corrigé (#447)

N'utilise **ni** le balayage **ni** le script de cycle : les deux règles sont
réimplémentées ici, le classement refait, puis comparé au publié.

## Contrôle 1 — la règle nouvelle est-elle bien en place ?

- occurrences de la règle nouvelle dans le balayage : **2** (2 attendues)
- ancienne règle `"**PASS" in t` absente : **OUI**

## Contrôle 2 — le classement refait indépendamment

- reclassés trouvés par cet audit : **5**
- reclassés publiés par le cycle : **5**
- **mêmes noms : OUI**

| Rapport | Avant | Après |
|---|---|---|
| `capitulation_gate_floor_sweep` | PASS | indéterminé |
| `npz_report_consistency_baskets` | PASS | indéterminé |
| `protocol_inventory` | PASS | indéterminé |
| `sweep_pass_prose_fix` | PASS | indéterminé |
| `third_npz_schema_handling` | FAIL | indéterminé |

## Contrôle 3 — la relecture, refaite d'une autre façon

Le script de cycle cherchait un verdict en titre par expression régulière.
Cet audit procède autrement : il isole les lignes contenant un marqueur et
regarde si elles **parlent du rapport lui-même** — un titre `Verdict`, ou un
marqueur seul sur sa ligne.

| Rapport | Lignes portant un marqueur | Verdict propre ? |
|---|---|---|
| `capitulation_gate_floor_sweep` | 1 | **aucun** |
| `npz_report_consistency_baskets` | 1 | **aucun** |
| `protocol_inventory` | 1 | **aucun** |
| `sweep_pass_prose_fix` | 4 | FAIL |
| `third_npz_schema_handling` | 2 | FAIL |

**Contredits : 2.**

## Verdict de l'audit

**CONFORME** sur ce qu'il vérifie.

- règle nouvelle en place aux deux endroits : **oui**
- ancienne règle absente du **code** : **oui**
- reclassés retrouvés à l'identique : **oui**

> **Le contrôle 1 s'est trompé une première fois**, et de la manière même que
> ce cycle corrige : il cherchait `"**PASS" in t` **en sous-chaîne** et la
> retrouvait dans le *commentaire* qui cite l'ancienne règle. Il cherche
> désormais la ligne **exécutable**. Troisième fois dans ce cycle qu'une
> comparaison de texte confond le code et le discours sur le code.

Cet audit **confirme aussi le FAIL** du cycle : il retrouve les mêmes
contradictions (2), par une méthode différente de celle du script
de cycle. Un audit qui ne confirmerait que les bonnes nouvelles ne servirait
à rien.

### Ce que cet audit ne prouve pas

Il ne dit pas que la règle nouvelle est **la bonne** — seulement qu'elle est
appliquée telle qu'annoncée, et que ses effets sont ceux publiés. Le cycle
établit par ailleurs qu'elle rate les verdicts énoncés en titre.
