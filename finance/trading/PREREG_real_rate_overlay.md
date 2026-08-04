# Pré-enregistrement — Taux réel TIPS 10 ans (DFII10), overlay défensif

**Committé AVANT tout calcul.** Cycle #202 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Le rendement des Treasury Inflation-Protected Securities (TIPS) 10 ans
(`DFII10`, FRED) mesure le taux d'intérêt RÉEL (net de l'inflation
anticipée) — le véritable coût du capital pour l'économie, distinct du
taux NOMINAL déjà testé et clos (niveau/pente/inversion,
#175/#178/#186/#187, tous FAIL) ET distinct de l'écart nominal-réel
(breakeven inflation, #200, PASS niveau 1). Une hausse rapide des taux
réels resserre les conditions financières INDÉPENDAMMENT de l'inflation
(par exemple si la Fed relève ses taux plus vite que l'inflation
n'augmente) — mécanisme économique distinct de celui du #200, jamais
exploité dans ce backlog.

## 2. Donnée (nouvelle, à récupérer — fetch réseau)

Série FRED `DFII10` (10-Year Treasury Inflation-Indexed Security,
Constant Maturity, quotidienne, historique complet 2003-2026 confirmé
par fetch) — gratuite, même mécanisme que les cycles précédents.
Sauvegardée dans `data/dfii10_daily.csv`, aucune modification.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier — identique au #200)

- Alignement causal sur le marché cible : `ffill` (calendrier du marché
  cible) puis `shift(1)` — **technique identique à `load_rate_lag()`**
  déjà utilisée aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/
  #198/#199/#200, Règle 7.
- Seuil : **tercile EXPANDING** de `DFII10_lag(t)` (technique établie,
  #169/#177/#183/#191/#192/#193/#195/#196/#197/#198/#199/#200).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `DFII10_lag(t)` est dans son tercile expanding le PLUS HAUT (taux réel
  le plus élevé — resserrement des conditions financières réelles),
  `1,0x` sinon. **Jamais de levier**. Coûts 5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#200)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour le niveau des taux NOMINAUX (#175/#178/#186/#187), un
   signal de NIVEAU de taux (même réel) pourrait souffrir du même
   problème structurel de désalignement avec les régimes de marché
   pertinents — contrairement au #200 (breakeven, un écart et non un
   niveau, qui a PASSÉ), rien ne garantit que le même succès se
   transfère à un niveau de taux réel.
2. L'historique utilisable (2003+) est identique au #200, mêmes limites
   de couverture de crise (dot-com non couvert).
3. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/#198/
   #199, un design purement défensif sans levier compensatoire limite
   structurellement le rendement total.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
