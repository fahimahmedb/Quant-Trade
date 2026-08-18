# Audit indépendant — valeurs suspectes cherchées aux rapports (#504)

Le backtest identifie les rapports d'un cycle par le **nom de stratégie**
extrait de sa section. Cet audit les identifie par la **date
d'introduction git** : les rapports d'un cycle sont ceux dont le premier
commit tombe entre son `PREREG_` et le suivant. **Même question, source
d'identification différente** — et c'est le point faible du #504.

## Le rattachement, recoupé par les dates

- cycles vérifiés : **8**
- dont les rapports trouvés par **nom** tombent bien dans la **fenêtre
  temporelle** du cycle : **8**
- en désaccord : **0**

- `PREREG_` datés par cette route : **480** *(un compte nul
  signalerait que la route ne mesure rien — le premier jet de cet audit
  passait `finance/trading/PREREG_` à `git log`, qui n'est pas un chemin :
  il rattachait **0** cycle et le critère l'absolvait quand même.)*

## Trois propriétés que le backtest n'énonce pas

- les quatre classes forment une **partition** : **OUI**
- l'effectif (**13**) égale les valeurs suspectes du #503 (**13**) : **OUI**
- résidus dont le nombre apparaît **quelque part** dans `results/` : **5** sur **5**

> Ces résidus **existent ailleurs dans les rapports**, mais pas dans
> ceux du cycle qu'ils citent. Cela ne les innocente pas : un nombre
> qui traîne partout dans un dépôt de cette taille ne prouve rien —
> c'est exactement la faiblesse que le **#501** avait mesurée.

## Ce que cet audit ne prouve pas

Les deux routes partagent la **règle contextuelle** du #502. Leur accord
valide le **rattachement cycle → rapport**, pas l'idée qu'un recouvrement
de mots-clés vaut identité de sujet. **Aucun des cinq cycles #500-#504
n'a établi qu'un seul emprunt soit faux** — ils ont établi ce qu'on ne
peut pas conclure.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **36** ; dont **tapés en dur** : **0**

## Verdict

1. les quatre classes forment une partition — **OUI**.
2. l'effectif égale les valeurs suspectes du #503 — **OUI**.
3. le rattachement par nom est recoupé par les dates (**8**/**8**) — **OUI**.
4. les **5** résidus sont re-cherchés dans tout `results/` — **OUI**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (5/5)

Anti-lookahead **sans objet au sens temporel** pour les prix ; la
datation employée ici est **strictement rétrospective** — premier commit
d'ajout, jamais l'état courant.
