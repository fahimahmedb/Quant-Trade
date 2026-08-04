# Pré-enregistrement — Anticipations d'inflation implicites (breakeven 10 ans), overlay défensif

**Committé AVANT tout calcul.** Cycle #200 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Le taux d'inflation anticipée implicite (breakeven, `T10YIE` — écart
entre le rendement nominal du Trésor 10 ans et le rendement réel des
TIPS 10 ans, FRED) mesure les ANTICIPATIONS DU MARCHÉ, pas un taux
observé. Une hausse rapide des anticipations d'inflation est documentée
comme un facteur de resserrement monétaire anticipé (la Fed réagit aux
anticipations, pas seulement à l'inflation réalisée) et de compression
des multiples de valorisation des actions (le taux d'actualisation des
flux futurs augmente). Distinct de TOUS les signaux de taux NOMINAUX
déjà testés dans ce backlog — niveau/pente/inversion/différentiel
(#44/#134/#149/#175/#178/#186/#187/#195) — qui portent tous sur des
rendements OBSERVÉS, jamais sur une anticipation dérivée d'un écart
nominal-réel. Distinct aussi du spread de crédit (#199, risque de
défaut d'entreprise) : ici le signal porte sur le risque
MACROÉCONOMIQUE d'inflation, pas sur le risque de crédit.

## 2. Donnée (nouvelle, à récupérer — fetch réseau)

Série FRED `T10YIE` (10-Year Breakeven Inflation Rate, quotidienne,
historique complet 2003-2026 confirmé par fetch) — gratuite, même
mécanisme que les cycles précédents. Sauvegardée dans
`data/t10yie_daily.csv`, aucune modification.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal sur le marché cible : `ffill` (calendrier du marché
  cible) puis `shift(1)` — **technique identique à `load_rate_lag()`**
  déjà utilisée aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/
  #198/#199, Règle 7.
- Seuil : **tercile EXPANDING** de `T10YIE_lag(t)` (technique établie,
  #169/#177/#183/#191/#192/#193/#195/#196/#197/#198/#199) — cohérent
  avec le traitement du #199 (niveau du spread, pas son changement).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `T10YIE_lag(t)` est dans son tercile expanding le PLUS HAUT
  (anticipations d'inflation les plus élevées — risque de resserrement
  monétaire, compression des multiples), `1,0x` sinon. **Jamais de
  levier** — design purement défensif, cohérent avec la pratique établie
  de cette famille de signaux. Coûts 5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#199)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour le niveau des taux souverains (#175/#178/#186/#187) et le
   spread de crédit (#199), un signal de NIVEAU pourrait souffrir du
   même problème structurel de désalignement avec les régimes de marché
   pertinents — les 4 derniers cycles de cette famille (#191/#195/#198/
   #199) ont tous montré un Sharpe amélioré mais un rendement
   insuffisant, schéma potentiellement amené à se répéter ici.
2. L'historique utilisable (2003+) est plus court que les signaux basés
   sur DGS10/DGS3MO (1962+), limitant le nombre de cycles économiques
   couverts, notamment absence du choc inflationniste des années 1970.
3. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/#198/
   #199, un design purement défensif sans levier compensatoire limite
   structurellement le rendement total.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
