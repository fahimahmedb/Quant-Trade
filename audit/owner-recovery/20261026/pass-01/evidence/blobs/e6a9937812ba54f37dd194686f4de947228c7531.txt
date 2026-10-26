# Amendement à la charte A2 : quotas et choix du modèle — PROJET

```text
DOCUMENT_STATUS = DRAFT_PENDING_EXPLICIT_OWNER_RATIFICATION
AMENDS = charte ratifiée au commit 5bb9b349742db21a07dc67f1718a66fa87aa30d6 (ajoute le §6 quater)
EFFECT_BEFORE_RATIFICATION = NONE
```

Date : 2026-10-08. Modifier la charte est réservé à Owner (§5.5) : ce texte n'a d'effet qu'une fois ratifié à son commit et son blob exacts.

## §6 quater. Quotas et choix du modèle

**Principe.** Chaque agent connaît l'état de son quota, le déclare, et appelle le meilleur modèle seulement quand la tâche le justifie et que son quota le permet. Un agent n'estime jamais le quota de l'autre : il lit ce qui est lisible et traite le reste comme inconnu.

### 1. Ce que chaque agent lit

| Agent | Source | Valeurs lues |
|---|---|---|
| Claude Code | `get_session` (sa session, ou celle de tout agent Claude du compte, dont Astra) | `rate_limit_info.status` (`allowed`, `allowed_warning`, `rejected`), type de fenêtre, `resetsAt`, `isUsingOverage` ; `context_usage` ; `usage.cost_usd` |
| Codex | À renseigner d'après sa réponse à la demande du 2026-10-08 (comm. de la PR #22), puis à confirmer par Owner dans la page d'usage de Codex | Tant que non confirmé : `NON_VISIBLE` |

### 2. Ligne de quota dans chaque message

Chaque message `[A2-TEAM]` commence par une ligne :

```text
QUOTA: <agent> | <statut> | <remise à zéro ISO ou INCONNUE> | <modèle utilisé>
```

Un agent qui ne peut pas lire son quota écrit `INCONNU`. Un quota `INCONNU` est traité comme `allowed_warning`.

### 3. Échelle de modèles et seuils

| Niveau de tâche | Modèle de Claude Code | Modèle de Codex | Condition de quota |
|---|---|---|---|
| T, réflexion et revue décisive | Opus, par sous-agent (`model: opus`) ou session neuve | modèle le plus fort disponible | statut `allowed` |
| B, construction | Sonnet | modèle intermédiaire | `allowed` ou `allowed_warning` |
| M, mécanique | Haiku ou script | modèle le plus économe | tout statut sauf `rejected` |

- **`allowed_warning`** : un agent réserve son modèle le plus fort aux seules tâches bloquantes (niveau de risque 2 et plus du §6 bis), et passe les autres au niveau inférieur.
- **`rejected`, ou dépassement de budget (§6 bis)** : l'agent se met en pause selon le §6 ter d.
- **Choix d'un modèle plus fort que le sien :** Claude ouvre une session neuve (`create_session`, paramètre `model`) ou délègue à un sous-agent. Pour Codex, le mécanisme est celui que Codex a décrit et qu'Owner a confirmé ; à défaut, Owner règle le modèle dans les réglages de Codex.

### 4. Pas de dégradation silencieuse

Un livrable produit avec un modèle plus faible que le niveau requis est marqué `MODELE_DEGRADE` dans son message et dans la fiche de reprise. Il est refait au bon niveau avant d'être utilisé pour une décision de niveau 2 ou plus. Une tâche de niveau 3 n'est jamais dégradée : elle attend la remise à zéro du quota.

### 5. Reprise de charge

Si le quota d'un agent est `rejected` ou si sa dernière demande est restée sans réponse après un rappel (§6 ter c), l'autre agent reprend les tâches de la file qu'il est habilité à faire, sans élargir son autorité, et alerte Owner. Une tâche d'écriture ne revient à Codex que si Owner a ouvert la PR de sa tâche.

### 6. Vue d'Owner

La fiche de reprise contient un tableau « Quotas » : une ligne par agent (dernier statut, remise à zéro, modèle, coût du lot), mis à jour par Claude Code au début et à la fin de chaque lot à partir de ses lectures et de la dernière ligne `QUOTA:` de Codex.

```text
NEW_SUBSTANTIVE_AUTHORITY_CREATED = NONE
OWNER_RESERVED_DECISIONS = SECTION_5_UNCHANGED
MERGE_AUTHORITY = NONE
```
