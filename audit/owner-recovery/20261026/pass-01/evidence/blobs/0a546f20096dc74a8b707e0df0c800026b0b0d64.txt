# Backlog — Lot IA-1

> Sauvegardé ici lors de son traitement (docs/context-strategy.md) plutôt que
> de rester seulement dans l'historique de conversation. Voir
> `docs/bilan-ia-1.md` pour l'état d'avancement réel des tickets ci-dessous.

À traiter après `avancement-lot-ia-0-trois-decisions.md`. Objectif de ce document : que Claude Code puisse enchaîner les tickets sans repasser par une clarification à chaque étape. Tout ce qui pouvait être tranché à l'avance l'est ; ce qui reste vraiment ouvert le dit explicitement.

---

## 0. Ordre de traitement
1. Les trois décisions du document précédent.
2. Ce backlog, dans l'ordre de la section 4.
3. Retour vers le porteur du projet une fois les deux faits — pas avant, sauf blocage réel (section 2).

---

## 1. Trois décisions actées maintenant

Elles étaient en suspens dans `extension-ia-f10-f19.md` §5. Tranchées ici pour ne pas revenir dessus :

- **Journal de décision du modèle** : à construire, priorité haute. Coût faible, et sans lui aucune sortie F10-F19 n'est traçable au pilote.
- **Écran de comparaison en mode ombre** : à construire, après F6 déjà en place. `backtest_vs_v1` (Lot IA-0) en est la brique de calcul — l'écran l'expose, il n'invente rien de nouveau.
- **Rejeu historique** : reste hors périmètre. Ne pas construire, ne pas y revenir sans demande explicite.

---

## 2. Règle de résolution d'ambiguïté

Avant de vous arrêter pour demander : appliquer dans l'ordre.

1. **Chercher si une décision analogue existe déjà dans le projet** (specs V2, Lot IA-0, ce backlog) et la réutiliser plutôt qu'en inventer une nouvelle — un seuil, un pattern de code, une convention de nommage.
2. **Préférer la dégradation silencieuse à la supposition.** Si une donnée optionnelle manque, la fonctionnalité reste inerte (comportement déjà appliqué à F7, F13, F14, F16) — jamais deviner une valeur à la place.
3. **Sur une question de jugement produit ou métier** (pas technique) : ne pas construire plutôt que deviner. Documenter le point bloquant dans le rapport de sortie du lot.
4. **Sur une question purement technique** sans impact métier (nom de variable, structure de fichier) : trancher et documenter le choix, ne pas remonter.

Seul le cas 3 justifie de revenir avant la fin du lot.

---

## 3. Leçons du Lot IA-0, à appliquer par défaut

Chacune vient d'un bug réellement trouvé sur ce projet — pas des principes abstraits.

- **Horodater par la date métier, jamais par la date de traitement.** `rolling_avg_daily_consumption` lisait `StockMovement.created_at` (l'heure d'exécution) plutôt que la date de vente — faux sur tout historique rejoué ou importé après coup. Tout calcul sur une fenêtre temporelle doit utiliser la date métier de l'événement.
- **Tout calcul qui rejoue le passé prend un paramètre `as_of`**, testé pour l'étanchéité passé/futur (modifier une donnée après la coupure ne doit rien changer au résultat calculé avant elle).
- **Aucun formatage de date localisé sans fonction dédiée.** `strftime("%A")` est sorti en anglais dans le conteneur (locale C). Toute sortie de jour de semaine passe par une fonction du projet, jamais par le formatage natif.
- **Réutiliser un seuil réglable existant plutôt qu'en créer un nouveau** pour un concept proche (le garde-fou SYN-D réutilise le seuil de perte récurrente plutôt que d'inventer une constante).
- **Tester explicitement le cas dégénéré de tout calcul statistique** (médiane nulle, échantillon vide, division par zéro) — pas seulement le cas nominal.
- **Vérifier qu'un test de robustesse s'exerce réellement dans les conditions qu'il prétend couvrir.** SYN-B/C étaient sous leur propre gate, l'aberration de SYN-F était hors fenêtre d'estimation — deux tests verts qui ne prouvaient rien. Toute nouvelle donnée synthétique doit être vérifiée contre les gates de la fonctionnalité qu'elle teste, pas seulement contre le résultat attendu.

---

## 4. Backlog priorisé

Détail fonctionnel complet (règles métier, AC, TC) dans `extension-ia-f10-f19.md` — non reproduit ici. Chaque ticket ajoute la séquence et les décisions par défaut propres à ce lot.

### Ticket 1 — F10, classification de criticité
Gate : ≥ 4 semaines de ventes, aucun comptage requis. Prérequis de F11.
**Décision par défaut** : sur ex-æquo de valeur entre deux ingrédients au bord d'une classe, celui avec la plus forte volatilité (§F10.2) monte dans la classe supérieure — cohérent avec la règle déjà écrite, pas un cas nouveau à trancher.

### Ticket 2 — F11, comptage tournant intelligent ⭐
Gate : F10 actif, ≥ 3 comptages complets. Dépend du ticket 1.
**Décision par défaut** : le comptage complet périodique forcé (§F11, 4 semaines par défaut) utilise la même variable de réglage que la fenêtre de moyenne glissante existante si elle est sémantiquement compatible ; sinon, nouvelle variable dans `Settings`, documentée comme telle — vérifier avant d'écrire, ne pas dupliquer sans avoir cherché.

### Ticket 3 — F12, alerte de marge érodée ⭐
Gate : ≥ 2 relevés de prix. **Dépendance non levée** : suppose le prix de vente sur la fiche plat (U7 du plan UX), pas encore construit.
**Décision par défaut** : construire F12 quand même, en amont de l'écran — la fonctionnalité reste inerte tant qu'aucun prix de vente n'est saisi nulle part (cohérent avec §2, règle 2). Ne pas attendre U7 pour écrire la logique.

### Ticket 4 — F15, contrôle d'intégrité des imports
Gate : ≥ 3 semaines d'imports. Aucune dépendance UI.
Priorité haute (garde-fou de tout le reste, coût faible) — inchangé depuis `extension-ia-f10-f19.md` §12.

### Ticket 5 — F18, indicateur de confiance et retour automatique à v1
Gate : ≥ 4 semaines de prévisions produites (mode ombre compris).
**Décision par défaut** : l'hystérésis anti-bascule-en-boucle (TC-F18-05) utilise des fenêtres asymétriques — 3 semaines de dégradation pour désactiver, 3 semaines d'amélioration **confirmée par un nouveau backtest complet**, pas seulement 3 bonnes semaines consécutives, pour réactiver. Évite qu'un rebond ponctuel réenclenche immédiatement ce que la dégradation venait d'éteindre.

### Ticket 6 — F14, risque de péremption
Gate : durée de conservation renseignée (champ optionnel F7). Dépendance non levée, dégrade proprement (§2 règle 2).

### Ticket 7 — F16, consolidation de commande par fournisseur
Gate : aucun, purement combinatoire. Fournisseur/franco/minimum optionnels, dégrade proprement.

### Ticket 8 — F17, diagnostic de cause d'écart
Gate : ≥ 6 comptages, ≥ 3 écarts avec motif saisi.
**Décision par défaut** : en cas de deux hypothèses plausibles simultanées (TC-F17-05), les afficher toutes les deux, jamais un score de confiance qui laisserait croire à un classement fiable entre deux corrélations sur un aussi petit échantillon.

### Ticket 9 — F13, prévision de mise en place
Gate : F6 actif pour les ingrédients concernés, champ « préparé en interne » renseigné. Confort — dernier de la liste, à construire seulement si les tickets 1 à 8 sont faits.

### Explicitement hors de ce lot
**F19** (socle effet réseau) reste hors périmètre — question juridique non tranchée, un seul restaurant actif. Ne pas y toucher sans instruction explicite.
**Les écrans du Lot IA-0** restant « non construits » (refus F5, marquage journée exceptionnelle F6, journal d'adoption F7, export matrice F9) ne sont pas non plus dans ce lot — c'est du travail d'écran, pas d'algorithme ; à cadrer dans un lot UX dédié plutôt que mélangé ici.

---

## 5. Jeux de données à générer

SYN-J à SYN-O déjà spécifiés dans `extension-ia-f10-f19.md` §11 — à construire au fur et à mesure des tickets, pas tous d'avance. Même principe que le Lot IA-0 : graine fixe, vérité terrain interrogeable, et vérifier systématiquement (leçon §3) que chaque jeu respecte le gate de la fonctionnalité qu'il teste.

---

## 6. Critères de sortie du lot

- Tickets 1 à 8 construits, testés, derrière feature flag éteint. Ticket 9 si le temps le permet, sinon reporté sans que ce soit un échec du lot.
- Journal de décision du modèle en place dès le ticket 1 (chaque sortie F10+ y est journalisée).
- Écran de comparaison en mode ombre construit après le ticket 2.
- NR-01 à NR-18 et la suite du Lot IA-0 toujours verts.
- Aucun changement visible pour un utilisateur, sauf l'écran de comparaison en mode ombre — réservé à l'équipe projet, jamais au restaurateur (à protéger comme tel, pas seulement caché derrière un lien).
- Rapport de sortie listant, comme pour le Lot IA-0 : ce qui est prouvé sur données contrôlées, les écarts entre ce backlog et ce qui a été construit, et tout point bloquant relevant de la section 2 règle 3.

---

## Modèle et effort recommandés

**Opus, effort par défaut** pour les tickets 1, 2 et 8 — criticité (F10) et comptage tournant (F11) sont les fonctionnalités à plus fort enjeu de conception de ce lot, et le diagnostic de cause (F17) demande de juger quand une corrélation est assez solide pour être montrée. **Sonnet, effort par défaut** pour les tickets 3 à 7 et 9 — patron déjà établi par F5-F9, application répétée plus qu'invention. Repasser en Opus uniquement si un ticket Sonnet remonte un point de la section 2 règle 3.
