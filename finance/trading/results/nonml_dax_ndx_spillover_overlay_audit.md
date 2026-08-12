# Audit adversarial — Spillover cross-marché DAX(t-1)->NDX

## 1. Recalcul indépendant de la porte (boucle Python explicite, sans pandas.reindex/shift)

| Date NDX (indice) | Concorde |
|---|---|
| 4100 | OUI |
| 4800 | OUI |
| 5500 | OUI |
| 6200 | OUI |
| 6900 | OUI |
| 7600 | OUI |
| 8300 | OUI |
| 9000 | OUI |
| 9700 | OUI |

**OK — porte confirmée par recalcul indépendant (9 dates).**

## 2. Test anti-lookahead (mutation des 20% de données DAX les plus récentes)

Écart de porte sur les séances antérieures à la mutation : 0
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Confirmation du bug de fuseau horaire initial (dax_ret(t) vs dax_ret(t-1))

Version buguée (dax_ret(t), chevauchement horaire) : rendement total = +2608267988002.0% (aberrant, confirme la fuite détectée au premier essai).
Version corrigée (dax_ret(t-1), committée comme résultat officiel) : rendement total = +9392.6% (plausible, cohérent avec les autres résultats du backlog).

**La version corrigée (t-1) est la seule utilisée pour le verdict PASS/FAIL officiel — cette section documente uniquement pourquoi la version initiale a été rejetée avant tout commit de résultat.**
