# Étendre la règle de verdict aux rapports de batterie (pré-enregistré)

Défaut trouvé au #457 **en cherchant autre chose**. La règle unifiée, taillée
sur les rapports de **stratégie**, répondait « indéterminé » sur tous les
rapports de batterie.

## L'effet, sur tout le dépôt

- fichiers `.md` examinés : **1449**
- **reclassés** : **120**
- dont rapports de **batterie** : **120**
- dont rapports **hors batterie** : **0**

## Les rapports de batterie

- total dans le dépôt : **121**
- désormais **FAIL** : **120**
- désormais **PASS** : **0**
- encore « indéterminé » : **1**

> **Aucun rapport de batterie ne porte un PASS RENFORCÉ.** Sur les
> **121** que compte le dépôt, **pas un seul** n'a jamais
> franchi les cinq contrôles.

Le #457 l'avait établi sur les 29 qu'il faisait passer ; c'est vrai sur
**l'ensemble du dépôt**. **Prédiction vérifiée.**

## Critère 3 — aucun rapport de stratégie reclassé

**Aucun.** Le risque réel de cette modification — reclasser un rapport de
stratégie contenant par hasard cette formule — ne s'est pas matérialisé.
**Prédiction vérifiée.**

## Critère 1 — diff confiné

`nonml_verdict.py` : **+7 / −0**, une seule branche
insérée dans `porte_verdict`.

**Confiné : OUI.**

## Le reproche que je m'étais adressé d'avance — maintenu

Le pré-enregistrement disait, **avant** toute mesure :

> *Cette branche est taillée sur une formulation connue, comme la couche
> « étiquette » du #448 dont la robustesse avait montré qu'elle ne servait
> qu'à un cas. C'est une règle ajustée à un corpus existant, pas une théorie
> générale de l'énoncé d'un verdict.*

**Il reste vrai maintenant que la branche fonctionne.** L'engagement 3
prévoyait de ne pas l'effacer si elle marchait bien — c'est tenu.

La seule défense honnête : elle est **déclarée**, **étroite**, **vérifiable**,
et l'alternative — laisser des centaines de rapports « indéterminés » — est
pire. Ce n'est pas une bonne règle, c'est une règle moins mauvaise que le
silence.

## Ce que ce cycle ne fait pas

- Il ne **régénère** aucun rapport : les 7 consommateurs de la règle verront
  l'effet à leur prochaine exécution, et **mélanger cet effet avec la dérive
  du dépôt** est précisément ce que les #449 et #450 ont appris à éviter.
- Il ne **change aucun verdict de stratégie** : reclasser un rapport de
  batterie, c'est **lire correctement ce qu'il dit déjà**.
- Il ne touche ni la batterie ni sa formulation.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).