# Pré-enregistrement — Spread de crédit corporate (Baa-10 ans), overlay défensif

**Committé AVANT tout calcul.** Cycle #199 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

L'écart de rendement entre les obligations d'entreprises notées Baa
(qualité d'investissement, mais la plus basse du segment) et le Trésor
10 ans (`BAA10Y`, FRED, Moody's) est un indicateur de risque de CRÉDIT
d'entreprise très documenté : son élargissement précède ou accompagne
systématiquement les phases de stress sur les actifs risqués (le marché
exige une prime plus élevée pour détenir du risque de défaut). Distinct
de la volatilité implicite/réalisée déjà testée (#9/#31/#165/#191) et
des taux SOUVERAINS SANS RISQUE déjà testés (niveau/pente/inversion/
différentiel, #44/#134/#149/#175/#178/#186/#187/#195) : ici le signal
capture spécifiquement le risque de DÉFAUT D'ENTREPRISE, jamais exploité
dans ce backlog.

## 2. Donnée (nouvelle, à récupérer — fetch réseau, correction pré-calcul)

**Correction avant tout calcul** : la piste proposée au backlog visait
initialement la série FRED `BAMLH0A0HYM2` (ICE BofA US High Yield
Index OAS), mais le fetch effectué via ce mécanisme réseau ne renvoie
que ~3 ans d'historique (2023-08-07→aujourd'hui) au lieu de l'historique
complet attendu (normalement 1996+) — anomalie du service de fetch, pas
une propriété voulue de la série. **Substituée par `BAA10Y`** (Moody's
Seasoned Baa Corporate Bond Yield Relative to Yield on 10-Year Treasury,
FRED, historique complet 1986-2026 confirmé via fetch), un indicateur de
risque de crédit tout aussi standard et même plus classique en
littérature académique — cette substitution est faite AVANT toute
écriture de PREREG ou de script, aucun résultat n'existe encore à ce
stade (Règle 2 : correction légitime avant calcul). Sauvegardée dans
`data/baa10y_daily.csv`, aucune modification des valeurs.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal sur le marché cible : `ffill` (calendrier du marché
  cible) puis `shift(1)` — **technique identique à `load_rate_lag()`**
  déjà utilisée aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/
  #198, Règle 7.
- Seuil : **tercile EXPANDING** de `BAA10Y_lag(t)` (technique établie,
  #169/#177/#183/#191/#192/#193/#195/#196/#197/#198).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `BAA10Y_lag(t)` est dans son tercile expanding le PLUS HAUT (spread de
  crédit le plus large — stress de crédit élevé), `1,0x` sinon.
  **Jamais de levier** — design purement défensif, cohérent avec la
  pratique établie de cette famille de signaux. Coûts 5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#198)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour le niveau/direction des taux souverains (#175/#178/#186/
   #187), un signal de NIVEAU (même s'il s'agit ici d'un spread de
   crédit et non d'un taux sans risque) pourrait souffrir du même
   problème structurel de désalignement avec les régimes de marché
   pertinents.
2. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/#198, un
   design purement défensif sans levier compensatoire limite
   structurellement le rendement total.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
