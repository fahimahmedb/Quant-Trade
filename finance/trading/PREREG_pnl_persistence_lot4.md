# Pré-enregistrement — persistance du P&L, lot 4 (les 2 derniers candidats du #415)

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**infrastructure et de vérification**. Aucune stratégie évaluée, aucun
verdict recalculé, aucun paramètre de stratégie touché.

## Le motif inscrit à la file était faux — vérifié avant d'écrire

La file du #425 inscrivait ce cycle sous condition :

> « Doter d'un `.npz` les 2 derniers candidats du #415, **si et seulement si leurs
> sources externes redeviennent accessibles hors ligne** — sinon les déclarer
> définitivement hors portée. »

**Cette condition n'a pas lieu d'être.** Vérification faite par lecture du code
avant d'écrire ce pré-enregistrement (règle du #400, étendue aux #417, #420,
puis #425) :

| Candidat | Source réelle | Présente ? |
|---|---|---|
| `vix_regime_vol_targeting_overlay` | `data/vixcls_daily.csv` + `data/nasdaq100_daily.txt` | **oui**, locales |
| `rebound_speed_breadth_vol_targeting_overlay` | `data/pead/prices/*.json` (99 fichiers) + `data/nasdaq100_daily.txt` | **oui**, locales |

Aucun des deux n'appelle le réseau. Leur `.npz` est absent pour une raison
banale, déjà rencontrée aux #416, #423 et #424 : la sauvegarde est **placée sous
`if verdict:`**, et les deux portent un **FAIL**.

C'est la **quatrième fois** qu'un chiffre ou un motif repris d'un cycle antérieur
sans re-vérification se révèle faux (#417, #420, #425, celui-ci). Aggravant : je
l'ai écrit au #425, dans le cycle même où j'énonçais la règle interdisant de
recopier un chiffre sans le re-mesurer. La règle est bonne ; je ne me l'étais pas
appliquée à la phrase que j'écrivais au même moment. Le fait est publié tel quel.

## Ce que ce lot fait — et ce qu'il n'apporte pas

**Ce qu'il fait** : rendre la sauvegarde **inconditionnelle** dans les 2 scripts,
convention du #416 reprise sans changement. Schéma indiciel (`pos`, `r_asset`,
`dates`, `cost_bps`), déjà celui des deux blocs `savez` existants — seule la
condition `if verdict:` disparaît, aucune ligne de calcul n'est touchée.

**Ce qu'il n'apporte pas** : les 2 portent un **FAIL**. Aucun verdict ne peut
changer, et le #421 a mesuré que `n_trials` est immatériel (il faudrait
`n_trials ≤ 3` pour franchir le seuil DSR). Le gain est la **complétude du
diagnostic** : le volet B du balayage #415 passerait de 60/62 à **62/62**.
Je l'écris avant de commencer pour ne pas survendre l'issue après coup.

## Contrôle de non-régression — le vrai contenu du cycle

Les 2 fichiers `results/nonml_<nom>_result.md` doivent être **identiques octet à
octet** avant et après ré-exécution. Toute différence bloque la conclusion et
devient le résultat principal du cycle.

C'est le quatrième lot soumis à ce contrôle (#416 : 10/10 ; #423 : 4/4 ;
#424 : 12/12). Deux résultats publiés de plus seraient testés contre leur propre
code, portant le total à **28**.

## Mesures publiées après ré-exécution

1. Couverture du volet B du balayage #415, avant et après.
2. Pour chacun des 2, l'activation mesurée et son classement au seuil de 2 %
   (repris tel quel du #410), avec la discrimination du #416.
3. Balayage de doublons rejoué **sans modification** : nombre de groupes exacts
   et de quasi-doublons, comparé aux 3 et 1 du #424.

## Critère de succès — chiffré

1. **2/2** scripts modifiés, ré-exécutés, `.npz` produit — ou la raison de
   l'échec publiée.
2. **0 différence** sur les 2 fichiers de résultat.
3. Les trois mesures ci-dessus publiées, quelles que soient leurs valeurs.

## Prédiction — déductive

**0 différence de résultat.** Même raisonnement qu'aux #416, #423 et #424, tous
trois vérifiés : retirer une condition autour d'un `np.savez` ne touche aucun
calcul.

> **Attente : 0 différence, couverture 60 → 62/62.**

**Aucune prédiction** sur l'activation des 2 candidats ni sur d'éventuels
nouveaux doublons : je n'ai pas de base pour l'anticiper, et les deux fois où
j'ai prédit sans base (#407, #408) je me suis trompé.

Cette fois le chiffre de couverture est **re-mesuré à l'instant** (60 mesurés sur
62 structurés, relevé au #425), pas recopié — c'est précisément le défaut que ce
cycle documente.

## Engagements

1. Résultat rapporté tel quel, y compris si le lot ne révèle rien.
2. Aucune ligne de calcul modifiée ; chaque script lu avant édition.
3. Tout script dont la structure ne correspond pas à la convention est **écarté
   et listé**, pas forcé.
4. Dette restante re-chiffrée au backlog.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).
