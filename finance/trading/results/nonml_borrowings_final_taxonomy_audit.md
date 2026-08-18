# Audit indépendant — taxonomie des emprunts (#508)

Le backtest teste les sources **dans un ordre de priorité**. Un ordre
peut masquer une erreur : si le test **A** est trop permissif, **B** et
**C** ne sont jamais atteints. Cet audit calcule les **quatre
appartenances indépendamment**, sans ordre, puis reconstruit la classe.

## Le reclassement sans ordre

| Classe | Rapport | Audit | Accord |
|---|---|---|---|
| **A** | **11** | **11** | **oui** |
| **B** | **26** | **26** | **oui** |
| **C** | **2** | **2** | **oui** |
| **D** | **0** | **0** | **oui** |

- classes en désaccord : **0**
- effectif recalculé : **39** ; annoncé : **39**

## Trois propriétés que le backtest n'énonce pas

- **monotonie** : tout emprunt en **A** ou **B** satisfait aussi
  « existe » — **OUI**
- emprunts en **A** dont le nombre n'existe nulle part : **0** *(doit valoir 0 : être au sujet implique exister)*
- la classe **D** vide est-elle légitime ? tous les nombres existent : **OUI**

> **D vide n'est pas un artefact de test trop large** : chaque nombre
> emprunté est réellement présent quelque part dans le dépôt. Le
> test d'existence est **nu** — donc permissif — mais son résultat
> est cohérent avec la monotonie ci-dessus.

## Ce que cet audit ne prouve pas

Il valide l'**ordre** de la taxonomie, pas ses **définitions**. Les deux
routes partagent la règle contextuelle du #502 : si « ≥ 2 mots-clés dans
±200 caractères » est un mauvais test de « même sujet », **les deux se
trompent ensemble**. Le rapport le dit déjà ; l'audit ne le contredit
pas.

Il ne se prononce pas non plus sur le **contrôle échoué** : que les deux
résidus du #505 tombent en **B** est un **fait**, et le pré-enregistrement
en faisait un **FAIL**. Rien ici ne le rattrape.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **35** ; dont **tapés en dur** : **0**

## Verdict

1. les deux routes donnent les mêmes quatre comptes — **OUI**.
2. l'effectif recalculé égale l'effectif annoncé — **OUI**.
3. la monotonie A/B ⊂ existe est vérifiée — **OUI**.
4. la classe D vide n'est pas un artefact — **OUI**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (5/5)

> **Un audit qui passe sur un cycle qui échoue n'est pas une
> contradiction** : le cycle échoue son **contrôle pré-enregistré**,
> l'audit vérifie que son **classement** est cohérent. Les deux peuvent
> être vrais en même temps, et le backlog doit porter les deux.

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
