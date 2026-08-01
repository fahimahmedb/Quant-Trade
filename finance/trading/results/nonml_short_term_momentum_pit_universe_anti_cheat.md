# Vérification anti-cheat — short_term_momentum_pit_universe

- **[OK]** Pré-enregistrement committé (premier commit à 1785547712).
- **[INFO]** Résultat pas encore committé — vérification différée.
- **[OK]** Aucun motif de recherche de paramètres ni de dépendance ML détecté.

**Verdict : CONFORME** (0 échec(s) sur 3 vérifications).

## Complément manuel (Règle 5)

Le fichier de résultat de ce cycle s'appelle
`results/nonml_short_term_momentum_result_pit_universe.md` (suffixe `_pit_universe`
pour ne pas écraser le résultat d'origine du #14), et non
`nonml_short_term_momentum_pit_universe_result.md` que cherche le script
générique — d'où le statut `INFO`. Vérification faite à la main :

- PREREG `PREREG_short_term_momentum_pit_universe.md` : premier commit `36cffce`,
  timestamp 1785547712 — **antérieur à toute exécution** du mode `--pit`.
- Aucun nouveau fetch de données : prix (`data/pead/prices_pit/`) et composition
  (`data/ndx100_history/`) étaient déjà committés au cycle #163.
- Non-régression : le mode par défaut de
  `scripts/nonml_short_term_momentum_backtest.py` reproduit
  `results/nonml_short_term_momentum_result.md` **bit-identique** (diff vide)
  après l'ajout des arguments optionnels.
- Motifs interdits (grille de seuils, `GridSearch`, `itertools.product`,
  `sklearn`) : aucun dans le script modifié.

**CONFORME.**
