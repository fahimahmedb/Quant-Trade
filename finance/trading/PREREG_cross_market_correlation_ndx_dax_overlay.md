# Pré-enregistrement — Corrélation cross-marché NDX-DAX, overlay défensif

**Committé AVANT tout calcul.** Cycle #193 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

La littérature documente une hausse systématique de la corrélation entre
marchés internationaux en période de stress global ("correlation goes to
one in a crisis") — la perte de diversification géographique est
elle-même un signal de risque. Distinct du #90 (corrélation moyenne PAR
PAIRES entre les 100 titres INTRA-NDX-100, régime de co-mouvement AU
SEIN d'un seul marché) : ici la corrélation est mesurée ENTRE deux
INDICES ENTIERS de zones géographiques différentes (NDX/US, DAX/zone
euro), jamais testée sous cette forme dans ce backlog. Direction du
signal réutilisée à l'identique du #90 (corrélation ÉLEVÉE = défavorable,
corrélation FAIBLE = régime calme/diversifié), Règle 7 — pas un nouveau
choix arbitraire.

## 2. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — le signal de
corrélation globale NDX-DAX est appliqué de façon uniforme aux 5
marchés, comme les autres signaux macro-économiques externes de ce
backlog (#175/#178/#186/#187/#191/#192), pas seulement aux deux
constituants du signal.

## 3. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Corrélation glissante : `corr(t) = Pearson(rendements log NDX,
  rendements log DAX)` sur une fenêtre glissante de **60 jours,
  réutilisée à l'identique de la fenêtre de corrélation du #90** (aucun
  nouveau paramètre de fenêtre), calculée sur les dates communes aux
  deux séries.
- Alignement causal sur le marché cible : `ffill` (calendrier du marché
  cible) puis `shift(1)` — **technique identique à `load_rate_lag()`**
  déjà utilisée aux #175/#178/#186/#187/#191/#192, Règle 7.
- Seuil : **tercile EXPANDING** de `corr_lag(t)` (technique établie aux
  #169/#177/#183/#191/#192, aucune fenêtre fixe à choisir).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique** des
  #175/#176/#178/#186/#187/#191/#192) si `corr_lag(t)` est dans son
  tercile expanding le PLUS HAUT (corrélation NDX-DAX élevée — perte de
  diversification internationale, régime de stress global), `1,0x`
  sinon. **Jamais de levier** — design purement défensif, cohérent avec
  la leçon des #175/#186 et la pratique des #187/#191/#192. Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que les #175/#178/#186/#187/#191/#192)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, une fenêtre de
corrélation réutilisée, un critère multi-marché figé, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme au #90 (échec de justesse, informatif), le régime de
   corrélation pourrait être actif et informatif sans pour autant battre
   Buy & Hold — la corrélation cross-marché pourrait souffrir du même
   problème.
2. Comme aux #175/#178/#186/#187/#191/#192, un design purement défensif
   sans levier compensatoire limite structurellement le rendement total.
3. Le décalage horaire entre NDX (clôture US) et DAX (clôture zone euro,
   plusieurs heures avant l'ouverture US) pourrait introduire un biais
   de synchronisation dans le calcul de la corrélation glissante — limite
   méthodologique reconnue à l'avance (comme au #110, qui avait dû
   corriger une erreur de fuseau horaire), pas une correction post-hoc :
   la corrélation est calculée sur les rendements CLOTURE-À-CLOTURE des
   deux séries alignées par DATE calendaire commune, sans ajustement de
   fuseau horaire (limite documentée, pas un bug si le résultat est
   cohérent).
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
