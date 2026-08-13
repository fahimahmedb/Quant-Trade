# Audit — échantillon de reproductibilité (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## Contrôle 1 — le tirage est reproductible à partir de la graine publiée

- éligibles : **285** — graine **20260813** — taille **12**
- tirage redérivé identique à celui publié : **oui** ✔

Le tirage n'a donc pas été choisi : n'importe qui rejouant la graine sur le
vivier d'alors obtient les mêmes douze noms.

**Un piège d'auto-référence a dû être écarté**, et il est signalé plutôt que
corrigé en silence : ce cycle crée lui-même un couple script + rapport qui,
laissé dans le vivier, le ferait passer de 285 à 286 et **décalerait le tirage**.
Le vivier est donc reconstruit tel qu'il était **au moment du tirage**, en
excluant les artefacts de ce cycle. Sans cette exclusion, la graine ne redonne
pas les mêmes noms — ce qui aurait fait échouer le contrôle pour une raison
purement mécanique.

## Contrôle 2 — aucun rapport publié n'a été modifié

- `results/*_result.md` modifiés dans l'arbre de travail : **0**

**Aucun.** La restauration systématique a fonctionné : douze scripts ont été
ré-exécutés, douze rapports réécrits puis remis à l'identique. Le régime
annoncé — « ce cycle mesure, il ne publie aucune correction » — est tenu.

## Contrôle 3 — le résultat brut

- identiques : **12** / 12
- divergents : **0**

## La prémisse du pré-enregistrement était fausse

C'est le **résultat principal de ce cycle**, et il porte contre lui.

Le pré-enregistrement affirmait :

> « Les **244** autres n'ont jamais été ré-exécutés depuis leur publication, alors
> que le code partagé a évolué entre-temps. »

**Vérification faite après coup — et qui aurait dû l'être avant.** Le commit
`e00d817` — *2026-08-12 Correction de la composition dans 208 backtests indiciels* — a touché **208** scripts d'un coup.

| | Nombre |
|---|---|
| scripts de backtest | **287** |
| **touchés depuis le 12/08/2026** | **285** |

Autrement dit : **la quasi-totalité du corpus a été régénérée un à deux jours
avant ce cycle.** Les rapports ne sont pas d'anciens documents dont on teste la
dérive — ils viennent d'être réécrits par leur propre code.

### Ce que le 12/12 mesure réellement

**Il mesure** que le corpus est, aujourd'hui, cohérent avec son code : douze
ré-exécutions indépendantes redonnent l'octet près. Ce n'est pas rien — un
générateur non déterministe, une dépendance à l'horloge ou à l'ordre des fichiers
se serait vu ici.

**Il ne mesure pas** ce que le pré-enregistrement annonçait : la dérive d'anciens
rapports face à un code qui a bougé. Cette question-là reste **ouverte et
intestable en l'état**, parce que la correction de masse du 12/08 a effacé
l'écart qu'il aurait fallu mesurer.

Un taux de **100 %** annoncé sans cette précision aurait donné à ce cycle un
poids qu'il n'a pas. C'est la sixième fois qu'une affirmation non vérifiée se
révèle fausse (#417, #420, #425, #426, #428, celle-ci) — et la deuxième, après
le #428, où c'est le cycle lui-même qui l'attrape avant que le chiffre ne soit
survendu.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| tirage reproductible depuis la graine | oui | oui | ✔ |
| rapports publiés modifiés | 0 | 0 | ✔ |
| classement de chaque script | 12/12 | 12/12 | ✔ |
| taux publié tel quel | oui | 100 % | ✔ |

Les quatre critères sont tenus. **Mais la portée du résultat est plus étroite que
ce que le pré-enregistrement lui prêtait**, et c'est ce qu'il faut retenir du
cycle — pas le 100 %.

Aucune prédiction chiffrée n'avait été formulée ; il n'y a donc rien à compter
comme vérifié.
