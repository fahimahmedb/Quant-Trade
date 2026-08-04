# Pré-enregistrement — Année 2 du cycle électoral (mid-term), overlay coupé

**Committé AVANT tout calcul.** Cycle #176 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec le #30

Le "presidential cycle" (Hirsch 1986) documente l'année 3 du mandat
(pré-électorale) comme historiquement la plus forte — déjà testé et
**PASS (5/5)** au #30 (overlay LEVÉ). La même littérature documente
l'année 2 (mid-term, année des élections législatives de mi-mandat)
comme historiquement la plus FAIBLE (incertitude politique, cycle du
resserrement monétaire post-élection). Ce cycle teste l'hypothèse
**inverse et complémentaire** : un overlay COUPÉ (pas levé) pendant
l'année de mid-term devrait réduire l'exposition à une période
statistiquement plus faible et donc améliorer Sharpe/rendement.

## 2. Marchés testés (figés, périmètre ajusté par rapport à l'idée
initiale — décision prise ICI, avant tout calcul, aucun résultat n'existe)

La ligne de backlog proposait "NDX 40 ans (~10 cycles)" uniquement.
Décision prise avant calcul : Russell 2000, S&P 500 et DAX ont aussi un
historique suffisant (≥9 cycles électoraux chacun) pour ce test — seul le
**Composite est exclu** (5 ans, moins d'un cycle électoral complet,
insuffisant). **4 marchés testés** : NDX, Russell 2000, S&P 500, DAX —
cohérent avec le seuil ≥3/4 déjà utilisé pour les cycles à 4 marchés de
ce backlog (#166/#168/#169/#170). **Même prudence que le #30** : ces 4
marchés ne sont PAS des essais indépendants (même cycle électoral
américain affectant simultanément tous les indices mondiaux via la
politique monétaire globale) — signalé, pas un obstacle au test.

## 3. Mécanisme (figé, réutilisation stricte Règle 7 de la détection du #30)

- Détection 100% data-driven, réutilisation directe de la logique
  `preelection_mask` du #30 (`(annee+1)%4==0`), adaptée à l'année de
  mid-term : `midterm_mask(t) = (année(t) % 4) == 2` (élections
  législatives de mi-mandat : 2018, 2022, 2026… — 2 ans après chaque
  année d'élection présidentielle, divisible par 4).
- `position(t) = 0.5x` pendant l'année de mid-term (CUT, valeur déjà
  établie au #175 pour un plancher symétrique à CAP=2.0x autour de 1.0x),
  `1.0x` sinon. Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé)

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (une fenêtre calendaire fixée avant calcul, un plancher
réutilisé du #175, un critère multi-marché, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Réduire l'exposition à 0.5x pendant ~25% du temps (1 année sur 4)
   coûte structurellement du rendement composé si le marché monte quand
   même pendant cette période dans la majorité des cycles observés
   (Hirsch documente une TENDANCE statistique, pas une garantie
   systématique par cycle) — même mécanisme de risque que le #175.
2. Comme au #30, un petit nombre de cycles (9-10) limite la puissance
   statistique — un ou deux cycles atypiques (ex. 2002, 2022, années de
   krach ou de forte reprise) peuvent dominer le résultat.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
