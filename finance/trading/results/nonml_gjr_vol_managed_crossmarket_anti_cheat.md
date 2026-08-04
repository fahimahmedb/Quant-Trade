# Vérification anti-cheat — gjr_vol_managed_crossmarket (cycle #166)

**Note méthodologique** : `scripts/nonml_anti_cheat_check.py` suppose une
correspondance 1:1 `PREREG_<nom>.md` / `scripts/nonml_<nom>_backtest.py` /
`results/nonml_<nom>_result.md`. Ce cycle a un seul PREREG et un seul
script pour 3 marchés (3 fichiers résultat distincts,
`nonml_gjr_vol_managed_{sp500,russell2000,dax}_result.md`), ce qui ne
correspond pas au schéma attendu par l'outil générique — lancer l'outil
tel quel produirait un faux négatif ("résultat non committé"). Les mêmes
5 vérifications sont donc reproduites manuellement ci-dessous à partir de
l'historique git réel.

- **[OK]** Pré-enregistrement `PREREG_gjr_vol_managed_crossmarket.md` committé en premier (`c43dd22`, ts=1785830141), avant le script (`28feaf0`, ts=1785830698) et avant les 3 résultats (`9395429` DAX ts=1785830725, `b22fc63` Russell 2000 ts=1785830742, `65a9aa8` S&P 500 ts=1785830793).
- **[OK]** Le pré-enregistrement précède chronologiquement les 3 premiers résultats (aucune exception).
- **[OK]** Aucune modification du pré-enregistrement après le premier résultat (`git log` sur `PREREG_gjr_vol_managed_crossmarket.md` ne montre qu'un seul commit, `c43dd22`).
- **[OK]** Aucun motif suspect détecté dans `scripts/nonml_gjr_vol_managed_crossmarket_backtest.py` (grep sur `GridSearch`, `itertools.product`, `sklearn`, boucle sur seuil/fenêtre : aucune occurrence).
- **[OK]** Paramètres `TARGET_VOL_ANNUAL_PCT=20.0`, `CAP=2.0`, `T0=750`, `REFIT_EVERY=21` : valeurs littéralement identiques (mêmes constantes, même script) à `nonml_volatility_managed_portfolio_gjr_backtest.py` (#165) — aucun retuning par marché, vérifiable par diff des deux fichiers.

**Verdict : CONFORME** (0 échec sur 5 vérifications, reproduites manuellement pour la raison indiquée ci-dessus).
