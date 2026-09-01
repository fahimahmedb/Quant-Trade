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

- **FastAPI + Jinja2 + HTMX** : rendu serveur, pages HTML classiques
  (fonctionnent sans JavaScript) avec quelques fragments HTMX/JS pour le
  confort (voir `app/static/app.js`). Pas de SPA, pas d'étape de build front —
  un seul processus à déployer.
- **SQLAlchemy + SQLite** (`data/restaurant_stock.db`) : suffisant pour un
  établissement unique. Le passage à PostgreSQL ne demanderait qu'un
  changement d'URL de connexion (`RESTAURANT_STOCK_DATABASE_URL`).
- **Tailwind via CDN** : gain de vitesse pour le MVP. À remplacer par un
  build Tailwind classique si le projet dépasse le stade pilote.
- Pas d'authentification : un seul restaurant, équipe partageant le même
  appareil. Le champ « comptage par » est déclaratif (texte libre), pas un
  compte utilisateur.
- Pas de migrations (Alembic) : les tables sont créées par
  `Base.metadata.create_all` au démarrage. À ajouter avant tout usage en
  production réelle avec des données à préserver entre versions du schéma.

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

23+ tests couvrent la logique métier (`app/services/`) : calcul du coût
matière, parsing CSV tolérant (délimiteur `,`/`;`, dates FR/ISO, décimales à
virgule), décrémentation du stock théorique, recalibrage après comptage,
calcul des écarts, logique de suggestion de commande. Base SQLite en mémoire,
aucune dépendance à un serveur externe.

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
