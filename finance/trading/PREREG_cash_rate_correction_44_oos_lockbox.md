# Pré-enregistrement — Verrou temporel OOS pur du #149 (12 derniers mois)

**Committé AVANT tout calcul.** Cycle #153 du backlog non-ML. Applique
la **Règle 8** (verrou temporel) de `PROTOCOLE_ANTI_SNOOPING.md`,
comme au cycle #122 pour le #115 et au cycle #138 pour le #134 — cette
fois sur le #149 (nouveau meilleur candidat, 4/5 Règle 9, meilleur
résultat brut du backlog).

## Hypothèse

Le #138 a montré que le #134 (proche du #149) NE TIENT PAS sur les 12
derniers mois — régime haussier calme, sans crise, cohérent avec le
profil de couverture déjà documenté. Ce cycle teste la MÊME fenêtre
verrouillée sur le #149 (mécanisme plus agressivement défensif, cible
15% au lieu de 20%), avec le MÊME critère (Calmar), sans aucun
paramètre retouché.

## Définition (fixée ici, avant tout calcul — identique en tout point au #122/#138 sauf l'artefact source)

- Source : `results/nonml_cash_rate_correction_defensive_vol_
  targeting_44_pnl.npz` (#149, déjà committé), AUCUN paramètre modifié.
- `LOCKBOX_DAYS = 252` (~12 mois de bourse), identique au #122/#138.
- Isole simplement les 252 dernières séances de l'artefact déjà
  committé — pas de recalcul du mécanisme.
- Critère : Calmar overlay > Calmar Buy&Hold sur cette fenêtre
  (identique au #122/#138, pas le critère standard Sharpe+rendement
  utilisé pour le PASS niveau 1 initial du #149).

## Ce que cette analyse NE fait PAS

Ne retune AUCUN paramètre même si le résultat déçoit. Ne change pas le
verdict Règle 9 déjà rendu sur l'échantillon complet du #149 (FAIL,
SPA/DSR).

## Anti-cheat

Analyse committée en un seul passage, fenêtre et critère fixés avant
tout calcul (identiques au #122/#138).
