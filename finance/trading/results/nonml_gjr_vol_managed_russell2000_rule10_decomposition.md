# Règle 10 — décomposition portage / effet-prix, Russell 2000 (cycle #166, volatility-managed GJR-t)

Engagement pré-enregistré, exécuté parce que ce marché est PASS de niveau 1. **La série de positions n'est pas modifiée** : seules trois comptabilisations de la fraction non investie (ou empruntée) sont comparées.

Fenêtre commune Russell 2000 ∩ DGS3MO : **9030 séances**, 30/08/1990 → 13/07/2026.
Taux 3 mois moyen sur la fenêtre : **2.71 %** annualisé. Exposition sous 1,0x : 34.2 % du temps ; exposition moyenne 1.251x.

## Résultats

| Comptabilisation | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH |
|---|---|---|---|---|---|
| Buy & Hold (référence) | +0.388 | +788.1% | -59.9% | — | — |
| A. 0 % / 0 % (pré-enregistré, verdict committé) | +0.435 | +1029.9% | -48.9% | OUI | OUI |
| B. DGS3MO des deux côtés (comptabilisation correcte) | +0.385 | +684.1% | -48.5% | non | non |
| C. DGS3MO côté cash seulement (borne haute) | +0.443 | +1097.2% | -47.9% | OUI | OUI |

## Contribution du portage (part du résultat qui vient du taux, pas du signal)

- Somme des rendements log de la variante A (signal seul) : +316.6 points.
- Terme de portage symétrique (B − A) : **-36.6 points** (-11.5 % du résultat de A).
- Terme de portage asymétrique (C − A, borne haute) : **+5.8 points** (+1.8 % du résultat de A).

## Lecture

**Le verdict PASS pré-enregistré (A) sur Russell 2000 NE SURVIT PAS à la comptabilisation économiquement correcte du portage (B).** Sous l'hypothèse 0 %/0 %, le mécanisme bat Buy & Hold (Sharpe et rendement) ; dès que le cash rapporte le taux réel et que le levier le paie (B), les deux jambes échouent (Sharpe +0.385 vs BH +0.388, rendement +684.1% vs BH +788.1%). C'est exactement le mécanisme identifié au #142 : une partie du gain pré-enregistré vient de l'hypothèse de taux irréaliste (0 % sur une exposition qui emprunte en moyenne 1.25x), pas uniquement du signal de vol prévue. **Verdict révisé, honnêtement : le PASS de niveau 1 sur ce marché ne tient pas sous une comptabilisation réaliste du financement — à traiter comme un FAIL économique tant que cette correction n'est pas neutralisée.**
