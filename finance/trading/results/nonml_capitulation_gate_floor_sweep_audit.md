# Audit — balayage des portes de capitulation neutralisées par le plancher 1,0×

## 1. La détection sait-elle chercher ?

Un balayage qui ne trouve presque rien peut signifier qu'il n'y a presque rien,
ou qu'il ne sait pas chercher. Deux contrôles séparent les deux cas.

**Contrôle positif** — le cas établi au #410 doit être détecté :

- `nonml_weakness_breadth_vol_targeting_overlay_backtest.py` présent : **OUI**
- détecté comme portant la structure : **OUI**

**Contrôle négatif** — un overlay à exposition **constante** (`CAP` fixe, sans
vol-targeting) ne doit **pas** être signalé :

- `nonml_leaders_trend_union_overlay_backtest.py` présent : **OUI**
- signalé à tort : **NON**

**CONFORME — la détection trouve ce qu elle doit trouver et rien de plus.**

## 2. Confirmation par lecture du « PASS vide » signalé

Critère 2 du pré-enregistrement : aucun candidat n'est déclaré vide sur la seule
foi du compteur.

### `weakness_breadth_vol_targeting_overlay_pit_universe`

- activation mesurée : **0.00 %**
- verdict au rapport : **PASS**
- le rapport porte-t-il déjà l'avertissement « NON INFORMATIF » : **OUI**

**Confirmé, et déjà documenté.** C'est le cas établi au #410, dont le
rapport porte l'étiquette depuis ce cycle-là. Le balayage ne découvre
donc rien de neuf ici — il **retrouve** le cas connu, ce qui est la
condition pour que son silence sur les autres ait un sens.

## 3. Exposition restante — ce que ce cycle ne peut pas lever

- candidats détectés mais non mesurés : **29**
- dont portant un **PASS** : **10**

- `dispersion_trend_vol_targeting_overlay`
- `momentum_breadth_vol_targeting_overlay`
- `momentum_dispersion_trend_and_overlay`
- `multimarket_breadth_vol_targeting_overlay`
- `net_breadth_vol_targeting_overlay`
- `santa_vol_targeting_overlay`
- `sma200_breadth_vol_targeting_overlay`
- `sma200_momentum_breadth_and_overlay`
- `weakness_breadth_vol_targeting_overlay`
- `winners_trend_vol_targeting_overlay`

Ces candidats ont la structure à risque et un verdict positif, mais aucun `.npz`
ne permet de mesurer leur activation. **Le diagnostic les laisse en suspens** :
c'est la mesure exacte de ce que la lacune du #406 coûte, et l'argument le plus
concret en faveur de la sauvegarde systématique du P&L.

## 4. Ce que ce balayage corrige dans la formulation du #410

Le #410 concluait que la structure valait « pour **toute** variante combinant une
porte de capitulation avec un vol-targeting à plancher 1,0× ». Le balayage
permet de préciser cette phrase.

- candidats portant la structure `clip(…, 1.0, …)` : **62**
- parmi les **33** mesurés, activation normale (≥ 2 %) : **32**
- activation médiane des mesurés : **31.1 %**

**La structure seule ne neutralise rien.** Le plancher à 1,0× est très répandu
dans le dépôt et, dans la quasi-totalité des cas mesurés, l'overlay s'active
normalement. Ce qui neutralise, c'est la **conjonction** du plancher avec une
porte qui s'ouvre précisément quand la volatilité est haute — la faiblesse.

La formulation du #410 était donc trop large : elle laissait entendre qu'un
montage fréquent était défectueux, alors que le défaut tient à un type de porte
particulier. Correction consignée ici plutôt que laissée à l'interprétation.

## Verdict de l'audit

**MÉTHODE VALIDE.** Contrôles positif et négatif conformes : le balayage
retrouve le cas connu et ne signale pas de faux positif évident.

Résultat : **1** candidat structurellement inactif parmi les
33 mesurés, déjà documenté. **10** candidats
à PASS restent hors de portée faute de `.npz` — c'est la limite du cycle, et
elle est chiffrée plutôt que passée sous silence.
