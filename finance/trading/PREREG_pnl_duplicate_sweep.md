# Pré-enregistrement — balayage des doublons de P&L du backlog

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.
Cycle de **diagnostic** : aucune stratégie n'est évaluée, aucun paramètre choisi.

## Pourquoi

Le #403 a établi que deux entrées du backlog comptées séparément depuis leur
création — `sma200_leaders_overlay` (#33) et `leaders_trend_union_overlay` (#41)
— désignent la **même stratégie** : le signal « indice à ≥ 95 % de son plus haut
252 j » est un sous-ensemble strict de « indice au-dessus de sa SMA200 » sur les
10273 séances disponibles, donc leur union est identiquement égale à SMA200 seul.
Leurs P&L sont bit-à-bit identiques.

Rien ne garantit que ce soit le seul cas. La question ouverte au #403 est traitée
ici : **combien de paires du backlog produisent le même P&L ?**

L'enjeu n'est pas cosmétique. Le nombre d'essais `n_trials` entre directement
dans le **Deflated Sharpe Ratio** et dans les corrections de multiplicité. Des
doublons le **gonflent** — ce qui, contre-intuitivement, rend le critère DSR
**plus sévère** qu'il ne devrait, donc défavorable aux candidats. Le corriger
peut donc *assouplir* un seuil : raison de plus pour fixer la méthode d'avance
plutôt que de la choisir en voyant les résultats.

## Univers balayé

**Tous** les fichiers `results/*_pnl.npz` du dépôt — 165 à ce jour — sans
restriction de préfixe ni de famille. Un balayage restreint à la liste attendue
est précisément ce qui m'a fait manquer un foyer au #390 et un portage au #395.

Huit schémas coexistent ; le P&L net est reconstruit selon le schéma détecté :

| Schéma | Reconstruction |
|---|---|
| `pos, r_asset` | `pos·r_asset − |Δpos|·c` |
| `pos, r_asset, r_alt` | jambe double : `pos·r_asset + (1−pos)·r_alt − |Δpos|·c` |
| `pnl_gross_ov, turn_ov` (panier) | `pnl_gross_ov − turn_ov·c` |
| `pnl_candidate, turn_candidate` | `pnl_candidate − turn_candidate·c` |
| `pnl_candidate` seul | tel quel |
| schémas ML (`pos_primary`, `var_trials`, …) | jambe `pos` uniquement |

Tout fichier dont le schéma n'est pas reconnu est **compté et listé**, jamais
ignoré en silence.

## Critères — fixés avant exécution

Deux séries sont comparées uniquement si elles ont la **même longueur**.

- **Doublon exact** : `np.array_equal` sur le P&L net reconstruit.
- **Quasi-doublon** : non exact, mais corrélation de Pearson **≥ 0,9999**.
  Ce seuil vise les transformations triviales (renommage, changement d'échelle,
  coût marginal différent), pas la ressemblance économique. Deux stratégies
  réellement distinctes qui corrèlent à 0,999 ne sont **pas** un doublon et ne
  seront pas comptées comme tel.

## Critère de succès — chiffré

Ce cycle est un diagnostic ; son succès ne se mesure pas en Sharpe.

1. **Couverture** : 100 % des `.npz` traités ou explicitement listés comme
   schéma non reconnu. Toute couverture < 100 % est un échec du balayage et sera
   rapportée comme tel.
2. **Vérification** : chaque paire signalée est confirmée ou rejetée **par
   lecture des deux scripts**, pas sur la seule foi du chiffre. Le rapport
   distingue les deux.
3. **Correction** : le nombre d'essais indépendants du backlog est corrigé de
   `nombre de groupes de doublons confirmés − nombre de groupes`, c'est-à-dire du
   nombre d'entrées surnuméraires.

**Aucune correction du DSR n'est appliquée dans ce cycle.** Le décompte corrigé
est publié ; le rejouer sur les batteries existantes serait une seconde
opération, à faire dans un cycle dédié et déclaré. Modifier `n_trials` après
avoir vu quels candidats en bénéficieraient serait exactement le geste que le
protocole interdit.

## Prédiction — non tranchée

Je n'annonce aucun nombre attendu de doublons. Le seul cas connu (#33/#41) a été
trouvé par accident, pas par recherche : je n'ai aucune base pour extrapoler.

## Engagements

1. Résultat rapporté **tel quel**, y compris si le balayage ne trouve rien —
   auquel cas le cycle aura coûté un tour pour confirmer une absence, ce qui est
   un résultat et sera écrit comme tel.
2. Aucun seuil ajusté après lecture des paires trouvées.
3. Les paires signalées mais **rejetées** après lecture sont listées avec leur
   raison, au même titre que les confirmées.
