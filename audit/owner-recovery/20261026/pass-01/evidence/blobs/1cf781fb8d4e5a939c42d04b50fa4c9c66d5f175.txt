# Exploitation — mise en service chez un vrai restaurant (Specs V2, F2)

Tant que l'application tourne sur un poste de développement, rien de ceci
n'est nécessaire. Dès qu'un restaurant y saisit ses données, tout ce qui
suit est une condition d'existence du pilote, pas une option.

## 1. HTTPS obligatoire

L'application ne termine pas TLS elle-même : elle se place derrière un
reverse proxy (Caddy, nginx, Traefik) qui s'en charge.

```bash
# Uvicorn derrière un proxy : --proxy-headers pour que l'application sache
# que la requête d'origine était en HTTPS (le cookie de session n'est marqué
# Secure que dans ce cas).
uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips='*'
```

Exemple minimal avec Caddy, qui obtient et renouvelle le certificat seul :

```
stock.mon-restaurant.fr {
    reverse_proxy 127.0.0.1:8000
}
```

Vérification : `https://…` répond, `http://…` redirige vers HTTPS, et le
cookie `resto_session` porte bien `Secure` et `HttpOnly`.

HTTPS conditionne aussi le comptage hors-ligne : un navigateur refuse
d'enregistrer un service worker sur une origine non sûre. Sans certificat,
`/counting` cesse d'être utilisable sans réseau, en silence et sans erreur
visible. À vérifier après mise en service : ouvrir `/counting`, couper le
réseau du téléphone, recharger — la page doit s'afficher avec le bandeau
« Hors ligne ».

Le proxy ne doit pas mettre `/sw.js` en cache longue durée : l'application
le sert déjà avec `Cache-Control: no-cache` et `Service-Worker-Allowed: /`,
il suffit de ne pas écraser ces en-têtes.

## 2. Variables d'environnement

| Variable | Rôle | À définir en production |
|---|---|---|
| `RESTAURANT_STOCK_SECRET_KEY` | Signature des sessions | **Oui.** Sans elle, une clé est générée dans `data/secret_key` ; suffisant sur une seule machine, mais à fixer explicitement dès qu'il y a plusieurs instances ou des redéploiements fréquents. |
| `RESTAURANT_STOCK_DATABASE_URL` | Base de données | Optionnel (SQLite par défaut dans `data/`). |
| `RESTAURANT_STOCK_COOKIE_SECURE` | Mettre `0` **uniquement** pour un accès local en http | Non |

Génération d'une clé : `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

## 3. Premier démarrage

1. `pip install -r requirements.txt`
2. `alembic upgrade head` (ou premier lancement de l'application : les
   migrations s'appliquent au démarrage, y compris sur une base v1
   existante, qui est estampillée puis migrée sans perte).
3. Ouvrir l'application : le premier écran propose la création du compte de
   l'établissement (e-mail + mot de passe, 8 caractères minimum). Tant
   qu'aucun compte n'existe, aucune page métier n'est accessible.

## 4. Sauvegarde quotidienne

```bash
python scripts/backup.py backup     # sauvegarde + vérification + purge > 30 jours
python scripts/backup.py list       # inventaire, avec état de relecture
python scripts/backup.py restore data/backups/20260902_030000.db
```

Chaque sauvegarde est relue (`PRAGMA integrity_check` + présence des tables
métier) avant d'être déclarée bonne : une sauvegarde jamais testée ne vaut
rien. La restauration prend d'abord une copie de sécurité de la base en
place, sous `pre_restore_*.db`.

Automatisation (cron, 3 h du matin) :

```cron
0 3 * * * cd /srv/restaurant-stock && python scripts/backup.py backup >> data/backups/cron.log 2>&1
```

Les sauvegardes vivent dans `data/backups/`, hors dépôt Git. **Copier ce
dossier hors de la machine** (rsync, S3, disque externe) : une sauvegarde
sur le disque qui meurt ne sauve rien.

### Test de restauration (à faire une fois avant la mise en production)

1. Copier une sauvegarde sur un environnement de recette.
2. `python scripts/backup.py restore <fichier>` en chronométrant.
3. Ouvrir l'application : les données de la veille doivent être là.

Objectif : moins de 15 minutes (TC-F2-05).

## 5. Migrations de schéma

```bash
alembic upgrade head     # montée
alembic downgrade -1     # retour arrière d'une révision
alembic current          # révision en place
alembic check            # aucune dérive entre modèles et migrations
```

Avant chaque mise en production : jouer la montée **et** la descente sur une
copie de la base de production. La suite de tests le vérifie automatiquement
(`tests/test_migrations.py`), y compris l'absence de dérive entre les
modèles et les migrations.

## 5 bis. Déploiement d'une version qui change le comptage

Le service worker garde en cache la coquille (CSS, scripts, icônes) et les
pages de comptage. Sa version de cache n'est pas une constante à incrémenter
à la main : la route `/sw.js` (`app/main.py`, `_sw_build_version`) la calcule
au démarrage du serveur à partir du contenu réel des fichiers de la coquille
et des gabarits de comptage (`_SW_WATCHED_FILES`). Elle change donc toute
seule dès qu'un déploiement touche l'un de ces fichiers — rien à se rappeler
de faire.

L'activation du nouveau service worker supprime alors les caches de
l'ancienne version. Le seul geste qui reste au déploiement : redémarrer le
processus serveur (la version est calculée une fois à ce moment-là, pas
recalculée à chaque requête). Un simple rechargement de code sans redémarrage
(certains outils de déploiement à chaud) ne suffirait pas.

## 6. Réversibilité des données

`/settings` propose l'export complet (archive ZIP, un CSV par table) et le
réimport du catalogue sur une installation neuve. Le restaurateur repart
avec ses données s'il arrête ; aucun mot de passe ni jeton n'y figure.

## 7. Journal des erreurs

`/settings/errors` liste les 100 dernières erreurs applicatives : écran
concerné, type, message, trace technique. Aucune donnée saisie n'y est
enregistrée (pas de query string, pas de corps de requête). Les erreurs
restent aussi dans les logs du serveur : le journal ne masque rien.

## 8. Avant chaque mise en production (go / no-go, section 6.5 des specs)

- [ ] NR-01 à NR-18 verts (`pytest tests/test_nr.py tests/test_nr_mobile.py`)
- [ ] TC de la version verts (V1.1 : `pytest tests/test_offline_counting.py tests/test_offline_pwa.py`)
- [ ] Le processus serveur redémarre au déploiement (la version de cache du
      service worker se recalcule à ce moment-là, pas autrement)
- [ ] Sauvegarde de la veille restaurée avec succès
- [ ] Migration testée en montée et en descente sur copie de production
- [ ] Retour arrière écrit et exécuté une fois en recette
- [ ] Test terrain de la section 6.4 réalisé

Un seul rouge = no-go.
