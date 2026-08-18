# Audit indépendant — confrontation par le contexte (#502)

Le backtest mesure le recouvrement sur une **fenêtre de ±200 caractères**. Cet audit le remesure sur la **phrase**
qui contient l'occurrence — un découpage **sémantique**, pas métrique.

## Le recouvrement, remesuré à la phrase

- emprunts dont le nombre est **présent** dans la section : **22**
- confirmés par la **fenêtre** (rapport) : **8**
- confirmés par la **phrase** (ici) : **5**

- écart : **+3**

> **La phrase est plus stricte que la fenêtre**, et c'est attendu :
> ±200 caractères débordent sur les phrases voisines. Le
> sens de l'écart **confirme** que la fenêtre est une borne
> supérieure, non un compte exact.

## Quatre propriétés que le backtest n'énonce pas

- les cinq classes forment une **partition** (**39** = **39**) : **OUI**
- la table de transition somme à l'effectif (**39**) : **OUI**
- **confirmé + présent sans contexte** = nombres présents dans la
  section (**22**) : **OUI**
- aucun « contexte indisponible » n'a ≥ 2 mots-clés : **OUI**

## Ce que cet audit ne prouve pas

Les deux découpages partagent la **même notion de mot-clé** et le **même
seuil de recouvrement**. Leur accord valide le **découpage du contexte**,
**pas** l'idée qu'un recouvrement de mots vaut identité de sujet. Cette
idée reste une **convention**, et le rapport le dit.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **74** ; dont **tapés en dur** : **0**

## Verdict

1. le recouvrement à la phrase ne contredit pas la fenêtre — **OUI**.
2. les cinq classes forment une partition — **OUI**.
3. la table de transition somme à l'effectif — **OUI**.
4. confirmé + sans contexte = présents dans la section — **OUI**.
5. la classe « contexte indisponible » est cohérente — **OUI**.
6. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (6/6)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
Son équivalent ici est **l'inertie**, vérifiée ci-dessus.
