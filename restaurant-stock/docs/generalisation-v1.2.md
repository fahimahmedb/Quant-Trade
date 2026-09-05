# Généralisation V1.2 — de « Ok généralise le » à la couleur unifiée

Ce document couvre tout ce qui a été fait depuis l'instruction « Ok généralise
le » : étendre la direction visuelle validée sur les deux écrans témoins
(accueil + comptage, lot 1) au reste de l'application, puis corriger les
incohérences que cette généralisation a rendues visibles. Cinq commits,
tous sur `claude/restaurant-stock-management-mvp-6oq43e` :

| Commit | Contenu |
|---|---|
| `6b575c3` | Lot 2 — écarts, commandes, catalogue (ingrédients, fiches techniques) |
| `6c34823` | Lot 3 — ventes, livraisons |
| `36f282a` | Lot 4 — réglages, indicateurs, authentification, comptage (accueil/résumé) |
| `0bd6bc8` | Cohérence — couleur unique, séparateurs, AC-U6-1, virgule, identité |
| `695a4d6` | Correctif — prix pré-rempli de /deliveries/new encore au point décimal |

Suite de tests : **182 → 216** au fil des deux relectures (sections 2 et 4),
toujours au vert à chaque commit. L'écran de comptage actif
(`counting/session.html`) n'a pas été touché : il garde sa réparation
antérieure et attend son propre passage dédié, comme prévu dès le début de
cette généralisation.

## 1. Lots 2 à 4 — extension mécanique de la direction validée

Chaque écran restant est passé sur le même vocabulaire que les deux écrans
témoins : fond blanc, `.ligne`/`.champ`/`.select`/`.btn*`, filet fin aligné
sur le texte plutôt qu'un encadré, trois couleurs sémantiques réservées à
leur usage (accent = action, alerte = problème réel, valide = favorable
réel). Introduit à cette occasion : la distinction `.select` (texte) vs
`.champ` (numérique, aligné à droite, chasse fixe), et les badges de
décision (Acceptée/Modifiée/Rejetée) posés sur valide/neutre, jamais sur
alerte pour un état de routine.

Trouvé et corrigé en généralisant, avant même la relecture par capture :

- `variance_table.html` utilisait encore `text-encre-doux`, un jeton
  supprimé par la révision précédente.
- Classes mortes ponctuelles (`rounded-full`, `w-40`, `w-28`) issues de
  l'ancienne échelle Tailwind, remplacées par les équivalents actuels.
- `self.title()` avait été auto-dérivé en grand titre 34 px sur tous les
  écrans hors accueil (lot 4) : ça faisait disparaître le lien de
  déconnexion partout ailleurs, et débordait sur un titre dynamique
  (`/sales/imports/{id}`). Revenu au bloc d'en-tête simple, avec l'explication
  écrite dans `base.html` pour ne pas retomber dans le même piège.
- `offline-count.js` référençait encore deux classes des systèmes visuels
  abandonnés (bandeau hors-ligne, compteur de progression) — invisible côté
  gabarit puisque le bug vit uniquement dans le JavaScript.
- Bloc d'alias transitoire de `tailwind.config.js` (`white`, `gray-500`,
  `emerald-600`…) supprimé une fois son dernier usage disparu.
- `POST /counting/start` déclarait `counted_by: str = ""` sans `Form(...)` :
  FastAPI le lisait comme paramètre de requête, jamais comme champ de
  formulaire. Le nom du compteur n'avait **jamais** été enregistré via
  l'écran de démarrage, depuis la toute première version du projet.
- `metrics/dashboard.html` affichait « Indicateurs (section 8 du brief) »
  depuis le tout premier commit — une référence interne jamais nettoyée.

Chaque correctif ci-dessus est couvert par un test qui échoue sur le code
précédent (vérifié par `git stash` avant/après), pas seulement par une
relecture visuelle.

## 2. Cohérence — ce qu'une vue d'ensemble a révélé

Les captures des sept écrans du lot 4 posées côte à côte ont fait apparaître
des défauts invisibles écran par écran :

**Couleur de marque unique.** Le héros de l'accueil était vert (repris du
prototype, jamais validé — un commentaire explicite le disait dans le code),
alors que tous les boutons et liens des vingt écrans migrés étaient bleu
marine (`--accent`). Deux identités à l'échelle de l'app. Tranché en faveur
du bleu partout, y compris le héros : plus petit changement (un seul bloc à
modifier contre vingt), et ça évite une seconde collision — un héros vert
aurait aussi fait doublon avec `--valide` (le succès), déjà vert.

**Séparateurs.** `variance_table.html` utilisait `divide-filet`, une classe
Tailwind construite sur un nom de couleur supprimé depuis la révision
précédente. Sans erreur de compilation (Tailwind ignore silencieusement un
nom inconnu), elle retombait sur `currentColor` : un filet noir bord à bord,
au lieu du filet clair aligné sur le texte utilisé partout ailleurs.

**AC-U6-1 (signalé trois fois).** Un ingrédient sans écart recevait la même
ligne complète (nom, quantités, pourcentage) qu'un vrai problème — sur 9
ingrédients ça passe, sur 40 les vrais écarts se noient. Les lignes à
0,00 € sont maintenant repliées sous un compte consultable
(« 6 ingrédients conformes, sans écart »), sans perte d'information.

**Bouton de fichier natif.** « Choose File » / « No file chosen » suivent la
langue du navigateur, jamais le `lang="fr"` de la page — aucun moyen de les
franciser en CSS. Remplacé par un `<label>` habillé qui déclenche le vrai
`<input>` (masqué mais accessible), avec le nom du fichier réécrit en JS à
la sélection ; fonctionne sans JavaScript (le `<label>` ouvre le sélecteur
nativement), seul le nom affiché ne se met pas à jour sans script.

**Virgule décimale.** Un `<input type="number">` impose le point décimal et
l'interdiction du séparateur de milliers, quel que soit `lang` — Chromium ne
le francise jamais. Un commentaire antérieur affirmait le contraire,
jamais vérifié sur un vrai navigateur. Passés en `type="text"
inputmode="decimal"` avec un nouveau filtre `decimal_fr`, sur les six
champs concernés (réglages, ingrédients, fiches techniques, livraisons,
commandes) — l'écran de comptage actif garde son `type="number"`, sa
correction attend le passage dédié à cet écran.

**Pluriels.** Le raccourci « (s) » (« ligne(s) », « suggestion(s)… ») a été
remplacé par un vrai accord partout où il restait : gabarits, messages
flash construits dans les routeurs, et le bandeau hors-ligne écrit en JS.

**Identité.** Le repli « Stock » (avant tout compte, ou établissement sans
nom saisi) devient « Stock resto » — déjà le nom du produit dans le
manifest PWA, jamais réutilisé ailleurs. Couleurs du manifest (fond/thème)
réalignées sur le blanc actuel (elles dataient d'un système visuel antérieur
au blanc).

**Trouvé en corrigeant les pluriels : un espace parasite avant une virgule**
(`{{ x }}\n  {% if y %}, z{% endif %}` laisse l'espace d'indentation Jinja
atterrir avant la ponctuation — « 13 lignes , 1 plat… »). Present dans
**sept gabarits**, dont un jamais touché par cette généralisation
(`ingredients/form.html`, l'historique des prix d'achat) : trouvé par un
test au motif générique, pas par relecture écran par écran.

## 3. Correctif isolé — prix pré-rempli de /deliveries/new

Une dernière relecture des captures a montré « 1.2 €/kg » malgré la
conversion en `type="text"` + `decimal_fr`. Cause : le routeur formatait
déjà le prix en chaîne (`_price_input_value`, un reliquat de l'ancien
`<input type="number">`) avant que le gabarit ne le voie — `decimal_fr`
reçoit alors une chaîne déjà faite et la laisse passer telle quelle (pensé
pour une ressaisie après une erreur de validation, pas pour une valeur déjà
mise en forme ailleurs). Supprimé : le routeur fournit maintenant un
nombre, `decimal_fr` fait tout le formatage à un seul endroit.

## 4. Second passage — ce qu'une deuxième relecture a révélé

Une deuxième relecture, sur les captures déjà corrigées par la section 2, a
trouvé six défauts supplémentaires — quatre commits, tous sur
`claude/restaurant-stock-management-mvp-6oq43e` :

| Commit | Contenu |
|---|---|
| `54b5123` | AC-U6-1 sur l'accueil : les ingrédients conformes ne comblent plus la liste |
| `427d402` | Réception : date en français, plus d'ingrédient pré-sélectionné, prix à 2 décimales |
| `2e47112` | Commandes : U8 (poids des actions, phrase lisible, précision sensée) |
| `2431042` | Comptage : le résumé mène par la conformité, plus par la perte |

Suite de tests : **206 → 216**.

**AC-U6-1 sur l'accueil.** La règle posée section 2 (un ingrédient conforme
replié sous un compte consultable) n'avait été appliquée qu'à
`variance_table.html` — le partiel partagé par `/variance` et le résumé de
comptage. L'accueil a sa propre boucle (« Derniers écarts ») avec son propre
filtre côté routeur (`app/routers/dashboard.py`) : un ingrédient sans écart
ne s'y affiche plus du tout au-delà des cinq premiers vrais écarts.

**Date de réception en anglais.** `<input type="date">` affiche sa valeur
dans le format du **navigateur**, pas celui de la page (`lang="fr"` n'a
aucun effet sur ce rendu natif, et `toLocaleDateString()` a exactement le
même défaut). Le sélecteur natif reste — c'est le meilleur clavier possible
sur mobile — mais une ligne en clair calculée en JS (« 5 septembre 2026 »)
lève toute ambiguïté à côté, sans dépendre de la langue du navigateur.

**Commandes — critère U8.** Trois défauts sur le même écran : « Valider »
et « Rejeter » n'avaient pas le même poids visuel (rejeter une suggestion de
routine ne doit pas être teinté alerte — l'alerte est réservée à un vrai
problème) ; l'explication était un dump de champs bruts (stock, conso.,
seuil) plutôt qu'une phrase ; la précision affichée dépassait le gramme utile
(« 728,4137 g »). Corrigé ensemble : `btn-secondaire` symétrique sur les deux
boutons, une phrase (« 1,62 kg suggérés : il reste 728 g, vous en consommez
~470 g/jour »), et `qty_lisible` partout où la quantité peut dépasser 1000 g.

**Résumé de comptage — le favorable doit dominer.** Le résumé ouvrait sur
l'écart total valorisé (un chiffre en alerte, en grand), avant même de dire
combien d'ingrédients étaient conformes — l'inverse de la section 3 de la
direction, déjà respectée par le héros de l'accueil. Le résumé affiche
maintenant d'abord « X/Y conformes » au format `.titre-ecran`, l'écart total
ensuite, plus bas et dans un format plus modeste.

**Trouvé au passage, même commit :** le total « brut » de `/metrics`
n'était accompagné d'aucune explication (deux chiffres proches, rien pour
dire pourquoi ils diffèrent) — une phrase ajoutée en dessous. Et la propre
boucle de l'accueil (« Derniers écarts ») affichait encore les grandes
quantités en grammes bruts (« 12 672 g ») au lieu de basculer en kilo comme
le reste des écrans depuis la section 2 — même défaut que sur
`variance_table.html`, mais sur le gabarit qui ne le partage pas.

**Trois lignes de réception toutes pré-remplies sur le même ingrédient.**
Chaque ligne du formulaire de réception proposait « Farine » par défaut
(premier ingrédient de la liste) : valider les trois lignes sans y prêter
attention pouvait tripler cet ingrédient au lieu de recevoir trois produits
différents. Chaque `<select>` part maintenant sur un choix explicite
(« Choisir un ingrédient »), rien de pré-sélectionné.

## 5. Ce qui reste

- **`counting/session.html`** (l'écran de saisie tactile actif) : direction
  visuelle non retouchée par cette généralisation, y compris son propre
  `type="number"` sur les quantités saisies — décision explicite, pas un
  oubli. C'est la friction n°1 signalée du projet ; elle mérite son écran
  témoin et sa propre validation, pas un lot de plus parmi d'autres.
- Un écart de logique noté au passage, hors du périmètre de cette
  généralisation : sur `/orders`, la comparaison acceptée-vs-modifiée se
  fait contre `suggested_quantity` brute alors que le champ affiché est
  arrondi à 2 décimales — une suggestion à décimales longues, validée sans
  changement, peut s'enregistrer comme « modifiée ». Pas corrigé ici (hors
  du signalement initial), à reprendre si ça se confirme en usage réel.

## 6. Captures

Les captures d'écran de chaque étape sont dans `docs/captures-v1.2/`, à
l'état final (couleur unifiée + toutes les corrections des deux relectures) :
création de compte, accueil, comptage (accueil et résumé, replié et
déplié), écarts, commandes, réceptions (liste et nouvelle réception),
fiches techniques, ingrédients, ventes, réglages, indicateurs.
