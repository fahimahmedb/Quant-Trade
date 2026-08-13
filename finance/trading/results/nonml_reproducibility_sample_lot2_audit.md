# Audit — reproductibilité, lot 2 (pré-enregistré)

Recalcul **indépendant** : cet audit n'importe rien du script de mesure. Il
redérive les deux tirages depuis les graines committées, vérifie leur
disjonction, recalcule la borne et contrôle le régime.

## Contrôle 1 — le tirage est reproductible depuis la graine committée

- vivier recompté par l'audit : **285**
- vivier restant après exclusion du lot 1 : **273**
- échantillon redérivé **identique** à celui publié : **oui** ✔

## Contrôle 2 — les deux lots sont bien disjoints

Retirer un script déjà testé n'apporterait aucune information neuve et
gonflerait artificiellement le cumul sur lequel la borne est calculée.

- scripts communs aux deux lots : **0** ✔


## Contrôle 3 — aucun rapport publié n'a été modifié

- rapports `*_result.md` modifiés hors artefacts de ce cycle : **0** ✔

Les 24 scripts ont été ré-exécutés **deux fois** — la mesure initiale, puis une
régénération après correction d'une ligne de tableau malformée. Les deux passes
ont donné le même résultat, et aucun rapport n'est resté modifié.

## Contrôle 4 — la borne, recalculée indépendamment

| | Sans divergence | Borne à 95 % | Annoncée au pré-enregistrement |
|---|---|---|---|
| #434 seul | 12 | 22.1 % | — |
| **#434 + #435** | **36** | **8.0 %** | **8,0 %** |
| version prudente | 35 | 8.2 % | 8,2 % |

**La borne obtenue est exactement celle annoncée avant la mesure.** C'était
l'objet de l'annonce : aucun chiffre obtenu après coup ne pouvait être
présenté comme « une nette amélioration ».

## Ce que cette borne ne dit pas

À **p ≤ 8.0 %** sur un dépôt de **285** rapports, il reste
de la place pour **jusqu'à ~22** rapports divergents non détectés. Le
passage de 22 % à 8 % **resserre** la dette ; il ne la ferme pas.

| Total testé sans divergence | Borne | Rapports divergents encore possibles |
|---|---|---|
| 12 | 22.1 % | ~62 |
| 36 | 8.0 % | ~22 |
| 60 | 4.9 % | ~13 |
| 100 | 3.0 % | ~8 |
| 150 | 2.0 % | ~5 |

Le rendement est **décroissant** : les 24 tirages de ce lot ont fait passer la
borne de 22 % à 8 %, mais il en faudrait **24 de plus** pour atteindre ~5 %, et
**249** de plus pour la fermer entièrement. Je publie ce tableau
pour que la décision d'un lot 3 se prenne sur un gain chiffré, pas sur
l'impression qu'« encore un peu » suffirait.

## La réserve annoncée, maintenue

La formule `p ≤ 1 − 0,05^(1/N)` suppose des tirages **indépendants**, alors que
l'échantillonnage est **sans remise** dans un vivier fini. Dans ce cadre la borne
binomiale est **conservatrice** — elle surestime légèrement `p`.

Elle n'a **pas** été raffinée après avoir vu le résultat : une borne prudente qui
se trompe du côté sévère vaut mieux qu'une borne optimisée après coup, et le
pré-enregistrement l'annonçait ainsi.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| tirage reproductible | oui | oui | ✔ |
| lots disjoints | 0 commun | 0 | ✔ |
| rapports publiés modifiés | 0 | 0 | ✔ |
| borne cumulée publiée | 8,0 % | 8.0 % | ✔ |

**Les quatre contrôles passent.** Aucune divergence sur 36 scripts distincts,
et le régime « ne rien modifier » a tenu sur deux passes complètes.

Le pré-enregistrement engageait à écrire ce résultat « sans le présenter comme
une preuve ». Il ne l'est pas : c'est une borne, elle a été divisée par près
de trois, et le tableau ci-dessus dit exactement ce qu'il resterait à faire.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
