# Règle 10 — décomposition portage / effet-prix, S&P 500 (cycle #166, volatility-managed GJR-t)

Engagement pré-enregistré, exécuté parce que ce marché est PASS de niveau 1. **La série de positions n'est pas modifiée** : seules trois comptabilisations de la fraction non investie (ou empruntée) sont comparées.

Fenêtre commune S&P 500 ∩ DGS3MO : **11304 séances**, 02/09/1981 → 13/07/2026.
Taux 3 mois moyen sur la fenêtre : **3.84 %** annualisé. Exposition sous 1,0x : 17.4 % du temps ; exposition moyenne 1.452x.

## Résultats

| Comptabilisation | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH |
|---|---|---|---|---|---|
| Buy & Hold (référence) | +0.509 | +6006.0% | -56.8% | — | — |
| A. 0 % / 0 % (pré-enregistré, verdict committé) | +0.580 | +17741.2% | -60.0% | OUI | OUI |
| B. DGS3MO des deux côtés (comptabilisation correcte) | +0.487 | +7638.9% | -60.0% | non | OUI |
| C. DGS3MO côté cash seulement (borne haute) | +0.585 | +18490.6% | -59.6% | OUI | OUI |

## Contribution du portage (part du résultat qui vient du taux, pas du signal)

- Somme des rendements log de la variante A (signal seul) : +518.4 points.
- Terme de portage symétrique (B − A) : **-83.5 points** (-16.1 % du résultat de A).
- Terme de portage asymétrique (C − A, borne haute) : **+4.1 points** (+0.8 % du résultat de A).

## Lecture

**Le verdict PASS pré-enregistré (A) sur S&P 500 NE SURVIT PAS à la comptabilisation économiquement correcte du portage (B).** Sous l'hypothèse 0 %/0 %, le mécanisme bat Buy & Hold (Sharpe et rendement) ; dès que le cash rapporte le taux réel et que le levier le paie (B), la jambe Sharpe échoue (Sharpe +0.487 vs BH +0.509, rendement +7638.9% vs BH +6006.0%). C'est exactement le mécanisme identifié au #142 : une partie du gain pré-enregistré vient de l'hypothèse de taux irréaliste (0 % sur une exposition qui emprunte en moyenne 1.45x), pas uniquement du signal de vol prévue. **Verdict révisé, honnêtement : le PASS de niveau 1 sur ce marché ne tient pas sous une comptabilisation réaliste du financement — à traiter comme un FAIL économique tant que cette correction n'est pas neutralisée.**
