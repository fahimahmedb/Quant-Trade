# Pré-enregistrement — inventaire vérifié de la dette de protocole

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.
Cycle d'**inventaire** : aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché.

## Pourquoi ce cycle existe

Le #430 a constaté que la file d'outillage était vide : les cinq chantiers
ouverts depuis le #406 sont clos. Le #429 avait prévu ce cas et fixé la règle :

> « Le prochain cycle devra **chercher une dette réelle plutôt qu'en inventer
> une** — et, s'il n'en trouve pas, l'écrire. »

C'est ce cycle. Il ne fabrique pas de travail : il **cherche méthodiquement**, et
publiera « rien d'actionnable » si c'est la conclusion.

## Cinq contrôles mécaniques, définis avant toute mesure

Chacun est une requête reproductible sur le dépôt, sans jugement :

| # | Contrôle | Ce qu'un résultat non nul signifierait |
|---|---|---|
| **A** | rapports `*_anti_cheat.md` dont le verdict n'est **pas** CONFORME | protocole violé, ou faux positif du vérificateur |
| **B** | `nonml_X_result.md` sans `PREREG_X.md` dans l'historique git | backtest exécuté sans pré-enregistrement |
| **C** | rapports **PASS** jamais soumis à la batterie de validation (Règle 9) | PASS de niveau 1 présenté sans son second filtre |
| **D** | scripts référençant un fichier de `data/` **absent** | rapport publié depuis une source disparue |
| **E** | `PREREG_X.md` sans aucun artefact produit (`_result.md` ni `_audit.md`) | cycle déclaré puis abandonné |

Les contrôles B et E se comptent mécaniquement mais **ne se concluent pas
mécaniquement** : un `PREREG` peut porter un nom différent de son résultat, et
un cycle d'outillage produit un `_audit.md` sans `_result.md`. Tout écart sera
donc **inspecté** avant d'être qualifié, et le nombre brut publié à côté du
nombre confirmé.

## Ce que ce cycle ne fera pas — annoncé d'avance

**1. Aucun pré-enregistrement rétroactif.** Si le contrôle A ou B révèle un
cycle sans PREREG, écrire ce PREREG aujourd'hui serait antidater une garantie
qui n'a pas existé. Le manque sera **publié**, jamais comblé après coup.

**2. Aucun assouplissement du vérificateur anti-cheat.** Un constat déjà fait
avant d'écrire ces lignes : `nonml_log_return_compounding_audit` porte un verdict
**ÉCHEC — protocole violé**, et son script déclare dans sa docstring être un
audit de code « aucun degré de liberté de calibrage, aucun critère de succès à
optimiser ». Le vérificateur, lui, exige un PREREG sans exception.

Rendre le vérificateur tolérant aux exceptions **créerait précisément la faille
qu'il existe pour fermer** : tout cycle futur pourrait se déclarer exempt. Je ne
le modifierai donc pas de ma propre initiative. Le cas sera documenté et
**porté à l'arbitrage de l'utilisateur**, au même titre que `n_trials` (#421).

C'est un cycle où la bonne action peut être de **ne pas agir**, et de le dire.

## Critère de succès — chiffré

1. Les **5** contrôles exécutés et leurs comptes publiés, y compris les zéros.
2. Chaque anomalie des contrôles B et E **inspectée individuellement**, et
   qualifiée « confirmée » ou « faux positif » avec sa raison.
3. Conclusion explicite : soit une file d'actions pour les cycles suivants, soit
   la phrase « rien d'actionnable », sans travail fabriqué pour combler le vide.
4. **0** pré-enregistrement rétroactif, **0** modification du vérificateur
   anti-cheat.

## Prédiction

**Aucune prédiction chiffrée** sur les contrôles B à E : je n'ai pas mesuré, et
prédire sans base m'a déjà trompé deux fois (#407, #408).

Le contrôle A est le seul déjà mesuré, et il l'est **avant** ce pré-enregistrement
plutôt que recopié : **1** rapport non CONFORME, nommé ci-dessus.

## Engagements

1. Résultat rapporté tel quel, y compris si les cinq contrôles ne donnent rien —
   ce serait alors le résultat du cycle, pas son échec.
2. Aucun pré-enregistrement antidaté, aucune tolérance ajoutée au vérificateur.
3. Aucun verdict de stratégie modifié.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
