# Audit — reproductibilité des rapports publiés (pré-enregistré)

Recalcul **indépendant** : cet audit n'importe rien du script de mesure. Il
redérive le tirage depuis la graine committée, vérifie que le régime « aucun
rapport modifié » a tenu, et borne ce que 12 tirages autorisent à conclure.

## Contrôle 1 — le tirage est reproductible depuis la graine committée

- éligibles recomptés par l'audit : **285**
- graine : **20260813** (fixée au pré-enregistrement, avant tout tirage)
- échantillon redérivé **identique** à celui publié : **oui** ✔

Le tirage n'a donc pas été choisi : n'importe qui peut le refaire à partir du
pré-enregistrement seul, sans faire confiance au script de mesure.

**Une subtilité attrapée par ce contrôle avant tout commit** : le vivier doit
être reconstruit *tel qu'il était au tirage*. Ce cycle produit lui-même un
`nonml_reproducibility_sample_result.md`, ce qui ajoutait son propre nom au
vivier (285 → 286) et **décalait tout le tirage**. Une première version de cet
audit concluait donc à tort au désaccord. Les artefacts du cycle courant sont
désormais exclus explicitement — un tirage n'est reproductible que si son
vivier l'est aussi.

## Contrôle 2 — aucun rapport publié n'a été modifié

Ré-exécuter un script **réécrit** son rapport ; le pré-enregistrement exigeait
une sauvegarde puis une restauration à l'identique.

- rapports `*_result.md` modifiés dans l'arbre de travail : **0**

**Régime tenu.** Le dépôt est dans l'état exact où ce cycle l'a trouvé.

## Contrôle 3 — la portée statistique, bornée plutôt que suggérée

Résultat : **12** identiques, **0** divergents, **0** non concluants.

Un sans-faute sur **12** tirages est tentant à lire comme « le dépôt est
reproductible ». **Il ne le démontre pas.** Si le taux réel de divergence
valait `p`, la probabilité d'observer 12 succès d'affilée serait
`(1−p)^12`. En exigeant que cette probabilité dépasse 5 % :

> **Borne supérieure à 95 % de confiance : p ≤ 22.1 %.**

Autrement dit, ces 12 tirages restent compatibles avec **jusqu'à ~22 %**
de rapports divergents dans le dépôt — soit potentiellement plusieurs dizaines
des 285 éligibles. Ce cycle écarte un problème **massif**, pas un
problème **fréquent**, et encore moins un problème rare.

Je publie cette borne parce que l'énoncé « 100 % de reproductibilité » serait,
seul, une surinterprétation d'un échantillon de 4 %.

## Contrôle 4 — le candidat dont le résultat était connu d'avance

- scripts chronométrés **avant** le pré-enregistrement : **3**
- présents dans le tirage : **1** — `halloween_effect`

Ils avaient été chronométrés pour dimensionner le délai, et s'étaient reproduits.
Ils sont **restés dans le tirage** — les exclure l'aurait biaisé — mais leur
résultat était connu. Sur les **12** testés, **11** constituent
donc une vérification réellement neuve.

En ne comptant que ceux-là, la borne se relâche à **p ≤ 23.8 %**.
C'est la lecture la plus prudente, et c'est celle que je retiens.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| tirage reproductible depuis la graine | oui | oui | ✔ |
| scripts classés | 12 | 12 | ✔ |
| rapports publiés modifiés | 0 | 0 | ✔ |
| taux publié tel quel | oui | 12/12 | ✔ |

**Aucune divergence détectée**, et le régime « ne rien modifier » a tenu.

Le pré-enregistrement engageait à écrire ce résultat « sans le présenter comme
un exploit ». Il ne l'est pas : un échantillon de 4 % qui ne trouve rien
**réduit** l'inquiétude sans l'éteindre, et la borne ci-dessus dit de combien.

La dette n'est pas soldée — elle est **mesurée pour la première fois**, et son
ampleur reste encadrée plutôt que connue.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
