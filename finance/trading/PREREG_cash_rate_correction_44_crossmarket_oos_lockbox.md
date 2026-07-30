# Pré-enregistrement — Verrou temporel OOS pur du #149 généralisé (S&P 500, Russell 2000)

**Committé AVANT tout calcul.** Cycle #158 du backlog non-ML. Applique
la **Règle 8** (verrou temporel) de `PROTOCOLE_ANTI_SNOOPING.md`,
comme au #122 (#115, NDX), #138 (#134, NDX) et #153 (#149, NDX) — cette
fois sur les versions S&P 500 et Russell 2000 du #149 (#151), jamais
testées en OOS pur.

## Hypothèse

Le #153 a montré que le #149 (NDX) NE TIENT PAS sur les 12 derniers
mois, avec un écart plus marqué que le #134. Ce cycle teste la MÊME
fenêtre verrouillée (proportionnellement, dernières 252 séances de
chaque artefact) sur les deux marchés généralisés, avec le MÊME
critère (Calmar), sans aucun paramètre retouché.

## Définition (fixée ici, avant tout calcul — identique en tout point au #153 sauf le marché)

- Sources : `results/nonml_cash_rate_correction_44_crossmarket_sp500_pnl.npz`
  et `..._russell2000_pnl.npz` (#151, déjà committés), AUCUN paramètre
  modifié.
- `LOCKBOX_DAYS = 252` (~12 mois de bourse), identique aux cycles
  précédents.
- Isole simplement les 252 dernières séances de chaque artefact déjà
  committé — pas de recalcul du mécanisme.
- Critère : Calmar overlay > Calmar Buy&Hold sur cette fenêtre,
  rapporté séparément pour les deux marchés.

## Ce que cette analyse NE fait PAS

Ne retune AUCUN paramètre même si le résultat déçoit. Ne change pas
les verdicts Règle 9 déjà rendus sur les échantillons complets.

## Anti-cheat

Analyse committée en un seul passage, fenêtre et critère fixés avant
tout calcul (identiques aux cycles précédents).
