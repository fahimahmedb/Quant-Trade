# Un `.npz` pour `tom_decomposition_overlay`, et le balayage enfin possible (pré-enregistré)

**Cycle de MODIFICATION**, huitième après les #445 → #451, et le premier
depuis longtemps à toucher une **stratégie** plutôt qu'un instrument.

## La question qui ne pouvait pas être posée

`tom_decomposition_overlay` porte un **PASS** (variante A, fin de mois seule,
4/5 marchés) et ne produisait **aucun `.npz`** : elle échappait au balayage de
doublons (#446). Le **#8** (`tom_overlay`, ToM complet — **union** des deux
sous-fenêtres) est PASS lui aussi et **possède** le sien.

La variante A est une **sous-fenêtre** de cette union. Si les deux séries sont
très proches, **deux essais n'en font qu'un**, et le décompte d'hypothèses qui
nourrit le DSR de la famille est faussé.

## Le résultat qui compte

**Corrélation entre la variante A et le #8 : +0.963497.**

Seuil de quasi-doublon du balayage : **0.9999**.

**Elle reste en dessous.** Les deux séries partagent l'essentiel de leur
exposition sans être interchangeables : la décomposition du ToM isole
bien un effet distinct de l'union du #8.

**Ma prédiction est vérifiée** — j'attendais une corrélation élevée mais
sous le seuil. Elle l'est, et je n'en tire aucun mérite : c'était la
déduction la plus banale, et elle aurait pu être fausse.

## Ce que le balayage dit maintenant qu'il la voit

- groupes de doublons **exacts** contenant la série : **0**
- paires **quasi-doublons** l'impliquant : **0**

**Aucun appariement.** La série est isolée dans le dépôt — au seuil du
balayage, aucune autre stratégie ne la reproduit.

## Les critères

| | Critère | État |
|---|---|---|
| 1 | diff confiné à l'insertion annoncée | ✔ (+14 / −0) |
| 2 | **les chiffres publiés ne bougent pas** | ✔ |
| 3 | concordance `.npz` / rapport | ✔ (+0.53) |
| 4 | le balayage voit la série | ✔ |

Le critère 2 est le plus exigeant des quatre : **ajouter une sauvegarde ne
calcule rien**, donc le rapport régénéré devait être identique **au
caractère près** à sa baseline épinglée. Il l'est.

### **PASS**

**Ce cycle ne requalifie rien** : ni le verdict de la variante A, ni celui du
#8, ni le décompte d'essais de la famille ToM. Il rend une question
**mesurable**, et publie la mesure.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).