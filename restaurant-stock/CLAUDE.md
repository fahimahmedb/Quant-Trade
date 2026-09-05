# restaurant-stock — repères pour toute session (Claude Code)

Lu automatiquement par Claude Code au démarrage de toute session travaillant
dans ce dépôt, y compris un sous-agent lancé en tâche de fond. But de ce
fichier : qu'un sous-agent n'ait pas besoin qu'on lui réexplique les
conventions du projet dans chaque prompt — juste la tâche précise.

## Le projet

App FastAPI + Jinja2 + SQLite pour la gestion de stock d'un restaurant
indépendant (comptage physique, écarts, suggestions de commande). Mobile
d'abord, francophone de bout en bout (utilisateurs, code produit, docs).

- `app/routers/*.py` — un routeur par écran/domaine
- `app/services/*.py` — logique métier, testée indépendamment des routes
- `app/templates/**/*.html` — Jinja2, un fichier par écran
- `app/templating.py` — tous les filtres Jinja custom (voir plus bas)
- `app/static/tailwind_src.css` → compilé vers `tailwind.css` (`npm run build:css`)
- `tests/` — pytest ; `docs/` — bilans et récapitulatifs par lot

## Commandes utiles

```
python3 -m pytest tests/ -q              # suite complète (~110s)
python3 -m pytest tests/<fichier>.py -q  # ciblé — toujours faire ça d'abord
npm run build:css                        # après toute modif de tailwind_src.css ou tailwind.config.js
```

## Direction visuelle V1.2 (« révision 2 »)

Fond blanc partout, pas de cartes ni d'ombres. Vocabulaire de composants :
`.ligne` / `.champ` (numérique) / `.select` (texte) / `.btn` + `.btn-principal`
`.btn-secondaire` `.btn-tertiaire` / `.pastille*` / `.barre-onglets`.

**Une seule couleur de marque : bleu marine (`--accent`)**, y compris le
héros de l'accueil (tranché après coup — voir `docs/generalisation-v1.2.md`).
Trois couleurs sémantiques seulement : `--accent` (action), `--alerte`
(problème réel : écart, rupture — jamais un choix de routine), `--valide`
(favorable réel). Un manquant de stock est en alerte ; un surplus est en
encre neutre, pas en alerte (ce n'est pas une perte).

**Le favorable domine, le défavorable reste secondaire** (section 3 de la
spec) : un héros ou un résumé mène toujours par ce qui va bien (ex. « X/Y
conformes ») avant de mentionner une perte, jamais l'inverse.

**AC-U6-1** : un ingrédient sans écart n'occupe pas une ligne complète —
replié sous un compte consultable (`partials/variance_table.html`), pas
supprimé. À vérifier sur tout nouvel écran qui liste des écarts, y compris
les listes qui n'utilisent pas ce partiel (ex. l'accueil a sa propre boucle).

**`counting/session.html`** (l'écran de saisie tactile actif) est
délibérément non retouché par la généralisation V1.2 — il attend son propre
écran témoin et sa propre validation, pas un lot parmi d'autres. Ne pas le
redessiner en passant sur un autre écran.

## Filtres Jinja custom (`app/templating.py`) — ne pas réinventer

- `qty` — quantité, 0 ou 2 décimales selon si entier
- `qty_lisible(unit)` — quantité + unité ensemble, convertit g→kg / mL→L
  au-delà de 1000 (un cuisinier ne dit pas « 0,05 kg »). Préférer à
  `{{ x | qty }} {{ unit.value }}` partout où l'unité de référence peut
  dépasser 1000.
- `euros` — toujours 2 décimales (4 si ça arrondirait à 0,00 €)
- `decimal_fr(min_decimals=0)` — valeur d'un `<input type="text"
  inputmode="decimal">` (PAS `type="number"` : la spec HTML impose le point
  décimal dessus, aucun navigateur ne le francise, quel que soit `lang`).
  Une chaîne déjà formée passe telle quelle (cas d'un formulaire ré-affiché
  après erreur) — ne jamais faire down-stream d'un routeur qui pré-formate
  déjà la valeur en chaîne, sinon ce filtre ne peut plus rien corriger.
  `min_decimals=2` pour un prix (cohérence avec `euros`), 0 par défaut
  (une quantité ou un nombre de jours n'a pas besoin de zéros de remplissage).
- `pluriel(n)` — `""` à n==1, `"s"` sinon. Toujours ça, jamais `(s)` entre
  parenthèses ni `{{ 's' if x > 1 }}` (faux à x==0). Existe aussi comme
  fonction Python importable (`from app.templating import pluriel`) pour
  les messages flash construits dans les routeurs, pas seulement les gabarits.
- `datetime_fr` / `date_fr` — jamais `strftime` à la main dans un gabarit.

## Piège Jinja récurrent (trouvé 8 fois avant qu'un test générique l'attrape)

```
{{ x }} chose{{ x | pluriel }}
{% if y %}, {{ y }}{% endif %}
```
Le saut de ligne avant `{% if %}` laisse un espace s'afficher avant la
virgule (« 13 lignes , 1 plat… »). Toujours `{%- if %}` (trim) quand un
bloc conditionnel qui suit un texte commence par une ponctuation collée.
Gardé sous contrôle par `test_no_stray_space_before_a_comma_from_an_untrimmed_jinja_if`
dans `tests/test_v1_2_coherence.py` — si ce test échoue, c'est ce piège.

## Discipline de test (non négociable, établie par le porteur du projet)

1. **Un correctif = un test qui échoue sur l'ancien code.** Après avoir
   écrit le test, annuler temporairement le correctif (`git diff`/`git
   stash` du fichier concerné, ou commenter), lancer le test, confirmer
   qu'il échoue, puis restaurer le correctif et confirmer qu'il passe.
   Ne jamais déclarer un test « de régression » sans avoir fait cette
   vérification — un test qui n'a jamais pu échouer ne prouve rien.
2. **Suite ciblée d'abord.** `python3 -m pytest tests/<fichier>.py -q`
   pendant le développement. La suite complète (`tests/`) ne tourne qu'une
   fois à la fin, jamais en boucle — elle prend ~110s.
3. Tests browser (Playwright) seulement quand le bug ne peut être vu QUE
   dans un vrai navigateur (rendu CSS, interaction tactile, ce qu'un client
   HTTP ne verrait pas). Sinon, `TestClient` (`seeded_client`/`anonymous_client`
   dans `tests/conftest.py`) suffit et est bien plus rapide.
4. Un bug trouvé en relisant une capture d'écran mérite le même traitement
   qu'un bug trouvé en code : test nommé, non-vacuité prouvée, expliqué
   dans le message de commit — pas juste corrigé en silence.

## Pour un sous-agent qui reçoit une tâche découpée depuis ce dépôt

- Reste strictement dans les fichiers listés par ton brief. Le découpage
  en agents parallèles suppose zéro recouvrement de fichiers — sortir du
  périmètre casse cette hypothèse pour les autres agents en cours.
- Si ton brief référence un filtre/une fonction qui n'existe pas encore
  dans ta copie de travail (`git log` en retard sur la branche principale),
  dis-le clairement plutôt que de le réimplémenter en double — un
  changement partagé committé séparément doit être récupéré (`git fetch`
  + `cherry-pick`), pas dupliqué.
- Ne lance pas `npm run build:css` sauf si tu ajoutes une classe Tailwind
  réellement nouvelle (vérifie d'abord — la plupart des composants existent
  déjà dans `tailwind_src.css`).
- Ne commit pas, ne push pas — laisse les changements dans l'arbre de
  travail ; l'agent principal collecte et committe.
