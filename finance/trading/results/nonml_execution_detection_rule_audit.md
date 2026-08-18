# Audit indépendant — règle de détection de l'exécution (#496)

Le backtest classe par **AST**. Cet audit reconstruit les mêmes comptes
par **expressions régulières** — une route qui ne partage aucune ligne
avec la première.

## Recalcul par la route indépendante

| Grandeur | Rapport | Route regex | Accord |
|---|---|---|---|
| scripts analysés | **969** | **969** | **oui** |
| scripts « exécute un tiers » | **30** | **33** | **NON** |
| angle mort du #494 | **8** | **6** | **NON** |
| cibles distinctes | **11** | **3** | **NON** |

> **Désaccord entre les deux routes.** Il est publié tel quel :
> - *scripts « exécute un tiers »* : AST **30**, regex **33** — écart **3**.
> - *angle mort du #494* : AST **8**, regex **6** — écart **2**.
> - *cibles distinctes* : AST **11**, regex **3** — écart **8**.

**La cause est mesurée, pas invoquée.**

- **2** script(s) où le motif ne vit que dans un
  **littéral de chaîne** : la regex y voit un porteur, l'AST un
  **citeur** — c'est la distinction du #473, et l'AST a raison ;
- **2** script(s) appellent `subprocess.Popen([sys.executable, …])`,
  une forme que la **condition 1 ne nomme pas** : elle dit « la forme
  du #494 », et le #494 cherchait `subprocess.run`.
  **C'est un troisième angle mort — celui de ma règle corrigée** ;
- pour les **cibles**, la route regex ne collecte que celles de la
  condition 2 ; elle ignore par construction les littéraux passés à
  `subprocess` et la condition 3.

L'implémentation du backtest accepte aussi `check_call`/`check_output`,
que le texte pré-enregistré ne nomme pas — **dépassement mesuré** :
scripts concernés dans le dépôt : **0**.

> **Rien n'est reclassé ici.** La règle a été figée avant mesure ;
> `Popen` est enregistré comme angle mort, pas absorbé après coup.

## Les témoins sont-ils bien ceux du #494 ?

- noms listés par le #496 : **4**
- noms listés par le #494 : **4**
- listes identiques : **OUI**

## Le backtest exécute-t-il quelque chose ?

- appels `subprocess` sur `sys.executable` dans son AST : **0**
- modules `nonml_*` du dépôt qu'il importe : **0**
- fichiers de l'arbre git modifiés hors ce cycle : **0**

> **Rien n'a été exécuté.** Le script lit des sources et écrit son
> seul rapport ; l'arbre ne porte aucune trace d'un tiers.

## Les chiffres du rapport sont-ils calculés ?

- nombres en gras dans le rapport : **30**
- dont **tapés en dur** dans le backtest : **0**


## L'écart est-il **entièrement** attribué ?

- écart sur « exécute un tiers » : **3**
- scripts porteurs d'une cause nommée (citeur ou `Popen`) : **4**
- l'écart tient dans les causes nommées : **OUI**

> Ce test **borne**, il n'**identifie** pas : il vérifie qu'il reste assez
> de causes nommées pour couvrir l'écart, non que ce sont les bonnes.
> Une réconciliation nom par nom exigerait la liste AST, que cet audit
> s'interdit d'utiliser pour rester indépendant. **Limite assumée.**

## Verdict

1. tout écart entre routes tient dans des causes nommées — **OUI**.
2. les témoins du #496 sont exactement ceux du #494 — **OUI**.
3. le backtest n'exécute aucun tiers et ne salit pas l'arbre — **OUI**.
4. aucun chiffre du rapport n'est tapé en dur — **OUI**.

**AUDIT OK**

Anti-lookahead **sans objet au sens temporel** : ce cycle ne lit aucune
série de prix. Son équivalent ici est **l'inertie** — vérifiée ci-dessus.
