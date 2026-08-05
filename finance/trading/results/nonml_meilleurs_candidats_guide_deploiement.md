# Guide de formalisation — meilleurs candidats du backlog pour un déploiement prudent

Synthèse décisionnelle (pas un backtest). 251 hypothèses testées à ce
jour, **0 PASS RENFORCÉ Règle 9 sans exception** — aucun candidat de ce
document n'est un edge "prouvé" au sens strict des propres critères du
backlog. Ce qui suit classe les MOINS mauvais candidats par usage, avec
leurs limites explicites, pour éclairer une décision éventuelle plutôt
que la prendre.

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

## Ce que les deux candidats restants (A, B) n'ont PAS en commun

Ils optimisent des objectifs différents et ne se combinent pas
trivialement : A réduit la variance sans generer de rendement excédentaire
significatif ; B a la meilleure significativité statistique mais un
estimateur numériquement fragile. **Aucune tentative de combinaison
n'a été testée dans ce cycle** (hors scope, nécessiterait son propre
PREREG et backtest dédiés). Le candidat C initialement proposé a été
retiré au #252 (voir correction en tête de document) — aucun candidat
de remplacement pour "meilleur Sharpe historique corrigé" n'est
identifié à ce stade.

## Rappel du plafond structurel (déjà établi au #116, confirmé à la v4)

À n_trials≈252, le Sharpe annualisé nécessaire pour franchir DSR>0,95 est
supérieur à tous les repères académiques standards. Ni A (DSR 0,0122) ni
B (DSR 0,0001) n'en est proche — le plafond n'a jamais été atteint sur
l'ensemble du backlog, et le retrait du candidat C (dont le DSR 0,754
était un artefact de bug, la vraie valeur étant 0,011) le confirme
d'autant plus fermement : aucun candidat du backlog, une fois les bugs
d'exécution correctement appliqués, ne s'approche du seuil. Ce document
ne prétend pas que cette situation change : il identifie les candidats
relativement les plus solides SOUS ce plafond, pour un usage prudent et
documenté (avant tout risk management, jamais comme signal de rendement
autonome sans garde-fous supplémentaires), pas des stratégies validées
au sens plein de la Règle 9.
