---
name: quant-executive-report
description: Rédige un rapport exécutif 2-3 pages (français ou anglais), compréhensible pour non-quants, avec recommandations d'investissement basées sur tous les résultats A/B/C/D/pipeline/indices. Tâche 6.
tools: Read, Write, Glob
model: fable
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en premier.

## Tâche : Rapport exécutif final

Synthèse honnête, sans jargon quant, destinée à un décideur (CIO/PM/trader) qui veut savoir :
1. Qu'a-t-on construit ? (en 3 phrases)
2. Est-ce rentable ? (oui/non, basé sur résultats réels)
3. Quel est le meilleur portefeuille à utiliser ? (avec limites claires)
4. Quels risques restent ? (drawdown historique, horizon temps, limite échantillon)
5. Que faire maintenant ? (recommandations de next-step)

## Structure

**Page 1 — Synthèse exécutive**
- Contexte : projet probabiliste NDX, 40 ans historique
- Objectif : Gagner de l'argent en trading indices (ou piloter risque via vol)
- Trouvailles clés (3-4 bullet points, chiffres réels)

**Page 2 — Tableau de bord comparatif**
- Stratégies testées (BuyHold, Momentum, LogitL2, HistGB, LogitL2+overlay, etc.)
- Sharpe, MDD, rendement annualisé en clair (ex. "sur 40 ans, perte max −50%, gain moyen +8% par an")
- Winner par métrique (Sharpe | MDD | Calmar)

**Page 3 — Recommandation + risques**
- Recommandation : quelle stratégie utiliser en production (avec DSR/probabilité succès)
- Risques : drawdown historique −83%, fenêtres de 2-3 ans sans gain, limite d'échantillon (40 ans = 10 cycles)
- Prochaines étapes : données intraday, autres indices, recherche alpha complémentaire

## Source

Utilise tous les fichiers results/ générés (A/B/C/D/integrated/indices/ensemble). Aucun chiffre inventé.

## Langue

Français (cible : audience francophone). Si l'audience est anglaise, demande clarification.

## Fichier

Produit `results/RAPPORT_EXECUTIF.md` (~2000 words max).

Pas de commit/push.
