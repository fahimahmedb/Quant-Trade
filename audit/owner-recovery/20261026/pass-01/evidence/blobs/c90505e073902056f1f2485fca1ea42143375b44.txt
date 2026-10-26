# Additif propriétaire → 🟩 B : tester sans rien acheter (complète l'ordre 10)

```text
ADDITIF À L'ORDRE 10. Règle du propriétaire : on teste avec les données gratuites. On n'achète une offre de données qu'APRÈS un gain net prouvé.

1. Corrections de frais (docs.polymarket.com/trading/fees, relu le 2026-09-29) :
   - crypto, dont les marchés horaires « above K » : frais = C × 0,07 × p × (1−p), soit 1,75 ¢ par part à p = 0,5 (3,5 % du coût). Le « pic 1,56 % » de l'ordre 10 est l'ancien barème de janvier ;
   - Kalshi facture aussi les makers sur ses séries sport principales (KXNFLGAME : fee_type = quadratic_with_maker_fees, fee_multiplier = 1, via l'API /series/{ticker}). Son coefficient taker (0,07 selon des tiers) n'est pas confirmé : le PDF officiel renvoie 429. Donc PAS de « priorité à Kalshi » par principe : pour chaque série, compare le frais réel (fee_type, fee_multiplier) à l'écart attendu, et préfère les séries à multiplicateur réduit (ex. KXMLBGAME = 0,5).

2. B6 (déclaration P7-B6 → H-014, branche claude/prompt-recherche-praticiens-dfy1l0, research/praticiens/declarations_registre.jsonl) : SHADOW_DIRECT, 0 € de données.
   - Chaque heure, pour les marchés BTC et ETH « above K » qui expirent dans 60 min : carnet CLOB (meilleur bid/ask et taille, par strike), DVOL horaire (deribit.com/api/v2/public/get_volatility_index_data?currency=…&resolution=3600), spot Hyperliquid (candleSnapshot 1h).
   - p* = N(d2), avec σ = DVOL ramenée à l'horizon restant. Acheter le côté dont l'ask < p* − 0,07·p·(1−p). Tenir jusqu'au règlement.
   - Exécution papier au ask observé, pour une taille ≤ la taille affichée.
   - KPI : P&L net par $ (t-SPRT par fenêtre), score de Brier du prix contre p*.
   - Grille de la déclaration : 2 essais (avec ou sans les barreaux p < 0,15 ou > 0,85).

3. H-001 avec le quota gratuit (500 crédits/mois) : 1 appel h2h, région eu = 1 crédit = toutes les rencontres à venir d'une ligue.
   - Par ligue et par créneau de coups d'envoi : 1 appel à T−2 h (entrée) et 1 appel à T−10 min (clôture pour la CLV), soit ≈ 25-50 crédits par ligue et par mois, donc ≈ 10 ligues.
   - Le goulot n'est pas le quota mais la rareté des écarts nets de frais (H-006 : 3 paris sur 378 matchs).
   - Acheter l'offre 20K (30 $/mois) SEULEMENT si la CLV nette est > 0 avec t ≥ required_t sur le forward pristine.

Réponse : 3 lignes (SHA, H-014 importée, collecte B6 active oui/non).
```
