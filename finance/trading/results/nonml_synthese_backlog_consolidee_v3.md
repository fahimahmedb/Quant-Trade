# Synthèse consolidée v3 — backlog non-ML (155 cycles, 30/07/2026)

Met à jour `nonml_synthese_backlog_consolidee_v2.md` (#145, jusqu'au
#144) avec les cycles #146-155. Ne recalcule rien : lit les résultats
déjà committés.

## 1. Chiffres globaux

- **155 hypothèses testées**, **73 PASS niveau 1**.
- **0 PASS RENFORCÉ** (Règle 9 complète) sur les candidats évalués
  sous cette batterie.
- Score Règle 9 record : **4/5**, atteint par DEUX candidats
  indépendants (#134 et #149), sur DEUX marchés chacun (NDX et S&P 500).

## 2. Le développement majeur depuis la v2 : le #149 dépasse le #134

Le #146 a testé si la correction "taux réaliste sur cash" (#142)
s'appliquait à d'autres mécanismes défensifs du backlog. Après avoir
vérifié — AVANT tout calcul — que les candidats initialement visés
(#9, #58) ne s'appliquaient pas (ils restent ≥1,0x en permanence, comme
la famille calendaire), le #44 (vol-targeting défensif cible 15%,
FAIL originel par sous-dimensionnement) a été identifié comme
candidat de remplacement.

**Résultat (#149) : nouveau MEILLEUR résultat brut du backlog.**
Sharpe +0,53→+0,84 (dépasse le #134, +0,77), MDD -82,9%→-37,9%
(dépasse le #134, -50,9%). **4/5 sous la Règle 9** — deuxième candidat
à atteindre ce score, avec la même propriété clé que le #134 (stabilité
4/4 folds, confirmée au #139 comme spécifique aux mécanismes à un seul
estimateur simple, pas aux ensembles).

Huit cycles supplémentaires ont approfondi ce nouveau candidat :

| Cycle | Question posée | Résultat |
|---|---|---|
| #150 | La famille diversification passe-t-elle un SPA conjoint ? | Limite mécanique identifiée (marchés différents = T différents), restreint à 5 membres NDX : p=0,31, non significatif |
| #151 | Le #149 se généralise-t-il cross-marché comme le #134 ? | OUI : S&P 500 confirme 4/5, MAIS Russell 2000 révèle le **1er échec de stress de coûts** de toute la famille (2/5) |
| #152 | Le #149 peut-il être formalisé en Étape D officielle ? | OUI, ajouté comme 4e variante — meilleure réduction de MDD des 3 variantes testées (+54,3% sur NDX) |
| #153 | Le #149 tient-il sur un verrou temporel pur (12 derniers mois) ? | NON, écart PLUS marqué que le #134 (Calmar 1,70 vs 2,23 BH) — cohérent avec un profil de couverture plus prononcé |
| #154 | Le rebalancement hebdomadaire corrige-t-il la fissure coûts du #151 ? | OUI : Russell 2000 passe de 2/5 à 3/5, NDX maintient 4/5 sans dégradation |
| #155 | Le #149 réduit-il le risque de queue (VaR/ES) mieux que le #134 ? | OUI sur toutes les mesures : ES99 +48,1% (vs +39,0%), jusqu'à +75,1% en crise COVID (vs +67,4%) |

## 3. Bilan de la Règle 10 (rémunération explicite du cash)

La Règle 10, adoptée au #147 suite au reframe du #142, a maintenant un
bilan empirique complet sur 3 tests :

- **#149** (vol-targeting défensif cible 15%) : la correction
  GÉNÉRALISE — meilleur résultat du backlog, confirme que l'effet
  n'est pas spécifique au #115/cible 20%.
- **#55** (faux breakout Donchian, #146) : la correction NE SAUVE PAS
  un signal structurellement mauvais — reste FAIL.
- **Famille calendaire** (#8/#17/#21 et la quasi-totalité des overlays
  du backlog) : la correction NE S'APPLIQUE PAS — ces mécanismes
  restent investis ≥1,0x en permanence par construction, ne détiennent
  jamais de cash.

**Conclusion opérationnelle** : la Règle 10 est un amplificateur d'un
bon signal, pas un réparateur universel. Ce bilan à 3 cas (généralise/
ne sauve pas/ne s'applique pas) est probablement complet — les mécanismes
défensifs restants du backlog sont peu nombreux et déjà couverts.

## 4. Le cycle diagnostic→correction Russell 2000 comme méthode reproductible

Le #151→#154 illustre un pattern méthodologique validé : (1) généraliser
un mécanisme à un nouveau marché, (2) si un contrôle Règle 9 échoue,
diagnostiquer PRÉCISÉMENT lequel et pourquoi (ici : stress de coûts,
turnover trop élevé sur un marché plus volatil), (3) appliquer une
correction CIBLÉE sur ce diagnostic précis (pas une nouvelle exploration
générique), (4) re-valider sur le marché en échec ET vérifier l'absence
de régression sur les marchés déjà réussis. Ce pattern a fonctionné une
fois — reproductible pour d'éventuelles fissures futures.

## 5. Candidats au plafond Règle 9 (mis à jour, remplace le tableau de la v2)

| Candidat | Mécanisme | Score Règle 9 | Remarque |
|---|---|---|---|
| **#149 (NDX)** | Vol-targeting défensif cible 15% + diversification obligataire | **4/5** | Meilleur résultat brut, meilleur VaR/ES, MDD -37,9% |
| **#149 (S&P 500)** | #149 généralisé | **4/5** | Confirme la généralisation |
| **#134 (NDX)** | Vol-targeting défensif cible 20% + diversification obligataire | 4/5 | Le précédent record, encore valide |
| **#134 (S&P 500)** | #134 généralisé | 4/5 | Confirme la généralisation |
| #149 (Russell 2000, hebdo) | #149 + rebalancement hebdomadaire | 3/5 | Fissure coûts corrigée par le #154, stabilité reste 3/4 |
| #137/#139 | #134 empilé sur #131/#124 | 3/5 | Plafond antérieur, non dépassé par l'empilement |

## 6. Recommandation (mise à jour)

Le §5 de la v2 recommandait de trancher entre deux voies (question
n_trials, ou pivot risk management). Le développement #146-155 a
répondu empiriquement aux deux : le #133 avait déjà tranché la
question n_trials (même à 8 familles, DSR reste à 0,51) ; le #135/#155
ont pleinement développé le cadrage risk management (VaR/ES documenté
pour les deux meilleurs candidats).

**Le backlog a désormais exploré, sur 155 cycles, la quasi-totalité
des axes praticables avec des données non-ML gratuites** : calendrier,
tendance, breadth, volatilité (3 estimateurs), diversification
cross-actif (généralisée à 4 marchés, 2 mécanismes défensifs
indépendants), rotation, empilements, décomposition causale, et
correction systématique d'un biais de backtest découvert en cours de
route. Les pistes réellement neuves et non redondantes s'épuisent —
les propositions les plus récentes (#146-155) étaient déjà largement
des corrections/vérifications ciblées plutôt que de nouvelles
directions de recherche.

**Recommandation honnête (pas une décision unilatérale)** : sans
nouvelle catégorie de données ou de mécanisme fondamentalement
différente, poursuivre ce backlog produira probablement des
rendements marginaux décroissants (déjà observés #137/#139 : empiler
n'améliore plus le score). Deux directions restent ouvertes et
n'ont pas encore été formellement proposées à l'utilisateur pour
décision : (a) considérer le backlog non-ML comme substantiellement
complet et basculer l'effort vers la formalisation/déploiement
prudent des deux meilleurs candidats (#134/#149) comme outils de risk
management documentés, avec les garde-fous de surveillance déjà
discutés ; (b) rouvrir l'angle ML (abandonné après l'Étape B) avec les
leçons de rigueur accumulées ici (Règle 9, décomposition causale,
Règle 10). Décision à l'utilisateur.
