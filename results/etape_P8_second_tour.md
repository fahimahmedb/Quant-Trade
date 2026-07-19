# Étape — Second tour 2022 par circonscription : reports de voix (données réelles)

## 0. Données

Présidentielle 2022, 2nd tour, Macron vs Le Pen, **577 circonscriptions** (ministère de l'Intérieur / data.gouv.fr, ressource récupérée via l'API tabulaire puis parsée depuis le .txt — l'API tabulaire *beta* mésinterprète les décimales à virgule de ce fichier, on calcule donc les parts depuis les voix brutes). Agrégat national reconstitué = officiel : **Macron 58.55 % / Le Pen 41.45 %**.

## 1. Géographie du 2nd tour (ce que le national masque)

- Part Le Pen au 2nd tour : de **7.5 %** (circo la plus macroniste) à **72.2 %** (écart-type 12.8 pts). Le « 41,5 % » national recouvre une France coupée en deux.

## 2. Peut-on lire les REPORTS de voix ? Oui pour le tout, NON pour le détail

La part Le Pen T2 est **très bien prédite** par la composition du 1er tour (R² = 0.95). Mais **les taux de report individuels ne sont PAS identifiables** depuis des agrégats — c'est le *sophisme écologique* (King 1997). Preuve par l'instabilité des estimateurs naïfs :

- **OLS** (part T2 ~ parts T1, avec constante) : intercept absurde de **+235** et coefficients négatifs partout → colinéarité compositionnelle (les parts somment à 100).
- **NNLS** (taux ≥ 0 sur les voix) : « taux » de **1.30 pour RN** (soit >100 %) et explosion sur les micro-partis → sous-identification quand deux partis (RN, Reconquête) sont spatialement corrélés.

On **ne rapporte donc PAS** de matrice de reports : ce serait inventer une précision inexistante (l'erreur corrigée dans `results/AUDIT.md`). L'estimation rigoureuse exige de l'**inférence écologique** (King) ou des données de sondage individuelles.

## 3. Le paradoxe Zemmour : le sophisme écologique en une ligne

Corrélation spatiale part Le Pen T2 vs part Zemmour T1 : **r = +0.01** (quasi nulle !) — alors qu'au niveau **individuel** les électeurs Zemmour ont massivement voté Le Pen. Explication : les fiefs de Zemmour (quartiers aisés) ne sont pas ceux de Le Pen (France populaire/périurbaine), donc la corrélation entre circonscriptions s'annule. **C'est exactement pourquoi on ne lit pas les reports dans les agrégats.**

## 4. Ce qui EST robuste

**Corrélations spatiales** de la part Le Pen T2 (directionnelles, stables) :

| Score 1er tour | Corrélation avec Le Pen T2 |
|---|---|
| Le Pen (RN) | +0.90 |
| Dupont-Aignan | +0.53 |
| Lassalle | +0.27 |
| Roussel (PCF) | +0.21 |
| Pécresse (LR) | -0.28 |
| Hidalgo (PS) | -0.29 |
| Mélenchon (LFI) | -0.31 |
| Macron (ENS) | -0.68 |
| Jadot (EELV) | -0.80 |

**Comptabilité du réservoir** (robuste car agrégée) :

- Bloc droite radicale au 1er tour : RN 23.2 % + Reconquête 7.1 % + DLF 2.1 % = **32.3 %**.
- Le Pen au 2nd tour : **41.5 %** → **+9.2 pts** au-delà de ce bloc (reports d'électeurs de gauche/centre anti-Macron et d'abstentionnistes du 1er tour). Le « front républicain » a plafonné son report.

## 5. Ce que le 2nd tour apporte au modèle deux tours

- **Carte de vulnérabilité** : les circonscriptions où Le Pen dépasse 50 % au 2nd tour (158 / 577) dessinent son socle de conquête — base d'une projection de sièges (législatives) et de scénarios 2027.
- **Contrainte pour la fusion (P4)** : la relation T1→T2 est forte en agrégat mais les reports fins sont incertains ; tout modèle deux tours doit porter cette incertitude, pas prétendre à une matrice de report exacte.
- **Limite assumée** : une élection (2022) ; inférence écologique non conduite (méthode citée, pas implémentée) ; l'API tabulaire data.gouv (beta) reste utile pour explorer mais peu fiable sur les décimales françaises de ces fichiers.
