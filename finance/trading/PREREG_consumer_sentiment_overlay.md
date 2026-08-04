# Pré-enregistrement — Indice de confiance des consommateurs (Michigan), overlay défensif contrarian

**Committé AVANT tout calcul.** Cycle #205 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

L'indice de confiance des consommateurs de l'Université du Michigan
(FRED `UMCSENT`, mensuel) est un signal d'ENQUÊTE (perception), pas
dérivé de prix/rendements/taux — angle qualitativement distinct de tout
signal déjà testé dans ce backlog. Anomalie comportementale documentée :
un sentiment EXTRÊMEMENT BAS coïncide souvent avec des points bas de
marché déjà largement intégrés dans les prix ("be greedy when others
are fearful", contrarian), tandis qu'un sentiment EXTRÊMEMENT ÉLEVÉ
(complaisance excessive) précède souvent une sous-performance relative.
Ce cycle teste la partie DÉFENSIVE de cette hypothèse contrarian (couper
en période de complaisance excessive), cohérent avec le design purement
défensif de toute la famille macro-externe de ce backlog — la partie
"lever en période de pessimisme extrême" n'est PAS testée ici (limite
reconnue à l'avance, pas un choix arbitraire post-hoc).

## 2. Donnée (nouvelle, à récupérer — fetch réseau, traitement mensuel)

Série FRED `UMCSENT` (University of Michigan: Consumer Sentiment,
mensuelle, historique complet 1952-2026 confirmé par fetch, quelques
valeurs manquantes ponctuelles — ex. déc. 1952/jan. 1953 — traitées par
suppression directe, pas d'interpolation). **Traitement causal
conservateur** : bien que la lecture finale du mois M soit publiée en
fin du mois M lui-même (délai réel plus court que le M2/DE10Y déjà
traités), le MÊME traitement conservateur qu'aux #195/#203 est appliqué
par cohérence et par prudence (décalage d'un mois calendaire complet
avant `ffill`, puis `shift(1)` jour de bourse) — choix délibérément
conservateur déclaré avant tout calcul, pas un réglage après résultat.
Sauvegardée dans `data/umcsent_monthly.csv`, aucune modification des
valeurs (hors suppression des lignes vides).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal : décalage d'un mois + `ffill` + `shift(1)` (§2),
  cohérent avec `load_rate_lag()`/le traitement mensuel déjà utilisé aux
  #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/#198/#199/#200/#202/
  #203/#204, Règle 7.
- Seuil : **tercile EXPANDING** de `UMCSENT_lag(t)` (technique établie,
  #169/#177/#183/#191/#192/#193/#195/#196/#197/#198/#199/#200/#202/#203/
  #204).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `UMCSENT_lag(t)` est dans son tercile expanding le PLUS HAUT (sentiment
  le plus élevé — complaisance excessive, risque de sous-performance
  contrarian), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#204)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour la grande majorité des signaux de NIVEAU/RÉGIME
   macro-externes déjà testés (14 hypothèses, 2 PASS niveau 1
   seulement), la probabilité de base d'un FAIL reste élevée.
2. Le sentiment élevé (complaisance) coïncide souvent avec des phases de
   croissance économique prolongée qui peuvent durer plusieurs années —
   couper l'exposition dès le tercile haut pourrait sacrifier une part
   substantielle du rendement composé, même si le signal de risque est
   économiquement valide à long terme (même mécanisme que #175/#186).
3. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/#198/
   #199/#202/#203/#204, un design purement défensif sans levier
   compensatoire limite structurellement le rendement total.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
