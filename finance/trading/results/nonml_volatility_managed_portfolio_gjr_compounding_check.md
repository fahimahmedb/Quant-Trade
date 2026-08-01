# Complément d'audit — le verdict dépend-il de la convention de capitalisation ?

Contrôle écrit **après** avoir vu le résultat, et uniquement dans le sens qui peut l'affaiblir : la jambe « rendement » du critère renforcé est-elle un artefact de la façon dont le backlog capitalise les rendements ? Le verdict pré-enregistré du cycle reste celui de la convention 1 (celle de `nonml_pass_validation_battery.py` et des 164 cycles précédents) — ce tableau sert à en donner la marge réelle, pas à la remplacer.

| Arithmétique | Capital final candidat | Capital final Buy & Hold | Sharpe candidat | Sharpe BH | Rdt > BH |
|---|---|---|---|---|---|
| 1. Convention du projet — `cumprod(1 + pos·r_log)` | ×72.8 (+7179 %) | ×46.5 (+4553 %) | +0.666 | +0.521 | OUI |
| 2. Hybride log — `exp(Σ pos·r_log)` (INCORRECTE si pos ≠ 1) | ×156.6 (+15557 %) | ×167.5 (+16652 %) | +0.666 | +0.521 | **non** |
| 3. Arithmétique exacte — `cumprod(1 + pos·(e^r − 1))` | ×175.4 (+17439 %) | ×167.5 (+16652 %) | +0.782 | +0.650 | OUI |

MDD sous l'arithmétique exacte : candidat -56.5 % contre -82.9 % pour Buy & Hold (Sortino candidat +1.13).

## Lecture honnête

1. **Le sens du résultat ne change pas** sous la seule autre arithmétique défendable (la n° 3, exacte) : le candidat bat Buy & Hold sur les deux jambes, avec un Sharpe encore un peu meilleur (+0,78 contre +0,65).
2. **Mais l'ampleur du gain de rendement, elle, change beaucoup** : +58 % de capital final relatif sous la convention du projet, seulement **+4,7 %** sous l'arithmétique exacte. La marge réelle sur la jambe rendement est donc **mince**, et c'est ce chiffre-là qu'il faut retenir, pas le premier.
3. La convention n° 2 (hybride log) ferait basculer la jambe rendement en échec — mais elle est **mathématiquement fausse pour une exposition variable** (`ln(1 + pos·(e^r − 1)) ≠ pos·r`), elle n'est donc pas retenue ; elle est publiée pour que personne ne découvre ce chiffre plus tard en croyant à une dissimulation.
4. **Portée au-delà de ce cycle** : la convention n° 1 avantage mécaniquement toute stratégie MOINS volatile que son benchmark (l'écart `prod(1+x)` vs `exp(Σx)` croît avec la variance de `x`). Les 164 cycles du backlog utilisent tous cette convention, appliquée identiquement au candidat et au benchmark ; ce constat ne réécrit aucun verdict passé mais mérite d'être connu — il est signalé ici, pas transformé en campagne de révision rétroactive (même principe que la Règle 10, portée prospective).
