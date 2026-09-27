# Message propriétaire → 🟩 B (à coller tel quel)

```text
MESSAGE PROPRIÉTAIRE — 4 points, par ordre de priorité.

1. HIGH INTÉGRITÉ (invariant 6), à corriger en premier. CALENDAR_PRISTINE_AFTER = "2026-09-11", mais la lane a été introduite le 2026-09-25 (commit 076391c). L'événement FOMC du 2026-09-16 n'est donc pas prospectif.
   - Fixe pristine_after à la date de commit de chaque règle (2026-09-25 pour les lanes calendaires).
   - Retire l'événement du 16/09 du forward et du t-SPRT.
   - Ajoute un test qui échoue si pristine_after précède le premier commit de la lane.
   - Vérifie toutes les autres lanes en SHADOW.

2. JURIDICTION = ÉTATS-UNIS pour le futur capital réel. Ajoute au registre et à FAST_RAIL_STATE.md une colonne « accès légal US » :
   - Kalshi : oui, SAUF le sport, qui dépend de l'État (9e Circuit, 2026-08-28 : les contrats sport sont des paris dans le Nevada ; divergence avec le 3e Circuit) ;
   - Polymarket US (DCM CFTC, ouverture progressive) : oui ;
   - Polymarket international, Hyperliquid, dYdX, Binance.com : non (US persons exclus) ;
   - CME, IBKR (actions, ETF, futures, offres de rachat odd-lot) : oui ;
   - books sportifs licenciés : selon l'État.
   KYC d'un non-résident en séjour temporaire (SSN, visa) : à vérifier.

3. PÉRIMÈTRE DE RECHERCHE : on teste TOUT en papier/shadow, y compris ce qui n'est pas accessible légalement aujourd'hui. La colonne d'accès sert au CLASSEMENT et au transfert vers le rail sûr, jamais de filtre de recherche. Restent interdits sans exception : capital réel, ordres réels et tout contournement (VPN, prête-nom, fausse résidence). Les règles d'économie des essais restent en vigueur.

4. NOUVELLES PISTES issues de l'étude praticiens indépendante (102 sources), sur la branche claude/new-session-kfwf1b : research/practitioners_2026-09-27/REPORT.md et SOURCES.md. Lis la synthèse et les fiches R1 à R4 seulement. Les σ sont des hypothèses : calibre-les dès les deux premières semaines de forward.
   - R1, rente maker par catégorie sur Kalshi, hors échantillon publié : TESTER, avec calcul de puissance d'abord. Au règlement il faut environ 8 600 événements, donc UNDERPOWERED en dessous. En markouts, environ 38 marchés suffisent : privilégie les markouts.
   - R2, maker papier sur le sport de niche, juste valeur sharp (Pinnacle), jugé en markouts : FORWARD SEULEMENT, 2 à 3 mois. S'intègre au collecteur H-001.
   - R3, pricing papier des combos RFQ Kalshi, jugé en « CLV combo » (environ 580 combos, moins d'une semaine) : FORWARD SEULEMENT. Vérifie d'abord si un membre voit le flux complet des RFQ.
   - R4, récompenses de liquidité (Kalshi LIP, rewards Polymarket), en ligne séparée : FORWARD SEULEMENT, sans expected_t (aucune preuve A ou B).
   L'étude confirme les rejets : carry funding, déblocages de tokens, merger arb, mention markets, longshot Polymarket, copy-trading. Ne les teste pas.
   Déclare chaque piste au registre AVANT toute donnée, avec expected_t. Une piste FORWARD SEULEMENT consomme 0 essai historique.

Réponse : 5 lignes (SHA, HIGH corrigé, pistes déclarées, essais /200).
```

# Message propriétaire → Blue (à coller dans une session Blue)

```text
Ajoute UNE ligne à la section « 9. Rail C » de governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md, sans créer de nouveau document :
« Juridiction d'opération prévue : États-Unis. Recherche papier/shadow sur tous les marchés ; aucun transfert au rail sûr sans accès légal US confirmé pour le compte réel (venue, État, KYC). Aucun contournement (VPN, prête-nom, fausse résidence). »
Un commit, pas de merge. Rendu : SHA.
```
