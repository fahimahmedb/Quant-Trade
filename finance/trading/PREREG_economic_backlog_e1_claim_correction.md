# Pré-enregistrement — correction d'une revendication fausse dans ECONOMIC_MULTIASSET_BACKLOG.md (E1)

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de RÉPARATION**, découvert en vérifiant l'état
réel du fil économique après le constat d'épuisement du #532.

## L'incohérence trouvée

`ECONOMIC_MULTIASSET_BACKLOG.md` (§ Statut, ligne E1, et § « Prochaine
étape immédiate ») affirme :

> « **E1** (déblocage schéma panier) **ne dépend d'aucune donnée
> externe** et peut démarrer dès le prochain cycle sur ce fil — PREREG
> dédié avant toute modification du code de la batterie. »

`NONML_STRATEGY_BACKLOG.md` (cycle **#432**, section « File des
prochains cycles ») dit le contraire : E1 (« étendre ou non la
batterie au **schéma panier** ») est l'un des **trois points en
attente d'arbitrage de l'utilisateur, aucun tranché unilatéralement**
— au motif explicite que « la batterie a été conçue pour une position
**scalaire** », rendre son design compatible avec un schéma panier
étant un choix d'architecture, pas une tâche mécanique. Cette réserve
est **répétée sans interruption** — `grep -c` sur le motif exact
compte **102** occurrences dans tout le backlog principal (#432 à
#531 inclus), jamais levée par une décision utilisateur ni par un
cycle ultérieur.

**Vérifié avant toute conclusion** : le #443 (« concordance panier »,
cité comme candidat de levée possible) est un cycle d'**inventaire**
de concordance `.npz`/rapport, **pas** une extension du code de la
batterie de validation (`nonml_*_pass_validation_battery.py`) — les
deux sont des scripts complètement différents. Aucun cycle entre #432
et #531 ne modifie la batterie pour accepter un schéma panier.

## Ce que ce cycle corrige, et ce qu'il ne fait pas

Il corrige la **prose** d'`ECONOMIC_MULTIASSET_BACKLOG.md` pour qu'elle
cesse de contredire l'état réel, documenté et répété du backlog
principal. **Il ne tranche PAS lui-même la question laissée en
attente d'arbitrage au #432** — ce serait exactement l'erreur inverse
(décider unilatéralement ce que le #432 a explicitement refusé de
trancher seul). Il n'exécute aucun script de marché, ne modifie aucun
code de stratégie ou de batterie.

## Le protocole

1. Citer la phrase exacte du #432 établissant la réserve (déjà fait
   ci-dessus, vérifié par lecture directe de la section #432).
2. Corriger les **deux** endroits d'`ECONOMIC_MULTIASSET_BACKLOG.md`
   qui affirment l'absence de dépendance (ligne E1 du tableau,
   paragraphe « Prochaine étape immédiate ») pour qu'ils citent
   correctement la réserve du #432 et pointent vers elle.
3. **Diff borné** à ces deux passages, rien d'ajouté ni retiré
   ailleurs dans le fichier.
4. Vérifier par relecture intégrale du fichier corrigé que la
   cohérence interne du reste du document (univers d'actifs, E2/E3)
   n'est pas affectée.

## Critère de succès — chiffré

1. La citation exacte du #432 reproduite et vérifiée par lecture
   directe de la section.
2. Les **2** passages incohérents identifiés et corrigés.
3. Diff borné à ces 2 passages.
4. Relecture intégrale du fichier corrigé, cohérence confirmée.
5. Aucun script de marché exécuté, aucune décision d'arbitrage prise
   à la place de l'utilisateur.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les 2 passages sont bien ceux identifiés ci-dessus (aucun autre
   passage du fichier ne contredit le #432).
2. Le diff final ne touche que ces 2 passages (pas de dérive de
   scope).

## Ce que ce cycle ne fait pas

- Il ne **décide pas** d'étendre la batterie au schéma panier — cette
  décision reste **en attente d'arbitrage de l'utilisateur**, comme au
  #432.
- Il ne **réexamine** aucun verdict de stratégie déjà tranché.
- Il n'**exécute** aucun script de marché.

## Simulation 300 € et robustesse

**Sans objet** : cycle de correction documentaire, aucune position,
aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel.
2. **Chaque affirmation adossée à une ligne de texte citée.**
3. **Relecture intégrale du fichier corrigé avant commit** (engagement
   #414).
