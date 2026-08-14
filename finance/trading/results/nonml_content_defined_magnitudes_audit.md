# Audit adversarial — grandeurs définies par le contenu (#465)

Route distincte : le backtest fait un `git show` par fichier et filtre en
Python ; l'audit délègue la recherche à **`git grep`** sur l'arbre du
commit.

## A. G1 recompté aux 18 commits

- commits recomptés : **18**
- lignes du rapport relues : **18**
- **écarts** : **0**

**CONCORDANT.**

## B. La décomposition du #449 — le point qui évite une accusation

Le rapport n'accuse pas le #449 parce que **2** des importateurs sont
l'instrument du cycle. **Si cette décomposition est fausse, l'accusation
redevient due** — c'est donc le contrôle le plus important de cet audit.

- importateurs au commit du #449 : **8**
- **instrument** du cycle : **2**
  - `nonml_verdict_rule_propagation_audit.py`
  - `nonml_verdict_rule_propagation_backtest.py`
- **consommateurs** : **6**
  - `nonml_capitulation_gate_floor_sweep_backtest.py`
  - `nonml_empty_pass_basket_extension_backtest.py`
  - `nonml_empty_pass_requalification_backtest.py`
  - `nonml_pnl_persistence_lot4_audit.py`
  - `nonml_protocol_inventory_backtest.py`
  - `nonml_sameday_timestamp_resolution_backtest.py`

**CONCORDANT** — la correction « six
consommateurs » du #449 est confirmée.

## C. La limite avouée — peut-on retrouver l'émetteur ?

Le rapport avoue ne pas distinguer un **porteur** d'un **citeur**, faute
de savoir quel script **émet** la marque. Le #451 le savait. On vérifie
que cette information est bien accessible — et donc que la limite est
**réelle mais surmontable**, ce qui en fait une piste et non une impasse.

- scripts **émettant** la marque au commit du #451 : **8**
  - `nonml_capitulation_gate_floor_sweep_backtest.py`
  - `nonml_empty_pass_basket_extension_backtest.py`
  - `nonml_empty_pass_requalification_backtest.py`
  - `nonml_marker_emitted_by_scripts_backtest.py`
  - `nonml_protocol_inventory_backtest.py`
  - `nonml_reproducibility_campaign_v2_backtest.py`
  - `nonml_selfref_reports_marking_backtest.py`
  - `nonml_six_reports_regeneration_backtest.py`
- rapports contenant la marque : **8**

**CONCORDANT** — l'émetteur est identifiable dans le dépôt. La limite
du backtest tient à **sa** méthode (lire le seul texte des rapports),
pas à une impossibilité : un cycle déclaré pourrait la lever en
croisant rapports et scripts émetteurs.

## D. Idempotence de mon propre rapport

- avant : `5bcf982a3681253f`
- après : `5bcf982a3681253f`

**CONCORDANT.**

## Ce que cet audit ne couvre pas

- Il ne recompte **pas** G2 par une autre route : `git grep` trouve les
  fichiers contenant la phrase, pas ceux qui la **portent** en tête de
  ligne — c'est précisément la distinction que le rapport déclare ne pas
  savoir faire.
- Il ne dit rien du faux du **#453**, hors de portée des deux cycles.

## Verdict — **CONCORDANT** (4/4)

Aucun écart par recomptage indépendant.