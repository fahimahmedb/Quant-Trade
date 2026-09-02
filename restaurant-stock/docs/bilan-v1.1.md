# Bilan de sortie V1.1 « Fondations » (Specs V2, section 3)

État au terme du lot V1.1 : les quatre fonctions demandées (F1 à F4) sont
livrées et couvertes par des tests nommés. La suite complète compte
**128 tests, tous au vert**, dont NR-01 à NR-18 et TC-F1-01 à TC-F3-05.

Ce document dit trois choses : ce qui est fait et comment on le vérifie, ce
qui a été décidé en cours de route et pourquoi, et ce qui reste — dont deux
points qu'aucun test ne pourra jamais fermer à la place du pilote.

## 1. F1 — Réception de livraison et historique des prix

| Critère | État | Preuve |
|---|---|---|
| AC-F1-1 réception 3 lignes sans quitter l'écran, prix pré-remplis | Fait | `tests/test_deliveries.py` |
| AC-F1-2 stock théorique augmenté de la quantité reçue | Fait | mouvement `RECEPTION` tracé dans `StockMovement` |
| AC-F1-3 coût matière reflétant le nouveau prix | Fait | `tests/test_deliveries.py` |
| AC-F1-4 historique des prix consultable | Fait | `/ingredients/{id}/edit`, table `PriceHistory` |
| AC-F1-5 alerte à +20 %, silence à +10 % | Fait | seuil réglable sur `/settings` (`price_alert_pct`, 15 % par défaut) |
| TC-F1-01 réception nominale | Fait | |
| TC-F1-02 quantité « 2,5 » à virgule française | Fait | `app/forms.py` |
| TC-F1-03 prix à 0 refusé avec message clair | Fait | validation avant toute écriture |
| TC-F1-04 réception antidatée → acceptée + avertissement | Fait | comparaison au dernier comptage clos |
| TC-F1-05 ingrédient supprimé entre saisie et validation | Fait | message clair, aucune écriture partielle |
| TC-F1-06 deux réceptions le même jour | Fait | deux entrées distinctes dans l'historique |
| TC-F1-07 recalcul du coût d'une fiche à 4 ingrédients | Fait | |

Décision notable : **une réception est validée en entier ou pas du tout.**
Toutes les lignes sont vérifiées avant la première écriture. Un bon de
livraison à moitié saisi laisserait un stock faux sans que personne le sache.

## 2. F2 — Hébergement, compte, sauvegarde, migrations

| Critère | État | Preuve |
|---|---|---|
| AC-F2-1 accès sans session → connexion, aucune page métier | Fait | `app/middleware.py`, fermé par défaut |
| AC-F2-2 restauration d'une sauvegarde | Fait | `scripts/backup.py` (`backup`, `verify`, `restore`, `prune`) |
| AC-F2-3 montée de version, données préservées | Fait | `tests/test_migrations.py` sur base réelle |
| AC-F2-4 export CSV réimportable | Fait | export complet depuis `/settings` |
| TC-F2-01 connexion nominale | Fait | `tests/test_auth.py` |
| TC-F2-02 mot de passe erroné 5 fois → temporisation | Fait | verrouillage 5 minutes |
| TC-F2-03 session expirée → retour connexion sans perte | Fait, avec une limite | redirection vers l'écran demandé, zones déjà enregistrées intactes |
| TC-F2-04 migration ascendante puis descendante | Fait | `tests/test_migrations.py` |
| TC-F2-05 restauration chronométrée < 15 min | **À faire par le pilote** | procédure écrite dans `exploitation.md`, le chronomètre demande une vraie machine |

Limite de TC-F2-03, dite explicitement : ce qui est conservé, ce sont les
zones **déjà enregistrées**, ligne par ligne, côté serveur. Une zone tapée
mais non validée au moment où la session expire est perdue, comme n'importe
quel formulaire. Le comptage étant sauvegardé zone par zone, la perte
maximale est une zone ; la session durant 30 jours, le cas reste rare.

Décisions notables :

- **La protection est fermée par défaut.** Une route non déclarée publique
  redirige vers la connexion. Un oubli côté routeur donne donc une
  redirection, jamais un écran métier ouvert.
- **Le message d'erreur de connexion est identique** que le compte existe ou
  non : sinon le formulaire dit à un inconnu quelles adresses sont valides.
- **Le cookie n'est marqué `Secure` que derrière HTTPS**, sinon l'application
  serait inutilisable en développement local.

## 3. F3 — Comptage hors-ligne (PWA)

| Règle des specs | État | Preuve |
|---|---|---|
| Installable sur l'écran d'accueil | Fait | `manifest.webmanifest`, icônes 192/512 |
| Session poursuivie intégralement hors-ligne | Fait | `sw.js`, vérifié dans un vrai Chromium hors-ligne |
| Saisies conservées puis synchronisées, confirmation « comptage synchronisé » | Fait | `offline-count.js`, `POST /counting/{id}/sync` |
| Conflit : dernière saisie par ligne, avertissement listant les lignes | Fait | arbitrage sur l'heure de saisie, pas d'arrivée |
| Chronomètre juste hors-ligne | Fait | `ended_at` fourni par l'appareil |
| TC-F3-01 coupure à mi-comptage, 5 lignes hors-ligne, 9 au serveur | Fait | `test_offline_counting.py` + parcours navigateur |
| TC-F3-02 onglet fermé hors-ligne, brouillon récupéré | Fait | vérifié dans Chromium, pas seulement en API |
| TC-F3-03 deux appareils → avertissement, aucune ligne perdue | Fait | conflit nommé à l'écran |
| TC-F3-04 hors-ligne 24 h → durée cohérente | Fait | 40 min de comptage restent 40 min |
| TC-F3-05 cache périmé → « liste mise à jour » | Fait | empreinte de la liste affichée |

Décisions notables :

- **Seul le comptage fonctionne hors-ligne.** Le reste du site n'est pas mis
  en cache : un écran d'écarts servi depuis un cache afficherait des chiffres
  périmés sans le dire. Une erreur franche vaut mieux.
- **L'arbitrage se fait sur l'heure de saisie sur l'appareil**, pas sur
  l'heure d'arrivée au serveur. Sinon l'appareil qui retrouve le réseau en
  dernier écraserait toujours l'autre, alors qu'il a compté en premier. Une
  horloge de téléphone absurde retombe sur l'heure serveur.
- **Une session close depuis un autre appareil refuse les saisies en
  attente**, au lieu de les appliquer. Le stock a déjà été recalé à la
  clôture ; les écrire après coup laisserait des lignes comptées sans
  mouvement de stock correspondant, c'est-à-dire un écart inexplicable.
- **Ajout non demandé, assumé : la déconnexion purge les pages de comptage
  en cache.** Le téléphone de la cuisine est partagé ; sans cela, la liste de
  stock restait lisible hors-ligne après déconnexion.

## 4. F4 — Clôture des observations v1

OBS-1, OBS-2 et OBS-3 sont closes, chacune avec sa cause écrite et son test
de non-régression dédié (NR-16, NR-17, NR-18). Voir
[`observations-v1.md`](observations-v1.md).

NR-01 à NR-18 sont codés un test nommé par point, dans `tests/test_nr.py`
(NR-12, le débordement horizontal, dans `tests/test_nr_mobile.py` : il
demande un vrai navigateur à 320, 360 et 390 px). Les trois NR que les
specs signalent comme impactés par F3 — NR-06, NR-11, NR-12 — sont verts
après le lot.

## 5. Ce qui reste, et pour qui

Trois points sortent du périmètre de ce qu'un test automatique peut établir.
Ils appartiennent au pilote, pas au code.

1. **L'ergonomie réelle du comptage.** C'est la friction n°1 du brief et elle
   n'est toujours vérifiée qu'au clavier et en navigateur simulé. Il faut un
   cuisinier, son téléphone, une vraie chambre froide, mains froides et
   écran gras. Question à trancher sur le terrain : le pré-remplissage par
   zone fait-il gagner du temps, ou fait-il valider sans regarder ?
2. **Le format d'export de la caisse.** Le parseur CSV est un minimum
   générique tolérant, pas calé sur un export réel de Zelty, L'Addition ou
   Square. Il faut un vrai fichier du pilote pour savoir ce qu'il faut
   ajuster. C'est aussi le préalable à F8 (import intelligent) en V1.3.
3. **TC-F2-05, la restauration chronométrée sous 15 minutes.** La procédure
   est écrite et testée fonctionnellement ; le chronomètre demande la vraie
   machine de production.

Rien de ceci ne bloque la V1.2. Les points 1 et 2 conditionnent en revanche
la valeur de tout ce qui suit : F5 et F6 raisonnent sur des écarts et des
ventes, et un historique construit sur un import mal calé produirait des
recommandations fausses avec assurance.

## 6. Go / no-go avant mise en service

La liste de contrôle est dans [`exploitation.md`](exploitation.md), section 8.
Deux points valent d'être répétés ici :

- **Sans HTTPS, le comptage hors-ligne ne fonctionne pas** — un navigateur
  refuse d'enregistrer un service worker sur une origine non sûre, sans
  erreur visible.
- **Après un déploiement touchant `app/static/` ou le gabarit de comptage,
  incrémenter `VERSION` dans `app/static/sw.js`**, faute de quoi un téléphone
  déjà équipé continuera de servir l'ancien écran depuis son cache.
