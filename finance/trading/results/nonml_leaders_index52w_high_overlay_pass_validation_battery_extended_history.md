# Batterie de validation renforcée (Règle 9) — leaders_index52w_high_overlay (cycle #38) — historique étendu (cycle #162)

Candidat : Leaders + overlay 52w-high indice ×2.0. Référence : portefeuille Leaders 1.0x (cycle #4), **PAS Buy&Hold** — même convention que le PREREG original du #38. Coût pré-enregistré 5 bps. 14009 séances (1970-12-31 → 2026-07-27). Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ.

**LIMITE MÉTHODOLOGIQUE MAJEURE, à lire avant toute interprétation** : l'univers de titres utilisé ici est la liste des membres du NDX-100 **de 2026** (`data/pead/ndx100_constituents.json`), appliquée telle quelle à un historique remontant jusqu'à 1970 pour les titres qui en disposent. Sur les décennies anciennes, ceci introduit un **biais du survivant sévère** : seuls les titres qui (a) existaient déjà ET (b) sont restés assez grands pour rester dans le NDX-100 en 2026 sont inclus — le portefeuille des années 1970-1990 ne peut matériellement contenir QUE de futurs géants technologiques déjà connus aujourd'hui, jamais les entreprises qui ont existé puis disparu/reculé. Ce biais s'atténue à mesure qu'on se rapproche de 2026 (univers de plus en plus complet et réaliste) mais reste présent à un degré inconnu sur toute la période. **Les rendements totaux astronomiques ci-dessous (§a) en sont la signature typique** — ce n'est PAS un résultat économiquement interprétable en niveau absolu. Les métriques les MOINS affectées par ce biais sont le SPA (teste un ordre relatif candidat/référence sur le MÊME univers biaisé des deux côtés) et le score par fold (qui montre COMMENT l'edge évolue dans le temps) ; le DSR reste, lui, informatif sur la significativité mais ne corrige PAS ce biais de sélection de l'univers. **Conclusion à ce cycle : ce test ne peut PAS confirmer ni réfuter proprement l'hypothèse du #162 (édge borné par l'échantillon vs favorable par chance) tant que l'univers n'est pas reconstruit avec la composition HISTORIQUE réelle du NDX-100 à chaque date (donnée non triviale à obtenir gratuitement, hors scope de ce cycle) — rapporté ici pour traçabilité complète (Règle 6), PAS comme un verdict fiable.** *(Corrigé au cycle #163 : la composition point-in-time réelle a finalement été trouvée et utilisée — voir `..._pit_universe.md`.)*

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | OK |
|---|---|---|---|---|---|
| 5 | +0.64 | +0.62 | +194040.3% | +32101.7% | OUI |
| 15 | +0.62 | +0.61 | +129581.8% | +29282.9% | OUI |
| 25 | +0.59 | +0.60 | +86506.0% | +26710.1% | non |

**ÉCHEC — tient jusqu'à 5x le coût nominal : NON.**

## b. Stress de crise (MDD candidat vs référence)

| Fenêtre | Séances | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 752 | -51.6% | -45.0% | non |
| Crise financière 2008 | 378 | -54.1% | -50.4% | non |
| Krach COVID | 62 | -37.1% | -32.6% | non |
| Resserrement 2022 | 251 | -29.2% | -25.9% | non |

**ÉCHEC — 4/4 fenêtres de crise couvertes par l'historique de prix titre-par-titre disponible.**

## c. Stabilité temporelle (4 folds non chevauchants + embargo 5j)

| Fold | Séances | Période | Sharpe candidat | Sharpe référence | Candidat > référence |
|---|---|---|---|---|---|
| 1 | 3502 | 12/1970→11/1984 | +0.44 | +0.44 | non |
| 2 | 3497 | 11/1984→09/1998 | +0.88 | +0.83 | OUI |
| 3 | 3497 | 09/1998→08/2012 | +0.47 | +0.42 | OUI |
| 4 | 3498 | 08/2012→07/2026 | +0.77 | +0.81 | non |

**ÉCHEC — 2/4 folds battus (majorité requise).**

## d. SPA de Hansen à 1 candidat contre la référence

t_SPA = 3.528, **p = 0.0006** (bootstrap stationnaire, H0 : la référence Leaders 1.0x n'est battue par aucun candidat).

**OK — seuil p < 0,05.**

## e. DSR avec n_trials = taille du backlog AVANT ce cycle (jamais 1)

n_trials=266 (backlog avant ce cycle), var(SR essais) extraite sur 101 Sharpe du backlog = 1.5414e-01 (annualisée) → 6.1165e-04 (journalière). Sharpe quotidien +0.0405, seuil SR₀ = 0.0707, z = -3.53, **DSR = 0.000**.

**ÉCHEC — seuil DSR > 0,95.**

## Verdict de la batterie

| Contrôle | Statut |
|---|---|
| a. stress de coûts ×3/×5 | ÉCHEC |
| b. stress de crise | ÉCHEC |
| c. stabilité temporelle | ÉCHEC |
| d. SPA 1 candidat | OK |
| e. DSR (n_trials=266) | ÉCHEC |

### PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE

Aucune notification Telegram n'est émise (réservée au PASS RENFORCÉ complet).
