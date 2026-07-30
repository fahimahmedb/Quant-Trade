# Pré-enregistrement — Lecture DSR alternative du #131 avec n_trials par FAMILLE (informatif)

**Committé AVANT tout calcul.** Cycle #133 du backlog non-ML. Analyse
méthodologique, PAS un nouveau backtest — répond à la question laissée
ouverte au #116 et rappelée au #132 : le DSR officiel (Règle 9e) compte
`n_trials` = nombre BRUT de lignes du backlog (125 pour le #131). Cette
analyse calcule, à titre PUREMENT INFORMATIF, ce que donnerait le DSR
du #131 si `n_trials` comptait le nombre de FAMILLES de mécanismes
DISTINCTES plutôt que le nombre de lignes.

## Ce que cette analyse NE fait PAS

Ne change AUCUN verdict Règle 9 déjà rendu (le #131 reste FAIL sous la
convention officielle n_trials=125). N'adopte PAS unilatéralement cette
convention alternative pour les cycles futurs — reste une information
soumise à l'utilisateur, comme annoncé explicitement au #116 et au
§3 du #132.

## Méthode (fixée ici, avant tout calcul — règle de classification MÉCANIQUE, pas ajustée après avoir vu le résultat)

1. Extraction de toutes les lignes `| N | description | ... |` du
   tableau `NONML_STRATEGY_BACKLOG.md` pour N=0 à N=131 (tout ce qui
   précède le cycle #131 inclus — le #131 est le candidat évalué, pas
   compté dans son propre n_trials, cohérent avec la convention
   officielle qui utilisait n_trials=125 = taille du backlog AVANT le
   #131).
2. Classification de chaque ligne dans EXACTEMENT une famille parmi 8,
   par une règle de mots-clés FIXE appliquée dans cet ORDRE de
   priorité (le premier mot-clé trouvé dans la description détermine
   la famille — ordre choisi pour éviter qu'un mot générique comme
   "combiner" n'écrase les familles plus spécifiques) :
   1. `evenementiel_fondamental` : PEAD, surprise de résultats
   2. `macro_externe` : pente des taux, courbe des taux, T10Y2Y, VIX, macro
   3. `volatilite_autoreferentielle` : vol-targeting, vol réalisée, vol cible,
      GARCH, EWMA, Parkinson, vol-of-vol, kurtosis, skewness de l'indice,
      autocorrélation, Sharpe glissant, streak, régime de vol, range
      intra-séance, défensif Calmar, rebalancement hebdomadaire
   4. `breadth_dispersion_titre` : breadth, dispersion, corrélation moyenne,
      spread de rendement décile, drawdown profond, concentration du
      marché, petites capitalisations, position moyenne dans le range,
      beta glissant
   5. `momentum_tendance` : momentum, SMA, golden cross, MACD, Donchian,
      52-semaines, 52 semaines, tendance, plus haut, plus bas, low-volatility
   6. `calendaire_saisonnier` : tournant de mois, turn-of-month, jour-de-semaine,
      Halloween, Sell in May, Santa Claus, jour férié, window dressing,
      trimestre, janvier, cycle électoral, triple witching, weekend,
      fin de semaine, lundi
   7. `choc_microstructure` : reversal, pullback, rebond post-drawdown, gap
      d'ouverture, faux breakout, faux breakdown, overnight, intraday,
      spillover, lead-lag, pause de marché
   8. `ensembles_combinaisons` : ensemble/vote, moyenne de deux moteurs,
      moyenne de deux expositions, vote majoritaire
   9. (résiduel) `autre` : tout le reste (ex. #10 buy&hold levé simple)
3. Compte le nombre de familles DISTINCTES effectivement peuplées
   parmi les 132 lignes (0 à 131) → `n_trials_famille`.
4. Recalcule le DSR du #131 (même `var_trials`, même méthode que
   `nonml_pass_validation_battery.py`) avec `n_trials = n_trials_famille`
   au lieu de 125, et rapporte le résultat CÔTE À CÔTE avec le DSR
   officiel — sans remplacer ce dernier.

## Limite reconnue explicitement

Toute règle de classification par mots-clés est arbitraire dans ses
frontières exactes (une ligne "combiner momentum + vol-targeting"
pourrait légitimement appartenir à deux familles). La règle ci-dessus
est fixée AVANT calcul précisément pour éviter d'ajuster les frontières
après avoir vu si le résultat DSR devient favorable ou non — mais elle
reste UNE partition parmi plusieurs défendables, pas LA réponse
définitive à la question ouverte du #116.

## Anti-cheat

Règle de classification et méthode écrites dans ce fichier avant toute
exécution du script `nonml_dsr_family_ntrials_reading.py`.
