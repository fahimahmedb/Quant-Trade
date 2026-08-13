# Audit adversarial — dispersion du momentum, univers point-in-time

## 1. Recalcul de la dispersion par un chemin de code disjoint

Le backtest décale les prix par tranches NumPy puis appelle `np.std` ;
l'audit passe par `pandas.shift` puis `Series.std(ddof=1)`. Les deux chemins ne
partagent aucune ligne.

| Date | Dispersion backtest | Dispersion audit | Écart |
|---|---|---|---|
| 2015-01-02 | 0.265569 | 0.265569 | 0.00e+00 |
| 2017-04-25 | 0.370175 | 0.370175 | 0.00e+00 |
| 2019-08-15 | 0.252669 | 0.252669 | 0.00e+00 |
| 2021-12-03 | 0.291966 | 0.291966 | 0.00e+00 |
| 2024-03-28 | 0.411810 | 0.411810 | 0.00e+00 |
| 2026-07-27 | 5.654990 | 5.654990 | 0.00e+00 |

- écart maximal : **0.00e+00**

**CONFORME — les deux chemins concordent à la précision machine.**

## 2. Anti-lookahead — mutation du futur

Les prix postérieurs à l'indice 12808 (2020-10-09) sont multipliés
par 7. La dispersion calculée **à** cette date doit être strictement inchangée.

- dispersion avant mutation : **0.950881**
- dispersion après mutation : **0.950881**

**CONFORME — aucune fuite du futur.**

## 3. Le filtre d'appartenance change-t-il réellement le signal ?

Un filtre sans effet rendrait le « maintenu » vide de sens. La dispersion est
recalculée en forçant l'univers à **tous** les tickers disponibles ; elle doit
différer de la version point-in-time.

- dates comparées : **6**
- dates où la dispersion diffère : **6**
Écart moyen (univers élargi − point-in-time) : **-0.1082**. Aucun mécanisme n'avait été annoncé au
pré-enregistrement (abstention motivée depuis le #409) : la mesure est donc
publiée sans hypothèse à confirmer ou infirmer.

## 4. Causalité de la porte

`combined_position` consomme `gate_aligned[:-1]` : la porte appliquée au
rendement du jour t est celle observée en t−1. Vérifié sur une porte synthétique
n'ayant qu'un seul jour actif (indice 20).

- indices de position modifiée : **[np.int64(20)]**

**CONFORME — décalage d un jour, aucune décision prise sur le rendement du jour même.**

## 5. Proximité avec le #407 — mesure pré-enregistrée

Les deux candidats sont construits sur la **même matrice de momentum 12-1**,
agrégée autrement : écart-type transversal ici, écart entre déciles extrêmes au
#407. Le pré-enregistrement annonçait de mesurer leur proximité sans en préjuger,
le #403 ayant montré qu'un tel voisinage pouvait aller jusqu'à l'identité.

- séances communes : **2656**
- part des séances où les deux portes donnent la **même** décision : **93.3 %**
- corrélation des deux portes : **0.8679**

**Portes très proches mais distinctes.** Elles ne sont pas interchangeables au
sens du #403 (qui exigeait l'identité), mais leur voisinage signifie que les
deux PASS ne constituent **pas** deux confirmations indépendantes.

Le `.npz` de ce cycle est sauvegardé : le balayage du #406 pourra comparer les
deux séries de P&L directement.

## Verdict de l'audit

**CONFORME — les contrôles de validité (1 à 4) passent.**

Le contrôle 5 est une **mesure** de proximité avec le #407, pas un test : il
n'entre pas dans ce verdict.
