# Audit — correction de `n_trials` pour non-indépendance mesurée

## 1. La déduction est-elle appliquée ?

- `n_trials` publié par la batterie : **370**
- déduction : **2** entrée(s)

**CONFORME — 372 → 370, comme annoncé avant calcul.**

## 2. La déduction reste-t-elle dans son périmètre ?

Le pré-enregistrement limitait la déduction aux **identités mesurées**. Les
paires seulement voisines ou emboîtées devaient rester comptées.

Entrées déduites :

- `leaders_trend_union_overlay` (jumeau conservé : `sma200_leaders_overlay`, identité établie au #419)
- `leaders_trend_union_overlay_pit_universe` (jumeau conservé : `sma200_leaders_overlay_pit_universe`, identité établie au #403)

- paires voisines/emboîtées déduites à tort : **0**

**CONFORME — aucune paire de jugement n a été déduite.**

## 3. Effet mesuré

| Candidat | DSR avant (372) | DSR après (370) | Δ | Verdict e. |
|---|---|---|---|---|
| `market_concentration_vol_targeting_overlay_pit_universe` | 0.1781 | 0.1787 | +0.0006 | ÉCHEC |
| `momentum_dispersion_vol_targeting_overlay_pit_universe` | 0.1712 | 0.1718 | +0.0006 | ÉCHEC |
| `momentum_decile_spread_vol_targeting_overlay_pit_universe` | 0.1717 | 0.1722 | +0.0005 | ÉCHEC |

- verdicts modifiés par la correction : **0**

**Aucun verdict modifié.** L'écart de DSR est de l'ordre de +0,0005 — cinq
dix-millièmes, pour un seuil situé à 0,95 et des valeurs autour de 0,17.

**La dette portée trois fois était donc immatérielle.** C'est un résultat, et
il vaut d'être écrit : il aurait été plus confortable de la laisser ouverte
comme une réserve indéfinie sur la validité des DSR publiés. Elle est close,
et elle ne changeait rien.

## 4. Jusqu'où faudrait-il abaisser `n_trials` pour franchir le seuil ?

Contrôle destiné à empêcher qu'on espère un jour sauver un candidat en jouant
sur ce compte — moi compris.

Candidat au DSR le plus élevé des trois : `market_concentration_vol_targeting_overlay_pit_universe`.

- Sharpe journalier : **0.0535**, observations : **2645**
- `n_trials` maximal permettant DSR ≥ 0,95 : **3**

Un `n_trials` inférieur ou égal à **3** suffirait. À 370, on en est
loin, mais l'ordre de grandeur mérite d'être connu.

## Verdict de l'audit

**CONFORME.**
