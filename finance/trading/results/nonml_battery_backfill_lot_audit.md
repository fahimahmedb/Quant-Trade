# Audit — rattrapage de batterie sur les PASS postérieurs à la Règle 9 (pré-enregistré)

Cycle d'**infrastructure de protocole**. Aucune stratégie nouvelle, aucun
paramètre touché, **aucun verdict de niveau 1 modifié**.

Cet audit relit les rapports produits par la batterie ; il ne rejoue aucun
contrôle. La batterie est l'outil de référence, l'audit constate et qualifie.

## Périmètre — 4 exécutés, 2 écartés avec leur raison

- `january_effect_lowprice_overlay_pit_universe` — schéma **panier** — la batterie exige le schéma indiciel (`pos`, `r_asset`, `dates`, `cost_bps`). Lui fabriquer une position scalaire serait inventer une donnée.
- `capitulation_gate_floor_sweep` — **diagnostic, pas une stratégie** — faux positif de détection écarté d'office par le pré-enregistrement (établi au #427).

## Résultats — les cinq contrôles, candidat par candidat

| Candidat | a. Coûts | b. Crise | c. Stabilité | d. SPA | e. DSR | Verdict |
|---|---|---|---|---|---|---|
| `gjr_vol_managed_russell2000` | ÉCHEC | OK | ÉCHEC | ÉCHEC | ÉCHEC | non validé |
| `gjr_vol_managed_sp500` | ÉCHEC | ÉCHEC | OK | OK | ÉCHEC | non validé |
| `deep_drawdown_breadth_vol_targeting_overlay_pit_universe` | ÉCHEC | OK | OK | OK | ÉCHEC | non validé |
| `weakness_breadth_vol_targeting_overlay_pit_universe` | OK | OK | OK | ÉCHEC | ÉCHEC | non validé |

**0/4 candidat(s) obtiennent le PASS RENFORCÉ.**

## La prédiction pré-enregistrée

> « Attente : **0 des 4** candidats ne passe les 5 contrôles, l'échec venant au
> minimum du **DSR**. »

**Vérifiée sur les deux points** : 0/4 PASS RENFORCÉ, et le DSR
échoue pour **4/4**.

| Candidat | DSR obtenu | Seuil |
|---|---|---|
| `gjr_vol_managed_russell2000` | 0.0 | 0,95 |
| `gjr_vol_managed_sp500` | 0.0 | 0,95 |
| `deep_drawdown_breadth_vol_targeting_overlay_pit_universe` | 0.1583 | 0,95 |
| `weakness_breadth_vol_targeting_overlay_pit_universe` | 0.1045 | 0,95 |

`n_trials = 370` pour les quatre. Les #111 et #112 avaient déjà mesuré qu'à
`n_trials = 110`, **aucune hypothèse individuelle du backlog n'avait de chance
réaliste** de franchir le seuil. À 370, le constat ne pouvait que se répéter.

**Cette prédiction n'a donc aucun mérite** : elle découle d'un résultat déjà
mesuré il y a plus de trois cents cycles, pas d'une intuition. Je l'écris ainsi
plutôt que de la compter comme un succès de plus.

## Le candidat inactif — pourquoi ses trois « OK » ne valent rien

`weakness_breadth_vol_targeting_overlay_pit_universe` passe **3** contrôles sur 5 :

- Stress coûts : OK
- Stress crise : OK
- Stabilité temporelle : OK

**Ce n'est pas une force, c'est un artefact d'inactivité.** Ce candidat active
son overlay **0,00 %** du temps : son P&L est *identique* à celui de Buy & Hold
(#415, #417, étiquette « PASS NON INFORMATIF » déjà portée par son rapport).

Une série identique au benchmark ne peut évidemment pas être dégradée par un
stress de coûts, ni faire pire que lui en crise, ni être instable *par rapport
à lui-même*. Les trois « OK » mesurent une **absence de position**, pas une
robustesse.

Le pré-enregistrement l'annonçait avant l'exécution : « son résultat ne dira
rien d'un edge ». Il est publié ici tel quel, avec sa lecture, plutôt que
présenté comme 3/5 encourageants.

## Ce que ce cycle ne fait pas

**Aucun verdict de niveau 1 n'est modifié.** La batterie **ajoute** un jugement,
elle n'annule pas un PASS pré-enregistré : chacun de ces candidats a bien atteint
le critère qu'il s'était fixé, sur les données annoncées. Ce que le lot établit,
c'est qu'aucun ne survit au filtre joint que le backlog s'impose depuis le #111.

Ce constat était **déjà celui du backlog** : « 0 PASS RENFORCÉ » y figure depuis
les #111-#112. Ce cycle ne le découvre pas — il **étend sa couverture** aux
candidats qui avaient échappé au filtre.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| candidats soumis | 4/4 | 4/4 | ✔ |
| écartés avec raison publiée | 1 (+1 d'office) | 2 | ✔ |
| cinq contrôles reportés individuellement | oui | oui | ✔ |
| verdicts de niveau 1 modifiés | 0 | 0 | ✔ |

La dette ouverte par le #431 est **soldée pour les 4 candidats exécutables**. Il
reste **1** candidat hors de portée de l'outil (schéma panier), listé et non
forcé — étendre la batterie au schéma panier serait un cycle distinct, à déclarer.
