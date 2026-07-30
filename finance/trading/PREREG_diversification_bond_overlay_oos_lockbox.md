# Pré-enregistrement — Verrou temporel OOS pur du #134 (12 derniers mois)

**Committé AVANT tout calcul.** Cycle #138 du backlog non-ML. Applique
la **Règle 8** (verrou temporel) de `PROTOCOLE_ANTI_SNOOPING.md`, comme
au cycle #122 pour le #115 — mais cette fois sur le #134 (nouveau
meilleur candidat, 4/5 Règle 9, qui a dépassé le #115 depuis).

## Hypothèse

Le #122 a montré que le #115 (défensif Calmar) ne tenait PAS sur les 12
derniers mois (régime haussier calme, sans crise) — résultat rapporté
honnêtement, sans retunage. Le #134 ajoute la diversification
obligataire au même squelette #115 : ce cycle teste si cette
amélioration change la lecture OOS pure sur la MÊME fenêtre verrouillée
(12 derniers mois), avec le MÊME critère (Calmar), sans aucun paramètre
retouché.

## Définition (fixée ici, avant tout calcul — identique en tout point au #122 sauf l'artefact source)

- Source : `results/nonml_defensive_diversification_bond_overlay_pnl.npz`
  (#134, déjà committé), AUCUN paramètre modifié.
- `LOCKBOX_DAYS = 252` (~12 mois de bourse), identique au #122.
- Isole simplement les 252 dernières séances de l'artefact déjà
  committé — pas de recalcul du mécanisme.
- Critère : Calmar overlay > Calmar Buy&Hold sur cette fenêtre
  (identique au #122, pas le critère standard Sharpe+rendement).

## Ce que cette analyse NE fait PAS

Ne retune AUCUN paramètre même si le résultat déçoit (Règle 8 :
"si le prospectif déçoit, le modèle est abandonné, jamais retouché").
Ne change pas le verdict Règle 9 déjà rendu sur l'échantillon complet
du #134 (FAIL, SPA/DSR).

## Anti-cheat

Analyse committée en un seul passage, fenêtre et critère fixés avant
tout calcul (identiques au #122, pas choisis après avoir vu un
résultat favorable ou défavorable).
