# Audit — la couverture du balayage inscrite dans son propre rapport (pré-enregistré)

Cycle d'**outillage documentaire**. Aucune stratégie évaluée, aucun verdict
recalculé, aucun seuil de détection touché.

Recalcul **indépendant** : cet audit ne réutilise aucune variable du balayage.
Il recompte les fichiers lui-même et compare au rapport produit.

## Contrôle 1 — le `diff` du rapport ne contient que des insertions

Les cinq lots de persistance (#416 → #427) tenaient un régime « 0 différence
octet à octet ». **Ce cycle en sort délibérément** : son objet est d'ajouter des
lignes à un rapport publié. Le pré-enregistrement le déclarait avant de commencer,
plutôt que de laisser croire que le régime tenait encore.

- lignes **ajoutées** : **41**
- lignes **supprimées ou modifiées** : **0**

**Contrôle passé — 0 suppression, 0 modification.** Tout le contenu publié
auparavant est intact ; le rapport n'a fait que gagner une section.

## Contrôle 2 — les décomptes de doublons sont inchangés

| | #427 | #428 | |
|---|---|---|---|
| séries de P&L reconstruites | 218 | **218** | ✔ |
| groupes de doublons exacts | 3 | **3** | ✔ |
| quasi-doublons | 1 | **1** | ✔ |

**Aucun décompte n'a bougé.** L'ajout est documentaire : il ne touche ni les
seuils (égalité bit-à-bit, corrélation ≥ 0,9999) ni les séries comparées.

## Contrôle 3 — cohérence des chiffres ajoutés (recomptage indépendant)

Écart toléré, fixé avant calcul : **0**.

| Grandeur | Publiée par le rapport | Recomptée par l'audit | Écart | |
|---|---|---|---|---|
| séries lues | 218 | 218 | 0 | ✔ |
| dont candidats non-ML | 208 | 208 | 0 | ✔ |
| dont séries ML / Étape D | 10 | 10 | 0 | ✔ |
| scripts de backtest non-ML | 284 | 284 | 0 | ✔ |

- somme `non-ML + ML = total` : 208 + 10 = **218** vs **218** → ✔
- taux de couverture publié : **73.2 %**

**4/4 recomptages en accord, somme cohérente.** Les chiffres
inscrits dans le rapport sont reproduits par un décompte qui n'emprunte rien
au balayage.

## Un défaut attrapé avant publication — et une correction du #427

La première rédaction de la section ajoutée écrivait :

> « **76** candidats non-ML n'ont aucun `.npz`… Ils portent un FAIL pour la
> plupart, mais ce balayage ne peut pas le vérifier. »

**Deux fautes dans une seule phrase**, l'une arithmétique, l'autre d'assertion.

1. Le **76** venait de la soustraction `284 − 208`. Les deux ensembles ne se
   correspondent pas un à un : **23** `.npz` portent le nom d'une variante
   (`*_pit_universe`, `*_russell2000`…) sans script homonyme. La différence
   ensembliste réelle est **99**, pas 76. Une soustraction
   entre deux ensembles non alignés ne compte rien.
2. « Ils portent un FAIL pour la plupart » était une **assertion non mesurée** —
   exactement le geste que ces cycles corrigent ailleurs. Le verdict est
   désormais **compté** et publié dans le tableau du rapport.

**Le #427 propage la même erreur** et doit être corrigé : son entrée de backlog
écrit « les ~76 restants sont des scripts sans `savez` portant un FAIL ». Le
chiffre exact est **99**, dont **90** FAIL, **2** PASS (les deux écartés du
#427 lui-même), **6** indéterminés et **1** sans rapport. La correction est portée
à l'entrée #428 plutôt que de réécrire une entrée déjà publiée.

## Ce que ce cycle n'a délibérément pas fait

La ligne « **Couverture 100 %** » du rapport **subsiste telle quelle**. Elle est
exacte dans son domaine — tous les fichiers trouvés ont été relus — mais isolée,
elle se lit comme une couverture du dépôt.

La corriger aurait été **modifier** une ligne existante, ce que le contrôle 1
interdit. J'ai donc **ajouté** juste en dessous la section qui dit ce que ce
100 % recouvre, plutôt que de réécrire la ligne. Le compromis est signalé ici :
le lecteur qui s'arrête au gras avant la section ajoutée peut encore se
méprendre. Réécrire cette ligne relève d'un cycle qui déclarerait la
modification, comme celui-ci a déclaré l'insertion.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| `diff` du rapport | 0 suppression | 0 | ✔ |
| décomptes de doublons | 218 / 3 / 1 | 218 / 3 / 1 | ✔ |
| cohérence des chiffres | 2/2 à écart nul | 4/4 + somme | ✔ |
| couverture inscrite au rapport | oui | oui | ✔ |

**Prédiction déductive vérifiée.** Le balayage publie désormais sa propre
portée : le lecteur n'a plus à croire que « 218 P&L reconstruits » désigne le
dépôt entier. La piste 1 du #427 est close.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
