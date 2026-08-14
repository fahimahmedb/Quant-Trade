# Idempotence — **lot 2** : dix scripts jamais éprouvés (pré-enregistré)

Le **#467** a clos la piste de la **détection statique** : sur 6
signalements, **0** était réellement défectueux. Ce qui reste est coûteux
et démontré — **rejouer les scripts**.

## La couverture, en proportion

- scripts du dépôt : **323**
- éprouvés avant ce cycle : **24**
- éprouvés ici : **10**
- **couverture atteinte** : **34 / 323** (**10,5 %**)

> **L'engagement 3 demandait la proportion, pas seulement le nombre.**
> « 34 scripts éprouvés » sonne mieux que « **10,5 %** du
> dépôt », et c'est la seconde formulation qui dit la vérité.

## Le résultat

- échantillon : **10** *(10 premiers par ordre
  alphabétique parmi les jamais éprouvés — règle fixée avant de regarder)*
- **éprouvés** : **10**
- **écartés** : **0**
- **non idempotents** : **0**

## Les deux empreintes, script par script

| Script | État | Passage 1 | Passage 2 |
|---|---|---|---|
| `nonml_acf_lag1_vol_targeting_overlay_backtest.py` | idempotent | `64145880e56fca` | `64145880e56fca` |
| `nonml_amihud_illiquidity_tilt_backtest.py` | idempotent | `72c9328cfbc02b` | `72c9328cfbc02b` |
| `nonml_amihud_illiquidity_tilt_pit_universe_backtest.py` | idempotent | `8adece25631a05` | `8adece25631a05` |
| `nonml_arch_clustering_vol_targeting_overlay_backtest.py` | idempotent | `fc30eae327efbf` | `fc30eae327efbf` |
| `nonml_atr_vol_targeting_overlay_backtest.py` | idempotent | `30af1cd7e10b20` | `30af1cd7e10b20` |
| `nonml_auto_loan_delinquency_overlay_backtest.py` | idempotent | `4275105876fdbd` | `4275105876fdbd` |
| `nonml_autocorrelation_regime_overlay_backtest.py` | idempotent | `45105a77653226` | `45105a77653226` |
| `nonml_backlog_figures_verification_backtest.py` | idempotent | `7be90fe842a42c` | `7be90fe842a42c` |
| `nonml_beta_dispersion_vol_targeting_overlay_backtest.py` | idempotent | `de20f0ef8233fc` | `de20f0ef8233fc` |
| `nonml_bitcoin_momentum_overlay_backtest.py` | idempotent | `a5e0eba7f846d5` | `a5e0eba7f846d5` |

## Les non idempotents — avec le diff qui le prouve

**Aucun.** Les scripts éprouvés rendent deux fois le même octet.

## L'échantillon pouvait-il seulement contenir le défaut ?

*Constat ajouté après mesure, et signalé comme tel.*

L'auto-inclusion — **seul** mécanisme observé (#463, #468) — suppose
qu'un script **énumère** `results/`. Sinon il ne peut pas se compter.

- scripts de l'échantillon **structurellement capables** du défaut : **0 / 10**

> **Aucun.** La règle alphabétique a sélectionné dix scripts de
> **stratégie**, qui lisent des données de marché et n'inspectent
> jamais le dépôt. **Ils ne pouvaient pas porter le défaut cherché.**

**Ce 0/10 est donc encore moins informatif que la réserve du
pré-enregistrement ne le disait.** Celle-ci parlait d'un échantillon
trop petit ; il faut ajouter qu'il est **hors sujet**. Les deux
défauts connus vivent dans les scripts qui inspectent le dépôt, et
l'échantillon n'en contient aucun.

> **Ma règle d'échantillonnage était mal conçue** : déterministe et
> annoncée d'avance, donc honnête, mais aveugle à la seule
> caractéristique qui rendait un script pertinent.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 1 non idempotent | ≥ 1 | 0 | **réfutée** |
| ≥ 8 tiennent dans le budget | ≥ 8 | 10 | **vérifiée** |
| tout défaut trouvé est une auto-inclusion | — | *sans objet* | *non testable* |

**La prédiction 1 est réfutée, et le pré-enregistrement interdit d'en
tirer que le dépôt est sain.** Dix scripts sur **296** non éprouvés,
c'est **3,4 %** du reste : ne rien trouver dans un si petit lot est
**parfaitement compatible** avec le taux de ~8 % observé jusqu'ici.

> C'est le genre de résultat qu'il serait facile de présenter comme
> rassurant. Il ne l'est pas : il est **sans information**.

## L'effet de bord

La restauration a lieu **après la dernière exécution** — le #468 avait
annoncé « 0 résidu » **sur un arbre sale** pour avoir inversé cet ordre.

- résidus sous `results/` : **0**

**Aucun rapport régénéré n'est committé.**

## Critères de succès

1. **10/10** scripts traités — **OUI**.
2. Les deux empreintes publiées — **OUI**.
3. Tout non idempotent publié avec son diff — **OUI**.
4. Arbre propre après restauration finale — **OUI**.

**PASS** — le critère porte sur le
**procédé** : un lot qui ne trouve rien et le montre proprement réussit.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).