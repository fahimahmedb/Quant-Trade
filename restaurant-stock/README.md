# Gestion de stock intelligente pour restaurants indépendants — MVP v1

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
- Pas d'authentification : un seul restaurant, équipe partageant le même
  appareil. Le champ « comptage par » est déclaratif (texte libre), pas un
  compte utilisateur.
- Pas de migrations (Alembic) : les tables sont créées par
  `Base.metadata.create_all` au démarrage. À ajouter avant tout usage en
  production réelle avec des données à préserver entre versions du schéma.
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

uvicorn app.main:app --reload
# → http://127.0.0.1:8000
```

Un fichier d'exemple pour tester l'import des ventes se trouve dans
`sample_data/exemple_export_ventes.csv` (compatible avec les noms de plats
du jeu de données de démonstration ; une ligne "Burger" y est volontairement
non reconnue pour illustrer l'écran de rattachement manuel).

### Tests

```bash
pytest
```

40+ tests : logique métier (`app/services/`, coût matière, parsing CSV
tolérant, décrémentation du stock théorique, recalibrage après comptage,
écarts, suggestion de commande) et intégration HTTP (`tests/test_routers.py`
— erreurs utilisateur plausibles comme un nom en double ou un nombre mal
saisi, qui doivent ré-afficher un message clair plutôt que planter en 500).
Base SQLite en mémoire, aucune dépendance à un serveur externe. Tourne aussi
en CI sur chaque push touchant `restaurant-stock/`
(`.github/workflows/restaurant-stock-tests.yml`).

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
| 4.3 Stock théorique | `app/services/stock.py` (journal `StockMovement`) |
| 4.4/4.5 Comptage + écarts | `app/services/counting.py`, `app/routers/counting.py`, `/variance` |
| 4.6 Suggestion de commande | `app/services/ordering.py`, `app/routers/orders.py` |
| 5. Comptage mobile par zone | `app/templates/counting/session.html` (+ `app/static/app.js`) |
| 8. Indicateurs | `app/services/metrics.py`, page `/metrics` |

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
- **Pas de validation de stock négatif** : un stock théorique peut devenir
  négatif (casse non déclarée, erreur de saisie). C'est volontaire — c'est
  justement ce que le comptage physique et l'écran d'écarts sont censés
  révéler, pas quelque chose à masquer en bloquant la saisie.

## Hors périmètre (identique au brief, section 6)

Intégration caisse temps réel, multi-fournisseurs, signaux externes,
HACCP complet, reporting avancé/menu engineering, multi-sites. La saisie
vocale (section 5, v1.5) n'est pas implémentée.

## Angles morts non résolus (section 9 du brief)

Le format d'import CSV (`date,plat,quantite,prix_unitaire`, délimiteur `,`
ou `;`, dates `JJ/MM/AAAA` ou `AAAA-MM-JJ`) est un minimum générique tolérant,
pas calé sur un export réel de Zelty/L'Addition/Square — à confronter au
premier restaurant pilote et ajuster `app/services/sales_import.py` en
conséquence. Le pré-remplissage du comptage par zone n'a pas été testé avec
un vrai cuisinier.
