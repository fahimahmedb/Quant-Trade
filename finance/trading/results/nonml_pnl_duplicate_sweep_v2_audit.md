# Audit — second balayage des doublons de P&L

## 1. Couverture réelle

| | #406 | #418 |
|---|---|---|
| fichiers `*_pnl.npz` | 165 | **183** |
| entrées numérotées du backlog | 404 | **416** |
| proportion visible | 41 % | **44 %** |

La couverture progresse de deux points. Le balayage voit toujours **moins de la
moitié** du backlog : son silence ne vaut que pour ce qu'il voit, exactement
comme au #406.

## 2. L'angle mort du #406 est-il levé ?

Le #403 avait établi que `sma200_leaders_overlay` et
`leaders_trend_union_overlay` sont la **même stratégie**, sur univers d'origine
comme point-in-time. Le #406 ne pouvait pas le voir : le second n'avait pas de
`.npz`.

- `nonml_sma200_leaders_overlay_pnl.npz` présent : **OUI**
- `nonml_leaders_trend_union_overlay_pnl.npz` présent : **NON**

**ANGLE MORT NON LEVÉ.** Le cycle #416 a doté dix candidats d'un `.npz`, mais
`leaders_trend_union_overlay` n'en faisait pas partie — sa liste venait du
#415, qui ciblait les candidats à porte de capitulation, pas les doublons
connus.

**Conséquence, redite explicitement plutôt que laissée à la mémoire du
lecteur** : le résultat de ce balayage reste une **borne inférieure**, au même
titre que celui du #406. Le seul doublon établi avant tout balayage lui
échappe encore.

## 3. Le quasi-doublon signalé — confirmation par lecture

Paire signalée : `nonml_momentum_breadth_vol_targeting_overlay` / `nonml_sma200_momentum_breadth_and_overlay`, corrélation **0.99990654**.

Lecture des deux scripts :

- le second **importe la fonction de signal du premier** (`compute_momentum_breadth_series`) : **OUI**
- le second est décrit comme une **double porte AND** : **OUI**
- séances où les deux P&L diffèrent : **17** sur 1133

**Rejeté comme doublon, mais signalé comme paire emboîtée.** Le second candidat
est le **ET** de la porte du premier avec une seconde condition (breadth SMA200).
Ce n'est donc pas la même stratégie : l'ajout d'une condition ne peut que
restreindre l'ouverture de la porte. Mais sur ces données la seconde condition
ne mord presque jamais, d'où deux P&L quasi identiques.

**Conséquence pour le décompte d'essais** : ces deux PASS ne constituent pas
deux confirmations indépendantes — même constat qu'au #414 pour la paire
`momentum_decile_spread` / `momentum_dispersion`. Le seuil de 0,9999 les laisse
hors du décompte de doublons, et **il n'est pas ajusté** pour les y faire
entrer : le rejeter après avoir vu la donnée serait du retuning.

## 4. Corrélation de P&L des paires mesurées au #414

Mesure annoncée d'avance, publiée sans ajustement de seuil.

| Paire | Corrélation de P&L |
|---|---|
| `momentum_decile_spread_vol_targeting_overlay` / `momentum_dispersion_vol_targeting_overlay` | 0.999740 |
| `momentum_decile_spread_vol_targeting_overlay_pit_universe` / `momentum_dispersion_vol_targeting_overlay_pit_universe` | 0.996063 |

Le #414 mesurait **93,3 %** de décisions de porte identiques et une corrélation
de portes de **0,8679** pour la paire point-in-time. La corrélation des P&L est
plus élevée que celle des portes — attendu, puisque les deux stratégies
partagent la même jambe Buy & Hold la plupart du temps et ne divergent que
lorsque les portes diffèrent.

Ces paires restent **sous** le seuil de doublon et ne sont pas comptées comme
telles.

## Verdict de l'audit

Le décompte de doublons exacts est **inchangé depuis le #406** : deux groupes,
dont un rejeté par lecture comme alias de nommage. **1 essai surnuméraire**,
comme au #406.

Ce que le second passage apporte n'est donc pas un décompte différent, mais
**une paire emboîtée nouvellement visible** — rendue mesurable par les `.npz`
ajoutés au #416 — et la confirmation que l'angle mort du #406 persiste.
