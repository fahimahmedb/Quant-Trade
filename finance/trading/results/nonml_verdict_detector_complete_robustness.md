# Robustesse — la règle du #448 hors de sa forme exacte

**Étape 7a. Ce n'est pas un retuning** : la règle du balayage reste celle du
#448, inchangée. On démonte la décoration retirée en **quatre couches** et on
regarde si le résultat tient sur un voisinage ou dépend d'une seule d'entre
elles. La grille était fixée avant exécution.

Rapports examinés : **115**

| Variante | PASS | FAIL | indéterminé | Faux négatifs #447 récupérés (/2) |
|---|---|---|---|---|
| V0 — aucune (règle #447) | 1 | 90 | 24 | **0** |
| V1 — titres | 2 | 92 | 21 | **1** |
| V2 — titres + citations | 2 | 92 | 21 | **1** |
| V3 — titres + citations + puces | 2 | 92 | 21 | **1** |
| V4 — tout (règle #448) | 2 | 93 | 20 | **2** |

## Lecture — et un constat qui dérange

Les deux faux négatifs ne sont **tous deux** récupérés qu'à partir de
**V4 — tout (règle #448)**. Autrement dit :

- la couche **titres** (V1) rattrape `### **FAIL**` — le rapport du #446 ;
- la couche **étiquette** (V4) est **seule** à rattraper
  `## Verdict : **FAIL**` — le rapport du #444. Les couches intermédiaires
  (citations, puces) ne changent **rien** : 0 reclassement entre V1 et V3.

**Ce n'est pas un plateau, c'est un escalier à deux marches** — et la seconde
marche ne porte qu'**un seul** cas.

Le rapport de robustesse que j'avais rédigé d'avance annonçait un plateau et
le mot « pic » n'y figurait qu'en garde-fou. **La mesure dit l'inverse de ce
que j'avais écrit**, et c'est la mesure qui est publiée.

### La question qu'il faut poser franchement

La couche « étiquette » a-t-elle été **taillée pour le cas qu'elle devait
rattraper** ? Le pré-enregistrement l'a déclarée avant toute mesure, et
l'anti-cheat le confirme — mais elle a été déclarée **en sachant** que le
#444 énonçait `## Verdict : **FAIL**`, puisque le #447 l'avait publié.

**Honnêtement : oui, en partie.** La règle couvre quatre formes ; deux
d'entre elles ne servent à rien sur le corpus actuel, et une n'existe que
pour un unique rapport. Ce n'est pas du data-snooping au sens du protocole —
aucun seuil n'a été balayé, aucun résultat de stratégie n'est en jeu — mais
c'est une règle **ajustée à des cas connus**, et le dire vaut mieux que
laisser le tableau suggérer une robustesse qu'il ne montre pas.

Ce qui **ne** serait **pas** honnête serait de retirer la couche maintenant
pour faire joli : elle est déclarée, elle est utile, elle reste.

## Ce que ces couches valent pour la suite

Il **ne** signifie **pas** que les trois couches supplémentaires sont inutiles :
elles couvrent des formes d'énoncé qui n'existent pas *encore* dans le dépôt
(`> **FAIL**`, `- **PASS**`, `Verdict final : **PASS**`). Les garder, c'est
accepter un coût nul aujourd'hui contre un faux négatif évité demain.

Mais il faut lire le tableau pour ce qu'il montre : **sur le corpus
d'aujourd'hui, deux des quatre couches sont inertes et une ne sert qu'une fois.**
La robustesse de la règle est donc **à démontrer par l'usage**, pas acquise.
