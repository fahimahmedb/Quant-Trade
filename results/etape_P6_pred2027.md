# Étape P6 — Prévision FORWARD de la présidentielle 2027

## 0. Statut : prévision honnêtement vérifiable

2027 est un scrutin **futur** : aucun hindsight n'est possible. C'est la seule prévision de ce dépôt qui pourra être confrontée à la réalité a posteriori. Les fondamentaux sont entraînés sur les 11 présidentielles 1965-2022 et appliqués aux hypothèses macro 2027 (`data/fr_2027_hypotheses.csv` — chiffres publics réels et datés, mis à jour au fil des publications).

## 1. Ce que la base validée SAIT et NE SAIT PAS faire

Rappel de l'audit (`results/AUDIT.md`) : le modèle structurel ne prédit que le **sort du camp sortant**, et il ne bat même pas nettement une heuristique simple à n=11. Il est **structurellement incapable** de désigner le vainqueur d'un siège ouvert avec recomposition — comme il n'a pas pu voir Macron émerger en 2017. On livre donc un **prior sur la Macronie**, pas un pronostic du gagnant.

## 2. Configuration 2027 (siège ouvert)

Emmanuel Macron **ne peut pas se représenter** (limite de deux mandats consécutifs, art. 6 de la Constitution). Le camp présidentiel sortant (Renaissance/Ensemble) présentera un candidat encore indéterminé — c'est la **référence** dont on modélise le sort.

| Variable fondamentale | Valeur 2027 | Lecture |
|---|---|---|
| Croissance PIB | 0.9 % | atone |
| Chômage | 7.5 % | élevé |
| Approbation du camp sortant | 26 % | basse |
| Ancienneté au pouvoir | 10 ans | usure marquée |
| Président sortant candidat | non | siège ouvert |

## 3. Analogie historique (plus proches voisins en fondamentaux)

Élections passées les plus proches du profil 2027 (distance standardisée sur les 4 variables) :

| Rang | Élection | Référence (camp sortant) | Le camp sortant a-t-il gagné ? |
|---|---|---|---|
| 1 | 2007 | sarkozy_2007 | oui |
| 2 | 2017 | hamon_2017 | NON |
| 3 | 2012 | sarkozy_2012 | NON |

*Le profil 2027 est le plus proche de **2007** — où le camp sortant (Sarkozy, droite héritière de Chirac) a **gagné**. Les analogies sont donc **mitigées** : 2007 (victoire), 2012 et 2017 (défaite/élimination). Le signal historique n'est PAS univoque ; il n'autorise pas à annoncer un effondrement certain de la Macronie.*

## 4. Prior structurel sur la Macronie (fondamentaux)

- Part 2nd tour prédite pour le camp sortant (**s'il est finaliste**) : **49.6%** ± 10.2% (1 σ).
- Probabilité structurelle qu'il l'emporte (conditionnelle à un 2nd tour) : **49%** — soit un **quasi pile-ou-face**, PAS une défaite annoncée.
- **Lecture honnête** : les fondamentaux ne donnent AUCUN signal fort pour 2027 (≈ 50/50), et l'écart-type large (±10 pts) mange la moindre nuance. C'est cohérent avec un modèle qui, rappelons-le, ne bat pas une règle triviale à n=11. Toute affirmation plus tranchée (« la Macronie est condamnée ») serait une sur-interprétation du chiffre.
- Réserve importante : ce modèle prédit la part *au 2nd tour*, pas la probabilité d'**atteindre** le 2nd tour. Or le vrai risque pour le camp sortant (cf. PS 2017) est l'élimination au 1er tour — que cette version ne modélise pas encore explicitement.

## 5. Sources live (marchés / NLP) — état au moment de l'exécution

- **Marchés** : `available=False`. La tentative de fetch live Polymarket n'a trouvé **aucun marché mappable** sur la présidentielle FR 2027 (marché inexistant ou mapping outcome→camp non déclaré). Aucune probabilité n'est inventée. La source s'activera automatiquement le jour où un marché liquide existera.
- **NLP** : available=False (données Trends/presse 2027 à collecter en live le moment venu).
- **Fusion actuelle** = prior fondamental seul (part 49.6%, P(victoire camp sortant) 49%). Elle se raffinera quand marchés/NLP livreront de vraies données contemporaines.

## 6. Conclusion honnête

**Ce que la base dit (avec prudence)** : sur les fondamentaux seuls, le sort du camp présidentiel sortant en 2027 est **indécis (≈ 50/50)** — ni favori, ni condamné. Le contexte (impopularité, 10 ans de pouvoir, siège ouvert) est défavorable, mais le plus proche précédent (2007) s'est soldé par une victoire du camp sortant : le modèle refuse de trancher, et à n=11 il a raison de le faire.

**Ce que la base NE dit PAS, et ne peut pas dire** : qui gagne (RN, gauche, droite). Les fondamentaux sont aveugles aux recompositions ; désigner un vainqueur exigerait des marchés de prédiction liquides et/ou des signaux de campagne (NLP) contemporains, qui n'existent pas encore à ~21 mois du scrutin. Toute prévision du gagnant aujourd'hui serait de l'invention déguisée — précisément l'erreur corrigée dans `results/AUDIT.md`.

**Prochaine actualisation** : rejouer ce script quand (a) de nouvelles données macro sortent, (b) un marché 2027 ouvre, (c) des séries Trends/presse datées sont disponibles. La prévision se resserrera alors honnêtement, sans jamais rétro-ajuster.
