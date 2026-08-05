# Pré-enregistrement — Ré-exécution du #14 (momentum court terme) sur l'univers point-in-time AVEC exécution causale corrigée

**Committé AVANT tout calcul.** Cycle #252 du backlog non-ML. Comble un
écart explicitement identifié dans le backlog lui-même.

## Contexte et écart identifié

Le #164 a ré-exécuté le #14 (momentum court terme "Winners") sur
l'univers **point-in-time** réel du NDX-100 et obtenu **PASS MAINTENU**
(Sharpe +1,85, rendement +8303%). Mais ce calcul a été committé
(`ade6b61`) **AVANT** la correction du bug d'exécution "même barre"
(`bd5ef75`, qui rend `causal=True` par défaut dans
`nonml_short_term_momentum_backtest.py`) — vérifié par `git log`, ordre
chronologique confirmé. Le résultat PIT actuellement committé
(`results/nonml_short_term_momentum_result_pit_universe.md`) est donc la
version **PRÉ-correction** (exécution "même barre", fuite d'un jour).

Les cycles #42 et #51 (dérivés du #14) affirment, SANS l'avoir
explicitement recalculé eux-mêmes, que "**le #14 ... est FAIL sur
l'univers point-in-time 2015-2026**" une fois la correction causale
appliquée — une **inférence non vérifiée empiriquement**, jamais
recalculée pour #14 lui-même avec les DEUX corrections combinées (PIT +
causal). Ce cycle comble cet écart : recalculer réellement le #14 avec
les deux corrections simultanément, au lieu de se fier à l'inférence.

## Hypothèse testée

Le PASS niveau 1 du #14 sur l'univers point-in-time (#164) survit-il à
la correction du bug d'exécution "même barre" (#166/#167) ?

## Méthode (déclarée avant calcul, réutilisation stricte, Règle 7)

- Ré-exécution de `python3 scripts/nonml_short_term_momentum_backtest.py
  --pit` **tel quel, sans aucune modification du script** — le flag
  `--pit` était déjà utilisé au #164, le paramètre `causal=True` est
  désormais la valeur par défaut de `main()` depuis `bd5ef75`, donc
  cette invocation applique automatiquement les deux corrections.
- Aucun paramètre du #14 ne change (SIGNAL_WINDOW=5, REBAL_EVERY=5,
  TERCILE=1/3, coût 5 bps, univers PIT 2015-2026).
- Non-régression vérifiée au préalable : re-confirmer que le mode
  `causal=False` (conservé pour audit) reproduit bit-identique le
  résultat déjà committé au #164, avant de lire le résultat `causal=True`.

## Critère de succès (n_trials=1)

PASS niveau 1 si Sharpe ET rendement de "Winners PIT causal" dépassent
la référence équipondérée PIT causale (même critère renforcé que tout
le backlog). Un résultat FAIL confirmerait l'inférence des #42/#51 avec
un chiffre réel plutôt qu'une extrapolation.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. L'inférence des #42/#51 est probablement correcte (la correction
   causale a déjà fait basculer #38/#14/#4 en FAIL sur l'univers
   d'origine) — un FAIL ici est le scénario le plus probable, à
   documenter comme confirmation plutôt que découverte surprenante.
2. Il est possible, bien que moins probable, que la combinaison avec
   l'univers PIT (référence elle-même dégradée, cf. #164) atténue
   suffisamment l'écart relatif pour que le PASS survive malgré la
   perte causale — serait alors une découverte réellement nouvelle,
   contredisant l'inférence non vérifiée des #42/#51.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Aucun script nouveau — réutilise
`scripts/nonml_short_term_momentum_backtest.py --pit` sans modification.
Anti-cheat : non-régression du mode `causal=False` vérifiée avant lecture
du résultat `causal=True`, documentée dans le résultat lui-même.
