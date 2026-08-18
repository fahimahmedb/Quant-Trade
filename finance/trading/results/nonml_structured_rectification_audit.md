# Audit indépendant — détecteur structurel de rectification (#513)

Le #513 conclut qu'**aucun détecteur ne passe**. Une conclusion négative
a une faiblesse propre : elle peut venir d'un **détecteur cassé** plutôt
que d'une impossibilité. Cet audit monte donc le **témoin positif** —
l'inverse de celui du #512.

## Le corpus synthétique, où la réponse est connue

Quatre sections fabriquées :

- `#900` — cible, sans rien de particulier ;
- `#901` — **titre** : « La justification du #900 est **fausse** » ;
- `#902` — **span en gras** : « Le verdict du #900 est réfuté… » ;
- `#903` — **aucune** référence, **aucun** marqueur *(piège à faux
  positifs)*.

| Détecteur | Attendu | Trouvé | Correct |
|---|---|---|---|
| **S1** (titres) | `[900]` | `[900]` | **OUI** |
| **S2** (gras) | `[900]` | `[900]` | **OUI** |

- faux positif sur `#903` : **S1 non**, **S2 non**

> **Les deux détecteurs fonctionnent.** Ils retrouvent exactement ce
> qu'on a mis dans le corpus et n'inventent rien sur la section
> piège. **Leur échec sur le vrai registre vient donc du registre,
> pas du code** — la conclusion négative du #513 tient.

## Les quatre taux, recalculés sur le vrai registre

| Détecteur | Liste | Rapport | Audit |
|---|---|---|---|
| **S1** | réel | **3,9 %** | **3,9 %** |
| **S1** | témoin | **16,5 %** | **16,5 %** |
| **S2** | réel | **4,5 %** | **4,5 %** |
| **S2** | témoin | **13,3 %** | **13,3 %** |

- grandeurs en désaccord : **0**

## Ce que cet audit ne prouve pas

Le témoin positif montre que les détecteurs **savent voir** une
rectification écrite sous les deux formes prévues. Il ne montre **pas**
qu'une rectification s'écrive toujours ainsi : si le registre les
exprime le plus souvent **en prose ordinaire**, aucun des deux ne les
verra — et c'est précisément ce que le #513 conclut.

**Les deux cycles se rejoignent donc sur un point qu'aucun n'a prouvé
seul** : ce n'est pas que la rectification soit rare, c'est qu'elle
n'est pas **formatée**.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **23** ; dont **tapés en dur** : **0**

## Verdict

1. le témoin positif est monté et publié — **OUI**.
2. S1 retrouve exactement la rectification attendue — **OUI**.
3. S2 retrouve exactement la rectification attendue — **OUI**.
4. aucun faux positif sur la section piège — **OUI**.
5. les quatre taux du rapport sont recalculés à l'identique — **OUI**.
6. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (6/6)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
