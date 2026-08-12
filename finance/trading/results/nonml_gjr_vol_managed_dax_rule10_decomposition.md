# Règle 10 — décomposition portage / effet-prix, DAX (cycle #166, volatility-managed GJR-t)

Engagement pré-enregistré, exécuté parce que ce marché est PASS de niveau 1. **La série de positions n'est pas modifiée** : seules trois comptabilisations de la fraction non investie (ou empruntée) sont comparées.

Fenêtre commune DAX ∩ DGS3MO : **6025 séances**, 16/10/2002 → 10/07/2026.
Taux 3 mois moyen sur la fenêtre : **1.76 %** annualisé. Exposition sous 1,0x : 34.1 % du temps ; exposition moyenne 1.184x.

## Résultats

| Comptabilisation | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH |
|---|---|---|---|---|---|
| Buy & Hold (référence) | +0.415 | +721.9% | -54.8% | — | — |
| A. 0 % / 0 % (pré-enregistré, verdict committé) | +0.399 | +541.6% | -47.7% | non | non |
| B. DGS3MO des deux côtés (comptabilisation correcte) | +0.369 | +459.0% | -47.9% | non | non |
| C. DGS3MO côté cash seulement (borne haute) | +0.403 | +553.3% | -47.5% | non | non |

## Contribution du portage (part du résultat qui vient du taux, pas du signal)

- Somme des rendements log de la variante A (signal seul) : +185.9 points.
- Terme de portage symétrique (B − A) : **-13.8 points** (-7.4 % du résultat de A).
- Terme de portage asymétrique (C − A, borne haute) : **+1.8 points** (+1.0 % du résultat de A).

## Lecture

**Le verdict PASS pré-enregistré (A) sur DAX NE SURVIT PAS à la comptabilisation économiquement correcte du portage (B).** Sous l'hypothèse 0 %/0 %, le mécanisme bat Buy & Hold (Sharpe et rendement) ; dès que le cash rapporte le taux réel et que le levier le paie (B), les deux jambes échouent (Sharpe +0.369 vs BH +0.415, rendement +459.0% vs BH +721.9%). C'est exactement le mécanisme identifié au #142 : une partie du gain pré-enregistré vient de l'hypothèse de taux irréaliste (0 % sur une exposition qui emprunte en moyenne 1.18x), pas uniquement du signal de vol prévue. **Verdict révisé, honnêtement : le PASS de niveau 1 sur ce marché ne tient pas sous une comptabilisation réaliste du financement — à traiter comme un FAIL économique tant que cette correction n'est pas neutralisée.**
