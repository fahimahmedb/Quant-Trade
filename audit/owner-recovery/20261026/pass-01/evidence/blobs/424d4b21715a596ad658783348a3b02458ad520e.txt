# Ordre 12 — 🟩 B : H-001, de la CLV à une expérience économique complète (URGENT, avant le premier match noté)

> À coller tel quel dans la session du builder B (`claude/new-session-0ydmkg`).
> Base : audit Astra du 2026-09-29 (direction et gain), vérifié par Blue dans le code.
> Une tâche parallèle, le test séquentiel à garantie, est confiée à un autre builder (ordre 12b). Tu ne la codes pas ; tu la branches.

```text
QUESTION PRINCIPALE (elle juge chaque ligne de code que tu écris)
« Cette stratégie peut-elle produire un gain net ENCAISSABLE, après tous les frais,
sur le capital réellement immobilisé, avec une exécution plausible ? »
Un travail qui ne rapproche pas d'une réponse à cette question n'est pas prioritaire.

CONSTATS (audit Astra, vérifiés par Blue dans research/fast_rail/h001/forward.py)
1. FORWARD_PASS possible avec 30 paris réglés et une moyenne positive. Les paris non réglés
   sont ignorés, et le verdict devient ensuite définitif (sticky).
2. Un pari sans cotation de clôture sur la venue (`close is None`) ou sur un match reporté
   disparaît aussi du P&L : c'est un biais de sélection.
3. La profondeur n'est pas contrôlée sur Kalshi : le fill de 100 contrats y est supposé.
4. La condition P&L n'a presque aucun pouvoir (σ ≈ 0,5 par contrat à p = 0,5, erreur type
   ≈ 0,09 sur 30 paris, contre un edge d'environ 0,02).
5. Aucune garantie d'α sous dépendance (plusieurs matchs d'un même soir) ni sous queues épaisses.
Aucun faux passage n'a eu lieu : 0 match forward. C'est le moment de corriger la règle,
tant que c'est encore propre.

## 1. Déclaration amendée (commit AVANT tout autre travail)
Dans forward.py et au registre (événement "declared", horodatage UTC réel) :
- PRISTINE_AFTER = heure de ce commit, arrondie à l'heure supérieure. Les paris entrés avant
  sont journalisés, mais ne comptent jamais (invariant 6 : la règle précède les données).
- Chaque pari entré est un ENGAGEMENT. Il reste dans le P&L jusqu'au règlement de la venue,
  y compris sans cotation de clôture et en cas de report. Seule la CLV peut manquer.
- Si plus de 10 % des engagements n'ont pas de clôture exploitable → INCONCLUSIVE(données).
- Test : l'e-processus de l'ordre 12b (anytime-valid, statistique bornée), α = 0,025,
  paramètres fixés dans 12b. Tant qu'il n'est pas livré, le statut reste SHADOW_DIRECT
  (aucune décision possible). L'ancien t-SPRT n'est plus qu'un indicateur.
- Nouveau statut terminal FORWARD_PASS(PRIX) = l'e-processus accepte l'edge de CLV nette
  ET tous les engagements jusqu'au point d'arrêt sont réglés ET le P&L net n'est pas
  significativement inférieur à ce que la CLV laisse attendre (P&L moyen ≥ CLV moyenne
  − 1,96 × erreur type du P&L). Le statut n'est figé qu'une fois tous ces règlements reçus.
- Le rapport écrit explicitement : « FORWARD_PASS(PRIX) prouve un edge de prix, pas un gain
  encaissable. Il faut environ (1,96·σ/edge)² ≈ 2 400 paris pour prouver le P&L. La preuve
  de gain relève d'un micro-test réel, décision du propriétaire. »

## 2. Exécution plausible
- Kalshi : lire le carnet d'ordres public du marché visé au moment de l'entrée, puis
  appliquer le même contrôle qu'ailleurs (100 contrats au prix demandé ou mieux). Si le
  carnet est inaccessible (401 ou erreur), le pari Kalshi n'est PAS pris. On ne suppose
  jamais un fill.
- Journaliser pour chaque engagement : venue, prix, frais, profondeur vue, horodatages
  d'entrée et de règlement.

## 3. Mesure économique
Ajouter au rapport, sans en faire une condition de passage :
- P&L net total ;
- capital immobilisé (prix × contrats) × durée jusqu'au règlement ;
- rendement sur capital immobilisé, annualisé ;
- intervalle de confiance du P&L.

## 4. Tests adversariaux (obligatoires)
- Un pari sans clôture reste dans le P&L.
- Un report reste dans le P&L.
- Pas de FORWARD_PASS tant qu'un engagement du préfixe n'est pas réglé.
- Plus de 10 % de clôtures manquantes → INCONCLUSIVE.
- Kalshi sans carnet → pas de pari.
- Un pari antérieur à PRISTINE_AFTER est ignoré.
- Replay identique (fonction pure).
Red team (économique et runtime, 2 agents qui n'ont pas écrit le code) avant le push sur la
branche de données.

## 5. Livraison
Merge dans claude/data-feeds-6vr22g pour que le workflow horaire évalue la nouvelle règle.
Quand 12b est livré : merge de sa branche, branchement de l'e-processus, tests, push.
Ensuite, reprends l'ordre 11 là où tu l'avais laissé.

## Rapport (6 lignes)
SHA de la déclaration amendée et nouveau PRISTINE_AFTER ; tests ; accès au carnet Kalshi
(OK ou BLOCKED) ; paris journalisés mais exclus ; essais /200 ; ce qui m'est demandé.
```
