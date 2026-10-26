# Architecture de contexte et discipline de session

**Remplace** le document « Rôle : Business Analyst & Architecte de contexte » transmis. Garde son ossature (arborescence de fichiers, handoffs, discipline de session) et corrige un principe qui allait à l'encontre de ce qui est déjà établi sur ce projet.

---

## 0. Ce qui change, et pourquoi

Le document d'origine pose une seule métrique de succès — minimiser les tokens — au-dessus de tout, y compris de la justesse du contenu (plans limités à 400-600 mots, interdiction de coller du contexte long dans un prompt). C'est exactement l'inverse de la règle déjà en place : *les documents ne se compressent pas, la concision y est un risque élevé* — et ce n'est pas une posture abstraite, trois épisodes réels de ce projet le confirment :

- **`specs-v2-ia-plan-test.md` n'a jamais atteint Claude Code** lors du lot IA-0 — les gates de F5/F6 ont dû être déduits plutôt que lus. Un document non transmis en entier a coûté plus cher en clarifications après coup qu'il n'aurait coûté en tokens à transmettre en entier.
- **SYN-D** (le seuil « 3× la médiane ») était mathématiquement dégénéré sur le cas le plus fréquent. Un modèle sous-spécifié pour tenir dans une limite de mots aurait masqué ce problème plutôt que de le révéler.
- **La dérogation de licence ROB** a été décidée en une phrase, en cours de session, sans le contexte des raisons qui avaient justifié la règle initiale — exactement le risque d'une discipline qui privilégie la brièveté du prompt à la présence du contexte nécessaire.

**Le principe corrigé** : l'efficacité en tokens se joue dans l'**architecture** — quels fichiers existent, lesquels se chargent pour quelle tâche, quand une session s'arrête — jamais dans le **contenu**. Un document reste aussi long que la justesse l'exige. Ce qui doit être court, c'est la liste de ce qu'on demande à Claude Code de lire pour une tâche donnée, pas ce qu'il y a dans chaque fichier.

---

## 1. Arborescence de fichiers

```
CLAUDE.md                          # racine, court, référence uniquement
docs/
  context-strategy.md              # ce document
  session-handoff-template.md      # gabarit, section 3
  feature-plans/
    comptage.md
    ia-f5-f9.md
    ia-f10-f19.md
    ux-v1-2.md
    ...un fichier par lot ou module, pas de limite de longueur
  handoffs/
    handoff-2026-09-05-lot-ia-0.md
    ...un fichier par fin de session, jamais réécrit après coup
```

### 1.1 `CLAUDE.md` racine
Court parce qu'il est **toujours chargé**, pas parce que le projet doit tenir en peu de mots. Contient : stack, commandes de build/test, invariants non négociables (ex. « aucune fonctionnalité IA active par défaut »), et des renvois explicites.

```markdown
# CLAUDE.md

Stack : FastAPI + Jinja2 + HTMX, SQLAlchemy/SQLite, Tailwind.
Tests : pytest tests/ — doit rester vert avant tout commit.

Invariants :
- Aucune fonctionnalité IA (F5-F19) active par défaut : feature flags éteints.
- Toute fonctionnalité IA gatée par des données réelles avant activation (voir specs-v2-ia-plan-test.md).
- Jamais de résultat sur donnée externe utilisé pour une décision métier (voir docs/feature-plans/ia-robustesse.md §3.1).

Pour une tâche précise, lire uniquement le plan de feature concerné dans docs/feature-plans/.
Avant de démarrer une session longue, lire le dernier handoff dans docs/handoffs/.
```

### 1.2 `docs/feature-plans/*.md`
Un fichier par module ou par lot cohérent. **Aucune limite de mots.** Un plan contient tout ce qu'il faut pour qu'une session qui ne lit que ce fichier ait le contexte complet — c'est le but même du découpage : pas « plus court », mais « scindé pour qu'on ne charge que ce qui concerne la tâche ». `specs-v2-ia-plan-test.md` et `extension-ia-f10-f19.md` sont déjà de bons exemples du niveau de détail attendu — rien à réduire là-dedans.

### 1.3 `docs/session-handoff-template.md`
```markdown
# Handoff — [date] — [sujet]

## Objectif de la session
[une phrase]

## Accompli
- [liste factuelle, pas de reformulation]

## Décisions prises et pourquoi
- [décision] — [raison en une ligne, avec renvoi au document source si la raison est longue]

## État actuel
[ce qui tourne, ce qui est testé, ce qui est derrière un flag]

## Prochaines tâches, par priorité
1. ...

## Pièges identifiés cette session
[ce qui a fait perdre du temps ou a cassé quelque chose, pour ne pas le refaire]

## Fichiers à lire pour reprendre
- [chemin] — [pourquoi celui-ci et pas un autre]
```
Rempli en entier à chaque fin de session ou jalon. **Aucune limite de longueur** — un handoff court sur une session complexe reproduit l'échec de la transmission de specs-v2 : moins de mots, mais la décision suivante prise sans le contexte qui l'aurait éclairée.

### 1.4 `docs/context-rules.md` (révisé)
- Ne jamais utiliser `/compact` sur une session longue sans avoir d'abord écrit un handoff.
- À un jalon logique (feature terminée, lot livré), écrire le handoff puis proposer `/clear`.
- Pour une nouvelle session, lire le plan de feature concerné et le dernier handoff pertinent — pas l'historique complet du projet.
- Déléguer à un sous-agent l'exploration lourde (parcourir un gros fichier, chercher un pattern dans le code) : il renvoie un résumé, pas le contenu brut.
- **Coller le contexte nécessaire à une décision reste toujours légitime.** La règle n'est pas « prompts courts », c'est « ne charger que les fichiers pertinents pour la tâche ». Une fois les bons fichiers identifiés, leur contenu se transmet en entier.

---

## 2. Discipline de session

### 2.1 Avant de démarrer
- Un objectif unique par session.
- Les fichiers à lire : le plan de feature concerné, le dernier handoff s'il y en a un. Pas plus par défaut ; plus si la tâche l'exige réellement.

### 2.2 Pendant la session
Signal de fin à surveiller : la fenêtre de contexte approche 60 %, ou un jalon logique est atteint (lot terminé, feature livrée). À ce moment : écrire le handoff, puis recommander `/clear`. Jamais `/compact` seul sur une session qui a pris des décisions non encore écrites ailleurs.

### 2.3 À la fin
Le handoff et, si le lot le justifie, le plan de feature mis à jour. La session suivante démarre sur ces deux fichiers, pas sur un rejeu de la conversation.

---

## 3. Ce qui est explicitement écarté du document d'origine

| Proposition d'origine | Pourquoi elle est écartée |
|---|---|
| Plans de feature limités à 400-600 mots | Contredit la règle établie ; aurait pu produire un SYN-D mal spécifié pour tenir dans la limite |
| « Jamais copier-coller de longs contenus dans les prompts » | Reformulé : ne pas coller ce qui n'est pas pertinent, mais transmettre en entier ce qui l'est — c'est la distinction entre architecture et contenu de la section 0 |
| Token comme métrique de succès prioritaire sur tout le reste | Mon rôle reste le même qu'à l'ouverture de ce projet : challenger avant de valider, distinguer fait/hypothèse/opinion, signaler les implications commerciales et techniques. L'efficacité de contexte est une discipline opérationnelle en plus, jamais une raison de sacrifier la justesse d'une décision |

Ce qui est gardé sans réserve : le découpage par fichier, le gabarit de handoff, le seuil de 60 % comme signal (pas comme contrainte de contenu), la délégation aux sous-agents pour l'exploration lourde, `CLAUDE.md` court par nature (toujours chargé) plutôt que par discipline de brièveté générale.

---

## 4. Modèle et effort recommandés

Mettre en place cette arborescence (créer les dossiers, écrire les gabarits, déplacer les documents existants dans `docs/feature-plans/`) : **Sonnet, effort par défaut** — mécanique une fois la structure ci-dessus donnée, aucune conception à inventer. Si le classement d'un document existant dans tel ou tel plan de feature est ambigu, ce point précis mérite d'être remonté plutôt que tranché seul.
