# Pré-enregistrement — trancher les 17 candidats « du jour même » par horodatage

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.
Cycle d'**infrastructure de protocole**. Aucune stratégie nouvelle, aucun
paramètre touché, **aucun verdict de niveau 1 modifié**.

## Ce que j'avais écrit, et pourquoi c'était insuffisant

Le #431 a classé les PASS sans batterie selon la **date** d'ajout de leur
rapport, comparée à celle de `nonml_pass_validation_battery.py` (2026-07-29).
**17** candidats tombent le **jour même**, et j'ai écrit :

> « Rien ne dit s'ils ont été publiés avant ou après l'ajout du script dans la
> même journée. Je les compte à part plutôt que de les ranger du côté qui
> m'arrange. »

Puis au #432 : « statut non tranchable **par la date seule**, laissés en l'état ».

**C'était exact et insuffisant.** La phrase était vraie au mot près — la *date*
ne tranche pas — mais git conserve l'**horodatage à la seconde**, et je ne l'ai
pas utilisé. Compter à part était correct ; s'arrêter là ne l'était pas. Le #429
avait posé la règle « chercher avant de conclure », et je m'étais arrêté à la
première résolution disponible au lieu de la plus fine.

Vérification de faisabilité faite avant d'écrire ces lignes : la batterie a été
ajoutée à **17:56:16 UTC**, et un candidat testé au hasard porte **02:15:46** le
même jour. L'horodatage **discrimine**.

## Règle de classification — fixée avant toute mesure

Pour chacun des 17, on compare l'horodatage du **commit d'ajout** de son
`results/nonml_<nom>_result.md` (`git log --diff-filter=A --format=%ct`) à celui
du commit d'ajout de la batterie.

> - horodatage **strictement antérieur** ⇒ **antériorité** : le candidat n'a
>   jamais pu être soumis à une règle qui n'existait pas. Blanchi.
> - horodatage **strictement postérieur** ⇒ **dette réelle**, au même titre que
>   les 6 du #431.
> - horodatage **exactement égal** ⇒ resterait indécidable, et serait compté à
>   part une troisième fois plutôt que rangé arbitrairement.

Aucune tolérance, aucune marge : la comparaison est exacte à la seconde.

## Ce que ce cycle fera des candidats en dette

Déclaré d'avance pour ne pas choisir après avoir vu les noms :

> Tout candidat classé « dette réelle » **et** portant le schéma indiciel
> (`pos`, `r_asset`, `dates`, `cost_bps`) est **soumis à la batterie dans ce même
> cycle**. Ceux au schéma panier sont **écartés et listés**, comme
> `january_effect_lowprice_overlay_pit_universe` au #432.

## Prédiction

**Aucune prédiction sur le nombre.** Je n'ai vérifié qu'un seul des 17, pour
établir que la méthode discrimine, et un échantillon de un ne fonde rien.

Sur l'issue des batteries éventuelles, en revanche, la prédiction est
**déductive** et reprend celle du #432 :

> Tout candidat effectivement soumis **échouera au DSR**, `n_trials` valant la
> taille du backlog (370 au #432). Les #111-#112 avaient déjà établi qu'à
> `n_trials = 110` le seuil est hors de portée d'une hypothèse isolée.

Comme au #432, cette prédiction **n'aura aucun mérite** si elle se vérifie : elle
découle d'un résultat mesuré il y a trois cents cycles.

## Critère de succès — chiffré

1. **17/17** candidats classés par horodatage, aucun laissé « ambigu » sauf
   égalité exacte à la seconde, auquel cas le compte est publié.
2. Les trois catégories publiées avec leurs effectifs **et** leurs listes.
3. Tout candidat en dette et de schéma indiciel **soumis à la batterie** dans ce
   cycle, ses 5 contrôles reportés individuellement.
4. **0** verdict de niveau 1 modifié.

## Engagements

1. Résultat rapporté tel quel — y compris si les 17 sont tous blanchis, auquel
   cas le cycle aura confirmé une absence, ce qui reste un résultat.
2. Aucun candidat déplacé de catégorie après lecture de son nom ou de son
   verdict.
3. Aucun seuil de batterie modifié, aucun `n_trials` ajusté — la question du
   `n_trials` lu par expression régulière reste **portée à l'arbitrage** (#421).
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
