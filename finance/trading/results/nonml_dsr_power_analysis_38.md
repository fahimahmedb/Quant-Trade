# Analyse de puissance du DSR sur le #38 — jusqu'où l'historique peut-il aider ?

Complément du cycle #163 (aucun nouveau backtest, aucune nouvelle hypothèse, aucun paramètre touché). Produit par `scripts/nonml_dsr_power_analysis_38.py`, toutes les entrées recalculées depuis les poids réels de l'univers point-in-time.

## Entrées mesurées (univers point-in-time 2015-2026, cycle #163)

| Quantité | Valeur |
|---|---|
| Séances `n` | 2907 (2015-01-02 → 2026-07-27) |
| Sharpe quotidien | +0.0892 |
| Sharpe annualisé | +1.42 |
| Asymétrie / kurtosis excédentaire | -0.250 / +2.471 |
| `n_trials` (taille du backlog) | 163 |
| `var_trials` (journalière, 68 Sharpe extraits) | 8.0052e-04 |
| Seuil de sélection `SR0` | 0.0763 |
| `z` | +0.6828 |
| **DSR** | **0.753** |

## Combien d'observations faudrait-il pour franchir 0,95 ?

Le DSR vaut `Phi(z)` et, à edge journalier / asymétrie / kurtosis / `SR0` constants, `z` croît exactement en `sqrt(n-1)`. Le `n` requis pour `z = 1.6449` (soit DSR = 0,95) se résout donc directement :

    n = 1 + (n_actuel - 1) x (z_cible / z_actuel)^2
      = 1 + (2907 - 1) x (1.6449 / 0.6828)^2
      ≈ **16,865 séances**, soit environ **67 ans** de données quotidiennes.

## Vérification empirique de la trajectoire

| Cycle | Univers | Séances | z | DSR |
|---|---|---|---|---|
| #161 | liste 2026, 2022-2026 | 1144 | +0,61 | 0,730 |
| #163 | **point-in-time, 2015-2026** | 2907 | +0.68 | 0.753 |

Multiplier l'échantillon par 2.5 a rapporté +0.023 de DSR. La progression est conforme à la loi en `sqrt(n)` — donc parfaitement prévisible, et donc extrapolable.

## Conclusion — limite structurelle, pas un problème d'échantillon

Il faudrait ~67 ans de données quotidiennes pour que ce candidat franchisse le seuil de la Règle 9 **par accumulation d'historique seule**. C'est matériellement impossible :

- le NDX-100 n'existe que depuis 1985 (~41 ans) ;
- une composition point-in-time fiable et gratuite n'existe que depuis 2015   (recherche menée et documentée au cycle #163 : aucune source libre   antérieure trouvée) ;
- et `n_trials` **augmente** à chaque cycle du backlog, ce qui relève `SR0`   et éloigne la cible au fil du temps plutôt que de la rapprocher.

**La contrainte qui bloque le #38 n'est donc PAS la taille d'échantillon** (hypothèse formulée au #161, ici quantitativement infirmée) **mais le niveau de son Sharpe quotidien face au seuil de sélection imposé par 163 hypothèses testées.** Un edge de cette taille n'est pas distinguable du meilleur d'un tel nombre d'essais, quel que soit l'historique disponible.

**Recommandation : cet axe de recherche rétrospective est clos.** La seule voie de confirmation restante pour le #38 est un test **PROSPECTIF** (Règle 8 : validation en avant sur définition figée, plusieurs mois, sans aucune modification en cours de route), pas une nouvelle tentative d'extension de données historiques. Le résultat du #163 (DSR = 0.753, univers point-in-time réel, biais du survivant corrigé et mesuré) reste la **meilleure preuve rétrospective** obtenue sur ce candidat, et le verdict final de cet axe sauf donnée nouvelle qui changerait la donne.

