# Backlog — stratégies à **mécanisme économique identifiable** + **multi-actifs**

Fil de travail distinct de `NONML_STRATEGY_BACKLOG.md` (qui a dérivé vers
l'audit du dépôt lui-même, cf. son historique #497-#515). Ce fil-ci
revient au test de stratégies proprement dit, mais restreint à deux
familles motivées par autre chose qu'un pattern statistique pur :

1. une **prime de risque** compensant un risque réellement porté (value,
   momentum, carry) ;
2. l'exploitation d'une **contrainte institutionnelle documentée**
   (rebalancements forcés d'indices, ventes fiscales de fin d'année).

**Même discipline que le reste du dépôt, sans exception** :
`PROTOCOLE_ANTI_SNOOPING.md` s'applique intégralement. Univers d'actifs et
de règles **figé et nommé avant tout calcul**. `n_trials` continue le
compte **global** déjà tenu par la batterie de validation — on ne repart
pas à 1 pour ce fil sous prétexte qu'il est nouveau. DSR et SPA obligatoires
avant toute annonce de succès. Coûts réalistes. Rapporté PASS ou FAIL sans
retuning après résultat.

## Pourquoi ce fil existe

Deux constats motivent son ouverture, tous deux déjà présents dans le
dépôt avant sa création :

- **Le momentum intra-indice a déjà été testé et a échoué** (Étape B,
  univers figé à 4 modèles, `Momentum signe rdt-10j` sous le seuil DSR).
  Ce fil ne le retestera pas tel quel — il vise le momentum
  **cross-actifs** (Asness, Moskowitz & Pedersen 2013, *Value and
  Momentum Everywhere*), jamais tenté ici.
- **L'effet fiscal de fin d'année était déjà identifié, mais bloqué** —
  `january_effect_lowprice_overlay_pit_universe` est mis de côté dans
  `nonml_battery_backfill_lot_audit.py` (`SET_ASIDE`) au motif « schéma
  panier, la batterie exige le schéma indiciel ». C'est l'item **#432**
  du backlog principal, en attente d'arbitrage depuis plusieurs cycles.

## L'univers d'actifs — figé ici, avant tout calcul

| Jambe | Instrument | Rôle économique | Source | Historique récupéré |
|---|---|---|---|---|
| Actions | NDX / Composite | risque actions | déjà en dépôt | depuis 1985 / 2021 |
| Obligations longues US | `TLT` (proxy) | prime de duration, réagit à l'inverse des actions en stress | **récupéré** (`data/tlt_daily.txt`) | 30/07/2002 → 06/08/2026, 6044 séances |
| Or | `GLD` (proxy) | valeur refuge, prime de rareté | **récupéré** (`data/gld_daily.txt`) | 19/08/2016 → 18/08/2026, 2512 séances |
| Dollar US | `UUP` (proxy) | divergence de politique monétaire, flux de refuge | **récupéré** (`data/uup_daily.txt`) | 01/03/2007 → 18/08/2026, 4898 séances |

Les trois fichiers passent `quality_report()` sans anomalie. **Contrainte
déclarée avant tout calcul** : `GLD` limite la fenêtre **commune aux quatre
jambes** à **19/08/2016 → 18/08/2026** (~10 ans) — c'est cette fenêtre, et
elle seule, que le PREREG de E3 devra utiliser pour la période multi-actifs,
sans l'ajuster après avoir vu un résultat.

### Incident de qualité de données — corrigé avant tout calcul

**TLT (première tentative) : données fabriquées, rejetées.** Le premier
fetch a synthétisé l'open/high/low à partir du close seul ("ranges
réalistes basés sur la volatilité historique" — admis explicitement par
l'agent). Vérification : ranges intra-jour jusqu'à 3% dès le 2ᵉ jour de
cotation, incompatibles avec un ETF obligataire réel. **Rejeté et
re-fetché avec consigne explicite d'interdiction de synthèse** avant tout
commit poussé. Ce cycle n'avait pas encore été poussé sur `origin` au
moment de la détection — aucune correction d'historique publié n'a été
nécessaire.

**UUP : anomalie mineure identifiée, non bloquante.** Les 10 plus fortes
valeurs de range intra-jour (jusqu'à 19,5%) sont concentrées sur les
premiers mois de cotation (2007), avec des volumes très faibles
(quelques milliers de titres) — signature typique d'un ETF nouvellement
listé et peu liquide, pas d'une fabrication. **Sans objet pour E3** : la
fenêtre commune est de toute façon bornée par `GLD` à 2016+, bien après
cette période. Signalé pour mémoire, aucune action requise.

**Leçon retenue** : `quality_report()` vérifie la cohérence interne
(high ≥ max(o,c) etc.), **pas l'authenticité**. Toute nouvelle donnée
récupérée par un agent doit être soumise à un contrôle de plausibilité des
ranges intra-jour avant d'être committée — ajouté comme pratique
systématique pour ce fil.

**Aucun autre actif ne sera ajouté à cet univers après avoir vu un
résultat.** Une extension éventuelle sera un nouveau fil, déclaré comme
tel.

## Statut

| # | Piste | Données nécessaires | Statut |
|---|---|---|---|
| E1 | Débloquer la batterie de validation pour le schéma panier (plusieurs actifs simultanés) — condition préalable à E2 | aucune nouvelle donnée, travail d'infrastructure sur `nonml_*_pass_validation_battery.py` | **à faire** |
| E2 | Effet fiscal de fin d'année sur le panier déjà préparé (`january_effect_lowprice_overlay_pit_universe`), enfin exécutable une fois E1 fait | déjà en dépôt | **bloqué sur E1** |
| E3 | Momentum cross-actifs sur le quatuor actions/obligations/or/dollar (signal : allocation vers les jambes en tendance positive, réduite/nulle sur les jambes en tendance négative) | TLT, GLD, UUP (fetch en cours) | **à faire dès que les 3 fetches sont terminés** |

## Ce que ce fil ne fait pas

- Il ne relâche **aucun** seuil du protocole anti-snooping — le prior plus
  favorable d'un mécanisme économique documenté n'exempte pas de la
  correction multi-tests.
- Il ne prétend pas se protéger contre le biais de sélection à l'échelle
  du champ entier (cf. discussion en tête de session sur le "garden of
  forking paths") — seule une performance réelle, hors-échantillon dans
  le temps, y répond.
- Il ne recommence rien depuis zéro ailleurs : il réutilise l'intégralité
  de l'infrastructure déjà auditée du dépôt (`data_loader`, walk-forward,
  DSR, SPA, batterie de validation).

## Prochaine étape immédiate

E1 (déblocage schéma panier) ne dépend d'aucune donnée externe et peut
démarrer dès qu'un cycle se déclenche sur ce fil — PREREG dédié avant
toute modification du code de la batterie.
