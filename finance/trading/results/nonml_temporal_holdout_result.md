# Hors-échantillon temporel sur les PASS (pré-enregistré)

**Piste C**, la dernière des trois du #455.

## Ce que ce test est — et ce qu'il n'est pas

**Ce n'est pas un vrai hors-échantillon.** Les règles sont déterministes —
rien n'a été « appris » sur la période — mais elles ont été **choisies en
connaissant tout l'échantillon**. La tranche finale est contaminée par la
**sélection**, pas par l'estimation.

C'est le meilleur test disponible sans données nouvelles, et il est **plus
faible** qu'un vrai OOS. Le présenter autrement serait malhonnête.

## Couverture

- PASS retenus : **100**
- exclus : **0**

## Découpe : 252 dernières séances *(principale)*

Candidats évaluables sur cette découpe : **100**

| | Avant | Hors-échantillon |
|---|---|---|
| Sharpe **médian** | **+0.59** | **+1.34** |
| Sharpe moyen | +0.63 | +1.37 |
| 1ᵉʳ quartile | +0.52 | +1.23 |
| 3ᵉ quartile | +0.72 | +1.39 |

- fraction à Sharpe hors-échantillon **positif** : **100.0 %**
- fraction **battant son propre Sharpe d'avant** : **98.0 %**
- **chute de la médiane** : **-128.2 %**

Les cinq pires hors-échantillon :

- `lowvol_sma200_overlay` — avant +0.98, après **+0.12**
- `diversification_bond_overlay_dax` — avant +0.29, après **+0.19**
- `intl_breadth_confirmation_overlay` — avant +0.52, après **+0.86**
- `gjr_vol_managed_russell2000` — avant +0.42, après **+0.97**
- `halloween_midterm_multiplicative_overlay` — avant +0.56, après **+0.98**

Les cinq meilleurs :

- `amihud_illiquidity_tilt` — avant +0.99, après **+2.99**
- `january_effect_lowprice_overlay` — avant +1.27, après **+2.63**
- `momentum_turnover_doublesort` — avant +1.10, après **+2.55**
- `leaders_vol_targeting_20_overlay` — avant +0.73, après **+2.26**
- `winners_trend_vol_targeting_overlay` — avant +0.91, après **+2.20**

## Découpe : 504 dernières séances *(secondaire)*

Candidats évaluables sur cette découpe : **100**

| | Avant | Hors-échantillon |
|---|---|---|
| Sharpe **médian** | **+0.60** | **+0.76** |
| Sharpe moyen | +0.63 | +0.84 |
| 1ᵉʳ quartile | +0.53 | +0.70 |
| 3ᵉ quartile | +0.72 | +0.83 |

- fraction à Sharpe hors-échantillon **positif** : **100.0 %**
- fraction **battant son propre Sharpe d'avant** : **78.0 %**
- **chute de la médiane** : **-25.5 %**

Les cinq pires hors-échantillon :

- `turn_of_month` — avant +0.59, après **+0.17**
- `halloween_midterm_multiplicative_overlay` — avant +0.57, après **+0.42**
- `intl_breadth_confirmation_overlay` — avant +0.54, après **+0.48**
- `halloween_effect` — avant +0.53, après **+0.55**
- `index_52w_high_overlay` — avant +0.57, après **+0.57**

Les cinq meilleurs :

- `january_effect_lowprice_overlay` — avant +0.99, après **+2.28**
- `amihud_illiquidity_tilt` — avant +0.75, après **+2.26**
- `momentum_turnover_doublesort` — avant +0.75, après **+2.13**
- `short_term_momentum` — avant +0.62, après **+1.88**
- `winners_trend_vol_targeting_overlay` — avant +0.74, après **+1.86**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| médiane hors-éch. < moitié de la médiane d'avant | < +0.29 | +1.34 | **réfutée** |
| fraction positive proche de 50 % | 35–65 % | 100.0 % | **réfutée** |
| moins d'un quart battent leur Sharpe d'avant | < 25 % | 98.0 % | **réfutée** |

## Le défaut est dans ma découpe — diagnostic post-hoc

Le pré-enregistrement engageait : *« si ces prédictions sont démenties, je
devrai **d'abord douter de ma découpe** avant de conclure à un edge »*. Elles
le sont toutes les trois, et dans le sens **favorable** — le cas qui oblige à
chercher le défaut chez soi.

**Ce qui suit est hors des métriques déclarées**, et ne sert pas à recalculer
un verdict : il sert à expliquer pourquoi les métriques déclarées ne disent
rien.

**Buy & Hold**, sur exactement la même fenêtre de 252 séances,
mesuré sur **186** séries sous-jacentes :

| | Stratégies PASS | Buy & Hold |
|---|---|---|
| Sharpe médian | +1.34 | **+1.39** |
| fraction positive | 100.0 % | **100.0 %** |

> **Buy & Hold obtient le même résultat, et légèrement meilleur.** Les
> 252 dernières séances sont une phase de hausse à faible volatilité : tout
> ce qui est long y affiche un Sharpe élevé.

**Ma découpe compare une décennie contenant des krachs à une seule année
haussière.** Elle mesure donc le **régime de marché**, pas l'edge. La
« persistance » que le tableau semblait montrer n'existe pas : elle est un
artefact de la fenêtre choisie.

**Le test déclaré est confondu et n'établit rien sur l'edge.** Je le publie
tel quel plutôt que de le remplacer : le remplacer par une comparaison au
benchmark serait changer la métrique après avoir vu le résultat, ce que le
pré-enregistrement interdit. La bonne version — Sharpe **relatif au
benchmark** sur la même fenêtre — est un cycle à déclarer d'avance.

Un point mérite néanmoins d'être noté, parce qu'il va **contre** les
stratégies : leur médiane est **inférieure** à celle de Buy & Hold sur cette
fenêtre. Même dans le régime qui les flatte le plus, elles ne le battent pas.

## Lecture

**Mes trois prédictions sont réfutées**, et dans le sens favorable aux
stratégies. Je ne le compte pas comme une bonne nouvelle : le diagnostic
ci-dessus montre que c'est **ma découpe** qui est en cause, pas un edge
retrouvé. Rapporté tel quel, sans ajustement de découpe ni de seuil.

**Le résultat utile de ce cycle est donc négatif à son propre égard** : il
a produit un test qui ne mesure pas ce qu'il prétendait mesurer, et c'est
le pré-enregistrement — en m'obligeant à douter de la découpe avant de
crier au succès — qui a permis de s'en apercevoir.

**Ce que cela ne tranche pas** : un effondrement est compatible avec un
**surapprentissage de sélection** comme avec la **disparition réelle** d'une
anomalie. Ce cycle ne départage pas les deux, et le pré-enregistrement
l'annonçait.

**Ce qu'il ne prouve pas non plus** : les candidats encore positifs ne sont
**pas** validés pour autant. Sur une tranche contaminée par la sélection, un
Sharpe positif est ce à quoi on s'attend pour une fraction des candidats,
même sans aucun edge.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).