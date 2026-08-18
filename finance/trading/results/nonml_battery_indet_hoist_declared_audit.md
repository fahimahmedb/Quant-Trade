# Audit adversarial — le hissage déclaré (#491)

Un cycle qui exécute un geste **déjà validé par le précédent** n'apprend
rien sur le geste. **L'audit vérifie donc ce qui restait ouvert.**

## 1. La sortie a-t-elle vraiment changé ?

Le rapport annonce un **changement de sortie**, pas un simple
déplacement. Route : compter les **écritures à profondeur 0** — celles
qui paraissent quoi qu'il arrive.

- écritures inconditionnelles **avant** : **41**
- écritures inconditionnelles **après** : **42**
- variation : **+1**

> **Confirmé : une ligne de plus paraît désormais quoi qu'il arrive.**
> Le rapport avait raison de refuser le mot « déplacement » — un
> lecteur verra maintenant `**0**` là où il ne voyait rien.

## 2. La prédiction réfutée est-elle publiée sans atténuation ?

Une prédiction chiffrée fausse par une ligne blanche est la plus facile
à présenter comme « essentiellement vérifiée ». **Contrôle textuel :**

| Contrôle | Résultat |
|---|---|
| le tableau marque la prédiction 1 réfutée | **OUI** |
| le rapport refuse l'atténuation | **OUI** |
| il nomme la cause exacte (un séparateur redondant) | **OUI** |
| il en tire une conséquence sur le #490 | **OUI** |
| le résultat sur la règle est dit non informatif | **OUI** |

> **La réfutation est publiée telle quelle**, avec sa cause, et sans
> la formule « essentiellement vérifiée » que le rapport écarte
> explicitement.

## 3. Le périmètre est-il tenu ?

- fichiers modifiés hors la cible : **0**
- rapport de la cible : **inchangé**

> **Un seul fichier touché, aucun rapport régénéré.** Le geste est
> resté dans son périmètre.

## 4. Le dépôt entier a-t-il été recompté ?

Un cycle pourrait ne recompter que sa cible et présenter le résultat
comme global. **Contrôle : le rapport publie-t-il des totaux à deux
chiffres, incompatibles avec un script isolé ?**

- chiffres relus dans le tableau : **[40, 13, 9]**
- compatibles avec un **recomptage du dépôt entier** : **OUI**

> **Les totaux dépassent largement ce qu'un seul script peut porter.**
> Le recomptage est bien global.

## Verdict

**CONCORDANT** — le **changement de sortie**
est confirmé par une route indépendante, la **prédiction réfutée est
publiée sans atténuation**, le **périmètre est tenu**, le recomptage est
**global**, et **5/5**
contrôles de transparence sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).