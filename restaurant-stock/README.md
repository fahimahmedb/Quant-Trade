# Gestion de stock intelligente pour restaurants indépendants — MVP v1.1

Implémentation du brief « Gestion de stock intelligente pour restaurants
indépendants » : fiche technique → import des ventes → stock théorique →
comptage physique → écarts → suggestion de commande. Application web
mobile-first, autonome (aucune intégration tierce requise), pensée pour un
restaurant indépendant à carte fixe et établissement unique.

> Ce sous-projet vit dans le même dépôt que l'outil NASDAQ (`src/`, `scripts/`,
> `results/` à la racine) mais n'a **aucun rapport** avec lui — deux projets
> indépendants d'un même auteur, séparés dans leur propre dossier.

## Stack et choix d'architecture

- **FastAPI + Jinja2** : rendu serveur, formulaires HTML classiques qui
  fonctionnent sans JavaScript (délibéré : le comptage se fait en marchant
  dans un stockage, potentiellement avec un réseau faible — chaque zone se
  sauvegarde par son propre `<form>`, pas de round-trip JS qui échouerait
  silencieusement). Un peu de JS progressif dans `app/static/app.js`
  (sélection auto au focus, ajout de ligne dans les fiches techniques) qui
  n'est jamais requis pour que l'appli fonctionne.
- **SQLAlchemy + SQLite** (`data/restaurant_stock.db`) : suffisant pour un
  établissement unique. Le passage à PostgreSQL ne demanderait qu'un
  changement d'URL de connexion (`RESTAURANT_STOCK_DATABASE_URL`).
- **Tailwind compilé statiquement** (`app/static/tailwind.css`, généré via
  `npm run build:css`) plutôt que le CDN `cdn.tailwindcss.com` : ce dernier
  échoue silencieusement sans accès internet sortant et n'est de toute façon
  pas recommandé pour autre chose qu'un prototype jetable. Regénérer après
  toute modification de classes Tailwind dans `app/templates/` (voir
  « Développement » ci-dessous).
- **Un compte par établissement** (v1.1) : l'équipe partage un identifiant,
  la session dure 30 jours pour ne pas faire ressaisir un mot de passe les
  mains pleines. La protection est fermée par défaut — une route non
  déclarée publique redirige vers la connexion, un oubli côté routeur ne
  peut donc pas ouvrir un écran métier. Le champ « comptage par » reste
  déclaratif (texte libre) : il dit qui a compté, pas qui est connecté.
- **Migrations Alembic** (v1.1, `alembic upgrade head`) : le schéma évolue
  sans perdre les données du restaurant. `render_as_batch` est activé, SQLite
  ne sachant pas modifier une colonne en place.
- **Service worker** (`app/static/sw.js`, servi à la racine par `/sw.js`) :
  seules la coquille et les pages de comptage sont mises en cache. Le reste
  du site n'est pas disponible hors-ligne, délibérément — un écran d'écarts
  calculé sur des chiffres périmés serait pire qu'une erreur franche.
- **Saisie numérique tolérante** (`app/forms.py`) : les formulaires acceptent
  la virgule décimale française en plus du point, et toute valeur invalide
  ré-affiche le formulaire déjà rempli avec un message clair plutôt que de
  planter ou de faire tout ressaisir — important pour l'équipe visée
  (section 2 du brief : pas à l'aise avec les outils digitaux).

## Démarrage

```bash
cd restaurant-stock
pip install -r requirements.txt

# Optionnel : jeu de données de démonstration (ingrédients + fiches techniques
# d'un bistrot fictif). Ne fait rien si des ingrédients existent déjà.
python -m app.seed

# Schéma : à faire avant le premier démarrage et après chaque mise à jour.
alembic upgrade head

uvicorn app.main:app --reload
# → http://127.0.0.1:8000
```

Au premier lancement, l'application ouvre `/setup` pour créer le compte de
l'établissement. Tant qu'aucun compte n'existe, toutes les routes y mènent ;
une fois créé, `/setup` n'est plus accessible. La mise en service chez un
vrai restaurant (HTTPS, sauvegardes, restauration) est décrite dans
[`docs/exploitation.md`](docs/exploitation.md).

Un fichier d'exemple pour tester l'import des ventes se trouve dans
`sample_data/exemple_export_ventes.csv` (compatible avec les noms de plats
du jeu de données de démonstration ; une ligne "Burger" y est volontairement
non reconnue pour illustrer l'écran de rattachement manuel).

### Tests

```bash
pytest
```

128 tests. Logique métier (`app/services/` : coût matière, parsing CSV
tolérant, décrémentation du stock théorique, recalibrage après comptage,
écarts, suggestion de commande, réception et historique des prix) et
intégration HTTP (`tests/test_routers.py` — erreurs utilisateur plausibles
comme un nom en double ou un nombre mal saisi, qui doivent ré-afficher un
message clair plutôt que planter en 500). Base SQLite en mémoire, aucune
dépendance à un serveur externe. Tourne en CI sur chaque push touchant
`restaurant-stock/` (`.github/workflows/restaurant-stock-tests.yml`).

Trois fichiers méritent un mot :

| Fichier | Ce qu'il verrouille |
|---|---|
| `tests/test_nr.py` | NR-01 à NR-18, la suite de non-régression des specs V2 — un test nommé par point, pour que « ça remarchait avant » soit vérifiable |
| `tests/test_offline_counting.py` | TC-F3-01 à TC-F3-05 : contrat serveur de la file hors-ligne (rejeu, conflit à deux appareils, durée juste après 24 h, cache périmé) |
| `tests/test_offline_pwa.py`, `tests/test_nr_mobile.py` | Ce qu'aucun test serveur ne prouve : un vrai Chromium hors-ligne, et l'absence de débordement horizontal à 320/360/390 px |

Les deux derniers ont besoin de Chromium (Playwright) ; ils sont ignorés
proprement s'il est absent, la suite reste exécutable partout.

### Développement — régénérer le CSS

Après avoir modifié des classes Tailwind dans `app/templates/` :

```bash
npm install        # une fois
npm run build:css  # ou npm run watch:css pendant le développement
```

`app/static/tailwind.css` est committé (pas de build Node au démarrage de
l'appli elle-même) : oublier de le régénérer ne casse rien immédiatement,
mais les nouvelles classes utilisées ne seront pas stylées tant que le
fichier n'est pas régénéré.

## Où trouver quoi (mapping avec le brief)

| Section du brief | Code |
|---|---|
| 4.1 Fiches techniques | `app/services/recipes.py`, `app/routers/recipes.py` |
| 4.2 Import des ventes | `app/services/sales_import.py`, `app/routers/sales.py` |
| 4.3 Stock théorique | `app/services/stock.py` (journal `StockMovement`, historique visible sur `/ingredients/{id}/edit`) |
| 4.4/4.5 Comptage + écarts | `app/services/counting.py`, `app/routers/counting.py`, `/variance` |
| 4.6 Suggestion de commande | `app/services/ordering.py`, `app/routers/orders.py` |
| 5. Comptage mobile par zone | `app/templates/counting/session.html` (+ `app/static/app.js`) |
| 8. Indicateurs | `app/services/metrics.py`, page `/metrics` |

Fonctions ajoutées en v1.1 (Specs V2) :

| Fonction | Code |
|---|---|
| F1 — Réception de livraison, historique et alerte de prix | `app/services/deliveries.py`, `app/routers/deliveries.py`, `/deliveries` |
| F2 — Compte, sessions, sauvegarde, export, journal d'erreurs | `app/services/auth.py`, `app/middleware.py`, `scripts/backup.py`, `/settings` |
| F3 — Comptage hors-ligne | `app/static/sw.js`, `app/static/offline-count.js`, `POST /counting/{id}/sync` |
| F4 — Clôture des observations v1 | [`docs/observations-v1.md`](docs/observations-v1.md), `tests/test_nr.py` |

## Simplifications assumées (v1)

- **Une seule unité par ingrédient** (g, kg, mL, L ou unité), utilisée
  partout — stock, grammage des fiches techniques, coût unitaire, saisie de
  comptage. Aucune conversion automatique (ex. g ↔ kg) : un ingrédient
  suivi en grammes doit être grammé en grammes dans toutes les fiches
  techniques qui l'utilisent.
- **Résolution des plats à l'import** : par nom (insensible à la casse),
  puis par table d'alias (`DishAlias`) mémorisée dès qu'un rattachement
  manuel est fait — un même intitulé de caisse non standard n'a besoin
  d'être mappé qu'une seule fois.
- **Seuil de commande** : `alert_threshold` manuel sur l'ingrédient si
  défini, sinon dérivé de la consommation moyenne glissante (fenêtre,
  jours de sécurité et jours de couverture cible réglables sur `/settings`,
  section 4.6 et 7 du brief : recommandation toujours explicable et
  modifiable, jamais d'envoi automatique).
- **Pas de blocage sur stock négatif, mais signalé** : un stock théorique
  peut devenir négatif (casse non déclarée, erreur de saisie, vente
  important avant le premier comptage). C'est volontaire — c'est justement
  ce que le comptage physique est censé révéler, pas quelque chose à
  masquer en bloquant la saisie. Un stock théorique négatif est en
  revanche signalé explicitement (⚠ en rouge) sur l'écran de comptage et
  sur l'écran d'écarts, où le % d'écart n'aurait sinon aucun sens.

## Comptage hors-ligne — ce qui est garanti, ce qui ne l'est pas (v1.1, F3)

Le comptage se fait en réserve et en chambre froide, là où le réseau tombe.
Ce qui est promis :

- La page de comptage s'ouvre et s'utilise sans réseau, y compris après
  fermeture et réouverture de l'onglet.
- Une zone enregistrée hors-ligne est gardée sur l'appareil et repart seule
  au retour du réseau, sans action de l'utilisateur.
- Une session terminée hors-ligne garde la durée réelle du comptage, pas le
  délai avant que le réseau revienne.

Ce qui ne l'est pas, et pourquoi :

- **Le reste de l'application n'est pas disponible hors-ligne.** Un écran
  d'écarts ou de commandes servi depuis un cache afficherait des chiffres
  périmés sans le dire : une erreur franche est préférable.
- **Deux appareils sur la même session ne fusionnent pas.** La saisie la
  plus récente gagne (à l'heure de saisie sur l'appareil, pas à l'heure
  d'arrivée au serveur) et la plus ancienne est annoncée à l'écran, nommée.
  Rien n'est écrasé en silence, mais rien n'est additionné non plus.
- **Une session close depuis un autre appareil refuse les saisies en
  attente.** Le stock théorique a déjà été recalé à la clôture ; les
  appliquer après coup laisserait des lignes comptées sans mouvement de
  stock correspondant.
- **La file vit dans le stockage local du navigateur.** Vider les données du
  site ou compter en navigation privée la perd.

## Hors périmètre (identique au brief, section 6)

Intégration caisse temps réel, multi-fournisseurs, signaux externes,
HACCP complet, reporting avancé/menu engineering, multi-sites. La saisie
vocale (section 5, v1.5) n'est pas implémentée.

## Angles morts non résolus (section 9 du brief)

Deux angles morts restent ouverts, et aucun test ne peut les fermer :

1. **Le format d'import CSV** (`date,plat,quantite,prix_unitaire`, délimiteur
   `,` ou `;`, dates `JJ/MM/AAAA` ou `AAAA-MM-JJ`) est un minimum générique
   tolérant, pas calé sur un export réel de Zelty, L'Addition ou Square. À
   confronter à l'export du premier restaurant pilote, puis ajuster
   `app/services/sales_import.py`.
2. **L'ergonomie réelle du comptage.** Le pré-remplissage par zone, la taille
   des cibles tactiles et le temps que prend un comptage complet n'ont été
   vérifiés qu'au clavier et en navigateur simulé. Il faut un vrai cuisinier,
   un vrai téléphone et une vraie chambre froide — mains froides, gants,
   écran gras — pour savoir si le parcours tient. C'est le point que la
   section 5 du brief désigne comme décisif, et c'est celui qui reste.
