# Audit adversarial — la réserve du #485, tranchée (#488)

Le cycle conclut **A** (irréparable) **tout en réfutant la justification
du #485**. C'est une position confortable : il **garde le verdict qu'il a
signé** en se donnant le mérite d'en corriger la raison. **L'audit teste
donc les deux moitiés séparément.**

## 1. Le script lit-il vraiment le backlog ?

Route : **AST** — un appel `.read_text()` sur un nom contenant `BACKLOG`,
et non une correspondance textuelle.

- lecture du backlog détectée : **OUI**

> **Confirmé par une route indépendante.** La justification du #485 —
> « cet audit ne construit pas le décompte » — **est bien fausse**, et
> le #488 a raison de la réfuter. **Cette moitié tient.**

## 2. Le `372` est-il hors de portée de **tout** le dépôt ?

Le #488 ne teste que la cible. **L'audit élargit** : un autre script
expose-t-il une comptabilité d'**essais** que la cible pourrait importer ?

| Motif | Scripts retenus |
|---|---|
| **large** — toute mention de « n_trials » | **294** |
| **précis** — constante de module ou fonction exposant le compte | **60** |

  - `nonml_atr_vol_targeting_overlay_backtest.py`
  - `nonml_auto_loan_delinquency_overlay_backtest.py`
  - `nonml_autocorrelation_regime_overlay_backtest.py`
  - `nonml_backlog_spa_dsr_validation_audit.py`
  - `nonml_bitcoin_momentum_overlay_backtest.py`
  - `nonml_breadth_vol_targeting_overlay_backtest.py`
  - `nonml_capacity_utilization_overlay_backtest.py`
  - `nonml_chicago_fed_activity_overlay_backtest.py`

*(**Mon premier motif sur-captait massivement** : il retenait
**294** scripts parce que « `n_trials = 1` » est écrit **en
prose** dans presque chaque pré-enregistrement cité. **C'est mon
instrument qui était fautif, pas le dépôt** — même nature d'erreur
qu'aux #478, #482, #484 et #487, et je publie les deux comptes.)*

> **60 module(s)** passent le motif précis — mais
> l'inspection de leurs noms montre qu'il s'agit de **scripts de
> stratégie déclarant leur propre `n_trials = 1`** pour le calcul du
> DSR, **pas** de modules exposant une comptabilité du dépôt.

> **Aucun motif textuel ne sait faire cette distinction**, et je ne
> vais pas en essayer un troisième : ce serait ajuster l'instrument
> jusqu'à ce qu'il donne la réponse attendue. **Ce contrôle est donc
> déclaré non concluant** — il n'infirme pas le #488, il ne le
> confirme pas non plus.

## 3. L'écart `n_entries` / `372` est-il stable dans l'historique ?

Si `n_entries` avait **valu 372** à un moment, la thèse « ce n'est pas la
même grandeur » s'effondrerait. **Contrôle sur l'historique du backlog.**

- commits du backlog échantillonnés : **25**
- `n_entries` observé : de **23** à **449**
- a-t-il **jamais** valu **372** : **NON**

> **`n_entries` n'a jamais valu 372** sur l'échantillon
> historique. La thèse du #488 — deux grandeurs différentes — **tient**
> par une voie qu'il n'avait pas empruntée.

## 4. Le cycle publie-t-il ce qui l'affaiblit ?

| Contrôle | Résultat |
|---|---|
| il déclare que sa prédiction 2 est réfutée | **OUI** |
| il écrit que la justification du #485 était fausse | **OUI** |
| il ne s'attribue pas la réserve de l'audit comme un succès | **OUI** |
| il rappelle que c'est lui qui a signé le verdict du #485 | **OUI** |
| il ne tranche pas la question `n_trials` du #421 | **OUI** |

> **Le cycle garde son verdict et démolit sa justification**, sans
> présenter la seconde opération comme un mérite. C'est la seule
> façon honnête de conclure « A » quand on a soi-même signé le #485.

## Effets de bord du backtest

- écritures : **1** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire le disque.**

## Verdict

**CONCORDANT SUR 2 CONTRÔLES SUR 3** — la réfutation de la
justification du #485 est **confirmée** (contrôle 1), l'écart des deux
grandeurs **tient sur l'historique** (contrôle 3), et
**5/5** contrôles de
transparence sont tenus.

**Le contrôle 2 est déclaré non concluant** : aucun motif textuel ne
distingue un script déclarant son propre `n_trials` d'un module exposant
une comptabilité du dépôt. **Il n'infirme pas le #488, il ne le confirme
pas non plus** — et j'ai refusé d'essayer un troisième motif jusqu'à
obtenir la réponse attendue.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).