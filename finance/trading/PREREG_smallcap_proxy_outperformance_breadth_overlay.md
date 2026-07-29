# Pré-enregistrement — Overlay vol-targeting gaté par la breadth de surperformance des "petites capitalisations" (proxy volatilité idiosyncratique)

**Committé AVANT tout calcul.** Cycle #123 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Limite de données (déclarée AVANT tout calcul)

`data/pead/prices/*.json` ne contient QUE `ts` et `close` — aucune
donnée de capitalisation boursière ni de flottant. Un vrai split par
capitalisation est donc IMPOSSIBLE avec les données disponibles.
Conformément à la clause de repli déjà anticipée dans le backlog
("à défaut par la volatilité idiosyncratique"), ce cycle utilise la
volatilité idiosyncratique glissante comme PROXY de taille — fait
stylisé bien établi en finance (Fama & French 1992 et suite) : les
petites capitalisations ont une volatilité idiosyncratique
structurellement plus élevée que les grandes. Ce n'est PAS un test
direct de l'effet taille, mais un test de son proxy le plus proche
disponible avec ces données — limitation assumée explicitement, pas
présentée comme un vrai test taille/liquidité.

## Hypothèse

Signal jamais testé dans ce backlog (distinct de tous les signaux de
niveau/dispersion/vitesse déjà couverts) : une fraction élevée de titres
à forte volatilité idiosyncratique (proxy "petite capitalisation")
SURPERFORMANT le reste du marché signale un regain d'appétit pour le
risque (rotation vers les valeurs les plus spéculatives), régime
propice à amplifier l'exposition via le mécanisme hiérarchique déjà
validé.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 individuels, `data/pead/prices/*.json`
  (calendrier UNION des tickers, convention identique à #78/#89/#111).
- `IdioVol_60(t)` par titre = écart-type glissant (ddof=1) des
  rendements log quotidiens sur 60 séances (fenêtre pleine requise).
- Chaque jour, les titres éligibles (IdioVol calculable) sont classés
  par IdioVol décroissante ; la moitié SUPÉRIEURE = groupe "PETIT"
  (proxy petite capitalisation).
- `Mom_21(t)` par titre = rendement sur 21 séances glissantes
  (`close(t)/close(t-21) - 1`).
- `Breadth_Small(t)` = fraction des titres du groupe PETIT dont
  `Mom_21(t)` est SUPÉRIEUR à la MÉDIANE cross-sectionnelle de
  `Mom_21(t)` calculée sur TOUT l'univers éligible ce jour-là (petites
  capitalisations qui battent l'ensemble du marché, pas seulement leurs
  pairs "petites").
- Porte active si `Breadth_Small(t) ≥` sa médiane glissante 252j (même
  convention que le reste de la famille).
- Position : `clip(20%/vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, sinon 1.0x (mécanisme hiérarchique identique).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX (`nasdaq100_daily.txt`).
- Échantillon restreint à la période où le signal titre-par-titre est
  disponible (leçon #77/#89).

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1.

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

`scripts/nonml_pass_validation_battery.py smallcap_proxy_outperformance_
breadth_overlay`, n_trials=taille totale du backlog.

## Robustesse prévue (SI PASS niveau 1)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — IdioVol_60/Mom_21/le seuil
"moitié" ne sont PAS retunés.

## Anti-cheat

Ce fichier committé avant
`nonml_smallcap_proxy_outperformance_breadth_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py smallcap_proxy_outperformance_breadth_overlay`.
