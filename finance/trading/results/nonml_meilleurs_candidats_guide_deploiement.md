# Guide de formalisation — meilleurs candidats du backlog pour un déploiement prudent

Synthèse décisionnelle (pas un backtest). 269 hypothèses testées à ce
jour (**mise à jour v2, cycle #263** — v1 au #251/#252 s'arrêtait à
251), **0 PASS RENFORCÉ Règle 9 sans exception** — aucun candidat de ce
document n'est un edge "prouvé" au sens strict des propres critères du
backlog. Ce qui suit classe les MOINS mauvais candidats par usage, avec
leurs limites explicites, pour éclairer une décision éventuelle plutôt
que la prendre.

**MISE À JOUR v2 (cycle #263)** : ajout du Candidat C (v2) — #261 (tilt
Amihud illiquidité), obtenu depuis la v1 via une catégorie de données
entièrement nouvelle (volume, #258-262). Sans lien avec l'ancien
Candidat C retiré au #252 (mécanisme totalement différent : prime de
liquidité, pas momentum/survivorship) — voir la correction déjà en place
ci-dessous, conservée inchangée.

**CORRECTION (cycle #252, committée le lendemain de la première version
de ce document)** : le Candidat C ci-dessous (#38/#163) citait un DSR
"record" de 0,754 comme le meilleur résultat du backlog. Le #252 a
découvert que ce chiffre (et le Sharpe corrigé +1,42 qui l'accompagnait)
provenait d'un calcul committé AVANT la correction du bug d'exécution
"même barre" (#166/#167) — le même bug qui avait déjà fait basculer le
#38 lui-même en FAIL sur son univers d'origine. Une fois recalculé avec
l'exécution causale (aujourd'hui la valeur par défaut du script), le
#38 sur univers point-in-time s'effondre à **0/5 sur toute la ligne**
(DSR 0,011, SPA p=0,154). **Le Candidat C n'est PLUS un candidat valable
— section conservée ci-dessous barrée, à titre d'archive honnête, et
remplacée par le constat réel.** Voir la mise à jour du backlog, cycle
#252.

## Candidat A — Risk management / réduction de drawdown : #149

`position = clip(15% / vol_réalisée, 0, CAP)` avec correction du taux de
financement réaliste (Règle 10, DGS3MO appliqué des deux côtés).

- **Meilleur résultat BRUT de tout le backlog** : Sharpe +0,53→+0,84,
  **MDD -82,9%→-37,9%** (réduction de 45 points).
- Règle 9 : **4/5** — coûts, crise et stabilité temporelle (4/4 folds)
  OK ; SPA (p=1,00) et DSR (0,0122) en échec.
- **Lecture honnête** : le SPA à 1,00 signifie que l'edge de RENDEMENT
  n'est pas statistiquement distinguable du hasard — tout l'apport
  visible vient de la réduction de variance/drawdown, pas d'un
  sur-rendement journalier. C'est cohérent avec son usage recommandé :
  un outil de gestion du risque de queue (VaR/ES, MDD), PAS un générateur
  de rendement excédentaire.

## Candidat B — Meilleure significativité statistique récente : #237/#238 (ν Student-t)

Porte `ν(t) glissant (MLE Student-t) >= médiane 252j` sur le mécanisme
#46 standard (vol réalisée 20j, cible 20%, cap 2,0x).

- PASS niveau 1 4/5 (NDX Sharpe +0,49→+0,54).
- Règle 9 (#238) : **4/5**, l'un des meilleurs scores de tout le
  backlog — coûts OK à 5x, crise OK (4/4), stabilité OK (3/4 folds),
  **SPA OK (p=0,0022)** ; seul le DSR échoue (0,0001).
- **Limite majeure documentée** (#237, audit) : l'estimateur ν sous-jacent
  est **numériquement non identifiable** sur les fenêtres proches de la
  gaussienne (MLE non contraint divergeant vers des valeurs arbitraires,
  jusqu'à ~1,5e10 sur S&P 500) — la Règle 9 reste bonne malgré cette
  fragilité (la porte binaire n'est pas affectée dans la plupart des
  cas), mais un déploiement réel nécessiterait de borner ν
  explicitement, ce qui n'a PAS été fait ici (Règle 2 : aucune
  correction après résultat).
- Alternative proche : la conjonction ET avec la kurtosis (#240/#241)
  donne un profil quasiment identique (Règle 9 4/5, SPA p=0,0134,
  légèrement moins net) sans avantage net — pas recommandée comme
  substitut, seulement comme confirmation indépendante du signal.

## ~~Candidat C — Meilleur Sharpe historique corrigé (biais du survivant) : #38/#163~~ RETIRÉ (cycle #252)

~~Momentum, univers point-in-time réel du NDX-100 (couverture 87,6%).
Sharpe corrigé le plus élevé du backlog, DSR record à 0,754, SPA le
plus net jamais obtenu (t=7,637, p=0,0000).~~

**Ce chiffre était calculé avec l'exécution "même barre" (bug corrigé
au #166/#167, mais jamais réappliqué à ce calcul spécifique avant le
#252).** Recalculé avec l'exécution causale (script inchangé, simple
ré-exécution) : Sharpe candidat +0,47 contre référence +0,54 (candidat
SOUS la référence), **batterie Règle 9 0/5 sur toute la ligne** (coûts
ÉCHEC, crise ÉCHEC, stabilité 1/4 folds, SPA p=0,154, **DSR 0,011** —
au lieu du "record" 0,754). Un second bug a été trouvé et corrigé au
passage : le script produisait un texte narratif figé (écrit au moment
du #163) concaténé sans jamais être régénéré, créant un document
contradictoire une fois les chiffres corrigés. **Aucun candidat de
remplacement n'est proposé ici** pour cette catégorie ("meilleur Sharpe
historique corrigé") — voir le backlog, cycle #252, pour le détail
complet.

## Candidat C (v2, cycle #263) — Meilleur profil DSR/SPA du backlog : #261 (tilt Amihud illiquidité)

Tercile de titres NDX-100 LE PLUS illiquide (ILLIQ = |rendement|/volume-
dollars, moyenne glissante 126j, Amihud 2002), rebalancé mensuellement.
Première stratégie du guide construite sur une catégorie de données
entièrement nouvelle pour ce backlog (volume, jamais exploitée avant le
#258).

- PASS niveau 1 net : Sharpe +0,59→+0,84, rendement +70,0%→+142,8%,
  robustesse 5/5 plateau parfait (référence = Buy&Hold équipondéré, pas
  un mécanisme de vol-targeting comme A/B).
- Règle 9 (#262) : **4/5, ÉGALE LE MEILLEUR SCORE DE TOUT LE BACKLOG**
  (avec #209/#229) et **DSR=0,2731 — le plus élevé authentique de tout
  le backlog** (22× le Candidat A, 2700× le Candidat B). SPA OK
  (p=0,0034, meilleur que A à p=1,00, proche de B à p=0,0022). Coûts OK
  à 25 bps, crise OK (2022), stabilité OK (3/4 folds). Seul le DSR
  échoue, comme pour A et B.
- **Lecture honnête** : le mécanisme économique (prime de risque de
  liquidité) est distinct de A (vol-targeting défensif) et B (porte de
  régime de queue) — la persistance temporelle de l'illiquidité au sein
  d'un univers de grandes capitalisations explique à la fois la
  résistance aux coûts et la solidité relative du score Règle 9. Limite
  déclarée à l'avance (#261) : la variation d'illiquidité au sein du
  NDX-100 reste structurellement faible comparée aux études originales
  d'Amihud (univers complet, y compris micro-caps) — le mécanisme
  fonctionne ici mais sur une plage de variation étroite.

## Ce que les trois candidats (A, B, C v2) n'ont PAS en commun

Ils optimisent des objectifs différents et reposent sur des mécanismes
non redondants : A réduit la variance sans générer de rendement
excédentaire significatif (vol-targeting) ; B a une porte de régime de
queue (kurtosis/ν) avec un estimateur numériquement fragile ; C (v2)
est une prime de liquidité sur une catégorie de données inédite dans ce
backlog. **Aucune tentative de combinaison n'a été testée** (hors
scope, nécessiterait son propre PREREG et backtest dédiés). L'ancien
candidat C (#38/#163, momentum/survivorship) reste retiré depuis le
#252 (voir correction en tête de document) — le C (v2) n'a aucun lien
mécanique avec lui.

## Rappel du plafond structurel (déjà établi au #116, confirmé à la v4/v5)

À n_trials=269, le Sharpe annualisé nécessaire pour franchir DSR>0,95 est
supérieur à tous les repères académiques standards. Ni A (DSR 0,0122),
ni B (DSR 0,0001), ni **C v2 (DSR 0,2731 — le plus proche jamais obtenu,
mais encore à 3,5x sous le seuil)** n'en est proche — le plafond n'a
jamais été atteint sur l'ensemble du backlog. Le C (v2) rapproche
sensiblement la meilleure marge observée (précédent record authentique :
0,0210 au #201) sans la franchir, confirmant que le plafond résiste même
au meilleur candidat stock-selection découvert à ce jour. Ce document ne
prétend pas que cette situation change : il identifie les candidats
relativement les plus solides SOUS ce plafond, pour un usage prudent et
documenté (avant tout risk management, jamais comme signal de rendement
autonome sans garde-fous supplémentaires), pas des stratégies validées
au sens plein de la Règle 9.
