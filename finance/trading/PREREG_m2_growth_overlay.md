# Pré-enregistrement — Croissance de la masse monétaire M2 (glissement annuel), overlay défensif

**Committé AVANT tout calcul.** Cycle #203 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

La croissance de la masse monétaire M2 (FRED `M2SL`) est un indicateur
monétariste documenté de la LIQUIDITÉ disponible dans l'économie —
distinct de tous les signaux déjà testés (taux/spreads de crédit/
inflation mesurent le PRIX du risque ou du capital, la corrélation
mesure le co-mouvement, la vol mesure l'incertitude). Une croissance de
M2 anormalement faible ou négative (contraction de liquidité) a précédé
plusieurs resserrements et corrections de marché documentés,
notamment 2022 (première contraction M2 annuelle depuis les années
1930). Jamais exploité dans ce backlog.

## 2. Donnée (nouvelle, à récupérer — fetch réseau, traitement mensuel)

Série FRED `M2SL` (Money Stock M2, mensuelle, historique complet
1959-2026 confirmé par fetch) — gratuite. **Traitement causal identique
au #195** (série mensuelle, publiée avec un délai réel) : la date de
chaque observation est décalée d'un mois calendaire complet
(`pd.DateOffset(months=1)`) AVANT le `ffill` — la valeur de mai devient
disponible à partir du 1er juin, jamais avant (le M2 du mois M n'est
matériellement connu par le marché qu'après la publication, environ un
mois après la fin du mois M). Un `shift(1)` supplémentaire (jour de
bourse) est appliqué ensuite par cohérence avec l'alignement causal
quotidien du reste du backlog. Sauvegardée dans `data/m2sl_monthly.csv`,
aucune modification des valeurs.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `M2Growth(t) = log(M2SL(t) / M2SL(t-12))` (glissement annuel, 12 mois
  — convention standard pour ce type de série, mentionnée explicitement
  dans l'idée du backlog).
- Alignement causal : décalage d'un mois + `ffill` + `shift(1)` (§2).
- Seuil : **tercile EXPANDING** de `M2Growth_lag(t)` (technique établie,
  #169/#177/#183/#191/#192/#193/#195/#196/#197/#198/#199/#200/#202).
- **Direction (choisie AVANT calcul)** : `position(t) = 0,5x` (**CUT=0,5
  réutilisé à l'identique**) si `M2Growth_lag(t)` est dans son tercile
  expanding le PLUS BAS (croissance de M2 la plus faible/négative —
  contraction de liquidité, risque accru), `1,0x` sinon — **inverse des
  cycles précédents** (qui coupaient sur le tercile le PLUS HAUT d'un
  indicateur de risque) car ici c'est la FAIBLESSE de la croissance, pas
  son niveau élevé, qui signale le risque. **Jamais de levier**. Coûts
  5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#202)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour tous les signaux de NIVEAU/RÉGIME déjà testés dans cette
   famille macro-externe (12 hypothèses, 2 PASS niveau 1 seulement),
   la probabilité de base d'un FAIL reste élevée.
2. La fréquence mensuelle avec décalage d'un mois introduit une
   staleness structurelle du signal (jusqu'à ~2 mois), comme pour le
   #195 (FAIL).
3. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/#198/
   #199/#202, un design purement défensif sans levier compensatoire
   limite structurellement le rendement total.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
