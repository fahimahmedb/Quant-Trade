# Pré-enregistrement — Force relative Russell 2000 vs S&P 500 (small-cap vs large-cap), overlay défensif

**Committé AVANT tout calcul.** Cycle #192 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

La sous-performance des small-caps (Russell 2000) par rapport aux
large-caps (S&P 500) est une anomalie de "breadth" documentée par les
techniciens de marché : les small-caps, plus sensibles au crédit et à la
liquidité domestique, tendent à décrocher AVANT le marché large en
phase de rotation défensive précoce (les investisseurs réduisent le
risque en sortant d'abord des actifs les plus fragiles). Distinct du
#123 (breadth des PETITES capitalisations PROXY, approximée par le prix
et la volatilité idiosyncratique DE TITRES INTRA-NDX-100 — pas un vrai
indice small-cap, limite reconnue explicitement dans ce cycle) : ici le
signal utilise deux VRAIS indices déjà en local (Russell 2000, S&P 500),
sans proxy. Distinct aussi de la confirmation multi-marché du #52/#57
(NDX ET Russell 2000 SIMULTANÉMENT en tendance haussière, signal
binaire de CONFIRMATION servant à LEVER) : ici le signal est l'ÉCART de
performance RELATIVE entre les deux indices sur une fenêtre glissante,
jamais testé sous cette forme.

## 2. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — y compris
Russell 2000 et S&P 500 eux-mêmes : le signal n'est pas le rendement
ABSOLU de l'un des deux (ce qui serait tautologique), mais leur ÉCART
RELATIF, une information distincte même appliquée à l'un des deux
constituants (cohérent avec le #52/#57 qui appliquaient déjà un signal
dérivé de Russell 2000 sur NDX, et avec la pratique déjà établie de ce
backlog d'appliquer un signal macro identique aux 5 marchés).

## 3. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Rendement glissant 21j (mois calendaire, fenêtre déjà réutilisée dans
  ce backlog — ex. #170) de chaque indice : `ret21_X(t) =
  log(close_X(t)/close_X(t-21))`.
- `RS(t) = ret21_Russell(t) - ret21_SP500(t)` (force relative, positive
  si Russell 2000 SURPERFORME S&P 500 sur le mois écoulé).
- Alignement causal sur le marché cible : `ffill` (calendrier du marché
  cible, gère les jours fériés distincts p.ex. pour le DAX) puis
  `shift(1)` — **technique identique à `load_rate_lag()`** déjà utilisée
  aux #175/#178/#186/#187/#191 pour les séries FRED, appliquée ici à un
  signal dérivé de deux séries OHLC au lieu d'une série de taux, Règle 7.
- Seuil : **tercile EXPANDING** de `RS_lag(t)` (technique établie aux
  #169/#177/#183/#191, aucune fenêtre fixe à choisir).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique** des
  #175/#176/#178/#186/#187/#191) si `RS_lag(t)` est dans son tercile
  expanding le PLUS BAS (Russell 2000 sous-performe nettement S&P 500 —
  signal de rotation défensive précoce), `1,0x` sinon. **Jamais de
  levier** — design purement défensif, cohérent avec la leçon des
  #175/#186 (le levier bidirectionnel sur un signal macro externe est
  contre-productif) et avec le #191 (même design, MDD amélioré). Coûts
  5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que les #175/#178/#186/#187/#191)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, une fenêtre de
rendement réutilisée, un critère multi-marché figé, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le signal de breadth small-cap/large-cap est documenté comme un
   indicateur AVANT-COUREUR, mais son délai d'anticipation exact n'est
   pas garanti — comme pour l'inversion de courbe (#187), le signal
   pourrait arriver trop tôt ou trop tard pour un mécanisme statique
   sans paramètre de délai.
2. Comme aux #175/#178/#186/#187/#191, un design purement défensif sans
   levier compensatoire limite structurellement le rendement total.
3. Appliquer le signal à Russell 2000 et S&P 500 eux-mêmes pourrait
   introduire une forme de circularité partielle (bien que le signal
   soit RELATIF, pas absolu) — signalé comme limite méthodologique à
   l'avance, pas comme correction post-hoc.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
