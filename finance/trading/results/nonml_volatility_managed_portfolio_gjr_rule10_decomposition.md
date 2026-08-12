# Règle 10 — décomposition portage / effet-prix (cycle #165, volatility-managed GJR-t)

Engagement pré-enregistré (§6 du PREREG), exécuté parce que le cycle est PASS de niveau 1. **La série de positions n'est pas modifiée** : seules trois comptabilisations de la fraction non investie (ou empruntée) sont comparées. Ce n'est ni un nouvel essai, ni une nouvelle hypothèse.

Fenêtre commune NDX ∩ DGS3MO : **9521 séances**, 21/09/1988 → 13/07/2026 (la série DGS3MO commence en 1981, elle couvre donc toute la fenêtre OOS).
Taux 3 mois moyen sur la fenêtre : **2.99 %** annualisé. Exposition sous 1,0x : 45.5 % du temps ; exposition moyenne 1.038x (donc la stratégie **emprunte** en moyenne, légèrement).

## Résultats

| Comptabilisation | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH |
|---|---|---|---|---|---|
| Buy & Hold (référence) | +0.520 | +16587.1% | -82.9% | — | — |
| A. 0 % / 0 % (pré-enregistré, verdict committé) | +0.665 | +15474.6% | -59.9% | OUI | non |
| B. DGS3MO des deux côtés (comptabilisation correcte) | +0.662 | +15137.1% | -57.6% | OUI | non |
| C. DGS3MO côté cash seulement (borne haute) | +0.685 | +17984.0% | -57.6% | OUI | OUI |

## Contribution du portage (part du résultat qui vient du taux, pas du signal)

- Somme des rendements log de la variante A (signal seul) : +504.8 points.
- Terme de portage symétrique (B − A) : **-2.2 points** (-0.4 % du résultat de A).
- Terme de portage asymétrique (C − A, borne haute) : **+14.9 points** (+3.0 % du résultat de A).

## Lecture

Le point à trancher, posé par le #142 : le résultat est-il un edge du mécanisme, ou l'artefact d'une hypothèse de taux irréaliste ? Ici la réponse est directement lisible — **le verdict pré-enregistré (A) ne doit rien au portage**, puisqu'il est rendu sous l'hypothèse 0 %. La comptabilisation correcte (B) est même **légèrement défavorable** au candidat (exposition moyenne > 1x ⇒ il paie plus de financement qu'il ne touche d'intérêts), ce qui est l'inverse exact de la situation du #134, où 86-89 % du gain venait du portage. La borne haute (C) montre l'ampleur maximale que pourrait prendre l'effet si l'on n'imputait aucun coût de financement — elle est publiée pour encadrer l'incertitude, pas pour être retenue.
