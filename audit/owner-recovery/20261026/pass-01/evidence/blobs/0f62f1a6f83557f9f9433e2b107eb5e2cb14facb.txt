# Handoff — 2026-09-08 — Mise en conformité specs-v2-ia-plan-test.md + mise en place de docs/context-strategy.md

## Objectif de la session
Recevoir `specs-v2-ia-plan-test.md` (arrivé après l'écriture du lot IA-0),
relire F5/F6/F7/F9 ligne à ligne contre lui, corriger les écarts trouvés,
puis mettre en place l'architecture de contexte décrite dans
`docs/context-strategy.md` pour que ce genre de document ne se reperde plus.

## Accompli
- Relu `specs-v2-ia-plan-test.md` §4 contre le code de F5/F6/F7/F9. Quatre
  règles étaient fausses (pas seulement absentes) : gate F5 (semaines de
  ventes manquantes), seuil de perte récurrente F5 (ratio inventé au lieu
  du % réglable), badge « inhabituel » F5 (moyenne au lieu de médiane),
  fenêtre/pondération F6 (historique complet au lieu de 8 occurrences
  pondérées). Deux étaient purement absentes : marge de sécurité F7 (la
  formule sous-commandait de 15 % à chaque suggestion), matrice
  popularité/marge F9 (entièrement manquante).
- Ajouté `ai_forecast.backtest_vs_v1` (IA-01) — F6 n'avait aucun moyen de
  se comparer à la règle v1 avant activation, alors que c'est le seul gate
  d'activation qui compte selon le document.
- Trois colonnes réglables ajoutées à `Settings` (`loss_alert_pct`,
  `loss_alert_eur`, `order_safety_margin_pct`) + migration Alembic —
  le document dit explicitement que ces seuils sont « des valeurs de
  départ raisonnées, pas des constantes validées ».
- Suite passée de 220 à 291 tests (285 + 6 ROB), chaque correction
  re-cassée puis restaurée pour prouver la non-vacuité. Commit `676cdbd`
  poussé sur `claude/restaurant-stock-management-mvp-6oq43e`.
- Mis en place `docs/context-strategy.md` (ce document remplace l'ancien
  « Rôle : Business Analyst & Architecte de contexte », corrige son
  principe central) :
  - `docs/feature-plans/` créé, `docs/IA scope.md` scindé en
    `ia-f5-f9.md` (Lot IA-0) et `ia-f10-f19.md` (extension), et
    `docs/exploitation.md` / `docs/generalisation-v1.2.md` déplacés là.
  - **`specs-v2-ia-plan-test.md` sauvegardé intégralement** dans
    `docs/feature-plans/` — c'est le document dont l'absence a coûté cher
    dans cette session même ; il n'existait dans aucun fichier du dépôt
    avant maintenant, seulement dans l'historique de conversation.
  - `docs/session-handoff-template.md` créé, ce fichier en est le premier
    remplissage réel.
  - `CLAUDE.md` racine mis à jour avec les renvois vers `feature-plans/`
    et `handoffs/`, sans en gonfler la taille (il reste court parce qu'il
    est toujours chargé, pas par discipline de brièveté générale).

## Décisions prises et pourquoi
- **Contradiction interne du document résolue** (F6 §4 vs IA-08 §6.3) :
  la moyenne pondérée par récence de §4 échoue seule à IA-08 (un pic ×100
  la déplacerait de >1500 %). Résolu en suivant la lettre d'IA-08
  elle-même — détecter (écarter les occurrences >3× la médiane du jour,
  les rapporter) puis appliquer la moyenne pondérée au reste. Documenté
  comme une lecture à faire confirmer, pas un arbitrage tranché — voir
  `docs/bilan-ia-0.md` §3.
- **Garde-fou hors-spec conservé pour SYN-D** : le cas dégénéré (médiane
  historique nulle) n'est résolu par aucun des deux documents. Un seuil
  relatif de repli (15 % de la conso de la période) reste en place, à
  trancher au pilote où la médiane sera rarement nulle.
- **Classification des bilans/observations non tranchée seule** :
  `bilan-ia-0.md`, `bilan-v1.1.md`, `observations-v1.md` sont restés à la
  racine de `docs/`, PAS déplacés dans `feature-plans/` (ce sont des
  rapports de sortie de lot, pas des plans prospectifs) ni dans
  `handoffs/` (ce sont des documents adressés à l'humain porteur du
  projet, pas des reprises de session à session). `docs/context-strategy.md`
  ne définit explicitement l'emplacement d'aucun des deux genres — point à
  remonter plutôt qu'à trancher, comme demandé par le document lui-même
  (§4, dernière phrase).

## État actuel
Tous les tests verts (291, ROB compris). Le lot IA-0 (F5/F6/F7/F9) reste
derrière ses feature flags, éteints par défaut — rien de visible n'a
changé pour un utilisateur. La nouvelle arborescence `docs/feature-plans/`
et `docs/handoffs/` est en place mais pas encore committée au moment
d'écrire ce handoff.

## Prochaines tâches, par priorité
1. Committer/pousser la mise en place de l'architecture de contexte
   (déplacements de fichiers + `CLAUDE.md` + ce handoff).
2. Faire confirmer par le porteur du projet les deux lectures non
   tranchées : la conciliation F6/IA-08, et le garde-fou du cas dégénéré
   de SYN-D (voir ci-dessus).
3. Décider où vivent les bilans de sortie de lot (`bilan-*.md`) dans
   l'arborescence — rester à la racine de `docs/`, ou un nouveau dossier
   dédié (`docs/bilans/` ?) distinct de `feature-plans/` et `handoffs/`.
4. Le reste à faire avant pilote réel est dans `docs/bilan-ia-0.md` §6
   (inchangé par cette session).

## Pièges identifiés cette session
- `specs-v2-ia-plan-test.md` avait été **transmis dans le chat**, jamais
  écrit comme fichier — exactement le mode de perte que
  `docs/context-strategy.md` diagnostique en premier exemple. Réflexe à
  prendre : tout document de plusieurs centaines de lignes collé dans une
  conversation doit être sauvegardé en fichier dans la même session, pas
  seulement lu et appliqué de mémoire.
- Un ratio de magnitude « raisonnable » avait été inventé en l'absence de
  spec (RECURRING_MAGNITUDE_RATIO) plutôt que signalé comme une hypothèse
  à vérifier explicitement dans le bilan de sortie — il a fallu la relecture
  de specs-v2 pour le découvrir faux. Une hypothèse non spécifiée doit être
  marquée comme telle au moment où elle est prise, pas seulement documentée
  après coup dans le bilan final.

## Fichiers à lire pour reprendre
- `docs/feature-plans/specs-v2-ia-plan-test.md` — la référence normative de
  F5-F9, désormais dans le dépôt.
- `docs/bilan-ia-0.md` §2-§3 — la relecture ligne à ligne complète et les
  deux points laissés ouverts.
- `docs/context-strategy.md` — l'architecture elle-même, pour toute session
  future qui réorganise ou étend `docs/`.
