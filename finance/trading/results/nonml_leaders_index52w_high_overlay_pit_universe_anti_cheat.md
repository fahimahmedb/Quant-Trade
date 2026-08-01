# Vérification anti-cheat — leaders_index52w_high_overlay_pit_universe

- **[OK]** Pré-enregistrement committé (premier commit à 1785546598).
- **[INFO]** Résultat pas encore committé — vérification différée.
- **[OK]** Aucun motif de recherche de paramètres ni de dépendance ML détecté.

**Verdict : CONFORME** (0 échec(s) sur 3 vérifications).

## Complément manuel (Règle 5 : un contrôle différé ne doit pas être absorbé en silence)

Le script générique cherche `results/nonml_<nom>_result.md`. Ce cycle ne
produit pas de fichier à ce nom (comme le #161 et le #162 : il ré-exécute une
batterie de validation, il n'introduit pas une nouvelle stratégie), d'où le
statut `INFO` ci-dessus. Les deux vérifications différées sont donc faites
explicitement ici, à la main.

### 1. Chronologie pré-enregistrement → résultat

| Fichier | Commits (timestamp Unix) |
|---|---|
| `PREREG_leaders_index52w_high_overlay_pit_universe.md` | `0f7cd8e` 1785546598 (01/08/2026 01:09:58 UTC), `c51ec31` 1785547468 |
| `results/nonml_leaders_index52w_high_overlay_pass_validation_battery_pit_universe.md` | `c51ec31` 1785547468 (01/08/2026 01:24:28 UTC) |

Le pré-enregistrement précède le premier résultat de ~15 minutes, et précède
également le fetch réseau des prix (`b54cb5e`). **CONFORME.**

**Divulgation explicite d'une modification du pré-enregistrement** : le PREREG
a reçu UNE modification après son premier commit (`0f7cd8e`) — la précision
sur la base de calcul du tercile, décrite dans le PREREG lui-même en note de
conformité. Elle a été rédigée pendant l'écriture du code, **avant la première
exécution de la batterie** (aucun chiffre de performance n'existait alors), et
ne modifie aucun paramètre. Un processus d'auto-commit du dépôt a regroupé
cette modification avec le commit des résultats (`c51ec31`), d'où deux
timestamps identiques ci-dessus : ce n'est PAS une réécriture postérieure au
résultat, mais c'est signalé ici plutôt que passé sous silence.

### 2. Absence de motif de recherche de paramètres, sur les scripts réellement utilisés

Les 4 motifs interdits (boucle sur grille de seuils, `GridSearch`,
`itertools.product`, `sklearn`) ont été cherchés manuellement dans les
5 scripts effectivement exécutés par ce cycle :

- `scripts/nonml_leaders_index52w_high_overlay_backtest.py` — aucun
- `scripts/nonml_leaders_index52w_high_overlay_pass_validation_battery.py` — aucun
- `scripts/ndx100_membership.py` — aucun
- `scripts/fetch_ndx100_pit_universe.py` — aucun
- `scripts/nonml_ndx100_universe_census.py` — aucun

**CONFORME.**

### 3. Non-régression du refactor (Règle 7)

`scripts/nonml_pit_universe_regression_check.py` vérifie que les nouveaux
arguments optionnels de `build_weights()` laissent le comportement d'origine
strictement inchangé : le #38 est reproduit à l'identique (Sharpe référence
+0,7837, candidat +1,4992, rendements +81,56 % / +508,27 %, 1144 séances
2022-01-03 → 2026-07-27). La batterie du #161 ré-exécutée ne diffère du
fichier committé que par `n_trials` (160 → 162, le backlog ayant grandi) :
DSR 0,730 → 0,729, Sharpe quotidien identique (+0,0944). **Aucune régression.**
